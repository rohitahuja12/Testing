import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    product: {},
    products: [],
    calibrationProductId: null
};

export const productSlice = createSlice({
    name: 'product',
    initialState,
    reducers: {
        setProduct: (state, action) => {
            state.product = { ...action.payload };
        },
        setProducts: (state, { payload }) => {
            state.products = payload;
        },
        setCalibrationProductId: (state, { payload }) => {
            state.calibrationProductId = payload;
        }
    }
});


//selectors
export const productSelector = state => state.product;

// Action creators are generated for each case reducer function
export const {
    setProduct,
    setProducts,
    setCalibrationProductId
} = productSlice.actions;

export default productSlice.reducer;
