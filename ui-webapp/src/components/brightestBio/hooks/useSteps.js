import { useState, useCallback, useEffect } from 'react';

/**
 * 
 * @param {number} totalSteps 
 */
export const useSteps = (totalSteps) => {
  const [activeStep, setActiveStep] = useState(0);
  const [isLastStep, setIsLastStep] = useState(false);
  const [isFirstStep, setIsFirstStep] = useState(true);

  const nextStep = useCallback(() => {
    if (activeStep === totalSteps) return;
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  }, [activeStep, totalSteps]);

  const prevStep = useCallback(() => {
    if (activeStep === 0) return;
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  }, [activeStep]);

  useEffect(() => {
    setIsLastStep(activeStep === (totalSteps - 1));
    setIsFirstStep(activeStep === 0);
  }, [activeStep, totalSteps]);

  return {
    activeStep,
    nextStep,
    prevStep,
    isLastStep,
    isFirstStep
  };
}