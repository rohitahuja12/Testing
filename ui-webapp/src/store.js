import { configureStore } from "@reduxjs/toolkit";
import scanReducer from "./features/scan/scanSlice.js";
import analysisReducer from "./features/analysis/analysisSlice.js";
import flowReducer from "./features/flow/flowSlice.js";
import systemReducer from "./features/system/systemSlice.js";
import productReducer from "./features/product/productSlice.js";
import readerReducer from "./features/reader/readerSlice.js";
import plateReducer from "./features/plates/plateSlice.js";

export const store = configureStore(
  /**
   * @type {Store}
   */
  {
    reducer: {
      system: systemReducer,
      analysis: analysisReducer,
      scan: scanReducer,
      product: productReducer,
      flow: flowReducer,
      reader: readerReducer,
      plate: plateReducer,
    },
  }
);

export const setupMockStore = (preloadedState) => {
  return configureStore({
    reducer: {
      system: systemReducer,
      analysis: analysisReducer,
      scan: scanReducer,
      product: productReducer,
      flow: flowReducer,
      reader: readerReducer,
      plate: plateReducer,
    },
    preloadedState,
  });
};

/**
 * @typedef {{
 * system: import('./features/system/systemSlice.types.js').SystemState,
 * analysis: import("./features/analysis/analysisSlice.types.js").AnalysisState,
 * scan: import("./features/scan/scanSlice.types.js").ScanState,
 * product: import("./features/product/productSlice.types.js").ProductState,
 * flow: import("./features/flow/flowSlice.types.js").FlowState,
 * reader: import("./features/reader/readerSlice.types.js").ReaderState,
 * plate: import("./features/plates/plateSlice.types.js").PlateState,
 * }} Store
 */
