import React, { useState, useCallback, useEffect } from 'react';
import {
  createStyles,
  Button,
  Header,
  Paper,
  Card,
  Code,
  Group,
  Container,
  Grid,
  Title,
  Text,
  ScrollArea
} from '@mantine/core';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { setFlowType, flowTypes } from '../features/flow/flowSlice.js';
import { setCalibrationStatus, setReaderDoorStatus } from '../features/system/systemSlice.js';
import { reset as scanReset } from '../features/scan/scanSlice.js';
import { reset as analysisReset } from '../features/analysis/analysisSlice.js';
import { Logo } from '../components/Logo.jsx';
import { SubHeading } from '../components/SubHeading.jsx';
import { IndicatorBadge } from '../components/IndicatorBadge.jsx';
import { IllustrationScan } from '../assets/IllScan.js';
import { IllustrationAnalyze } from '../assets/IllAnalyze.js';
import { IllustrationTemplate } from '../assets/IllTemplate.js';
import { createReadableDate } from '../../lib/util/createReadableDate.js';
import { getDefaultReader } from '../actions/readerActions.js';
import { useAppStyles } from '../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export default function Dashboard() {
  const { classes, cx } = useStyles();
  const [scan, setScan] = useState();
  const navigate = useNavigate();

  const dispatch = useDispatch();
  // get state from redux
  const getScanState = useSelector((state) => ({
    scan: state.scan
  }));

  const systemState = useSelector((state) => ({
    lastCalibrationDate: state.system.lastCalibrationDate,
    readerDoorStatus: state.system.readerDoorStatus
  }));

  const getAnalysisState = useSelector((state) => state.analysis);

  useEffect(() => {
    dispatch(setFlowType({ type: flowTypes.NONE }));
    dispatch(scanReset());
    dispatch(getDefaultReader());
    dispatch(analysisReset());
  }, []);

  // function to get calibration data
  const getInitialCalibrationData = async () => {
    const initCalibrationData = await window.api.getCalibration;

    if (initCalibrationData) {
      await dispatch(setCalibrationStatus(initCalibrationData));
    } else {
      await dispatch(setCalibrationStatus(null));
    }
  };

  // get initial calibration data on mount
  useEffect(() => {
    getInitialCalibrationData();
  }, []);

  /*
  // calibration calclations
  */
  let calibrationStatus = 'not calibrated';
  let calibrationMessage = 'Your device has not been calibrated yet. Please calibrate your device before use.';
  let readableLastCalibratedDate;
  let readableNextCalibrationDate;

  // console.log('Dashboard: system calibration date', systemState);

  if (systemState.lastCalibrationDate !== null) {
    // set new last calibrated date
    const lastCalibrated = new Date(systemState.lastCalibrationDate);
    readableLastCalibratedDate = createReadableDate(lastCalibrated);
    // console.log('__lastCalibrationDate__', readableLastCalibratedDate);

    const today = new Date();

    const daysSinceLastCalibration = Math.round((today - lastCalibrated) / (1000 * 60 * 60 * 24));
    // const daysSinceLastCalibration = 23;
    // console.log('daysSinceLastCalibration', daysSinceLastCalibration);

    // calculate next calibration date
    const upcomingCalibrationDate = new Date(lastCalibrated.setDate(lastCalibrated.getDate() + 90));
    readableNextCalibrationDate = createReadableDate(upcomingCalibrationDate);
    // console.log('__nextCalibrationDate__', readableNextCalibrationDate);

    // set calibration status
    if (daysSinceLastCalibration >= 90) {
      calibrationStatus = 'expired';
      calibrationMessage = 'Your calibration has expired. Please calibrate your device.';
    } else if ((daysSinceLastCalibration >= 83) && (daysSinceLastCalibration < 90)) {
      calibrationStatus = 'warning';
      const daysLeft = 90 - daysSinceLastCalibration;
      calibrationMessage = `Your calibration will expire in ${daysLeft} days. Please calibrate your device.`;
    } else if (daysSinceLastCalibration < 83) {
      calibrationStatus = 'calibrated';
      const daysLeft = 90 - daysSinceLastCalibration;
      calibrationMessage = `Your calibration will expire in ${daysLeft} days. You're OK for now.`;
    }
  }
  // console.log('calibrationStatus', calibrationStatus);

  /*
  // documentation windows
  */
  const showDocumentation = (url) => {
    window.api.popWindow(url);
  };

  const toAnalyze = useCallback(() => {
    dispatch(setFlowType({ type: flowTypes.ANALYZE }));
    navigate('/analyze/analyze-one', { replace: true });
  }, [navigate]);
  const toKitSelection = useCallback(() => {
    dispatch(setFlowType({ type: flowTypes.SCAN }));
    navigate('/scan/scan-one', { replace: true });
  }, [navigate]);
  const toManageTemplates = useCallback(() => {
    dispatch(setFlowType({ type: flowTypes.MANAGE_ANALYSIS_TEMPLATES }));
    navigate('/manage-templates/analysis-temps-one', { replace: true });
  }, [navigate]);
  const toViewResults = useCallback(() => {
    dispatch(setFlowType({ type: flowTypes.VIEW_RESULTS }));
    navigate('/view-results/results-one', { replace: true });
  }, [navigate]);

  const disableReader = calibrationStatus === 'expired' || calibrationStatus === 'not calibrated';

  // console.log('Dashboard: reader disabled?', disableReader);

  return (
    <>
      <Header className={classes.header} height={60} p="xs" fixed>
        <Group position="start">
          <Logo />
          <Code className={classes.version}>v1.0.0</Code>
        </Group>
      </Header>
      <div className={classes.dashboardAppBackground}>
        <section className={classes.container}>
          <Title order={4} mb={25} className={classes.text}>Dashboard</Title>
          <Grid grow="true" align="stretch">
            <Grid.Col span={7}>
              <Paper>
                <SubHeading>Empower Reader</SubHeading>
                <Group apart="true" grow="true" align="stretch">
                  <Card withBorder>
                    <div className={classes.titleWithBadge}>
                      <Title order={6}>
                        Reader Status
                        {' '}
                      </Title>

                      <IndicatorBadge status="ok" />
                    </div>
                    <Text size="xs" className={classes.text}>Reader is connected</Text>

                    <Card.Section className={classes.cardSpacer} />

                    <Text size="xs" className={classes.text}>Your reader status indicates that the reader is connected and ready to be used.</Text>
                  </Card>

                  <Card>
                    <div className={classes.titleWithBadge}>
                      <Title order={6}>Reader Door Status</Title>
                      <IndicatorBadge status="warning" />
                    </div>
                    <Text size="xs" className={classes.text}>Door is open</Text>
                    <Card.Section className={classes.cardSpacer} />
                    <Text size="xs" className={classes.text}>The reader door is open and will need to be closed in order for a scan to run.</Text>
                  </Card>

                  <Group apart="true" grow="true" direction="column">
                    <Card>
                      <Title order={6}>Last Calibration</Title>
                      <Text size="xs" className={classes.text}>{readableLastCalibratedDate || 'Not Calibrated'}</Text>
                    </Card>

                    <Card>
                      <Title order={6}>Reader Serial Number</Title>
                      <Text size="xs" className={classes.text}>xxxx-xxxx-xxxx-xxxx</Text>
                    </Card>
                  </Group>

                  {/* {(calibrationStatus !== 'calibrated' || calibrationStatus === 'not calibrated') && ( */}
                  <Card>
                    {readableNextCalibrationDate && (
                      <>
                        <Title order={6}>Next Calibration Date</Title>
                        <Text size="xs" className={classes.text} mb={10}>{readableNextCalibrationDate}</Text>
                      </>
                    )}
                    <Button
                      type="button"
                      color={
                        // eslint-disable-next-line no-nested-ternary
                        calibrationStatus === 'warning' ? 'yellow' : calibrationStatus === 'calibrated' ? 'blue' : 'red'
                      }
                      sx={(theme) => ({ backgroundColor: calibrationStatus === 'warning' ? theme.colors.yellow[5] : calibrationStatus === 'calibrated' ? theme.colors.blue[5] : theme.colors.red[5] })}
                      size="xs"
                      radius="xl"
                      onClick={() => navigate('/calibration', { replace: true })}
                    >
                      Calibrate
                    </Button>
                    <Card.Section className={classes.cardSpacer} />
                    <Text size="xs" className={classes.text}>{calibrationMessage}</Text>
                  </Card>
                </Group>
              </Paper>
            </Grid.Col>

            <Grid.Col span={3}>
              <Paper style={{ height: '100%' }}>
                <SubHeading>Documentation</SubHeading>

                <ScrollArea style={{ height: 180 }} type="always" offsetScrollbars scrollbarSize={6}>
                  <Group position="apart" grow="true" direction="column" style={{ paddingRight: 15 }}>
                    <Card>
                      <Group position="apart">
                        <Container size={180} px={0}>
                          <Title order={6}>Connect to the Empower Reader</Title>
                          <Text sx={{ fontSize: 10 }} className={classes.text}>Provides instructions on how to connect to the Empower Reader.</Text>
                        </Container>
                        <Button
                          type="button"
                          className={classes.actionButton}
                          size="xs"
                          radius="xl"
                          onClick={() => showDocumentation('Connect Documentation')}
                        >
                          View
                        </Button>
                      </Group>
                    </Card>

                    <Card>
                      <Group position="apart" style={{ width: '100%' }}>
                        <Container size={180} px={0}>
                          <Title order={6}>Load a plate</Title>
                          <Text sx={{ fontSize: 10 }} className={classes.text}>Provides instructions on how to load a plate.</Text>
                        </Container>
                        <Button
                          type="button"
                          className={classes.actionButton}
                          size="xs"
                          radius="xl"
                          onClick={() => showDocumentation('Load Plate Documentation')}
                        >
                          View
                        </Button>
                      </Group>
                    </Card>

                    <Card>
                      <Group position="apart" style={{ width: '100%' }}>
                        <Container size={180} px={0}>
                          <Title order={6}>Product Kit</Title>
                          <Text sx={{ fontSize: 10 }} className={classes.text}>Provides instructions on how to load a plate.</Text>
                        </Container>
                        <Button
                          type="button"
                          className={classes.actionButton}
                          size="xs"
                          radius="xl"
                          onClick={() => showDocumentation('Load Plate Documentation')}
                        >
                          View
                        </Button>
                      </Group>
                    </Card>
                  </Group>
                </ScrollArea>
              </Paper>
            </Grid.Col>
          </Grid>

          <Group grow="true" mt={15} align="stretch">
            <Paper>
              <SubHeading centered>Scan</SubHeading>

              <Card mb={15} style={{ height: '244px' }}>
                <Card.Section p={40} style={{ padding: 40, textAlign: 'center' }}>
                  <IllustrationScan />
                </Card.Section>
                <Text size="xs" className={classes.text} align="center">Set up a plate for scanning by the Reader.</Text>
              </Card>

              <Button
                type="button"
                className={classes.actionButton}
                size="md"
                fullWidth
                disabled={disableReader}
                onClick={() => toKitSelection()}
              >
                Set Up Scan
              </Button>
            </Paper>
            <Paper>
              <SubHeading centered>Analyze Scan</SubHeading>

              <Card mb={15} style={{ height: '244px' }}>
                <Card.Section p={40} style={{ padding: 40, textAlign: 'center' }}>
                  <IllustrationAnalyze />
                </Card.Section>
                <Text size="xs" className={classes.text} align="center">Select a scan and analysis template to analyze the results.</Text>
              </Card>

              <Button
                type="button"
                className={classes.actionButton}
                size="md"
                fullWidth
                onClick={() => toAnalyze()}
              >
                Analyze Scan
              </Button>
            </Paper>

            <Group position="apart" grow="true" direction="column">
              <Paper>
                <SubHeading centered>Manage Analysis Template</SubHeading>
                <Text
                  size="xs"
                  className={classes.text}
                  sx={(theme) => ({
                    maxWidth: '200px',
                    margin: '0 auto 30px auto',
                    textAlign: 'center'
                  })}
                >
                  Create, upload, or, copy and modify an analysis template.
                </Text>

                <Button
                  type="button"
                  className={classes.actionButton}
                  size="md"
                  fullWidth
                  onClick={() => toManageTemplates()}
                >
                  Manage Templates
                </Button>
              </Paper>

              <Paper>
                <SubHeading centered>Results</SubHeading>
                <Text
                  size="xs"
                  className={classes.text}
                  sx={(theme) => ({
                    maxWidth: '200px',
                    margin: '0 auto 18px auto',
                    textAlign: 'center'
                  })}
                >
                  View and export previous results to your local environment.
                </Text>

                <Button
                  type="button"
                  className={classes.actionButton}
                  size="md"
                  fullWidth
                  onClick={() => toViewResults()}
                >
                  View Results
                </Button>
              </Paper>
            </Group>

          </Group>

          {/* TODO: remove below code, it was just api testing */}
          <div className={classes.body}>
            <div style={{ textAlign: 'center' }}>

              {scan && (
                <div
                  className="scan-data"
                  style={{
                    textAlign: 'left'
                    // color: 'white'
                  }}
                >
                  <h2>Scan Data</h2>

                  <div style={{ padding: '15px 20px' }}>
                    <pre>
                      {JSON.stringify({ scan }, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* </ScrollArea> */}
        </section>
      </div>
    </>
  );
}
