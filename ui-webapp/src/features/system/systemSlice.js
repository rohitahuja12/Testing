import { createSlice } from "@reduxjs/toolkit";
/**@typedef {import('./systemSlice.types').SystemState} SystemState */
/** @type {SystemState} */
const initialState = {
  lastCalibrationDate: "",
  readerDoorStatus: "",
  snackbar: {
    open: false,
    message: "",
    severity: "unset", // 'success', 'info', 'warning', 'error', 'unset
  },
  useMUIStyleSystem: true,
  useDarkTheme: !!JSON.parse(localStorage.getItem("useDarkTheme")) || false,
  loadingData: false,
  featureFlags: [],
  featureFlagExpiration: new Date(0).getTime(),
  token: null,
};

export const systemSlice = createSlice(
  /** @type {SystemSlice} */
  {
    name: "system",
    initialState,
    reducers: {
      toggleAppTheme: (state) => {
        state.useDarkTheme = !state.useDarkTheme;
        localStorage.setItem("useDarkTheme", state.useDarkTheme);
      },
      toggleStyleSystem: (state) => {
        state.useMUIStyleSystem = !state.useMUIStyleSystem;
        localStorage.setItem("useMUIStyleSystem", state.useMUIStyleSystem);
      },
      setCalibrationStatus: (state, action) => {
        state.lastCalibrationDate = action.payload;
      },
      setReaderDoorStatus: (state, action) => {
        state.readerDoorStatus = action.payload;
      },
      showSnackbar: (state, action) => {
        state.snackbar.open = true;
        state.snackbar.message = action.payload?.message;
        state.snackbar.severity = action.payload?.severity || "success";
      },
      hideSnackbar: (state) => {
        state.snackbar.open = false;
      },
      setLoadingData: (state, action) => {
        state.loadingData = action.payload;
      },
      setFeatureFlags: (state, action) => {
        state.featureFlags = action.payload;
        state.featureFlagExpiration = new Date(
          Date.now() + 1000 * 60 * 60 * 4
        ).getTime(); // 4 hours from now
      },
      setToken: (state, action) => {
        state.token = action.payload;
      },
    },
  }
);

export const {
  setCalibrationStatus,
  setReaderDoorStatus,
  showSnackbar,
  hideSnackbar,
  toggleStyleSystem,
  toggleAppTheme,
  setLoadingData,
  setFeatureFlags,
  setToken,
} = systemSlice.actions;

export const systemSelector = (state) => state.system;

export default systemSlice.reducer;
