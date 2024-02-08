import React, { useState, useMemo, useEffect } from "react";
import {
  deleteScan,
  getScan,
  getScanImages,
  getScansWithoutWellData,
} from "../../../actions/scanActions.js";
import { useDispatch, useSelector } from "react-redux";
import { createColumn, createRow } from "../utils/mui_tableHeaderSortHelper.js";
import BBViewShell from "../BBViewShell.jsx";
import { Grid, Typography, Paper, Button, IconButton } from "@mui/material";
import { useNavigate, useSearchParams, Navigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BBTable from "../reusable/BBTable.jsx";
import DeleteIcon from "@mui/icons-material/Delete";
import DownloadIcon from "@mui/icons-material/Download";
import BBViewScanModal from "../BBViewScanModal.jsx";
import { clearLastSavedScan } from "../../../features/scan/scanSlice.js";
import { BBViewPageLoader } from "../BBViewPageLoader.jsx";
import { Auth } from "aws-amplify";
import ConfigureTableModal from "../ConfigureTableModal.jsx";
import SettingsIcon from "@mui/icons-material/Settings";
import { httpResourceApiUrl } from "../../../api/client.js";
import { useFeatureFlags } from "../hooks/useFeatureFlags.js";
import { downloadB64AsFile } from "../../../utils/fileUtils.js";
import { showSnackbar } from "../../../features/system/systemSlice.js";

const defaultColumns = [
  createColumn("Name", "name", true),
  createColumn("ID", "id", true),
  createColumn("Date", "date", true),
  createColumn("Reader", "reader", true),
  createColumn("Status", "status", true),
  createColumn("Barcode", "barcode", true),
  {
    ...createColumn("Download", "download", false, true),
    preventConfiguration: true,
  },
  {
    ...createColumn("Delete", "delete", false, true),
    preventConfiguration: true,
  },
];

const storedColumnsJson = localStorage.getItem("scan-columns");
const scanColumns =
  storedColumnsJson &&
  JSON.parse(storedColumnsJson).length === defaultColumns.length
    ? JSON.parse(storedColumnsJson)
    : defaultColumns;

/**
 *
 * @param {{
 * screenTitle: string,
 * signOut: function
 * }} props
 */
const ViewScans = (props) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const scans = useSelector((state) => state?.scan?.scans) || [];
  const [filteredScans, setFilteredScans] = useState(scans || []);
  const [isBrightestBioDev, setIsBrightestBioDev] = useState(false);
  const [orderBy, setOrderBy] = useState("date");
  const [rowsPerPage] = useState(6);
  const [openViewScanModal, setOpenViewScanModal] = useState(false);
  const loadedScan = useSelector((state) => state?.scan?.lastSavedScan);
  const [searchParams, setSearchParams] = useSearchParams();
  const scanIdToLoadBySearchParam = searchParams.get("scan");
  const [redirectToCreateScan, setRedirectToCreateScan] = useState(false);
  const [showConfigureTableModal, setShowConfigureTableModal] = useState(false);
  const [columns, setColumns] = useState(scanColumns);
  const { checkFeatureFlag } = useFeatureFlags();
  const [downloadScanObject, setDownloadScanObject] = useState(null);
  const appIsLoadingData = useSelector(
    (
      /** @type {Store} */
      state
    ) => state?.system?.loadingData
  );
  const { downloadFileUrl } = useSelector((state) => state?.scan);

  useMemo(() => {
    dispatch(getScansWithoutWellData());
  }, [dispatch]);

  useEffect(() => {
    localStorage.setItem("scan-columns", JSON.stringify(columns));
  }, [columns]);

  useEffect(() => {
    if (downloadScanObject && downloadFileUrl) {
      downloadB64AsFile(
        `${downloadScanObject?.name}-summary.zip`,
        downloadFileUrl
      );
      setDownloadScanObject(null);
    }
  }, [downloadScanObject, downloadFileUrl]);

  useEffect(() => {
    setFilteredScans(scans);

    // Auth.currentAuthenticatedUser().then((user) => {
    //   if (user.attributes["custom:organization"].includes("Brightest Bio")
    //     && user.attributes["custom:group"].includes("devs")) {
    //     setIsBrightestBioDev(true);
    //   }
    // });
  }, [scans]);

  useEffect(() => {
    if (scanIdToLoadBySearchParam) {
      dispatch(getScan(scanIdToLoadBySearchParam));
      setOpenViewScanModal(true);
      // setSearchParams({ scan: null });
    }
  }, [scanIdToLoadBySearchParam, dispatch, setSearchParams]);

  const handleDelete = (scan) => {
    dispatch(deleteScan(scan?._id));
  };

  const handleDownload = (item) => {
    const scanName = item?.name?.value || item?.name;
    const status = item?.status?.value || item?.status;
    if (status !== "COMPLETE" && status !== "ERROR") {
      dispatch(
        showSnackbar({
          message: "Cannot export an incomplete scan.",
          severity: "error",
        })
      );
      return;
    }

    if (!downloadFileUrl) {
      dispatch(getScanImages(item?._id?.value || item?._id));
      setDownloadScanObject({
        name: scanName,
      });
      return;
    }

    downloadB64AsFile(`${scanName}-summary.zip`, downloadFileUrl);
  };

  const rows = useMemo(
    () =>
      filteredScans?.map((scan) => ({
        id: createRow(scan?._id),
        name: createRow(scan?.name),
        date: createRow(new Date(scan?.createdOn)),
        barcode: createRow(scan?.plateBarcode),
        reader: createRow(scan?.readerSerialNumber),
        status: createRow(scan?.status),
        download: {
          isAction: true,
          value: <DownloadIcon sx={{ fontSize: 16, cursor: "pointer" }} />,
          onClick: () => handleDownload(scan),
        },
        delete: {
          isAction: true,
          value: <DeleteIcon sx={{ fontSize: 16, cursor: "pointer" }} />,
          onClick: () => handleDelete(scan),
        },
      })),
    [filteredScans]
  );

  return (
    <BBViewShell alignItems="start" signOut={props?.signOut}>
      {redirectToCreateScan && <Navigate to="/scan/create" />}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography
            variant="h2"
            component="h1"
            mb={0}
            mt={5}
            color="textPrimary"
            gutterBottom
          >
            {props.screenTitle}
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Button
            color="secondary"
            variant="contained"
            onClick={() => {
              navigate("/");
            }}
            sx={{ marginRight: 1 }}
          >
            <ArrowBackIcon sx={{ fontSize: 24 }} />
            Back to Dashboard
          </Button>
        </Grid>
        <Grid item xs={12} mt={5}>
          <Paper>
            <BBViewPageLoader loadingText="Loading Scans">
              <Grid container spacing={3}>
                <Grid
                  item
                  xs={12}
                  ml={5}
                  mr={5}
                  sx={{ display: "flex", justifyContent: "end" }}
                >
                  <IconButton
                    aria-label="configure"
                    onClick={() => {
                      setShowConfigureTableModal(true);
                    }}
                  >
                    <SettingsIcon />
                  </IconButton>

                  <Button
                    onClick={() => {
                      setRedirectToCreateScan(true);
                    }}
                    color="secondary"
                    variant="outlined"
                  >
                    Create New
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <BBTable
                    columns={columns
                      .filter((col) => !col?.hidden)
                      .filter((col) => {
                        return (
                          col.label !== "Download" ||
                          checkFeatureFlag("scan-results-download")
                        );
                      })}
                    rows={rows}
                    orderBy={orderBy}
                    setOrderBy={setOrderBy}
                    rowsPerPage={rowsPerPage}
                    onRowClick={(event, row) => {
                      dispatch(getScan(row?.id?.value));
                      setOpenViewScanModal(true);
                    }}
                    tableLabel="View Scans"
                    // showSearchBar={true}
                    // onSearch={(e) => handleSearch(e, 'analyses')}
                  />
                </Grid>
              </Grid>
            </BBViewPageLoader>
          </Paper>
        </Grid>
      </Grid>
      <BBViewScanModal
        open={openViewScanModal}
        onClose={() => {
          dispatch(clearLastSavedScan());
          setOpenViewScanModal(false);
        }}
        scan={loadedScan}
      />
      <ConfigureTableModal
        open={showConfigureTableModal}
        onClose={() => {
          setShowConfigureTableModal(false);
        }}
        columns={columns}
        setColumns={setColumns}
      />
    </BBViewShell>
  );
};

export default ViewScans;

/**
 * @typedef {import('../../../store.js').Store} Store
 */
