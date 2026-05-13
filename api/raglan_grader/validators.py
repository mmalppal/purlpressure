"""Post-grading sanity checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .raglan import GradedRaglan


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    severity: Severity
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.code}: {self.message}"


def validate(graded: GradedRaglan) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    m = graded.measurements
    g = graded.gauge
    spi = g.sts_per_inch

    if graded.cast_on_components_check != graded.cast_on_total:
        issues.append(ValidationIssue(
            code="CAST_ON_MISMATCH",
            severity=Severity.ERROR,
            message=(
                f"cast_on parts ({graded.cast_on_back} back + {graded.cast_on_front} front + "
                f"2 * {graded.cast_on_each_sleeve} sleeve + {graded.cast_on_raglan_markers} raglan = "
                f"{graded.cast_on_components_check}) do not sum to cast_on_total={graded.cast_on_total}."
            ),
        ))

    yoke = graded.yoke
    if yoke.total_inc_rounds_in_yoke + yoke.body_only_below_join_rounds < 4:
        issues.append(ValidationIssue(
            code="YOKE_TOO_SHALLOW",
            severity=Severity.ERROR,
            message=f"Only {yoke.total_inc_rounds_in_yoke} yoke increase rounds planned — minimum 4.",
        ))

    B0 = graded.cast_on_back + graded.cast_on_front
    expected_body_at_join = (
        B0 + 4 * (yoke.full_raglan_rounds + yoke.body_only_in_yoke_rounds) + 2 * graded.underarm_cast_on
    )
    if expected_body_at_join != graded.body.sts_at_join:
        issues.append(ValidationIssue(
            code="BODY_JOIN_MISMATCH",
            severity=Severity.ERROR,
            message=f"body sts at join ({graded.body.sts_at_join}) doesn't match computed ({expected_body_at_join}).",
        ))

    S0 = graded.cast_on_each_sleeve
    expected_sleeve = S0 + 2 * (yoke.full_raglan_rounds + yoke.sleeve_only_in_yoke_rounds) + graded.underarm_cast_on
    if expected_sleeve != graded.sleeve.sts_at_underarm:
        issues.append(ValidationIssue(
            code="SLEEVE_UNDERARM_MISMATCH",
            severity=Severity.ERROR,
            message=f"sleeve sts at underarm ({graded.sleeve.sts_at_underarm}) doesn't match computed ({expected_sleeve}).",
        ))

    expected_chest = expected_body_at_join + 4 * yoke.body_only_below_join_rounds
    if expected_chest != graded.body.sts_at_chest:
        issues.append(ValidationIssue(
            code="CHEST_MISMATCH",
            severity=Severity.ERROR,
            message=f"body sts at chest ({graded.body.sts_at_chest}) doesn't match computed ({expected_chest}).",
        ))

    if graded.finished_upper_arm >= graded.finished_bust / 2:
        issues.append(ValidationIssue(
            code="SLEEVE_VS_BUST_RATIO",
            severity=Severity.WARNING,
            message=f"upper arm {graded.finished_upper_arm:.2f}\" is more than half the bust {graded.finished_bust:.2f}\".",
        ))

    if graded.yoke_depth < 7.5:
        issues.append(ValidationIssue(
            code="YOKE_DEPTH_LOW",
            severity=Severity.WARNING,
            message=f"yoke depth {graded.yoke_depth}\" is below the 7.5\" minimum for any adult raglan.",
        ))

    if m.bust >= 50 and graded.yoke_depth < 10.5:
        issues.append(ValidationIssue(
            code="YOKE_DEPTH_LOW_PLUS",
            severity=Severity.WARNING,
            message=f"yoke depth {graded.yoke_depth}\" is shallow for plus bust {m.bust}\" — recommended ≥10.5\".",
        ))

    if graded.sleeve.dec_rounds > 0 and graded.sleeve.dec_interval < 2:
        issues.append(ValidationIssue(
            code="SLEEVE_DEC_TOO_FAST",
            severity=Severity.WARNING,
            message=f"sleeve dec interval {graded.sleeve.dec_interval} row(s) is faster than every other row.",
        ))

    if graded.sleeve.dec_rounds > 0 and graded.sleeve.dec_interval > 20:
        issues.append(ValidationIssue(
            code="SLEEVE_DEC_SPARSE",
            severity=Severity.INFO,
            message=f"sleeve dec interval {graded.sleeve.dec_interval} rows is very sparse — sleeve will be nearly straight.",
        ))

    if graded.body.waist_dec_rounds > 0 and graded.body.waist_dec_interval and graded.body.waist_dec_interval < 2:
        issues.append(ValidationIssue(
            code="WAIST_DEC_TOO_FAST",
            severity=Severity.WARNING,
            message=f"waist dec interval {graded.body.waist_dec_interval} row(s) is faster than every other row.",
        ))

    if graded.body.sts_at_waist and graded.body.sts_at_waist < graded.body.sts_at_chest * 0.5:
        issues.append(ValidationIssue(
            code="EXTREME_WAIST_SHAPING",
            severity=Severity.WARNING,
            message=f"waist sts {graded.body.sts_at_waist} is less than 50% of chest sts {graded.body.sts_at_chest}.",
        ))

    if m.bust >= 46 and graded.ease.upper_arm < 2.0:
        issues.append(ValidationIssue(
            code="PLUS_SLEEVE_EASE_TIGHT",
            severity=Severity.WARNING,
            message=f"upper arm ease {graded.ease.upper_arm:.2f}\" is tight for bust {m.bust}\" — plus sizes need ≥2\".",
        ))

    if m.bust >= 42 and (graded.front_back_short_rows is None or graded.front_back_short_rows.pairs == 0):
        issues.append(ValidationIssue(
            code="NO_BUST_SHORT_ROWS",
            severity=Severity.INFO,
            message=f"bust {m.bust}\" usually benefits from bust short rows for full bust projection — none planned.",
        ))

    if graded.finished_neck < 18.0:
        issues.append(ValidationIssue(
            code="NECK_BELOW_MIN",
            severity=Severity.WARNING,
            message=f"finished neck {graded.finished_neck:.2f}\" is below the 18\" head-circumference minimum.",
        ))

    if graded.finished_neck < graded.finished_bust * 0.32:
        issues.append(ValidationIssue(
            code="TIGHT_NECK",
            severity=Severity.INFO,
            message=(
                f"neck is {graded.finished_neck / graded.finished_bust * 100:.1f}% of bust "
                "— tight neckline. Acceptable for crew but binding for boatneck."
            ),
        ))

    if graded.finished_neck > graded.finished_bust * 0.65:
        issues.append(ValidationIssue(
            code="WIDE_NECK",
            severity=Severity.INFO,
            message=f"neck is {graded.finished_neck / graded.finished_bust * 100:.1f}% of bust — very wide; may slip off shoulder.",
        ))

    if yoke.body_only_in_yoke_rounds > 0 or yoke.body_only_below_join_rounds > 0:
        bits = []
        if yoke.body_only_in_yoke_rounds:
            bits.append(f"{yoke.body_only_in_yoke_rounds} in yoke")
        if yoke.body_only_below_join_rounds:
            bits.append(f"{yoke.body_only_below_join_rounds} below join")
        issues.append(ValidationIssue(
            code="BODY_ONLY_INC_USED",
            severity=Severity.INFO,
            message="Asymmetric raglan used: body-only increase rounds added (" + ", ".join(bits) + ").",
        ))

    return issues


def has_errors(issues: list[ValidationIssue]) -> bool:
    return any(i.severity is Severity.ERROR for i in issues)
