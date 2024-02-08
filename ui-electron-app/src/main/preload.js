// this preload file is used as a safe intermedate between the main.js file and the renderer process.
const { ipcRenderer, contextBridge } = require('electron');
const { platform } = require('os');

// TODO: I'm using ipcRenderer.send and ipcRenderer.on to communicate between the main process and the renderer process in many of these endpoints.
// however, I may be able to replace some or all of these instances with ipcRenderer.invoke async function as I did for calibration.
// This might reduce the endpoints. currently I have one to send to the main process and one to receive from the main process for many of these.
const API = {
  getScan: () => ipcRenderer.send('get-scan'), // send event to main process to get scan data
  scanContent: (callback) => ipcRenderer.on('scan', (event, data) => callback(data)), // `window.api.scanContent` in the renderer process
  getScanList: () => ipcRenderer.send('get-scans-list'), // send event to main process to get scan list data
  scanListContent: (callback) => ipcRenderer.on('scans-list', (event, data) => callback(data)), // `window.api.scanListContent` in the renderer process
  getProductsList: () => ipcRenderer.send('get-products-list'), // send event to main process to get scan list data
  productsListContent: (callback) => ipcRenderer.on('products-list', (event, data) => callback(data)), // `window.api.scanListContent` in the renderer process
  popWindow: (url) => ipcRenderer.send('pop-window', url), // `window.api.popWindow()` in the main process
  // getCalibration: (callback) => ipcRenderer.on('get-calibration', (event, data) => callback(data)), // send event to main process to get calibration data
  getCalibration: ipcRenderer.invoke('load-calibration'), // event to load calibration data from main process
  exportData: (content) => ipcRenderer.send('export-data', content), // event to export data to main process for saving to files
  importData: () => ipcRenderer.send('import-data'), // event to initiate import data to main process for uploading to the API
  importDataComplete: (callback) => ipcRenderer.on('import-data-complete', (event, data) => callback(data)) // `window.api.importDatacomplete` in the renderer process for status
};

// `contextBridge.exposeInMainWorld` lets us add pieces of our app to the global scope
// so that they can be accessed from the renderer process via a keyword ('api', in this case).
contextBridge.exposeInMainWorld('api', API);
