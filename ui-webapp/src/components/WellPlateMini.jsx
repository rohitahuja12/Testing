import React, { useReducer, useEffect, useMemo } from "react";
import { createStyles, SimpleGrid, Group } from "@mantine/core";
import { Grid, Box, Typography, useMediaQuery } from "@mui/material";
import { useWellPlateMiniStyles } from "./styles/WellPlateMiniStyles";
import PlateWell from "./brightestBio/PlateWell.jsx";
import { grey } from "@mui/material/colors";

const rows = ["A", "B", "C", "D", "E", "F", "G", "H"];
const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const wellArray = Array.from({ length: 96 }, (v, i) => ({
  row: rows[Math.floor(i / 12)],
  column: columns[i % 12].toString(),
  type: "empty",
}));

const initWells = {
  wells: wellArray,
};

// const scale = 0.9;
// const miniFontSize = 16 * scale;
// const miniWellSize = 40 * scale;
// const miniMinWellHeight = 60 * scale;
// const plateForeignObjectWidth = 675 * scale;

const getScaledPlateValues = (scale, isPhoneView, isTabletView) => {
  if (isPhoneView) {
    return {
      scale,
      miniFontSize: 12 * scale,
      miniWellSize: 30 * scale,
      miniMinWellHeight: 60 * scale,
      plateForeignObjectWidth: 675   * scale,
    };
  }

  return {
    scale,
    miniFontSize: 20 * scale,
    miniWellSize: 40 * scale,
    miniMinWellHeight: 60 * scale,
    plateForeignObjectWidth: 675 * scale,
  };
};

function plateReducer(state, action) {
  switch (action.type) {
    case "setWells":
      return {
        ...state,
        wells: state.wells.map((stateWell) => {
          const newState = action.payload?.find(
            (actionWell) =>
              actionWell.row === stateWell.row &&
              actionWell.column.toString() === stateWell.column
          );
          return newState || stateWell;
        }),
      };
    case "error":
      return { ...state, isError: true, error: action.error };
    default:
      throw new Error();
  }
}

export const WellPlateMini = ({ ...props }) => {
  const { classes, cx } = useWellPlateMiniStyles();
  const [plateState, dispatch] = useReducer(plateReducer, initWells);
  const { wells, extraMini = false, padRight = false } = props;
  const colcss = Array(12).fill("columns").join(" ");
  const wellscss = Array(12).fill("wells").join(" ");
  const rowcss = `"rows ${wellscss}"\n`.repeat(8);
  const gridTemplateAreasCss = `". ${colcss}"\n${rowcss}`;
  const isPhoneView = useMediaQuery("(max-width:600px)");
  const isTabletView = useMediaQuery("(max-width:1000px)");

  const {
    scale,
    miniFontSize,
    miniWellSize,
    miniMinWellHeight,
    plateForeignObjectWidth,
  } = useMemo(
    () => getScaledPlateValues(1, isPhoneView, isTabletView),
    [isPhoneView, isTabletView]
  );

  useEffect(() => {
    dispatch({ type: "setWells", payload: wells?.wells });
  }, []);

  const getIndexByRowColumn = (row, column) => {
    const rowNumberRepresentation = row.toLowerCase().charCodeAt(0) - 97;
    return rowNumberRepresentation * columns.length + (Number(column) - 1);
  };

  const wellsGrid = useMemo(() => {
    return (
      <Grid container spacing={0}>
        {rows.map((row) => {
          return columns.map((column) => {
            const wellData = wells[getIndexByRowColumn(row, column)];
            return (
              <Grid
                item
                xs={1}
                key={`${row}-${column}`}
                style={{ minHeight: miniMinWellHeight }}
              >
                <PlateWell
                  classes={classes}
                  key={`${row}-${column}`}
                  row={row}
                  column={column}
                  replicateGroup={wellData.replicateGroup}
                  type={wellData.type}
                  replicateId={wellData.replicateId}
                  mini
                  size={extraMini ? miniWellSize : 24}
                />
              </Grid>
            );
          });
        })}
      </Grid>
    );
  }, [wells, rows, columns]);

  const getSvgWidth = () => {
    if (isPhoneView) return "150px";
    if (isTabletView) return "250px";
    return "300px";
  }

  return (
    <svg
      preserveAspectRatio="xMaxYMid meet"
      viewBox="0 0 765 600"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ width: getSvgWidth() }}
      // width={extraMini ? 500 : 600}
    >
      <path
        fillOpacity={"0%"}
        stroke={grey[500]}
        style={{ transform: `scale(${scale})` }}
        d="M 744.7384 0.8491 H 17.3453 C 8.1784 0.8491 0.7471 9.2941 0.7471 19.7117 V 578.1976 C 0.7471 588.6157 8.1784 597.0611 17.3453 597.0611 H 744.7384 C 753.9048 597.0611 761.3366 588.6157 761.3366 578.1976 V 19.7117 C 761.3366 9.2941 753.9048 0.8491 744.7384 0.8491 Z M 45.2157 50.4782 L 45.2258 50.4671 L 45.2355 50.4556 L 59.1706 34.0105 C 62.2993 30.3179 66.6158 28.2317 71.1266 28.2317 H 698.3295 H 725.2139 C 731.403 28.2317 736.4205 33.9339 736.4205 40.9678 V 524.5317 V 555.0815 C 736.4205 562.1142 731.403 567.8177 725.2139 567.8177 H 698.3295 H 70.7432 C 66.4495 567.8177 62.3228 565.9257 59.2299 562.5404 L 44.5027 546.4259 L 44.4828 546.404 L 30.3017 529.6668 C 27.3236 526.151 25.6597 521.4628 25.6597 516.5818 V 79.9016 C 25.6597 74.7753 27.4953 69.8701 30.7447 66.3145 L 45.2157 50.4782 Z"
      />
      <foreignObject x="40" y="40" width={plateForeignObjectWidth} height="600">
        <div
          style={{
            gridTemplateAreas: gridTemplateAreasCss,
            display: "grid",
            gridTemplateColumns:
              "20px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr",
            gridTemplateRows: "20px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr",
            gap: "10px 10px",
            gridAutoFlow: "row",
            padding: extraMini
              ? padRight
                ? "0px 0px 0px 0px"
                : "0px"
              : "15px 10px",
            userSelect: "none",
            // maxWidth: extraMini ? 300 : 400,
            width: "100%",
            // minWidth: 270,
          }}
        >
          <Box
            style={{
              display: "flex",
              flexDirection: "row",
              justifyContent: "center",
              alignItems: "center",
              gridArea: "columns",
              maxHeight: "15px",
            }}
          >
            {columns.map((column) => (
              <div
                key={column}
                style={{
                  width: `${100 / columns.length}%`,
                  textAlign: "center",
                }}
              >
                <Typography
                  variant="body1"
                  fontSize={extraMini ? miniFontSize : 14}
                  lineHeight={2}
                >
                  {column}
                </Typography>
              </div>
            ))}
          </Box>

          <Box
            style={{
              gridArea: "rows",
              justifyContent: "center",
              alignItems: "center",
              gap: "0px",
            }}
          >
            {rows.map((row) => (
              <div
                key={row}
                style={{
                  height: `${100 / rows.length}%`,
                  textAlign: "center",
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "start",
                }}
              >
                <Typography
                  variant="body1"
                  fontSize={extraMini ? miniFontSize : 14}
                  lineHeight={2}
                >
                  {row}
                </Typography>
              </div>
            ))}
          </Box>

          <div style={{ gridArea: "wells" }}>{wellsGrid}</div>
        </div>
      </foreignObject>
    </svg>
  );
};
