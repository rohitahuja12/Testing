import React, { useState, useEffect, useCallback } from 'react';
import {
    createStyles,
    Text,
    Group,
    Button,
    ScrollArea,
    Paper,
    Alert,
    Modal,
    Box,
    Grid
} from '@mantine/core';
import { AlertCircle } from 'tabler-icons-react';
import { useTheme } from '@table-library/react-table-library/theme';
import { Link, useNavigate } from 'react-router-dom';
import {
    DEFAULT_OPTIONS,
    getTheme
} from '@table-library/react-table-library/mantine';
import { useDispatch, useSelector } from 'react-redux';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { ProgressBar } from '../../components/ProgressBar.jsx';
import { stop } from '../../features/scan/scanSlice.js';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export default function ScanSummary({ ...props }) {
    const [showError, setShowError] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);

    // dispatch to redux
    const dispatch = useDispatch();
    // get state from redux
    const {
        name, notes, product, scan, lastScanUpdate, lastSavedScan
    } = useSelector((state) => state.scan);

    const { classes, cx } = useStyles();
    const mantineTheme = getTheme(DEFAULT_OPTIONS);
    const theme = useTheme(mantineTheme);
    const navigate = useNavigate();

    const onHandleSubmit = () => {
        setShowError(false);
    };

    // const toDashboard = useCallback(() => navigate('/', { replace: true }), [navigate]);

    return (
        <>
            <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
                {/* Group at position start in AppShellHeader component with title prop */}
                <Group position="end">
                    <Button variant="default" onClick={() => console.log('click')}>
                        Set Up Another Scan
                    </Button>

                    <Button
                        type="button"
                        color="dark"
                        onClick={() => navigate('/', { replace: true })}
                    >
                        Return to Dashboard
                    </Button>
                </Group>
            </AppShellHeader>

            <div className={classes.appBackground}>
                {lastScanUpdate?.status === "COMPLETE" && <Alert icon={<AlertCircle size={16} />} title="Scan details successfully saved." color="green" sx={{ border: 'solid 1px #37B24D' }} />}

                <Box className={classes.tableBox}>
                    <Paper sx={{ marginTop: 30, padding: 30 }} className={classes.tablePaper} >
                        <Text size="sm" weight={700}>Scan Details</Text>
                        <Text color="dimmed" sx={{ fontSize: 12 }}>The following are details of your scan summary.</Text>

                        <hr />

                        <Grid>
                            <Grid.Col span={6}>
                                <Box sx={{ minHeight: 50, marginBottom: 20 }}>
                                    <Text sx={{ fontSize: 12, fontWeight: 700 }}>Scan Name</Text>
                                    <Text sx={{ fontSize: 12 }}>{lastSavedScan.name}</Text>
                                </Box>

                                <Box sx={{ minHeight: 50, marginBottom: 20 }}>
                                    <Text sx={{ fontSize: 12, fontWeight: 700 }}>Scan Notes</Text>
                                    <Text sx={{ fontSize: 12 }}>{lastSavedScan.notes}</Text>
                                </Box>
                            </Grid.Col>

                            <Grid.Col span={6}>
                                <Box sx={{ minHeight: 50, marginBottom: 20 }}>
                                    <Text sx={{ fontSize: 12, fontWeight: 700 }}>Product / Kit Name</Text>
                                    <Text sx={{ fontSize: 12 }}>{product.productName}</Text>
                                </Box>

                                <Box sx={{ minHeight: 50, marginBottom: 20 }}>
                                    <Text sx={{ fontSize: 12, fontWeight: 700 }}>Scan Metadata</Text>
                                    <Text sx={{ fontSize: 12 }}>I dont know what the metadata is supposed to be.</Text>
                                </Box>
                            </Grid.Col>
                        </Grid>
                    </Paper>
                </Box>
            </div>

            <Modal
                opened={lastScanUpdate?.status === "QUEUED" || lastScanUpdate?.status === "RUNNING"}
                onClose={() => setModalOpen(false)}
                withCloseButton={false}
                closeOnClickOutside={false}
                closeOnEscape={false}
                size={441}
                centered
                styles={{
                    header: { marginBottom: 0 },
                    body: { textAlign: 'center' }
                    // overlay: { backdropFilter: 'blur(3px)', backgroundColor: 'initial !important' }
                }}
            >
                <ProgressBar // TODO: refactor this whole thing
                    total={20}
                    completed={lastScanUpdate?.status === "COMPLETE"
                        ? 20
                        : 1}
                    error={lastScanUpdate?.status === "ABORTED" || lastScanUpdate?.status === "ERROR"}
                    clickHandler={() => dispatch(stop())}
                    runningText={lastScanUpdate?.status === "QUEUED" || lastScanUpdate?.status === "RUNNING"
                        ? 'estimated completion time 20 minutes'
                        : 'Scan stopped'}
                    completedText="Scan Complete"
                    buttonText="Stop Scan"
                />
            </Modal>
        </>
    );
}
