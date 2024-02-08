import { useState, useCallback, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  deleteAnalysisTemplate, getAnalysisTemplates, getAnalysisTemplate
} from '../../../actions/analysisTemplateActions';
import { analysisSelector, clearLoadedAnalysisTemplate } from '../../../features/analysis/analysisSlice';

// sample analysis template
// {
//   "_id": "636544db5ef215e24ff2c477",
//   "createdOn": "2022-11-04T16:59:07.066316",
//   "name": "AB Standards",
//   "notes": "",
//   "productId": "63600b855ef215e24ff2ba6d",
//   "productName": "V2_Inflammatory_Kit_12P_062822",
//   "protocol": "pArrayFluoro",
// }

export const useAnalysisTemplates = () => {
  const dispatch = useDispatch();
  const { analysisTemplates, loadedAnalysisTemplate } = useSelector(analysisSelector);

  useEffect(() => {
    if (dispatch) {
      dispatch(getAnalysisTemplates(['protocolArgs']))
    }
  }, [dispatch]);

  const getTemplate = useCallback((id) => {
    dispatch(getAnalysisTemplate(id));
  }, [dispatch]);

  const clearTemplate = useCallback(() => {
    dispatch(clearLoadedAnalysisTemplate(null));
  }, [dispatch]);

  const deleteTemplate = useCallback((id) => {
    dispatch(deleteAnalysisTemplate(id));
  }, [dispatch]);

  return { analysisTemplates, deleteTemplate, getTemplate, loadedTemplate: loadedAnalysisTemplate, clearTemplate };
}

