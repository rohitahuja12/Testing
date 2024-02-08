/**
 * @typedef {{
 * id: string,
 * name: string,
 * notes: string,
 * date: string,
 * product: {id: string},
 * selectedWells: Array<string> | null,
 * analysisTemplates: Array<Object> | null,
 * lastAnalysisUpdate: Object | null,
 * lastSavedAnalysis: Object | null,
 * analyses: Array<Object> | null,
 * loadedAnalysis: Object | null,
 * analysisImages: Array<Object> | null,
 * downloadFileUrl: string | null,
 * loadedAnalysisTemplate: Object | null,
 * savedAnalysisStatus: string | null,
 * }} AnalysisState
 */

export const unused = {}; // dummy export to avoid DCE