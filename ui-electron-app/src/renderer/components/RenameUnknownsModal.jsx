import { Button, Modal, Table, Text, TextInput } from '@mantine/core';
import React, { useCallback, useState } from 'react';
import { useEffect } from 'react';
import { WellType } from '../enums/WellType';


export const RenameUnknownsModal = ({
    open,
    onClose, //aka set modal open
    wells,
    renameWells,
}) => {
    const [renamedWells, setRenamedWells] = useState(wells);

    useEffect(() => {
        setRenamedWells(wells);
    }, [wells])

    const rows = wells
        .filter(well => well.type === WellType.UNKNOWN)
        .sort((a, b) => Number(a.column) - Number(b.column))
        .map((well) => (
            <tr key={`${well.column}-${well.row}`}>
                <td>{well.label}</td>
                <td>
                    <TextInput
                        placeholder={well.label}
                        variant="unstyled"
                        size="xs"
                        required
                        onBlur={(e) => {
                            const newLabel = e?.target?.value;
                            if (newLabel) {
                                const willBeDuplicate = wells.find(w => w.label === newLabel);

                                if (willBeDuplicate) {
                                    // ac: https://auragentbioscience.slack.com/archives/C03H7B3ME4T/p1657556682053649?thread_ts=1657553977.755529&cid=C03H7B3ME4T
                                    const wellsWithSameLabel = wells.filter(w => w.label === well.label);

                                    setRenamedWells(renamedWells.map(w => (
                                        (wellsWithSameLabel.find(wellInGroup => wellInGroup.row === w.row && wellInGroup.column === w.column))
                                            ? { ...w, label: e.target.value, replicateId: willBeDuplicate.replicateId, replicateGroup: willBeDuplicate.replicateGroup }
                                            : w)));
                                } else {
                                    // find all wells with the same label
                                    const wellsWithSameLabel = wells.filter(w => w.label === well.label);
                                    setRenamedWells(renamedWells.map(w => (
                                        // (w.row === well.row && w.column === well.column)
                                        (wellsWithSameLabel.find(wellInGroup => wellInGroup.row === w.row && wellInGroup.column === w.column))
                                            ? { ...w, label: e.target.value }
                                            : w)));
                                }

                            }
                        }}
                    />
                </td>
            </tr>
        ));

    return <Modal
        opened={open}
        onClose={() => onClose()}
        size={400}
        overflow="inside"
        closeOnClickOutside={false}
        closeOnEscape={false}
        centered
        title="Rename Unknown Labels"
        transition="fade"
        transitionDuration={600}
        transitionTimingFunction="ease"
        styles={{
            header: { marginBottom: 0, textAlign: 'center' },
            body: { textAlign: 'center' },
        }}
    >

        <Table
            styles={{ textAlign: 'center' }}
        >
            <thead>
                <tr>
                    <th>Current Labels</th>
                    <th>Change Labels to</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </Table>
        <Button
            color="dark"
            onClick={() => {
                console.log(renamedWells);
                renameWells(renamedWells);
            }}
        >
            Apply
        </Button>

    </Modal>
}