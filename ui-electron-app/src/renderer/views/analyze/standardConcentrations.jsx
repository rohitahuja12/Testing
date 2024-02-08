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
    Grid,
    Box,
    NumberInput,
    Loader
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
import { Flow } from '../../enums/Flow.js';
import { setTemplateConcentrations, setTemplateStandardDilution } from '../../features/analysis/analysisSlice.js';
import { saveAnalysisTemplate, saveAnalysis } from '../../actions/analysisTemplateActions.js';
import { scanSelector } from '../../features/scan/scanSlice.js';
import { BBLoader } from '../../components/brightestBio/BBLoader.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export default function StandardConcentrations({ ...props }) {
    // get state from redux
    const globalAnalysisState = useSelector((state) => state.analysis);
    const [showError, setShowError] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [concentrations, setConcentrations] = useState(null);
    const [originalConcentrations, setOriginalConcentrations] = useState(null);
    const [standardDilution, setStandardDilution] = useState(3.0);
    const analysis = useSelector((state) => state.analysis);
    const { product } = useSelector((state) => state.product);
    const flowType = useSelector((state) => (state.flow.type));
    const templatedWells = useSelector((state) => (state.analysis.templatedWells));
    const savedAnalysisTemplate = useSelector((state) => (state.analysis.savedAnalysisTemplate));
    const { lastScanUpdate } = useSelector(scanSelector);

    useEffect(() => {
        if (product?.recommendedInitialConcentrations) {
            setConcentrations(product.recommendedInitialConcentrations);
            setOriginalConcentrations(product.recommendedInitialConcentrations);
        } else {
            const defaults = {
                "IL-4": 1000.00,
                "IL-10": 1000.00,
                "IL-5": 1000.00,
                "IL-13": 1000.00,
                "IL-6": 1000.00,
                "IL-1B": 1000.00,
                "IL-8": 1000.00,
                "IL-2": 1000.00,
            };
            setConcentrations(defaults);
            setOriginalConcentrations(defaults);
        }
    }, [product])

    useEffect(() => {
        if (savedAnalysisTemplate && flowType === Flow.SCAN_TO_ANALYSIS) {
            // create a new analysis with the template data
            // navigate to analysis summary page
            // make sure to reset the pre-selected analysis template data
            // keep in mind that the scan could still be in progress
            const scanId = lastScanUpdate?._id;
            const analysis = {
                scanId,
                templateId: savedAnalysisTemplate._id,
                ...savedAnalysisTemplate
            }
            dispatch(saveAnalysis(analysis));
            navigate('/analyze/analyze-two', { replace: true });


        }
    }, [savedAnalysisTemplate]);

    // dispatch to redux
    const dispatch = useDispatch();
    const { classes, cx } = useStyles();
    const mantineTheme = getTheme(DEFAULT_OPTIONS);
    const theme = useTheme(mantineTheme);
    const navigate = useNavigate();

    const onHandleSubmit = () => {
        // save state to redux
        dispatch(setTemplateConcentrations(concentrations));
        dispatch(setTemplateStandardDilution(standardDilution));

        dispatch(saveAnalysisTemplate({
            protocol: 'pArrayFluoro', // TODO: where should this come from?
            name: analysis.name,
            productId: product._id,
            productName: product?.productName,
            notes: analysis.notes,
            protocolArgs: {
                initialConcentrations: concentrations,
                standardDilutionFactor: standardDilution,
                wells: templatedWells,
                initialConcentrationUnits: 'pg/ml'
            }
        }));

        if (flowType === Flow.MANAGE_ANALYSIS_TEMPLATES) {
            navigate('/manage-templates/analysis-temps-six', { replace: true });
        }
    };

    const renderConcentrationInput = (initialConcentration, label, onChange, showError) => {

        const calculateAndsyncConcentrations = (concentrations, previousConcentration, newConcentration, concentrationKey) => {
            const concentrationKeys = Object.keys(concentrations);
            const concentrationRatio = newConcentration / previousConcentration;
            const newConcentrations = { ...concentrations };
            concentrationKeys.forEach((key) => {
                if (key !== concentrationKey) {
                    newConcentrations[key] = originalConcentrations[key] * concentrationRatio;
                }
            });
            return newConcentrations;
        }

        initialConcentration = initialConcentration || 0;

        return (<Grid.Col span={6}>
            <NumberInput
                placeholder={initialConcentration}
                defaultValue={initialConcentration}
                label={label}
                onChange={(val) => {
                    const newConcentrations = calculateAndsyncConcentrations(concentrations, originalConcentrations[label], val, label);
                    onChange({ ...newConcentrations, [label]: val });
                }}
                required
                error={showError ? 'Please enter a concentration' : false}
                mb={30}
                precision={2}
                value={initialConcentration}
                hideControls
            />
        </Grid.Col>)
    }

    const renderDilutionInput = (initialDilution, label, onChange, showError) => (
        <NumberInput
            placeholder={initialDilution}
            defaultValue={initialDilution}
            label={label}
            onChange={(val) => { onChange(val); console.log('dilution', standardDilution) }}
            required
            error={showError ? 'Please enter a dilution' : false}
            mb={30}
            precision={1}
            hideControls
        />
    );

    const renderDefaultConcentrationInputs = () => {
        return (
            <>
                {renderConcentrationInput(concentrations['IL-2'] || 1000.00, 'IL-2', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-4'] || 1000.00, 'IL-4', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-5'] || 1000.00, 'IL-5', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-6'] || 1000.00, 'IL-6', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-8'] || 1000.00, 'IL-8', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-10'] || 1000.00, 'IL-10', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-13'] || 1000.00, 'IL-13', setConcentrations, false)}
                {renderConcentrationInput(concentrations['IL-1B'] || 1000.00, 'IL-1B', setConcentrations, false)}
            </>
        )
    }

    return (
        <>
            <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
                {/* Group at position start in AppShellHeader component with title prop */}
                <Group position="end">
                    <Button variant="default" leftIcon={<ArrowLeft size={18} />} onClick={() => navigate('/manage-templates/analysis-temps-four', { replace: true })}>
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

                <Box className={classes.tableBox}>
                    <Paper sx={{ marginTop: 30, padding: 30 }} className={classes.tablePaper}>
                        <Text>
                            Default values are based off the product. Please adjust as needed. Enter the initial concentration of each of the standard analytes in pg/ml.
                        </Text>

                        <Grid sx={{ marginTop: 30 }} grow>
                            {concentrations && Object.keys(concentrations).map((label, index) => {
                                return renderConcentrationInput(concentrations[label], label, setConcentrations, showError);
                            })}
                            {!concentrations && <BBLoader />}
                        </Grid>

                        <hr />

                        <Text style={{ marginTop: 30 }}>
                            Enter the dilution factors.
                        </Text>

                        <Grid sx={{ marginTop: 30 }} grow>
                            <Grid.Col span={6}>
                                {renderDilutionInput(standardDilution, 'Standard Dilution Factor', setStandardDilution, false)}
                            </Grid.Col>
                            <Grid.Col span={6} />
                        </Grid>


                    </Paper>
                </Box>
            </div>
        </>
    );
}
