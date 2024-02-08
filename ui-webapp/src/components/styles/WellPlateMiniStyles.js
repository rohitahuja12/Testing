import { createStyles } from '@mantine/core';

export const useWellPlateMiniStyles = createStyles((theme, _params, getRef) => ({
    plate: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
        gridTemplateRows: '25px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
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
        "rows wells wells wells wells wells wells wells wells wells wells wells wells"`
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
