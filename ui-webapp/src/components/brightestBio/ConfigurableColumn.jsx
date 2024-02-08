import { Checkbox, ListItem, ListItemIcon, ListItemText } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { forwardRef } from "react";
import DragIndicatorIcon from "@mui/icons-material/DragIndicator";
import { useTheme } from '@mui/material/styles';

/**
 * @param {{
 * column: {field: string, label: string, hidden: boolean, preventConfiguration?: boolean}
 * setColumnsFromChangeEvent: Function
 * }}
 */
const ConfigurableColumn = forwardRef(
  (
    {
      column,
      setColumnsFromChangeEvent,
      attributes,
      listeners,
      isDragging,
      style,
      transform,
      id,
    },
    ref
  ) => {
    const theme = useTheme();


    return (
      <ListItem
        id={id}
        key={id}
        style={{
          ...style,
          border: `1px solid ${theme.palette.mode === 'dark' ? grey[800] : grey[300]}`,
          marginBottom: 5,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexDirection: "row",
          alignItems: "center",
        }}
        ref={ref}
      >
        <ListItemIcon>
          <Checkbox
            edge="start"
            checked={!column.hidden}
            tabIndex={-1}
            disableRipple
            inputProps={{ "aria-labelledby": column.field }}
            onChange={setColumnsFromChangeEvent}
            sx={{
              color: "secondary.main",
              "&.Mui-checked": {
                color: "secondary.main",
              },
            }}
          />
        </ListItemIcon>
        <ListItemText style={{ textAlign: "center" }} primary={column.label} />
        <ListItemIcon
          style={{
            cursor: "grab",
            display: "flex",
            alignItems: "center",
            justifyContent: "end",
          }}
          {...attributes}
          {...listeners}
        >
          <DragIndicatorIcon />
        </ListItemIcon>
      </ListItem>
    );
  }
);

export default ConfigurableColumn;
