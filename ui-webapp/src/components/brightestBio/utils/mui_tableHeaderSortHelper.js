

export const descendingComparator = (a, b, orderBy) => {
  if (!a[orderBy].value) return 1;
  if (!b[orderBy].value) return -1;
  if ((b[orderBy].value < a[orderBy].value)) {
    return -1;
  }
  if (b[orderBy].value > a[orderBy].value) {
    return 1;
  }
  return 0;
}

export const getComparator = (order, orderBy) => order === 'desc'
  ? (a, b) => descendingComparator(a, b, orderBy)
  : (a, b) => -descendingComparator(a, b, orderBy);

export const stableSort = (array, comparator) => {
  const stabilizedThis = array.map((el, index) => [el, index]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

/**
 * 
 * @param {string} label 
 * @param {string} field 
 * @param {boolean} sortable 
 * @param {boolean} centered 
 * @returns 
 */
export const createColumn = (label, field, sortable, centered = false) => ({
  label,
  field,
  sortable,
  centered
});

/**
 * 
 * @param {any} value 
 * @param {boolean} isAction 
 * @returns 
 */
export const createRow = (value, isAction = false) => ({
  value,
  isAction
});
