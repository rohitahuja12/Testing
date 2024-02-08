import { createSlice } from "@reduxjs/toolkit";

/**
 * @typedef {import('./analysisSlice.types').AnalysisState} AnalysisState
 * @type {AnalysisState}
 */
const initialState = {
  id: "",
  name: "",
  notes: "",
  date: "",
  product: { id: null },
  selectedWells: null,
  analysisTemplates: [],
  lastAnalysisUpdate: null,
  lastSavedAnalysis: null,
  analyses: [],
  loadedAnalysis: null,
  analysisImages: null,
  downloadFileUrl: null,
  loadedAnalysisTemplate: null,
  savedAnalysisTemplate: null,
};

export const analysisSlice = createSlice({
  name: "analysis",
  initialState,
  reducers: {
    // Redux Toolkit allows us to write "mutating" logic in reducers. It
    // doesn't actually mutate the state because it uses the Immer library,
    // which detects changes to a "draft state" and produces a brand new
    // immutable state based off those changes
    setSavedAnalysisStatus: (state, action) => {
      state.saved = action.payload;
    },
    setLastSavedAnalysis: (state, action) => {
      state.lastSavedAnalysis = action.payload;
    },
    clearLastSavedAnalysis: (state) => {
      state.lastSavedAnalysis = null;
    },
    setNameNotes: (state, action) => {
      state.name = action.payload.name;
      state.notes = action.payload.notes;
    },
    setSelectedTemplate: (state, action) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
      state.notes = action.payload.notes;
      state.date = action.payload.date;
      state.product = action.payload.product;
      state.selectedWells = action.payload.selectedWells;
    },
    setProduct: (state, action) => {
      state.product = action.payload.product;
    },
    setSelectedWells: (state, action) => {
      state.selectedWells = action.payload;
    },
    error: (state, action) => {
      state.scan.isError = true;
      state.scan.error = action.payload;
    },
    reset: (state) => {
      state.id = "";
      state.name = "";
      state.notes = "";
      state.date = "";
      state.product = { id: null };
      state.selectedWells = null;
      state.templatedWells = null;
      state.savedAnalysisStatus = null;
      state.savedAnalysisTemplate = null;
      state.lastAnalysisUpdate = null; // not sure if this is needed, but it may prevent issues
      state.lastSavedAnalysis = null;
      state.analysisImages = null;
      state.analyses = null;
      state.analysisTemplates = null;
      state.loadedAnalysisTemplate = null;
      state.downloadFileUrl = null;
    },
    analysisTemplateDeleted: (state, action) => {
      const id = action.payload;
      state.analysisTemplates = state.analysisTemplates.filter(
        (template) => template?.id !== id && template?._id !== id
      );
    },
    analysisDeleted: (state, action) => {
      const id = action.payload;
      state.analyses = state.analyses.filter(
        (analysis) => analysis?.id !== id && analysis?._id !== id
      );
    },
    setAnalysisTemplates: (state, action) => {
      state.analysisTemplates = action.payload;
    },
    setDefaultPlateMaps: (state, action) => {
      state.defaultPlateMaps = action.payload;
    },
    setTemplateConcentrations: (state, { payload }) => {
      state.templateConcentrations = payload;
    },
    setTemplateStandardDilution: (state, { payload }) => {
      state.templateStandardDilution = payload;
    },
    setTemplatedWells: (state, { payload }) => {
      state.templatedWells = payload;
    },
    setSavedAnalysisTemplate: (state, { payload }) => {
      // used to set the saved analysis template.
      // this is useful in the SCAN_TO_ANALYSIS flow
      // where the user creates an analysis template, it is saved
      // then used to create a new analysis
      state.savedAnalysisTemplate = payload;
    },
    setLastAnalysisUpdate: (state, { payload }) => {
      state.lastAnalysisUpdate = payload;
    },
    setAnalysisImages: (state, { payload }) => {
      // used by:
      // - single analysis resutls page
      // - view results page
      state.analysisImages = payload;
    },
    setDownloadFileUrl: (state, { payload }) => {
      // used by:
      // - view results page
      state.downloadFileUrl = payload;
    },
    clearAnalysisImages: (state) => {
      if (state.analysisImages) {
        state.analysisImages.forEach((image) => {
          URL.revokeObjectURL(image);
        });
        state.analysisImages = null;
      }
    },
    setAnalyses: (state, { payload }) => {
      // specific to view results page
      state.analyses = payload;
    },
    setLoadedAnalysis: (state, { payload }) => {
      // specific to view results page
      state.loadedAnalysis = payload;
    },
    setLoadedAnalysisTemplate: (state, { payload }) => {
      // specific to view results page
      state.loadedAnalysisTemplate = payload;
    },
    clearLoadedAnalysisTemplate: (state) => {
      state.loadedAnalysisTemplate = null;
    },
  },
});

// reducers
export const analysisSelector = (state) => state.analysis;
export const lastSavedAnalysisTemplateSelector = (state) =>
  state.analysis.savedAnalysisTemplate;
export const defaultPlateMapsSelector = (state) =>
  state.analysis.defaultPlateMaps;

// Action creators are generated for each case reducer function
export const {
  setLoadedAnalysisTemplate,
  clearLoadedAnalysisTemplate,
  setNameNotes,
  setProduct,
  setSelectedWells,
  setSelectedTemplate,
  error,
  reset,
  setAnalysisTemplates,
  setDefaultPlateMaps,
  setTemplateConcentrations,
  setTemplateStandardDilution,
  setTemplatedWells,
  setSavedAnalysisStatus,
  setSavedAnalysisTemplate,
  setLastAnalysisUpdate,
  setLastSavedAnalysis,
  clearLastSavedAnalysis,
  setAnalysisImages,
  clearAnalysisImages,
  setAnalyses,
  setLoadedAnalysis,
  analysisTemplateDeleted,
  setDownloadFileUrl,
  analysisDeleted,
} = analysisSlice.actions;

export default analysisSlice.reducer;
