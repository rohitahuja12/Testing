import { Button, Grid, Modal, Text, TextInput } from '@mantine/core';
import React, { useState } from 'react';

export const EditWellModal = ({
    open,
    onClose, //aka set modal open
    well,
    saveWell,
}) => {
    const [updatedReplicateIndex, setUpdatedReplicateIndex] = useState(well.replicateIndex);
    const [updatedLabel, setUpdatedLabel] = useState(well.label);
    const [updatedType, setUpdatedType] = useState(well.type);

    const renderInputSection = (title, placeholder, onChange, span) => (
        <Grid.Col span={span} mt={10}>
            <Text size='sm' weight={700}>{title}</Text>
            <TextInput
                mt={5}
                placeholder={placeholder}
                onChange={onChange}
            ></TextInput>
        </Grid.Col>
    )

    return <Modal
        opened={open}
        onClose={() => onClose()}
        size={400}
        overflow="inside"
        closeOnClickOutside={false}
        closeOnEscape={false}
        centered
        title="Edit Well"
        styles={{
        }}
        overlayColor="#E9ECEF"
        overlayOpacity={0.55}
    >
        <Grid>
            {renderInputSection('Replicate Index', well.replicateIndex, e => setUpdatedReplicateIndex(e.target.value), 6)}
            {renderInputSection('Label', well.label, e => setUpdatedLabel(e.target.value), 6)}
            <Grid.Col span={12} mt={10} sx={{ textAlign: 'center' }}>
                <Button
                    color="dark"
                    onClick={() => {
                        saveWell({
                            ...well,
                            replicateIndex: updatedReplicateIndex,
                            label: updatedLabel,
                            // type: updatedType,
                        });
                        onClose();
                    }}
                >
                    Save Well
                </Button>
            </Grid.Col>
        </Grid>

    </Modal>
}
