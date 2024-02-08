import { createAsyncThunk } from "@reduxjs/toolkit";
import * as client from "./../api/client";
import { showSnackbar } from "../features/system/systemSlice";

export const saveNewUser = createAsyncThunk(
  "auth/organization/user",
  async (newUser, thunkAPI) => {
    try {
      const response = await client.createUser(newUser);
      if (response.toLowerCase().includes("created.")) {
        thunkAPI.dispatch(
          showSnackbar({
            message: "User created",
            severity: "success",
          })
        );
      } else {
        throw new Error("User Creation failed");
      }
    } catch (e) {
      thunkAPI.dispatch(
        showSnackbar({
          message: "User creation failed",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);
