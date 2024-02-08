import React, { useReducer, useEffect, useState } from 'react';
import {
    SimpleGrid,
    Group,
    Box,
    Switch,
    Button,
    createStyles
} from '@mantine/core';
import Selecto from 'react-selecto';
import { Well } from './Well.jsx';
import { PlateDropDown } from './PlateDropDown.jsx';
import { getDefaultPlateMaps } from './../actions/analysisTemplateActions.js';
import { useSelector, useDispatch } from 'react-redux';
import { defaultPlateMapsSelector } from '../features/analysis/analysisSlice.js';
import { RenameUnknownsModal } from './RenameUnknownsModal.jsx';
import { WellType } from '../enums/WellType.js';
import { useWellPlateAdvancedStyles } from './styles/WellPlateAdvancedStyles.js';
import { useAppStyles } from '../styles/appStyles.js';

const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
const wellArray = Array.from({ length: 96 }, (v, i) => ({
    label: `${rows[Math.floor(i / 12)]}${columns[i % 12]}`,
    row: rows[Math.floor(i / 12)],
    column: columns[i % 12].toString(),
    type: 'empty',
    knownConcentration: 1000.0,
    replicateIndex: 0
}));

const initWells = {
    wells: wellArray,
    selectedWells: [],
    showLabels: true
};

const useStyles = createStyles(useAppStyles);

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
        case 'setDeselectAllWells':
            return {
                ...state,
                wells: wellArray,
                selectedWells: []
            };
        case 'setShowLabels':
            return {
                ...state,
                showLabels: !state.showLabels
            };
        case 'setWells': //set the wells outright. This is used when the user is editing the labels
            return {
                ...state,
                wells: action.payload
            }
        case 'setWellType':
            const getWellTypeShorthand = (longType) => {
                if (longType === WellType.STANDARD) return 'stnd';
                if (longType === WellType.UNKNOWN) return 'unk';
                return 'empty';
            };

            const capitlizeFirstLetter = (string) => {
                return string.charAt(0).toUpperCase() + string.slice(1);
            }

            return {
                ...state,
                wells: state.wells.map((well) => {
                    if (well.row === action.payload.row && well.column === action.payload.column) {
                        return Number.isInteger(action.payload.replicateIndecesCount)
                            ? {
                                ...well,
                                type: action.payload.type,
                                replicateIndex: action.payload.replicateIndecesCount + 1,
                                label: `${getWellTypeShorthand(action.payload.type)}${action.payload.index + 1}`
                            }
                            : {
                                ...well,
                                type: action.payload.type
                            };
                    }
                    return well;
                })
            };
        case 'error':
            return { ...state, isError: true, error: action.error };
        default:
            throw new Error();
    }
}

export const WellPlateAdvanced = ({ ...props }) => {
    const defaultPlateMaps = useSelector(defaultPlateMapsSelector)?.map(defaultPlateMap =>
        ({ ...defaultPlateMap, label: defaultPlateMap.name, value: defaultPlateMap._id }));
    const templatedWells = useSelector(state => state?.analysis?.templatedWells);
    const { classes, cx } = useWellPlateAdvancedStyles();
    const { classes: appClasses } = useStyles();
    const [plateState, plateDispatch] = useReducer(plateReducer,
        templatedWells ? { selectedWells: [], showLabels: true, wells: templatedWells } : initWells
    );
    const [showContextMenu, setShowContextMenu] = useState(false);
    const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
    const { error } = props;
    const [menuOpenForId, setMenuOpenForId] = useState({ id: null });
    const [renameUnknownsModalOpen, setRenameUnknownsModalOpen] = useState(false);
    const dispatch = useDispatch();
    const { onWellChanges } = props;

    const handleClearSelections = () => plateDispatch({ type: 'setDeselectAllWells' });

    const renderMenuButton = (title, callback) => (<Button
        onClick={callback}
        color="dark"
        fullWidth
        variant="default"
        size='xs'
    >
        {title}
    </Button>);

    const getReplicateIndecesCountByWellType = (isColumn, columnOrRow, wellType) => {
        const wells = plateState?.wells.filter(well => well.type === wellType);
        const replicateIndeces = wells.reduce((acc, well) => {
            if (isColumn) {
                if (well.column === columnOrRow) {
                    return acc;
                }
            } else {
                if (well.row === columnOrRow) {
                    return acc;
                }
            }
            if (!acc.find(replicateIndex => replicateIndex === well.replicateIndex)) {
                acc.push(well.replicateIndex);
            }
            return acc;
        }, []);
        return replicateIndeces.length;
    }

    //get well in the same row but from the previous column
    const getPreviousWellByColumn = (well) => {
        const previousColumn = Number(well.column) - 1;
        return plateState.wells.find(w => w.row === well.row && w.column === previousColumn.toString());
    }
    const getPreviousWellByRow = (well) => {
        const previousRow = rows.indexOf(well.row) - 1;
        return plateState.wells.find(w => w.row === rows[previousRow] && w.column === well.column);
    }

    const getPreviousWell = (likePrevious, well, isColumn) => {
        if (likePrevious && isColumn && well.column !== 1) return getPreviousWellByColumn(well);
        if (likePrevious && !isColumn && well.row !== rows[0]) return getPreviousWellByRow(well);

        return null;
    }

    const getIndexForWellTypeSet = (likePrevious, well, isColumn, index, replicateIndecesCount, arrLength) => {
        const previousWell = getPreviousWell(true, well, isColumn);
        if (likePrevious && previousWell && previousWell.label.toLowerCase().includes('unk')) {
            const unknownLabelId = Number(previousWell.label.replace('unk', '')); // 9
            return unknownLabelId - 1; // setWellType expects index to be 0-based
        } else if (!likePrevious && previousWell && previousWell.label.toLowerCase().includes('unk')) {
            const unknownLabelId = Number(previousWell.label.replace('unk', '')); // 9
            return unknownLabelId + arrLength - 1; // setWellType expects index to be 0-based
        }

        return (index) + (replicateIndecesCount * arrLength);
    }

    const handleMenuSelectionForRowOrColumn = (selectedWellType, likePrevious = false) => () => {
        setMenuOpenForId({ id: '' });
        setShowContextMenu(false);

        if (selectedWellType === WellType.STANDARD || selectedWellType === WellType.UNKNOWN) {
            const replicateIndecesCount = getReplicateIndecesCountByWellType(menuOpenForId?.isColumn, menuOpenForId?.id?.toString(), selectedWellType);
            if (menuOpenForId?.isColumn) {
                rows?.forEach((row, index, arrRef) => {
                    if (selectedWellType === WellType.STANDARD && index === arrRef.length - 1) {
                        // last well in series should be blank
                        plateDispatch({ type: 'setWellType', payload: { row: row?.toString(), column: menuOpenForId?.id?.toString(), type: WellType.BLANK } });
                    } else if (selectedWellType === WellType.UNKNOWN) {
                        const modifiedIndex = getIndexForWellTypeSet(likePrevious,
                            { row: row?.toString(), column: menuOpenForId?.id?.toString() },
                            true,
                            index,
                            replicateIndecesCount,
                            arrRef.length);
                        plateDispatch({ type: 'setWellType', payload: { row: row?.toString(), column: menuOpenForId?.id?.toString(), type: selectedWellType, replicateIndecesCount, index: modifiedIndex } });
                    } else {
                        plateDispatch({ type: 'setWellType', payload: { row: row?.toString(), column: menuOpenForId?.id?.toString(), type: selectedWellType, replicateIndecesCount, index } });
                    }
                });
            } else {
                columns?.forEach((column, index, arrRef) => {
                    if (selectedWellType === WellType.STANDARD && index === arrRef.length - 1) {
                        plateDispatch({ type: 'setWellType', payload: { row: menuOpenForId?.id?.toString(), column: column?.toString(), type: WellType.BLANK } });
                    } else if (selectedWellType === WellType.UNKNOWN) {
                        const modifiedIndex = getIndexForWellTypeSet(likePrevious,
                            { row: menuOpenForId?.id?.toString(), column: column?.toString() },
                            false,
                            index,
                            replicateIndecesCount,
                            arrRef.length);
                        plateDispatch({ type: 'setWellType', payload: { row: menuOpenForId?.id?.toString(), column: column?.toString(), type: selectedWellType, replicateIndecesCount, index: modifiedIndex } });
                    } else {
                        plateDispatch({ type: 'setWellType', payload: { row: menuOpenForId?.id?.toString(), column: column?.toString(), type: selectedWellType, replicateIndecesCount, index } });
                    }
                });
            }
        } else {
            if (menuOpenForId?.isColumn) {
                rows?.forEach((row) => plateDispatch({ type: 'setWellType', payload: { row: row?.toString(), column: menuOpenForId?.id?.toString(), type: selectedWellType } }));
            } else {
                columns?.forEach((column) => plateDispatch({ type: 'setWellType', payload: { row: menuOpenForId?.id?.toString(), column: column?.toString(), type: selectedWellType } }));
            }
        }

    }

    const renderRowColumnMenu = () => (<div
        className={appClasses.contextMenu}
        style={{
            position: 'absolute',
            top: contextMenuPosition.y,
            left: contextMenuPosition.x,
            zIndex: '1',
            borderRadius: '4px',
            padding: '5px 0 5px 0',
            width: '160px',
            height: 'auto',
            margin: 0,
            opacity: 1,
            transition: 'opacity 0.5s linear',
            boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)',
            listStyle: 'none',
        }}
    >
        {renderMenuButton('Make Standard', handleMenuSelectionForRowOrColumn(WellType.STANDARD))}
        {renderMenuButton('Make Unknown', handleMenuSelectionForRowOrColumn(WellType.UNKNOWN))}
        {renderMenuButton('Copy Unknown', handleMenuSelectionForRowOrColumn(WellType.UNKNOWN, true))}
        {renderMenuButton('Make Blank', handleMenuSelectionForRowOrColumn(WellType.BLANK))}
        {renderMenuButton('Make Empty', handleMenuSelectionForRowOrColumn(WellType.EMPTY))}
    </div>)

    useEffect(() => {
        dispatch(getDefaultPlateMaps());
    }, [])

    return (
        <>
            {<RenameUnknownsModal
                open={renameUnknownsModalOpen}
                onClose={() => setRenameUnknownsModalOpen(false)}
                wells={plateState.wells}
                renameWells={(wells) => {
                    plateDispatch({ type: 'setWells', payload: wells });
                    onWellChanges(wells);
                }}
            />}
            <Box sx={classes.topControls}>
                <div className="section center">
                    {defaultPlateMaps && <PlateDropDown
                        onChange={(selection) => {
                            const wells = defaultPlateMaps?.find(template => selection === template._id).map
                                ?.map(well => well.label ? well : ({ ...well, }));
                            plateDispatch({ type: 'setWells', payload: wells });
                            onWellChanges(wells);
                        }}
                        title="Standard Plate Maps"
                        optionList={defaultPlateMaps} />}
                </div>
                {showContextMenu && (menuOpenForId?.isColumn || menuOpenForId?.isRow) && renderRowColumnMenu()}

                <div className="section middle">
                    <Button className={appClasses.actionButton} compact onClick={() => setRenameUnknownsModalOpen(true)}>
                        Rename Unknowns
                    </Button>
                    <Button className={appClasses.actionButton}  compact onClick={() => handleClearSelections()}>
                        Clear Plate
                    </Button>
                </div>

                <div className="section right">
                    <Group>
                        <Switch
                            label="Show Labels"
                            color="dark"
                            size="xs"
                            sx={classes.controlsToggles}
                            checked={plateState.showLabels} // Ian requested show labels be defaulted to true
                            onChange={() => plateDispatch({ type: 'setShowLabels' })}
                        />
                    </Group>
                </div>
            </Box>

            <svg onClick={() => { setMenuOpenForId({ id: '' }) }} width="750" height="518" viewBox="0 0 935.7 645.3" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginLeft: '10%' }}>
                <path className={classes.backplate} d="M 744.7384 0.8491 H 17.3453 C 8.1784 0.8491 0.7471 9.2941 0.7471 19.7117 V 578.1976 C 0.7471 588.6157 8.1784 597.0611 17.3453 597.0611 H 744.7384 C 753.9048 597.0611 761.3366 588.6157 761.3366 578.1976 V 19.7117 C 761.3366 9.2941 753.9048 0.8491 744.7384 0.8491 Z M 45.2157 50.4782 L 45.2258 50.4671 L 45.2355 50.4556 L 59.1706 34.0105 C 62.2993 30.3179 66.6158 28.2317 71.1266 28.2317 H 698.3295 H 725.2139 C 731.403 28.2317 736.4205 33.9339 736.4205 40.9678 V 524.5317 V 555.0815 C 736.4205 562.1142 731.403 567.8177 725.2139 567.8177 H 698.3295 H 70.7432 C 66.4495 567.8177 62.3228 565.9257 59.2299 562.5404 L 44.5027 546.4259 L 44.4828 546.404 L 30.3017 529.6668 C 27.3236 526.151 25.6597 521.4628 25.6597 516.5818 V 79.9016 C 25.6597 74.7753 27.4953 69.8701 30.7447 66.3145 L 45.2157 50.4782 Z" />

                <foreignObject x="25" y="25" width="700" height="550">
                    <div className={`plate ${classes.plate}`}>
                        <Group grow gap={5} className={classes.columns}>
                            {columns.map((column) => (
                                <div
                                    className="column-header"
                                    key={column}
                                    onContextMenu={(args) => {
                                        setMenuOpenForId({ id: column, isRow: false, isColumn: true })
                                        args.preventDefault()
                                        setShowContextMenu(true);
                                        setContextMenuPosition({ x: args.pageX - 75, y: args.pageY - 30 });
                                    }}
                                >
                                    {column}
                                </div>
                            ))}
                        </Group>
                        <Group grow gap={8} direction="column" className={classes.rows}>
                            {rows.map((row) => (
                                <div
                                    className="row-header"
                                    key={row}
                                    onContextMenu={(args) => {
                                        setMenuOpenForId({ id: row, isRow: true, isColumn: false })
                                        args.preventDefault()
                                        setShowContextMenu(true);
                                        setContextMenuPosition({ x: args.pageX - 75, y: args.pageY - 30 });
                                    }}
                                >
                                    {row}
                                </div>
                            ))}
                        </Group>

                        <div className={`wells ${classes.wells}`}>
                            <SimpleGrid cols={12} spacing={plateState.showLabels ? 0 : 0}>
                                {plateState.wells.map((wellData, i) => {
                                    const selected = plateState.selectedWells.find((well) => well.row === wellData.row && well.column === wellData.column);

                                    return (
                                        <Well
                                            key={i}
                                            label={wellData.label}
                                            replicateIndex={wellData.replicateIndex}
                                            row={wellData.row}
                                            column={wellData.column}
                                            knownConcentration={wellData.knownConcentration}
                                            type={wellData.type}
                                            showLabel={plateState.showLabels}
                                            classes={classes}
                                            selected={selected}
                                            setMenuOpenForId={setMenuOpenForId}
                                            forceHideMenu={menuOpenForId.id !== `${wellData.column}-${wellData.row}`}
                                            setWellData={(row, column, updatedWell) => {
                                                const wells = plateState.wells.map((well) => {
                                                    if (well.row === row && well.column === column) {
                                                        return {
                                                            ...well,
                                                            label: updatedWell.label,
                                                            replicateIndex: updatedWell.replicateIndex,
                                                        };
                                                    }
                                                    return well;
                                                })
                                                plateDispatch({ type: 'setWells', payload: wells });
                                                onWellChanges(wells);
                                            }}
                                            setWellType={(row, column, type) => {
                                                const wells = plateState.wells.map((well) => {
                                                    if (well.row === row && well.column === column) {
                                                        return {
                                                            ...well,
                                                            type: type
                                                        };
                                                    }
                                                    return well;
                                                })
                                                plateDispatch({ type: 'setWells', payload: wells });
                                                onWellChanges(wells);
                                            }}
                                            setWellLabel={(previousLabel, newLabel, row, column, changeAll) => {
                                                const wells = plateState.wells.map((well) => {
                                                    if (changeAll) {
                                                        if (well.label === previousLabel) {
                                                            return {
                                                                ...well,
                                                                label: newLabel
                                                            };
                                                        }
                                                    } else if (well.row === row && well.column === column) {
                                                        return {
                                                            ...well,
                                                            label: newLabel
                                                        };
                                                    }
                                                    return well;
                                                })
                                                plateDispatch({ type: 'setWells', payload: wells });
                                                onWellChanges(wells);
                                            }}
                                        />
                                    );
                                })}
                            </SimpleGrid>
                        </div>
                    </div>
                </foreignObject>
            </svg>

            <Button variant="subtle" color="orange" radius="xl" size="xs"
                onClick={() => console.log('plate map: ', plateState?.wells)}>
                dev: log plate map
            </Button>

            <Selecto
                dragContainer=".plate"
                selectableTargets={['.wells .well']}
                hitRate={20}
                selectByClick
                selectFromInside
                toggleContinueSelect="shift"
                ratio={0}
                onSelect={(e) => {
                    plateDispatch({ type: 'setSelectedWells', payload: e.selected });
                    e.added.forEach((el) => el.classList.add('selected'));
                    e.removed.forEach((el) => el.classList.remove('selected'));
                }}
            />
        </>
    );
}
