import {
    createStyles,
} from '@mantine/core';

export const useWellPlateAdvancedStyles = createStyles((theme, _params, getRef) => {
    const isDarkTheme = () => theme.colorScheme === "dark";
    const getBorderStyle = (px = 1) => `${px}px solid ${isDarkTheme() ? theme.colors.dark[5] : theme.colors.gray[2]}`;

    return {
        plate: {
            display: 'grid',
            gridTemplateColumns: '25px 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr',
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
    "rows wells wells wells wells wells wells wells wells wells wells wells wells"`,
            // width: '670px',
            // height: '407px',
            padding: '25px 15px', //where the top-left corner of the plate is
        },
        backplate: {
            stroke: isDarkTheme() ? theme.colors.dark[3] : theme.colors.gray[0],
            fill: isDarkTheme() ? theme.colors.dark[5] : theme.white,
        },
        columns: {
            gridArea: 'columns',
            justifyContent: 'center',
            alignItems: 'center',
            maxHeight: '50px'
        },
        rows: {
            gridArea: 'rows',
            justifyContent: 'center',
            alignItems: 'center',
            gap: '0px',
            '.row-header': {
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'start',
                lineHeight: '1px',
            }
        },
        wells: { gridArea: 'wells' },
        well: {
            textAlign: 'center',
            cursor: 'auto'
        },
        topControls: {
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            gridTemplateRows: '1fr',
            gap: '0 0 0 0',
            gridTemplateAreas: '"left middle right"',
            marginBottom: 25,
            border: getBorderStyle(),
            borderRadius: 8,
            '.section': {
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                minHeight: 60,
                padding: 0,
                '&:not(:last-child)': {
                    borderRight: getBorderStyle()
                }
            },
            '.left': { gridArea: 'left', justifyContent: 'space-between' },
            '.middle': { gridArea: 'middle', gap: 5 },
            '.right': { gridArea: 'right' }
        },
        controlsToggles: {
            flexDirection: 'row-reverse',
            justifyContent: 'flex-start',
            width: '100%',
            label: {
                width: '100%',
                marginRight: 5,
                paddingLeft: 0,
                textAlign: 'right',
                fontSize: 10
            }
        }
    }
});