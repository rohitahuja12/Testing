import { createAsyncThunk } from "@reduxjs/toolkit";
import {
  setLastSavedScan,
  setScans,
  scanDeleted,
  setImages,
  setDownloadFileUrl,
} from "../features/scan/scanSlice";
import { showSnackbar } from "../features/system/systemSlice";
import { getRegionsBySelectedWells } from "../utils/plateRegionUtils";
import * as client from "./../api/client";
import { setLoadingData } from "../features/system/systemSlice";
import { getAccessToken } from "./authenticationHelper";
import { blobToDataURL } from "../utils/fileUtils";

/**
 *
 * @param {{ row: string, column: string }} wells
 */
const get2DPlateFromWells = (wells) =>
  [...new Set(wells.map((well) => well.row))] // ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    .map((rowLetter, yIndex) =>
      wells
        .filter((well) => well.row === rowLetter)
        .map((well, xIndex) => ({ ...well, x: xIndex, y: yIndex }))
    ); // [[row], [row]]

export const saveCalibration = createAsyncThunk(
  "resource-api/scan/calibration",
  async (calibration, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const response = await client.postScan(calibration, accessToken);
      thunkAPI.dispatch(
        showSnackbar({
          message: "Calibration created",
          severity: "success",
        })
      );
    } catch (e) {
      thunkAPI.dispatch(
        showSnackbar({
          message: "Calibration failed",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);

export const saveScan = createAsyncThunk(
  "resource-api/scan",
  async (scanData, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const state = thunkAPI.getState();
      const { scan } = state;

      const regions = getRegionsBySelectedWells(scan.selectedWells);
      const savedScan = await client.postScan(
        {
          ...scanData,
          protocolArgs: {
            images: regions,
          },
        },
        accessToken
      );
      thunkAPI.dispatch(setLastSavedScan(savedScan));
    } catch (e) {
      console.error(e);
    }
  }
);

export const saveScanWithWells = createAsyncThunk(
  "resource-api/scan",
  async (scan, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const regions = getRegionsBySelectedWells(scan.selectedWells);
      const savedScan = await client.postScan(
        {
          ...scan,
          status: "NOT_QUEUED", // phx 229
          protocolArgs: {
            images: regions,
          },
          protocol: "pArray",
        },
        accessToken
      );
      thunkAPI.dispatch(setLastSavedScan(savedScan));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Scan created",
          severity: "success",
        })
      );
    } catch (e) {
      thunkAPI.dispatch(
        showSnackbar({
          message: "Scan creation failed",
          severity: "error",
        })
      );
      thunkAPI.dispatch(setLastSavedScan({ error: true }));
      console.error(e);
    }
  }
);

export const deleteScan = createAsyncThunk(
  "resource-api/scan",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const response = await client.deleteScan(id, accessToken);
      if (response.toString().toLowerCase() === "deleted") {
        thunkAPI.dispatch(scanDeleted(id));
        thunkAPI.dispatch(
          showSnackbar({
            message: "Scan deleted",
            severity: "success",
          })
        );
      } else {
        thunkAPI.dispatch(
          showSnackbar({
            message: "Failed to delete scan",
            severity: "error",
          })
        );
      }
    } catch (e) {
      console.error(e);
    }
  }
);

export const getScans = createAsyncThunk(
  "resource-api/scan",
  async (args, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const scans = await client.getScans(null, accessToken);
      thunkAPI.dispatch(setScans(scans));
    } catch (e) {
      console.error(e);
    }
  }
);

export const getScansWithoutWellData = createAsyncThunk(
  "resource-api/scan",
  async (args, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      thunkAPI.dispatch(setLoadingData(true));
      const scans = await client.getScans(["protocolArgs"], accessToken);
      thunkAPI.dispatch(setScans(scans));
      thunkAPI.dispatch(setLoadingData(false));
    } catch (e) {
      // handle loading error
      thunkAPI.dispatch(setLoadingData(false));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Cannot load scans. Try again later.",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);

export const getScan = createAsyncThunk(
  "resource-api/scan",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const scan = await client.getScan(id, accessToken);
      thunkAPI.dispatch(setLastSavedScan(scan));
    } catch (e) {
      console.error(e);
    }
  }
);

export const getScanImages = createAsyncThunk(
  "resource-api/scan",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const attachments = await client.getScanAttachments(id, accessToken);
      const downloadFileName = attachments.find(
        (attachment) => attachment.filename.includes("results") // results doesn't have a .zip extension, so let's use the name
      )?.filename;

      if (attachments.length === 0)  {
        thunkAPI.dispatch(setImages([]));
        return;
      }

      const downloadFileBlob = await client.getScanAttachmentByName(
        id,
        downloadFileName,
        accessToken
      );
      const downloadFileUrl = await blobToDataURL(downloadFileBlob);

      thunkAPI.dispatch(setDownloadFileUrl(downloadFileUrl));
    } catch (e) {
      console.error(e);
    }
  }
);
