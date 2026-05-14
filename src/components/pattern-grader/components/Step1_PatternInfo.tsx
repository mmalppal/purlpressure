import React, { useRef } from 'react';
import { ConstructionType, FormState } from '../types';
import { StepLayout } from './StepLayout';
import styles from './Step1_PatternInfo.module.css';

interface Props {
  state: FormState;
  onBack: () => void;
  onNext: () => void;
  updateSpec: <K extends keyof FormState['spec']>(
    key: K,
    value: FormState['spec'][K],
  ) => void;
  reset: () => void;
  importJson: (file: File) => void;
}

const CONSTRUCTION_OPTIONS: {
  value: ConstructionType;
  label: string;
  description: string;
  disabled?: boolean;
}[] = [
  {
    value: 'top_down_raglan',
    label: 'Top-Down Raglan',
    description:
      'Cast on at the neck, knit downward with 4 diagonal raglan increase lines.',
  },
  {
    value: 'bottom_up_seamed',
    label: 'Bottom-Up Seamed',
    description: 'Cast on at the hem, knit upward. Pieces are seamed after.',
  },
  {
    value: 'drop_shoulder',
    label: 'Drop Shoulder',
    description: 'Rectangles with minimal armhole shaping. No armhole curve.',
  },
  {
    value: 'top_down_yoke',
    label: 'Top-Down Yoke',
    description:
      'Circular yoke radiating from the neck (coming soon)',
    disabled: true,
  },
];

export function Step1_PatternInfo({
  state,
  onBack,
  onNext,
  updateSpec,
  reset,
  importJson,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { spec } = state;

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) importJson(file);
    e.target.value = '';
  }

  return (
    <StepLayout
      step={1}
      totalSteps={9}
      title="Pattern Info"
      subtitle="Tell us about the pattern you're grading."
      onBack={onBack}
      onNext={onNext}
    >
      <div className={styles.toolbar}>
        <button
          type="button"
          className={styles.toolBtn}
          onClick={() => fileInputRef.current?.click()}
        >
          Load saved JSON
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <button
          type="button"
          className={styles.toolBtnDestructive}
          onClick={() => {
            if (
              window.confirm(
                'Start fresh? All entered data will be cleared.',
              )
            )
              reset();
          }}
        >
          Start fresh
        </button>
      </div>

      <div className={styles.fields}>
        <div className={styles.field}>
          <label className={styles.label}>
            Pattern name <span className={styles.req}>*</span>
          </label>
          <input
            type="text"
            className={styles.input}
            value={spec.pattern_name}
            onChange={(e) => updateSpec('pattern_name', e.target.value)}
            placeholder="e.g. Mara Cardigan"
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Designer</label>
          <input
            type="text"
            className={styles.input}
            value={spec.designer}
            onChange={(e) => updateSpec('designer', e.target.value)}
            placeholder="e.g. Joji Locatelli"
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Ravelry URL</label>
          <input
            type="url"
            className={styles.input}
            value={spec.source_url}
            onChange={(e) => updateSpec('source_url', e.target.value)}
            placeholder="https://www.ravelry.com/patterns/library/..."
          />
        </div>
      </div>

      <div className={styles.sectionLabel}>Construction type</div>
      <div className={styles.constructionGrid}>
        {CONSTRUCTION_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`${styles.constructionCard} ${
              spec.construction === opt.value
                ? styles.constructionCardActive
                : ''
            } ${opt.disabled ? styles.constructionCardDisabled : ''}`}
            onClick={() => !opt.disabled && updateSpec('construction', opt.value)}
            disabled={opt.disabled}
          >
            <span className={styles.constructionLabel}>{opt.label}</span>
            <span className={styles.constructionDesc}>{opt.description}</span>
          </button>
        ))}
      </div>
    </StepLayout>
  );
}
