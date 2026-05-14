import React from 'react';
import { FormState, StitchCounts, ValidationIssue } from '../../types';
import { FieldRow } from '../FieldRow';
import styles from './StitchCounts.module.css';

interface Props {
  spec: FormState['spec'];
  updateSpec: <K extends keyof FormState['spec']>(
    key: K,
    value: FormState['spec'][K],
  ) => void;
  issues: ValidationIssue[];
}

export function RaglanCounts({ spec, updateSpec, issues }: Props) {
  const sts = spec.stitches;

  function updateSts(key: keyof StitchCounts, value: number | null) {
    updateSpec('stitches', { ...sts, [key]: value });
  }

  function markUnknown(field: string) {
    updateSpec(
      'unknown_fields',
      [...spec.unknown_fields, field].filter((x, i, a) => a.indexOf(x) === i),
    );
  }

  const issueFor = (field: string) =>
    issues.find((i) => i.field === field || i.field === `stitches.${field}`);

  // Live cast-on check
  const { back_cast_on: b, front_cast_on: f, each_sleeve_cast_on: s, neck_cast_on: t } = sts;
  const partsSum =
    b !== null && f !== null && s !== null ? b + f + 2 * s + 4 : null;
  const castOnOk =
    partsSum !== null && t !== null && Math.abs(partsSum - t) <= 2;
  const castOnBad =
    partsSum !== null && t !== null && Math.abs(partsSum - t) > 2;

  return (
    <div>
      {/* Section A: Cast-on */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>A</span>
          Cast-On Stitches
        </div>
        <p className={styles.sectionHelper}>
          These are the stitches you cast on at the very start (the neck). Look
          for a table labeled with your sizes right at the beginning of the
          pattern.
        </p>

        <FieldRow
          label="Total neck cast-on"
          fieldName="neck_cast_on"
          value={sts.neck_cast_on}
          onChange={(v) => updateSts('neck_cast_on', v as number | null)}
          unit="sts"
          helper="The total number of stitches cast on at the neck. Often the sum of all parts."
          issue={issueFor('neck_cast_on')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Back cast-on"
          fieldName="back_cast_on"
          value={sts.back_cast_on}
          onChange={(v) => updateSts('back_cast_on', v as number | null)}
          unit="sts"
          helper="Stitches designated for the back panel at cast-on."
          issue={issueFor('back_cast_on')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Front cast-on"
          fieldName="front_cast_on"
          value={sts.front_cast_on}
          onChange={(v) => updateSts('front_cast_on', v as number | null)}
          unit="sts"
          helper="Stitches designated for the front panel at cast-on."
          issue={issueFor('front_cast_on')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Each sleeve cast-on"
          fieldName="each_sleeve_cast_on"
          value={sts.each_sleeve_cast_on}
          onChange={(v) => updateSts('each_sleeve_cast_on', v as number | null)}
          unit="sts"
          helper="Stitches for ONE sleeve at cast-on (both sleeves are equal)."
          issue={issueFor('each_sleeve_cast_on')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />

        {partsSum !== null && (
          <div
            className={`${styles.checkRow} ${
              castOnOk
                ? styles.checkOk
                : castOnBad
                ? styles.checkBad
                : styles.checkNeutral
            }`}
          >
            <span className={styles.checkIcon}>
              {castOnOk ? '✓' : castOnBad ? '✗' : '?'}
            </span>
            <span>
              Parts (back + front + 2&times;sleeve + 4 markers) ={' '}
              <strong>{partsSum}</strong>
              {t !== null && (
                <>
                  {' '}
                  vs total = <strong>{t}</strong>
                  {castOnBad && (
                    <span className={styles.diff}>
                      {' '}
                      (off by {Math.abs(partsSum - t)})
                    </span>
                  )}
                </>
              )}
            </span>
          </div>
        )}
      </div>

      {/* Section B: End of yoke */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>B</span>
          End of Yoke
        </div>
        <p className={styles.sectionHelper}>
          After all raglan increases are complete, just before you separate the
          sleeves. Check the row where the pattern says &ldquo;separate
          sleeves&rdquo; or &ldquo;divide for body.&rdquo;
        </p>

        <FieldRow
          label="Body stitches at end of yoke"
          fieldName="body_at_yoke_end"
          value={sts.body_at_yoke_end}
          onChange={(v) => updateSts('body_at_yoke_end', v as number | null)}
          unit="sts"
          helper="Combined front + back body stitches just before sleeve separation."
          issue={issueFor('body_at_yoke_end')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Each sleeve at end of yoke"
          fieldName="each_sleeve_at_yoke_end"
          value={sts.each_sleeve_at_yoke_end}
          onChange={(v) =>
            updateSts('each_sleeve_at_yoke_end', v as number | null)
          }
          unit="sts"
          helper="Stitches for ONE sleeve at the end of yoke increases."
          issue={issueFor('each_sleeve_at_yoke_end')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
      </div>

      {/* Section C: Body */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>C</span>
          Body
        </div>
        <p className={styles.sectionHelper}>
          The body stitch counts after sleeve separation. Look for stitch count
          notes at the underarm, chest, waist, and hem.
        </p>

        <FieldRow
          label="Underarm cast-on (each side)"
          fieldName="underarm_cast_on_each"
          value={sts.underarm_cast_on_each}
          onChange={(v) =>
            updateSts('underarm_cast_on_each', v as number | null)
          }
          unit="sts"
          helper="Stitches cast on at each underarm when joining body in the round. Often 2–6."
          issue={issueFor('underarm_cast_on_each')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Body at chest (after underarm join)"
          fieldName="body_at_chest"
          value={sts.body_at_chest}
          onChange={(v) => updateSts('body_at_chest', v as number | null)}
          unit="sts"
          issue={issueFor('body_at_chest')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Body at waist"
          fieldName="body_at_waist"
          value={sts.body_at_waist}
          onChange={(v) => updateSts('body_at_waist', v as number | null)}
          unit="sts"
          helper="After waist decreases, before hip increases. If no waist shaping, leave blank."
          issue={issueFor('body_at_waist')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Body at hem"
          fieldName="body_at_hem"
          value={sts.body_at_hem}
          onChange={(v) => updateSts('body_at_hem', v as number | null)}
          unit="sts"
          helper="Before hem ribbing begins. May be the same as chest if straight body."
          issue={issueFor('body_at_hem')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
      </div>

      {/* Section D: Sleeves */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>D</span>
          Sleeves
        </div>
        <p className={styles.sectionHelper}>
          Sleeve stitch counts after separating from the body. Decreases taper
          to the cuff.
        </p>

        <FieldRow
          label="Each sleeve at underarm"
          fieldName="each_sleeve_at_underarm"
          value={sts.each_sleeve_at_underarm}
          onChange={(v) =>
            updateSts('each_sleeve_at_underarm', v as number | null)
          }
          unit="sts"
          helper="Sleeve sts after picking up underarm stitches and joining in the round."
          issue={issueFor('each_sleeve_at_underarm')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Each sleeve at cuff"
          fieldName="each_sleeve_at_cuff"
          value={sts.each_sleeve_at_cuff}
          onChange={(v) => updateSts('each_sleeve_at_cuff', v as number | null)}
          unit="sts"
          helper="Stitches at the cuff, before ribbing begins."
          issue={issueFor('each_sleeve_at_cuff')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
      </div>
    </div>
  );
}
