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
    Grid,
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
    Switch,
    NumberInput,
    Title
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
import { WellPlateMini } from '../../components/WellPlateMini.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

const TemplateSummary = ({ ...props }) => {
    const { product } = useSelector((state) => state.product);
    const {
        name,
        templatedWells,
        templateConcentrations,
        templateStandardDilution
    } = useSelector((state) => state.analysis);
    const flowType = useSelector((state) => (state.flow.type));
    const dispatch = useDispatch();
    const { classes, cx } = useStyles();
    const mantineTheme = getTheme(DEFAULT_OPTIONS);
    const theme = useTheme(mantineTheme);
    const navigate = useNavigate();

    const renderStandardConcentrations = (concentrations) => (
        Object.keys(concentrations)?.map(analyteName => (
            <Group spacing='xl' grow style={{ marginTop: 30 }}>
                <Text style={{ textAlign: 'left' }}>{analyteName}</Text>
                <Text style={{ textAlign: 'right' }}>{parseFloat(concentrations[analyteName]).toFixed(2)}</Text>
            </Group>
        ))
    )

    console.log(product);
    console.log(name);

    return (
        <>
            <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
                {/* Group at position start in AppShellHeader component with title prop */}
                <Group position="end">
                    <Button
                        type="button"
                        color="dark"
                        rightIcon={<ArrowRight size={18} />}
                        onClick={() => {
                            navigate('/', { replace: true });
                        }}
                    >
                        Done
                    </Button>
                </Group>
            </AppShellHeader>

            <div className={classes.appBackground}>
                <Box className={classes.tableBox}>
                    <Paper sx={{ marginTop: 30, padding: 30 }} className={classes.tablePaper}>
                        <Title style={{ fontSize: 18 }}>
                            Analysis Template Details
                        </Title>
                        <Text>
                            The following are the details of your analysis template summary.
                        </Text>

                        <hr className={classes.hr} />

                        <Grid sx={{ marginTop: 30 }} grow>
                            <Grid.Col span={6}>
                                <Text>
                                    Analysis Template Name
                                </Text>
                                <Text color="gray">
                                    {name || 'Sample Name'}
                                </Text>
                            </Grid.Col>
                            <Grid.Col span={6}>
                                <Text>
                                    Product/Kit Name
                                </Text>
                                <Text color="gray">
                                    {product?.productName || 'Sample Name'}
                                </Text>
                            </Grid.Col>
                            <Grid.Col span={12}>
                                <Text >
                                    Plate Map Configuration
                                </Text>
                            </Grid.Col>
                            <Grid.Col span={6}>
                                <Card
                                    style={{ minHeight: 650 }}
                                    shadow="sm" p="lg"
                                    className={classes.card}
                                >
                                    <Text style={{ fontWeight: 700, marginBottom: 30 }}>
                                        {product?.productName || 'Sample Product'} Named Analytes
                                    </Text>
                                    <WellPlateMini wells={templatedWells} />
                                </Card>
                            </Grid.Col>
                            <Grid.Col span={6}>
                                <Card
                                    style={{
                                        paddingLeft: 70, paddingRight: 70, minHeight: 650
                                    }}
                                    shadow="sm" p="lg"
                                    className={classes.card}
                                >
                                    <Text style={{ fontWeight: 700, marginBottom: 10 }}>
                                        Standard Concentrations
                                    </Text>
                                    <Text>
                                        The initial concentrations of each of the standard analytes in pg/ml.
                                    </Text>
                                    {renderStandardConcentrations(templateConcentrations || {
                                        "IL-4": 1000.00,
                                        "IL-10": 1000.00,
                                        "IL-5": 1000.00,
                                        "IL-13": 1000.00,
                                        "IL-6": 1000.00,
                                        "IL-1B": 1000.00,
                                        "IL-8": 1000.00,
                                        "IL-2": 1000.00,
                                    })}
                                    <hr />
                                    <Group spacing='xl' grow style={{ marginTop: 30 }}>
                                        <Text style={{ textAlign: 'left' }}>Serial Dilution Factor</Text>
                                        <Text style={{ textAlign: 'right' }}>{parseFloat(templateStandardDilution || 3.0).toFixed(1)}</Text>
                                    </Group>

                                </Card>
                            </Grid.Col>
                        </Grid>


                    </Paper>
                </Box>
            </div>
        </>
    );
}

export default TemplateSummary;
