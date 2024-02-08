# Auragent Empower Reader README

### Overview
-----------------------
_Technologies used:_

- Electron `^17.*.*` - https://www.electronjs.org/docs/latest
- Electron Forge `6.*.*` - https://www.electronforge.io/
- React `^17.0.2` - https://reactjs.org/docs/getting-started.html
- Mantine `^4.*.*` - https://mantine.dev/pages/basics/

### Getting Started
-----------------------
1. Clone repository and change to newly created directory
```
git clone git@gitlab.com:spry-digital/auragent/empower-reader.git
cd empower-reader
```
2. Install needed dependencies
```
npm i
```
3. Start local development
    - This will compile the app and open an application window with dev tools already open.
    - Saves to the React files should hot reload the window, however saving the `main.js` (main process file) or `preload.js` file may require you to stop and restart the application.
```
npm start
```
4. Other possible commands are:
```
npm run package // package your application into a platform specific format and put the result in a folder
npm run make // make distributables for your application based on your Forge config
npm run publish // attempt to make the forge application and then publish it to the publish targets defined in your forge config
npm run lint // lint your application based on eslint config
npm run lint:fix // lint and attempt to fix errors in your appplication based on eslint config
```
