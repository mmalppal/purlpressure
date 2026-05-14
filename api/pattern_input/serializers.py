"""JSON ↔ PatternSpec serialization for saving and loading forms."""

from __future__ import annotations

import dataclasses
import json
from typing import Any

from .models import (
    ConstructionType,
    LengthMeasurements,
    PatternGauge,
    PatternSpec,
    ShapingRates,
    SizeEntry,
    StitchCounts,
)


def to_dict(spec: PatternSpec) -> dict:
    """Convert PatternSpec to a plain dict (JSON-safe)."""
    d = dataclasses.asdict(spec)
    # Enum → string
    d["construction"] = spec.construction.value
    return d


def to_json(spec: PatternSpec, indent: int = 2) -> str:
    """Serialize a PatternSpec to a JSON string."""
    return json.dumps(to_dict(spec), indent=indent, ensure_ascii=False)


def from_dict(d: dict) -> PatternSpec:
    """Deserialize a PatternSpec from a plain dict."""
    d = dict(d)  # shallow copy — don't mutate caller's dict

    # Construction enum
    d["construction"] = ConstructionType(d.get("construction", "top_down_raglan"))

    # Nested objects
    if d.get("gauge") is not None:
        d["gauge"] = PatternGauge(**d["gauge"])

    d["sizes"] = [SizeEntry(**s) for s in d.get("sizes", [])]
    d["stitches"] = StitchCounts(**d.get("stitches", {}))
    d["lengths"] = LengthMeasurements(**d.get("lengths", {}))
    d["shaping"] = ShapingRates(**d.get("shaping", {}))

    d.setdefault("notes", [])
    d.setdefault("unknown_fields", [])

    return PatternSpec(**d)


def from_json(data: str) -> PatternSpec:
    """Deserialize a PatternSpec from a JSON string."""
    return from_dict(json.loads(data))


def save_to_file(spec: PatternSpec, path: str) -> None:
    """Save a PatternSpec to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(to_json(spec))


def load_from_file(path: str) -> PatternSpec:
    """Load a PatternSpec from a JSON file."""
    with open(path, encoding="utf-8") as f:
        return from_json(f.read())
