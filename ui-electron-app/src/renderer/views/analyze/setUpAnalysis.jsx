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
  Kbd
} from '@mantine/core';
import {
  ArrowLeft, ArrowRight, BorderTop, InfoCircle
} from 'tabler-icons-react';
import { useTheme } from '@table-library/react-table-library/theme';
import { Link, useNavigate } from 'react-router-dom';
import {
  DEFAULT_OPTIONS,
  getTheme
} from '@table-library/react-table-library/mantine';
import { useDispatch, useSelector } from 'react-redux';
import { setNameNotes } from '../../features/analysis/analysisSlice.js';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export default function SetUpAnalysis({ ...props }) {
  // get state from redux
  const flowType = useSelector((state) => state.flow.type);
  const globalAnalysisState = useSelector((state) => state.analysis);
  const [analysisInfo, setAnalysisInfo] = useState({ name: globalAnalysisState.name || '', notes: globalAnalysisState.notes || '' });
  const [showError, setShowError] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  // dispatch to redux
  const dispatch = useDispatch();

  const { classes, cx } = useStyles();
  const mantineTheme = getTheme(DEFAULT_OPTIONS);
  const theme = useTheme(mantineTheme);
  const navigate = useNavigate();

  // get product kit data
  // const getProductsData = async () => {
  //   window.api.getProductsList();
  //   await window.api.productsListContent((data) => setProductsList(data));
  // };
  // useEffect(() => {
  //   getProductsData();
  // }, []);

  const onHandleSubmit = () => {
    // set error states on fields that don't meet requirements
    if (analysisInfo.name === '') {
      setShowError(true);
      return;
    }

    setShowError(false);
    dispatch(setNameNotes(analysisInfo)); // probably needs to include the scan id as well
    if (flowType === 'SCAN_TO_ANALYSIS') {
      navigate('/analyze/analyze-five', { replace: true });
    } else {
      navigate('/manage-templates/analysis-temps-four', { replace: true });
    }
  };

  // watch fields for changes and update error state
  useEffect(() => {
    if (analysisInfo.name !== '') {
      setShowError(false);
    }
  }, [analysisInfo.name]);

  // const toScanSummary = useCallback(() => navigate('/scan/scan-three', { replace: true }), [navigate]);
  // const toAnalysisFlow = useCallback(() => navigate('/analyze/analyze-three', { replace: true }), [navigate]);

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
          {/* eslint-disable-next-line max-len */}
          <Text className={`${classes.commandHeader} ${classes.text}`}>Enter a name and notes to associate with the analysis template being created.</Text>
          <Text size='xs' className={classes.text}>Note: If you have copied and modified a previously saved analysis template from the table, that analysis template&apos;s content will autofill, with the ability to edit throughout.</Text>

          <Paper sx={{ marginTop: 30, padding: 30 }}>
            <TextInput
              placeholder="Analysis 1234"
              label="Analysis Template Name"
              description="Enter a name for this analysis template."
              value={analysisInfo?.name}
              onChange={(event) => setAnalysisInfo({ ...analysisInfo, name: event.target.value })}
              required
              error={showError ? 'Analysis template name is mandatory' : false}
              mb={30}
            />

            <Textarea
              placeholder="Enter analysis template notes..."
              label="Analysis Template Notes"
              description="Enter any notes to reference for help identifying this analysis template later."
              value={analysisInfo?.notes}
              onChange={(event) => setAnalysisInfo({ ...analysisInfo, notes: event.target.value })}
              autosize
              minRows={6}
            />
          </Paper>
        </Box>
      </div>
    </>
  );
}
