import React, { useState, useMemo, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Grid, Typography, Paper, Button, List, IconButton } from "@mui/material";
import { useNavigate, Navigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BBViewShell from "../BBViewShell";
import { useAnalysisTemplates } from "../hooks/useAnalysisTemplates";
import BBTable from "../reusable/BBTable";
import { createRow, createColumn } from "../utils/mui_tableHeaderSortHelper";
import DeleteIcon from "@mui/icons-material/Delete";
import BBViewScanModal from "../BBViewScanModal";
import BBViewAnalysisTemplateModal from "../BBViewAnalysisTemplateModal";
import { BBViewPageLoader } from "../BBViewPageLoader";
import SettingsIcon from '@mui/icons-material/Settings';
import ConfigureTableModal from "../ConfigureTableModal";

const storedColumnsJson = localStorage.getItem('analysis-template-columns')
const analysisTemplateColumns = storedColumnsJson ? JSON.parse(storedColumnsJson) : [
  createColumn("Name", "name", true),
  createColumn("Date", "date", true),
  createColumn("Product", "product", true),
  createColumn("Protocol", "protocol", true),
  { ...createColumn("Delete", "delete", false, true), preventConfiguration: true },
  // preventConfiguration prevents the user from being able to hide a column
];

/**
 *
 * @param {
 * screenTitle: string,
 * signOut: function
 * } props
 * @returns
 */
const BBViewAnalysisTemplates = (props) => {
  const navigate = useNavigate();
  const {
    analysisTemplates,
    deleteTemplate,
    loadedTemplate,
    getTemplate,
    clearTemplate,
  } = useAnalysisTemplates();
  const [rowsPerPage] = useState(6);
  const [templateOrderBy, setTemplateOrderBy] = useState("date");
  const [redirectToCreate, setRedirectToCreate] = useState(false);
  const [openViewTemplateModal, setOpenViewTemplateModal] = useState(false);
  const [showConfigureTableModal, setShowConfigureTableModal] = useState(false);
  const [columns, setColumns] = useState(analysisTemplateColumns);

  useEffect(() => {
    localStorage.setItem('analysis-template-columns', JSON.stringify(columns));
  }, [columns]);

  const analysisTemplateRows = useMemo(
    () =>
      analysisTemplates?.map((template) => ({
        id: createRow(template?._id),
        name: createRow(template?.name),
        date: createRow(new Date(template?.createdOn + "Z")),
        product: createRow(template?.productName),
        protocol: createRow(template?.protocol),
        productId: createRow(template?.productId),
        delete: {
          isAction: true,
          value: <DeleteIcon sx={{ fontSize: 16, cursor: "pointer" }} />,
          onClick: () => deleteTemplate(template?._id),
        },
      })),
    [analysisTemplates]
  );

  return (
    <BBViewShell alignItems="start" signOut={props?.signOut}>
      {redirectToCreate && <Navigate to="/analysis-template/create" />}
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
            {props?.screenTitle}
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
            <BBViewPageLoader loadingText="Loading Templates">
              <Grid container spacing={3}>
                <Grid
                  item
                  xs={12}
                  ml={5}
                  mr={5}
                  sx={{ display: "flex", justifyContent: "end" }}
                >
                  <IconButton aria-label="configure" onClick={() => {
                    setShowConfigureTableModal(true);
                  }}>
                    <SettingsIcon />
                  </IconButton>

                  <Button
                    onClick={() => {
                      setRedirectToCreate(true);
                    }}
                    color="secondary"
                    variant="outlined"
                  >
                    Create New
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <BBTable
                    columns={columns.filter((col) => !col?.hidden)}
                  rows={analysisTemplateRows}
                  orderBy={templateOrderBy}
                  setOrderBy={setTemplateOrderBy}
                  rowsPerPage={rowsPerPage}
                  onRowClick={(event, row) => {
                    if (row?.id?.value) {
                      getTemplate(row?.id?.value);
                      setOpenViewTemplateModal(true);
                    }
                  }}
                  tableLabel="Analysis Templates"
                  />
                </Grid>
              </Grid>
            </BBViewPageLoader>
          </Paper>
        </Grid>
      </Grid>
      <BBViewAnalysisTemplateModal
        open={openViewTemplateModal}
        onClose={() => {
          setOpenViewTemplateModal(false);
          clearTemplate();
        }}
        analysisTemplate={loadedTemplate}
      />
      <ConfigureTableModal
        open={showConfigureTableModal}
        onClose={() => setShowConfigureTableModal(false)}
        columns={columns}
        setColumns={setColumns}
      />
    </BBViewShell>
  );
};

export default BBViewAnalysisTemplates;
