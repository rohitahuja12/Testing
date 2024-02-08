import { createAsyncThunk } from "@reduxjs/toolkit";
import { setDefaultReader } from "../features/reader/readerSlice";
import * as client from "./../api/client";
import { setLoadingData, showSnackbar } from "../features/system/systemSlice";
import { getAccessToken } from "./authenticationHelper";

export const getDefaultReader = createAsyncThunk(
  "resource-api/reader/defaultReader",
  async (token, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI, token);
      thunkAPI.dispatch(setLoadingData(true));
      const readers = await client.getReaders(accessToken);
      thunkAPI.dispatch(setDefaultReader({ readers }));
      thunkAPI.dispatch(setLoadingData(false));
    } catch (e) {
      thunkAPI.dispatch(setLoadingData(false));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Cannot load readers. Try again later.",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);
