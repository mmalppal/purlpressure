import React from 'react';
import { FormState, EasePreset } from '../types';
import { StepLayout } from './StepLayout';
import styles from './Step8_Ease.module.css';

interface Props {
  state: FormState;
  onBack: () => void;
  onNext: () => void;
  setEase: (ease: EasePreset) => void;
}

interface EaseOption {
  value: EasePreset;
  label: string;
  description: string;
  easeRange: string;
}

const EASE_OPTIONS: EaseOption[] = [
  {
    value: 'skin_tight',
    label: 'Skin Tight',
    description: 'Very close fit, negative ease. Think form-fitting tee.',
    easeRange: '−2" to 0"',
  },
  {
    value: 'close_fitting',
    label: 'Close Fitting',
    description: 'Fitted silhouette with minimal positive ease.',
    easeRange: '0" to 1"',
  },
  {
    value: 'classic',
    label: 'Classic',
    description: 'Standard comfortable fit. The most common ease for knitwear.',
    easeRange: '~2"',
  },
  {
    value: 'relaxed',
    label: 'Relaxed',
    description: 'Comfortable and roomy without being boxy.',
    easeRange: '3" to 4"',
  },
  {
    value: 'oversized',
    label: 'Oversized',
    description: 'Dramatic ease for a boxy, oversized look.',
    easeRange: '5"+',
  },
  {
    value: 'plus_friendly_classic',
    label: 'Plus-Friendly Classic',
    description:
      'Classic ease proportions with plus-size shaping adjustments — wider shoulders, fuller sleeve caps, more hip room.',
    easeRange: '~2" + adjustments',
  },
];

export function Step8_Ease({ state, onBack, onNext, setEase }: Props) {
  const bust = state.body.bust;
  const isPlus = bust !== null && bust > 44;

  return (
    <StepLayout
      step={8}
      totalSteps={9}
      title="Ease Preference"
      subtitle="How much extra room do you like in a sweater?"
      onBack={onBack}
      onNext={onNext}
    >
      {isPlus && (
        <div className={styles.plusNote}>
          Based on your bust measurement ({bust}&quot;), the{' '}
          <strong>Plus-Friendly Classic</strong> preset is recommended. It uses
          standard ease but applies proportional shaping throughout.
        </div>
      )}

      <div className={styles.grid}>
        {EASE_OPTIONS.map((opt) => {
          const isActive = state.ease === opt.value;
          const isRecommended = isPlus && opt.value === 'plus_friendly_classic';
          const isDefault = !isPlus && opt.value === 'classic';

          return (
            <button
              key={opt.value}
              type="button"
              className={`${styles.card} ${isActive ? styles.cardActive : ''} ${
                isRecommended ? styles.cardRecommended : ''
              }`}
              onClick={() => setEase(opt.value)}
            >
              <div className={styles.cardTop}>
                <span className={styles.cardLabel}>{opt.label}</span>
                <div className={styles.badges}>
                  {isRecommended && (
                    <span className={styles.badge}>Recommended</span>
                  )}
                  {isDefault && !isPlus && (
                    <span className={styles.badgeDefault}>Default</span>
                  )}
                </div>
              </div>
              <span className={styles.easeRange}>{opt.easeRange}</span>
              <p className={styles.cardDesc}>{opt.description}</p>
              {isActive && <div className={styles.checkmark}>✓</div>}
            </button>
          );
        })}
      </div>
    </StepLayout>
  );
}
