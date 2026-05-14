export type ConstructionType =
  | 'top_down_raglan'
  | 'bottom_up_seamed'
  | 'drop_shoulder'
  | 'top_down_yoke'
  | 'set_in_sleeve';

export interface PatternGauge {
  sts_per_4in: number | null;
  rows_per_4in: number | null;
  swatch_stitch: string;
  note: string; // 'blocked' | 'unblocked' | ''
}

export interface SizeEntry {
  label: string;
  finished_bust: number | null;
  finished_length: number | null;
  finished_sleeve: number | null;
  finished_upper_arm: number | null;
  target_body_bust: number | null;
}

export interface StitchCounts {
  // Top-down raglan
  neck_cast_on: number | null;
  back_cast_on: number | null;
  front_cast_on: number | null;
  each_sleeve_cast_on: number | null;
  body_at_yoke_end: number | null;
  each_sleeve_at_yoke_end: number | null;
  underarm_cast_on_each: number | null;
  body_at_chest: number | null;
  each_sleeve_at_underarm: number | null;
  body_at_waist: number | null;
  body_at_hem: number | null;
  each_sleeve_at_cuff: number | null;
  // Bottom-up seamed
  hem_cast_on: number | null;
  waist_sts: number | null;
  bust_sts: number | null;
  armhole_bind_off: number | null;
  shoulder_sts: number | null;
  neck_bind_off: number | null;
  sleeve_cast_on: number | null;
  sleeve_at_underarm: number | null;
  sleeve_cap_rows: number | null;
}

export interface LengthMeasurements {
  yoke_depth: number | null;
  body_length_total: number | null;
  sleeve_length_total: number | null;
  waist_above_hem: number | null;
  bust_above_waist: number | null;
  armhole_depth: number | null;
  neckband_depth: number | null;
  hem_ribbing_depth: number | null;
  cuff_ribbing_depth: number | null;
}

export interface ShapingRates {
  raglan_inc_every_n_rows: number | null;
  waist_dec_every_n_rows: number | null;
  waist_dec_sts_per_round: number | null;
  hip_inc_every_n_rows: number | null;
  hip_inc_sts_per_round: number | null;
  sleeve_dec_every_n_rows: number | null;
  sleeve_dec_sts_per_round: number | null;
  armhole_dec_every_n_rows: number | null;
  armhole_dec_sts_per_row: number | null;
}

export interface BodyMeasurements {
  bust: number | null;
  yoke_depth: number | null;
  body_length: number | null;
  sleeve_length: number | null;
  upper_arm: number | null;
  neck_circumference: number | null;
  wrist: number | null;
  waist: number | null;
  high_hip: number | null;
}

export interface PatternSpec {
  pattern_name: string;
  designer: string;
  source_url: string;
  construction: ConstructionType;
  gauge: PatternGauge;
  sizes: SizeEntry[];
  reference_size: string;
  stitches: StitchCounts;
  lengths: LengthMeasurements;
  shaping: ShapingRates;
  notes: string[];
  unknown_fields: string[];
}

export type EasePreset =
  | 'skin_tight'
  | 'close_fitting'
  | 'classic'
  | 'relaxed'
  | 'oversized'
  | 'plus_friendly_classic';

export interface FormState {
  step: number;
  spec: PatternSpec;
  body: BodyMeasurements;
  ease: EasePreset;
  output_pattern_name: string;
}

export interface ValidationIssue {
  field: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
}

// ─── Defaults ────────────────────────────────────────────────────────────────

export const DEFAULT_SPEC: PatternSpec = {
  pattern_name: '',
  designer: '',
  source_url: '',
  construction: 'top_down_raglan',
  gauge: { sts_per_4in: null, rows_per_4in: null, swatch_stitch: 'stockinette', note: '' },
  sizes: [],
  reference_size: '',
  stitches: {
    neck_cast_on: null, back_cast_on: null, front_cast_on: null,
    each_sleeve_cast_on: null, body_at_yoke_end: null, each_sleeve_at_yoke_end: null,
    underarm_cast_on_each: null, body_at_chest: null, each_sleeve_at_underarm: null,
    body_at_waist: null, body_at_hem: null, each_sleeve_at_cuff: null,
    hem_cast_on: null, waist_sts: null, bust_sts: null, armhole_bind_off: null,
    shoulder_sts: null, neck_bind_off: null, sleeve_cast_on: null,
    sleeve_at_underarm: null, sleeve_cap_rows: null,
  },
  lengths: {
    yoke_depth: null, body_length_total: null, sleeve_length_total: null,
    waist_above_hem: null, bust_above_waist: null, armhole_depth: null,
    neckband_depth: null, hem_ribbing_depth: null, cuff_ribbing_depth: null,
  },
  shaping: {
    raglan_inc_every_n_rows: null, waist_dec_every_n_rows: null,
    waist_dec_sts_per_round: null, hip_inc_every_n_rows: null,
    hip_inc_sts_per_round: null, sleeve_dec_every_n_rows: null,
    sleeve_dec_sts_per_round: null, armhole_dec_every_n_rows: null,
    armhole_dec_sts_per_row: null,
  },
  notes: [],
  unknown_fields: [],
};

export const DEFAULT_BODY: BodyMeasurements = {
  bust: null, yoke_depth: null, body_length: null, sleeve_length: null,
  upper_arm: null, neck_circumference: null, wrist: null, waist: null, high_hip: null,
};

export const DEFAULT_FORM_STATE: FormState = {
  step: 1,
  spec: DEFAULT_SPEC,
  body: DEFAULT_BODY,
  ease: 'classic',
  output_pattern_name: '',
};
