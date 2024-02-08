import React, { useState, useEffect, useMemo } from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import TableSortLabel from "@mui/material/TableSortLabel";
import {
  getComparator,
  stableSort,
} from "./../utils/mui_tableHeaderSortHelper";
import { TablePagination, TextField, Typography } from "@mui/material";
import { createReadableDate } from "../../../util/createReadableDate";

/**
 *
 * @param {{
 * tableLabel: string,
 * showLabel: boolean,
 * columns: Array<{
 *  label: string,
 *  field: string,
 *  sortable: boolean,
 * }>
 * orderBy: string,
 * setOrderBy: function
 * rows: Array<{}>
 * rowsPerPage: number
 * onRowClick: (event: {}, row: {}) => void
 * defaultOrder: 'asc' | 'desc'
 * showSearchBar: boolean
 * onSearch: (event: any) => void
 * }} props
 * @returns
 */
const BBTable = ({
  tableLabel,
  showLabel = false,
  columns,
  orderBy,
  setOrderBy,
  rows,
  rowsPerPage = 10,
  onRowClick,
  defaultOrder = "desc",
  showSearchBar = false,
  onSearch,
}) => {
  const [page, setPage] = useState(0);
  const [order, setOrder] = useState(defaultOrder); // asc, desc

  const handleRequestSort = (event, property) => {
    const isAsc = orderBy === property && order === "asc";
    setOrder(isAsc ? "desc" : "asc");
    setOrderBy(property);
  };

  const createSortHandler = (property) => (event) => {
    handleRequestSort(event, property);
  };

  const pageToShow = useMemo(() => {
    if (rows?.length === 0) {
      return 0;
    } else if (page > 0) {
      return Math.min(page, Math.ceil(rows?.length / rowsPerPage) - 1);
    }
  }, [rows, page, rowsPerPage]);

  const createHeaderCellFromColumn = (column) => {
    if (column.sortable) {
      return (
        <TableCell
          width={
            Math.floor(
              100 / columns.filter((c) => c?.isAction === false)?.length
            ).toString() + "%" || "100%"
          }
          sx={{
            fontSize: 16,
            fontWeight: 700,
            textAlign: column.centered ? "center" : "left",
          }}
          sortDirection={orderBy === column.field ? order : false}
          key={column.field}
        >
          <TableSortLabel
            active={orderBy === column.field}
            direction={orderBy === column.field ? order : "asc"}
            onClick={createSortHandler(column.field)}
          >
            {column.label}
          </TableSortLabel>
        </TableCell>
      );
    } else {
      return (
        <TableCell
          width={
            Math.floor(
              100 / columns.filter((c) => c?.isAction === false)?.length
            ).toString() + "%" || "100%"
          }
          sx={{
            fontSize: 16,
            fontWeight: 700,
            textAlign: column.centered ? "center" : "left",
          }}
          key={column.field}
        >
          {column.label}
        </TableCell>
      );
    }
  };

  const emptyRows = useMemo(
    () => (page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows?.length) : 0),
    [rows, page]
  );

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const getReadableValue = (value) => {
    if (value === null || value === undefined) {
      return "";
    } else if (typeof value === "string") {
      return value;
    } else if (typeof value === "number") {
      return value.toString();
    } else if (value instanceof Date) {
      return createReadableDate(value);
    } else {
      return value.toString();
    }
  };

  return (
    <Paper
      sx={{ paddingLeft: 5, paddingRight: 5, paddingTop: 4, paddingBottom: 1 }}
    >
      {showLabel && (
        <Typography
          variant="h5"
          component="div"
          sx={{ marginBottom: 2, fontWeight: 700 }}
        >
          {tableLabel}
        </Typography>
      )}
      {showSearchBar && (
        <TextField
          color="secondary"
          id="search-textbox-basic"
          label="Search"
          variant="outlined"
          fullWidth
          sx={{ marginBottom: 2 }}
          onChange={(e) => {
            setPage(0);
            onSearch(e);
          }}
        />
      )}
      <TableContainer>
        <Table
          sx={{ minWidth: 500, minHeight: 500 }}
          aria-label={tableLabel}
          color="textPrimary"
        >
          <TableHead>
            <TableRow>{columns?.map(createHeaderCellFromColumn)}</TableRow>
          </TableHead>
          <TableBody>
            {rows &&
              rows?.length > 0 &&
              stableSort(rows, getComparator(order, orderBy))
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, i) => (
                  <TableRow
                    key={"mui-tr-" + i}
                    sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
                    hover
                  >
                    {columns?.map((column, j) => {
                      const field = row[column.field];

                      if (field?.isAction) {
                        return (
                          <TableCell
                            key={"mui-td-" + j}
                            sx={{ fontSize: 14, textAlign: "center" }}
                          >
                            <div
                              style={{
                                display: "flex",
                                justifyContent: "center",
                              }}
                            >
                              <div
                                onClick={() => field.onClick()}
                                style={{ maxWidth: 20 }}
                              >
                                {field?.value}
                              </div>
                            </div>
                          </TableCell>
                        );
                      } else {
                        return (
                          <TableCell
                            key={"mui-td-" + j}
                            sx={{ fontSize: 14 }}
                            onClick={(event) => onRowClick(event, row)}
                          >
                            <div
                              style={{
                                whiteSpace: "nowrap",
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                              }}
                            >
                              {getReadableValue(field?.value)}
                            </div>
                          </TableCell>
                        );
                      }
                    })}
                  </TableRow>
                ))}
            {emptyRows > 0 && (
              <TableRow
                style={{
                  height: 52.5 * emptyRows,
                }}
              >
                <TableCell key="empty-rows" colSpan={6} />
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[rowsPerPage]}
        component="div"
        count={rows?.length || 0}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={() => {}}
        variant="outlined"
      />
    </Paper>
  );
};
export default BBTable;
