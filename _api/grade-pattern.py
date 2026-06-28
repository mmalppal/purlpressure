"""Vercel Python serverless function — pattern grader.

POST /api/grade-pattern
Body (JSON):
  spec:         { PatternSpec as serialized by pattern_input.serializers }
  gauge:        { sts_per_4in, rows_per_4in }           (user's actual gauge)
  measurements: { bust, yoke_depth, body_length, sleeve_length, ... }
  ease:         "classic" | "plus_friendly_classic" | etc.
  options:      { pattern_name?, designer? }

Response (JSON):
  ok: true,  pattern: "<markdown string>",  warnings: [...]
  ok: false, error: "<message>"
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Both pattern_input and raglan_grader live alongside this file in api/.
sys.path.insert(0, os.path.dirname(__file__))

from pattern_input.models import (  # noqa: E402
    ConstructionType,
    GradingRequest,
    PatternGauge,
    PatternSpec,
    SizeEntry,
    StitchCounts,
    LengthMeasurements,
    ShapingRates,
)
from pattern_input.serializers import from_dict as spec_from_dict  # noqa: E402
from pattern_input.router import grade  # noqa: E402
from raglan_grader import (  # noqa: E402
    BodyMeasurements,
    EaseProfile,
    Gauge,
    has_errors,
    validate,
    write_pattern,
)

_EASE_PRESETS = {
    "skin_tight": EaseProfile.skin_tight,
    "close_fitting": EaseProfile.close_fitting,
    "classic": EaseProfile.classic,
    "relaxed": EaseProfile.relaxed,
    "oversized": EaseProfile.oversized,
    "plus_friendly_classic": EaseProfile.plus_friendly_classic,
}


def _parse_float(value, name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{name}' must be a number, got {value!r}")


def _parse_optional_float(value) -> float | None:
    if value is None or value == "" or value == "null":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(content_length)
            data = json.loads(raw)
        except (json.JSONDecodeError, KeyError) as exc:
            self._respond(400, {"ok": False, "error": f"Invalid JSON: {exc}"})
            return

        try:
            pattern, warnings = _process(data)
            self._respond(200, {"ok": True, "pattern": pattern, "warnings": warnings})
        except ValueError as exc:
            self._respond(400, {"ok": False, "error": str(exc)})
        except NotImplementedError as exc:
            self._respond(400, {"ok": False, "error": str(exc)})
        except Exception as exc:
            self._respond(500, {"ok": False, "error": f"Server error: {exc}"})

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def _respond(self, status: int, body: dict) -> None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):
        pass


def _process(data: dict) -> tuple[str, list[str]]:
    # ── PatternSpec ────────────────────────────────────────────────────────────
    raw_spec = data.get("spec")
    if not raw_spec:
        raise ValueError("'spec' is required")
    spec: PatternSpec = spec_from_dict(raw_spec)

    # ── User gauge ─────────────────────────────────────────────────────────────
    g = data.get("gauge") or {}
    gauge = Gauge.from_4in_swatch(
        _parse_float(g.get("sts_per_4in"), "gauge.sts_per_4in"),
        _parse_float(g.get("rows_per_4in"), "gauge.rows_per_4in"),
    )

    # ── User body measurements ─────────────────────────────────────────────────
    m = data.get("measurements") or {}
    m_kwargs: dict = {
        "bust": _parse_float(m.get("bust"), "measurements.bust"),
        "yoke_depth": _parse_float(m.get("yoke_depth"), "measurements.yoke_depth"),
        "body_length": _parse_float(m.get("body_length"), "measurements.body_length"),
        "sleeve_length": _parse_float(m.get("sleeve_length"), "measurements.sleeve_length"),
    }
    for opt_field in ("upper_arm", "neck_circumference", "wrist", "cross_back"):
        v = _parse_optional_float(m.get(opt_field))
        if v is not None:
            m_kwargs[opt_field] = v
    body_measurements = BodyMeasurements(**m_kwargs)

    # ── Ease ───────────────────────────────────────────────────────────────────
    ease_name = data.get("ease", "classic")
    ease_factory = _EASE_PRESETS.get(ease_name, EaseProfile.classic)
    ease = ease_factory()

    # ── Grade ──────────────────────────────────────────────────────────────────
    opts = data.get("options") or {}
    request = GradingRequest(
        spec=spec,
        gauge=gauge,
        body_measurements=body_measurements,
        ease=ease,
        output_pattern_name=opts.get("pattern_name") or spec.pattern_name or "My Pattern",
    )

    graded = grade(request)
    issues = validate(graded)

    warnings = [str(i) for i in issues if i.severity.value != "error"]
    if has_errors(issues):
        error_msgs = [str(i) for i in issues if i.severity.value == "error"]
        raise ValueError("Validation failed: " + "; ".join(error_msgs))

    pattern_name = (opts.get("pattern_name") or spec.pattern_name or "My Pattern").strip()
    designer = (opts.get("designer") or spec.designer or "(your name)").strip()

    return write_pattern(graded, pattern_name, designer, "Intermediate", issues), warnings
