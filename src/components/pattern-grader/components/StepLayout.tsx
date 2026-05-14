import React from 'react';
import { ValidationIssue } from '../types';
import styles from './StepLayout.module.css';

interface StepLayoutProps {
  step: number;
  totalSteps: number;
  title: string;
  subtitle?: string;
  onBack: () => void;
  onNext: () => void;
  onSave?: () => void;
  issues?: ValidationIssue[];
  nextLabel?: string;
  children: React.ReactNode;
}

export function StepLayout({
  step,
  totalSteps,
  title,
  subtitle,
  onBack,
  onNext,
  onSave,
  issues = [],
  nextLabel = 'Next',
  children,
}: StepLayoutProps) {
  const errors = issues.filter((i) => i.severity === 'error').length;
  const warnings = issues.filter((i) => i.severity === 'warning').length;
  const progress = (step / totalSteps) * 100;

  return (
    <div className={styles.layout}>
      <header className={styles.header}>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className={styles.stepMeta}>
          <span className={styles.stepCounter}>
            Step {step} of {totalSteps}
          </span>
          {onSave && (
            <button
              type="button"
              className={styles.saveBtn}
              onClick={onSave}
            >
              Save progress
            </button>
          )}
        </div>
        <h1 className={styles.title}>{title}</h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        {(errors > 0 || warnings > 0) && (
          <div className={styles.issuesSummary}>
            {errors > 0 && (
              <span className={styles.errorBadge}>
                {errors} error{errors !== 1 ? 's' : ''}
              </span>
            )}
            {warnings > 0 && (
              <span className={styles.warningBadge}>
                {warnings} warning{warnings !== 1 ? 's' : ''}
              </span>
            )}
          </div>
        )}
      </header>

      <main className={styles.content}>{children}</main>

      <footer className={styles.footer}>
        <button
          type="button"
          className={styles.backBtn}
          onClick={onBack}
          disabled={step === 1}
        >
          Back
        </button>
        <button
          type="button"
          className={styles.nextBtn}
          onClick={onNext}
        >
          {nextLabel}
        </button>
      </footer>
    </div>
  );
}
