import React from 'react';
import ReactDOM from 'react-dom';
import {
  HashRouter,
  Routes,
  Route
} from 'react-router-dom';
import { MantineProvider, ColorSchemeProvider } from '@mantine/core';
import { Provider } from 'react-redux';
import { store } from './store.js';
import Dashboard from './views/dashboard.jsx';
import Layout from './views/layout.jsx';
import LayoutInit from './views/layoutInit.jsx';
import Calibration from './views/calibration.jsx';
import ScanAndAnalyze from './views/analyze/scanAndAnalyze.jsx';
import SelectAnalysis from './views/analyze/selectAnalysis.jsx';
import KitSelection from './views/scan/kitSelection.jsx';
import empowerTheme from './styles/theme.js';
import SetUpScan from './views/scan/setUpScan.jsx';
import ScanSummary from './views/scan/scanSummary.jsx';
import AnalysisResults from './views/analyze/analysisResults.jsx';
import SetUpAnalysis from './views/analyze/setUpAnalysis.jsx';
import PlateConfig from './views/analyze/plateConfig.jsx';
import WebsocketClient from './components/WebsocketClient.jsx';
import StandardConcentrations from './views/analyze/standardConcentrations.jsx';
import TemplateSummary from './views/analyze/templateSummary.jsx';
import HistoricalResults from './views/analyze/historicalResults.jsx';
import { useHotkeys, useLocalStorage } from '@mantine/hooks';

const root = document.getElementById('app');

const App = () => {
  const [colorScheme, setColorScheme] = useLocalStorage({
    key: 'mantine-color-scheme',
    defaultValue: 'light',
    getInitialValueInEffect: true,
  });

  const toggleColorScheme = (value) =>
    setColorScheme(value || (colorScheme === 'dark' ? 'light' : 'dark'));

  useHotkeys([['mod+J', () => toggleColorScheme()]]);

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleColorScheme}>
      <Provider store={store}>
        <WebsocketClient />
        {console.log('colorScheme', colorScheme)}
        <MantineProvider theme={{ colorScheme, ...empowerTheme}}>
          <HashRouter>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/layoutInit" element={<LayoutInit />} />
              <Route path="/calibration" element={<Calibration />} />

              <Route path="/analyze" element={<Layout />}>
                <Route path="/analyze/analyze-one" element={<ScanAndAnalyze screenTitle="Select Scan + Analysis Template" />} />
                <Route path="/analyze/analyze-two" element={<AnalysisResults screenTitle="Analysis Results" />} />
                <Route path="/analyze/analyze-three" element={<SelectAnalysis screenTitle="Analysis Template Selection" />} />
                <Route path="/analyze/analyze-four" element={<SetUpAnalysis screenTitle="Analysis Template Name & Notes" />} />
                <Route path="/analyze/analyze-five" element={<PlateConfig screenTitle="Set Up Plate Configuration" />} />
              </Route>

              <Route path="/manage-templates" element={<Layout />}>
                <Route path="/manage-templates/analysis-temps-one" element={<SelectAnalysis screenTitle="Manage Analysis Templates" />} />
                <Route path="/manage-templates/analysis-temps-two" element={<KitSelection screenTitle="Select a Product/Kit" />} />
                <Route path="/manage-templates/analysis-temps-three" element={<SetUpAnalysis screenTitle="Analysis Template Name & Notes" />} />
                <Route path="/manage-templates/analysis-temps-four" element={<PlateConfig screenTitle="Set Up Plate Configuration" />} />
                <Route path="/manage-templates/analysis-temps-five" element={<StandardConcentrations screenTitle="Standard Concentrations" />} />
                <Route path="/manage-templates/analysis-temps-six" element={<TemplateSummary screenTitle="Analysis Template Summary" />} />
              </Route>

              <Route path="/scan" element={<Layout />}>
                <Route path="/scan/scan-one" element={<KitSelection screenTitle="Select Product/Kit & Load Plate" />} />
                <Route path="/scan/scan-two" element={<SetUpScan screenTitle="Set Up Scan" />} />
                <Route path="/scan/scan-three" element={<ScanSummary screenTitle="Scan Summary" />} />
              </Route>

              <Route path="/view-results" element={<Layout />}>
                <Route path="/view-results/results-one" element={<HistoricalResults screenTitle="View Results" />} />
              </Route>
            </Routes>
          </HashRouter>
        </MantineProvider>
      </Provider>
    </ColorSchemeProvider>
  )
}

ReactDOM.render(
  <App />
  ,
  root
);
