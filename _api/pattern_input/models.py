"""Pattern input data model.

The user reads their purchased pattern and fills in these fields.
No PDF parsing — direct human transfer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConstructionType(str, Enum):
    TOP_DOWN_RAGLAN  = "top_down_raglan"
    BOTTOM_UP_SEAMED = "bottom_up_seamed"
    DROP_SHOULDER    = "drop_shoulder"
    TOP_DOWN_YOKE    = "top_down_yoke"   # future
    SET_IN_SLEEVE    = "set_in_sleeve"   # future


@dataclass
class PatternGauge:
    sts_per_4in: float
    rows_per_4in: float
    swatch_stitch: str = "stockinette"
    note: str = ""          # e.g. "blocked" or "unblocked"


@dataclass
class SizeEntry:
    """One size column from the original pattern."""
    label: str               # e.g. "S", "M", "2XL"
    finished_bust: float     # finished garment measurement (not body)
    finished_length: Optional[float] = None
    finished_sleeve: Optional[float] = None
    finished_upper_arm: Optional[float] = None
    target_body_bust: Optional[float] = None  # body size this size fits


@dataclass
class StitchCounts:
    """Key stitch counts entered by the user from their pattern."""

    # ── Top-down raglan ──────────────────────────────────────────────────────
    neck_cast_on: Optional[int] = None
    back_cast_on: Optional[int] = None
    front_cast_on: Optional[int] = None
    each_sleeve_cast_on: Optional[int] = None
    body_at_yoke_end: Optional[int] = None
    each_sleeve_at_yoke_end: Optional[int] = None
    underarm_cast_on_each: Optional[int] = None
    body_at_chest: Optional[int] = None
    each_sleeve_at_underarm: Optional[int] = None
    body_at_waist: Optional[int] = None
    body_at_hem: Optional[int] = None
    each_sleeve_at_cuff: Optional[int] = None

    # ── Bottom-up seamed (per piece: front or back) ──────────────────────────
    hem_cast_on: Optional[int] = None
    waist_sts: Optional[int] = None
    bust_sts: Optional[int] = None
    armhole_bind_off: Optional[int] = None
    shoulder_sts: Optional[int] = None
    neck_bind_off: Optional[int] = None
    sleeve_cast_on: Optional[int] = None
    sleeve_at_underarm: Optional[int] = None
    sleeve_cap_rows: Optional[int] = None


@dataclass
class LengthMeasurements:
    """Key vertical lengths from the original pattern (inches)."""
    yoke_depth: Optional[float] = None
    body_length_total: Optional[float] = None
    sleeve_length_total: Optional[float] = None
    waist_above_hem: Optional[float] = None
    bust_above_waist: Optional[float] = None
    armhole_depth: Optional[float] = None
    neckband_depth: Optional[float] = None
    hem_ribbing_depth: Optional[float] = None
    cuff_ribbing_depth: Optional[float] = None


@dataclass
class ShapingRates:
    """Decrease/increase intervals from the original pattern (every N rows)."""
    raglan_inc_every_n_rows: Optional[int] = None  # typically 2
    waist_dec_every_n_rows: Optional[int] = None
    waist_dec_sts_per_round: Optional[int] = None  # typically 4
    hip_inc_every_n_rows: Optional[int] = None
    hip_inc_sts_per_round: Optional[int] = None
    sleeve_dec_every_n_rows: Optional[int] = None
    sleeve_dec_sts_per_round: Optional[int] = None  # typically 2
    armhole_dec_every_n_rows: Optional[int] = None
    armhole_dec_sts_per_row: Optional[int] = None


@dataclass
class PatternSpec:
    """Complete structured representation of a knitting pattern as entered by the user."""

    # Pattern metadata
    pattern_name: str
    designer: str = ""
    source_url: str = ""
    construction: ConstructionType = ConstructionType.TOP_DOWN_RAGLAN

    # Gauge
    gauge: Optional[PatternGauge] = None

    # Original sizes
    sizes: list[SizeEntry] = field(default_factory=list)
    reference_size: str = ""  # which size the user is grading FROM

    # Stitch counts (for reference_size)
    stitches: StitchCounts = field(default_factory=StitchCounts)

    # Lengths (for reference_size)
    lengths: LengthMeasurements = field(default_factory=LengthMeasurements)

    # Shaping rates (for reference_size)
    shaping: ShapingRates = field(default_factory=ShapingRates)

    # Notes and unknowns
    notes: list[str] = field(default_factory=list)
    unknown_fields: list[str] = field(default_factory=list)

    @property
    def reference_size_entry(self) -> Optional[SizeEntry]:
        """Return the SizeEntry for reference_size, or None."""
        for s in self.sizes:
            if s.label == self.reference_size:
                return s
        return None


@dataclass
class GradingRequest:
    """Everything needed to produce a regraded pattern."""
    spec: PatternSpec
    gauge: "Gauge"                  # from raglan_grader.Gauge
    body_measurements: "BodyMeasurements"  # from raglan_grader.BodyMeasurements
    ease: "EaseProfile"             # from raglan_grader.EaseProfile
    output_pattern_name: str = ""
