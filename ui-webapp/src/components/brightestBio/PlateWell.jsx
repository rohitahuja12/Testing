import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
  useMemo,
} from "react";
import { WellColor } from "../../enums/WellColor";
import { WellType } from "../../enums/WellType";
import { EditWellModal } from "../EditWellModal.jsx";
import {
  Grid,
  Typography,
  Paper,
  IconButton,
  TextField,
  Button,
  Modal,
  Box,
  Fade,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { grey } from "@mui/material/colors";

const WELL_FILL_PATH =
  "M28 18C28 12.4772 23.5228 8 18 8C12.4772 8 8 12.4772 8 18C8 23.5228 12.4772 28 18 28C23.5228 28 28 23.5228 28 18Z";
const WELL_OUTLINE_PATH =
  "M34.6535 17.6968C34.6535 8.30792 27.0423 0.696763 17.6535 0.696763C8.26466 0.696763 0.653503 8.30792 0.653503 17.6968C0.653503 27.0856 8.26466 34.6968 17.6535 34.6968C27.0423 34.6968 34.6535 27.0856 34.6535 17.6968Z";
const WELL_OUTLINE_STROKE_DARK = grey[300];
const WELL_OUTLINE_STROKE_LIGHT = grey[700];
const WELL_OUTLINE_STROKE_WIDTH = "0.7165";
const WELL_OUTLINE_PATH_MINI =
  "M 33.6139 17.1659 C 33.6139 8.0587 26.231 0.6759 17.1239 0.6759 C 8.0167 0.6759 0.6339 8.0587 0.6339 17.1659 C 0.6339 26.273 8.0167 33.6559 17.1239 33.6559 C 26.231 33.6559 33.6139 26.273 33.6139 17.1659 Z";
const WELL_FILL_PATH_MINI =
  "M 27.02 17.02 C 27.02 11.4972 22.5428 7.02 17.02 7.02 C 11.4972 7.02 7.02 11.4972 7.02 17.02 C 7.02 22.5428 11.4972 27.02 17.02 27.02 C 22.5428 27.02 27.02 22.5428 27.02 17.02";

const style = {
  position: "absolute",
  top: "50%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: 400,
  minWidth: 400,
  bgcolor: "background.modalPaper",
  boxShadow: 24,
  borderRadius: 1,
  borderColor: "secondary",
  pt: 2,
  px: 4,
  pb: 3,
};

const PlateWell = React.memo(
  ({
    label,
    replicateIndex,
    row,
    column,
    knownConcentration,
    type,
    showLabel,
    classes,
    selected,
    setMenuOpenForId,
    forceHideMenu,
    setWellType,
    mini,
    setWellLabel,
    setWellData,
    setContextMenuForWell,
    size = 24,
  }) => {
    const [showContextMenu, setShowContextMenu] = useState(false);
    const [contextMenuPosition, setContextMenuPosition] = useState({
      x: 0,
      y: 0,
    });
    const labelRef = useRef(null);
    const getWellId = () => `${column}-${row}`;
    const [renameModalOpened, setRenameModalOpened] = useState(false);
    const [renameValue, setRenameValue] = useState("");
    const [editWellModalOpen, setEditWellModalOpen] = useState(false);
    const theme = useTheme();

    useEffect(() => {
      if (forceHideMenu) {
        setShowContextMenu(false);
      }
    }, [forceHideMenu]);

    const getWellColor = (type) => {
      switch (type) {
        case WellType.BLANK:
          return WellColor.BLANK;
        case WellType.STANDARD:
          return WellColor.STANDARD;
        case WellType.UNKNOWN:
          return WellColor.UNKNOWN;
        case WellType.SELECTED:
          return WellColor.SELECTED;
        default:
          return theme.palette.mode === "dark"
            ? WellColor.EMPTY_DARK
            : WellColor.EMPTY;
      }
    };

    const renderLabel = useCallback(
      () => (
        <TextField
          placeholder={label || getWellId()}
          variant="outlined"
          size="small"
          inputRef={labelRef}
          onKeyUp={(e) => {
            if (e.key === "Enter") {
              setRenameModalOpened(true);
              setRenameValue(e.target.value);
            }
          }}
          inputProps={{
            style: {
              fontSize: 10,
              paddingLeft: 2,
              paddingRight: 2,
              paddingTop: 4,
              paddingBottom: 4,
            },
          }}
          sx={{
            overflow: "hidden",
            maxWidth: "8ch",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            input: {
              textAlign: "center",
            },
            fontSize: "8px", // size of the underline
            marginBottom: "10px",
            paddingBottom: "0px",
            paddingTop: "0px",
            marginTop: "0px",
            top: "-2px",
          }}
        />
      ),
      [label]
    );

    const renderEmptyLabel = useCallback(
      () => (
        <TextField
          variant="outlined"
          size="xs"
          readOnly
          inputProps={{
            style: { fontSize: 10, paddingLeft: 2, paddingRight: 2 },
          }}
          sx={{
            overflow: "hidden",
            maxWidth: "8ch",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            input: {
              textAlign: "center",
            },
            fontSize: "8px", // size of the underline
            marginBottom: "10px", // distance from textbox to next well
            paddingBottom: "0px",
            paddingTop: "0px",
            marginTop: "0px",
            top: "-2px", // distance from well to textbox
          }}
        />
      ),
      []
    );

    const handleRenameModalAction = useCallback(
      (changeAll) => {
        setRenameModalOpened(false);
        setWellLabel(label, renameValue, row, column, changeAll);
        labelRef.current.value = "";
      },
      [label, renameValue, row, column, setWellLabel, setRenameModalOpened]
    );

    const handleShowMenu = useCallback(
      (args) => {
        setShowContextMenu(true);
        setContextMenuForWell &&
          setContextMenuForWell({
            show: true,
            x: args.pageX,
            y: args.pageY,
            callbacks: [
              {
                label: "Make Standard",
                callback: () => {
                  setWellType(row, column, WellType.STANDARD);
                  setContextMenuForWell({
                    show: false,
                    x: 0,
                    y: 0,
                    callbacks: [],
                  });
                },
              },
              {
                label: "Make Unknown",
                callback: () => {
                  setWellType(row, column, WellType.UNKNOWN);
                  setContextMenuForWell({
                    show: false,
                    x: 0,
                    y: 0,
                    callbacks: [],
                  });
                },
              },
              {
                label: "Make Blank",
                callback: () => {
                  setWellType(row, column, WellType.BLANK);
                  setContextMenuForWell({
                    show: false,
                    x: 0,
                    y: 0,
                    callbacks: [],
                  });
                },
              },
              {
                label: "Make Empty",
                callback: () => {
                  setWellType(row, column, WellType.EMPTY);
                  setContextMenuForWell({
                    show: false,
                    x: 0,
                    y: 0,
                    callbacks: [],
                  });
                },
              },
              {
                label: "Edit Well",
                callback: () => {
                  setEditWellModalOpen(true);
                  setContextMenuForWell({
                    show: false,
                    x: 0,
                    y: 0,
                    callbacks: [],
                  });
                },
              },
            ],
          });
        // setContextMenuPosition({ x: args.pageX - 150, y: args.pageY - 550 });
        setContextMenuPosition({ x: args.pageX / 2.5, y: args.pageY - 550 });
        setMenuOpenForId && setMenuOpenForId({ id: getWellId() });
      },
      [
        setMenuOpenForId,
        getWellId,
        setShowContextMenu,
        setContextMenuPosition,
        setWellType,
        row,
        column,
        setContextMenuForWell,
        setEditWellModalOpen,
      ]
    );

    const wellSvg = useMemo(() => {
      return (
        <svg
          width={size}
          height={size}
          viewBox="0 0 36 36"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d={mini ? WELL_OUTLINE_PATH_MINI : WELL_OUTLINE_PATH}
            stroke={
              theme.palette.mode === "dark"
                ? WELL_OUTLINE_STROKE_DARK
                : WELL_OUTLINE_STROKE_LIGHT
            }
            strokeWidth={WELL_OUTLINE_STROKE_WIDTH}
          />
          <path
            d={mini ? WELL_FILL_PATH_MINI : WELL_FILL_PATH}
            fill={getWellColor(type)}
          />
        </svg>
      );
    }, [mini, type, size, theme.palette.mode]);

    return (
      <>
        <div
          onClick={() => {
            setMenuOpenForId && setMenuOpenForId({ id: "" });
          }}
          onContextMenu={handleShowMenu}
          onBlur={() => {
            showContextMenu && setShowContextMenu(false);
            setContextMenuForWell &&
              setContextMenuForWell({ show: false, x: 0, y: 0, callbacks: [] });
          }}
          key={`${column}-${row}`}
          className={`well ${classes.well} ${column}-${row}`}
          row={row}
          column={column}
        >
          {wellSvg}
          {showLabel && !mini && renderLabel()}
          {!showLabel && !mini && renderEmptyLabel()}
          {
            <EditWellModal
              open={editWellModalOpen}
              onClose={() => {
                setEditWellModalOpen(false);
              }}
              well={{
                row,
                column,
                label,
                type,
                replicateIndex,
                knownConcentration,
              }}
              saveWell={(updatedWell) => {
                setWellData(row, column, updatedWell);
              }}
            />
          }
          <Modal
            open={renameModalOpened}
            onClose={() => setRenameModalOpened(false)}
            aria-labelledby={`Rename Well`}
            aria-describedby="modal-modal-description"
            closeAfterTransition
          >
            <Fade in={renameModalOpened}>
              <Box sx={{ ...style, width: 300 }}>
                <Grid
                  container
                  spacing={2}
                  direction="column"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Grid item xs={12}>
                    <Typography
                      variant="h3"
                      component="span"
                      style={{
                        backgroundColor:
                          theme.palette.mode === "dark" ? grey[700] : grey[300],
                        borderRadius: 4,
                        fontWeight: 300,
                        textAlign: "center",
                        paddingLeft: 10,
                        paddingRight: 10,
                      }}
                    >
                      {`${label} → ${renameValue}`}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Button
                      style={{ width: 190 }}
                      color="secondary"
                      variant="outlined"
                      onClick={() => {
                        handleRenameModalAction(false);
                      }}
                    >
                      Rename Well
                    </Button>
                  </Grid>
                  <Grid item xs={6}>
                    <Button
                      style={{ width: 190 }}
                      color="secondary"
                      variant="outlined"
                      onClick={() => {
                        handleRenameModalAction(true);
                      }}
                    >
                      Rename Matching Wells
                    </Button>
                  </Grid>
                </Grid>
              </Box>
            </Fade>
          </Modal>
        </div>
      </>
    );
  }
);

export default PlateWell;
