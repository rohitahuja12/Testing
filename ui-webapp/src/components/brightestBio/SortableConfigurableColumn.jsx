import React from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import ConfigurableColumn from "./ConfigurableColumn";

/**
 * @param {{
 * column: {field: string, label: string, hidden: boolean, preventConfiguration?: boolean}
 * setColumnsFromChangeEvent: Function
 * }}
 */
const SortableConfigurableColumn = ({
  column,
  setColumnsFromChangeEvent,
  id,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });
  const style = {
    transition,
    opacity: isDragging ? 0.5 : 1,
    transform: CSS.Translate.toString(transform),
  };

  return (
    <ConfigurableColumn
      id={id}
      ref={setNodeRef}
      style={style}
      attributes={attributes}
      listeners={listeners}
      column={column}
      setColumnsFromChangeEvent={setColumnsFromChangeEvent}
      transform={transform}
      isDragging={isDragging}
    />
  );
};

export default SortableConfigurableColumn;
