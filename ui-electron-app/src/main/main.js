import {
  app,
  BrowserWindow,
  ipcMain,
  session,
  dialog
} from 'electron';
import path from 'path';
import os from 'os';
import fetch from 'electron-fetch';
import * as fs from 'fs';

import CalibrationData from '../data-ui/calibration.js';

const isDev = app.isPackaged === false; // set isDev flag

const apiUrl = isDev ? 'http://localhost:9000' : '';
// const { remote } = electron.remote;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) { // eslint-disable-line global-require
  app.quit();
}

// load react-devtools
// on macOS
const reactDevToolsPath = path.join(
  os.homedir(),
  '/Library/Application Support/Google/Chrome/Default/Extensions/fmkadmapgofadopljbjfkapdkoienihi/4.24.6_1'
);
const reduxDevToolsPath = path.join(
  os.homedir(),
  '/Library/Application Support/Google/Chrome/Default/Extensions/lmhkpmbekcpmknklioeibfkpmmfibljd/3.0.11_0'
);

app.whenReady().then(async () => {
  await session.defaultSession.loadExtension(reactDevToolsPath);
  await session.defaultSession.loadExtension(reduxDevToolsPath);
});

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    title: 'Empower Reader',
    width: 1440,
    height: 1000,
    minWidth: 1440,
    backgroundColor: '#f1f3f5',
    show: false,
    webPreferences: {
      allowRunningInsecureContent: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // mainWindow.webContents.setZoomFactor(3.0);
  // mainWindow.webContents.setZoomLevel(10);

  // mainWindow.setzoomfactor(2.0);

  // ignore cors entirely
  mainWindow.webContents.session.webRequest.onBeforeSendHeaders(
    (details, callback) => {
      callback({
        requestHeaders: {
          Origin: '*',
          "Access-Control-Allow-Headers": "Content-Type",
          ...details.requestHeaders
        }
      });
    },
  );

  mainWindow.webContents.session.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        'Access-Control-Allow-Origin': ['*'],
        'Access-Control-Allow-Headers': ['*'],
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        ...details.responseHeaders,
      },
    });
  });

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.maximize();
    mainWindow.focus();
    mainWindow.webContents.setZoomFactor(1.2);
  });

  // documentation windows
  ipcMain.on('pop-window', (event, url) => { // on `pop-window` event from the renderer process
    const child = new BrowserWindow({
      parent: mainWindow,
      modal: false,
      title: `Empower Reader - ${url}`,
      width: 1000,
      height: 800
    });
    console.log('pop-window', url);

    child.loadURL(url);
    child.once('ready-to-show', () => { child.show(); });
  });

  // get a scan from api
  ipcMain.on('get-scan', (event) => { // on `pop-window` event from the renderer process
    let scan;
    fetch(
      'http://localhost:5984/reader/_design/design-doc/_view/scans?key="reader123"',
      {
        headers: {
          Authorization: `Basic ${btoa('admin:password')}`
        }
      }
    )
      .then((response) => response.json())
      .then((data) => scan = data)
      .then(() => event.reply('scan', scan));
  });

  // same as above but for data from the API
  ipcMain.on('get-scans-list', (event) => { // on `pop-window` event from the renderer process
    let scansList;
    fetch(
      'http://fargatealb-150082972.us-east-2.elb.amazonaws.com:5984/reader/_design/design-doc/_view/scans', // TODO: may need to append the reader `?key="reader123"`
      {
        headers: {
          Authorization: `Basic ${btoa('readeradmin:topsecret')}`
        }
      }
    )
      .then((response) => response.json())
      .then((data) => scansList = data)
      .then(() => event.reply('scans-list', scansList));
  });

  // and load the index.html of the app.
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY); // eslint-disable-line no-undef

  // Open the DevTools.
  if (isDev) { mainWindow.webContents.openDevTools(); }
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.

// TODO: update this to interact (fetch data) with real API to get calibration data once it's ready
// handle load-calibration event and return calibration data
ipcMain.handle('load-calibration', async () => {
  const result = await CalibrationData.lastCalibrationDate;
  return result;
});

// same as above but for data from the API
ipcMain.on('get-products-list', (event) => { // on `pop-window` event from the renderer process
  let productsList;
  fetch(
    'http://fargatealb-150082972.us-east-2.elb.amazonaws.com:5984/reader/_design/design-doc/_view/configs-by-entity-id-and-name?key=["reader123","productList"]',
    {
      headers: {
        Authorization: `Basic ${btoa('readeradmin:topsecret')}`
      }
    }
  )
    .then((response) => response.json())
    .then((data) => productsList = data)
    .then(() => event.reply('products-list', productsList));
});

// call saveContent function when 'save-data' message is received from renderer
ipcMain.on('export-data', (event, content) => {
  let date = new Date().toISOString();
  date = date.replace(/([: / .])/g, '-'); // for some reason when exporting these files the ':' were being replaced with '/' in the file name so just sanitizing a bit so we don'thave to escape anything later on

  dialog.showSaveDialog({
    title: 'Export your data',
    defaultPath: `${app.getPath('documents')}/analysis-template-${date}.json`,
    buttonLabel: 'Export',
    // Restricting the user to only JSON Files.
    filters: [
      {
        name: 'JSON Files',
        extensions: ['json']
      }
    ]
  }).then((file) => {
    if (!file.canceled) {
      fs.writeFile(file.filePath, JSON.stringify(content), 'utf8', (err) => {
        if (err) {
          throw err;
        }
        console.log('exported');
      });
    }
  });
});

// file uploads
ipcMain.on('import-data', (event, content) => {
  dialog.showOpenDialog({
    title: 'Import your JSON data',
    defaultPath: app.getPath('documents'),
    buttonLabel: 'Import',
    // Restricting the user to only JSON Files.
    filters: [
      {
        name: 'JSON Files',
        extensions: ['json']
      }
    ]
  }).then((file) => {
    console.log('file', file);
    // TODO: grab the file then send json contents to API / Database via fetch
    // if (!file.canceled) {
    //   fs.writeFile(file.filePath, JSON.stringify(content), 'utf8', (err) => {
    //     if (err) {
    //       throw err;
    //     }
    //     console.log('exported');
    //   });
    // }
    if (file.canceled === true) {
      event.reply('import-data-complete', { status: 'CANCELED', message: 'canceled' });
    } else {
      event.reply('import-data-complete', { status: 'OK', message: 'success' });
    }
  })
    .catch((err) => event.reply('import-data-complete', { status: 'ERROR', message: err }));
});
