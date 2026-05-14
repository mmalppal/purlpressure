import React from 'react';
import { FormState, ValidationIssue } from '../types';
import { StepLayout } from './StepLayout';
import { FieldRow } from './FieldRow';
import styles from './Step2_Gauge.module.css';

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

export function Step2_Gauge({
  state,
  onBack,
  onNext,
  updateSpec,
  issues,
}: Props) {
  const { spec } = state;
  const g = spec.gauge;
  const gaugeIssues = issues.filter(
    (i) => i.field === 'gauge' || i.field === 'gauge.sts_per_4in',
  );

  const stsPerInch =
    g.sts_per_4in !== null ? (g.sts_per_4in / 4).toFixed(2) : null;
  const rowsPerInch =
    g.rows_per_4in !== null ? (g.rows_per_4in / 4).toFixed(2) : null;

  function updateGauge<K extends keyof typeof g>(key: K, value: (typeof g)[K]) {
    updateSpec('gauge', { ...g, [key]: value });
  }

  return (
    <StepLayout
      step={2}
      totalSteps={9}
      title="Gauge"
      subtitle="Enter the gauge from your pattern."
      onBack={onBack}
      onNext={onNext}
      issues={issues}
    >
      <div className={styles.callout}>
        <p>
          Find this in your pattern under{' '}
          <strong>&ldquo;Gauge&rdquo;</strong> or{' '}
          <strong>&ldquo;Tension&rdquo;</strong>. It looks like:
        </p>
        <blockquote className={styles.example}>
          22 sts &times; 32 rows = 4 inches in stockinette, blocked
        </blockquote>
        <p>Enter 22 for stitches and 32 for rows.</p>
      </div>

      <FieldRow
        label="Stitches per 4 inches"
        fieldName="gauge.sts_per_4in"
        value={g.sts_per_4in}
        onChange={(v) => updateGauge('sts_per_4in', v as number | null)}
        type="number"
        unit="sts / 4in"
        required
        min={1}
        max={80}
        step={0.5}
        placeholder="e.g. 22"
        issue={gaugeIssues.find((i) => i.field === 'gauge.sts_per_4in')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={(f) =>
          updateSpec('unknown_fields', [...spec.unknown_fields, f].filter(
            (x, i, a) => a.indexOf(x) === i,
          ))
        }
      />

      <FieldRow
        label="Rows per 4 inches"
        fieldName="gauge.rows_per_4in"
        value={g.rows_per_4in}
        onChange={(v) => updateGauge('rows_per_4in', v as number | null)}
        type="number"
        unit="rows / 4in"
        required
        min={1}
        max={120}
        step={0.5}
        placeholder="e.g. 32"
        issue={gaugeIssues.find((i) => i.field === 'gauge')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={(f) =>
          updateSpec('unknown_fields', [...spec.unknown_fields, f].filter(
            (x, i, a) => a.indexOf(x) === i,
          ))
        }
      />

      {(stsPerInch || rowsPerInch) && (
        <div className={styles.computed}>
          {stsPerInch && (
            <span>
              <strong>{stsPerInch}</strong> sts/inch
            </span>
          )}
          {rowsPerInch && (
            <span>
              <strong>{rowsPerInch}</strong> rows/inch
            </span>
          )}
        </div>
      )}

      <div className={styles.field}>
        <label className={styles.label}>Gauge stitch</label>
        <input
          type="text"
          className={styles.input}
          value={g.swatch_stitch}
          onChange={(e) => updateGauge('swatch_stitch', e.target.value)}
          placeholder="stockinette"
        />
      </div>

      <div className={styles.radioGroup}>
        <span className={styles.label}>Gauge measured:</span>
        <div className={styles.radios}>
          {[
            { value: 'blocked', label: 'Blocked' },
            { value: 'unblocked', label: 'Unblocked' },
            { value: '', label: 'Not specified' },
          ].map((opt) => (
            <label key={opt.value} className={styles.radioLabel}>
              <input
                type="radio"
                name="gauge_note"
                value={opt.value}
                checked={g.note === opt.value}
                onChange={() => updateGauge('note', opt.value)}
                className={styles.radio}
              />
              {opt.label}
            </label>
          ))}
        </div>
      </div>
    </StepLayout>
  );
}
