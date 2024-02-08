
import { createAsyncThunk } from "@reduxjs/toolkit";
import { setDefaultReader } from "../features/reader/readerSlice";
import * as client from './../api/client';

export const getDefaultReader = createAsyncThunk('resource-api/reader/defaultReader',
    async (_, thunkAPI) => {
        try {
            const readers = await client.getReaders();
            thunkAPI.dispatch(setDefaultReader({readers}));
        } catch (e) {
            console.error(e);
        }
    }
);
