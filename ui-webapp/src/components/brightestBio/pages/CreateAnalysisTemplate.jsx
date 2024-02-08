import React, { useState, useMemo, useEffect, useCallback } from "react";
import {
  Grid,
  Typography,
  Paper,
  Button,
  List,
  Stepper,
  Box,
  Step,
  StepLabel,
  Card,
  CardMedia,
  CardContent,
  CardActions,
  Radio,
  TextField,
  Skeleton,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Divider,
} from "@mui/material";
import BBViewShell from "../BBViewShell";
import { useNavigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useProducts } from "../hooks/useProducts";
import { green, grey, yellow, blue, orange } from "@mui/material/colors";
import LoopIcon from "@mui/icons-material/Loop";
import { useSteps } from "../hooks/useSteps";
import { useCreateAnalysisTemplate } from "../hooks/useCreateAnalysisTemplate";
import { WellPlateAdvanced } from "../../WellPlateAdvanced";
import { WellPlateMini } from "../../WellPlateMini";
import { WellColor } from "../../../enums/WellColor";
import { useTheme } from "@mui/material/styles";

/**
 *
 * @param {string} value
 * @returns
 */
const valueIsBlank = (value) => !value || value.replaceAll(" ", "") === "";

/**
 *
 * @param {screenTitle: string, signOut: function} props
 * @returns
 */
const CreateAnalysisTemplate = ({ screenTitle, signOut }) => {
  const navigate = useNavigate();
  const { activeStep, nextStep, prevStep, isLastStep, isFirstStep } =
    useSteps(4);
  const scanImage = useMemo(() => require("./../../../assets/product.png"), []);
  const { products, getProductById } = useProducts();
  const {
    createTemplate,
    setTemplate,
    template,
    templateCreationInProgress,
    resetTemplate,
    resetWells,
    setWellTypes,
    setWells,
    renameUnknownsModalOpen,
    setRenameUnknownsModalOpen,
    plateMaps,
    selectedPlateMap,
    setSelectedPlateMap,
    templateName,
    setTemplateName,
    setConcentrations,
    concentrations,
    setStandardDilution,
    standardDilution,
    originalConcentrations,
    setOriginalConcentrations,
    analysisCreationFailed,
    thresholdAlgorithm,
    setThresholdAlgorithm,
    skipStandardConcentrationStep,
  } = useCreateAnalysisTemplate();
  const [dilutionError, setDilutionError] = useState(null);
  const [showConfigureStepLoader, setShowConfigureStepLoader] = useState(true);
  const theme = useTheme();

  // ********** description **********
  // this is a multi-step form to create an analysis template.
  // An analysis template is composed of a product, a name, wells that have been selected, and standard concentrations.
  // ********** steps **********
  // step1: select product
  // step2: set analysis template name and well selection
  // step3: set standard concentrations
  // step4: review and create

  const steps = [
    { label: "Product" },
    { label: "Configure" },
    { label: "Standard Concentrations" },
    { label: "Review" },
  ];

  const productsStep = useMemo(() => {
    return (
      <Grid container spacing={2} pl={"8vw"} pr={"8vw"}>
        {products?.map((product, i) => {
          const selected = template?.productId === product?._id;
          return (
            <Grid
              item
              xs={12}
              sm={6}
              md={4}
              lg={3}
              xl={3}
              key={"grid-item-" + i}
            >
              <Card
                key={i}
                sx={{
                  border: selected ? `1px solid` : "1px solid",
                  borderColor: selected ? blue[100] : "background.paper",
                }}
                onClick={() => {
                  setTemplate({
                    ...template,
                    productId: product?._id,
                    productName: product?.productName,
                  });
                }}
              >
                <CardMedia
                  component="img"
                  height="100"
                  image={scanImage}
                  alt={"product"}
                  sx={{
                    padding: "2em 1em 1em 0em",
                    objectFit: "contain",
                    cursor: "pointer",
                  }}
                />
                <CardContent
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    cursor: "pointer",
                    minHeight: 100,
                  }}
                >
                  <Typography gutterBottom variant="subtitle2" component="div">
                    {product?.productName}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {`${
                      Object.values(product?.productDescription).reduce(
                        (acc, curr) => acc + curr,
                        ""
                      ) || "no description"
                    }`}
                  </Typography>
                </CardContent>
                <CardActions
                  onClick={() => {
                    setTemplate({
                      ...template,
                      productId: product?._id,
                      productName: product?.productName,
                    });
                  }}
                  sx={{ cursor: "pointer" }}
                >
                  <Radio
                    checked={selected}
                    value="A"
                    name="radio-button-demo"
                    inputProps={{ "aria-label": product._id }}
                    color={"secondary"}
                    // sx={{
                    //   '&, &.Mui-checked': {
                    //     color: 'colorPrimary',
                    //   },
                    // }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Select
                  </Typography>
                </CardActions>
              </Card>
            </Grid>
          );
        })}
        <Grid item xs={12} /> {/* phx-231 */}
      </Grid>
    );
  }, [products, template, setTemplate]);

  const wellPlateComponent = useMemo(() => {
    return (
      <WellPlateAdvanced
        hideHud
        showLoader={showConfigureStepLoader}
        setShowLoader={setShowConfigureStepLoader}
        resetWells={resetWells}
        setWells={setWells}
        setWellTypes={setWellTypes}
        template={template}
        renameUnknownsModalOpen={renameUnknownsModalOpen}
        setRenameUnknownsModalOpen={setRenameUnknownsModalOpen}
      />
    );
  }, [
    nextStep,
    setTemplate,
    showConfigureStepLoader,
    setShowConfigureStepLoader,
    template,
    resetWells,
    setWells,
    setWellTypes,
    renameUnknownsModalOpen,
    setRenameUnknownsModalOpen,
  ]);

  // template name and well selection
  const configureStep = useMemo(() => {
    return (
      <Grid container spacing={2} pl={"8vw"} pr={"8vw"}>
        <Grid item xs={12}>
          <Typography
            variant="h6"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Analysis Template Details
          </Typography>
          <Typography
            variant="body1"
            component="h2"
            mb={2}
            color="textSecondary"
            gutterBottom
          >
            Enter a name for this analysis template. Then, choose a preset Plate
            Map or manually configure the wells by right-clicking wells,
            columns, and rows.
          </Typography>
        </Grid>
        <Grid
          item
          xs={12}
          md={6}
          style={{ opacity: showConfigureStepLoader ? 0 : 1 }}
        >
          <TextField
            required
            id="template-name"
            label="Template Name"
            variant="outlined"
            color="secondary"
            value={templateName || ""}
            fullWidth
            onChange={(event) => {
              setTemplateName(event.target.value);
            }}
          />
        </Grid>
        <Grid
          item
          xs={12}
          md={6}
          style={{ opacity: showConfigureStepLoader ? 0 : 1 }}
        >
          <FormControl fullWidth>
            <InputLabel color="secondary" id="plate-maps-label">
              Plate Maps
            </InputLabel>
            <Select
              color="secondary"
              variant="outlined"
              labelId="plate-maps-label"
              id="plate-maps"
              value={selectedPlateMap || ""}
              label="Plate Maps"
              onChange={(event) => setSelectedPlateMap(event.target.value)}
            >
              {plateMaps?.map((plateMap, i) => {
                return (
                  <MenuItem key={i} value={plateMap?._id}>
                    {plateMap?.name}
                  </MenuItem>
                );
              })}
            </Select>
          </FormControl>
        </Grid>
        <Grid
          item
          xs={12}
          md={6}
          style={{ opacity: showConfigureStepLoader ? 0 : 1 }}
        >
          <FormControl fullWidth>
            <InputLabel color="secondary" id="algorithm-select-label">
              Algorithm
            </InputLabel>
            <Select
              color="secondary"
              variant="outlined"
              labelId="algorithm-select-label"
              id="algorithm-select"
              value={thresholdAlgorithm || ""}
              label="Algorithm"
              onChange={(event) => setThresholdAlgorithm(event.target.value)}
            >
              <MenuItem value={"mean-threshold"}>mean-threshold</MenuItem>
              <MenuItem value={"circle-threshold"}>circle-threshold</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid
          item
          xs={12}
          md={6}
          style={{ opacity: showConfigureStepLoader ? 0 : 1 }}
        >
          {/* buttons for clear plate, rename unknowns */}
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Button
                variant="outlined"
                color="secondary"
                fullWidth
                onClick={() => {
                  resetWells();
                }}
              >
                clear plate
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              <Button
                variant="outlined"
                color="secondary"
                fullWidth
                style={{
                  whiteSpace: "nowrap",
                  minWidth: "auto",
                }}
                onClick={() => {
                  setRenameUnknownsModalOpen(true);
                }}
              >
                Rename Unknowns
              </Button>
            </Grid>
          </Grid>
        </Grid>
        {showConfigureStepLoader && (
          <Grid item xs={12}>
            <Skeleton
              sx={{ bgcolor: "primary" }}
              variant="rectangular"
              width={"100%"}
              height={"30vh"}
            />
          </Grid>
        )}
        <Grid item xs={0} lg={1}></Grid>
        <Grid
          item
          xs={12}
          lg={10}
          style={{
            opacity: showConfigureStepLoader ? 0 : 1,
          }}
        >
          {wellPlateComponent}
        </Grid>
        <Grid item xs={0} lg={1}></Grid>
      </Grid>
    );
  }, [
    template,
    setTemplate,
    nextStep,
    showConfigureStepLoader,
    resetWells,
    wellPlateComponent,
    renameUnknownsModalOpen,
    setRenameUnknownsModalOpen,
    plateMaps,
    selectedPlateMap,
    setSelectedPlateMap,
    setTemplateName,
    templateName,
  ]);

  const selectedProduct = useMemo(() => {
    return getProductById(template.productId);
  }, [getProductById, template.productId]);

  useEffect(() => {
    const decimalConcentrations = Object.keys(
      selectedProduct?.recommendedInitialConcentrations || {}
    ).reduce((acc, key) => {
      acc[key] = Number(
        selectedProduct?.recommendedInitialConcentrations[key]
      ).toFixed(2);
      return acc;
    }, {});

    setConcentrations(decimalConcentrations || {});
    setOriginalConcentrations(decimalConcentrations || {});
  }, [selectedProduct]);

  const calculateAndsyncConcentrations = (
    concentrations,
    previousConcentration,
    newConcentration,
    concentrationKey
  ) => {
    const concentrationKeys = Object.keys(concentrations);
    const concentrationRatio = newConcentration / previousConcentration;
    const newConcentrations = { ...concentrations };
    concentrationKeys.forEach((key) => {
      if (key !== concentrationKey) {
        newConcentrations[key] = Number(
          originalConcentrations[key] * concentrationRatio
        ).toFixed(2);
      }
    });
    return newConcentrations;
  };

  const renderConcentrationInput = useCallback(
    (initialConcentration, label, onChange, showError, skipStep) => {
      return (
        <Grid item xs={12} md={6} key={label}>
          <TextField
            required
            disabled={skipStep}
            type="number"
            id={label}
            label={label}
            variant="outlined"
            color="secondary"
            value={initialConcentration || ""}
            fullWidth
            onChange={(event) => {
              const newConcentrations = calculateAndsyncConcentrations(
                concentrations,
                originalConcentrations[label],
                event.target.value,
                label
              );
              onChange({ ...newConcentrations, [label]: event.target.value });
            }}
            error={showError}
            onBlur={(event) =>
              onChange({
                ...concentrations,
                [label]: Number(event.target.value).toFixed(2),
              })
            }
            helperText={showError ? "Please enter a valid concentration" : ""}
            step={0.01}
            inputProps={{ step: 0.01 }}
          />
        </Grid>
      );
    },
    [concentrations, originalConcentrations]
  );

  const standardConcentrationsStep = useMemo(() => {
    return (
      <Grid container spacing={2} pl={"8vw"} pr={"8vw"}>
        <Grid item xs={12}>
          {skipStandardConcentrationStep && (
            <>
              <Typography
                variant="h6"
                component="h2"
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                Standard Concentrations
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textSecondary"
                gutterBottom
              >
                Standard Concentrations are not required because no
                <Typography
                  variant="body1"
                  component="span"
                  fontWeight="bold"
                  mb={0}
                  color={WellColor.STANDARD}
                  gutterBottom
                >
                  {" Standards "}
                </Typography>
                were configured.
              </Typography>
            </>
          )}
          {!skipStandardConcentrationStep && (
            <>
              <Typography
                variant="h6"
                component="h2"
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                Standard Concentrations
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textSecondary"
                gutterBottom
              >
                Enter the standard concentrations in the plate.
              </Typography>
            </>
          )}
        </Grid>
        {concentrations &&
          Object.keys(concentrations).map((label, index) => {
            return renderConcentrationInput(
              concentrations[label],
              label,
              setConcentrations,
              false,
              skipStandardConcentrationStep
            );
          })}
        <Grid item xs={12}>
          <Divider />
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="h6"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Standard Dilution Factor
          </Typography>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            The serial dilution factor used to create the standard series.
          </Typography>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            required
            disabled={skipStandardConcentrationStep}
            type="number"
            id={"standard-dilution-factor"}
            label={"Standard Dilution Factor"}
            variant="outlined"
            color="secondary"
            value={standardDilution || ""}
            error={dilutionError}
            aria-errormessage={dilutionError}
            helperText={dilutionError}
            fullWidth
            onChange={(event) => {
              if (event.target.value <= 0) {
                setDilutionError("Please enter a valid dilution factor.");
              } else {
                setDilutionError(null);
              }
              setStandardDilution(event.target.value);
            }}
            step={0.1}
            inputProps={{ step: 0.1, min: 0.1 }}
          />
        </Grid>
        <Grid item xs={12} mb={6}></Grid>
      </Grid>
    );
  }, [
    selectedProduct,
    concentrations,
    standardDilution,
    setConcentrations,
    setStandardDilution,
    dilutionError,
    setDilutionError,
    skipStandardConcentrationStep,
    WellColor,
    theme.palette.mode,
  ]);

  const reviewStep = useMemo(() => {
    return (
      <Grid container spacing={2} pl={"8vw"} pr={"8vw"}>
        <Grid item xs={12}>
          <Typography
            variant="h6"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Review
          </Typography>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            Please review the Analysis Template below. Click "create" to create
            the template.
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Analysis Template Name
          </Typography>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            {templateName}
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Product
          </Typography>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            {template?.productName}
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Standard Concentrations
          </Typography>
          {!skipStandardConcentrationStep && (
            <Typography
              variant="body1"
              component="h2"
              mb={0}
              color="textSecondary"
              gutterBottom
            >
              {concentrations &&
                Object.keys(concentrations)
                  .map((key) => {
                    return `${key}: ${concentrations[key]}`;
                  })
                  .join(", ")}
            </Typography>
          )}
          {skipStandardConcentrationStep && (
            <Typography
              variant="body1"
              component="h2"
              mb={0}
              color={theme.palette.mode === "dark" ? yellow[700] : blue[700]}
              gutterBottom
            >
              No standards were configured.
            </Typography>
          )}
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Standard Dilution Factor
          </Typography>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textSecondary"
            gutterBottom
          >
            {standardDilution}
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Typography
            variant="body1"
            component="h2"
            mb={0}
            color="textPrimary"
            gutterBottom
          >
            Plate
          </Typography>
        </Grid>
        <Grid item xs={0} md={3} />
        <Grid item xs={12} md={6}>
          <WellPlateMini wells={template?.wells} />
        </Grid>
        <Grid item xs={0} md={3} />
        <Grid item xs={12} mb={6}></Grid>
      </Grid>
    );
  }, [
    template,
    concentrations,
    standardDilution,
    templateName,
    skipStandardConcentrationStep,
    WellPlateMini,
    theme,
  ]);

  return (
    <BBViewShell alignItems="start" signOut={signOut}>
      <Grid container spacing={2}>
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
          <Paper sx={{ paddingTop: 5, minHeight: "40vh" }}>
            <Box sx={{ width: "100%" }}>
              <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((step, i) => (
                  <Step key={i}>
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
                  pl: "8vw",
                  pr: "8vw",
                }}
              >
                <Button
                  color="secondary"
                  variant="contained"
                  disabled={activeStep === 0}
                  onClick={() => {
                    setShowConfigureStepLoader(true);
                    prevStep();
                  }}
                  sx={{ mr: 1 }}
                >
                  Back
                </Button>
                <Box sx={{ flex: "1 1 auto" }} />

                {isLastStep && templateCreationInProgress && (
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
                {isLastStep && !templateCreationInProgress && (
                  <Button
                    onClick={() => {
                      createTemplate();
                    }}
                    color={analysisCreationFailed ? "warning" : "secondary"}
                    variant="contained"
                  >
                    {analysisCreationFailed ? "Try Again?" : "Create"}
                  </Button>
                )}
                {!isLastStep && (
                  <Button
                    onClick={() => {
                      nextStep();
                    }}
                    color="secondary"
                    variant="contained"
                    disabled={
                      (isFirstStep && !template?.productId) ||
                      (activeStep === 1 && valueIsBlank(templateName)) ||
                      (activeStep === 2 && !standardDilution) ||
                      dilutionError
                    }
                    //   || (activeStep === 1 && (!scan?.name || !scan?.readerSerialNumber))}
                  >
                    Next
                  </Button>
                )}
              </Box>
            </Box>
            <Box
              className="analysis-template-creation-steps"
              sx={{ width: "100%", mt: 5 }}
            >
              {activeStep === 0 && productsStep}
              {activeStep === 1 && configureStep}
              {activeStep === 2 && standardConcentrationsStep}
              {activeStep === 3 && reviewStep}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </BBViewShell>
  );
};

export default CreateAnalysisTemplate;
