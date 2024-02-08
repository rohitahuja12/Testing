import React, { useEffect, useState, useMemo } from 'react';
import PlateWell from './brightestBio/PlateWell.jsx';
import { useSelector } from 'react-redux';
import { defaultPlateMapsSelector } from '../features/analysis/analysisSlice.js';
import { RenameUnknownsModal } from './RenameUnknownsModal.jsx';
import { WellType } from '../enums/WellType.js';
import { useWellPlateAdvancedStyles } from './styles/WellPlateAdvancedStyles.js';
import { useCallback } from 'react';
import { Grid, Box, Typography, Button } from '@mui/material';
import { grey } from '@mui/material/colors';
import { useTheme } from '@mui/material/styles';

const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

const WellPlateAdvanced = React.memo(({ ...props }) => {
    const defaultPlateMaps = useSelector(defaultPlateMapsSelector)?.map(defaultPlateMap =>
        ({ ...defaultPlateMap, label: defaultPlateMap.name, value: defaultPlateMap._id }))
    const { setWells, template, setWellTypes,
        renameUnknownsModalOpen, setRenameUnknownsModalOpen,
    } = props;
    const { classes, cx } = useWellPlateAdvancedStyles();
    const [showContextMenu, setShowContextMenu] = useState(false);
    const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
    const [contextMenuForWell, setContextMenuForWell] = useState({ show: false, x: 0, y: 0, row: null, callbacks: null });
    const [menuOpenForId, setMenuOpenForId] = useState({ id: null });
    const { setShowLoader } = props;
    const [showLabels, setShowLabels] = useState(true);
    const theme = useTheme();

    const currentWells = template.wells;

    useEffect(() => {
        setShowLoader(false);
    }, []);

    const renderMenuButton = useMemo(() => {
        return (title, callback) => (
            <Box style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: '40px',
                width: '100%',
                cursor: 'pointer',
                padding: '5px 0 5px 0',
                backgroundColor: theme.palette.mode === 'dark' ? grey[800] : grey[100],
                border: '3px solid',
                borderRadius: '4px',
                borderColor: theme.palette.mode === 'dark' ? grey[800] : grey[100],
            }}>
                <Button
                    onClick={callback}
                    color="secondary"
                    variant="outlined"
                    style={{ width: '90%'}}
                >
                    {title}
                </Button>
            </Box>
        );
    }, []);

    const getReplicateIndecesCountByWellType = (isColumn, columnOrRow, wellType) => {
        const wells = currentWells.filter(well => well.type === wellType);
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
        return currentWells.find(w => w.row === well.row && w.column === previousColumn.toString());
    }
    const getPreviousWellByRow = (well) => {
        const previousRow = rows.indexOf(well.row) - 1;
        return currentWells.find(w => w.row === rows[previousRow] && w.column === well.column);
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
        let wellChanges = [];

        if (selectedWellType === WellType.STANDARD || selectedWellType === WellType.UNKNOWN) {
            const replicateIndecesCount = getReplicateIndecesCountByWellType(menuOpenForId?.isColumn, menuOpenForId?.id?.toString(), selectedWellType);
            // series creation
            if (menuOpenForId?.isColumn) {
                rows?.forEach((row, index, arrRef) => {
                    if (selectedWellType === WellType.STANDARD && index === arrRef.length - 1) {
                        // last well in series should be blank
                        // blank should have a label like 'stnd'
                        wellChanges.push({ row: row?.toString(), column: menuOpenForId?.id?.toString(), type: WellType.BLANK, overrideLabel: 'stnd', replicateIndecesCount, index });
                    } else if (selectedWellType === WellType.UNKNOWN) {
                        const modifiedIndex = getIndexForWellTypeSet(likePrevious,
                            { row: row?.toString(), column: menuOpenForId?.id?.toString() },
                            true,
                            index,
                            replicateIndecesCount,
                            arrRef.length);
                        wellChanges.push({ row: row?.toString(), column: menuOpenForId?.id?.toString(), type: selectedWellType, replicateIndecesCount, index: modifiedIndex });
                    } else {
                        wellChanges.push({ row: row?.toString(), column: menuOpenForId?.id?.toString(), type: selectedWellType, replicateIndecesCount, index });
                    }
                });
            } else {
                columns?.forEach((column, index, arrRef) => {
                    if (selectedWellType === WellType.STANDARD && index === arrRef.length - 1) {
                        // last well in series should be blank
                        // blank should have a label like 'stnd'
                        wellChanges.push({ row: menuOpenForId?.id?.toString(), column: column?.toString(), type: WellType.BLANK, overrideLabel: 'stnd', replicateIndecesCount, index });
                    } else if (selectedWellType === WellType.UNKNOWN) {
                        const modifiedIndex = getIndexForWellTypeSet(likePrevious,
                            { row: menuOpenForId?.id?.toString(), column: column?.toString() },
                            false,
                            index,
                            replicateIndecesCount,
                            arrRef.length);
                        wellChanges.push({ row: menuOpenForId?.id?.toString(), column: column?.toString(), type: selectedWellType, replicateIndecesCount, index: modifiedIndex });
                    } else {
                        wellChanges.push({ row: menuOpenForId?.id?.toString(), column: column?.toString(), type: selectedWellType, replicateIndecesCount, index });
                    }
                });
            }
        } else {
            if (menuOpenForId?.isColumn) {
                rows?.forEach((row) => wellChanges.push({ row: row?.toString(), column: menuOpenForId?.id?.toString(), type: selectedWellType }));
            } else {
                columns?.forEach((column) => wellChanges.push({ row: menuOpenForId?.id?.toString(), column: column?.toString(), type: selectedWellType }));
            }
        }

        if (wellChanges.length > 0) {
            setWellTypes(wellChanges);
        }
    }

    const renderRowColumnMenu = useCallback(() => {
        return (<div
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
    }, [contextMenuPosition, menuOpenForId,
        showContextMenu, renderMenuButton, handleMenuSelectionForRowOrColumn,
        currentWells]);

    const renderWellContextMenu = useCallback(() => {
        return (<div
            style={{
                position: 'absolute',
                top: contextMenuForWell?.y,
                left: contextMenuForWell?.x,
                zIndex: '1',
                borderRadius: '4px',
                padding: '5px 0 5px 0',
                width: '160px',
                height: 'auto',
                margin: 0,
                boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)',
                listStyle: 'none',
            }}
        >
            {contextMenuForWell?.callbacks?.map((callback, i) => {
                return renderMenuButton(callback.label, callback.callback);
            }
            )}
        </div>)
    }, [contextMenuPosition, contextMenuForWell, renderMenuButton]);

    const getIndexByRowColumn = (row, column) => {
        const rowNumberRepresentation = (row.toLowerCase().charCodeAt(0) - 97);
        return (rowNumberRepresentation) * columns.length + (Number(column) - 1);
    }

    const wellsGrid = useMemo(() => {
        return (
            <Grid container spacing={0}>
                {rows.map((row) => {
                    return columns.map((column) => {
                        const wellData = currentWells[getIndexByRowColumn(row, column)];
                        return (<Grid item xs={1} >
                            <PlateWell
                                key={`${column}-${row}`}
                                label={wellData.label}
                                replicateIndex={wellData.replicateIndex}
                                row={wellData.row}
                                column={wellData.column}
                                knownConcentration={wellData.knownConcentration}
                                type={wellData.type}
                                showLabel={showLabels}
                                classes={classes}
                                selected={false}
                                setMenuOpenForId={setMenuOpenForId}
                                forceHideMenu={menuOpenForId.id !== `${wellData.column}-${wellData.row}`}
                                setContextMenuForWell={setContextMenuForWell}
                                setWellData={(row, column, updatedWell) => {
                                    let wellsCopy = currentWells.slice();
                                    const indexOfInterest = getIndexByRowColumn(row, column);
                                    wellsCopy[indexOfInterest] = {
                                        ...wellsCopy[indexOfInterest],
                                        label: updatedWell.label,
                                        replicateIndex: updatedWell.replicateIndex,
                                    }
                                    setWells(wellsCopy);
                                }}
                                setWellType={(row, column, type) => {
                                    let wellsCopy = currentWells.slice();
                                    const indexOfInterest = getIndexByRowColumn(row, column);
                                    wellsCopy[indexOfInterest] = {
                                        ...wellsCopy[indexOfInterest],
                                        type: type,
                                    };
                                    setWells(wellsCopy);
                                }}
                                setWellLabel={(previousLabel, newLabel, row, column, changeAll) => {
                                    const wells = currentWells.map((well) => {
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
                                    setWells(wells);
                                }}
                            />
                        </Grid>)
                    })
                })}
            </Grid>
        )
    }, [showLabels, menuOpenForId, currentWells, setWells]);
    const plateSvg = useMemo(() => {
        const colcss = Array(12).fill("columns").join(" ");
        const wellscss = Array(12).fill("wells").join(" ");
        const rowcss = `"rows ${wellscss}"\n`.repeat(8);
        const gridTemplateAreasCss = `". ${colcss}"\n${rowcss}`;

        return (
            <svg onContextMenu={(e) => { e.preventDefault() }} onClick={() => { setMenuOpenForId({ id: '' }) }} preserveAspectRatio="xMaxYMid meet" viewBox="0 0 765 800.3" fill="none" xmlns="http://www.w3.org/2000/svg" >
                <path fillOpacity={'0%'} stroke={theme.palette.mode === 'dark' ? grey[500] : grey[500]} d="M 744.7384 0.8491 H 17.3453 C 8.1784 0.8491 0.7471 9.2941 0.7471 19.7117 V 578.1976 C 0.7471 588.6157 8.1784 597.0611 17.3453 597.0611 H 744.7384 C 753.9048 597.0611 761.3366 588.6157 761.3366 578.1976 V 19.7117 C 761.3366 9.2941 753.9048 0.8491 744.7384 0.8491 Z M 45.2157 50.4782 L 45.2258 50.4671 L 45.2355 50.4556 L 59.1706 34.0105 C 62.2993 30.3179 66.6158 28.2317 71.1266 28.2317 H 698.3295 H 725.2139 C 731.403 28.2317 736.4205 33.9339 736.4205 40.9678 V 524.5317 V 555.0815 C 736.4205 562.1142 731.403 567.8177 725.2139 567.8177 H 698.3295 H 70.7432 C 66.4495 567.8177 62.3228 565.9257 59.2299 562.5404 L 44.5027 546.4259 L 44.4828 546.404 L 30.3017 529.6668 C 27.3236 526.151 25.6597 521.4628 25.6597 516.5818 V 79.9016 C 25.6597 74.7753 27.4953 69.8701 30.7447 66.3145 L 45.2157 50.4782 Z" />

                <foreignObject x="25" y="25" width="700" height="550">
                    <div
                        style={{
                            gridTemplateAreas: gridTemplateAreasCss,
                            display: 'grid',
                            gridTemplateColumns: '25px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
                            gridTemplateRows: '25px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
                            gap: '0px 0px',
                            gridAutoFlow: 'row',
                            padding: '25px 15px',
                            userSelect: 'none',
                        }}
                    >
                        <Box
                            style={{
                                display: 'flex',
                                flexDirection: 'row',
                                justifyContent: 'center',
                                alignItems: 'center',
                                gridArea: 'columns',
                                maxHeight: '15px'
                            }}
                        >
                            {columns.map((column) => (
                                <div
                                    key={column}
                                    style={{ width: `${100 / columns.length}%`, textAlign: 'center' }}
                                    onContextMenu={(args) => {
                                        setMenuOpenForId({ id: column, isRow: false, isColumn: true })
                                        args.preventDefault()
                                        setShowContextMenu(true);
                                        setContextMenuPosition({ x: args.pageX, y: args.pageY });
                                    }}
                                >
                                    <Typography variant="body1" style={{ fontWeight: 'bold' }}>
                                        {column}
                                    </Typography>
                                </div>
                            ))}
                        </Box>

                        <Box
                            style={{
                                gridArea: 'rows',
                                justifyContent: 'center',
                                alignItems: 'center',
                                gap: '0px'
                            }}
                        >
                            {rows.map((row) => (
                                <div
                                    key={row}
                                    style={{
                                        height: `${100 / rows.length}%`, textAlign: 'center',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'start',
                                    }}
                                    onContextMenu={(args) => {
                                        setMenuOpenForId({ id: row, isRow: true, isColumn: false })
                                        args.preventDefault()
                                        setShowContextMenu(true);
                                        setContextMenuPosition({ x: args.pageX, y: args.pageY });
                                    }}
                                >
                                    <Typography variant="body1" style={{ fontWeight: 'bold' }}>
                                        {row}
                                    </Typography>
                                </div>
                            ))}
                        </Box>
                        <div style={{ gridArea: 'wells' }}>
                            {wellsGrid}
                        </div>
                    </div>
                </foreignObject>
            </svg>
        );
    }, [menuOpenForId, showContextMenu, contextMenuPosition,
        classes, defaultPlateMaps,
        columns, rows,
        renderRowColumnMenu, setRenameUnknownsModalOpen, renameUnknownsModalOpen,
        currentWells, setWells]);

    return (
        <>

            {<RenameUnknownsModal
                open={renameUnknownsModalOpen}
                onClose={() => setRenameUnknownsModalOpen(false)}
                wells={currentWells}
                renameWells={(wells) => {
                    setWells(wells);
                }}
            />}
            {showContextMenu && (menuOpenForId?.isColumn || menuOpenForId?.isRow) && renderRowColumnMenu()}
            {contextMenuForWell && renderWellContextMenu()}
            {plateSvg}
        </>

    );
})

export { WellPlateAdvanced };