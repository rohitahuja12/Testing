import React, { useState, useEffect, useMemo } from "react";
import {
  Grid as MUIGrid,
  Typography,
  Paper,
  IconButton,
  Button as MUIButton,
  TextField,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useNavigate, Navigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import {
  getAnalysesWithoutWellData,
  getAttachments,
  getFileUrl,
  deleteAnalysis,
} from "../../../actions/analysisTemplateActions.js";
import {
  analysisSelector,
  clearAnalysisImages,
} from "../../../features/analysis/analysisSlice.js";
import {
  showSnackbar,
  systemSelector,
} from "../../../features/system/systemSlice.js";
import BBViewShell from "../BBViewShell.jsx";
import BBViewResultModal from "../BBViewResultModal.jsx";
import BBTable from "../reusable/BBTable.jsx";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import DeleteIcon from "@mui/icons-material/Delete";
import { createColumn } from "../utils/mui_tableHeaderSortHelper.js";
import { BBViewPageLoader } from "../BBViewPageLoader.jsx";
import ConfigureTableModal from "../ConfigureTableModal.jsx";
import SettingsIcon from "@mui/icons-material/Settings";
import { downloadB64AsFile } from "../../../utils/fileUtils.js";

const storedColumnsJson = localStorage.getItem("analysis-columns");
const defaultColumns = [
  createColumn("Name", "name", true),
  createColumn("Date", "date", true),
  createColumn("Scan", "scanName", true),
  createColumn("Template", "templateName", true),
  createColumn("Product/Kit", "product", false),
  createColumn("Status", "status", true),
  {
    ...createColumn("Export", "export", false, true),
    preventConfiguration: true,
  },
  {
    ...createColumn("Delete", "delete", false, true),
    preventConfiguration: true,
  },
];
const analysisColumns =
  storedColumnsJson &&
  JSON.parse(storedColumnsJson).length === defaultColumns.length
    ? JSON.parse(storedColumnsJson)
    : defaultColumns;

/**
 *
 * @param {
 * screenTitle: string,
 * signOut: function
 * } props
 * @returns
 */
export default function ViewAnalyses({ ...props }) {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const analysesWithoutWellData = useSelector(analysisSelector)?.analyses;
  const { analysisImages, downloadFileUrl } = useSelector(
    (state) => state?.analysis
  );
  const [search, setSearch] = useState({ analyses: "" });
  const [filteredAnalyses, setFilteredAnalyses] = useState({ nodes: [] });
  const [redirectToCreate, setRedirectToCreate] = useState(false);
  const useMUIStyleSystem = useSelector(systemSelector)?.useMUIStyleSystem;
  const [orderBy, setOrderBy] = useState("date");
  const [rowsPerPage] = useState(6);
  const [openViewResultModal, setOpenViewResultModal] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);
  const [showConfigureTableModal, setShowConfigureTableModal] = useState(false);
  const [columns, setColumns] = useState(analysisColumns);
  const [downloadAnalysisObject, setDownloadAnalysisObject] = useState(null);

  useEffect(() => {
    dispatch(getAnalysesWithoutWellData());
  }, []);

  useEffect(() => {
    localStorage.setItem("analysis-columns", JSON.stringify(columns));
  }, [columns]);

  useEffect(() => {
    if (downloadAnalysisObject && downloadFileUrl) {
      downloadB64AsFile(
        `${downloadAnalysisObject?.name}-summary.zip`,
        downloadFileUrl
      );
      setDownloadAnalysisObject(null);
    }
  }, [downloadAnalysisObject, downloadFileUrl]);

  useEffect(() => {
    if (analysesWithoutWellData) {
      setFilteredAnalyses({
        nodes: analysesWithoutWellData
          ?.filter(
            (item) =>
              item?.name
                ?.toLowerCase()
                .includes(search?.analyses?.toLowerCase()) ||
              item?.productId
                ?.toLowerCase()
                .includes(search?.analyses?.toLowerCase()) ||
              item?.productName
                ?.toLowerCase()
                .includes(search?.analyses?.toLowerCase())
          )
          ?.sort((a, b) => {
            return (
              new Date(b.createdOn + "Z").getTime() -
              new Date(a.createdOn + "Z").getTime()
            );
          }),
      });
    }
  }, [analysesWithoutWellData, search.analyses]);

  const handleSearch = (event, key) => {
    setSearch({ ...search, [key]: event.target.value });
  };

  const handleCopy = () => {
    // TODO: copy to clipboard
  };

  const handleExport = (item) => {
    const status = item?.status?.value || item?.status;
    if (status !== "COMPLETE" && status !== "ERROR") {
      dispatch(
        showSnackbar({
          message: "Cannot export an incomplete analysis.",
          severity: "error",
        })
      );
      return;
    }
    const analysisId = item?.name?.value || item?.name;

    if (!downloadFileUrl) {
      dispatch(getAttachments(item?.id?.value || item?._id));
      setDownloadAnalysisObject({
        name: analysisId,
      });
      return;
    }

    downloadB64AsFile(`${analysisId}-summary.zip`, downloadFileUrl);
  };

  const handleDelete = (analysis) => {
    dispatch(deleteAnalysis(analysis._id));
  };
  const rows = useMemo(
    () =>
      filteredAnalyses?.nodes?.map((analysis) => {
        return {
          id: {
            isAction: false,
            value: analysis._id,
          },
          name: {
            isACtion: false,
            value: analysis.name,
          },
          date: {
            isAction: false,
            value: new Date(analysis.createdOn + "Z"),
          },
          product: {
            isAction: false,
            value: analysis.productName,
          },
          status: {
            isAction: false,
            value: analysis.status,
          },
          scanName: {
            isAction: false,
            value: analysis?.scanName,
          },
          templateName: {
            isAction: false,
            value: analysis?.templateName,
          },
          export: {
            isAction: true,
            value: (
              <FileDownloadIcon sx={{ fontSize: 16, cursor: "pointer" }} />
            ),
            onClick: () => handleExport(analysis),
          },
          delete: {
            isAction: true,
            value: <DeleteIcon sx={{ fontSize: 16, cursor: "pointer" }} />,
            onClick: () => handleDelete(analysis),
          },
        };
      }),
    [filteredAnalyses]
  );

  return (
    <>
      {
        <BBViewShell alignItems="start" signOut={props?.signOut}>
          {redirectToCreate && <Navigate to="/analyze/create" />}
          <MUIGrid container spacing={3}>
            <MUIGrid item xs={12}>
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
            </MUIGrid>
            <MUIGrid item xs={12}>
              <MUIButton
                color="secondary"
                variant="contained"
                onClick={() => {
                  navigate("/");
                }}
                sx={{ marginRight: 1 }}
              >
                <ArrowBackIcon sx={{ fontSize: 24 }} />
                Back to Dashboard
              </MUIButton>
            </MUIGrid>

            <MUIGrid item xs={12} mt={5}>
              <Paper>
                <BBViewPageLoader loadingText="Loading Analyses">
                  <MUIGrid container spacing={3}>
                    <MUIGrid
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

                      <MUIButton
                        onClick={() => {
                          setRedirectToCreate(true);
                        }}
                        color="secondary"
                        variant="outlined"
                      >
                        Create New
                      </MUIButton>
                    </MUIGrid>
                    <MUIGrid item xs={12}>
                      <BBTable
                        columns={columns.filter((col) => !col?.hidden)}
                        rows={rows}
                        orderBy={orderBy}
                        setOrderBy={setOrderBy}
                        rowsPerPage={rowsPerPage}
                        onRowClick={(event, row) => {
                          setOpenViewResultModal(true);
                          dispatch(getAttachments(row.id.value));
                          setSelectedResult(row);
                        }}
                        tableLabel="View Results"
                        showSearchBar={true}
                        onSearch={(e) => handleSearch(e, "analyses")}
                      />
                    </MUIGrid>
                  </MUIGrid>
                </BBViewPageLoader>
              </Paper>
            </MUIGrid>
          </MUIGrid>
          <BBViewResultModal
            images={analysisImages}
            result={selectedResult}
            onClose={() => {
              setOpenViewResultModal(false);
              dispatch(clearAnalysisImages());
            }}
            open={openViewResultModal}
            onExport={() => handleExport(selectedResult)}
          />
          <ConfigureTableModal
            open={showConfigureTableModal}
            onClose={() => setShowConfigureTableModal(false)}
            columns={columns}
            setColumns={setColumns}
          />
        </BBViewShell>
      }
    </>
  );
}
