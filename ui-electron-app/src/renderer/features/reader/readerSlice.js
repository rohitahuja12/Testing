import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  serialNumber: ''
};

export const flowSlice = createSlice({
  name: 'reader',
  initialState,
  reducers: {
    /**
     * 
     * @param {*} state 
     * @param {*} action.payload [readers: { serialNumber: string} ]
     */
    setDefaultReader: (state, { payload }) => {
      const readers = payload?.readers;
      if (readers && readers.length > 0) {
        state.serialNumber = readers[0]?.serialNumber;
      }
    }
  }
});

// Action creators are generated for each case reducer function
export const { setDefaultReader } = flowSlice.actions;

export default flowSlice.reducer;
