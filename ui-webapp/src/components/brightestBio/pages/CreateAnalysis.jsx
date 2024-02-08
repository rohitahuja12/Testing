import React, { useState, useEffect, useMemo } from "react";
import BBViewShell from "../BBViewShell";
import { useAnalysisTemplates } from "../hooks/useAnalysisTemplates";
import { useScans } from "../hooks/useScans";
import { createColumn, createRow } from "../utils/mui_tableHeaderSortHelper";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import {
  Grid,
  Typography,
  Paper,
  Button,
  Stepper,
  Step,
  StepLabel,
  Box,
  Divider,
  TextField,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import BBTable from "../reusable/BBTable";
import { useSteps } from "../hooks/useSteps";
import { green, grey, yellow, blue } from "@mui/material/colors";
import { useCreateAnalysis } from "../hooks/useCreateAnalysis";
import LoopIcon from "@mui/icons-material/Loop";
import { Radio } from "@mui/material";
import BBViewScanModal from "../BBViewScanModal";
import { useDispatch, useSelector } from "react-redux";
import { getScan } from "../../../actions/scanActions";
import BBViewAnalysisTemplateModal from "../BBViewAnalysisTemplateModal";
import ReviewStep from "./createAnalysis/ReviewStep";

/**
 *
 * @param {
 * screenTitle: string
 * signout: function
 * } props
 * @returns
 */
const BBCreateAnalysis = ({ screenTitle, signOut }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { scans } = useScans();
  const { analysisTemplates, loadedTemplate, getTemplate, clearTemplate } =
    useAnalysisTemplates();
  const [rowsPerPage] = useState(6);
  const {
    analysis,
    setAnalysis,
    createAnalysis,
    analysisCreationInProgress,
    analysisCreationFailed,
  } = useCreateAnalysis();
  const loadedScan = useSelector((state) => state?.scan?.lastSavedScan);
  // ********* Steps *********
  const { activeStep, nextStep, prevStep, isLastStep, isFirstStep } =
    useSteps(4);
  const steps = useMemo(
    () => [
      { label: "Select Scan" },
      { label: "Select Template" },
      { label: "Name Analysis" },
      { label: "Review" },
    ],
    []
  );

  useEffect(() => {
    if (isLastStep) {
      getTemplate(analysis?.templateId);
      dispatch(getScan(analysis?.scanId));
    }
  }, [isLastStep, analysis]);

  // ********* Scans *********
  const [scanOrderBy, setScanOrderBy] = useState("date");
  const [openScanModal, setOpenScanModal] = useState(false);
  const [openTemplateModal, setOpenTemplateModal] = useState(false);
  const scanColumns = useMemo(
    () => [
      createColumn("", "select", false, true),
      createColumn("Name", "name", true),
      createColumn("Date", "date", true),
      createColumn("Reader", "reader", true),
      createColumn("Status", "status", true),
    ],
    []
  );
  const scanRows = useMemo(
    () =>
      scans?.map((scan) => ({
        id: createRow(scan?._id),
        name: createRow(scan?.name),
        date: createRow(new Date(scan?.createdOn)),
        reader: createRow(scan?.readerSerialNumber),
        status: createRow(scan?.status),
        select: {
          isAction: true,
          value: (
            <Radio
              checked={analysis?.scanId === scan?._id}
              color="secondary"
              disabled={
                scan?.status !== "COMPLETE" ||
                !scan?.productId ||
                (scan?.productId &&
                  analysis?.templateProductId &&
                  scan?.productId !== analysis?.templateProductId)
              }
            />
          ),
          onClick: () => {
            if (
              scan?.status !== "COMPLETE" ||
              !scan?.productId ||
              (scan?.productId &&
                analysis?.templateProductId &&
                scan?.productId !== analysis?.templateProductId)
            )
              return;
            setAnalysis({
              ...analysis,
              scanId: scan?._id,
              scanProductId: scan?.productId,
              scanProtocol: scan?.protocol,
              scanStatus: scan?.status,
              scanName: scan?.name,
              scanReaderSerialNumber: scan?.readerSerialNumber,
              scanCreatedOn: scan?.createdOn,
            });
          },
        },
      })),
    [scans, analysis]
  );
  // ********* Analysis Templates *********
  const [templateOrderBy, setTemplateOrderBy] = useState("date");
  const analysisTemplateColumns = useMemo(
    () => [
      createColumn("", "select", false, true),
      createColumn("Name", "name", true),
      createColumn("Date", "date", true),
      createColumn("Product", "product", true),
      createColumn("Protocol", "protocol", true),
    ],
    []
  );
  const analysisTemplateRows = useMemo(
    () =>
      analysisTemplates
        ?.filter((template) => template?.productId === analysis?.scanProductId)
        ?.map((template) => ({
          id: createRow(template?._id),
          name: createRow(template?.name),
          date: createRow(new Date(template?.createdOn + "Z")),
          product: createRow(template?.productName),
          protocol: createRow(template?.protocol),
          productId: createRow(template?.productId),
          select: {
            isAction: true,
            value: (
              <Radio
                checked={analysis?.templateId === template?._id}
                color="secondary"
                disabled={
                  template?.productId &&
                  analysis?.scanProductId &&
                  template?.productId !== analysis?.scanProductId
                }
              />
            ),
            onClick: () => {
              if (
                template?.productId &&
                analysis?.scanProductId &&
                template?.productId !== analysis?.scanProductId
              )
                return;
              setAnalysis({
                ...analysis,
                templateId: template?._id,
                templateName: template?.name,
                templateProductId: template?.productId,
                templateProtocol: template?.protocol,
                templateCreatedOn: template?.createdOn,
                templateProductName: template?.productName,
              });
            },
          },
        })),
    [analysisTemplates, analysis]
  );
  // ********* Steps Content *********
  const selectScanStep = useMemo(
    () => (
      <Grid container spacing={3}>
        <Grid item xs={12} mt={3}>
          <Typography
            variant="h6"
            component="span"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            Select a{" "}
            <Typography
              variant="h6"
              component="span"
              fontWeight="bold"
              mb={0}
              color="textSecondary"
              gutterBottom
            >
              Scan
            </Typography>{" "}
            to continue.
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <BBTable
            columns={scanColumns}
            rows={scanRows}
            orderBy={scanOrderBy}
            setOrderBy={setScanOrderBy}
            rowsPerPage={rowsPerPage}
            onRowClick={(event, row) => {}}
            tableLabel="Scans"
            showLabel
          />
        </Grid>
      </Grid>
    ),
    [
      scanColumns,
      scanRows,
      scanOrderBy,
      templateOrderBy,
      analysisTemplateColumns,
      analysisTemplateRows,
      rowsPerPage,
    ]
  );

  const selectAnalysisTemplateStep = useMemo(
    () => (
      <Grid container spacing={3}>
        <Grid item xs={12} mt={3}>
          <Typography
            variant="h6"
            component="span"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            Select an{" "}
            <Typography
              variant="h6"
              component="span"
              fontWeight="bold"
              mb={0}
              color="textSecondary"
              gutterBottom
            >
              Analysis Template
            </Typography>{" "}
            to continue.
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <BBTable
            columns={analysisTemplateColumns}
            rows={analysisTemplateRows}
            orderBy={templateOrderBy}
            setOrderBy={setTemplateOrderBy}
            rowsPerPage={rowsPerPage}
            onRowClick={(event, row) => {}}
            tableLabel="Analysis Templates"
            showLabel
          />
        </Grid>
      </Grid>
    ),
    [
      scanColumns,
      scanRows,
      scanOrderBy,
      templateOrderBy,
      analysisTemplateColumns,
      analysisTemplateRows,
      rowsPerPage,
      setTemplateOrderBy,
      templateOrderBy,
    ]
  );

  const nameAnalysisStep = useMemo(
    () => (
      <Grid container spacing={3}>
        <Grid item xs={12} mt={3}>
          <Typography
            variant="h6"
            component="span"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            Name the{" "}
            <Typography
              variant="h6"
              component="span"
              fontWeight="bold"
              mb={0}
              color="textSecondary"
              gutterBottom
            >
              Analysis
            </Typography>{" "}
            to continue.
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Analysis Name"
            value={analysis?.name}
            color="secondary"
            required
            onChange={(event) => {
              setAnalysis({
                ...analysis,
                name: event?.target?.value,
              });
            }}
          />
        </Grid>
      </Grid>
    ),
    [analysis, setAnalysis]
  );

  // const reviewStep = useMemo(
  //   () => (
  //     <Grid container spacing={3}>
  //       <Grid item xs={12}>
  //         <Typography
  //           variant="h6"
  //           component="span"
  //           mb={1}
  //           color="textSecondary"
  //           gutterBottom
  //         >
  //           Review the Analysis and click "Create" to continue.
  //         </Typography>
  //       </Grid>

  //       <Grid item xs={12}>
  //         <Divider sx={{ my: 3 }} />
  //       </Grid>

  //       <Grid item xs={12}>
  //         <Typography
  //           variant="h5"
  //           component="span"
  //           mb={5}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.name}
  //         </Typography>
  //       </Grid>

  //       <Grid item xs={12}>
  //         <Divider sx={{ my: 1 }} light variant="inset" />
  //       </Grid>

  //       <Grid item xs={12}>
  //         <Button
  //           variant="outlined"
  //           color="secondary"
  //           onClick={() => {
  //             dispatch(getScan(analysis?.scanId));
  //             setOpenScanModal(true);
  //           }}
  //         >
  //           View Scan
  //         </Button>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Scan Name
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.scanName}
  //         </Typography>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Scan Date
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.scanCreatedOn}
  //         </Typography>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Scan Reader
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.scanReaderSerialNumber}
  //         </Typography>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Scan Product ID
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.scanProductId}
  //         </Typography>
  //       </Grid>
  //       <Grid item xs={12}>
  //         <Divider sx={{ my: 1 }} light variant="inset" />
  //       </Grid>
  //       <Grid item xs={12}>
  //         <Button
  //           variant="outlined"
  //           color="secondary"
  //           onClick={() => {
  //             console.log(analysis?.templateId);
  //             getTemplate(analysis?.templateId);
  //             setOpenTemplateModal(true);
  //           }}
  //         >
  //           View Template
  //         </Button>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Template Name
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.templateName}
  //         </Typography>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Template Product ID
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.templateProductId}
  //         </Typography>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Template Product Name
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.templateProductName}
  //         </Typography>
  //       </Grid>
  //       <Grid
  //         item
  //         xs={6}
  //         mt={5}
  //         sx={{
  //           display: "flex",
  //           flexDirection: "column",
  //           alignItems: "center",
  //         }}
  //       >
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           sx={{ fontWeight: 700 }}
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           Template Protocol
  //         </Typography>
  //         <Typography
  //           variant="body1"
  //           component="h2"
  //           mb={0}
  //           color="textPrimary"
  //           gutterBottom
  //         >
  //           {analysis?.templateProtocol}
  //         </Typography>
  //       </Grid>
  //     </Grid>
  //   ),
  //   [analysis]
  // );

  const reviewStep = useMemo(
    () => (
      <ReviewStep
        analysis={analysis}
        scan={loadedScan}
        template={loadedTemplate}
      />
    ),
    [analysis, loadedScan, loadedTemplate]
  );

  return (
    <BBViewShell alignItems="start" signOut={signOut}>
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
            {screenTitle}
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
        <Grid item mt={5} xs={12}>
          <Paper
            sx={{
              padding: 5,
              minHeight: "40vh",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <Box sx={{ width: "90%" }}>
              <Stepper activeStep={activeStep}>
                {steps.map((step) => (
                  <Step key={step.label}>
                    <StepLabel
                      StepIconProps={{
                        sx: {
                          "&.Mui-completed": {
                            color: green[500],
                          },
                          "&.Mui-active": {
                            color: yellow[700],
                            fontWeight: 700,
                          },
                          "&.Mui-disabled": {
                            color: grey[300],
                            fontWeight: 700,
                          },
                        },
                      }}
                    >
                      {step.label}
                    </StepLabel>
                  </Step>
                ))}
              </Stepper>
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "row",
                  pt: 3,
                  justifyContent: "center",
                }}
              >
                <Button
                  color="secondary"
                  variant="contained"
                  disabled={activeStep === 0}
                  onClick={prevStep}
                  sx={{ marginRight: 1 }}
                >
                  Back
                </Button>
                <Box sx={{ flex: "1 1 auto" }} />
                {isLastStep && analysisCreationInProgress && (
                  <Button color="secondary" variant="contained" disabled>
                    <LoopIcon
                      sx={{
                        animation: "spin 2s linear infinite",
                        "@keyframes spin": {
                          "0%": {
                            transform: "rotate(360deg)",
                          },
                          "100%": {
                            transform: "rotate(0deg)",
                          },
                        },
                      }}
                    />
                  </Button>
                )}
                {isLastStep && !analysisCreationInProgress && (
                  <Button
                    onClick={createAnalysis}
                    color={analysisCreationFailed ? "warning" : "secondary"}
                    variant="contained"
                  >
                    {analysisCreationFailed ? "Try Again?" : "Create"}
                  </Button>
                )}
                {!isLastStep && (
                  <Button
                    onClick={nextStep}
                    color="secondary"
                    variant="contained"
                    disabled={
                      (isFirstStep && !analysis?.scanId) ||
                      (activeStep === 1 && !analysis?.templateId) ||
                      (activeStep === 2 && !analysis?.name)
                    }
                  >
                    Next
                  </Button>
                )}
              </Box>
            </Box>
            <Box
              className="analysis-creation-steps"
              sx={{ width: "90%", marginTop: 3 }}
            >
              {isFirstStep && selectScanStep}
              {activeStep === 1 && selectAnalysisTemplateStep}
              {activeStep === 2 && nameAnalysisStep}
              {isLastStep && reviewStep}
            </Box>
          </Paper>
        </Grid>
      </Grid>
      <BBViewScanModal
        open={openScanModal}
        onClose={() => {
          setOpenScanModal(false);
        }}
        scan={loadedScan}
      />
      <BBViewAnalysisTemplateModal
        open={openTemplateModal}
        onClose={() => {
          setOpenTemplateModal(false);
          clearTemplate();
        }}
        analysisTemplate={loadedTemplate}
      />
    </BBViewShell>
  );
};

export default BBCreateAnalysis;
