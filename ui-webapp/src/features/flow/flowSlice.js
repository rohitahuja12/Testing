import { createSlice } from '@reduxjs/toolkit';

/**
 * @type {import('./flowSlice.types.js').FlowTypes}
 */
export const flowTypes = {
  NONE: 'NONE',
  SCAN: 'SCAN',
  ANALYZE: 'ANALYZE',
  SCAN_TO_ANALYSIS: 'SCAN_TO_ANALYSIS',
  MANAGE_ANALYSIS_TEMPLATES: 'MANAGE_ANALYSIS_TEMPLATES',
  VIEW_RESULTS: 'VIEW_RESULTS',
};

/**
 * @type {import('./flowSlice.types.js').FlowState}
 */
const initialState = {
  type: flowTypes.NONE
};

export const flowSlice = createSlice({
  name: 'flow',
  initialState,
  reducers: {
    // Redux Toolkit allows us to write "mutating" logic in reducers. It
    // doesn't actually mutate the state because it uses the Immer library,
    // which detects changes to a "draft state" and produces a brand new
    // immutable state based off those changes
    setFlowType: (state, action) => {
      state.type = action.payload.type;
    }
  }
});

// Action creators are generated for each case reducer function
export const { setFlowType } = flowSlice.actions;

export default flowSlice.reducer;
