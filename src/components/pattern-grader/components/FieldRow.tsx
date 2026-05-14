import React, { useId, useState } from 'react';
import { ValidationIssue } from '../types';
import styles from './FieldRow.module.css';

interface FieldRowProps {
  label: string;
  fieldName: string;
  value: number | string | null;
  onChange: (value: number | string | null) => void;
  type?: 'number' | 'text';
  unit?: string;
  helper?: string;
  issue?: ValidationIssue;
  required?: boolean;
  unknownFields: string[];
  onMarkUnknown: (field: string) => void;
  min?: number;
  max?: number;
  step?: number;
  placeholder?: string;
}

export function FieldRow({
  label,
  fieldName,
  value,
  onChange,
  type = 'number',
  unit,
  helper,
  issue,
  required,
  unknownFields,
  onMarkUnknown,
  min,
  max,
  step,
  placeholder,
}: FieldRowProps) {
  const id = useId();
  const [touched, setTouched] = useState(false);
  const isUnknown = unknownFields.includes(fieldName);

  const displayValue =
    value === null ? '' : String(value);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const raw = e.target.value;
    if (type === 'number') {
      if (raw === '' || raw === '-') {
        onChange(null);
      } else {
        const parsed = parseFloat(raw);
        onChange(isNaN(parsed) ? null : parsed);
      }
    } else {
      onChange(raw === '' ? null : raw);
    }
  }

  function handleMarkUnknown() {
    onMarkUnknown(fieldName);
    onChange(null);
  }

  const showIssue = touched && issue;

  return (
    <div className={`${styles.row} ${isUnknown ? styles.isUnknown : ''}`}>
      <label htmlFor={id} className={styles.label}>
        {label}
        {required && <span className={styles.required}>*</span>}
        {unit && <span className={styles.unit}>{unit}</span>}
      </label>

      <div className={styles.inputWrap}>
        <input
          id={id}
          type={type}
          className={`${styles.input} ${showIssue ? styles[`input_${issue.severity}`] : ''}`}
          value={isUnknown ? '' : displayValue}
          onChange={handleChange}
          onBlur={() => setTouched(true)}
          placeholder={isUnknown ? 'Marked as unknown' : placeholder}
          disabled={isUnknown}
          min={min}
          max={max}
          step={step}
          aria-describedby={
            [helper ? `${id}-helper` : '', issue ? `${id}-issue` : '']
              .filter(Boolean)
              .join(' ') || undefined
          }
          aria-invalid={showIssue && issue.severity === 'error' ? true : undefined}
        />

        <button
          type="button"
          className={`${styles.unknownBtn} ${isUnknown ? styles.unknownBtnActive : ''}`}
          onClick={handleMarkUnknown}
          title={isUnknown ? 'Already marked as unknown' : "I can't find this value"}
          aria-label={isUnknown ? 'Marked as unknown' : "I can't find this value"}
        >
          {isUnknown ? '✓' : '?'}
        </button>
      </div>

      {helper && (
        <p id={`${id}-helper`} className={styles.helper}>
          {helper}
        </p>
      )}

      {showIssue && (
        <p
          id={`${id}-issue`}
          className={`${styles.issueMsg} ${styles[`issue_${issue.severity}`]}`}
          role={issue.severity === 'error' ? 'alert' : undefined}
        >
          {issue.message}
        </p>
      )}
    </div>
  );
}
