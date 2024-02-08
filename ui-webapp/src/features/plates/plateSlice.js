import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    plates: [],
};

export const plateSlice = createSlice({
    name: 'plate',
    initialState,
    reducers: {
        setPlates: (state, action) => {
            state.plates = action.payload;
        },
    }
});


//selectors
export const plateSelector = state => {
    /**
     * If no calibration product is set and there are products available, find and set the calibration product
     */
    return state.plate.plates;
};

// Action creators are generated for each case reducer function
export const {
    setPlates
} = plateSlice.actions;

export default plateSlice.reducer;
