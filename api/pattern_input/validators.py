"""Validation rules for PatternSpec.

Returns a list of ValidationResult objects. Each has:
  - field: str — which field triggered it
  - severity: "error" | "warning" | "info"
  - message: str — human-readable, actionable

Run all validators with `validate_spec(spec)`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import ConstructionType, PatternSpec


@dataclass
class ValidationResult:
    field: str
    severity: str   # "error" | "warning" | "info"
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.field}: {self.message}"

    @property
    def is_error(self) -> bool:
        return self.severity == "error"

    @property
    def is_warning(self) -> bool:
        return self.severity == "warning"


def _err(field: str, msg: str) -> ValidationResult:
    return ValidationResult(field=field, severity="error", message=msg)


def _warn(field: str, msg: str) -> ValidationResult:
    return ValidationResult(field=field, severity="warning", message=msg)


def _info(field: str, msg: str) -> ValidationResult:
    return ValidationResult(field=field, severity="info", message=msg)


def validate_spec(spec: PatternSpec) -> list[ValidationResult]:
    """Run all validation rules. Returns a list of issues (may be empty)."""
    issues: list[ValidationResult] = []

    issues.extend(_validate_gauge(spec))
    issues.extend(_validate_sizes(spec))

    if spec.construction == ConstructionType.TOP_DOWN_RAGLAN:
        issues.extend(_validate_raglan_stitches(spec))
    elif spec.construction == ConstructionType.BOTTOM_UP_SEAMED:
        issues.extend(_validate_bottomup_stitches(spec))

    issues.extend(_validate_lengths(spec))
    issues.extend(_validate_gauge_stitch_consistency(spec))

    return issues


def has_errors(issues: list[ValidationResult]) -> bool:
    return any(i.is_error for i in issues)


# ── Gauge ──────────────────────────────────────────────────────────────────────

def _validate_gauge(spec: PatternSpec) -> list[ValidationResult]:
    issues = []
    g = spec.gauge
    if g is None:
        return [_err("gauge", "Gauge is required.")]

    if g.sts_per_4in <= 0 or g.sts_per_4in >= 50:
        issues.append(_err("gauge.sts_per_4in",
            f"Stitches per 4\" must be between 0 and 50, got {g.sts_per_4in}."))

    if g.rows_per_4in <= 0 or g.rows_per_4in >= 80:
        issues.append(_err("gauge.rows_per_4in",
            f"Rows per 4\" must be between 0 and 80, got {g.rows_per_4in}."))

    if g.sts_per_4in > 0 and g.rows_per_4in > 0:
        if g.rows_per_4in < g.sts_per_4in:
            issues.append(_warn("gauge",
                f"Rows per 4\" ({g.rows_per_4in}) is less than stitches per 4\" "
                f"({g.sts_per_4in}). This is unusual — have you swapped them?"))

        sts_per_inch = g.sts_per_4in / 4
        if sts_per_inch > 10:
            issues.append(_warn("gauge.sts_per_4in",
                f"More than 10 sts/inch ({sts_per_inch:.1f}) is very fine lace weight. "
                "Double-check you're entering stitches per 4\", not per 1\"."))

    return issues


# ── Sizes ──────────────────────────────────────────────────────────────────────

def _validate_sizes(spec: PatternSpec) -> list[ValidationResult]:
    issues = []
    if not spec.sizes:
        issues.append(_warn("sizes", "No pattern sizes entered."))
        return issues

    if spec.reference_size and spec.reference_size_entry is None:
        issues.append(_err("reference_size",
            f"Reference size '{spec.reference_size}' not found in sizes list."))

    for s in spec.sizes:
        if s.finished_bust <= 0:
            issues.append(_err(f"sizes[{s.label}].finished_bust",
                f"Finished bust for size {s.label} must be positive."))

    return issues


# ── Raglan stitch counts ───────────────────────────────────────────────────────

def _validate_raglan_stitches(spec: PatternSpec) -> list[ValidationResult]:
    issues = []
    st = spec.stitches

    # Cast-on parts must sum to total
    parts = [st.back_cast_on, st.front_cast_on, st.each_sleeve_cast_on, st.neck_cast_on]
    if all(v is not None for v in parts):
        computed = st.back_cast_on + st.front_cast_on + 2 * st.each_sleeve_cast_on + 4
        diff = abs(computed - st.neck_cast_on)
        if diff > 4:
            issues.append(_err("stitches.neck_cast_on",
                f"Cast-on parts don't add up: back ({st.back_cast_on}) + front "
                f"({st.front_cast_on}) + 2×sleeve ({st.each_sleeve_cast_on}) + 4 markers "
                f"= {computed}, but total is {st.neck_cast_on} (off by {diff})."))
        elif diff > 2:
            issues.append(_warn("stitches.neck_cast_on",
                f"Cast-on parts sum to {computed} but total is {st.neck_cast_on}. "
                "Small discrepancies are normal (raglan marker style varies). Double-check."))

    # Body at chest > body at yoke end
    if st.body_at_chest is not None and st.body_at_yoke_end is not None:
        if st.body_at_chest <= st.body_at_yoke_end:
            issues.append(_err("stitches.body_at_chest",
                f"Body at chest ({st.body_at_chest}) must be greater than body at yoke "
                f"end ({st.body_at_yoke_end}). The body only grows after the yoke."))

    # Sleeve at underarm >= sleeve at yoke end
    if st.each_sleeve_at_underarm is not None and st.each_sleeve_at_yoke_end is not None:
        if st.each_sleeve_at_underarm < st.each_sleeve_at_yoke_end:
            issues.append(_err("stitches.each_sleeve_at_underarm",
                f"Sleeve at underarm ({st.each_sleeve_at_underarm}) is less than sleeve "
                f"at yoke end ({st.each_sleeve_at_yoke_end}). Sleeves don't shrink after "
                "separation."))

    # Waist shaping: waist < chest
    if st.body_at_waist is not None and st.body_at_chest is not None:
        if st.body_at_waist > st.body_at_chest:
            issues.append(_err("stitches.body_at_waist",
                f"Waist sts ({st.body_at_waist}) cannot exceed chest sts "
                f"({st.body_at_chest})."))
        elif st.body_at_waist > 0.95 * st.body_at_chest:
            issues.append(_warn("stitches.body_at_waist",
                f"Waist sts ({st.body_at_waist}) is more than 95% of chest sts "
                f"({st.body_at_chest}). Very minimal waist shaping — is this intentional?"))

    # Hem >= waist
    if st.body_at_hem is not None and st.body_at_waist is not None:
        if st.body_at_hem < st.body_at_waist:
            issues.append(_err("stitches.body_at_hem",
                f"Hem sts ({st.body_at_hem}) is less than waist sts ({st.body_at_waist}). "
                "The body should widen from waist to hem."))
        elif st.body_at_hem == st.body_at_waist:
            issues.append(_warn("stitches.body_at_hem",
                f"Hem sts ({st.body_at_hem}) equals waist sts — no hip shaping. "
                "Is this a straight tube from waist to hem?"))

    return issues


# ── Bottom-up seamed stitch counts ────────────────────────────────────────────

def _validate_bottomup_stitches(spec: PatternSpec) -> list[ValidationResult]:
    issues = []
    st = spec.stitches

    # Waist < hem cast-on
    if st.waist_sts is not None and st.hem_cast_on is not None:
        if st.waist_sts >= st.hem_cast_on:
            issues.append(_err("stitches.waist_sts",
                f"Waist sts ({st.waist_sts}) should be less than hem cast-on "
                f"({st.hem_cast_on}) for a fitted garment."))

    # Bust >= waist
    if st.bust_sts is not None and st.waist_sts is not None:
        if st.bust_sts < st.waist_sts:
            issues.append(_err("stitches.bust_sts",
                f"Bust sts ({st.bust_sts}) is less than waist sts ({st.waist_sts}). "
                "A garment can't be wider at the waist than the bust."))

    # Shoulder < bust
    if st.shoulder_sts is not None and st.bust_sts is not None:
        if st.shoulder_sts >= st.bust_sts:
            issues.append(_err("stitches.shoulder_sts",
                f"Shoulder sts ({st.shoulder_sts}) should be less than bust sts "
                f"({st.bust_sts})."))

    # Neck < shoulder
    if st.neck_bind_off is not None and st.shoulder_sts is not None:
        if st.neck_bind_off >= st.shoulder_sts:
            issues.append(_err("stitches.neck_bind_off",
                f"Neck bind-off ({st.neck_bind_off}) should be less than shoulder "
                f"sts ({st.shoulder_sts})."))

    return issues


# ── Length reasonableness ──────────────────────────────────────────────────────

def _validate_lengths(spec: PatternSpec) -> list[ValidationResult]:
    issues = []
    ln = spec.lengths

    checks = [
        ("yoke_depth",          ln.yoke_depth,          6.0,  15.0,
         "Yoke depth"),
        ("body_length_total",   ln.body_length_total,   8.0,  30.0,
         "Body length"),
        ("sleeve_length_total", ln.sleeve_length_total, 3.0,  25.0,
         "Sleeve length"),
    ]
    for field_name, value, lo, hi, label in checks:
        if value is not None and (value < lo or value > hi):
            issues.append(_warn(f"lengths.{field_name}",
                f"{label} of {value}\" is outside the expected range ({lo}\"–{hi}\"). "
                "Double-check units (should be inches)."))

    # Armhole depth ≈ (finished_bust / 4) × 0.7..1.0
    ref = spec.reference_size_entry
    if ln.armhole_depth is not None and ref is not None:
        expected_lo = ref.finished_bust / 4 * 0.7
        expected_hi = ref.finished_bust / 4 * 1.0
        if not (expected_lo <= ln.armhole_depth <= expected_hi):
            issues.append(_info("lengths.armhole_depth",
                f"Armhole depth {ln.armhole_depth}\" is outside the typical range "
                f"({expected_lo:.1f}\"–{expected_hi:.1f}\") for a {ref.finished_bust}\" bust. "
                "This is just a heads-up — shaped armholes vary widely."))

    return issues


# ── Gauge ↔ stitch count consistency ──────────────────────────────────────────

def _validate_gauge_stitch_consistency(spec: PatternSpec) -> list[ValidationResult]:
    """The most powerful validator: verify gauge × stitch count ≈ finished bust."""
    issues = []
    g = spec.gauge
    ref = spec.reference_size_entry
    if g is None or ref is None or g.sts_per_4in <= 0:
        return issues

    sts_per_inch = g.sts_per_4in / 4

    # Top-down raglan: use body_at_chest (full round ÷ sts_per_inch)
    if spec.construction == ConstructionType.TOP_DOWN_RAGLAN:
        body_sts = spec.stitches.body_at_chest
        if body_sts is not None:
            computed_bust = body_sts / sts_per_inch
            declared_bust = ref.finished_bust
            diff = abs(computed_bust - declared_bust)
            _add_consistency_issues(issues, computed_bust, declared_bust, diff,
                                    "body_at_chest", "top-down raglan body")

    # Bottom-up seamed: bust_sts × 2 (front + back) ÷ sts_per_inch
    elif spec.construction == ConstructionType.BOTTOM_UP_SEAMED:
        bust_sts = spec.stitches.bust_sts
        if bust_sts is not None:
            computed_bust = (bust_sts * 2) / sts_per_inch
            declared_bust = ref.finished_bust
            diff = abs(computed_bust - declared_bust)
            _add_consistency_issues(issues, computed_bust, declared_bust, diff,
                                    "bust_sts", "bottom-up bust (front + back)")

    return issues


def _add_consistency_issues(
    issues: list[ValidationResult],
    computed: float,
    declared: float,
    diff: float,
    field_name: str,
    context: str,
) -> None:
    if 1.0 < diff <= 2.0:
        issues.append(_warn(f"stitches.{field_name}",
            f"Gauge + stitch count gives a {context} of {computed:.1f}\", but the pattern "
            f"declares {declared:.1f}\" (off by {diff:.1f}\"). Check your entry."))
    elif diff > 2.0:
        issues.append(_err(f"stitches.{field_name}",
            f"Gauge + stitch count gives a {context} of {computed:.1f}\", but the pattern "
            f"declares {declared:.1f}\" (off by {diff:.1f}\"). There is likely an entry "
            "error — check gauge, stitch count, or finished bust."))


# ── Grading feasibility ────────────────────────────────────────────────────────

def validate_grading_feasibility(
    spec: PatternSpec,
    user_bust: float,
) -> list[ValidationResult]:
    """Check whether grading is feasible given the user's bust vs the pattern."""
    issues = []
    ref = spec.reference_size_entry
    if ref is None:
        return issues

    ref_bust = ref.finished_bust
    ratio = user_bust / ref_bust if ref_bust > 0 else 1.0

    if ratio < 0.7:
        issues.append(_warn("body_measurements.bust",
            f"Your bust ({user_bust}\") is less than 70% of the reference size "
            f"({ref_bust}\"). Grading down this far may not produce good results."))
    elif ratio > 1.5:
        issues.append(_warn("body_measurements.bust",
            f"Your bust ({user_bust}\") is more than 150% of the reference size "
            f"({ref_bust}\"). Plus-size corrections will be applied."))
    else:
        issues.append(_info("body_measurements.bust",
            f"Grading {'up' if ratio > 1 else 'down'} from {ref_bust}\" → {user_bust}\"."))

    return issues
