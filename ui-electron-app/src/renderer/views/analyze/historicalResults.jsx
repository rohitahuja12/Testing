import React, { useState, useEffect } from 'react';
import {
    createStyles,
    Text,
    Button,
    Paper,
    Box,
    Grid,
    Image,
    UnstyledButton,
    Collapse,
    Pagination,
    Loader,
    Highlight,
    TextInput
} from '@mantine/core';
import {
    Table,
    Header,
    HeaderRow,
    HeaderCell,
    Body,
    Row,
    Cell
} from '@table-library/react-table-library/table';
import {
    ArrowsSort,
    SortAscending,
    SortDescending,
    FileExport,
    Copy,
    FileX
} from 'tabler-icons-react';
import { useTheme } from '@table-library/react-table-library/theme';
import {
    DEFAULT_OPTIONS,
    getTheme
} from '@table-library/react-table-library/mantine';
import { useSort, HeaderCellSort } from '@table-library/react-table-library/sort';
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { getAnalysesWithoutWellData, getAttachments } from '../../actions/analysisTemplateActions.js';
import { createReadableDate } from '../../../lib/util/createReadableDate.js';
import { analysisSelector, clearAnalysisImages } from '../../features/analysis/analysisSlice.js';
import { usePagination } from '@table-library/react-table-library/pagination';
import { BBLoader } from '../../components/brightestBio/BBLoader.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

// View Results Page

const useStyles = createStyles(useAppStyles);

export default function HistoricalResults({ ...props }) {
    const navigate = useNavigate();
    const { classes, cx } = useStyles();
    const mantineTheme = getTheme(DEFAULT_OPTIONS);
    const theme = useTheme(mantineTheme);
    const dispatch = useDispatch();
    const analysesWithoutWellData = useSelector(analysisSelector)?.analyses
    const { analysisImages } = useSelector(state => state?.analysis);
    const [collapse, setCollapse] = useState({ analyses: { id: null } });
    const [search, setSearch] = useState({ analyses: '' });
    const [filteredAnalyses, setFilteredAnalyses] = useState({ nodes: [] });


    const toggleCollapse = (id, key) => {
        if (id === collapse[key].id) {
            // clear images, close collapse
            dispatch(clearAnalysisImages());
        }
        setCollapse({ ...collapse, [key]: { id: id === collapse[key].id ? null : id } });
    };
    const onSort = (action, state) => { console.log(action, state); }
    const tableSort = useSort(
        filteredAnalyses,
        { onChange: onSort },
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
    const tablePagination = usePagination(filteredAnalyses, { state: { page: 0, size: 8 } });

    useEffect(() => {
        if (collapse?.analyses?.id) {
            dispatch(getAttachments(collapse?.analyses?.id));
        }
    }, [collapse])

    useEffect(() => {
        dispatch(getAnalysesWithoutWellData());
    }, []);

    useEffect(() => {
        if (analysesWithoutWellData) {
            setFilteredAnalyses({
                nodes: analysesWithoutWellData?.filter((item) => (
                    item?.name?.toLowerCase().includes(search?.analyses?.toLowerCase())
                    || item?.productId?.toLowerCase().includes(search?.analyses?.toLowerCase())
                    || item?.productName?.toLowerCase().includes(search?.analyses?.toLowerCase())
                ))
            });
        }
    }, [analysesWithoutWellData, search.analyses]);

    const handleSearch = (event, key) => {
        setSearch({ ...search, [key]: event.target.value });
    };
    const getTableHeaderCellText = (content) => (<Text className={classes.tableHeaderCellText}>{content}</Text>);

    const renderTableHeaders = () => (
        <Header className={`${classes.tableHeaderRow} thead`}>
            <HeaderRow style={{ backgroundColor: 'transparent' }}>
                <HeaderCellSort style={{ stroke: 'white' }} sortKey="NAME">{getTableHeaderCellText('Name')}</HeaderCellSort>
                <HeaderCellSort sortKey="DATE">{getTableHeaderCellText('Date')}</HeaderCellSort>
                <HeaderCell>{getTableHeaderCellText('Product/Kit')}</HeaderCell>
                <HeaderCell stiff>{getTableHeaderCellText('Copy')}</HeaderCell>
                <HeaderCell stiff>{getTableHeaderCellText('Export')}</HeaderCell>
            </HeaderRow>
        </Header >
    );

    const renderAnalysisImagesGrid = () => {
        if (analysisImages && analysisImages.length > 0) {
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
        } else if (analysisImages === null) {
            return <BBLoader size='md' />
        } else {
            return <Text>No attachments found</Text>
        }
    }

    const renderTableBody = (tableList) => {
        return (tableList.map((item) => (
            <React.Fragment key={item._id}>
                <Row className={classes.tableRow} item={item} onClick={() => toggleCollapse(item._id, 'analyses')}>
                    {/* name */}
                    <Cell>
                        <Highlight className={classes.tableRowCellText} highlight={search?.analyses}>{item?.name || ""}</Highlight>
                    </Cell>
                    {/* date */}
                    <Cell>
                        <Highlight className={classes.tableRowCellText} highlight={search?.analyses}>{createReadableDate(item?.createdOn) || ""}</Highlight>
                    </Cell>
                    {/* product */}
                    <Cell>
                        <Highlight className={classes.tableRowCellText} highlight={search?.analyses}>{item?.productName || ""}</Highlight>
                    </Cell>
                    {/* copy */}
                    <Cell>
                        <UnstyledButton
                            onClick={() => handleCopy(item)}
                            sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}
                        >
                            <Copy size={18} />
                        </UnstyledButton>
                    </Cell>
                    {/* export */}
                    <Cell>
                        <UnstyledButton
                            onClick={() => handleExport(item)}
                            sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}
                        >
                            <FileExport size={18} />
                        </UnstyledButton>
                    </Cell>
                </Row>
                <Collapse in={collapse.analyses.id === item._id} key={`analyses-${collapse.analyses.id}${item._id}`}>
                    <div className="collapse" style={{ backgroundColor: 'var(--gray-1)', textAlign: 'center' }}>
                        <Paper className={`${classes.tablePaper} ${classes.noRadiusForDark}`} mt={20} mb={20}>
                            {renderAnalysisImagesGrid()}
                        </Paper>
                    </div>
                </Collapse>
            </React.Fragment>
        )))
    }

    return (
        <>
            <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
                <Button
                    type="button"
                    className={classes.secondaryNavigationButton}
                    onClick={() => { navigate('/') }}
                >
                    Dashboard
                </Button>
            </AppShellHeader>

            <div className={classes.appBackground}>
                <Box className={classes.tableBox}>
                    <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
                        <TextInput
                            placeholder="Search"
                            onChange={(e) => handleSearch(e, 'analyses')}
                            mb={30}
                        />
                        {analysesWithoutWellData && analysesWithoutWellData.length > 0 && <Table
                            data={filteredAnalyses}
                            style={{ minHeight: 435 }}
                            sort={tableSort}
                            theme={{
                                ...theme,
                                Row: ''
                            }}
                            pagination={tablePagination}
                        >
                            {/* {console.log('theme', theme)} */}
                            {(tableList) => (
                                <>
                                    {renderTableHeaders()}
                                    <Body className={classes.tableRow}>
                                        {renderTableBody(tableList)}
                                    </Body>
                                </>
                            )}
                        </Table>}
                        {analysesWithoutWellData
                            && analysesWithoutWellData.length > 0
                            && <div style={{ display: 'flex', justifyContent: 'flex-end', margin: '25px 0' }}>
                                <Pagination
                                    total={tablePagination.state.getTotalPages(filteredAnalyses?.nodes)}
                                    page={tablePagination.state.page + 1}
                                    onChange={(page) => tablePagination.fns.onSetPage(page - 1)}
                                />
                            </div>}
                    </Paper>
                </Box>
                <Box className={classes.tableBox}>
                    <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
                        <TextInput
                            placeholder="Search"
                            onChange={(e) => handleSearch(e, 'analyses')}
                            mb={30}
                        />
                        {analysesWithoutWellData && analysesWithoutWellData.length > 0 && <Table
                            data={filteredAnalyses}
                            style={{ minHeight: 435 }}
                            sort={tableSort}
                            theme={{
                                ...theme,
                                Row: ''
                            }}
                            pagination={tablePagination}
                        >
                            {/* {console.log('theme', theme)} */}
                            {(tableList) => (
                                <>
                                    {renderTableHeaders()}
                                    <Body className={classes.tableRow}>
                                        {renderTableBody(tableList)}
                                    </Body>
                                </>
                            )}
                        </Table>}
                        {analysesWithoutWellData
                            && analysesWithoutWellData.length > 0
                            && <div style={{ display: 'flex', justifyContent: 'flex-end', margin: '25px 0' }}>
                                <Pagination
                                    total={tablePagination.state.getTotalPages(filteredAnalyses?.nodes)}
                                    page={tablePagination.state.page + 1}
                                    onChange={(page) => tablePagination.fns.onSetPage(page - 1)}
                                />
                            </div>}
                    </Paper>
                </Box>
            </div>

        </>
    );
}
