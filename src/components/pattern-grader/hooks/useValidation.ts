import { useMemo } from 'react';
import { FormState, ValidationIssue } from '../types';

export function useValidation(state: FormState): ValidationIssue[] {
  return useMemo(() => {
    const issues: ValidationIssue[] = [];
    const { spec } = state;
    const g = spec.gauge;

    // Gauge checks
    if (g.sts_per_4in !== null && g.rows_per_4in !== null) {
      if (g.rows_per_4in < g.sts_per_4in) {
        issues.push({
          field: 'gauge',
          severity: 'warning',
          message: "Rows per 4\" is less than stitches — have you swapped them?",
        });
      }
      if (g.sts_per_4in / 4 > 10) {
        issues.push({
          field: 'gauge.sts_per_4in',
          severity: 'warning',
          message: "More than 10 sts/inch — are you sure you're entering per 4\"?",
        });
      }
    }

    // Raglan cast-on sum check
    if (spec.construction === 'top_down_raglan') {
      const {
        back_cast_on: b,
        front_cast_on: f,
        each_sleeve_cast_on: s,
        neck_cast_on: t,
      } = spec.stitches;

      if (b !== null && f !== null && s !== null && t !== null) {
        const computed = b + f + 2 * s + 4;
        const diff = Math.abs(computed - t);
        if (diff > 4) {
          issues.push({
            field: 'stitches.neck_cast_on',
            severity: 'error',
            message: `Cast-on parts sum to ${computed} but total is ${t} (off by ${diff}).`,
          });
        } else if (diff > 2) {
          issues.push({
            field: 'stitches.neck_cast_on',
            severity: 'warning',
            message: `Cast-on parts sum to ${computed} but total is ${t}. Double-check.`,
          });
        }
      }

      const {
        body_at_chest: chest,
        body_at_yoke_end: yoke,
        body_at_waist: waist,
        body_at_hem: hem,
      } = spec.stitches;

      if (chest !== null && yoke !== null && chest <= yoke) {
        issues.push({
          field: 'stitches.body_at_chest',
          severity: 'error',
          message: `Body at chest (${chest}) must be greater than body at yoke end (${yoke}).`,
        });
      }
      if (waist !== null && chest !== null && waist > chest) {
        issues.push({
          field: 'stitches.body_at_waist',
          severity: 'error',
          message: `Waist sts (${waist}) cannot exceed chest sts (${chest}).`,
        });
      }
      if (hem !== null && waist !== null && hem < waist) {
        issues.push({
          field: 'stitches.body_at_hem',
          severity: 'error',
          message: `Hem sts (${hem}) cannot be less than waist sts (${waist}).`,
        });
      }
    }

    // Bottom-up seamed checks
    if (spec.construction === 'bottom_up_seamed') {
      const {
        waist_sts: w,
        hem_cast_on: h,
        bust_sts: bust,
        shoulder_sts: sh,
        neck_bind_off: nk,
      } = spec.stitches;

      if (w !== null && h !== null && w >= h) {
        issues.push({
          field: 'stitches.waist_sts',
          severity: 'error',
          message: `Waist sts (${w}) should be less than hem cast-on (${h}).`,
        });
      }
      if (bust !== null && w !== null && bust < w) {
        issues.push({
          field: 'stitches.bust_sts',
          severity: 'error',
          message: `Bust sts (${bust}) is less than waist sts (${w}).`,
        });
      }
      if (sh !== null && bust !== null && sh >= bust) {
        issues.push({
          field: 'stitches.shoulder_sts',
          severity: 'error',
          message: `Shoulder sts (${sh}) should be less than bust sts (${bust}).`,
        });
      }
      if (nk !== null && sh !== null && nk >= sh) {
        issues.push({
          field: 'stitches.neck_bind_off',
          severity: 'error',
          message: `Neck bind-off (${nk}) should be less than shoulder sts (${sh}).`,
        });
      }
    }

    // Gauge × stitch consistency check
    if (g.sts_per_4in) {
      const spi = g.sts_per_4in / 4;
      const refSize = spec.sizes.find((sz) => sz.label === spec.reference_size);
      if (refSize?.finished_bust) {
        let computedBust: number | null = null;
        if (
          spec.construction === 'top_down_raglan' &&
          spec.stitches.body_at_chest
        ) {
          computedBust = spec.stitches.body_at_chest / spi;
        } else if (
          spec.construction === 'bottom_up_seamed' &&
          spec.stitches.bust_sts
        ) {
          computedBust = (spec.stitches.bust_sts * 2) / spi;
        }
        if (computedBust !== null) {
          const diff = Math.abs(computedBust - refSize.finished_bust);
          if (diff > 2) {
            issues.push({
              field: 'stitches',
              severity: 'error',
              message: `Gauge + sts gives a bust of ${computedBust.toFixed(1)}" but pattern says ${refSize.finished_bust}" (off by ${diff.toFixed(1)}").`,
            });
          } else if (diff > 1) {
            issues.push({
              field: 'stitches',
              severity: 'warning',
              message: `Gauge + sts gives ${computedBust.toFixed(1)}" but pattern says ${refSize.finished_bust}" — double-check.`,
            });
          }
        }
      }
    }

    return issues;
  }, [state]);
}
