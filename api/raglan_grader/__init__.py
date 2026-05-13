"""raglan_grader — plus-size-aware grading for top-down raglan sweaters."""

from .ease import EaseProfile
from .gauge import Gauge
from .measurements import (
    BodyMeasurements,
    estimate_cross_back,
    estimate_front_back_differential,
    estimate_neck_circumference,
    estimate_upper_arm,
    estimate_wrist,
    estimate_yoke_depth,
)
from .pattern_writer import write_pattern
from .raglan import (
    BodyShaping,
    FrontBackDifferential,
    GradedRaglan,
    SleeveShaping,
    YokeIncreasePlan,
    grade_raglan,
)
from .validators import Severity, ValidationIssue, has_errors, validate

__all__ = [
    "BodyMeasurements",
    "BodyShaping",
    "EaseProfile",
    "FrontBackDifferential",
    "Gauge",
    "GradedRaglan",
    "Severity",
    "SleeveShaping",
    "ValidationIssue",
    "YokeIncreasePlan",
    "estimate_cross_back",
    "estimate_front_back_differential",
    "estimate_neck_circumference",
    "estimate_upper_arm",
    "estimate_wrist",
    "estimate_yoke_depth",
    "grade_raglan",
    "has_errors",
    "validate",
    "write_pattern",
]

__version__ = "0.1.0"
