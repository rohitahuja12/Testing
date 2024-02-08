import React, { useReducer, useEffect } from 'react';
import {
    createStyles,
    SimpleGrid,
    Group,
    Code
} from '@mantine/core';
import { useDispatch } from 'react-redux';
import Selecto from 'react-selecto';
import { setSelectedWells, setWells } from '../features/scan/scanSlice.js';
import { grey } from '@mui/material/colors';

const useStyles = createStyles((theme, _params, getRef) => ({
    plate: {
        display: 'grid',
        gridTemplateColumns: '35px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
        gridTemplateRows: '35px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
        gap: '0px 0px',
        gridAutoFlow: 'row',
        gridTemplateAreas:
            `". columns columns columns columns columns columns columns columns columns columns columns columns"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"`,
        width: '670px',
        height: '475px',
        padding: '30px 15px'
    },
    columns: {
        gridArea: 'columns',
        justifyContent: 'center',
        alignItems: 'center',
        maxHeight: '50px',
        '.column-header': {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            maxHeight: '50px'
        }
    },
    rows: {
        gap: 30,
        gridArea: 'rows',
        justifyContent: 'center',
        alignItems: 'center',
        '.row-header': {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
        }
    },
    wells: { gridArea: 'wells' },
    well: {
        textAlign: 'center'
    }
}));

const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const wellArray = Array.from({ length: 96 }, (v, i) => ({
    row: rows[Math.floor(i / 12)],
    column: columns[i % 12].toString()
}));

const initWells = {
    wells: wellArray,
    selectedWells: []
};

function plateReducer(state, action) {
    switch (action.type) {
        case 'setSelectedWells':
            return {
                ...state,
                selectedWells: action.payload.map((well) => ({
                    row: well.attributes.row.value,
                    column: well.attributes.column.value
                }))
            };
        case 'setSelectAllWells':
            return {
                ...state,
                selectedWells: state.wells
            };
        case 'setDeselectAllWells':
            return {
                ...state,
                selectedWells: []
            };
        case 'error':
            return { ...state, isError: true, error: action.error };
        default:
            throw new Error();
    }
}

export function WellPlateBasic({ ...props }) {
    const { classes, cx } = useStyles();
    const [plateState, wellsDispatch] = useReducer(plateReducer, initWells);
    const { selectAll, clearSelections, error } = props;
    const scanDispatch = useDispatch();
    const handleSelectAll = () => wellsDispatch({ type: 'setSelectAllWells' });
    const handleClearSelections = () => wellsDispatch({ type: 'setDeselectAllWells' });

    useEffect(() => {
        if (selectAll && clearSelections) {
            selectAll.current = handleSelectAll;
            clearSelections.current = handleClearSelections;
        }
    }, []);

    useEffect(() => {
        if (!props?.readOnly && !props?.skipReduxInteractions) scanDispatch(setSelectedWells(plateState.selectedWells));

        if (!props?.readOnly && props?.setScanWells) {
            props.setScanWells({
                selectedWells: plateState.selectedWells,
                wells: plateState.wells
            });
        }

    }, [plateState.selectedWells]);

    useEffect(() => {
        if (!props?.readOnly && !props?.skipReduxInteractions) scanDispatch(setWells(plateState.wells));
        if (!props?.readOnly && props?.setScanWells) {
            props.setScanWells({
                selectedWells: plateState.selectedWells,
                wells: plateState.wells
            });
        }
    }, [plateState.wells])

    // useEffect(() => {
    //     document.addEventListener('contextmenu', (e) => {
    //         e.preventDefault();
    //     });
    // }, []);

    return (
        <>
            <svg onContextMenu={(e) => {e.preventDefault()}} style={{}} preserveAspectRatio="xMaxYMid meet" viewBox="0 0 750 525" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M732.93 0.73513H17.0703C8.04872 0.73513 0.735291 8.0469 0.735291 17.0664V500.604C0.735291 509.624 8.04872 516.936 17.0703 516.936H732.93C741.951 516.936 749.265 509.624 749.265 500.604V17.0664C749.265 8.0469 741.951 0.73513 732.93 0.73513Z" fill="white" fillOpacity={'0%'} stroke={error ? 'red' : grey[400]} />
                <path d="M44.4987 43.7041L44.5087 43.6945L44.5182 43.6845L58.2324 29.4463C61.3115 26.2493 65.5596 24.443 69.9988 24.443H687.257H713.715C719.806 24.443 724.744 29.38 724.744 35.4699V454.14V480.59C724.744 486.679 719.806 491.617 713.715 491.617H687.257H69.6215C65.3959 491.617 61.3346 489.979 58.2907 487.048L43.7971 473.096L43.7775 473.077L29.8213 458.586C26.8903 455.542 25.2528 451.483 25.2528 447.257V69.1789C25.2528 64.7406 27.0594 60.4936 30.2572 57.4151L44.4987 43.7041Z" fill="white" fillOpacity={'0%'} stroke={error ? 'red' : grey[400]} />

                <foreignObject x="25" y="25" width="700" height="466">
                    <div className={`plate ${classes.plate}`}>
                        <Group grow gap={8} className={classes.columns}>
                            {columns.map((column) => (
                                <div className="column-header" key={column} style={{ userSelect: 'none' }}>
                                    {column}
                                </div>
                            ))}
                        </Group>
                        <Group grow gap={12} direction="column" className={classes.rows}>
                            {rows.map((row) => (
                                <div className="row-header" key={row} style={{ userSelect: 'none' }}>
                                    {row}
                                </div>
                            ))}
                        </Group>

                        <div className={`wells ${classes.wells}`}>
                            <SimpleGrid cols={12} spacing={10}>
                                {!props?.readOnly && plateState.wells.map((wellData, i) => {
                                    const selected = plateState.selectedWells.find((well) => well.row === wellData.row && well.column === wellData.column);
                                    return (
                                        <Well data={wellData} selected={selected} key={`${wellData.column}-${wellData.row}`} />
                                    );
                                })}
                                {props?.readOnly && props?.selectedWells && plateState.wells.map((wellData, i) => {
                                    const selected = props?.selectedWells.find((well) => well.row === wellData.row && well.column === wellData.column);
                                    return (
                                        <Well data={wellData} selected={selected} key={`${wellData.column}-${wellData.row}`} readOnly />
                                    );
                                })}
                            </SimpleGrid>
                        </div>
                    </div>
                </foreignObject>
            </svg>

            <Selecto
                dragContainer=".plate"
                selectableTargets={['.wells .well']}
                hitRate={20}
                selectByClick
                selectFromInside
                toggleContinueSelect="shift"
                toggleContinueSelectWithoutDeselect="shift"
                onSelect={(e) => {
                    e.added.forEach((el) => el.classList.add('selected'));
                    e.removed.forEach((el) => el.classList.remove('selected'));
                    wellsDispatch({ type: 'setSelectedWells', payload: e.selected });
                }}
            />
        </>
    );
}

function Well({ ...props }) {
    const { data, selected } = props;
    const { classes, cx } = useStyles();

    return (
        <div className={`well ${classes.well} ${data.column}-${data.row}`} row={data.row} column={data.column}>
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M34.6535 17.6968C34.6535 8.30792 27.0423 0.696763 17.6535 0.696763C8.26466 0.696763 0.653503 8.30792 0.653503 17.6968C0.653503 27.0856 8.26466 34.6968 17.6535 34.6968C27.0423 34.6968 34.6535 27.0856 34.6535 17.6968Z" stroke="#C4C4C4" strokeWidth="0.7165" />
                {selected && <path d="M28 18C28 12.4772 23.5228 8 18 8C12.4772 8 8 12.4772 8 18C8 23.5228 12.4772 28 18 28C23.5228 28 28 23.5228 28 18Z" fill="#1864ab" />}
            </svg>
        </div>
    );
}
