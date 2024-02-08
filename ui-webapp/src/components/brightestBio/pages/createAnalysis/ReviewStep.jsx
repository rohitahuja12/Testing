import React, { useState, useEffect, useMemo } from "react";
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
  Card,
  CardContent,
  Stack,
} from "@mui/material";
import { blue, blueGrey, green, grey, red, yellow } from "@mui/material/colors";
import { BBLoader } from "../../BBLoader";
import { WellPlateMini } from "../../../WellPlateMini";
import {
  getWellsFromAnalysis,
  getWellsFromScan,
} from "../../../../utils/wellUtils";

/**
 *
 * @param {
 * analysis: {
 * name: string,
 * scanId: string,
 * scanName: string,
 * scanCreatedOn: string,
 * scanReaderSerialNumber: string,
 * scanProductId: string,
 * templateId: string,
 * templateName: string,
 * templateProductId: string,
 * templateProductName: string,
 * templateProtocol: string,}
 * scan: {
 * name: { isAction: boolean, value: string | Date },
 * createdOn: { isAction: boolean, value: string | Date },
 * productId: { isAction: boolean, value: string | Date },
 * _id: { isAction: boolean, value: string | Date },
 * wells: any[]
 * }
 * template: {
 * name: { isAction: boolean, value: string | Date },
 * createdOn: { isAction: boolean, value: string | Date },
 * productId: { isAction: boolean, value: string | Date },
 * _id: { isAction: boolean, value: string | Date },
 * protocolArgs: any
 * }
 * } props
 */
const ReviewStep = ({ analysis, scan, template }) => {
  const analysisImage = require("./../../../../assets/analyzescan.png");
  // src/assets/brightestbio.png
  const brightestBioLogo = require("./../../../../assets/brightestbio.png");

  const renderDescriptionTextField = (label, value) => {
    return (
      <TextField
        label={label}
        variant="standard"
        value={value}
        disabled
        sx={{
          "& .MuiInputBase-root.Mui-disabled:before": {
            borderBottom: "none",
          },
        }}
        style={{ maxWidth: "100%", marginBottom: "10px" }}
      />
    );
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Typography
          variant="h6"
          component="span"
          mb={1}
          color="textSecondary"
          gutterBottom
        >
          Review the{" "}
          <Typography
            variant="h6"
            component="span"
            mb={1}
            color="textSecondary"
            gutterBottom
          >
            <b>Analysis</b>
          </Typography>{" "}
          below and click "Create" to continue.
        </Typography>
      </Grid>

      <Grid item lg={1} xs={0} />
      <Grid item lg={10} xs={12}>
        <Card
          sx={{
            // backgroundColor: "#1e1b23",
            backgroundColor: "background.modalPaper",
            boxShadow: 7,
            // border: ".5px groove",
            // borderColor: blue[900],
            // boxShadow: 5,
            // borderBottom: "1px solid",
            // shadow color blue
            // borderColor: "background.paper",
            // borderColor: yellow[700],
          }}
        >
          <CardContent
          style={{
            paddingRight: "0px",
          }}
          >
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography
                  variant="h4"
                  component="span"
                  mb={1}
                  color="textSecondary"
                  gutterBottom
                >
                  {analysis?.name}
                </Typography>
              </Grid>
              <Grid
                item
                xs={12}
                md={6}
                style={{
                  display: "flex",
                  flexDirection: "row",
                  alignContent: "center",
                  justifyContent: "center",
                  paddingRight: "20px",
                }}
              >
                <Stack>
                  <Stack>
                    {/* display name, created on, product id, scan name, scan. with a title for each of these and then a textfield for the values. */}
                    {renderDescriptionTextField(
                      "Scan Name",
                      analysis?.scanName
                    )}
                    {renderDescriptionTextField(
                      "Scan Created On",
                      new Date(analysis?.scanCreatedOn).toLocaleString()
                    )}
                  </Stack>
                  <WellPlateMini extraMini padRight wells={getWellsFromScan(scan)} />
                </Stack>
              </Grid>
              <Grid
                item
                xs={12}
                md={6}
                pl={0}
                style={{
                  paddingLeft: "0px",
                  paddingRight: "0px",
                  display: "flex",
                  flexDirection: "row",
                  alignContent: "center",
                  justifyContent: "center",
                  borderLeft: `1px dashed ${grey[600]}`,
                }}
              >
                <Stack>
                  {renderDescriptionTextField(
                    "Template Name",
                    analysis?.templateName
                  )}
                  {renderDescriptionTextField(
                    "Template Created On",
                    new Date(analysis?.templateCreatedOn).toLocaleString()
                  )}
                  <WellPlateMini
                    extraMini
                    wells={getWellsFromAnalysis(template)}
                  />
                </Stack>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
      <Grid item lg={1} xs={0} />
    </Grid>
  );
};

export default ReviewStep;
