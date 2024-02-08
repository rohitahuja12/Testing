
import { createAsyncThunk } from "@reduxjs/toolkit";
import { setLastSavedScan, setScans, analyzeScan_setScansNoWellData, analyzeScan_setLoadedScan } from "../features/scan/scanSlice";
import { getRegionsBySelectedWells } from "../utils/plateRegionUtils";
import * as client from './../api/client';

/**
 * 
 * @param {{ row: string, column: string }} wells 
 */
const get2DPlateFromWells = (wells) => [...new Set(wells.map(well => well.row))] // ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    .map((rowLetter, yIndex) => wells
        .filter(well => well.row === rowLetter)
        .map((well, xIndex) => ({ ...well, x: xIndex, y: yIndex }))
    ); // [[row], [row]]    

export const saveCalibration = createAsyncThunk('resource-api/scan/calibration',
    async (calibration, thunkAPI) => {
        try {
            const response = await client.postScan(calibration);
        } catch (e) {
            console.error(e);
        }
    }
);

export const saveScan = createAsyncThunk('resource-api/scan',
    async (scanData, thunkAPI) => {
        try {
            const state = thunkAPI.getState();
            const { scan } = state;

            const regions = getRegionsBySelectedWells(scan.selectedWells);
            const savedScan = await client.postScan({
                ...scanData,
                protocolArgs: {
                    images: regions
                }
            });
            thunkAPI.dispatch(setLastSavedScan(savedScan));
        } catch (e) {
            console.error(e);
        }
    }
);

export const getNonCalibrationScansFromScanList = (scans) => scans.filter(scan => scan.protocol.toLowerCase() !== 'calibrate');

export const getScans = createAsyncThunk('resource-api/scan',
    async (args, thunkAPI) => {
        try {
            const scans = await client.getScans();
            const nonCalibrationScans = getNonCalibrationScansFromScanList(scans);
            thunkAPI.dispatch(setScans(nonCalibrationScans));
        } catch (e) {
            console.error(e);
        }
    }
);

export const getScansWithoutWellData = createAsyncThunk('resource-api/scan',
    async (args, thunkAPI) => {
        try {
            const scans = await client.getScans(['protocolArgs']);
            const nonCalibrationScans = getNonCalibrationScansFromScanList(scans);
            thunkAPI.dispatch(setScans(nonCalibrationScans));
        } catch (e) {
            console.error(e);
        }
    }
);

export const getScan = createAsyncThunk('resource-api/scan',
    async (id, thunkAPI) => {
        try {
            const scan = await client.getScan(id);
            thunkAPI.dispatch(setLastSavedScan(scan));
        } catch (e) {
            console.error(e);
        }
    }
);

