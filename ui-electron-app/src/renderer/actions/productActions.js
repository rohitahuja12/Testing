
import { createAsyncThunk } from "@reduxjs/toolkit";
import { setProducts, setCalibrationProductId } from "../features/product/productSlice";
import * as client from './../api/client';

export const getUniqueProducts = (products, excludeCalibrationPlates) => products.reduce((acc, product) => {
    const existingProduct = acc.find(p => p.productName === product.productName);
    if (existingProduct) {
        if (existingProduct.createdOn < product.createdOn) {
            acc.splice(acc.indexOf(existingProduct), 1, product);
        }
    } else {
        acc.push(product);
    }
    return acc;
}, [])
    .filter(p => excludeCalibrationPlates && !p.productName.toLowerCase().includes('calibration') || !excludeCalibrationPlates);


export const getProducts = createAsyncThunk('resource-api/product',
    async (args = {}, thunkAPI) => {
        try {
            const { excludeCalibrationPlates = false } = args;
            const products = await client.getProducts(['features']);

            // AC: we should only show one card per unique productName, get the one with the latest createdOn date
            const uniqueProducts = getUniqueProducts(products, excludeCalibrationPlates);
            thunkAPI.dispatch(setProducts(uniqueProducts));

        } catch (e) {
            console.error(e);
        }
    }
);

export const getCalibrationProduct = createAsyncThunk('resource-api/calibrationProduct',
    async (args, thunkAPI) => {
        try {
            const products = await client.getProducts(['features']);
            // todo: change this to use a property on the product instead of the name
            const calibrationProduct = products.find(p => p.productName.toLowerCase().includes('calibration'));
            thunkAPI.dispatch(setCalibrationProductId(calibrationProduct._id));
        } catch (e) {
            console.error(e);
        }
    }
);