import React, { useState } from 'react';
import { marked } from 'marked';
import { FormState, ValidationIssue } from '../types';
import { StepLayout } from './StepLayout';
import styles from './Step9_ReviewGenerate.module.css';

interface Props {
  state: FormState;
  onBack: () => void;
  issues: ValidationIssue[];
  exportJson: () => void;
}

interface GradeResponse {
  pattern?: string;
  error?: string;
}

export function Step9_ReviewGenerate({
  state,
  onBack,
  issues,
  exportJson,
}: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const { spec, body, ease } = state;
  const refSize = spec.sizes.find((s) => s.label === spec.reference_size);
  const errorCount = issues.filter((i) => i.severity === 'error').length;

  async function handleGenerate() {
    setLoading(true);
    setApiError(null);
    setResult(null);

    const payload = {
      gauge: {
        sts_per_4in: spec.gauge.sts_per_4in,
        rows_per_4in: spec.gauge.rows_per_4in,
      },
      measurements: {
        bust: body.bust,
        yoke_depth: body.yoke_depth,
        body_length: body.body_length,
        sleeve_length: body.sleeve_length,
        upper_arm: body.upper_arm,
        neck_circumference: body.neck_circumference,
        wrist: body.wrist,
        waist: body.waist,
        high_hip: body.high_hip,
      },
      ease,
      options: {
        pattern_name: spec.pattern_name,
        designer: spec.designer,
        construction: spec.construction,
        reference_size: spec.reference_size,
      },
      spec,
    };

    try {
      const res = await fetch('/api/grade-pattern', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data: GradeResponse = await res.json();
      if (!res.ok || data.error) {
        setApiError(data.error ?? `Server error: ${res.status}`);
      } else {
        setResult(data.pattern ?? JSON.stringify(data, null, 2));
      }
    } catch (e) {
      setApiError(e instanceof Error ? e.message : 'Network error');
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (!result) return;
    try {
      await navigator.clipboard.writeText(result);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback — not critical
    }
  }

  const renderedHtml =
    result ? (marked.parse(result) as string) : null;

  return (
    <StepLayout
      step={9}
      totalSteps={9}
      title="Review & Generate"
      subtitle="Check everything looks right, then generate your graded pattern."
      onBack={onBack}
      onNext={handleGenerate}
      nextLabel={loading ? 'Generating…' : 'Generate Pattern'}
      issues={issues}
    >
      {/* Summary table */}
      <section className={styles.section}>
        <div className={styles.sectionLabel}>Pattern Summary</div>
        <table className={styles.summaryTable}>
          <tbody>
            <SummaryRow label="Pattern" value={spec.pattern_name || '—'} />
            <SummaryRow label="Designer" value={spec.designer || '—'} />
            <SummaryRow label="Construction" value={spec.construction.replace(/_/g, ' ')} />
            <SummaryRow
              label="Gauge"
              value={
                spec.gauge.sts_per_4in && spec.gauge.rows_per_4in
                  ? `${spec.gauge.sts_per_4in} sts × ${spec.gauge.rows_per_4in} rows / 4"`
                  : '—'
              }
            />
            <SummaryRow label="Reference size" value={spec.reference_size || '—'} />
            {refSize?.finished_bust && (
              <SummaryRow
                label="Pattern bust"
                value={`${refSize.finished_bust}"`}
              />
            )}
          </tbody>
        </table>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionLabel}>Your Measurements vs Pattern</div>
        <table className={styles.summaryTable}>
          <thead>
            <tr>
              <th className={styles.th}>Measurement</th>
              <th className={styles.th}>You</th>
              <th className={styles.th}>Pattern ref</th>
            </tr>
          </thead>
          <tbody>
            <CompareRow
              label="Bust"
              yours={body.bust}
              pattern={refSize?.finished_bust ?? null}
              unit="in"
            />
            <CompareRow
              label="Sleeve length"
              yours={body.sleeve_length}
              pattern={refSize?.finished_sleeve ?? null}
              unit="in"
            />
            <CompareRow
              label="Body length"
              yours={body.body_length}
              pattern={refSize?.finished_length ?? null}
              unit="in"
            />
          </tbody>
        </table>
        <p className={styles.easeNote}>
          Ease preset: <strong>{ease.replace(/_/g, ' ')}</strong>
        </p>
      </section>

      {/* Validation issues */}
      {issues.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>
            Validation ({issues.length} issue{issues.length !== 1 ? 's' : ''})
          </div>
          <ul className={styles.issueList}>
            {issues.map((issue, i) => (
              <li
                key={i}
                className={`${styles.issueItem} ${styles[`issue_${issue.severity}`]}`}
              >
                <span className={styles.issueField}>{issue.field}</span>
                <span>{issue.message}</span>
              </li>
            ))}
          </ul>
          {errorCount > 0 && (
            <p className={styles.errorWarning}>
              There {errorCount === 1 ? 'is' : 'are'} {errorCount} error
              {errorCount !== 1 ? 's' : ''} above. The grader may still run,
              but results could be inaccurate.
            </p>
          )}
        </section>
      )}

      <div className={styles.actions}>
        <button
          type="button"
          className={styles.exportBtn}
          onClick={exportJson}
        >
          Export JSON spec
        </button>
        <button
          type="button"
          className={styles.generateBtn}
          onClick={handleGenerate}
          disabled={loading}
        >
          {loading ? (
            <span className={styles.spinner} aria-hidden="true" />
          ) : null}
          {loading ? 'Generating…' : 'Generate Pattern'}
        </button>
      </div>

      {/* API Error */}
      {apiError && (
        <div className={styles.apiError} role="alert">
          <strong>Error:</strong> {apiError}
        </div>
      )}

      {/* Result */}
      {result && (
        <section className={styles.resultSection}>
          <div className={styles.resultHeader}>
            <div className={styles.sectionLabel}>Generated Pattern</div>
            <button
              type="button"
              className={styles.copyBtn}
              onClick={handleCopy}
            >
              {copied ? '✓ Copied' : 'Copy Markdown'}
            </button>
          </div>
          <div
            className={styles.renderedMarkdown}
            dangerouslySetInnerHTML={{ __html: renderedHtml ?? '' }}
          />
        </section>
      )}
    </StepLayout>
  );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <tr>
      <td className={styles.summaryLabel}>{label}</td>
      <td className={styles.summaryValue}>{value}</td>
    </tr>
  );
}

function CompareRow({
  label,
  yours,
  pattern,
  unit,
}: {
  label: string;
  yours: number | null;
  pattern: number | null;
  unit: string;
}) {
  const diff =
    yours !== null && pattern !== null ? yours - pattern : null;
  const absDiff = diff !== null ? Math.abs(diff) : null;

  return (
    <tr>
      <td className={styles.summaryLabel}>{label}</td>
      <td className={styles.summaryValue}>
        {yours !== null ? `${yours}${unit}` : '—'}
      </td>
      <td className={styles.summaryValue}>
        {pattern !== null ? `${pattern}${unit}` : '—'}
        {absDiff !== null && absDiff > 0 && (
          <span
            className={`${styles.diffChip} ${
              absDiff > 3 ? styles.diffLarge : styles.diffSmall
            }`}
          >
            {diff! > 0 ? '+' : ''}
            {diff!.toFixed(1)}
          </span>
        )}
      </td>
    </tr>
  );
}
