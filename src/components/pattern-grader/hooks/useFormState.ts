import { useState, useCallback } from 'react';
import {
  FormState,
  DEFAULT_FORM_STATE,
  PatternSpec,
  BodyMeasurements,
  EasePreset,
} from '../types';

const STORAGE_KEY = 'pattern_input_form_v1';

function loadFromStorage(): FormState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...DEFAULT_FORM_STATE, ...JSON.parse(raw) };
  } catch {
    // ignore
  }
  return DEFAULT_FORM_STATE;
}

export function useFormState() {
  const [state, setState] = useState<FormState>(loadFromStorage);

  const save = useCallback(
    (next: FormState) => {
      setState(next);
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // ignore
      }
    },
    [],
  );

  const setStep = useCallback(
    (step: number) => save({ ...state, step }),
    [state, save],
  );

  const updateSpec = useCallback(
    <K extends keyof PatternSpec>(key: K, value: PatternSpec[K]) => {
      save({ ...state, spec: { ...state.spec, [key]: value } });
    },
    [state, save],
  );

  const updateBody = useCallback(
    <K extends keyof BodyMeasurements>(key: K, value: BodyMeasurements[K]) => {
      save({ ...state, body: { ...state.body, [key]: value } });
    },
    [state, save],
  );

  const setEase = useCallback(
    (ease: EasePreset) => save({ ...state, ease }),
    [state, save],
  );

  const reset = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setState(DEFAULT_FORM_STATE);
  }, []);

  const exportJson = useCallback(() => {
    const blob = new Blob([JSON.stringify(state.spec, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${state.spec.pattern_name || 'pattern'}-spec.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [state]);

  const importJson = useCallback(
    (file: File) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const spec = JSON.parse(e.target?.result as string) as PatternSpec;
          save({ ...state, spec });
        } catch {
          alert('Could not parse JSON file.');
        }
      };
      reader.readAsText(file);
    },
    [state, save],
  );

  return {
    state,
    setStep,
    updateSpec,
    updateBody,
    setEase,
    reset,
    exportJson,
    importJson,
  };
}
