import React, { useEffect, useState } from 'react';
import {
    Select
} from '@mantine/core';

export const PlateDropDown = ({
    title,
    optionList,
    onChange
}) => {

    const domSafeOptionList = optionList.map(option => ({
        value: option.value,
        label: option.label,
        map: option.map,
        name: option.name,
        _id: option._id,
    }));
    
    return (
        <Select
            onChange={onChange}
            label=""
            placeholder={title}
            data={domSafeOptionList}
            size="xs"
            sx={{ minWidth: '185px' }}
        />
    )
}