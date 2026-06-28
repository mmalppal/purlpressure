"""Route a GradingRequest to the correct grading engine."""

from __future__ import annotations

from .models import ConstructionType, GradingRequest


def grade(request: GradingRequest):
    """Route a GradingRequest to the correct grading engine."""
    spec = request.spec

    if spec.construction == ConstructionType.TOP_DOWN_RAGLAN:
        return _grade_raglan(request)
    elif spec.construction == ConstructionType.BOTTOM_UP_SEAMED:
        return _grade_bottom_up_seamed(request)
    elif spec.construction == ConstructionType.DROP_SHOULDER:
        return _grade_drop_shoulder(request)
    else:
        raise NotImplementedError(
            f"Grading for {spec.construction.value!r} is not yet implemented."
        )


def _grade_raglan(request: GradingRequest):
    """Route top-down raglan to raglan_grader.grade_raglan.

    Uses ratios from the original pattern spec to anchor the graded version.
    Currently passes through without override — sleeve_neck_fraction_override
    support requires an upstream change to grade_raglan().
    """
    try:
        from raglan_grader import grade_raglan  # type: ignore[import]
    except ImportError:
        raise ImportError(
            "raglan_grader is not installed. Run: pip install -e ../raglan_grader"
        )

    spec = request.spec
    # Note: sleeve_neck_fraction_override is not yet supported by grade_raglan().
    # The ratio from the original pattern (spec.stitches.each_sleeve_cast_on /
    # spec.stitches.neck_cast_on) could anchor the graded sleeve proportion, but
    # until grade_raglan() accepts this parameter we use the engine's default.

    return grade_raglan(
        gauge=request.gauge,
        measurements=request.body_measurements,
        ease=request.ease,
    )


def _grade_bottom_up_seamed(request: GradingRequest):
    raise NotImplementedError(
        "Bottom-up seamed grading is on the roadmap. "
        "Use the top-down raglan engine for now."
    )


def _grade_drop_shoulder(request: GradingRequest):
    raise NotImplementedError("Drop shoulder grading coming soon.")
