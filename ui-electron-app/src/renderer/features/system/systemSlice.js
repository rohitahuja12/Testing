import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  lastCalibrationDate: null,
  readerDoorStatus: ''
};

export const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    setCalibrationStatus: (state, action) => {
      state.lastCalibrationDate = action.payload;
    },
    setReaderDoorStatus: (state, action) => {
      state.readerDoorStatus = action.payload;
    }
  }
});

// Action creators are generated for each case reducer function
export const {
  setCalibrationStatus,
  setReaderDoorStatus
} = systemSlice.actions;

export default systemSlice.reducer;
