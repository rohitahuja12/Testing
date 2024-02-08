/**
 * @typedef {{
 * name: string,
 * notes: string,
 * product: {id: string | null},
 * selectedWells: Array<Object> | null,
 * scan: {
 * isStopped: boolean,
 * isRunning: boolean,
 * isComplete: boolean,
 * totalTime: number,
 * runningTime: number,
 * isError: boolean,
 * error: string | null
 * },
 * lastScanUpdate: Object | null,
 * lastSavedScan: Object | null,
 * plateWells: Array<Object>,
 * scans: Array<Object> | null,
 * lastCalibrateUpdate: Object | null,
 * }} ScanState
 */

export const unused = {}; // dummy export to avoid DCE