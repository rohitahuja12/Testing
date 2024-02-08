import { createSlice } from '@reduxjs/toolkit';
/**
 * @type {import('./readerSlice.types.js').ReaderState}
 */
const initialState = {
  serialNumber: '3',
  readers: []
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
        state.readers = readers;
      }
    }
  }
});

export const readerSelector = state => state.reader;

// Action creators are generated for each case reducer function
export const { setDefaultReader } = flowSlice.actions;

export default flowSlice.reducer;
