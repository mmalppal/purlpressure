"""Raglan grading engine — see docs/math_derivation.md for the algebra."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .ease import EaseProfile
from .gauge import Gauge
from .measurements import BodyMeasurements, estimate_yoke_depth


MIN_SLEEVE_CAST_ON = 8
SLEEVE_NECK_FRACTION = 0.14
TARGET_UNDERARM_CAST_ON_IN = 1.5
SETUP_ROUNDS_AFTER_NECKBAND = 2
MAX_CONSECUTIVE_INC_FRACTION = 0.50


def round_to_even(value: float) -> int:
    r = int(round(value))
    if r % 2 == 0:
        return r
    lo, hi = r - 1, r + 1
    return lo if (value - lo) <= (hi - value) else hi


def round_to_multiple(value: float, base: int) -> int:
    return int(round(value / base)) * base


def round_up_to_multiple(value: int, base: int) -> int:
    if base <= 0:
        raise ValueError("base must be positive")
    return ((value + base - 1) // base) * base


@dataclass
class YokeIncreasePlan:
    full_raglan_rounds: int
    body_only_in_yoke_rounds: int
    sleeve_only_in_yoke_rounds: int
    body_only_below_join_rounds: int
    inc_frequency: int
    neckband_rounds: int
    setup_rounds: int
    consecutive_inc_rounds_bottom: int = 0
    sequence: list[tuple[str, int, int]] = field(default_factory=list)

    @property
    def total_inc_rounds_in_yoke(self) -> int:
        return (
            self.full_raglan_rounds
            + self.body_only_in_yoke_rounds
            + self.sleeve_only_in_yoke_rounds
        )

    @property
    def yoke_rows(self) -> int:
        rows = self.neckband_rounds + self.setup_rounds
        for _, n, freq in self.sequence:
            rows += n * freq
        return rows


@dataclass
class BodyShaping:
    sts_at_join: int
    sts_at_chest: int
    sts_at_waist: Optional[int]
    sts_at_high_hip: Optional[int]
    sts_at_hem: int
    rows_join_to_chest: int
    rows_chest_to_waist: Optional[int]
    rows_waist_to_high_hip: Optional[int]
    rows_high_hip_to_hem: int
    total_body_rows: int
    bust_short_row_pairs: int
    waist_dec_rounds: int
    waist_dec_interval: Optional[int]
    hip_inc_rounds: int
    hip_inc_interval: Optional[int]
    body_only_below_join_interval: int


@dataclass
class SleeveShaping:
    sts_at_underarm: int
    sts_at_cuff: int
    dec_rounds: int
    dec_interval: int
    cuff_straight_rows: int
    total_sleeve_rows: int


@dataclass
class FrontBackDifferential:
    extra_front_rows: int
    pairs: int


@dataclass
class GradedRaglan:
    gauge: Gauge
    measurements: BodyMeasurements
    ease: EaseProfile
    finished_bust: float
    finished_upper_arm: float
    finished_neck: float
    finished_wrist: float
    yoke_depth: float
    cast_on_total: int
    cast_on_back: int
    cast_on_front: int
    cast_on_each_sleeve: int
    cast_on_raglan_markers: int
    underarm_cast_on: int
    yoke: YokeIncreasePlan
    body: BodyShaping
    sleeve: SleeveShaping
    front_back_short_rows: Optional[FrontBackDifferential]
    notes: list[str] = field(default_factory=list)

    @property
    def sts_at_underarm_body(self) -> int:
        return self.body.sts_at_join

    @property
    def sts_at_underarm_sleeve(self) -> int:
        return self.sleeve.sts_at_underarm

    @property
    def cast_on_components_check(self) -> int:
        return (
            self.cast_on_back
            + self.cast_on_front
            + 2 * self.cast_on_each_sleeve
            + self.cast_on_raglan_markers
        )


def grade_raglan(
    gauge: Gauge,
    measurements: BodyMeasurements,
    ease: EaseProfile,
    *,
    enable_waist_shaping: Optional[bool] = None,
    enable_full_bust_short_rows: Optional[bool] = None,
    inc_frequency: int = 2,
    neckband_rounds: int = 6,
    body_only_inc_max_inches: float = 2.0,
    min_finished_neck: float = 18.0,
) -> GradedRaglan:
    if inc_frequency < 1:
        raise ValueError(f"inc_frequency must be ≥ 1, got {inc_frequency}")
    if neckband_rounds < 0:
        raise ValueError(f"neckband_rounds must be ≥ 0, got {neckband_rounds}")
    if body_only_inc_max_inches < 0:
        raise ValueError(f"body_only_inc_max_inches must be ≥ 0, got {body_only_inc_max_inches}")

    notes: list[str] = []
    m = measurements.fill_defaults()

    spi = gauge.sts_per_inch
    rpi = gauge.rows_per_inch

    finished_bust = m.bust + ease.bust
    raw_finished_upper_arm = m.upper_arm + ease.upper_arm
    finished_upper_arm = max(raw_finished_upper_arm, m.upper_arm + 1.0)
    if finished_upper_arm > raw_finished_upper_arm:
        notes.append(
            f"upper arm ease bumped to +1.0\" (was +{ease.upper_arm:.2f}\") to prevent strangulation"
        )
    raw_finished_neck = m.neck_circumference + ease.neck
    finished_neck = max(raw_finished_neck, min_finished_neck)
    if finished_neck > raw_finished_neck:
        notes.append(
            f"neckline widened to {finished_neck:.2f}\" (from {raw_finished_neck:.2f}\") so a "
            "pullover will fit over the head. Set min_finished_neck=0 for cardigan / zip / placket designs."
        )
    finished_wrist = m.wrist + ease.wrist

    bust_sts = round_to_even(finished_bust * spi)
    upper_arm_sts = round_to_even(finished_upper_arm * spi)
    if finished_neck > raw_finished_neck:
        neck_sts = round_up_to_multiple(int(finished_neck * spi + 0.5), 4)
    else:
        neck_sts = round_to_multiple(finished_neck * spi, 4)
    wrist_sts = round_to_even(finished_wrist * spi)

    finished_bust = bust_sts / spi
    finished_upper_arm = upper_arm_sts / spi
    finished_neck = neck_sts / spi
    finished_wrist = wrist_sts / spi

    S0 = max(MIN_SLEEVE_CAST_ON, round_to_even(neck_sts * SLEEVE_NECK_FRACTION))
    B0 = neck_sts - 4 - 2 * S0
    if B0 < 12:
        raise ValueError(
            f"Neck circumference {finished_neck:.2f}\" yields neck_sts={neck_sts}, "
            f"but B0 (body cast-on) would be {B0} — too small after allocating "
            "raglan markers and sleeves. Increase neck circumference, increase neck ease, "
            "or reduce sleeve allocation."
        )

    u_target = round_to_even(TARGET_UNDERARM_CAST_ON_IN * spi)
    if u_target < 4:
        u_target = 4

    body_target_at_chest = bust_sts - 2 * u_target
    sleeve_target_at_underarm = upper_arm_sts - u_target
    B_growth = body_target_at_chest - B0
    S_growth = sleeve_target_at_underarm - S0

    if B_growth < 0:
        raise ValueError(
            f"Body would need to SHRINK from cast-on ({B0} sts) to bust "
            f"({body_target_at_chest} sts before underarm). Neck is too large "
            "relative to bust. Reduce neck ease or check measurements."
        )

    if S_growth < 0:
        candidate_S0 = MIN_SLEEVE_CAST_ON
        candidate_B0 = neck_sts - 4 - 2 * candidate_S0
        candidate_S_growth = sleeve_target_at_underarm - candidate_S0
        if candidate_S_growth >= 0 and candidate_B0 >= 12:
            S0 = candidate_S0
            B0 = candidate_B0
            B_growth = body_target_at_chest - B0
            S_growth = candidate_S_growth
            notes.append(f"sleeve cast-on reduced to floor ({MIN_SLEEVE_CAST_ON}) so sleeve grows positively")
        else:
            adj_needed = abs(S_growth)
            adj = round_up_to_multiple(adj_needed, 2)
            upper_arm_sts += adj
            finished_upper_arm = upper_arm_sts / spi
            sleeve_target_at_underarm = upper_arm_sts - u_target
            S_growth = sleeve_target_at_underarm - S0
            notes.append(
                f"upper arm bumped by {adj} sts ({adj/spi:.2f}\") to accept minimum sleeve cast-on"
            )

    B_growth_aligned = round_up_to_multiple(B_growth, 4)
    S_growth_aligned = round_up_to_multiple(S_growth, 2)
    B_overshoot = B_growth_aligned - B_growth
    S_overshoot = S_growth_aligned - S_growth

    if B_overshoot:
        notes.append(
            f"body grew by {B_overshoot} extra sts ({B_overshoot/spi:.2f}\") to align "
            "increase rounds to clean multiples of 4 (raglan symmetry)"
        )
    if S_overshoot:
        notes.append(f"each sleeve grew by {S_overshoot} extra sts to align increase rounds")

    a = min(B_growth_aligned // 4, S_growth_aligned // 2)
    b = B_growth_aligned // 4 - a
    s = S_growth_aligned // 2 - a

    if a + b + s < 4:
        raise ValueError(
            f"Only {a + b + s} increase rounds total — yoke would have nearly no raglan shaping. "
            "Increase the bust vs neck delta or reduce ease."
        )

    yoke_rows = int(round(m.yoke_depth * rpi))
    setup_rounds = SETUP_ROUNDS_AFTER_NECKBAND
    inc_rows_available = yoke_rows - neckband_rounds - setup_rounds
    if inc_rows_available < (a + b + s):
        recommended = estimate_yoke_depth(m.bust)
        needed = (((a + b + s) * inc_frequency) + neckband_rounds + setup_rounds) / rpi
        raise ValueError(
            f"Yoke depth {m.yoke_depth}\" gives only {inc_rows_available} rows "
            f"for {a + b + s} increase rounds — infeasibly shallow. Need at "
            f"least {needed:.2f}\" yoke depth (engine recommendation for bust "
            f"{m.bust}\" is {recommended:.2f}\")."
        )

    inc_rows_needed = (a + b + s) * inc_frequency
    b_below = 0
    b_yoke = b
    consecutive_inc_bottom = 0

    if inc_rows_needed > inc_rows_available:
        max_below_rounds = int(body_only_inc_max_inches * rpi) // max(inc_frequency, 1)
        shortfall_rows = inc_rows_needed - inc_rows_available
        k_needed = (shortfall_rows + inc_frequency - 1) // inc_frequency
        k = min(k_needed, max_below_rounds, b)
        b_below = k
        b_yoke = b - k
        inc_rows_needed = (a + b_yoke + s) * inc_frequency

    if inc_rows_needed > inc_rows_available:
        total_in_yoke = a + b_yoke + s
        K_needed = 2 * total_in_yoke - inc_rows_available
        max_K = int(total_in_yoke * MAX_CONSECUTIVE_INC_FRACTION)
        if K_needed <= max_K:
            consecutive_inc_bottom = K_needed
            inc_rows_needed = (total_in_yoke - consecutive_inc_bottom) * inc_frequency + consecutive_inc_bottom
            notes.append(
                f"{consecutive_inc_bottom} of {total_in_yoke} yoke increase rounds compressed "
                "to every-row near the underarm to fit yoke depth — this is normal for plus sizes."
            )
        else:
            recommended = estimate_yoke_depth(m.bust)
            max_compress = int((a + b + s) * MAX_CONSECUTIVE_INC_FRACTION)
            max_below = int(body_only_inc_max_inches * rpi) // max(inc_frequency, 1)
            below = min(max_below, b)
            in_yoke = (a + b + s) - below
            min_yoke_rows = (
                (in_yoke - max_compress) * inc_frequency
                + max_compress
                + neckband_rounds
                + setup_rounds
            )
            min_yoke = min_yoke_rows / rpi
            raise ValueError(
                f"Yoke depth {m.yoke_depth}\" is too shallow for bust {m.bust}\" with these proportions. "
                f"Required at least {min_yoke:.2f}\" yoke depth (engine recommendation: {recommended:.2f}\"). "
                "Options: increase yoke_depth, increase body_only_inc_max_inches "
                "(currently {bmax:.1f}\"), or reduce bust ease.".format(bmax=body_only_inc_max_inches)
            )

    if b_below > 0:
        notes.append(
            f"{b_below} body-only increase round(s) moved below the underarm join "
            f"(side-seam shaping over ~{b_below * inc_frequency / rpi:.2f}\") — necessary for plus-size proportion."
        )
    elif b > 0:
        notes.append(f"{b} body-only-in-yoke increase round(s) added for plus-size proportion.")

    sequence: list[tuple[str, int, int]] = []
    every_other = inc_frequency
    in_yoke_blocks: list[list] = []
    if a > 0:
        in_yoke_blocks.append(["full raglan", a, True])
    if s > 0:
        in_yoke_blocks.append(["sleeve-only-in-yoke", s, True])
    if b_yoke > 0:
        in_yoke_blocks.append(["body-only-in-yoke", b_yoke, True])

    if consecutive_inc_bottom > 0:
        remaining = consecutive_inc_bottom
        for block in reversed(in_yoke_blocks):
            if remaining == 0:
                break
            label, count, _ = block
            take = min(count, remaining)
            block[1] = count - take
            remaining -= take

    for label, count, _ in in_yoke_blocks:
        if count > 0:
            sequence.append((f"{label} (every other row)", count, every_other))

    if consecutive_inc_bottom > 0:
        remaining = consecutive_inc_bottom
        compressed: list[tuple[str, int]] = []
        for block in reversed(in_yoke_blocks):
            label = block[0]
            original = {"full raglan": a, "sleeve-only-in-yoke": s, "body-only-in-yoke": b_yoke}[label]
            taken = original - block[1]
            if taken > 0:
                compressed.append((label, taken))
                remaining -= taken
                if remaining == 0:
                    break
        for label, count in reversed(compressed):
            sequence.append((f"{label} (every row)", count, 1))

    body_at_join = B0 + 4 * (a + b_yoke) + 2 * u_target
    sleeve_at_underarm = S0 + 2 * (a + s) + u_target
    sts_at_chest = body_at_join + 4 * b_below

    assert sts_at_chest == B0 + 4 * (a + b) + 2 * u_target
    assert sleeve_at_underarm == S0 + 2 * (a + s) + u_target

    cast_on_back = B0 // 2
    cast_on_front = B0 - cast_on_back

    fb_extra_inches = m.front_back_differential or 0.0
    front_back_short_rows: Optional[FrontBackDifferential] = None
    use_short_rows = enable_full_bust_short_rows
    if use_short_rows is None:
        use_short_rows = fb_extra_inches > 0.0 or ease.front_bias > 0.0

    bust_short_row_pairs = 0
    extra_front_rows = 0
    if use_short_rows and fb_extra_inches > 0.0:
        extra_front_rows = int(round(fb_extra_inches * rpi))
        if extra_front_rows % 2 != 0:
            extra_front_rows -= 1
        if extra_front_rows >= 2:
            bust_short_row_pairs = extra_front_rows // 2
            front_back_short_rows = FrontBackDifferential(
                extra_front_rows=extra_front_rows,
                pairs=bust_short_row_pairs,
            )
            notes.append(
                f"{bust_short_row_pairs} bust short row pairs add "
                f"{extra_front_rows} rows ({extra_front_rows/rpi:.2f}\") to the front only."
            )

    use_waist_shaping = enable_waist_shaping
    if use_waist_shaping is None:
        use_waist_shaping = m.waist is not None

    sts_at_waist: Optional[int] = None
    sts_at_high_hip: Optional[int] = None
    rows_chest_to_waist: Optional[int] = None
    rows_waist_to_high_hip: Optional[int] = None
    waist_dec_rounds = 0
    waist_dec_interval: Optional[int] = None
    hip_inc_rounds = 0
    hip_inc_interval: Optional[int] = None

    rows_join_to_chest = 0
    body_only_below_interval = inc_frequency
    if b_below > 0:
        rows_join_to_chest = b_below * inc_frequency

    if use_waist_shaping and m.waist is not None:
        finished_waist = m.waist + ease.waist
        waist_sts_target = round_to_even(finished_waist * spi)
        dec_total = sts_at_chest - waist_sts_target
        if dec_total > 0:
            waist_dec_rounds = dec_total // 4
            sts_at_waist = sts_at_chest - 4 * waist_dec_rounds
            chest_to_waist_inches = (m.waist_above_underarm or m.body_length * 0.45) - 0.5
            chest_to_waist_inches = max(chest_to_waist_inches, 1.0)
            rows_chest_to_waist = int(round(chest_to_waist_inches * rpi))
            if waist_dec_rounds > 0:
                waist_dec_interval = max(rows_chest_to_waist // waist_dec_rounds, 2)
        else:
            sts_at_waist = sts_at_chest
            rows_chest_to_waist = 0

        if m.high_hip is not None:
            finished_high_hip = m.high_hip + ease.high_hip
            high_hip_sts_target = round_to_even(finished_high_hip * spi)
            inc_total = high_hip_sts_target - (sts_at_waist or sts_at_chest)
            if inc_total > 0:
                hip_inc_rounds = inc_total // 4
                sts_at_high_hip = (sts_at_waist or sts_at_chest) + 4 * hip_inc_rounds
                hip_section_rows = max(
                    int(round((m.body_length - (chest_to_waist_inches + rows_join_to_chest / rpi)) * rpi)),
                    int(round(2.0 * rpi)),
                )
                hip_inc_section_rows = max(hip_section_rows // 2, hip_inc_rounds * 2)
                rows_waist_to_high_hip = hip_inc_section_rows
                if hip_inc_rounds > 0:
                    hip_inc_interval = max(hip_inc_section_rows // hip_inc_rounds, 2)
            else:
                sts_at_high_hip = sts_at_waist
                rows_waist_to_high_hip = 0

    sts_at_hem = sts_at_high_hip or sts_at_waist or sts_at_chest

    body_rows_target = int(round(m.body_length * rpi))
    rows_used = rows_join_to_chest
    rows_used += extra_front_rows
    if rows_chest_to_waist:
        rows_used += rows_chest_to_waist
    if rows_waist_to_high_hip:
        rows_used += rows_waist_to_high_hip
    rows_high_hip_to_hem = max(body_rows_target - rows_used, 0)
    total_body_rows = rows_used + rows_high_hip_to_hem

    body = BodyShaping(
        sts_at_join=body_at_join,
        sts_at_chest=sts_at_chest,
        sts_at_waist=sts_at_waist,
        sts_at_high_hip=sts_at_high_hip,
        sts_at_hem=sts_at_hem,
        rows_join_to_chest=rows_join_to_chest,
        rows_chest_to_waist=rows_chest_to_waist,
        rows_waist_to_high_hip=rows_waist_to_high_hip,
        rows_high_hip_to_hem=rows_high_hip_to_hem,
        total_body_rows=total_body_rows,
        bust_short_row_pairs=bust_short_row_pairs,
        waist_dec_rounds=waist_dec_rounds,
        waist_dec_interval=waist_dec_interval,
        hip_inc_rounds=hip_inc_rounds,
        hip_inc_interval=hip_inc_interval,
        body_only_below_join_interval=body_only_below_interval,
    )

    dec_total = sleeve_at_underarm - wrist_sts
    if dec_total < 0:
        notes.append(
            f"sleeve at underarm ({sleeve_at_underarm} sts) is narrower than wrist ({wrist_sts} sts) "
            "— sleeve will taper UP, which is unusual. Will work straight to wrist instead."
        )
        sleeve_dec_rounds = 0
        sleeve_at_cuff = sleeve_at_underarm
        sleeve_dec_interval = 0
    else:
        sleeve_dec_rounds = dec_total // 2
        sleeve_at_cuff = sleeve_at_underarm - 2 * sleeve_dec_rounds
        cuff_inches = 2.0
        taper_inches = max(m.sleeve_length - cuff_inches, m.sleeve_length * 0.5)
        taper_rows = int(round(taper_inches * rpi))
        if sleeve_dec_rounds > 0:
            sleeve_dec_interval = max(taper_rows // sleeve_dec_rounds, 2)
        else:
            sleeve_dec_interval = 0
    cuff_rows = int(round(2.0 * rpi))
    total_sleeve_rows = int(round(m.sleeve_length * rpi))

    sleeve = SleeveShaping(
        sts_at_underarm=sleeve_at_underarm,
        sts_at_cuff=sleeve_at_cuff,
        dec_rounds=sleeve_dec_rounds,
        dec_interval=sleeve_dec_interval,
        cuff_straight_rows=cuff_rows,
        total_sleeve_rows=total_sleeve_rows,
    )

    yoke = YokeIncreasePlan(
        full_raglan_rounds=a,
        body_only_in_yoke_rounds=b_yoke,
        sleeve_only_in_yoke_rounds=s,
        body_only_below_join_rounds=b_below,
        inc_frequency=inc_frequency,
        neckband_rounds=neckband_rounds,
        setup_rounds=setup_rounds,
        consecutive_inc_rounds_bottom=consecutive_inc_bottom,
        sequence=sequence,
    )

    if m.estimated_fields:
        notes.append(
            "Estimated measurements used (not provided): "
            + ", ".join(m.estimated_fields)
            + ". Pattern fit may improve if you measure these directly."
        )

    return GradedRaglan(
        gauge=gauge,
        measurements=m,
        ease=ease,
        finished_bust=finished_bust,
        finished_upper_arm=finished_upper_arm,
        finished_neck=finished_neck,
        finished_wrist=finished_wrist,
        yoke_depth=m.yoke_depth,
        cast_on_total=neck_sts,
        cast_on_back=cast_on_back,
        cast_on_front=cast_on_front,
        cast_on_each_sleeve=S0,
        cast_on_raglan_markers=4,
        underarm_cast_on=u_target,
        yoke=yoke,
        body=body,
        sleeve=sleeve,
        front_back_short_rows=front_back_short_rows,
        notes=notes,
    )
