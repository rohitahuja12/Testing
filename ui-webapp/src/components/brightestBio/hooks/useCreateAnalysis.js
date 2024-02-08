import { useState, useCallback, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { saveAnalysis } from '../../../actions/analysisTemplateActions';
import { analysisSelector, clearLastSavedAnalysis } from '../../../features/analysis/analysisSlice';

export const useCreateAnalysis = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [analysisCreationInProgress, setAnalysisCreationInProgress] = useState(false);
  const { lastSavedAnalysis } = useSelector(analysisSelector);
  const analysisCreationFailed = useMemo(() => !!lastSavedAnalysis?.error, [lastSavedAnalysis]);

  /** sample analysis object
   * {
   * scanId: selectedScanId,
   * templateId: template._id,
   * }
   */
  const createAnalysis = useCallback(async () => {
    setAnalysisCreationInProgress(true);
    dispatch(saveAnalysis(analysis));
  }, [analysis]);

  useEffect(() => {
    if (lastSavedAnalysis?._id && analysisCreationInProgress) {
      setAnalysisCreationInProgress(false);
      dispatch(clearLastSavedAnalysis());
      navigate(`/view-results/analyses?analysis=${lastSavedAnalysis?._id}`); // TODO: navigate to view individual analysis
    } else if (lastSavedAnalysis?.error && analysisCreationInProgress) {
      setAnalysisCreationInProgress(false);
    }
  }, [lastSavedAnalysis]);

  return { analysis, setAnalysis, createAnalysis, analysisCreationInProgress, analysisCreationFailed };
}