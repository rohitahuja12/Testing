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
import { setNameNotes, start } from '../../features/scan/scanSlice.js';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { WellPlateBasic } from '../../components/WellPlateBasic.jsx';
import { setFlowType, flowTypes } from '../../features/flow/flowSlice.js';
import { saveScan } from '../../actions/scanActions.js';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export default function SetUpScan({ ...props }) {
    const [scanInfo, setScanInfo] = useState({ name: '', notes: '' });
    const [showError, setShowError] = useState(false);
    const [showWellsError, setShowWellsError] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const dispatch = useDispatch();
    const selectedWells = useSelector((state) => state.scan.selectedWells);
    const scanProduct = useSelector((state) => state.scan.product);
    const defaultReaderSerialNumber = useSelector((state) => state?.reader?.serialNumber);

    const { classes, cx } = useStyles();
    const mantineTheme = getTheme(DEFAULT_OPTIONS);
    const theme = useTheme(mantineTheme);
    const navigate = useNavigate();
    const clearSelections = useRef(null);
    const selectAll = useRef(null);

    const getIsValidAndShowInvalidErrorMessages = () => {
        // set error states on fields that don't meet requirements
        // TODO: Refactor this to not be a bit more generic. 
        // No need for two separate error message states
        if (scanInfo.name === '' || selectedWells.length === 0) {
            if (scanInfo.name === '') { setShowError(true); }
            if (selectedWells.length === 0) { setShowWellsError(true); }

            return false;
        }

        return true;
    }

    const unsetErrorMessageStates = () => {
        setShowError(false);
        setShowWellsError(false);
    }

    const handleAnalysisModal = (navigateToCreateAnalysis) => {
        console.log('pproductId', scanProduct?.productId);
        console.log('product name', scanProduct?.productName);

        dispatch(saveScan({
            name: scanInfo.name,
            protocol: 'pArray',
            productId: scanProduct?.productId,
            protocolArgs: {},
            readerSerialNumber: defaultReaderSerialNumber,
        }))
        dispatch(start({ isRunning: true, totalTime: 20000 })); // TODO: remove this implementation

        if (navigateToCreateAnalysis) {
            dispatch(setFlowType({ type: flowTypes.SCAN_TO_ANALYSIS }));
            navigate('/analyze/analyze-three', { replace: true });
        } else {
            navigate('/scan/scan-three', { replace: true })
        }
    }

    const onHandleSubmit = () => {

        if (!getIsValidAndShowInvalidErrorMessages()) return;

        unsetErrorMessageStates();

        // TODO: We may need to do soemthing here to check if the reader door is opn. May be a modal or just a warning if it is open?
        setModalOpen(true);
    };

    // watch fields for changes and update error state
    useEffect(() => {
        if (scanInfo.name !== '') {
            setShowError(false);
        }

        if (selectedWells?.length > 0) {
            setShowWellsError(false);
        }
    }, [scanInfo.name, selectedWells]);

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
                        onClick={onHandleSubmit}
                    >
                        Run Scan
                    </Button>
                </Group>
            </AppShellHeader>


            <div className={classes.appBackground}>
                <Box className={`${classes.tableBox} ${classes.commandHeader}`}>
                    <Text className={classes.text}>Enter a scan name and notes to associate with your scan. Then select which wells on the plate map the reader will scan.</Text>

                    <Paper sx={{ marginTop: 30, padding: 30 }} className={classes.tablePaper}>
                        <TextInput
                            placeholder="Scan 1234"
                            label="Scan Name"
                            description="Enter a name for this Scan."
                            value={scanInfo?.name}
                            onChange={(event) => setScanInfo({ ...scanInfo, name: event.target.value })}
                            required
                            error={showError ? 'Scan name is mandatory' : false}
                            mb={30}
                        />

                        <Textarea
                            placeholder="Enter scan notes..."
                            label="Scan Notes"
                            description="Enter any notes to reference for help identifying this scan later."
                            value={scanInfo?.notes}
                            onChange={(event) => setScanInfo({ ...scanInfo, notes: event.target.value })}
                            autosize
                            minRows={6}
                        />
                    </Paper>

                    <Paper sx={{ marginTop: 30, padding: 30 }} className={classes.tablePaper}>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                            <UnstyledButton sx={{ margin: '0 10px' }} onClick={() => clearSelections.current()}>Clear Plate</UnstyledButton>
                            <UnstyledButton sx={{ margin: '0 10px' }} onClick={() => selectAll.current()}>Select All</UnstyledButton>
                        </Box>
                        <InputWrapper
                            id="input-demo"
                            required
                            label="Well Selection"
                            // description="Please drag and select the area of the plate that you would like to be scanned. <br/>Hold down the shift key to select multiple wells."
                            mb={30}
                        // error="There is an error"
                        >
                            <Text sx={{ fontSize: 12 }} color="dimmed">
                                Please drag and select the area of the plate that you would like to be scanned.
                                {' '}
                                <br />
                                Hold down the
                                {' '}
                                <Kbd>shift</Kbd>
                                {' '}
                                key for multiple selections.
                            </Text>
                            {showWellsError && <Text sx={{ marginTop: 10, color: 'red', fontSize: 14 }}>A well selection is mandatory</Text>}
                        </InputWrapper>

                        <div className={classes.centeredChildren}>
                            <WellPlateBasic clearSelections={clearSelections} selectAll={selectAll} error={showWellsError} />
                        </div>

                    </Paper>
                </Box>
            </div>

            <Modal
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
                        onClick={() => handleAnalysisModal(false)}
                        mt={30}
                        mb={20}
                    >
                        No
                    </Button>

                    <Button
                        type="button"
                        color="blue"
                        size="md"
                        onClick={() => handleAnalysisModal(true)}
                        mt={30}
                        mb={20}
                    >
                        Yes
                    </Button>
                </Group>
            </Modal>
        </>
    );
}
