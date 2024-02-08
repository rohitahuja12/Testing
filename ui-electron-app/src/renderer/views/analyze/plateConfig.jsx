import React, {
  useState, useEffect, useRef, useCallback
} from 'react';
import {
  createStyles,
  Text,
  Group,
  Button,
  ScrollArea,
  Paper,
  TextInput,
  Textarea,
  InputWrapper,
  Card,
  Alert,
  UnstyledButton,
  Modal,
  Box,
  Kbd,
  Accordion,
  Select,
  Switch
} from '@mantine/core';
import {
  ArrowLeft, ArrowRight, BorderTop, FloatNone, InfoCircle
} from 'tabler-icons-react';
import { useTheme } from '@table-library/react-table-library/theme';
import { Link, useNavigate } from 'react-router-dom';
import {
  DEFAULT_OPTIONS,
  getTheme
} from '@table-library/react-table-library/mantine';
import { useDispatch, useSelector } from 'react-redux';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { WellPlateAdvanced } from '../../components/WellPlateAdvanced.jsx';
import { Flow } from '../../enums/Flow.js';
import { setTemplatedWells } from '../../features/analysis/analysisSlice.js';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export default function PlateConfig({ ...props }) {
  // get state from redux
  const [showError, setShowError] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const analysis = useSelector((state) => state.analysis);
  const { product } = useSelector((state) => state.product);
  const flowType = useSelector((state) => (state.flow.type));

  // dispatch to redux
  const dispatch = useDispatch();

  const { classes, cx } = useStyles();
  const mantineTheme = getTheme(DEFAULT_OPTIONS);
  const theme = useTheme(mantineTheme);
  const navigate = useNavigate();

  const onHandleSubmit = () => {
    console.log('continue to standard concentrations page');
    // continue to next standard concentrations page
    if (flowType === Flow.MANAGE_ANALYSIS_TEMPLATES || flowType === Flow.SCAN_TO_ANALYSIS) {
      navigate('/manage-templates/analysis-temps-five', { replace: true });
    }
  };

  return (
    <>
      <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
        {/* Group at position start in AppShellHeader component with title prop */}
        <Group position="end">
          <Button variant="default" leftIcon={<ArrowLeft size={18} />} onClick={() => navigate('/', { replace: true })}>
            Back
          </Button>

          <Button
            type="button"
            color="dark"
            rightIcon={<ArrowRight size={18} />}
            onClick={() => onHandleSubmit()}
          >
            Continue
          </Button>
        </Group>
      </AppShellHeader>


      <div className={classes.appBackground}>
        <Box sx={{ maxWidth: 815 }} className={classes.tableBox}>
          <Text className={classes.text} size="sm" weight={700}>{product?.name}</Text>
          <Text className={`${classes.text} ${classes.commandHeader}`}>Choose a preset Plate Map or create manually by configuring the wells properties. All configuration options are available by clicking on a column or row.</Text>

          <Paper sx={{ marginTop: '30px' }} className={classes.detailAccordion}>
            <Accordion

              iconPosition="right"
              styles={{
                item: {
                  borderBottom: '0px solid transparent'
                },
                label: {
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: 12,
                  fontWeight: 700
                },
                content: {
                },
                contentInner: {
                  padding: 30
                }
              }}
            >
              <Accordion.Item
                label={(
                  <>
                    <div>
                      Analysis Template Name:
                      {' '}
                      <span style={{ marginLeft: 10, fontWeight: 400 }}>{analysis.name}</span>
                    </div>
                    <Text sx={{ fontSize: 10, fontWeight: 400, color: '#7E7A7A' }}>Additional Information</Text>
                  </>
                )}
              >
                <Group spacing="xl" align="flex-start" grow>
                  <Box>
                    <Box mb={25}>
                      <Text
                        className={classes.text}
                        sx={(t) => ({
                          marginBottom: 5,
                          fontSize: 14,
                          fontWeight: 700,
                        })}
                      >
                        Product Name:
                      </Text>
                      {' '}
                      {product.name && <Text size="sm">{product.name}</Text>}
                    </Box>

                    <Box>
                      <Text
                        className={classes.text}
                        sx={(t) => ({
                          marginBottom: 5,
                          fontSize: 14,
                          fontWeight: 700,
                        })}
                      >
                        Analysis Template Notes:
                      </Text>
                      {' '}
                      {analysis.notes && <Text size="sm">{analysis.notes}</Text>}
                    </Box>
                  </Box>
                  <Box>
                    <Text
                      className={classes.text}
                      sx={(t) => ({
                        marginBottom: 5,
                        fontSize: 14,
                        fontWeight: 700,
                      })}
                    >
                      Analysis Template Additional Data:
                    </Text>
                    {' '}
                    <Text size="sm">A bunch of additional data.</Text>
                  </Box>
                </Group>
              </Accordion.Item>
            </Accordion>
          </Paper>

          <Paper sx={{ marginTop: 30, padding: 30 }} className={classes.detailAccordion}>
            <WellPlateAdvanced onWellChanges={(wells) => {
              dispatch(setTemplatedWells(wells));
            }} />
          </Paper>
        </Box>
      </div>

      {/* <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        closeOnClickOutside={false}
        closeOnEscape={false}
        size={441}
        centered
        styles={{
          header: { marginBottom: 0 },
          body: { textAlign: 'center' }
        }}
      >
        <Text size="lg" weight={600} mb={28}>
          While this scan is running, do you want
          <br />
          to set up its analysis?
        </Text>

        <Text size="sm" color="dimmed" mb={15} mt={28}>
          You can still configure an analysis template for
          <br />
          this scan later on if you prefer.
        </Text>

        <Group position="center">
          <Button
            type="button"
            variant="default"
            size="md"
            onClick={() => toScanSummary()}
            mt={30}
            mb={20}
          >
            No
          </Button>

          <Button
            type="button"
            color="blue"
            size="md"
            onClick={() => {
              dispatch(setFlowType({ type: flowTypes.SCAN_TO_ANALYSIS }));
              toAnalysisFlow();
            }}
            mt={30}
            mb={20}
          >
            Yes
          </Button>
        </Group>
      </Modal> */}
    </>
  );
}
