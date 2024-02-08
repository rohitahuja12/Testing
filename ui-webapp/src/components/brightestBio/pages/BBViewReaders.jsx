import React, {
  useMemo,
  useState,
} from "react";
import { Grid, Typography, Paper, Button } from "@mui/material";
import { useReaders } from "../hooks/useReaders";
import BBViewShell from "../BBViewShell";
import { useNavigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BBTable from "../reusable/BBTable";
import { createColumn, createRow } from "../utils/mui_tableHeaderSortHelper";
import { BBViewPageLoader } from "../BBViewPageLoader";

/**
 * @typedef {import("./reader.types").Reader} Reader
 */

const BBViewReaders = ({ screenTitle, signOut }) => {
  const navigate = useNavigate();
  const { readers } = useReaders();
  const [orderBy, setOrderBy] = useState("serialNumber");
  const [rowsPerPage] = useState(6);

  const columns = useMemo(
    () => [
      createColumn("Serial Number", "serialNumber", true),
      createColumn("Door", "door", true),
      createColumn("Laser", "laser", true),
    ],
    []
  );

  const rows = useMemo(
    () =>
      readers?.map((reader) => ({
        id: createRow(reader?._id),
        serialNumber: createRow(reader?.serialNumber),
        door: createRow(reader?.status?.door || "unknown"),
        laser: createRow(reader?.status?.laser || "unknown"),
      })),
    [readers]
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
        <Grid item xs={12}>
          <Paper>
            <BBViewPageLoader loadingText="Loading Readers">
              <BBTable
                columns={columns}
                rows={rows}
                orderBy={orderBy}
                setOrderBy={setOrderBy}
                tableLabel="Readers"
                rowsPerPage={rowsPerPage}
                onRowClick={(event, row) => {}}
              />
            </BBViewPageLoader>
          </Paper>
        </Grid>
      </Grid>
    </BBViewShell>
  );
};

export default BBViewReaders;
