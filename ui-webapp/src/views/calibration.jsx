import React, {
  useEffect,
  useState,
  useReducer,
  useCallback
} from 'react';
import {
  createStyles,
  Button,
  Header,
  Paper,
  Card,
  Code,
  Group,
  Text,
  Breadcrumbs,
  Modal
} from '@mantine/core';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { IllustrationTray } from '../assets/IllTray.js';
import { saveCalibration } from '../actions/scanActions.js';
import { getCalibrationProduct } from '../actions/productActions.js';
import { productSelector } from '../features/product/productSlice.js';
import { useAppStyles } from '../styles/appStyles.js';
import { MantineProvider, ColorSchemeProvider } from '@mantine/core';
import empowerTheme from '../styles/theme.js';

const useStyles = createStyles(useAppStyles);

export default function Calibration({ toggleMantineColorScheme, colorScheme }) {
  const { classes, cx } = useStyles(colorScheme);

  const navigate = useNavigate();
  const toDashboard = useCallback(() => navigate('/', { replace: true }), [navigate]);
  const dispatch = useDispatch();
  const systemState = useSelector((rState) => ({
    lastCalibrationDate: rState.system.lastCalibrationDate
  }));
  const { status = '' } = useSelector((state) => state?.scan?.lastCalibrateUpdate) || {};
  const [modalOpen, setModalOpen] = useState(false);
  const defaultReaderSerialNumber = useSelector((state) => state?.reader?.serialNumber);
  const { calibrationProductId } = useSelector(productSelector);

  useEffect(() => {
    dispatch(getCalibrationProduct());
  }, []);

  useEffect(() => {
    if (status === 'COMPLETE') {
      setTimeout(() => {
        toDashboard();
      }, 5000);
    }
  }, [status]);

  const startCalibration = () => {
    // get calibration plate product id

    const calibration = {
      "name": "config",
      "productId": calibrationProductId, // productName or _id?
      "protocol": "calibrate",
      "protocolArgs": {
      },
      "readerSerialNumber": defaultReaderSerialNumber,
    }
    dispatch(saveCalibration(calibration))
  }

  const renderCalibrationCommandMessage = (complete, error) => {

    if (!complete && !error) {
      return (
        <Text size="sm" color="gray" mb={15}>
          Confirm that the Calibration Plate is loaded into the Reader correctly to begin.
        </Text>
      );
    }

    if (error) {
      return (
        <div>
          <Text size="sm" color="gray" mb={15}>Something went wrong</Text>
          <Button
            type="button"
            color="red"
            size="md"
            onClick={() => {
              toDashboard();
            }}
          >
            Back to Dashboard
          </Button>
        </div>
      );
    }

    return (<Text size="sm" color="gray" mb={15}>Calibrating...</Text>);
  }

  let calibrationMessage = 'Your device has not been calibrated yet. It will not be usable.';

  if (systemState.lastCalibrationDate !== null) {
    const lastCalibrated = new Date(systemState.lastCalibrationDate);
    const today = new Date();
    const daysSinceLastCalibration = Math.round((today - lastCalibrated) / (1000 * 60 * 60 * 24));

    if (daysSinceLastCalibration >= 90) {
      calibrationMessage = 'Your calibration has expired. Your device will not be usable until it has been recalibrated.';
    } else if ((daysSinceLastCalibration >= 83) && (daysSinceLastCalibration < 90)) {
      const daysLeft = 90 - daysSinceLastCalibration;
      calibrationMessage = `If you stop calibration, you have ${daysLeft} days left to complete the calibration.`;
    } else if (daysSinceLastCalibration < 83) {
      calibrationMessage = '';
    }
  }

  const isComplete = status === 'COMPLETE';
  const isError = status === 'ERROR';
  const isCancelled = status === 'CANCELLED'; // TODO: this doesn't exist yet(?)!
  const isQueuedOrRunning = status === 'QUEUED' || status === 'RUNNING';

  return (
    <ColorSchemeProvider colorScheme={colorScheme} toggleColorScheme={toggleMantineColorScheme}>
      <MantineProvider theme={{ colorScheme, ...empowerTheme }}>
        <>
          <Header className={classes.header} height={60} p="xs" fixed>
            <Group position="start">
              <Code className={classes.version}>v1.1.0</Code>
            </Group>
          </Header>

          <div className={classes.dashboardAppBackground}>
            <section className={classes.calibrationContainer}>
              <Breadcrumbs separator="›">
                <Text size="sm" weight={600} sx={(theme) => ({ color: theme.colors.gray[5] })}>Dashboard</Text>
                <Text size="sm" weight={600} sx={(theme) => ({ color: theme.colors.gray[5] })}>Calibrate</Text>
              </Breadcrumbs>

              <div className={classes.column}>
                <Paper mb={50}>

                  <Card mb={30} className={classes.card}>
                    <Card.Section style={{ padding: '40px 0', textAlign: 'center' }}>
                      <IllustrationTray complete={isComplete} error={isError} />
                    </Card.Section>
                    {!isCancelled && (
                      <>
                        {renderCalibrationCommandMessage(isComplete, isError)}
                      </>
                    )}
                  </Card>

                  {(!isComplete && !isError && !isCancelled) && (
                    <div className={classes.buttonSection}>
                      <Button
                        type="button"
                        className={classes.actionButton}
                        size="md"
                        fullWidth
                        mb={30}
                        onClick={() => startCalibration()}
                        disabled={isQueuedOrRunning}
                      >
                        {isQueuedOrRunning ? 'Calibrating...' : 'Confirm & Calibrate'}
                      </Button>
                      <Text size="sm" align="center" sx={(theme) => ({ fontStyle: 'italic', color: theme.colors.dark[2] })}>
                        Calibration will take approximately 20 minutes. You will remain on this page until the calibration
                        has completed.
                      </Text>
                    </div>
                  )}
                </Paper>

                {(isComplete || isCancelled) && (
                  <Text size="sm" sx={(theme) => ({ fontStyle: 'italic', fontWeight: 'italic', color: theme.colors.dark[2] })} mb={15}>
                    You will now be redirected to the dashboard.
                  </Text>
                )}
              </div>
            </section>
          </div>



          {/* Stop Modal */}
          <Modal
            id={"calibration-cancel-modal"}
            opened={modalOpen}
            onClose={() => setModalOpen(false)}
            closeOnClickOutside={false}
            closeOnEscape={false}
            size="lg"
            // title="Stop Calibration?"
            sx={(theme) => ({
              ".mantine-Modal-modal": {
                top: '30%'
              },
            })}
            styles={{
              header: { marginBottom: 0 },
              body: { textAlign: 'center' }
            }}
          >
            <Text size="lg" weight={600} mb={15}>Stop Calibration?</Text>
            <Text size="sm" mb={15}>{calibrationMessage}</Text>
            <Text size="sm" mb={15}>Are you sure you want to stop calibration at this time?</Text>

            <Group apart="true" grow="true" align="stretch" mt={40}>
              <Button
                type="button"
                variant="default"
                size="md"
                onClick={() => { setModalOpen(false); }}
              >
                No, continue calibrating
              </Button>
              <Button
                type="button"
                color="red"
                size="md"
                onClick={() => {
                  setModalOpen(false);
                  toDashboard();
                  // todo: find if there's a way to cancel a calibration
                }}
              >
                Yes, stop calibration
              </Button>
            </Group>
          </Modal>
        </>
      </MantineProvider>
    </ColorSchemeProvider>
  );
}
