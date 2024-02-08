import React, { useState, useEffect, useCallback } from 'react';
import {
    createStyles,
    Text,
    Grid,
    Group,
    Button,
    ScrollArea,
    Paper,
    Card,
    TextInput,
    Checkbox,
    Collapse,
    Highlight,
    Pagination,
    Alert,
    Box,
    UnstyledButton
} from '@mantine/core';
import {
    ArrowLeft,
    ArrowRight,
    ArrowsSort,
    SortAscending,
    SortDescending,
    AlertCircle,
    FileExport,
    Copy,
    FileX
} from 'tabler-icons-react';
import {
    Table,
    Header,
    HeaderRow,
    HeaderCell,
    Body,
    Row,
    Cell
} from '@table-library/react-table-library/table';
import { usePagination } from '@table-library/react-table-library/pagination';
import {
    useRowSelect,
    CellSelect,
    SelectTypes,
    SelectClickTypes
} from '@table-library/react-table-library/select';
import { useSort, HeaderCellSort } from '@table-library/react-table-library/sort';
import { useTheme } from '@table-library/react-table-library/theme';
import {
    DEFAULT_OPTIONS,
    getTheme
} from '@table-library/react-table-library/mantine';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { analysisSelector, setSelectedTemplate } from '../../features/analysis/analysisSlice.js';
import { flowTypes } from '../../features/flow/flowSlice.js';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { createReadableDate } from '../../../lib/util/createReadableDate.js';
import { WellPlateMini } from '../../components/WellPlateMini.jsx';
import { scanList } from '../../../data-ui/scanlist.js';
import { getAnalysisTemplates, saveAnalysis } from '../../actions/analysisTemplateActions.js';
import { scanSelector } from '../../features/scan/scanSlice.js';
import { useAppStyles } from '../../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

/**
TODO:
* Depending on the flow we are in, if we want to choose a pre existing or copied analysis we need to make sure wells match.
* 'SCAN_TO_ANALYSIS' flow: we've already selected wells when setting up the scan so we can get those wells from scan.selectedWells in the redux store.
**/

export default function SelectAnalysis({ ...props }) {
    const [search, setSearch] = useState({ scans: '', templates: '' });
    const [collapse, setCollapse] = useState({ scans: { id: null }, templates: { id: null } });
    const [showAlert, setShowAlert] = useState(false);
    const [showUploadAlert, setShowUploadAlert] = useState({ show: false, status: null, message: '' });
    const { lastSavedScan } = useSelector(scanSelector);
    const analysisTemplates = useSelector(analysisSelector)?.analysisTemplates;

    const { classes, cx } = useStyles();
    const mantineTheme = getTheme(DEFAULT_OPTIONS);
    const theme = useTheme(mantineTheme);
    const navigate = useNavigate();

    const flowType = useSelector((state) => state.flow);
    // dispatch to redux
    const dispatch = useDispatch();

    const analysisData = analysisTemplates && analysisTemplates.length > 0 ? {
        nodes: analysisTemplates?.filter((item) => (
            item.name.toLowerCase().includes(search.templates.toLowerCase())
            || item?.notes.toLowerCase().includes(search.templates.toLowerCase())
            || item.kit.toLowerCase().includes(search.templates.toLowerCase())
        ))
    } : { nodes: [] };

    useEffect(() => {
        dispatch(getAnalysisTemplates());
    }
        , [])

    // search function to set search state
    // keyed for scans and templates
    const handleSearch = (event, key) => {
        setSearch({ ...search, [key]: event.target.value });
    };

    const onSortChange = (action, state) => {
        console.log(action, state);
    };

    const toggleCollapse = (id, key) => {
        setCollapse({ ...collapse, [key]: { id: id === collapse[key].id ? null : id } });
    };

    const analysisSort = useSort(
        analysisData,
        {
            onChange: onSortChange
        },
        {
            sortIcon: {
                iconDefault: <ArrowsSort color="black" fillOpacity={0} />,
                iconUp: <SortAscending color="black" fillOpacity={0} />,
                iconDown: <SortDescending color="black" fillOpacity={0} />
            },
            sortFns: {
                NAME: (array) => array.sort((a, b) => a.name - b.name),
                DATE: (array) => array.sort((a, b) => a.date - b.date)
            }
        }
    );

    const onSelectChange = (action, state) => {
        console.log(action, state);
    };

    const analysisSelect = useRowSelect(
        analysisData,
        { onChange: onSelectChange },
        {
            buttonSelect: SelectTypes.SingleSelect,
            clickType: SelectClickTypes.ButtonClick
        }
    );

    // add scan selection and analysis selection to object for analyzing
    // send to api to analyze
    // redirect to results page
    const selectAndAnalyze = () => {
        const analysisTemplateId = analysisSelect.state.id; // scanId field in analysis data

        // make sure scan `id` and scanId and `scanId` from analysis match
        if (analysisTemplateId) {
            const template = analysisTemplates.find((item) => item._id === analysisTemplateId);
            const analysis = {
                scanId: lastSavedScan._id,
                templateId: template._id,
                ...template
            }
            console.log('template', template);
            console.log('lastSavedScan', lastSavedScan);
            dispatch(saveAnalysis(analysis));
            navigate('/analyze/analyze-two', { replace: true });
        } else {
            setShowAlert(true);
        }
    };

    const handleCreateNew = () => {
        if (flowType.type === 'MANAGE_ANALYSIS_TEMPLATES') {
            navigate('/manage-templates/analysis-temps-two', { replace: true });
        } else {
            navigate('/analyze/analyze-four', { replace: true });
        }
    };

    const handleCopy = (selection) => {
        const copySelection = {
            id: selection.id,
            name: selection.name,
            notes: selection.notes,
            product: selection.id,
            date: selection.date.toISOString(),
            selectedWells: [...selection.scanProtocolArgs.wells]
        };

        dispatch(setSelectedTemplate(copySelection));

        if (flowType.type === 'MANAGE_ANALYSIS_TEMPLATES') {
            navigate('/manage-templates/analysis-temps-two', { replace: true });
        } else {
            navigate('/analyze/analyze-four', { replace: true });
        }
    };

    const handleExport = (selection) => {
        const exportSelection = {
            id: selection.id,
            name: selection.name,
            notes: selection.notes,
            product: selection.kit,
            date: selection.date.toISOString(),
            selectedWells: [...selection.scanProtocolArgs.wells]
        };

        window.api.exportData(exportSelection);
    };

    const handleImport = async () => {
        window.api.importData();
        await window.api.importDataComplete((data) => {
            console.log('import data', data);

            if (data.status === 'OK') {
                // TODO: if successful we need to refetch the table data so that we have the uploaded file available
                setShowUploadAlert({ show: true, status: 'success', message: 'Import Successful' });
            } else if (data.status === 'ERROR') {
                setShowUploadAlert({ show: true, status: 'error', message: 'Import Failed' });
            }
        });
    };

    const analysisPagination = usePagination(analysisData, {
        state: {
            page: 0,
            size: 8
        }
    });

    const getTableHeaderCellText = (content) => (<Text className={classes.tableHeaderCellText}>{content}</Text>);

    const renderTableHeaders = () => (
        <Header className={`${classes.tableHeaderRow} thead`}>
            <HeaderRow style={{ backgroundColor: 'transparent' }}>
                {flowType.type !== 'MANAGE_ANALYSIS_TEMPLATES' && <HeaderCell stiff>{getTableHeaderCellText('Select')}</HeaderCell>}
                <HeaderCellSort sortKey="NAME">{getTableHeaderCellText('Name of Analysis')}</HeaderCellSort>
                <HeaderCell>{getTableHeaderCellText('Analysis Notes')}</HeaderCell>
                <HeaderCellSort sortKey="DATE">{getTableHeaderCellText('Date')}</HeaderCellSort>
                <HeaderCell>{getTableHeaderCellText('Product/Kit')}</HeaderCell>
                <HeaderCell stiff>{getTableHeaderCellText('Copy')}</HeaderCell>
                <HeaderCell stiff>{getTableHeaderCellText('Export')}</HeaderCell>
            </HeaderRow>
        </Header>
    )

    return (
        <>
            <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
                {/* Group at position start in AppShellHeader component with title prop */}
                <Group position="end">
                    <Button className={classes.secondaryNavigationButton} variant="default" leftIcon={<ArrowLeft size={18} />} onClick={() => navigate('/', { replace: true })}>
                        Back
                    </Button>

                    {flowType.type !== 'MANAGE_ANALYSIS_TEMPLATES' && (
                        <Button
                            type="button"
                            className={classes.navigationButton}
                            rightIcon={<ArrowRight size={18} />}
                            onClick={() => selectAndAnalyze()}
                            disabled={analysisSelect.state.id === null}
                        >
                            Analyze
                        </Button>
                    )}
                </Group>
            </AppShellHeader>
            <div className={classes.appBackground}>
                <Box className={classes.tableBox}>
                    {showAlert && (
                        <Alert icon={<AlertCircle size={16} />} title="ERROR" color="red" withCloseButton onClose={() => setShowAlert(false)} mb={25}>
                            Your analysis template does not match your scan. Please make the appropriate selection to run analysis.
                        </Alert>
                    )}

                    {showUploadAlert.show === true && (
                        <>
                            {showUploadAlert.status === 'success' && (
                                <Alert icon={<AlertCircle size={16} />} title={showUploadAlert.message} color="green" withCloseButton onClose={() => setShowUploadAlert({ show: false })} mb={25} />
                            )}
                            {showUploadAlert.status === 'error' && (
                                <Alert icon={<AlertCircle size={16} />} title={showUploadAlert.message} color="red" withCloseButton onClose={() => setShowUploadAlert({ show: false })} mb={25} />
                            )}
                        </>
                    )}

                    {/* Analysis Templates */}
                    <Text  className={classes.title} size="sm" mt={20}>Analysis Templates</Text>
                    {flowType.type === 'MANAGE_ANALYSIS_TEMPLATES'
                        ? <Text className={classes.text}>To preview the “Plate Map & Concentration” and “Notes,” please click on a row to expand the view.</Text>
                        : <Text className={classes.text}>Create, upload, or, copy and modify an analysis template. You also have the option to select an existing analysis template and analyze without modifying.</Text>}

                    <Paper mt={30} mb={50} style={{ padding: 35 }}>
                        <Group position="apart" mb={30}>
                            <TextInput
                                placeholder="Search"
                                onChange={(e) => handleSearch(e, 'templates')}
                                sx={{ flexGrow: 1 }}
                            />
                            <Box>
                                <Button radius="xl" mr={15} onClick={() => handleImport()}>Upload</Button>
                                <Button radius="xl" onClick={() => handleCreateNew()}>Create New</Button>
                            </Box>
                        </Group>

                        <Table data={analysisData} sort={analysisSort} select={analysisSelect}
                            theme={{
                                ...theme,
                                Row: ''
                            }}
                            pagination={analysisPagination} style={{ minHeight: 435 }}>
                            {(tableList) => (
                                <>
                                    {renderTableHeaders()}
                                    <Body className={classes.tableRow}>
                                        {tableList.map((item) => (
                                            <React.Fragment key={`templatesTable-${item._id}`}>
                                                <Row item={item} onClick={() => toggleCollapse(item._id, 'templates')}>
                                                    {flowType.type !== 'MANAGE_ANALYSIS_TEMPLATES' && (
                                                        <Cell item={item}>
                                                            <Checkbox
                                                                checked={analysisSelect.state.id === item._id}
                                                                onChange={() => analysisSelect.fns.onToggleByIdExclusively(item._id)}
                                                                color="green"
                                                                radius="xl"
                                                            />
                                                        </Cell>
                                                    )}
                                                    <Cell style={{ maxWidth: 15 }}>
                                                        <Highlight className={classes.tableRowCellText} highlight={search.templates}>{item.name}</Highlight>
                                                    </Cell>
                                                    <Cell style={{ maxWidth: 15 }}>
                                                        <Highlight className={classes.tableRowCellText} highlight={search.templates}>{item?.notes}</Highlight>
                                                    </Cell>
                                                    <Cell>
                                                        <Highlight className={classes.tableRowCellText} highlight={search.templates}>{createReadableDate(item?.createdOn)}</Highlight>
                                                    </Cell>
                                                    <Cell>
                                                        <Highlight className={classes.tableRowCellText} highlight={search.templates}>{item?.productName}</Highlight>
                                                    </Cell>
                                                    <Cell>
                                                        <UnstyledButton
                                                            onClick={() => handleCopy(item)}
                                                            sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}
                                                        >
                                                            <Copy size={18} />
                                                        </UnstyledButton>
                                                    </Cell>
                                                    <Cell>
                                                        <UnstyledButton
                                                            onClick={() => handleExport(item)}
                                                            sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}
                                                        >
                                                            <FileExport size={18} />
                                                        </UnstyledButton>
                                                    </Cell>
                                                </Row>
                                                <Collapse in={collapse.templates.id === item._id} key={`templates-${collapse.templates.id}${item._id}`}>
                                                    <div className={`${classes.tablePaper} ${classes.noRadiusForDark}`} style={{ padding: '25px 50px' }}>
                                                        <Grid grow="true" align="stretch">
                                                            <Grid.Col span={6}>
                                                                <Text size="sm" weight={700} mb={10}>Notes:</Text>
                                                                <Paper style={{ minHeight: 420, padding: '30px 20px' }}>
                                                                    {item?.notes}
                                                                </Paper>
                                                            </Grid.Col>
                                                            <Grid.Col span={6}>
                                                                <Text size="sm" weight={700} mb={10}>Preview:</Text>
                                                                <Paper style={{ minHeight: 420, padding: '30px 20px' }}>
                                                                    <Card withBorder style={{ maxWidth: 430 }}>
                                                                        <WellPlateMini wells={item?.protocolArgs?.wells} />
                                                                    </Card>
                                                                </Paper>
                                                            </Grid.Col>
                                                        </Grid>
                                                    </div>
                                                </Collapse>
                                            </React.Fragment>
                                        ))}
                                    </Body>
                                </>
                            )}
                        </Table>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', margin: '25px 0' }}>
                            <Pagination
                                total={analysisPagination.state.getTotalPages(analysisData.nodes)}
                                page={analysisPagination.state.page + 1}
                                onChange={(page) => analysisPagination.fns.onSetPage(page - 1)}
                            />
                        </div>
                    </Paper>
                </Box>
            </div>
        </>
    );
}
