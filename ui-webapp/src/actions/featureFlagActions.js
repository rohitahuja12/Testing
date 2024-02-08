import { createAsyncThunk } from "@reduxjs/toolkit";
import * as client from "./../api/client";
import { setFeatureFlags } from "../features/system/systemSlice";
import { getAccessToken } from "./authenticationHelper";

export const getDefaultFeatureFlags = createAsyncThunk(
  "resource-api/reader/defaultReader",
  async (_, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const featureFlagSets = await client.getFeatureFlagSets(accessToken);
      if (!featureFlagSets) {
        throw new Error("Cannot load feature flag sets.");
      }
      const defaultSet = featureFlagSets.find((set) => set.isDefault === true);
      thunkAPI.dispatch(setFeatureFlags(defaultSet.features));
    } catch (e) {
      console.error(e);
    }
  }
);

/**
 *
 * @param {string} featureFlag
 * @param {[{ feature: string, enabled: boolean }]} featureFlags
 */
export const isFeatureFlagEnabled = (featureFlag, featureFlags) => {
  const flag = featureFlags.find((flag) => flag.feature === featureFlag);
  // console.debug(
  //   `Feature flag ${featureFlag} is ${flag?.enabled ? "enabled" : "disabled"}`
  // );
  return flag?.enabled;
};
