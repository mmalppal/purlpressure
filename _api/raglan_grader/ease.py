"""Ease profile presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EaseProfile:
    bust: float
    upper_arm: float
    neck: float
    wrist: float
    waist: float = 0.0
    high_hip: float = 0.0
    underarm_comfort: float = 0.75
    front_bias: float = 0.0

    @classmethod
    def skin_tight(cls) -> "EaseProfile":
        return cls(bust=-2.0, upper_arm=-1.0, neck=0.5, wrist=-0.5, underarm_comfort=0.5)

    @classmethod
    def close_fitting(cls) -> "EaseProfile":
        return cls(bust=1.0, upper_arm=1.0, neck=1.0, wrist=0.5, underarm_comfort=0.5)

    @classmethod
    def classic(cls) -> "EaseProfile":
        return cls(bust=3.0, upper_arm=2.0, neck=2.0, wrist=1.0, underarm_comfort=0.75)

    @classmethod
    def relaxed(cls) -> "EaseProfile":
        return cls(bust=5.0, upper_arm=3.0, neck=2.5, wrist=1.5, underarm_comfort=1.0)

    @classmethod
    def oversized(cls) -> "EaseProfile":
        return cls(bust=8.0, upper_arm=4.0, neck=3.0, wrist=2.0, underarm_comfort=1.25)

    @classmethod
    def plus_friendly_classic(cls) -> "EaseProfile":
        return cls(
            bust=3.5,
            upper_arm=2.5,
            neck=2.0,
            wrist=1.0,
            underarm_comfort=1.0,
            front_bias=0.25,
        )

    def describe(self) -> str:
        parts = [
            f"bust {_signed(self.bust)}",
            f"upper arm {_signed(self.upper_arm)}",
            f"neck {_signed(self.neck)}",
            f"wrist {_signed(self.wrist)}",
            f"underarm CO {self.underarm_comfort:.2f}\"",
        ]
        if self.front_bias > 0:
            parts.append(f"front bias {self.front_bias:.2f}")
        return ", ".join(parts)


def _signed(v: float) -> str:
    sign = "+" if v >= 0 else "-"
    return f"{sign}{abs(v):.2f}\""
