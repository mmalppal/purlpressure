"""Gauge: stitches and rows per unit length."""

from __future__ import annotations

from dataclasses import dataclass

INCH_PER_CM = 1.0 / 2.54

_MIN_SPI = 1.0
_MAX_SPI = 20.0
_MIN_RPI = 1.0
_MAX_RPI = 30.0


@dataclass(frozen=True)
class Gauge:
    sts_per_inch: float
    rows_per_inch: float

    def __post_init__(self) -> None:
        if not (_MIN_SPI <= self.sts_per_inch <= _MAX_SPI):
            raise ValueError(
                f"sts_per_inch={self.sts_per_inch} is outside the plausible "
                f"range [{_MIN_SPI}, {_MAX_SPI}]. Did you swap stitches and rows?"
            )
        if not (_MIN_RPI <= self.rows_per_inch <= _MAX_RPI):
            raise ValueError(
                f"rows_per_inch={self.rows_per_inch} is outside the plausible "
                f"range [{_MIN_RPI}, {_MAX_RPI}]. Did you swap stitches and rows?"
            )
        if self.rows_per_inch < self.sts_per_inch * 0.9:
            raise ValueError(
                f"rows_per_inch ({self.rows_per_inch}) is much lower than "
                f"sts_per_inch ({self.sts_per_inch}). This is almost always a "
                "swap — swatches typically have more rows than stitches per inch."
            )

    @classmethod
    def from_4in_swatch(cls, sts_per_4in: float, rows_per_4in: float) -> "Gauge":
        return cls(sts_per_inch=sts_per_4in / 4.0, rows_per_inch=rows_per_4in / 4.0)

    @classmethod
    def from_10cm_swatch(cls, sts_per_10cm: float, rows_per_10cm: float) -> "Gauge":
        inches = 10.0 * INCH_PER_CM
        return cls(sts_per_inch=sts_per_10cm / inches, rows_per_inch=rows_per_10cm / inches)

    def sts_for_width(self, inches: float) -> int:
        return int(round(inches * self.sts_per_inch))

    def rows_for_length(self, inches: float) -> int:
        return int(round(inches * self.rows_per_inch))

    def width_for_sts(self, sts: int) -> float:
        return sts / self.sts_per_inch

    def length_for_rows(self, rows: int) -> float:
        return rows / self.rows_per_inch

    def describe(self) -> str:
        return (
            f"{self.sts_per_inch * 4:.1f} sts x "
            f"{self.rows_per_inch * 4:.1f} rows over 4 in "
            f"({self.sts_per_inch:.2f} spi, {self.rows_per_inch:.2f} rpi)"
        )
