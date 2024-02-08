import { useDispatch, useSelector } from "react-redux";
import { Grid, Typography } from "@mui/material";
import React from "react";
import { BBLoader } from "./BBLoader";
/** @typedef {import('./../../store').Store} Store */

export const BBViewPageLoader = (
  /** @type {{
   * loadingText: string,
   * children: React.ReactNode
   *  }} */
  { loadingText, children }
) => {
  const appIsLoadingData = useSelector(
    (
      /** @type {Store} */
      state
    ) => state?.system?.loadingData
  );

  return (
    <>
      {appIsLoadingData && (
        <Grid
          container
          spacing={3}
          direction="column"
          alignItems="center"
          justifyContent="center"
        >
          <Grid
            item
            xs={12}
            ml={5}
            mr={5}
            direction="row"
            alignItems="center"
            justifyContent="center"
          >
            <Typography variant="h4" component="h2" mb={2}>
              {loadingText}
            </Typography>
            <div style={{ textAlign: "center" }}>
              <BBLoader size="lg" />
            </div>
          </Grid>
        </Grid>
      )}
      {!appIsLoadingData && <>{children}</>}
    </>
  );
};
