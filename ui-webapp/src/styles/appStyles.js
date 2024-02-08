import { createStyles } from "@mantine/core";

const containerTopOffset = 100;

export const useAppStyles = (theme, _params, getRef) => {
    const isDarkTheme = () => {
        // passing control of color theme to children of the app component
        // affects their ability to use the theme in all cases.
        // Always having acecss to view the theme in React, we can pass it through the
        // use styles params to override the theme.
        if (_params) return _params === "dark";
        return theme.colorScheme === "dark";
    };
    const icon = getRef('icon');
    const getBorderStyle = () => `1px solid ${isDarkTheme() ? theme.colors.dark[5] : theme.colors.gray[2]}`;

    return {
        logo: {
            fontSize: theme.fontSizes.md,
            fontWeight: 700,
            span: {
                fontWeight: 400
            },
            color: isDarkTheme() ? theme.colors.dark[0] : theme.colors.gray[9],
        },
        text: {
            color: isDarkTheme() ? theme.colors.dark[1] : theme.colors.gray[7],
        },
        title: {
            color: isDarkTheme() ? theme.colors.gray[1] : theme.colors.gray[9],
            fontWeight: 700
        },
        dimmedText: {
            color: isDarkTheme() ? theme.colors.gray[6] : theme.colors.gray[4],
        },
        popoverLink: {
            color: isDarkTheme() ? theme.colors.blue[3] : theme.colors.blue[6],
        },
        version: {
            backgroundColor: isDarkTheme() ? theme.colors.yellow[5] : theme.colors[theme.primaryColor][5],
            color: isDarkTheme() ? theme.black : theme.white,
            fontWeight: 700
        },
        main: {
            paddingTop: 0
        },
        navbar: {
            height: '100vh',
            backgroundColor: isDarkTheme() ? theme.colors.dark[7] : theme.colors.gray[0]
        },
        link: {
            ...theme.fn.focusStyles(),
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
            fontSize: theme.fontSizes.sm,
            color: isDarkTheme() ? theme.colors.gray[1] : theme.colors.gray[9],
            padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
            borderRadius: theme.radius.sm,
            fontWeight: 500,

            '&:hover': {
                backgroundColor: isDarkTheme() ? theme.colors.gray[7] : theme.colors.gray[3]
            },
            span: {
                display: 'flex',
                alignItems: 'center',
                svg: {
                    paddingRight: 10
                }
            }
        },
        linkIcon: {
            ref: icon,
            color: theme.white,
            opacity: 0.75,
            marginRight: theme.spacing.sm
        },
        linkActive: {
            '&, &:hover': {
                backgroundColor: theme.colors.gray[4],
                [`& .${icon}`]: {
                    opacity: 0.9
                }
            }
        },
        header: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
        },
        detailAccordion: {
            backgroundColor: isDarkTheme() ? theme.colors.dark[5] : theme.white,
            h3: {
                button: {
                    '&:hover': {
                        backgroundColor: isDarkTheme() ? theme.colors.dark[4] : theme.colors.gray[2],
                    }
                }
            }
        },
        layoutHeader: {
            paddingBottom: theme.spacing.md,
            marginBottom: theme.spacing.md * 1.5,
            borderBottom: getBorderStyle()
        },
        mainHeader: {
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            minHeight: '55px',
            padding: '0px 40px',
            backgroundColor: isDarkTheme() ? theme.colors.dark[7] : 'transparent',
            borderBottom: getBorderStyle()
        },
        cardSpacer: {
            margin: '10px -20px',
            borderTop: `1px solid ${isDarkTheme() ? theme.colors.gray[7] : theme.colors.gray[0]}`
        },
        tableBox: {
            maxWidth: 1060,
            marginLeft: 60,
            marginRight: 60,
            marginBottom: 30
        },
        commandHeader: {
            marginTop: 30
        },
        appBackground: {
            minWidth: '100%',
            maxWidth: '100%',
            minHeight: 'calc(100vh - 55px)',
            maxHeight: 'calc(100vh - 55px)',
            overflow: 'auto',
            backgroundColor: isDarkTheme() ? theme.colors.dark[7] : theme.colors.gray[0],
        },
        dashboardAppBackground: {
            minWidth: '100%',
            maxWidth: '100%',
            minHeight: '100vh',
            overflow: 'auto',
            backgroundColor: isDarkTheme() ? theme.colors.dark[7] : theme.colors.gray[0],
        },
        container: {
            backgroundColor: isDarkTheme() ? theme.colors.dark[7] : theme.colors.gray[0],
            height: '100%',
            width: '95%',
            maxHeight: `calc(100vh - (${containerTopOffset}px * 2))`,
            maxWidth: '1200px',
            margin: '0 auto',
            padding: `${containerTopOffset}px 12px`,
            '.mantine-Paper-root': {
                padding: '20px',
                border: isDarkTheme() ? `solid 1px ${theme.colors.gray[8]}` : `solid 1px ${theme.colors.gray[1]}`,
                borderRadius: theme.radius.md
            },
            '.card': {
                // padding: '20px',
                border: isDarkTheme() ? `solid 1px ${theme.colors.gray[3]}` : `solid 1px ${theme.colors.gray[5]}`,
                borderRadius: theme.radius.md
            },
        },
        progressBarContainer: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
            textAlign: 'center'
        },
        calibrationContainer: {
            height: '100%',
            maxHeight: `calc(100vh - (${containerTopOffset}px * 2))`,
            margin: '0 auto',
            padding: `${containerTopOffset}px 12px`,
            '.mantine-Paper-root': {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                maxWidth: '460px',
                width: '100%',
                padding: '20px',
                border: isDarkTheme() ? `solid 1px ${theme.colors.gray[8]}` : `solid 1px ${theme.colors.gray[1]}`,
                borderRadius: theme.radius.md,
                textAlign: 'center',
                '&.reduced-width': {
                    maxWidth: '315px'
                }
            },
        },
        column: {
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            paddingBottom: '50px'
        },
        buttonSection: {
            maxWidth: '315px'
        },
        card: {
            border: isDarkTheme() ? `solid 1px ${theme.colors.gray[8]}` : `solid 1px ${theme.colors.gray[1]}`,
            borderRadius: theme.radius.md,
        },
        titleWithBadge: {
            display: 'flex',
            flexWrap: 'nowrap',
            alignItems: 'center',
            justifyContent: 'space-between'
        },
        actionButton: {
            backgroundColor: isDarkTheme() ? theme.colors[theme.primaryColor][5] : theme.colors[theme.primaryColor][5],
        },
        navigationButton: {
            backgroundColor: isDarkTheme() ? theme.colors[theme.primaryColor][8] : theme.colors.gray[9],
            '&:hover': {
                backgroundColor: isDarkTheme() ? theme.colors[theme.primaryColor][7] : theme.colors[theme.primaryColor][7]
            },
        },
        secondaryNavigationButton: {
            backgroundColor: isDarkTheme() ? theme.colors.gray[8] : theme.white,
            '&:hover': {
                backgroundColor: isDarkTheme() ? theme.colors.gray[7] : theme.colors[theme.primaryColor][1]
            },
        },
        fullHeight: {
            height: '100%'
        },
        tableHeaderRow: {
            backgroundColor: isDarkTheme() ? theme.colors.gray[8] : theme.white,
            'svg': {
                stroke: isDarkTheme() ? theme.colors.gray[1] : theme.colors.gray[9],
            },
            '.tr-header': {
                borderBottom: isDarkTheme() ? `1px solid ${theme.colors.gray[5]}` : `1px solid ${theme.colors.gray[2]}`,
            }
        },
        tableHeaderCellText: {
            color: isDarkTheme() ? theme.colors.gray[2] : theme.colors.gray[7],
            fontSize: 14,
            fontWeight: 700,
        },
        tableRow: {
            backgroundColor: isDarkTheme() ? theme.colors.gray[8] : theme.white,
            '.tr-body': {
                backgroundColor: isDarkTheme() ? theme.colors.gray[8] : theme.white,
                borderBottom: `1px solid ${isDarkTheme() ? theme.colors.gray[7] : theme.colors.gray[0]}`,
                height: 50
            }
        },
        tableRowCellText: {
            color: isDarkTheme() ? theme.colors.gray[2] : theme.colors.gray[8],
            fontSize: 14,
            fontWeight: 400,
        },
        tablePaper: {
            backgroundColor: isDarkTheme() ? theme.colors.gray[8] : theme.white,
        },
        noRadiusForDark: {
            borderRadius: isDarkTheme() ? 0 : theme.radius.md,
        },
        tableWrapper: {
            height: 400
        },
        contextMenu: {
            backgroundColor: isDarkTheme() ? theme.colors.gray[8] : theme.white,
        },
        centeredChildren: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        },
        hr: {
            borderColor: isDarkTheme() ? theme.colors.gray[7] : theme.colors.gray[0]
        }
    }
}