/**
 * @typedef {{
*  lastCalibrationDate: string,
* readerDoorStatus: string,
* snackbar: {
* open: boolean,
* message: string,
* severity: 'success' | 'info' | 'warning' | 'error' | 'unset'
* },
* useMUIStyleSystem: boolean,
* useDarkTheme: boolean,
* loadingData: boolean,
* featureFlags: [{ feature: string, enabled: boolean }]
* }} SystemState
* 
* @typedef {{
* name: string,
* initialState: SystemState,
* reducers: {
* toggleAppTheme: (state: SystemState) => void,
* toggleStyleSystem: (state: SystemState) => void,
* setCalibrationStatus: (state: SystemState, action: {payload: string}) => void,
* setReaderDoorStatus: (state: SystemState, action: {payload: string}) => void,
* showSnackbar: (state: SystemState, action: {payload: {message: string, severity: 'success' | 'info' | 'warning' | 'error' | 'unset'}}) => void,
* hideSnackbar: (state: SystemState) => void,
* setLoadingData: (state: SystemState, action: {payload: boolean}) => void,
* setFeatureFlags: (state: SystemState, action: {payload: [{ feature: string, enabled: boolean }]}) => void,
* }
* }} SystemSlice
*/

export const unused = {}; // dummy export to avoid DCE