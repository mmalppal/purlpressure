import React from 'react';
import { FormState, LengthMeasurements, ValidationIssue } from '../types';
import { StepLayout } from './StepLayout';
import { FieldRow } from './FieldRow';
import styles from './Step5_Lengths.module.css';

interface Props {
  state: FormState;
  onBack: () => void;
  onNext: () => void;
  updateSpec: <K extends keyof FormState['spec']>(
    key: K,
    value: FormState['spec'][K],
  ) => void;
  issues: ValidationIssue[];
}

export function Step5_Lengths({ state, onBack, onNext, updateSpec, issues }: Props) {
  const { spec } = state;
  const len = spec.lengths;
  const isRaglan = spec.construction === 'top_down_raglan';
  const isBottomUp = spec.construction === 'bottom_up_seamed';

  function updateLen(key: keyof LengthMeasurements, value: number | null) {
    updateSpec('lengths', { ...len, [key]: value });
  }

  function markUnknown(field: string) {
    updateSpec(
      'unknown_fields',
      [...spec.unknown_fields, field].filter((x, i, a) => a.indexOf(x) === i),
    );
  }

  const issueFor = (field: string) =>
    issues.find((i) => i.field === field || i.field === `lengths.${field}`);

  return (
    <StepLayout
      step={5}
      totalSteps={9}
      title="Lengths"
      subtitle="Measurements from your pattern's schematic or instructions."
      onBack={onBack}
      onNext={onNext}
      issues={issues}
    >
      <div className={styles.schematicNote}>
        Find these in your pattern's <strong>schematic diagram</strong> — the
        flat technical drawing usually at the end of the pattern. All values in
        inches.
      </div>

      {isRaglan && (
        <>
          <div className={styles.sectionLabel}>Top-Down Body</div>

          <FieldRow
            label="Yoke depth"
            fieldName="yoke_depth"
            value={len.yoke_depth}
            onChange={(v) => updateLen('yoke_depth', v as number | null)}
            type="number"
            unit="in"
            helper='From neck cast-on to underarm, measured straight down. Often labeled "yoke depth" on the schematic.'
            issue={issueFor('yoke_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Total body length"
            fieldName="body_length_total"
            value={len.body_length_total}
            onChange={(v) => updateLen('body_length_total', v as number | null)}
            type="number"
            unit="in"
            helper="From cast-on neck to hem, including yoke depth."
            issue={issueFor('body_length_total')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Total sleeve length"
            fieldName="sleeve_length_total"
            value={len.sleeve_length_total}
            onChange={(v) => updateLen('sleeve_length_total', v as number | null)}
            type="number"
            unit="in"
            helper="From underarm pick-up to cuff edge."
            issue={issueFor('sleeve_length_total')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Waist above hem"
            fieldName="waist_above_hem"
            value={len.waist_above_hem}
            onChange={(v) => updateLen('waist_above_hem', v as number | null)}
            type="number"
            unit="in"
            helper="Distance from hem to waist shaping. Leave blank if no waist shaping."
            issue={issueFor('waist_above_hem')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Neckband depth"
            fieldName="neckband_depth"
            value={len.neckband_depth}
            onChange={(v) => updateLen('neckband_depth', v as number | null)}
            type="number"
            unit="in"
            issue={issueFor('neckband_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Hem ribbing depth"
            fieldName="hem_ribbing_depth"
            value={len.hem_ribbing_depth}
            onChange={(v) => updateLen('hem_ribbing_depth', v as number | null)}
            type="number"
            unit="in"
            issue={issueFor('hem_ribbing_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Cuff ribbing depth"
            fieldName="cuff_ribbing_depth"
            value={len.cuff_ribbing_depth}
            onChange={(v) => updateLen('cuff_ribbing_depth', v as number | null)}
            type="number"
            unit="in"
            issue={issueFor('cuff_ribbing_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
        </>
      )}

      {isBottomUp && (
        <>
          <div className={styles.sectionLabel}>Bottom-Up Body</div>

          <FieldRow
            label="Total body length"
            fieldName="body_length_total"
            value={len.body_length_total}
            onChange={(v) => updateLen('body_length_total', v as number | null)}
            type="number"
            unit="in"
            helper="From cast-on hem to shoulder seam."
            issue={issueFor('body_length_total')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Armhole depth"
            fieldName="armhole_depth"
            value={len.armhole_depth}
            onChange={(v) => updateLen('armhole_depth', v as number | null)}
            type="number"
            unit="in"
            helper="From the first armhole bind-off to the shoulder."
            issue={issueFor('armhole_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Waist above hem"
            fieldName="waist_above_hem"
            value={len.waist_above_hem}
            onChange={(v) => updateLen('waist_above_hem', v as number | null)}
            type="number"
            unit="in"
            issue={issueFor('waist_above_hem')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Bust above waist"
            fieldName="bust_above_waist"
            value={len.bust_above_waist}
            onChange={(v) => updateLen('bust_above_waist', v as number | null)}
            type="number"
            unit="in"
            helper="Distance from waist to fullest bust point."
            issue={issueFor('bust_above_waist')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Total sleeve length"
            fieldName="sleeve_length_total"
            value={len.sleeve_length_total}
            onChange={(v) => updateLen('sleeve_length_total', v as number | null)}
            type="number"
            unit="in"
            helper="From cuff cast-on to underarm, before cap shaping."
            issue={issueFor('sleeve_length_total')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Hem ribbing depth"
            fieldName="hem_ribbing_depth"
            value={len.hem_ribbing_depth}
            onChange={(v) => updateLen('hem_ribbing_depth', v as number | null)}
            type="number"
            unit="in"
            issue={issueFor('hem_ribbing_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
          <FieldRow
            label="Cuff ribbing depth"
            fieldName="cuff_ribbing_depth"
            value={len.cuff_ribbing_depth}
            onChange={(v) => updateLen('cuff_ribbing_depth', v as number | null)}
            type="number"
            unit="in"
            issue={issueFor('cuff_ribbing_depth')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            step={0.25}
            min={0}
          />
        </>
      )}

      {!isRaglan && !isBottomUp && (
        <p className={styles.comingSoon}>
          Length fields for this construction type are coming soon.
        </p>
      )}
    </StepLayout>
  );
}
