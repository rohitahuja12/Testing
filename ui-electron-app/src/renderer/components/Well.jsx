import React, { useEffect, useRef, useState } from 'react';
import { WellColor } from '../enums/WellColor';
import { WellType } from '../enums/WellType';
import {
    TextInput,
    createStyles,
    Button,
    Modal,
    Group,
    Text
} from '@mantine/core';
import { EditWellModal } from './EditWellModal.jsx';
import { useAppStyles } from '../styles/appStyles';
const WELL_FILL_PATH = 'M28 18C28 12.4772 23.5228 8 18 8C12.4772 8 8 12.4772 8 18C8 23.5228 12.4772 28 18 28C23.5228 28 28 23.5228 28 18Z';
const WELL_OUTLINE_PATH = 'M34.6535 17.6968C34.6535 8.30792 27.0423 0.696763 17.6535 0.696763C8.26466 0.696763 0.653503 8.30792 0.653503 17.6968C0.653503 27.0856 8.26466 34.6968 17.6535 34.6968C27.0423 34.6968 34.6535 27.0856 34.6535 17.6968Z';
const WELL_OUTLINE_STROKE = '#C4C4C4';
const WELL_OUTLINE_STROKE_WIDTH = '0.7165';
const WELL_OUTLINE_PATH_MINI = 'M 33.6139 17.1659 C 33.6139 8.0587 26.231 0.6759 17.1239 0.6759 C 8.0167 0.6759 0.6339 8.0587 0.6339 17.1659 C 0.6339 26.273 8.0167 33.6559 17.1239 33.6559 C 26.231 33.6559 33.6139 26.273 33.6139 17.1659 Z';
const WELL_FILL_PATH_MINI = 'M 27.02 17.02 C 27.02 11.4972 22.5428 7.02 17.02 7.02 C 11.4972 7.02 7.02 11.4972 7.02 17.02 C 7.02 22.5428 11.4972 27.02 17.02 27.02 C 22.5428 27.02 27.02 22.5428 27.02 17.02';

const useStyles = createStyles(useAppStyles);

export const Well = ({
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
    setWellData
}) => {
    const [showContextMenu, setShowContextMenu] = useState(false);
    const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
    const labelRef = useRef(null);
    const getWellId = () => `${column}-${row}`;
    const [renameModalOpened, setRenameModalOpened] = useState(false);
    const [renameValue, setRenameValue] = useState('');
    const [editWellModalOpen, setEditWellModalOpen] = useState(false);
    const { classes: appClasses, cx } = useStyles();

    useEffect(() => {
        if (forceHideMenu) {
            setShowContextMenu(false);
        }
    }, [forceHideMenu]);

    const getWellColor = (type) => {
        switch (type) {
            case WellType.BLANK: return WellColor.BLANK;
            case WellType.STANDARD: return WellColor.STANDARD;
            case WellType.UNKNOWN: return WellColor.UNKNOWN;
            case WellType.SELECTED: return WellColor.SELECTED;
            default: return WellColor.EMPTY;
        }
    }

    const renderLabel = () => (
        <TextInput
            placeholder={label || getWellId()}
            variant="unstyled"
            size="xs"
            color="gray"
            ref={labelRef}
            onKeyUp={(e) => {
                if (e.key === 'Enter') {
                    setRenameModalOpened(true);
                    setRenameValue(e.target.value);
                }
            }}
            sx={{
                overflow: 'hidden',
                maxWidth: '8ch',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                input: {
                    textAlign: 'center'
                }
            }}
        />
    )

    const renderEmptyLabel = () => (
        <TextInput
            variant="unstyled"
            size="xs"
            color="white"
            readOnly
            sx={{
                overflow: 'hidden',
                maxWidth: '8ch',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                input: {
                    textAlign: 'center',
                    cursor: 'auto'
                },
            }}
        />
    )

    const handleRenameModalAction = (changeAll) => {
        setRenameModalOpened(false);
        setWellLabel(label, renameValue, row, column, changeAll);
        labelRef.current.value = '';
    }

    const handleShowMenu = (args) => {
        setShowContextMenu(true);
        setContextMenuPosition({ x: args.pageX - 500, y: args.pageY - 370 });
        setMenuOpenForId && setMenuOpenForId({ id: getWellId() });
    }

    const renderMenuButton = (title, callback) => (<Button
        onClick={callback}
        color="dark"
        fullWidth
        variant="default"
        size='md'
    >
        {title}
    </Button>);

    const renderMenu = () => {
        return (
            <div
            className={appClasses.contextMenu}
                style={{
                    position: 'absolute',
                    top: contextMenuPosition.y,
                    left: contextMenuPosition.x,
                    zIndex: '10',
                    borderRadius: '4px',
                    padding: '5px 0 5px 0',
                    width: '200px',
                    height: 'auto',
                    margin: 0,
                    opacity: 1,
                    transition: 'opacity 0.5s linear',
                    boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.1)',
                    listStyle: 'none',
                }}
            >
                <div>
                    {renderMenuButton('Make Standard', () => { setWellType(row, column, WellType.STANDARD) })}
                    {renderMenuButton('Make Unknown', () => { setWellType(row, column, WellType.UNKNOWN) })}
                    {renderMenuButton('Make Blank', () => { setWellType(row, column, WellType.BLANK) })}
                    {renderMenuButton('Make Empty', () => { setWellType(row, column, WellType.EMPTY) })}
                    {renderMenuButton('Edit Well', () => { setEditWellModalOpen(true) })}
                </div>
            </div>
        )
    }

    return (
        <div
            onClick={() => { setMenuOpenForId && setMenuOpenForId({ id: '' }) }}
            onContextMenu={handleShowMenu}
            onBlur={() => {
                showContextMenu && setShowContextMenu(false);
            }}
            key={`${column}-${row}`}
            className={`well ${classes.well} ${column}-${row}`}
            row={row}
            column={column}
        >
            <svg width="24" height="24" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d={mini ? WELL_OUTLINE_PATH_MINI : WELL_OUTLINE_PATH} stroke={WELL_OUTLINE_STROKE} strokeWidth={WELL_OUTLINE_STROKE_WIDTH} />
                <path
                    d={mini ? WELL_FILL_PATH_MINI : WELL_FILL_PATH}
                    fill={getWellColor(type)}
                />
            </svg>

            {showContextMenu && renderMenu()}
            {(showLabel && !mini) && renderLabel()}
            {(!showLabel && !mini) && renderEmptyLabel()}
            {<EditWellModal
                open={editWellModalOpen}
                onClose={() => { setEditWellModalOpen(false) }}
                well={{ row, column, label, type, replicateIndex, knownConcentration }}
                saveWell={(updatedWell) => { setWellData(row, column, updatedWell) }}
            />}
            <Modal
                centered
                opened={renameModalOpened}
                onClose={() => setRenameModalOpened(false)}
                title={`Rename Well`}
                overlayColor="#E9ECEF"
                overlayOpacity={0.55}
                overlayBlur={1}
            >
                <Group position="center" style={{ marginBottom: 30 }}>
                    <Text
                        style={{ backgroundColor: '#f0f0f0', paddingLeft: 10, paddingRight: 10, borderRadius: 4, fontWeight: 300 }}
                        size="xl">
                        {`${label} → ${renameValue}`}
                    </Text>
                </Group>

                <Group position="center" spacing="sm">
                    <Button style={{ width: 190 }} size={'xs'} onClick={() => { handleRenameModalAction(false) }} color="dark">Rename Well</Button>
                    <Button style={{ width: 190 }} size={'xs'} onClick={() => { handleRenameModalAction(true) }} color="dark">Rename Matching Wells</Button>
                </Group>

            </Modal>
        </div>
    );
}