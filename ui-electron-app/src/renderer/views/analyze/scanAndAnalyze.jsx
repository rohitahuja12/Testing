import React, { useState, useEffect } from 'react';
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
  Tooltip,
  Popover,
  Box
} from '@mantine/core';
import {
  ArrowLeft,
  ArrowRight,
  ArrowsSort,
  SortAscending,
  SortDescending,
  AlertCircle
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
import { AppShellHeader } from '../../components/AppShellHeader.jsx';
import { createReadableDate } from '../../../lib/util/createReadableDate.js';
import { WellPlateMini } from '../../components/WellPlateMini.jsx';
import { getScan, getScans, getScansWithoutWellData } from '../../actions/scanActions.js';
import { useDispatch, useSelector } from 'react-redux';
import { getAnalysisTemplate, getAnalysisTemplates, saveAnalysis } from '../../actions/analysisTemplateActions.js';
import { analysisSelector, clearLoadedAnalysisTemplate } from '../../features/analysis/analysisSlice.js';
import { clearLastSavedScan, scanSelector } from '../../features/scan/scanSlice.js';
import { getWellsFromAnalysis, getWellsFromScan } from '../../utils/wellUtils.js';
import { BBLoader } from '../../components/brightestBio/BBLoader.jsx';
import { useAppStyles } from '../../styles/appStyles.js';

// # Analyze Scan Page

const useStyles = createStyles(useAppStyles);

export default function ScanAndAnalyze({ ...props }) {

  const dispatch = useDispatch();
  const scans = useSelector((state) => (state ?.scan ?.scans)) || [];
  const loadedScan = useSelector((state) => (state ?.scan ?.lastSavedScan))
  const loadedAnalysisTemplate = useSelector((state) => (state ?.analysis ?.loadedAnalysisTemplate))
  const [filteredScans, setFilteredScans] = useState({ nodes: [] });
  const [filteredTemplates, setFilteredTemplates] = useState({ nodes: [] });
  const analysisTemplates = useSelector(analysisSelector) ?.analysisTemplates;
  const [search, setSearch] = useState({ scans: '', templates: '' });
  const [collapse, setCollapse] = useState({ scans: { _id: null }, templates: { id: null } });
  const [showAlert, setShowAlert] = useState(false);
  const { classes, cx } = useStyles();
  const mantineTheme = getTheme(DEFAULT_OPTIONS);
  const theme = useTheme(mantineTheme);
  const navigate = useNavigate();
  const { lastScanUpdate } = useSelector(scanSelector)

  useEffect(() => {
    console.log('this should only run once to get all the data')
    dispatch(getScansWithoutWellData());
    dispatch(getAnalysisTemplates(['protocolArgs']));
  }, []);

  useEffect(() => { // websocket has updated scan, refresh
    if (lastScanUpdate) {
      console.log('getting all the data');
      dispatch(getScansWithoutWellData());
    }
  }, [lastScanUpdate])

  useEffect(() => {
    if (scans && scans.length > 0) {
      setFilteredScans({
        nodes: scans ?.filter((item) => (
          item ?.name ?.toLowerCase().includes(search ?.scans ?.toLowerCase())
            || item ?.productId ?.toLowerCase().includes(search ?.scans ?.toLowerCase())
        ))
      });
    }
  }, [scans, search.scans]);

  useEffect(() => {
    if (analysisTemplates && analysisTemplates.length > 0) {
      setFilteredTemplates({
        nodes: analysisTemplates ?.filter((item) => (
          item ?.name ?.toLowerCase().includes(search ?.templates ?.toLowerCase())
            || item ?.protocolArgs ?.notes ?.toLowerCase().includes(search ?.templates ?.toLowerCase())
              || item ?.productId ?.toLowerCase().includes(search ?.templates ?.toLowerCase())
        ))
      });
    }
  }, [analysisTemplates, search.templates]);

  useEffect(() => {
    if (collapse ?.scans ?._id) {
      dispatch(getScan(collapse ?.scans ?._id));
    } else if (collapse ?.templates ?._id) {
      dispatch(getAnalysisTemplate(collapse ?.templates ?._id));
    }

    if (!collapse ?.scans ?._id) {
      dispatch(clearLastSavedScan());
    } else if (!collapse ?.templates ?._id) {
      dispatch(clearLoadedAnalysisTemplate())
    }
  }, [collapse])

  const handleSearch = (event, key) => {
    setSearch({ ...search, [key]: event.target.value });
  };

  const onSortChange = (action, state) => {
    console.log(action, state);
  };

  const toggleCollapse = (id, key) => {
    setCollapse({ ...collapse, [key]: { _id: id === collapse[key]._id ? null : id } });
  };

  const sortOnChangeProps = { onChange: onSortChange };
  const sortProps = {
    sortIcon: {
      iconDefault: <ArrowsSort color="black" fillOpacity={0} />,
      iconUp: <SortAscending color="black" fillOpacity={0} />,
      iconDown: <SortDescending color="black" fillOpacity={0} />
    },
    sortFns: {
      NAME: (array) => array.sort((a, b) => a.name - b.name),
      DATE: (array) => array.sort((a, b) => a.createdOn - b.createdOn)
    }
  };
  const scanSort = useSort(filteredScans, sortOnChangeProps, sortProps);
  const analysisSort = useSort(filteredTemplates, sortOnChangeProps, sortProps);

  const onSelectChange = (action, state) => {
    console.log(action, state);
  };

  const scanSelect = useRowSelect(
    filteredScans,
    { onChange: onSelectChange },
    {
      buttonSelect: SelectTypes.SingleSelect,
      clickType: SelectClickTypes.ButtonClick
    }
  );

  const analysisSelect = useRowSelect(
    filteredTemplates,
    { onChange: onSelectChange },
    {
      buttonSelect: SelectTypes.SingleSelect,
      clickType: SelectClickTypes.ButtonClick
    }
  );

  const handleAnalyzeClick = () => {
    const selectedScanId = scanSelect.state.id;
    const selectedTemplateId = analysisSelect.state.id;

    if (selectedScanId && selectedTemplateId) {
      const template = analysisTemplates.find((item) => item._id === selectedTemplateId);
      const analysis = {
        scanId: selectedScanId,
        templateId: template._id,
        // _id: undefined, // don't copy template's _id
      }
      dispatch(saveAnalysis(analysis));
      navigate(`/analyze/analyze-two`);
    } else {
      setShowAlert(true);
    }
  };

  const defaultPaginationProps = {
    state: {
      page: 0,
      size: 8
    }
  };
  const scanPagination = usePagination(filteredScans, defaultPaginationProps);
  const analysisPagination = usePagination(filteredTemplates, defaultPaginationProps);

  const renderScanPlateMini = (scan) => {
    if (scan ?.protocolArgs) {
      console.log('rendering a mini plate');
      const wells = getWellsFromScan(scan);
      return (<WellPlateMini wells={wells} />);
    }

  }
  const getTableHeaderCellText = (content) => (<Text className={classes.tableHeaderCellText}>{content}</Text>);

  return (
    <>
      <AppShellHeader className={classes.mainHeader} screenTitle={props.screenTitle}>
        <Group position="end">
          <Button variant="default" leftIcon={<ArrowLeft size={18} />} onClick={() => navigate('/', { replace: true })}>
            Dashboard
          </Button>

          <Button
            type="button"
            color="dark"
            rightIcon={<ArrowRight size={18} />}
            onClick={() => handleAnalyzeClick()}
            disabled={(scanSelect.state.id === null) || (analysisSelect.state.id === null)}
          >
            Analyze
          </Button>
        </Group>
      </AppShellHeader>

      {/* <ScrollArea style={{ height: '91vh', padding: '30px 40px 0 40px' }}> */}
      <div className={classes.appBackground}>
        {showAlert && (
          <Alert icon={<AlertCircle size={16} />} title="ERROR" color="red" withCloseButton onClose={() => setShowAlert(false)} mb={25}>
            Your analysis template does not match your scan. Please make the appropriate selection to run analysis.
          </Alert>
        )}


        <div className={`${classes.tableBox} ${classes.commandHeader}`}>
          <Text size="sm" weight={700} className={classes.title}>Select Scan</Text>
          <Text size="sm" className={classes.text}>Select a scan that you want to apply an analysis template to analyze the results.</Text>
        </div>

        <Box className={classes.tableBox}>
          <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
            <TextInput
              placeholder="Search"
              onChange={(e) => handleSearch(e, 'scans')}
              mb={30}
            />

            <Table
              data={filteredScans}
              sort={scanSort}
              select={scanSelect}
              theme={{
                ...theme,
                Row: ''
              }}
              pagination={scanPagination}
              style={{ minHeight: 435 }}
            >
              {(tableList) => (
                <>
                  <Header className={`${classes.tableHeaderRow} thead`}>
                    <HeaderRow style={{ backgroundColor: 'transparent' }}>
                      <HeaderCell stiff>{getTableHeaderCellText('Select')}</HeaderCell>
                      <HeaderCellSort style={{ stroke: 'white' }} sortKey="NAME">{getTableHeaderCellText('Name of Scan')}</HeaderCellSort>
                      <HeaderCell>{getTableHeaderCellText('Scan Notes')}</HeaderCell>
                      <HeaderCellSort style={{ stroke: 'white' }} sortKey="DATE">{getTableHeaderCellText('Date')}</HeaderCellSort>
                      <HeaderCell>{getTableHeaderCellText('Product')}</HeaderCell>
                    </HeaderRow>
                  </Header>

                  <Body className={classes.tableRow}>
                    {tableList.map((item) => (
                      <React.Fragment key={`scansTable-${item._id}`}>
                        <Row className={classes.tableRow} item={item} onClick={() => {
                          toggleCollapse(item._id, 'scans');
                        }}>
                          <Cell item={item}>
                            <Checkbox
                              checked={scanSelect.state.id === item._id}
                              onChange={() => scanSelect.fns.onToggleByIdExclusively(item._id)}
                              color="green"
                              radius="xl"
                              disabled={item ?.status ?.toLowerCase() !== 'complete'}
                            />
                          </Cell>
                          <Cell>
                            <Highlight className={classes.tableRowCellText} highlight={search ?.scans}>{item ?.name || ""}</Highlight>
                          </Cell>
                          <Cell>
                            <Highlight className={classes.tableRowCellText} highlight={search ?.scans}>{item ?.protocolArgs ?.notes || ""}</Highlight>
                          </Cell>
                          <Cell>
                            <Text className={classes.tableRowCellText}>{createReadableDate(item ?.createdOn || "")}</Text>
                          </Cell>
                          <Cell>
                            <Highlight className={classes.tableRowCellText} highlight={search ?.scans}>{item ?.productId || ""}</Highlight>
                          </Cell>
                        </Row>

                        <Collapse in={collapse.scans._id === item._id} key={`scans-${collapse.scans._id}${item._id}`}>
                          <div className="collapse" style={{ backgroundColor: 'var(--gray-1)' }}>
                            <Paper className={`${classes.tablePaper} ${classes.noRadiusForDark}`} mt={20} mb={20}>
                              {loadedScan && collapse.scans._id === item._id
                                ? <Grid grow="true" align="stretch">
                                  <Grid.Col span={6}>
                                    <Text size="sm" weight={700} mb={10}>Notes:</Text>
                                    <Paper style={{ minHeight: 337, padding: '30px 20px' }}>
                                      {loadedScan ?.protocolArgs ?.notes}
                                    </Paper>
                                  </Grid.Col>
                                  <Grid.Col span={6}>
                                    <Text size="sm" weight={700} mb={10}>Preview:</Text>
                                    <Paper style={{ minHeight: 337, padding: '30px 20px' }}>
                                      <Text size="sm" weight={700} mb={10}>{loadedScan ?.productId}</Text>

                                      <Card withBorder style={{ maxWidth: 430 }}>
                                        {renderScanPlateMini(loadedScan)}
                                      </Card>
                                    </Paper>
                                  </Grid.Col>
                                </Grid>
                                : <Paper sx={{ textAlign: 'center' }} mt={20} mb={20}><BBLoader size='md' duration={1} /></Paper>
                              }
                            </Paper>

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
                total={scanPagination.state.getTotalPages(filteredScans.nodes)}
                page={scanPagination.state.page + 1}
                onChange={(page) => scanPagination.fns.onSetPage(page - 1)}
              />
            </div>
          </Paper>
        </Box>

        {/* Analysis Templates */}
        <div className={`${classes.tableBox} ${classes.commandHeader}`}>
          <Text className={classes.title} weight={700}>Select Analysis Template</Text>
          <Text className={classes.text}>Select an analysis template to apply to the scan selected above to analyze the results.</Text>
        </div>


        <Box className={classes.tableBox}>
          <Paper mt={30} mb={50} className={classes.tablePaper} style={{ padding: 35 }}>
            <TextInput
              placeholder="Search"
              onChange={(e) => handleSearch(e, 'templates')}
              mb={30}
            />

            <Table
              data={filteredTemplates} sort={analysisSort}
              select={analysisSelect}
              pagination={analysisPagination} style={{ minHeight: 435 }}
              theme={{
                ...theme,
                Row: ''
              }}
            >
              {(tableList) => (
                <>
                  <Header className={`${classes.tableHeaderRow} thead`}>
                    <HeaderRow style={{ backgroundColor: 'transparent' }}>
                      <HeaderCell stiff>{getTableHeaderCellText('Select')}</HeaderCell>
                      <HeaderCellSort style={{ stroke: 'white' }} sortKey="NAME">{getTableHeaderCellText('Name of Analysis')}</HeaderCellSort>
                      <HeaderCell>{getTableHeaderCellText('Analysis Notes')}</HeaderCell>
                      <HeaderCellSort style={{ stroke: 'white' }} sortKey="DATE">{getTableHeaderCellText('Date')}</HeaderCellSort>
                      <HeaderCell>{getTableHeaderCellText('Product/Kit')}</HeaderCell>
                    </HeaderRow>
                  </Header>

                  <Body className={classes.tableRow}>
                    {tableList.map((item) => (
                      <React.Fragment key={`templatesTable-${item._id}`}>
                        <Row className={classes.tableRow} item={item} onClick={() => toggleCollapse(item._id, 'templates')}>
                          <Cell item={item}>
                            <Checkbox
                              checked={analysisSelect.state.id === item._id}
                              onChange={() => analysisSelect.fns.onToggleByIdExclusively(item._id)}
                              color="green"
                              radius="xl"
                            />
                          </Cell>
                          <Cell>
                            <Highlight className={classes.tableRowCellText} highlight={search.templates}>{item.name}</Highlight>
                          </Cell>
                          <Cell>
                            <Highlight className={classes.tableRowCellText} highlight={search.templates}>{item ?.protocolArgs ?.notes}</Highlight>
                          </Cell>
                          <Cell>
                            <Text className={classes.tableRowCellText}>{createReadableDate(item.createdOn)}</Text>
                          </Cell>
                          <Cell>
                            <Highlight className={classes.tableRowCellText} highlight={search.templates}>{item ?.productName}</Highlight>
                          </Cell>
                        </Row>
                        <Collapse in={collapse.templates._id === item._id} key={`templates-${collapse.templates._id}${item._id}`}>
                          <div className="collapse" style={{ padding: '25px 50px', backgroundColor: 'var(--gray-1)' }}>
                            {loadedAnalysisTemplate && collapse ?.templates ?._id === item._id
                              ? <Grid grow="true" align="stretch">
                                <Grid.Col span={6}>
                                  <Text size="sm" weight={700} mb={10}>Notes:</Text>
                                  <Paper style={{ minHeight: 337, padding: '30px 20px' }}>
                                    {loadedAnalysisTemplate ?.protocolArgs ?.notes}
                                  </Paper>
                                </Grid.Col>
                                <Grid.Col span={6}>
                                  <Text size="sm" weight={700} mb={10}>Preview:</Text>
                                  <Paper style={{ minHeight: 337, padding: '30px 20px' }}>
                                    <Card withBorder style={{ maxWidth: 430 }}>
                                      <WellPlateMini wells={getWellsFromAnalysis(loadedAnalysisTemplate)} />
                                    </Card>
                                  </Paper>
                                </Grid.Col>
                              </Grid>
                              : <Paper sx={{ textAlign: 'center' }} mt={20} mb={20}><BBLoader size='md' duration={1} /></Paper>
                            }
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
                total={analysisPagination.state.getTotalPages(filteredTemplates.nodes)}
                page={analysisPagination.state.page + 1}
                onChange={(page) => analysisPagination.fns.onSetPage(page - 1)}
              />
            </div>
          </Paper>
        </Box>

        {/* </ScrollArea> */}
      </div>
    </>
  );
}
