import React, { useMemo, useState, useRef } from "react";
import {
  Grid,
  Typography,
  Paper,
  IconButton,
  Button,
  TextField,
  Card,
  CardContent,
  Box,
  Stepper,
  Step,
  StepLabel,
  CardMedia,
  CardActions,
  Radio,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
} from "@mui/material";
import { useProducts } from "../hooks/useProducts";
import { useCreateScan } from "../hooks/useCreateScan";
import { useReaders } from "../hooks/useReaders";
import BBViewShell from "../BBViewShell";
import { useSteps } from "../hooks/useSteps";
import { green, grey, yellow, blue } from "@mui/material/colors";
import { useNavigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { WellPlateBasic } from "../../WellPlateBasic";
import LoopIcon from "@mui/icons-material/Loop";
import {
  TransitionGroup,
  CSSTransition,
  Transition,
} from "react-transition-group"; // ES6

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
const CreateScan = ({ screenTitle, signOut }) => {
  const navigate = useNavigate();
  const {
    scan,
    setScan,
    saveScan,
    scanCreationInProgress,
    scanCreationFailed,
  } = useCreateScan();
  const { readers } = useReaders();
  const {
    products,
    selectedProduct,
    setSelectedProduct,
    selectProductByBarcode,
    getPlateBarcodeByProductId,
    selectedPlate,
  } = useProducts();
  const [barcode, setBarcode] = useState("");
  const clearSelections = useRef(null);
  const selectAll = useRef(null);
  const [showTransition, setShowTransition] = useState(true);
  const [barcodeErrorMessage, setBarcodeErrorMessage] = useState("");

  const { activeStep, nextStep, prevStep, isLastStep, isFirstStep } =
    useSteps(3);
  const scanImage = useMemo(() => require("./../../../assets/product.png"), []);

  const productCards = useMemo(() => {
    return (
      <Grid container spacing={2}>
        {/* {products?.map((product, i) => {
          const selected = selectedProduct?._id === product?._id;
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} xl={3} key={'grid-item-' + i}>
              <Card
                key={i}
                sx={{ border: selected ? `1px solid` : '1px solid', borderColor: selected ? blue[100] : 'background.paper' }}
                onClick={() => {
                  setSelectedProduct(product);
                  setScan({ ...scan, productId: product._id, plateBarcode: getPlateBarcodeByProductId(product._id) })
                }}
              >
                <CardMedia
                  component="img"
                  height="100"
                  image={scanImage}
                  alt={"product"}
                  sx={{ padding: "2em 1em 1em 0em", objectFit: "contain", cursor: 'pointer' }}
                />
                <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', minHeight: 100 }}>
                  <Typography gutterBottom variant="subtitle2" component="div">
                    {product?.productName}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {`${Object.values(product?.productDescription).reduce((acc, curr) => acc + curr, '') || 'no description'}`}
                  </Typography>
                </CardContent>
                <CardActions onClick={() => { setSelectedProduct(product._id) }} sx={{ cursor: 'pointer' }}>
                  <Radio
                    checked={selected}
                    value="A"
                    name="radio-button-demo"
                    inputProps={{ 'aria-label': product._id }}
                    color={'secondary'}
                  />
                  <Typography variant="body2" color="text.secondary">
                    Select
                  </Typography>
                </CardActions>
              </Card>
            </Grid>
          );
        })} */}
        <Grid item xs={12} />
        <Grid item xs={4} />
        <Grid item xs={4}>
          <TextField
            id="plate-barcode"
            label="Plate Barcode"
            variant="outlined"
            color="secondary"
            value={barcode}
            fullWidth
            error={!!barcodeErrorMessage}
            helperText={barcodeErrorMessage}
            onChange={(event) => {
              try {
                const tempBarcode = event.target.value;
                setBarcode(tempBarcode);
                const tempSelectedProduct = selectProductByBarcode(tempBarcode);
                setScan({
                  ...scan,
                  productId: tempSelectedProduct?._id,
                  plateBarcode: tempBarcode,
                });
                setBarcodeErrorMessage("");
              } catch (error) {
                setBarcodeErrorMessage(error.message);
                setScan({ ...scan, productId: null, plateBarcode: null });
              }
            }}
          />
        </Grid>
        <Grid item xs={4} />
        {selectedProduct && (
          <Grid
            item
            xs={12}
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Card sx={{ border: "1px solid", borderColor: blue[300] }}>
              <CardMedia
                component="img"
                height="100"
                image={scanImage}
                alt={"product"}
                sx={{ padding: "1em", objectFit: "contain", cursor: "pointer" }}
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
                  {selectedProduct?.productName}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {`${
                    Object.values(selectedProduct?.productDescription).reduce(
                      (acc, curr) => acc + curr,
                      ""
                    ) || "no description"
                  }`}
                </Typography>
              </CardContent>
              <CardActions>
                <Typography variant="body2" color={blue[500]}>
                  Product Selected ✔️
                </Typography>
              </CardActions>
            </Card>
          </Grid>
        )}
      </Grid>
    );
  }, [
    products,
    selectedProduct,
    barcode,
    selectProductByBarcode,
    selectedPlate,
    setScan,
    scan,
  ]);

  const configureStep = useMemo(() => {
    return (
      <Grid className="scan-creation-configure-step" container spacing={2}>
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography
                variant="h6"
                component="h2"
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                Scan Details
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textSecondary"
                gutterBottom
              >
                Enter a name and description for your scan.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                required
                id="scan-name"
                label="Scan Name"
                variant="outlined"
                color="secondary"
                value={scan?.name || ""}
                fullWidth
                onChange={(event) =>
                  setScan({ ...scan, name: event.target.value })
                }
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel required color="secondary" id="readers-label">
                  Readers
                </InputLabel>
                <Select
                  color="secondary"
                  variant="outlined"
                  labelId="readers-label"
                  id="readers"
                  value={
                    scan?.readerSerialNumber ? scan?.readerSerialNumber : ""
                  }
                  label="Readers"
                  onChange={(event) =>
                    setScan({ ...scan, readerSerialNumber: event.target.value })
                  }
                >
                  {readers?.map((reader, i) => {
                    return (
                      <MenuItem key={i} value={reader?.serialNumber}>
                        {reader?.serialNumber}
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} mt={3}>
              <Typography
                variant="h6"
                component="h2"
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                Well Selection
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textSecondary"
                gutterBottom
              >
                Please drag and select the area of the well plate you would like
                to scan.
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textSecondary"
                gutterBottom
              >
                Hold down the shift key for multiple selections.
              </Typography>
            </Grid>
            <Grid
              item
              xs={12}
              mt={3}
              sx={{ display: "flex", justifyContent: "space-evenly" }}
            >
              <Button
                onClick={() => {
                  selectAll.current();
                }}
                color="secondary"
                variant="outlined"
              >
                Select All
              </Button>
              <Button
                onClick={() => {
                  clearSelections.current();
                }}
                color="secondary"
                variant="outlined"
              >
                Clear Plate
              </Button>
            </Grid>

            <Grid item xs={0} xl={3} lg={2} md={1} />
            <Grid
              item
              xs={12}
              xl={6}
              lg={8}
              md={10}
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <WellPlateBasic
                clearSelections={clearSelections}
                selectAll={selectAll}
                setScanWells={({ selectedWells, wells }) => {
                  setScan({ ...scan, selectedWells });
                }}
                skipReduxInteractions
              />
            </Grid>
            <Grid item xs={0} xl={3} lg={2} md={1} />
          </Grid>
        </Grid>
      </Grid>
    );
  }, [scan, readers]);

  const reviewStep = useMemo(() => {
    // a review step to show the user what they have selected
    // use labels to show the scan name, reader, and wells
    return (
      <Grid className="scan-creation-review-step" container spacing={2}>
        <Grid item xs={12}>
          <Grid container spacing={2}>
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
                Please review the details of your scan.
              </Typography>
            </Grid>
            <Grid
              item
              xs={6}
              mt={5}
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <Typography
                variant="body1"
                component="h2"
                sx={{ fontWeight: 700 }}
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                Scan Name
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                {scan?.name}
              </Typography>
            </Grid>
            <Grid
              item
              xs={6}
              mt={5}
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <Typography
                variant="body1"
                component="h2"
                sx={{ fontWeight: 700 }}
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                Reader
              </Typography>
              <Typography
                variant="body1"
                component="h2"
                mb={0}
                color="textPrimary"
                gutterBottom
              >
                {scan?.readerSerialNumber}
              </Typography>
            </Grid>
            <Grid item xs={0} xl={3} lg={2} md={1} />
            <Grid
              item
              xs={12}
              xl={6}
              lg={8}
              md={10}
              sx={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <WellPlateBasic
                selectedWells={scan?.selectedWells}
                readOnly
                skipReduxInteractions
              />
            </Grid>
            <Grid item xs={0} xl={3} lg={2} md={1} />
          </Grid>
        </Grid>
      </Grid>
    );
  }, [scan]);

  const steps = useMemo(
    () => [
      { label: "Select Product" },
      { label: "Configure" },
      { label: "Review" },
    ],
    []
  );

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
          <Paper sx={{ padding: 5, minHeight: "60vh" }}>
            <Box sx={{ width: "100%" }}>
              <Stepper activeStep={activeStep}>
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
              <React.Fragment>
                <Box sx={{ display: "flex", flexDirection: "row", pt: 3 }}>
                  <Button
                    color="secondary"
                    variant="contained"
                    disabled={activeStep === 0}
                    onClick={() => {
                      setShowTransition(false);
                      setTimeout(() => {
                        prevStep();
                        setShowTransition(true);
                      }, 10);
                    }}
                    sx={{ mr: 1 }}
                  >
                    Back
                  </Button>
                  <Box sx={{ flex: "1 1 auto" }} />

                  {isLastStep && scanCreationInProgress && (
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
                  {isLastStep && !scanCreationInProgress && (
                    <Button
                      onClick={saveScan}
                      color={scanCreationFailed ? "warning" : "secondary"}
                      variant="contained"
                    >
                      {scanCreationFailed ? "Try Again?" : "Create"}
                    </Button>
                  )}
                  {!isLastStep && (
                    <Button
                      onClick={() => {
                        setShowTransition(false);
                        setTimeout(() => {
                          nextStep();
                          setShowTransition(true);
                        }, 10);
                      }}
                      color="secondary"
                      variant="contained"
                      disabled={
                        (isFirstStep && !selectedProduct) ||
                        (activeStep === 1 &&
                          (valueIsBlank(scan?.name) ||
                            !scan?.readerSerialNumber))
                      }
                    >
                      Next
                    </Button>
                  )}
                </Box>
              </React.Fragment>
            </Box>
            <CSSTransition
              in={showTransition}
              timeout={500}
              classNames={"scan-creation-steps"}
            >
              <Box
                className="scan-creation-steps"
                sx={{ width: "100%", mt: 5 }}
              >
                {isFirstStep && productCards}
                {activeStep === 1 && configureStep}
                {activeStep === 2 && reviewStep}
              </Box>
            </CSSTransition>
          </Paper>
        </Grid>
      </Grid>
    </BBViewShell>
  );
};

export default CreateScan;
