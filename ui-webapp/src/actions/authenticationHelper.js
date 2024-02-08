import { showSnackbar } from "../features/system/systemSlice";

export const getAccessToken = (thunkAPI, backupToken = null) => {
  const state = thunkAPI.getState();
  const { system } = state;
  const { token } = system;

  if (token || backupToken) {
    return token || backupToken;
  } else {
    thunkAPI.dispatch(
      showSnackbar({
        message: "Authentication error.",
        severity: "error",
      })
    );
    throw new Error("Authentication error.");
  }
};
