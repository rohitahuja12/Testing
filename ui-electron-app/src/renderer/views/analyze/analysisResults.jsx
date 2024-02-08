import React, { useState, useEffect } from 'react';
import {
  createStyles,
  Text,
  Button,
  ScrollArea,
  Paper,
  Alert,
  Box,
  Grid,
  Image
} from '@mantine/core';
import { AlertCircle } from 'tabler-icons-react';
import { useTheme } from '@table-library/react-table-library/theme';
import {
  DEFAULT_OPTIONS,
  getTheme
} from '@table-library/react-table-library/mantine';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { scanSelector } from '../../features/scan/scanSlice.js';
import { getAttachments } from '../../actions/analysisTemplateActions.js';
import { getScan } from '../../actions/scanActions.js';
import { BBLoader } from '../../components/brightestBio/BBLoader.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

// # Analysis Results Page

const useStyles = createStyles(useAppStyles);

export default function AnalysisResults({ ...props }) {
  const [showAlert, setShowAlert] = useState(false);
  const navigate = useNavigate();
  const { lastAnalysisUpdate, lastSavedAnalysis, analysisImages } = useSelector(state => state?.analysis);
  const { lastSavedScan } = useSelector(scanSelector);
  const { classes, cx } = useStyles();
  const mantineTheme = getTheme(DEFAULT_OPTIONS);
  const theme = useTheme(mantineTheme);
  const dispatch = useDispatch();

  useEffect(() => {

    // The pre-complete analysis object
    console.log('lastSavedAnalysis', lastSavedAnalysis);
    // On thte final websocket message for a given analysis,
    // this is the analysis object with the final results
    console.log('lastAnalysisUpdate', lastAnalysisUpdate);
    // The scan within the last saved analysis is retrieved in a useeffect below
    // This is the scan object related to this analysis
    console.log('lastSavedScan', lastSavedScan);

    if (lastSavedAnalysis && lastAnalysisUpdate) {
      dispatch(getScan(lastSavedAnalysis?.scanId));
      const id = lastSavedAnalysis?._id || lastSavedScan?.id;
      if (id) {
        dispatch(getAttachments(id));
      }

    }
  }, [lastAnalysisUpdate, lastSavedAnalysis]);

  const analysisIsComplete = (status) => status === 'COMPLETE';
  const analysisProcessingFailed = (status) => status === 'ERROR';
  const analysisIsRunningOrQueued = (status) => status === 'RUNNING' || status === 'QUEUED';

  const renderAnalysisImagesGridOrStatusDescription = () => {
    // analysis status states
    // "QUEUED",
    // "RUNNING",
    // "COMPLETE",
    // "ERROR"
    if (analysisImages && analysisImages?.length > 0) {
      return (<Grid>
        {analysisImages.map((image, index) => {
          return (<Grid.Col span={4} key={`img-${index}`}>
            <div style={{ width: 240, marginLeft: 'auto', marginRight: 'auto' }}>
              <Image
                key={index}
                radius="md"
                src={image}
                alt={`Analysis-Image-${index}`}
              />
            </div>
          </Grid.Col>);
        })}
      </Grid>)
    } else if (analysisIsRunningOrQueued(lastAnalysisUpdate?.status)) {
      console.log('analysis is running or queued, show loader', lastAnalysisUpdate?.status);
      return (<div style={{ textAlign: 'center' }}>
        <BBLoader size='md' />
        <Text>
          Analysis in progress.
        </Text>
      </div>)
    } else if (analysisProcessingFailed(lastAnalysisUpdate?.status)) {
      console.log('analysis failed, showing error', lastAnalysisUpdate?.status);

      return (<div style={{ textAlign: 'center' }}>
        <Alert
          title="Analysis Processing Failed"
          icon={<AlertCircle />}
          color="red"
        >
          The Analysis Processing Failed. Please try again.
        </Alert>
        <Text>
          The Analysis Processing Failed. Please try again.
        </Text>
      </div>)
    } else {
      return (<div style={{ textAlign: 'center' }}>
        <Text className={classes.text}>
          This analysis does not exist. Please return to the dashboard.
        </Text>
      </div>)
    }
  }

  /**
   * 
   * @param {*} span 
   * @param {*} titleSize 
   * @param {*} title 
   * @param {*} value 
   * @param {*} defaultValue 
   * @returns <Grid.Col /> outlining the title and value
   */
  const renderGridSection = (span, titleSize, title, value, defaultValue) => (
    <Grid.Col span={span}>
      <Text className={classes.title} size={titleSize || 'md'}>
        {title}
      </Text>
      <Text className={classes.text}>
        {value || defaultValue || ''}
      </Text>
    </Grid.Col>
  )

  return (
    <>
      <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
        <Button
          type="button"
          color="dark"
          onClick={() => { navigate('/') }}
        >
          Dashboard
        </Button>
      </AppShellHeader>

      <div className={classes.appBackground}>
        <Box className={classes.tableBox}>
          {showAlert && (
            <Alert icon={<AlertCircle size={16} />} title="ERROR" color="red" withCloseButton onClose={() => setShowAlert(false)} mb={25}>
              Your analysis template does not match your scan. Please make the appropriate selection to run analysis.
            </Alert>
          )}

          {/* scan details */}
          <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
            <Grid sx={{}}>
              {renderGridSection(12, 'lg', 'Scan Details')}
              {renderGridSection(6, 'md', 'Scan Name', lastSavedScan?.name, 'Scan Name')}
              {renderGridSection(6, 'md', 'Product Name', lastSavedScan?.productId, 'Scan Product Name')}
              {renderGridSection(12, 'md', 'Scan Notes', lastSavedScan?.notes, '')}
            </Grid>
          </Paper>

          <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
            <Grid sx={{}}>
              {renderGridSection(12, 'lg', 'Analysis Template Details')}
              {renderGridSection(6, 'md', 'Analysis Template', lastSavedAnalysis?.name, 'Scan Name')}
              {renderGridSection(6, 'md', 'Product Name', lastSavedAnalysis?.productName, 'Product Name')}
              {renderGridSection(12, 'md', 'Analysis Template Notes', lastSavedAnalysis?.notes, 'Analysis Template notes')}
            </Grid>
          </Paper>

          <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
            <Grid sx={{ marginBottom: 30, marginLeft: 35 }} justify="space-between" align="flex-start">
              <Grid.Col span={9}>
                <Text weight={700}>{lastSavedAnalysis?.name || "last saved analysis name"}</Text>
              </Grid.Col>
              <Grid.Col span={3}>
                <Button type="button" radius="xl" className={classes.actionButton} onClick={() => { console.log('Download images') }}>
                  Download Analysis
                </Button>
              </Grid.Col>
            </Grid>
            {renderAnalysisImagesGridOrStatusDescription()}
          </Paper>
        </Box>
      </div >
    </>
  );
}
