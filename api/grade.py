"""Vercel Python serverless function — raglan pattern grader.

POST /api/grade
Body (JSON):
  gauge:        { sts_per_4in, rows_per_4in }
  measurements: { bust, yoke_depth, body_length, sleeve_length,
                  upper_arm?, neck_circumference?, wrist?, cross_back? }
  ease:         "classic" | "plus_friendly_classic" | "close_fitting" |
                "relaxed" | "oversized"
  options:      { pattern_name?, designer?, skill_level?,
                  waist_shaping?: "auto"|"yes"|"no",
                  bust_short_rows?: "auto"|"yes"|"no",
                  body_only_inc_max_inches?: float }

Response (JSON):
  ok: true,  pattern: "<markdown string>"
  ok: false, error: "<message>"
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Vendor directory is alongside this file.
sys.path.insert(0, os.path.dirname(__file__))

from raglan_grader import (  # noqa: E402
    BodyMeasurements,
    EaseProfile,
    Gauge,
    grade_raglan,
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
            pattern = _process(data)
            self._respond(200, {"ok": True, "pattern": pattern})
        except ValueError as exc:
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
        pass  # suppress default request logging


def _process(data: dict) -> str:
    # ── Gauge ──────────────────────────────────────────────────────────────────
    g = data.get("gauge") or {}
    gauge = Gauge.from_4in_swatch(
        _parse_float(g.get("sts_per_4in"), "gauge.sts_per_4in"),
        _parse_float(g.get("rows_per_4in"), "gauge.rows_per_4in"),
    )

    # ── Measurements ──────────────────────────────────────────────────────────
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

    measurements = BodyMeasurements(**m_kwargs)

    # ── Ease ──────────────────────────────────────────────────────────────────
    ease_name = data.get("ease", "classic")
    ease_factory = _EASE_PRESETS.get(ease_name, EaseProfile.classic)
    ease = ease_factory()

    # ── Options ───────────────────────────────────────────────────────────────
    opts = data.get("options") or {}
    grade_kwargs: dict = {}

    ws = opts.get("waist_shaping", "auto")
    if ws == "yes":
        grade_kwargs["enable_waist_shaping"] = True
    elif ws == "no":
        grade_kwargs["enable_waist_shaping"] = False
    # "auto" → leave unset (engine decides based on whether waist was measured)

    bsr = opts.get("bust_short_rows", "auto")
    if bsr == "yes":
        grade_kwargs["enable_full_bust_short_rows"] = True
    elif bsr == "no":
        grade_kwargs["enable_full_bust_short_rows"] = False

    bmax = _parse_optional_float(opts.get("body_only_inc_max_inches"))
    if bmax is not None:
        grade_kwargs["body_only_inc_max_inches"] = bmax

    # ── Grade ─────────────────────────────────────────────────────────────────
    graded = grade_raglan(gauge, measurements, ease, **grade_kwargs)
    issues = validate(graded)

    if has_errors(issues):
        error_msgs = [str(i) for i in issues if i.severity.value == "error"]
        raise ValueError("Validation failed: " + "; ".join(error_msgs))

    pattern_name = (opts.get("pattern_name") or "My Raglan").strip() or "My Raglan"
    designer = (opts.get("designer") or "(your name)").strip() or "(your name)"
    skill_level = (opts.get("skill_level") or "Intermediate").strip() or "Intermediate"

    return write_pattern(graded, pattern_name, designer, skill_level, issues)
