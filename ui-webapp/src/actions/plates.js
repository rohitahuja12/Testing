import { createAsyncThunk } from "@reduxjs/toolkit";
import * as client from "./../api/client";
import { setPlates } from "../features/plates/plateSlice";
import { getAccessToken } from "./authenticationHelper";

export const getPlates = createAsyncThunk(
  "resource-api/plates",
  async (args, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const plates = await client.getPlates(accessToken);
      thunkAPI.dispatch(setPlates(plates));
    } catch (e) {
      console.error(e);
    }
  }
);
