import React from 'react';
import { FormState, SizeEntry } from '../types';
import { StepLayout } from './StepLayout';
import styles from './Step3_Sizes.module.css';

interface Props {
  state: FormState;
  onBack: () => void;
  onNext: () => void;
  updateSpec: <K extends keyof FormState['spec']>(
    key: K,
    value: FormState['spec'][K],
  ) => void;
}

function emptySize(): SizeEntry {
  return {
    label: '',
    finished_bust: null,
    finished_length: null,
    finished_sleeve: null,
    finished_upper_arm: null,
    target_body_bust: null,
  };
}

function numInput(
  value: number | null,
  onChange: (v: number | null) => void,
  placeholder?: string,
) {
  return (
    <input
      type="number"
      value={value === null ? '' : value}
      onChange={(e) => {
        const v = parseFloat(e.target.value);
        onChange(isNaN(v) ? null : v);
      }}
      placeholder={placeholder ?? '—'}
      className={styles.cellInput}
      step="0.25"
      min={0}
    />
  );
}

export function Step3_Sizes({ state, onBack, onNext, updateSpec }: Props) {
  const { spec } = state;
  const sizes = spec.sizes;

  function updateSize(index: number, patch: Partial<SizeEntry>) {
    const next = sizes.map((s, i) => (i === index ? { ...s, ...patch } : s));
    updateSpec('sizes', next);
  }

  function addSize() {
    updateSpec('sizes', [...sizes, emptySize()]);
  }

  function removeSize(index: number) {
    const next = sizes.filter((_, i) => i !== index);
    updateSpec('sizes', next);
    if (spec.reference_size === sizes[index].label) {
      updateSpec('reference_size', '');
    }
  }

  return (
    <StepLayout
      step={3}
      totalSteps={9}
      title="Sizes"
      subtitle="Enter the finished garment measurements from the pattern's size chart."
      onBack={onBack}
      onNext={onNext}
    >
      <p className={styles.helper}>
        These are <strong>finished garment measurements</strong>, not body
        measurements. Find them in your pattern's size chart or schematic.
      </p>

      {sizes.length === 0 ? (
        <div className={styles.empty}>
          No sizes added yet. Click &ldquo;Add Size&rdquo; below.
        </div>
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th className={styles.th}>Label</th>
                <th className={styles.th}>Finished bust&quot;</th>
                <th className={styles.th}>Length&quot;</th>
                <th className={styles.th}>Sleeve&quot;</th>
                <th className={styles.th}>Upper arm&quot;</th>
                <th className={styles.th}></th>
              </tr>
            </thead>
            <tbody>
              {sizes.map((sz, i) => (
                <tr key={i} className={styles.row}>
                  <td className={styles.td}>
                    <input
                      type="text"
                      value={sz.label}
                      onChange={(e) =>
                        updateSize(i, { label: e.target.value })
                      }
                      placeholder="e.g. S, M, 32"
                      className={styles.cellInput}
                    />
                  </td>
                  <td className={styles.td}>
                    {numInput(sz.finished_bust, (v) =>
                      updateSize(i, { finished_bust: v }),
                    )}
                  </td>
                  <td className={styles.td}>
                    {numInput(sz.finished_length, (v) =>
                      updateSize(i, { finished_length: v }),
                    )}
                  </td>
                  <td className={styles.td}>
                    {numInput(sz.finished_sleeve, (v) =>
                      updateSize(i, { finished_sleeve: v }),
                    )}
                  </td>
                  <td className={styles.td}>
                    {numInput(sz.finished_upper_arm, (v) =>
                      updateSize(i, { finished_upper_arm: v }),
                    )}
                  </td>
                  <td className={styles.td}>
                    <button
                      type="button"
                      className={styles.removeBtn}
                      onClick={() => removeSize(i)}
                      aria-label={`Remove size ${sz.label || i + 1}`}
                    >
                      &times;
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <button type="button" className={styles.addBtn} onClick={addSize}>
        + Add Size
      </button>

      {sizes.length > 0 && (
        <div className={styles.referenceSection}>
          <div className={styles.sectionLabel}>Reference size (grading FROM)</div>
          <p className={styles.helper}>
            Which size does your pattern's stitch counts refer to? This is
            typically the size you'd knit if no grading were needed.
          </p>
          <div className={styles.radioGroup}>
            {sizes.map((sz, i) => (
              <label key={i} className={styles.radioLabel}>
                <input
                  type="radio"
                  name="reference_size"
                  value={sz.label}
                  checked={spec.reference_size === sz.label}
                  onChange={() => updateSpec('reference_size', sz.label)}
                  className={styles.radio}
                />
                {sz.label || `Size ${i + 1}`}
                {sz.finished_bust && (
                  <span className={styles.bustHint}>
                    {sz.finished_bust}&quot; bust
                  </span>
                )}
              </label>
            ))}
          </div>
        </div>
      )}
    </StepLayout>
  );
}
