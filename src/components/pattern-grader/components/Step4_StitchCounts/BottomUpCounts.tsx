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

export function BottomUpCounts({ spec, updateSpec, issues }: Props) {
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

  return (
    <div>
      {/* Section A: Hem & body */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>A</span>
          Body (front or back piece)
        </div>
        <p className={styles.sectionHelper}>
          For bottom-up seamed patterns, these counts are usually for{' '}
          <strong>one piece</strong> (front or back). The full circumference is
          2&times; these values. Check the pattern schematic for confirmation.
        </p>

        <FieldRow
          label="Hem cast-on"
          fieldName="hem_cast_on"
          value={sts.hem_cast_on}
          onChange={(v) => updateSts('hem_cast_on', v as number | null)}
          unit="sts"
          helper="Stitches cast on at the hem for one piece."
          issue={issueFor('hem_cast_on')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Waist stitches"
          fieldName="waist_sts"
          value={sts.waist_sts}
          onChange={(v) => updateSts('waist_sts', v as number | null)}
          unit="sts"
          helper="Stitches at the narrowest waist point, after decreases. Leave blank if no waist shaping."
          issue={issueFor('waist_sts')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Bust stitches"
          fieldName="bust_sts"
          value={sts.bust_sts}
          onChange={(v) => updateSts('bust_sts', v as number | null)}
          unit="sts"
          helper="Stitches at the fullest bust point, after hip increases."
          issue={issueFor('bust_sts')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
      </div>

      {/* Section B: Armhole & shoulder */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>B</span>
          Armhole &amp; Shoulder
        </div>
        <p className={styles.sectionHelper}>
          These come from the armhole shaping section at the top of the body
          pieces.
        </p>

        <FieldRow
          label="Armhole bind-off"
          fieldName="armhole_bind_off"
          value={sts.armhole_bind_off}
          onChange={(v) => updateSts('armhole_bind_off', v as number | null)}
          unit="sts"
          helper="Initial stitches bound off at the underarm to begin armhole shaping."
          issue={issueFor('armhole_bind_off')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Shoulder stitches"
          fieldName="shoulder_sts"
          value={sts.shoulder_sts}
          onChange={(v) => updateSts('shoulder_sts', v as number | null)}
          unit="sts"
          helper="Stitches remaining at the shoulder after armhole shaping is complete (each shoulder separately if specified)."
          issue={issueFor('shoulder_sts')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Neck bind-off"
          fieldName="neck_bind_off"
          value={sts.neck_bind_off}
          onChange={(v) => updateSts('neck_bind_off', v as number | null)}
          unit="sts"
          helper="Centre front/back neck stitches bound off."
          issue={issueFor('neck_bind_off')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
      </div>

      {/* Section C: Sleeves */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionLetter}>C</span>
          Sleeves
        </div>
        <p className={styles.sectionHelper}>
          Sleeve stitch counts. For bottom-up sleeves, these increase from cuff
          to underarm.
        </p>

        <FieldRow
          label="Sleeve cast-on (cuff)"
          fieldName="sleeve_cast_on"
          value={sts.sleeve_cast_on}
          onChange={(v) => updateSts('sleeve_cast_on', v as number | null)}
          unit="sts"
          helper="Stitches cast on at the cuff edge."
          issue={issueFor('sleeve_cast_on')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Sleeve at underarm"
          fieldName="sleeve_at_underarm"
          value={sts.sleeve_at_underarm}
          onChange={(v) => updateSts('sleeve_at_underarm', v as number | null)}
          unit="sts"
          helper="Sleeve stitches at the underarm before cap shaping begins."
          issue={issueFor('sleeve_at_underarm')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
        <FieldRow
          label="Sleeve cap rows"
          fieldName="sleeve_cap_rows"
          value={sts.sleeve_cap_rows}
          onChange={(v) => updateSts('sleeve_cap_rows', v as number | null)}
          unit="rows"
          helper="Total number of rows in the sleeve cap shaping section."
          issue={issueFor('sleeve_cap_rows')}
          unknownFields={spec.unknown_fields}
          onMarkUnknown={markUnknown}
          min={0}
        />
      </div>
    </div>
  );
}
