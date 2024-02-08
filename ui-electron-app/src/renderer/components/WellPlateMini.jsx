import React, { useReducer, useEffect } from 'react';
import {
  createStyles,
  SimpleGrid,
  Group
} from '@mantine/core';
import { useWellPlateMiniStyles } from './styles/WellPlateMiniStyles';
import { Well } from './Well.jsx';

const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const wellArray = Array.from({ length: 96 }, (v, i) => ({
  row: rows[Math.floor(i / 12)],
  column: columns[i % 12].toString(),
  type: 'empty'
}));

const initWells = {
  wells: wellArray
};

function plateReducer(state, action) {
  switch (action.type) {
    case 'setWells':
      return {
        ...state,
        wells: state.wells.map((stateWell) => {
          const newState = action.payload?.find((actionWell) => actionWell.row === stateWell.row && actionWell.column.toString() === stateWell.column);
          return newState || stateWell;
        })
      };
    case 'error':
      return { ...state, isError: true, error: action.error };
    default:
      throw new Error();
  }
}

// const Well = ({ ...props }) => {
//   const { isOn } = props;
//   const { classes, cx } = useWellPlateMiniStyles();

//   return (
//     <div className={`${classes.well} ${isOn?.column}-${isOn?.row}`}>
//       <svg width="16" height="15" viewBox="0 0 16 15" fill="none" xmlns="http://www.w3.org/2000/svg">
//         <rect x="1.23378" y="0.852917" width="13.6047" height="13.6047" rx="6.80233" stroke="#C4C4C4" strokeWidth="0.530052" />
//         {isOn && <rect x="3.79688" y="3.41406" width="8.48083" height="8.48083" rx="4.24042" fill="#1C7ED6" />}
//       </svg>
//     </div>
//   );
// }

export const WellPlateMini = ({ ...props }) => {
  const { classes, cx } = useWellPlateMiniStyles();
  const [plateState, dispatch] = useReducer(plateReducer, initWells);
  const { wells } = props;

  useEffect(() => {
    dispatch({ type: 'setWells', payload: wells?.wells });
  }, []);

  return (
    <div className={classes.plate}>
      <Group grow spacing="xs" mb={10} className={classes.columns}>
        {columns.map((column) => (
          <div className="column-header" key={column}>
            {column}
          </div>
        ))}
      </Group>
      <Group grow spacing={18} mb={10} direction="column" className={classes.rows}>
        {rows.map((row) => (
          <div className="row-header" key={row} style={{ marginTop: 6 }}>
            {row}
          </div>
        ))}
      </Group>
      <SimpleGrid cols={12} spacing={10} className={classes.wells}>
        {wells?.map((wellData, i) => {
          const isOn = wells?.find((well) => well.row === wellData.row && well.column === wellData.column);

          return (
            <Well
              classes={classes}
              key={`${wellData.column}-${wellData.row}`}
              row={wellData.row}
              column={wellData.column}
              replicateGroup={wellData.replicateGroup}
              type={wellData.type}
              replicateId={wellData.replicateId}
              mini
            />
          );
        })}
      </SimpleGrid>
    </div>
  );
}
