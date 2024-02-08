import { configureStore } from '@reduxjs/toolkit';
import scanReducer from './features/scan/scanSlice.js';
import analysisReducer from './features/analysis/analysisSlice.js';
import flowReducer from './features/flow/flowSlice.js';
import systemReducer from './features/system/systemSlice.js';
import productReducer from './features/product/productSlice.js';
import readerReducer from './features/reader/readerSlice.js';

export const store = configureStore({
  reducer: {
    system: systemReducer,
    analysis: analysisReducer,
    scan: scanReducer,
    product: productReducer,
    flow: flowReducer,
    reader: readerReducer
  }
});

export const setupMockStore = (preloadedState) => {
  return configureStore({
    reducer: {
      system: systemReducer,
      analysis: analysisReducer,
      scan: scanReducer,
      product: productReducer,
      flow: flowReducer
    },
    preloadedState
  })
}