"""Body measurements + plus-size-aware estimators."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Optional


def estimate_upper_arm(bust: float) -> float:
    if bust <= 42:
        return bust * 0.30 + 1.0
    return 12.6 + 1.0 + (bust - 42) * 0.35


def estimate_neck_circumference(bust: float) -> float:
    if bust <= 42:
        return bust * 0.17 + 6.0
    return 42 * 0.17 + 6.0 + (bust - 42) * 0.12


def estimate_cross_back(bust: float) -> float:
    if bust <= 42:
        return bust * 0.32 + 0.5
    if bust <= 50:
        return 42 * 0.32 + 0.5 + (bust - 42) * 0.20
    return 42 * 0.32 + 0.5 + 8 * 0.20 + (bust - 50) * 0.10


def estimate_wrist(bust: float) -> float:
    if bust <= 42:
        return bust * 0.14 + 0.5
    return 42 * 0.14 + 0.5 + (bust - 42) * 0.08


def estimate_yoke_depth(bust: float) -> float:
    if bust <= 36:
        return 8.0 + (bust - 32) * 0.125
    if bust <= 46:
        return 8.5 + (bust - 36) * 0.20
    return 10.5 + (bust - 46) * 0.25


def estimate_front_back_differential(bust: float) -> float:
    if bust <= 38:
        return 0.0
    if bust <= 46:
        return (bust - 38) * 0.125
    return 1.0 + (bust - 46) * 0.15


@dataclass
class BodyMeasurements:
    bust: float
    yoke_depth: float
    body_length: float
    sleeve_length: float

    upper_arm: Optional[float] = None
    neck_circumference: Optional[float] = None
    cross_back: Optional[float] = None
    wrist: Optional[float] = None

    waist: Optional[float] = None
    high_hip: Optional[float] = None
    waist_above_underarm: Optional[float] = None

    front_back_differential: Optional[float] = None
    sloped_shoulder_drop: float = 0.0

    auto_estimate_front_back: bool = True

    estimated_fields: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        for name in ("bust", "yoke_depth", "body_length", "sleeve_length"):
            v = getattr(self, name)
            if v is None or v <= 0:
                raise ValueError(f"{name} must be positive, got {v!r}")
        if self.bust < 20 or self.bust > 80:
            raise ValueError(
                f"bust={self.bust} is outside the supported range (20-80 inches). "
                "Double-check the unit."
            )
        if self.sloped_shoulder_drop < 0 or self.sloped_shoulder_drop > 2.0:
            raise ValueError(
                f"sloped_shoulder_drop={self.sloped_shoulder_drop} should be "
                "in [0, 2.0] inches."
            )

    def fill_defaults(self) -> "BodyMeasurements":
        result = replace(self, estimated_fields=list(self.estimated_fields))
        if result.upper_arm is None:
            result.upper_arm = estimate_upper_arm(result.bust)
            result.estimated_fields.append("upper_arm")
        if result.neck_circumference is None:
            result.neck_circumference = estimate_neck_circumference(result.bust)
            result.estimated_fields.append("neck_circumference")
        if result.cross_back is None:
            result.cross_back = estimate_cross_back(result.bust)
            result.estimated_fields.append("cross_back")
        if result.wrist is None:
            result.wrist = estimate_wrist(result.bust)
            result.estimated_fields.append("wrist")
        if result.front_back_differential is None and result.auto_estimate_front_back:
            result.front_back_differential = estimate_front_back_differential(result.bust)
            if result.front_back_differential > 0:
                result.estimated_fields.append("front_back_differential")
        elif result.front_back_differential is None:
            result.front_back_differential = 0.0
        if result.waist is not None and result.waist_above_underarm is None:
            result.waist_above_underarm = max(2.0, result.body_length * 0.45)
            result.estimated_fields.append("waist_above_underarm")
        return result
