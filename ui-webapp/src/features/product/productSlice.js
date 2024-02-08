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
export const productSelector = state => {
    /**
     * If no calibration product is set and there are products available, find and set the calibration product
     */

    if (!state.product.calibrationProductId && state.product.products.length > 0) {
        const calibrationProduct = state.product.products.find(product => product?.productId?.toLowerCase().includes('calibration'));
        if (calibrationProduct) {
            state.product.calibrationProductId = calibrationProduct._id;
        }
    }
    return state.product;
};

// Action creators are generated for each case reducer function
export const {
    setProduct,
    setProducts,
    setCalibrationProductId
} = productSlice.actions;

export default productSlice.reducer;
