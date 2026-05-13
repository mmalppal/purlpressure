"""Markdown pattern writer."""

from __future__ import annotations

from typing import Iterable, Optional

from .raglan import GradedRaglan
from .validators import Severity, ValidationIssue, validate as run_validate


def write_pattern(
    graded: GradedRaglan,
    pattern_name: str = "Untitled Raglan",
    designer: str = "(your name)",
    skill_level: str = "Intermediate",
    issues: Optional[list[ValidationIssue]] = None,
) -> str:
    if issues is None:
        issues = run_validate(graded)

    errors = [i for i in issues if i.severity is Severity.ERROR]
    if errors:
        raise ValueError(
            "Cannot write pattern: validation errors present.\n"
            + "\n".join(str(e) for e in errors)
        )

    sections = [
        _header(pattern_name, designer, skill_level),
        _finished_measurements(graded),
        _materials(graded),
        _gauge(graded),
        _abbreviations(),
        _construction_overview(graded),
        _cast_on_and_neckband(graded),
        _yoke(graded),
        _separation(graded),
        _body(graded),
        _sleeves(graded),
        _finishing(graded),
        _schematic(graded),
        _engineering_notes(graded, issues),
    ]
    return "\n\n".join(s.rstrip() for s in sections if s) + "\n"


def _header(name: str, designer: str, skill_level: str) -> str:
    return (
        f"# {name}\n\n"
        f"**Designer:** {designer}  \n"
        f"**Skill level:** {skill_level}  \n"
        "**Construction:** Top-down seamless raglan"
    )


def _finished_measurements(g: GradedRaglan) -> str:
    rows = [
        ("Bust circumference", f"{g.finished_bust:.2f} in"),
        ("Upper arm circumference", f"{g.finished_upper_arm:.2f} in"),
        ("Neck circumference", f"{g.finished_neck:.2f} in"),
        ("Wrist circumference", f"{g.finished_wrist:.2f} in"),
        ("Yoke depth (neck to underarm)", f"{g.yoke_depth:.2f} in"),
        ("Body length (underarm to hem)", f"{g.measurements.body_length:.2f} in"),
        ("Sleeve length (underarm to cuff)", f"{g.measurements.sleeve_length:.2f} in"),
    ]
    table = _table(["Measurement", "Finished"], rows)
    return "## Finished measurements\n\n" + table


def _materials(g: GradedRaglan) -> str:
    bust_area = g.finished_bust * (g.measurements.body_length + g.yoke_depth)
    sleeve_area = g.finished_upper_arm * g.measurements.sleeve_length * 2
    total_area_in2 = bust_area + sleeve_area
    sts_per_in2 = g.gauge.sts_per_inch * g.gauge.rows_per_inch
    total_sts = int(total_area_in2 * sts_per_in2)
    yards_per_100_sts = 6.0 * (4.5 / g.gauge.sts_per_inch) ** 1.5
    yards = int(total_sts / 100 * yards_per_100_sts)
    yards_low = int(yards * 0.9)
    yards_high = int(yards * 1.2)

    return (
        "## Materials\n\n"
        f"- **Yarn:** approximately **{yards_low}-{yards_high} yards** of yarn "
        "appropriate for the gauge below. This is an estimate; buy 10-15% extra "
        "for swatching and seaming.\n"
        "- **Needles:** circular needles in the size that gives you the gauge "
        "below (most likely 16\" and 32\" cables, plus a method for small "
        "circumferences for sleeves — magic loop, DPNs, or two circulars).\n"
        "- **Notions:** 4 raglan markers + 2 side-seam markers (different "
        "color), tapestry needle, stitch holders or scrap yarn for sleeves."
    )


def _gauge(g: GradedRaglan) -> str:
    return (
        "## Gauge\n\n"
        f"**{g.gauge.describe()}** in stockinette stitch, blocked.\n\n"
        "**Gauge is critical.** A 5% gauge error compounds across an entire "
        "garment. Swatch in the round if you can, wash and dry as you will the "
        "finished sweater, then measure."
    )


def _abbreviations() -> str:
    return (
        "## Abbreviations\n\n"
        "- **CO**: cast on\n"
        "- **k**: knit\n"
        "- **p**: purl\n"
        "- **sl m / sm**: slip marker\n"
        "- **pm**: place marker\n"
        "- **M1L / M1R**: make 1 left-leaning / right-leaning (lifted increase)\n"
        "- **k2tog**: knit 2 together (right-leaning decrease)\n"
        "- **ssk**: slip slip knit (left-leaning decrease)\n"
        "- **w&t**: wrap and turn (short row)\n"
        "- **rep**: repeat\n"
        "- **st(s)**: stitch(es)\n"
        "- **RS / WS**: right side / wrong side"
    )


def _construction_overview(g: GradedRaglan) -> str:
    bits = [
        f"Cast on **{g.cast_on_total} sts** at the neck and join in the round.",
        f"Work raglan increases in the yoke for **{g.yoke_depth:.2f}\"**.",
    ]
    if g.yoke.body_only_below_join_rounds > 0:
        bits.append(
            f"Separate body from sleeves, then continue with **side-seam increases** for "
            f"{g.yoke.body_only_below_join_rounds} more rounds "
            f"(~{g.body.rows_join_to_chest / g.gauge.rows_per_inch:.2f}\") before reaching full bust width."
        )
    else:
        bits.append("Separate body from sleeves.")
    if g.body.bust_short_row_pairs > 0:
        bits.append(f"Work **{g.body.bust_short_row_pairs} short row pairs** on the front for bust shaping.")
    if g.body.waist_dec_rounds > 0:
        bits.append(f"Decrease **{g.body.waist_dec_rounds}** times at the waist.")
    if g.body.hip_inc_rounds > 0:
        bits.append(f"Increase **{g.body.hip_inc_rounds}** times below the waist.")
    bits.append("Work even to hem; finish with ribbed band.")
    bits.append("Pick up sleeves at the underarm and work down to wrist with decreases.")
    bits.append("Block to measurements.")
    return "## Construction overview\n\n" + "\n".join(f"{i+1}. {b}" for i, b in enumerate(bits))


def _cast_on_and_neckband(g: GradedRaglan) -> str:
    co_table = _table(
        ["Section", "Stitches"],
        [
            ("Back", str(g.cast_on_back)),
            ("Raglan st (right back)", "1"),
            ("Right sleeve", str(g.cast_on_each_sleeve)),
            ("Raglan st (right front)", "1"),
            ("Front", str(g.cast_on_front)),
            ("Raglan st (left front)", "1"),
            ("Left sleeve", str(g.cast_on_each_sleeve)),
            ("Raglan st (left back)", "1"),
            ("**Total**", f"**{g.cast_on_total}**"),
        ],
    )
    return (
        "## Cast on and neckband\n\n"
        f"Using your preferred long-tail or stretchy cast-on, CO **{g.cast_on_total} sts** "
        "and join in the round, being careful not to twist.\n\n"
        "Place markers and arrange the cast-on as follows. The four raglan stitches are "
        "single stitches that sit at each of the four raglan lines; markers go on either "
        "side of them. Begin and end each round at the start of the back.\n\n"
        + co_table
        + "\n\n"
        f"Work **{g.yoke.neckband_rounds} rounds** of k1, p1 ribbing for the neckband, "
        f"then work **{g.yoke.setup_rounds} plain knit round(s)** before starting the yoke increases."
    )


def _yoke(g: GradedRaglan) -> str:
    full_raglan_template = (
        "**Full raglan increase round:** \n"
        "*[Knit to 1 st before marker, M1R, k1 (the raglan st), sm, k1, M1L] "
        "× 4, knit to end of round.* — **+8 sts (back +2, front +2, each sleeve +2).**"
    )
    body_only_template = (
        "**Body-only increase round (in yoke):** \n"
        "*[Knit to 1 st before marker, M1R, k1, sm, k1 — at body marker only; "
        "do not inc on the sleeve side] then at the next marker [k1, sm, k1, M1L]* "
        "(so each body section gains 1 st each side of its two raglans, and sleeves do not). "
        "— **+4 sts (back +2, front +2).**"
    )
    sleeve_only_template = (
        "**Sleeve-only increase round (in yoke):** \n"
        "*Mirror of body-only: increase only on the sleeve sides of the four raglan markers.* "
        "— **+4 sts (each sleeve +2).**"
    )

    lines = ["## Yoke", "", "### Increase round templates", "", full_raglan_template]
    if g.yoke.body_only_in_yoke_rounds > 0:
        lines.append("")
        lines.append(body_only_template)
    if g.yoke.sleeve_only_in_yoke_rounds > 0:
        lines.append("")
        lines.append(sleeve_only_template)

    lines.append("")
    lines.append("### Working the yoke")
    lines.append("")
    lines.append("Work the increase rounds in this order:")
    lines.append("")
    seq_rows: list[tuple[str, str]] = []
    running = g.cast_on_total
    for label, count, rows_per in g.yoke.sequence:
        added_per_round = _added_per_round(label)
        running_before = running
        running += count * added_per_round
        seq_rows.append((
            f"{count} × {label}",
            f"every {rows_per} row{'s' if rows_per != 1 else ''} ({running_before} → {running} sts)",
        ))
    lines.append(_table(["Rounds", "Frequency / result"], seq_rows))
    lines.append("")

    after_yoke_total = (
        g.cast_on_back + g.cast_on_front + 2 * g.cast_on_each_sleeve + 4
        + 8 * g.yoke.full_raglan_rounds
        + 4 * g.yoke.body_only_in_yoke_rounds
        + 4 * g.yoke.sleeve_only_in_yoke_rounds
    )
    back_at_end = g.cast_on_back + 2 * (g.yoke.full_raglan_rounds + g.yoke.body_only_in_yoke_rounds)
    front_at_end = g.cast_on_front + 2 * (g.yoke.full_raglan_rounds + g.yoke.body_only_in_yoke_rounds)
    sleeve_at_end = g.cast_on_each_sleeve + 2 * (g.yoke.full_raglan_rounds + g.yoke.sleeve_only_in_yoke_rounds)

    lines.append("**Check:** at the end of the yoke you should have:")
    lines.append("")
    lines.append(_table(
        ["Section", "Stitches"],
        [
            ("Back", str(back_at_end)),
            ("Front", str(front_at_end)),
            ("Each sleeve", str(sleeve_at_end)),
            ("Raglan stitches", "4"),
            ("**Total**", f"**{after_yoke_total}**"),
        ],
    ))

    if g.yoke.consecutive_inc_rounds_bottom > 0:
        lines.append("")
        lines.append(
            f"*Note: the last {g.yoke.consecutive_inc_rounds_bottom} increase round(s) happen on "
            "consecutive rows (no plain row between) — this is normal for plus-size raglans and lets "
            "the bust:arm proportion fit in a sensible yoke depth.*"
        )

    return "\n".join(lines)


def _separation(g: GradedRaglan) -> str:
    u = g.underarm_cast_on
    sleeve_at_underarm = g.sleeve.sts_at_underarm
    body_at_join = g.body.sts_at_join
    return (
        "## Separating sleeves from body\n\n"
        "Work to the first sleeve. Slip the sleeve sts plus the two raglan stitches "
        f"flanking them onto scrap yarn (this is "
        f"{g.cast_on_each_sleeve + 2 * (g.yoke.full_raglan_rounds + g.yoke.sleeve_only_in_yoke_rounds) + 2} "
        "sts to hold). "
        f"Use the backward-loop cast-on to CO **{u} new sts** for the underarm. "
        "Continue across the front, holding the second sleeve the same way and casting on "
        "another underarm. Place a removable marker at the midpoint of each new underarm "
        "cast-on — these are your side-seam markers for any below-join shaping.\n\n"
        + _table(
            ["Section", "Stitches"],
            [
                ("Body at underarm join (waiting on needle)", str(body_at_join)),
                ("Each sleeve (on hold)", str(sleeve_at_underarm)),
                ("Underarm cast-on per side", str(u)),
            ],
        )
    )


def _body(g: GradedRaglan) -> str:
    rpi = g.gauge.rows_per_inch
    lines = ["## Body", ""]

    if g.body.bust_short_row_pairs > 0:
        front = g.cast_on_front + 2 * (g.yoke.full_raglan_rounds + g.yoke.body_only_in_yoke_rounds)
        first_turn_offset = max(front // 6, 4)
        lines.append("### Bust short rows")
        lines.append("")
        lines.append(
            f"Worked across the front only. {g.body.bust_short_row_pairs} pair(s) of short rows add "
            f"{g.front_back_short_rows.extra_front_rows} rows "
            f"({g.front_back_short_rows.extra_front_rows / rpi:.2f}\") to the front below the underarm.\n\n"
            "**Set-up:** Knit across the front to the right side-seam marker. Turn. Purl back across "
            f"the front to {first_turn_offset} sts before the left side-seam marker; w&t. Knit back "
            "to the same distance before the right marker; w&t.\n\n"
            f"Continue working short row pairs, moving the turn points approximately 2 sts further "
            f"inward each pair, until you have completed **{g.body.bust_short_row_pairs} pair(s)**. "
            "Resolve all wraps on the next full round."
        )
        lines.append("")

    if g.yoke.body_only_below_join_rounds > 0:
        lines.append("### Side-seam increases below join")
        lines.append("")
        added = 4 * g.yoke.body_only_below_join_rounds
        lines.append(
            "**Side-seam inc round:** *Knit to 1 st before right side marker, M1R, k1, sm, k1, M1L; "
            "knit to 1 st before left side marker; repeat the inc; knit to end.* — **+4 sts per round.**"
        )
        lines.append("")
        lines.append(
            f"Work this round every {g.body.body_only_below_join_interval} rows, "
            f"**{g.yoke.body_only_below_join_rounds} times** (+{added} sts total). "
            f"After this section you should have **{g.body.sts_at_chest} sts**."
        )
        lines.append("")
    else:
        lines.append(f"After joining, you have **{g.body.sts_at_chest} sts** on the body needle.")
        lines.append("")

    if g.body.waist_dec_rounds and g.body.waist_dec_interval and g.body.sts_at_waist is not None:
        lines.append("### Waist shaping")
        lines.append("")
        lines.append(
            "**Waist dec round:** *Knit to 3 sts before the right side marker, k2tog, k1, sm, k1, ssk; "
            "knit to 3 sts before the left side marker; repeat the dec; knit to end.* — **-4 sts per round.**"
        )
        lines.append("")
        lines.append(
            f"Work this round every {g.body.waist_dec_interval} rows, **{g.body.waist_dec_rounds} times**. "
            f"After waist shaping you should have **{g.body.sts_at_waist} sts**."
        )
        lines.append("")

    if g.body.hip_inc_rounds and g.body.hip_inc_interval and g.body.sts_at_high_hip is not None:
        lines.append("### Hip shaping")
        lines.append("")
        lines.append("**Hip inc round:** mirror of the waist dec, with M1R/M1L at the side markers. **+4 sts per round.**")
        lines.append("")
        lines.append(
            f"Work this round every {g.body.hip_inc_interval} rows, **{g.body.hip_inc_rounds} times**. "
            f"After hip shaping you should have **{g.body.sts_at_high_hip} sts**."
        )
        lines.append("")

    lines.append("### Hem")
    lines.append("")
    lines.append(
        f"Knit straight until the body measures **{g.measurements.body_length:.2f}\"** from the underarm. "
        f"End on a knit round. Work **{int(round(1.5 * rpi))} rounds** of k1, p1 ribbing. Bind off loosely."
    )

    return "\n".join(lines)


def _sleeves(g: GradedRaglan) -> str:
    rpi = g.gauge.rows_per_inch
    u = g.underarm_cast_on
    sleeve_held = g.sleeve.sts_at_underarm - u
    lines = ["## Sleeves (worked one at a time)", ""]
    lines.append(
        f"Transfer the held sleeve sts back to needles. Beginning at the center of the underarm "
        f"cast-on, pick up and knit **{u} sts** from the underarm cast-on, then knit across the "
        f"{sleeve_held} held sleeve sts. Place a marker for beginning of round. "
        f"Total: **{g.sleeve.sts_at_underarm} sts**."
    )
    lines.append("")
    if g.sleeve.dec_rounds > 0:
        lines.append(
            "**Sleeve dec round:** *K1, k2tog, knit to 3 sts before end of round, ssk, k1.* "
            "— **-2 sts per round.**"
        )
        lines.append("")
        lines.append(
            f"Work this dec round every {g.sleeve.dec_interval} rows, **{g.sleeve.dec_rounds} times**. "
            f"After all decreases you should have **{g.sleeve.sts_at_cuff} sts**."
        )
        lines.append("")
    lines.append(
        f"Knit straight until the sleeve measures **{g.measurements.sleeve_length - 1.5:.2f}\"** "
        f"from the underarm pickup. Work **{int(round(1.5 * rpi))} rounds** of k1, p1 ribbing. "
        "Bind off loosely. Repeat for the second sleeve."
    )
    return "\n".join(lines)


def _finishing(g: GradedRaglan) -> str:
    return (
        "## Finishing\n\n"
        "Weave in all ends. Sew up the small holes at each underarm if needed "
        "(use the tail from the underarm cast-on). Soak in cool water with a drop of wool wash "
        "for 20 minutes, gently press out water in a towel, and lay flat to dry. "
        "Block to the finished measurements above; pin any edges that want to roll."
    )


def _schematic(g: GradedRaglan) -> str:
    bust_w = max(int(g.finished_bust * 0.6), 12)
    yoke_h = max(int(g.yoke_depth * 0.6), 4)
    body_h = max(int(g.measurements.body_length * 0.6), 4)
    upper_arm = max(int(g.finished_upper_arm * 0.6), 6)
    sleeve_h = max(int(g.measurements.sleeve_length * 0.5), 4)
    wrist = max(int(g.finished_wrist * 0.6), 4)
    neck = max(int(g.finished_neck * 0.6), 6)

    lines = ["## Schematic", "", "```"]
    pad = " " * ((bust_w - neck) // 2)
    lines.append(pad + "[" + "—" * (neck - 2) + "]" + f"  neck {g.finished_neck:.1f}\"")
    for i in range(yoke_h):
        width = neck + int((bust_w - neck) * (i + 1) / yoke_h)
        lp = (bust_w - width) // 2
        lines.append(" " * lp + "/" + " " * (width - 2) + "\\")
    lines.append("+" + "—" * (bust_w - 2) + "+   ← underarm separation")
    lines.append("|" + " " * (bust_w - 2) + f"|   body length {g.measurements.body_length:.1f}\"")
    for _ in range(max(body_h - 2, 1)):
        lines.append("|" + " " * (bust_w - 2) + "|")
    lines.append("+" + "—" * (bust_w - 2) + "+")
    lines.append(f"  bust {g.finished_bust:.1f}\"")
    lines.append("")
    lines.append("Sleeve (taper):")
    for i in range(sleeve_h):
        width = upper_arm - int((upper_arm - wrist) * (i + 1) / sleeve_h)
        lines.append("  " + "[" + " " * max(width - 2, 0) + "]")
    lines.append(f"  upper arm {g.finished_upper_arm:.1f}\" → wrist {g.finished_wrist:.1f}\"")
    lines.append("```")
    return "\n".join(lines)


def _engineering_notes(g: GradedRaglan, issues: list[ValidationIssue]) -> str:
    lines = ["## Validation and engineering notes", ""]
    if g.notes:
        lines.append("**Engineering notes:**")
        lines.append("")
        for n in g.notes:
            lines.append(f"- {n}")
        lines.append("")
    if issues:
        lines.append("**Validation:**")
        lines.append("")
        for i in issues:
            tag = {
                Severity.ERROR: "ERROR",
                Severity.WARNING: "⚠ WARNING",
                Severity.INFO: "ℹ info",
            }[i.severity]
            lines.append(f"- **{tag}** ({i.code}): {i.message}")
    else:
        lines.append("No validation issues.")
    return "\n".join(lines)


def _table(headers: Iterable[str], rows: Iterable[tuple[str, str]]) -> str:
    headers = list(headers)
    rows = list(rows)
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([header_line, sep_line] + body_lines)


def _added_per_round(label: str) -> int:
    if label.startswith("full raglan"):
        return 8
    if label.startswith("body-only-in-yoke"):
        return 4
    if label.startswith("sleeve-only-in-yoke"):
        return 4
    return 0
