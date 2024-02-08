import React, { useMemo, useState } from "react";
import {
  Modal,
  List,
  ListItem,
  Box,
  Fade,
  Typography,
  Paper,
  ListItemIcon,
  Checkbox,
  ListSubheader,
  ListItemText,
} from "@mui/material";
import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  MouseSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import ConfigurableColumn from "./ConfigurableColumn";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import SortableConfigurableColumn from "./SortableConfigurableColumn";
import { SortableOverlay } from "./dndcore/SortableOverlay";

const style = {
  bgcolor: "background.modalPaper",
  boxShadow: 24,
  borderRadius: 1,
  border: "none",
  pt: 2,
  px: 4,
  pb: 3,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
};

/**
 * @param {{
 * open: boolean,
 * onClose: Function,
 * columns: {field: string, label: string, preventConfiguration?: boolean}[],
 * setColumns: Function
 * }} props
 */

/**
 * @param {{field: string, label: string, preventConfiguration?: boolean}} column
 * @param {Function} setColumns
 * @param {{field: string, label: string, preventConfiguration?: boolean}[]} columns
 */
const setColumnsFromChangeEvent =
  (column, setColumns, columns, disableLastCheckbox) =>
  /**
   * @param {React.ChangeEvent<HTMLInputElement>} event
   */
  (event) => {
    console.log(event.target.checked);
    if (disableLastCheckbox && !event.target.checked) {
      return;
    }
    setColumns(
      columns.map((col) => {
        if (col.field === column.field) {
          return {
            ...col,
            hidden: !event.target.checked,
          };
        }
        return col;
      })
    );
  };

const ConfigureTableModal = ({ open, onClose, columns, setColumns }) => {
  const [activeColumn, setActiveColumn] = useState(null);
  const disableLastCheckbox = useMemo(() => {
    return (
      columns.filter((col) => !col?.hidden && !col?.preventConfiguration)
        .length === 1
    );
  });
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
    useSensor(MouseSensor, {
      activationConstraint: {
        distance: 2,
      },
    })
  );
  const handleDragStart = (event) => {
    const { active } = event;
    const activeColumn = columns.find((col) => col.field === active.id);
    if (activeColumn) {
      setActiveColumn(activeColumn);
    }
  };
  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (active.id !== over.id) {
      const activeIndex = columns.findIndex((col) => col.field === active.id);
      const overIndex = columns.findIndex((col) => col.field === over.id);
      const newColumns = [...columns];
      newColumns.splice(overIndex, 0, newColumns.splice(activeIndex, 1)[0]);
      setColumns(newColumns);
    }
    setActiveColumn(null);
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="configure-table"
      aria-describedby="allows users to configure the table"
      closeAfterTransition
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Fade in={open}>
        <Box sx={{ ...style, width: 300 }}>
          <DndContext
            sensors={sensors}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            collisionDetection={closestCenter}
            // measuring={{
            //   draggable: {
            //     measure: (node) => {
            //       console.log("the measured node: ", node);
            //       // console.log("children: ", node.children);
            //       console.log("getBoundingClientRect: ", node.getBoundingClientRect());
            //       return node.getBoundingClientRect();
            //     },
            //   },
            // }}
          >
            <List
              sx={{
                width: "100%",
                maxWidth: 360,
                bgcolor: "background.modalPaper",
              }}
              title="Configure Table"
              subheader={
                <ListSubheader sx={{ bgcolor: "background.modalPaper" }}>
                  Columns to Display
                </ListSubheader>
              }
            >
              <SortableContext
                items={columns.map((col) => ({ ...col, id: col.field }))}
              >
                {columns
                  .filter((col) => !col?.preventConfiguration)
                  .map((column) => {
                    return (
                      <SortableConfigurableColumn
                        id={column.field}
                        column={column}
                        setColumnsFromChangeEvent={setColumnsFromChangeEvent(
                          column,
                          setColumns,
                          columns,
                          disableLastCheckbox
                        )}
                      />
                    );
                  })}
              </SortableContext>
              <SortableOverlay>
                {activeColumn ? (
                  <ConfigurableColumn
                    id={activeColumn.field}
                    column={activeColumn}
                    setColumnsFromChangeEvent={setColumnsFromChangeEvent(
                      activeColumn,
                      setColumns,
                      columns,
                      disableLastCheckbox
                    )}
                  />
                ) : null}
              </SortableOverlay>
            </List>
          </DndContext>
        </Box>
      </Fade>
    </Modal>
  );
};

export default ConfigureTableModal;
