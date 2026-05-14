import React from 'react';
import { FormState, ShapingRates, ValidationIssue } from '../types';
import { StepLayout } from './StepLayout';
import { FieldRow } from './FieldRow';
import styles from './Step6_ShapingRates.module.css';

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

export function Step6_ShapingRates({
  state,
  onBack,
  onNext,
  updateSpec,
  issues,
}: Props) {
  const { spec } = state;
  const shaping = spec.shaping;
  const isRaglan = spec.construction === 'top_down_raglan';
  const isBottomUp = spec.construction === 'bottom_up_seamed';

  function updateShaping(key: keyof ShapingRates, value: number | null) {
    updateSpec('shaping', { ...shaping, [key]: value });
  }

  function markUnknown(field: string) {
    updateSpec(
      'unknown_fields',
      [...spec.unknown_fields, field].filter((x, i, a) => a.indexOf(x) === i),
    );
  }

  const issueFor = (field: string) =>
    issues.find((i) => i.field === field || i.field === `shaping.${field}`);

  return (
    <StepLayout
      step={6}
      totalSteps={9}
      title="Shaping Rates"
      subtitle="How often shaping occurs in the pattern."
      onBack={onBack}
      onNext={onNext}
      issues={issues}
    >
      <div className={styles.helperCallout}>
        <strong>&ldquo;Every N rows&rdquo;</strong> means the pattern says
        something like <em>&ldquo;decrease every 6th row&rdquo;</em> or{' '}
        <em>&ldquo;increase every other round&rdquo;</em>. Enter the number of
        rows between shaping events. Most fields here are optional — fill in
        what your pattern specifies.
      </div>

      {isRaglan && (
        <>
          <div className={styles.sectionLabel}>Raglan Increases</div>

          <FieldRow
            label="Raglan increase every N rows"
            fieldName="raglan_inc_every_n_rows"
            value={shaping.raglan_inc_every_n_rows}
            onChange={(v) =>
              updateShaping('raglan_inc_every_n_rows', v as number | null)
            }
            type="number"
            unit="rows"
            helper='Usually 2 (every other row/round) for most raglan patterns. Enter 2 if the pattern says "increase every round."'
            issue={issueFor('raglan_inc_every_n_rows')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            min={1}
            step={1}
          />
        </>
      )}

      <div className={styles.sectionLabel}>Waist Shaping</div>

      <FieldRow
        label="Waist decrease every N rows"
        fieldName="waist_dec_every_n_rows"
        value={shaping.waist_dec_every_n_rows}
        onChange={(v) =>
          updateShaping('waist_dec_every_n_rows', v as number | null)
        }
        type="number"
        unit="rows"
        helper="Leave blank if no waist shaping."
        issue={issueFor('waist_dec_every_n_rows')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={markUnknown}
        min={1}
        step={1}
      />
      <FieldRow
        label="Waist decrease stitches per round"
        fieldName="waist_dec_sts_per_round"
        value={shaping.waist_dec_sts_per_round}
        onChange={(v) =>
          updateShaping('waist_dec_sts_per_round', v as number | null)
        }
        type="number"
        unit="sts"
        helper="Total stitches decreased per shaping row/round. Often 4 (2 each side)."
        issue={issueFor('waist_dec_sts_per_round')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={markUnknown}
        min={1}
        step={1}
      />

      <div className={styles.sectionLabel}>Hip Increases</div>

      <FieldRow
        label="Hip increase every N rows"
        fieldName="hip_inc_every_n_rows"
        value={shaping.hip_inc_every_n_rows}
        onChange={(v) =>
          updateShaping('hip_inc_every_n_rows', v as number | null)
        }
        type="number"
        unit="rows"
        issue={issueFor('hip_inc_every_n_rows')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={markUnknown}
        min={1}
        step={1}
      />
      <FieldRow
        label="Hip increase stitches per round"
        fieldName="hip_inc_sts_per_round"
        value={shaping.hip_inc_sts_per_round}
        onChange={(v) =>
          updateShaping('hip_inc_sts_per_round', v as number | null)
        }
        type="number"
        unit="sts"
        issue={issueFor('hip_inc_sts_per_round')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={markUnknown}
        min={1}
        step={1}
      />

      <div className={styles.sectionLabel}>Sleeve Shaping</div>

      <FieldRow
        label="Sleeve decrease every N rows"
        fieldName="sleeve_dec_every_n_rows"
        value={shaping.sleeve_dec_every_n_rows}
        onChange={(v) =>
          updateShaping('sleeve_dec_every_n_rows', v as number | null)
        }
        type="number"
        unit="rows"
        issue={issueFor('sleeve_dec_every_n_rows')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={markUnknown}
        min={1}
        step={1}
      />
      <FieldRow
        label="Sleeve decrease stitches per row"
        fieldName="sleeve_dec_sts_per_round"
        value={shaping.sleeve_dec_sts_per_round}
        onChange={(v) =>
          updateShaping('sleeve_dec_sts_per_round', v as number | null)
        }
        type="number"
        unit="sts"
        helper="Usually 2 (one decrease at each end)."
        issue={issueFor('sleeve_dec_sts_per_round')}
        unknownFields={spec.unknown_fields}
        onMarkUnknown={markUnknown}
        min={1}
        step={1}
      />

      {isBottomUp && (
        <>
          <div className={styles.sectionLabel}>Armhole Shaping</div>

          <FieldRow
            label="Armhole decrease every N rows"
            fieldName="armhole_dec_every_n_rows"
            value={shaping.armhole_dec_every_n_rows}
            onChange={(v) =>
              updateShaping('armhole_dec_every_n_rows', v as number | null)
            }
            type="number"
            unit="rows"
            issue={issueFor('armhole_dec_every_n_rows')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            min={1}
            step={1}
          />
          <FieldRow
            label="Armhole decrease stitches per row"
            fieldName="armhole_dec_sts_per_row"
            value={shaping.armhole_dec_sts_per_row}
            onChange={(v) =>
              updateShaping('armhole_dec_sts_per_row', v as number | null)
            }
            type="number"
            unit="sts"
            issue={issueFor('armhole_dec_sts_per_row')}
            unknownFields={spec.unknown_fields}
            onMarkUnknown={markUnknown}
            min={1}
            step={1}
          />
        </>
      )}
    </StepLayout>
  );
}
