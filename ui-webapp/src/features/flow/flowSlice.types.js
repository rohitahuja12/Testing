/**
 * @typedef {{
 * NONE: 'NONE',
 * SCAN: 'SCAN',
 * ANALYZE: 'ANALYZE',
 * SCAN_TO_ANALYSIS: 'SCAN_TO_ANALYSIS',
 * MANAGE_ANALYSIS_TEMPLATES: 'MANAGE_ANALYSIS_TEMPLATES',
 * VIEW_RESULTS: 'VIEW_RESULTS',
 * }} FlowTypes
 * 
 * @typedef {'NONE' | 'SCAN' | 'ANALYZE' | 'SCAN_TO_ANALYSIS' | 'MANAGE_ANALYSIS_TEMPLATES' | 'VIEW_RESULTS'} FlowType
 * 
 * @typedef {{
 * type: FlowType,
 * }} FlowState
 */

export const unused = {}; // dummy export to avoid DCE