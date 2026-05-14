import React from 'react';
import { FormState, ValidationIssue } from '../../types';
import { StepLayout } from '../StepLayout';
import { RaglanCounts } from './RaglanCounts';
import { BottomUpCounts } from './BottomUpCounts';
import styles from './StitchCounts.module.css';

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

export function Step4_StitchCounts({
  state,
  onBack,
  onNext,
  updateSpec,
  issues,
}: Props) {
  const { spec } = state;
  const construction = spec.construction;

  const stitchIssues = issues.filter(
    (i) => i.field.startsWith('stitches') || i.field === 'gauge',
  );

  return (
    <StepLayout
      step={4}
      totalSteps={9}
      title="Stitch Counts"
      subtitle="Enter the stitch counts from your reference size."
      onBack={onBack}
      onNext={onNext}
      issues={stitchIssues}
    >
      {construction === 'top_down_raglan' && (
        <RaglanCounts spec={spec} updateSpec={updateSpec} issues={stitchIssues} />
      )}

      {construction === 'bottom_up_seamed' && (
        <BottomUpCounts spec={spec} updateSpec={updateSpec} issues={stitchIssues} />
      )}

      {construction === 'drop_shoulder' && (
        <div className={styles.comingSoon}>
          <p>Drop shoulder stitch count entry is coming soon.</p>
          <p>
            For now, skip to Step 5 and use the JSON export to add stitch counts
            manually if needed.
          </p>
        </div>
      )}

      {construction === 'top_down_yoke' && (
        <div className={styles.comingSoon}>
          <p>Top-down yoke is coming soon. Skip ahead for now.</p>
        </div>
      )}
    </StepLayout>
  );
}
