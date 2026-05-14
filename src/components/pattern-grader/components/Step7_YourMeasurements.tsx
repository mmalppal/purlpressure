import React, { useState } from 'react';
import { FormState, BodyMeasurements } from '../types';
import { StepLayout } from './StepLayout';
import { FieldRow } from './FieldRow';
import styles from './Step7_YourMeasurements.module.css';

interface Props {
  state: FormState;
  onBack: () => void;
  onNext: () => void;
  updateBody: <K extends keyof BodyMeasurements>(
    key: K,
    value: BodyMeasurements[K],
  ) => void;
}

export function Step7_YourMeasurements({
  state,
  onBack,
  onNext,
  updateBody,
}: Props) {
  const { body } = state;
  const [estimateYoke, setEstimateYoke] = useState(body.yoke_depth === null);

  // Dummy unknownFields for body (body measurements don't have "unknown" concept,
  // but FieldRow requires the prop)
  const noUnknown: string[] = [];
  function noop() {}

  return (
    <StepLayout
      step={7}
      totalSteps={9}
      title="Your Measurements"
      subtitle="Measure yourself — these go straight into the grader."
      onBack={onBack}
      onNext={onNext}
    >
      <div className={styles.guideNote}>
        <strong>Tip:</strong> Measure in a well-fitting bra or your usual
        layering. Use a flexible tape measure, snug but not tight.
      </div>

      <div className={styles.sectionLabel}>Required</div>

      <FieldRow
        label="Bust circumference"
        fieldName="bust"
        value={body.bust}
        onChange={(v) => updateBody('bust', v as number | null)}
        type="number"
        unit="in"
        required
        helper="Around the fullest part of your chest."
        unknownFields={noUnknown}
        onMarkUnknown={noop}
        step={0.25}
        min={20}
        max={80}
      />

      <div className={styles.yoke}>
        <FieldRow
          label="Yoke depth"
          fieldName="yoke_depth"
          value={estimateYoke ? null : body.yoke_depth}
          onChange={(v) => updateBody('yoke_depth', v as number | null)}
          type="number"
          unit="in"
          required={!estimateYoke}
          helper='Measure from nape of neck to underarm (straight down). Typical: 7–10".'
          unknownFields={noUnknown}
          onMarkUnknown={noop}
          step={0.25}
          min={4}
          max={16}
          placeholder={estimateYoke ? 'Will be estimated from bust' : undefined}
        />
        <label className={styles.estimateToggle}>
          <input
            type="checkbox"
            checked={estimateYoke}
            onChange={(e) => {
              setEstimateYoke(e.target.checked);
              if (e.target.checked) updateBody('yoke_depth', null);
            }}
            className={styles.checkbox}
          />
          Estimate for me
        </label>
      </div>

      <FieldRow
        label="Body length (hem to underarm)"
        fieldName="body_length"
        value={body.body_length}
        onChange={(v) => updateBody('body_length', v as number | null)}
        type="number"
        unit="in"
        required
        helper={'From your underarm down to where you want the hem. Usually 14–17”.'}
        unknownFields={noUnknown}
        onMarkUnknown={noop}
        step={0.25}
        min={8}
        max={30}
      />

      <FieldRow
        label="Sleeve length"
        fieldName="sleeve_length"
        value={body.sleeve_length}
        onChange={(v) => updateBody('sleeve_length', v as number | null)}
        type="number"
        unit="in"
        required
        helper={'From your underarm to your wrist bone, arm relaxed. Usually 17–20".'}
        unknownFields={noUnknown}
        onMarkUnknown={noop}
        step={0.25}
        min={8}
        max={30}
      />

      <details className={styles.optionalDetails}>
        <summary className={styles.optionalSummary}>
          Optional measurements <span className={styles.badge}>improves grading</span>
        </summary>
        <div className={styles.optionalFields}>
          <FieldRow
            label="Upper arm circumference"
            fieldName="upper_arm"
            value={body.upper_arm}
            onChange={(v) => updateBody('upper_arm', v as number | null)}
            type="number"
            unit="in"
            helper="Around the fullest part of your bicep, arm relaxed."
            unknownFields={noUnknown}
            onMarkUnknown={noop}
            step={0.25}
            min={8}
            max={30}
          />
          <FieldRow
            label="Neck circumference"
            fieldName="neck_circumference"
            value={body.neck_circumference}
            onChange={(v) => updateBody('neck_circumference', v as number | null)}
            type="number"
            unit="in"
            helper="Around the base of your neck."
            unknownFields={noUnknown}
            onMarkUnknown={noop}
            step={0.25}
            min={10}
            max={22}
          />
          <FieldRow
            label="Wrist circumference"
            fieldName="wrist"
            value={body.wrist}
            onChange={(v) => updateBody('wrist', v as number | null)}
            type="number"
            unit="in"
            unknownFields={noUnknown}
            onMarkUnknown={noop}
            step={0.25}
            min={4}
            max={10}
          />
          <FieldRow
            label="Waist circumference"
            fieldName="waist"
            value={body.waist}
            onChange={(v) => updateBody('waist', v as number | null)}
            type="number"
            unit="in"
            helper="Around your natural waist."
            unknownFields={noUnknown}
            onMarkUnknown={noop}
            step={0.25}
            min={20}
            max={70}
          />
          <FieldRow
            label="High hip circumference"
            fieldName="high_hip"
            value={body.high_hip}
            onChange={(v) => updateBody('high_hip', v as number | null)}
            type="number"
            unit="in"
            helper={'About 3–4" below your natural waist.'}
            unknownFields={noUnknown}
            onMarkUnknown={noop}
            step={0.25}
            min={24}
            max={80}
          />
        </div>
      </details>
    </StepLayout>
  );
}
