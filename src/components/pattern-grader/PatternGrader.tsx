import React from 'react';
import './PatternGrader.css';
import { useFormState } from './hooks/useFormState';
import { useValidation } from './hooks/useValidation';

import { Step1_PatternInfo } from './components/Step1_PatternInfo';
import { Step2_Gauge } from './components/Step2_Gauge';
import { Step3_Sizes } from './components/Step3_Sizes';
import { Step4_StitchCounts } from './components/Step4_StitchCounts/index';
import { Step5_Lengths } from './components/Step5_Lengths';
import { Step6_ShapingRates } from './components/Step6_ShapingRates';
import { Step7_YourMeasurements } from './components/Step7_YourMeasurements';
import { Step8_Ease } from './components/Step8_Ease';
import { Step9_ReviewGenerate } from './components/Step9_ReviewGenerate';

export default function PatternGrader() {
  const {
    state,
    setStep,
    updateSpec,
    updateBody,
    setEase,
    reset,
    exportJson,
    importJson,
  } = useFormState();

  const issues = useValidation(state);
  const step = state.step;

  function goNext() {
    if (step < 9) setStep(step + 1);
  }

  function goBack() {
    if (step > 1) setStep(step - 1);
  }

  return (
    <div className="pg-root">
      {step === 1 && (
        <Step1_PatternInfo
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateSpec={updateSpec}
          reset={reset}
          importJson={importJson}
        />
      )}

      {step === 2 && (
        <Step2_Gauge
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateSpec={updateSpec}
          issues={issues}
        />
      )}

      {step === 3 && (
        <Step3_Sizes
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateSpec={updateSpec}
        />
      )}

      {step === 4 && (
        <Step4_StitchCounts
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateSpec={updateSpec}
          issues={issues}
        />
      )}

      {step === 5 && (
        <Step5_Lengths
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateSpec={updateSpec}
          issues={issues}
        />
      )}

      {step === 6 && (
        <Step6_ShapingRates
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateSpec={updateSpec}
          issues={issues}
        />
      )}

      {step === 7 && (
        <Step7_YourMeasurements
          state={state}
          onBack={goBack}
          onNext={goNext}
          updateBody={updateBody}
        />
      )}

      {step === 8 && (
        <Step8_Ease
          state={state}
          onBack={goBack}
          onNext={goNext}
          setEase={setEase}
        />
      )}

      {step === 9 && (
        <Step9_ReviewGenerate
          state={state}
          onBack={goBack}
          issues={issues}
          exportJson={exportJson}
        />
      )}
    </div>
  );
}
