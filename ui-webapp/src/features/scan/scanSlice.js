import { createSlice } from "@reduxjs/toolkit";
/**
 * @typedef {import('./scanSlice.types').ScanState} ScanState
 * @type {ScanState}
 */
const initialState = {
  name: "",
  notes: "",
  product: { id: null },
  selectedWells: null,
  scan: {
    isStopped: true,
    isRunning: false,
    isComplete: false,
    totalTime: 0,
    runningTime: 0,
    isError: false,
    error: null,
  },
  lastSavedScan: {},
  lastScanUpdate: null,
  plateWells: [],
  scans: [],
  lastCalibrateUpdate: null,
  images: null,
  downloadFileUrl: null,
};

export const scanSlice = createSlice({
  name: "scan",
  initialState,
  reducers: {
    setImages: (state, { payload }) => {
      state.images = payload;
    },
    setDownloadFileUrl: (state, { payload }) => {
      state.downloadFileUrl = payload;
    },
    setScans: (state, { payload }) => {
      state.scans = payload;
    },
    setLastScanUpdate: (state, { payload }) => {
      state.lastScanUpdate = payload;
    },
    setLastCalibrateUpdate: (state, { payload }) => {
      state.lastCalibrateUpdate = payload;
    },
    setLastSavedScan: (state, { payload }) => {
      state.lastSavedScan = payload;
    },
    clearLastSavedScan: (state, { payload }) => {
      state.lastSavedScan = null;
    },
    setNameNotes: (state, action) => {
      state.name = action.payload.name;
      state.notes = action.payload.notes;
    },
    setProduct: (state, action) => {
      state.product = action.payload.product;
    },
    setWells: (state, action) => {
      state.plateWells = action.payload;
    },
    setSelectedWells: (state, action) => {
      state.selectedWells = action.payload;
    },
    start: (state, action) => {
      state.scan.isStopped = false;
      state.scan.isRunning = true;
      state.scan.isComplete = false;
      state.scan.totalTime = action.payload.totalTime;
    },
    tick: (state) => {
      state.scan.runningTime += 1000;
    },
    stop: (state) => {
      // TODO: How do you abort a scan?
      state.scan.isStopped = true;
      state.scan.isRunning = false;
      state.scan.isComplete = false;
    },
    complete: (state) => {
      state.scan.isComplete = true;
      state.scan.isRunning = false;
    },
    error: (state, action) => {
      state.scan.isError = true;
      state.scan.error = action.payload;
    },
    reset: (state) => {
      state.name = "";
      state.notes = "";
      state.product = { id: null };
      state.selectedWells = null;
      state.scan = {
        isStopped: true,
        isRunning: false,
        isComplete: false,
        totalTime: 0,
        runningTime: 0,
        isError: false,
        error: null,
      };
      state.setLastScanUpdate = null;
      state.setLastSavedScan = null;
      state.scans = null;
      state.analyzeScanWorkflow = {};
      state.lastCalibrateUpdate = null;
    },
    scanDeleted: (state, action) => {
      state.scans = state.scans.filter((scan) => scan._id !== action.payload);
    },
  },
});

export const scanSelector = (state) => state.scan;

// Action creators are generated for each case reducer function
export const {
  setLastScanUpdate,
  setLastSavedScan,
  setLastCalibrateUpdate,
  setNameNotes,
  setProduct,
  setWells,
  setSelectedWells,
  start,
  stop,
  complete,
  tick,
  error,
  reset,
  setScans,
  clearLastSavedScan,
  scanDeleted,
  setDownloadFileUrl,
  setImages,
} = scanSlice.actions;

export default scanSlice.reducer;
