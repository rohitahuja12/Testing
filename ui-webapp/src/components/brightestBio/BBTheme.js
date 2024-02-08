import { blue, grey } from '@mui/material/colors';

export const getDesignTokens = (mode = "dark") => ({
    typography: {
        fontFamily: 'manrope, Roboto',
        fontSize: 16
    },
    palette: {
        mode,
        ...(mode === 'light')
            ? {
                primary: {
                    main: '#F1F2F3',
                },
                secondary: {
                    main: '#337FCC',
                },
                background: {
                    default: '#f8f9fa',
                    modalPaper: grey[100]
                },
                appVersion: {
                    marginLeft: 1,
                    fontWeight: 700,
                    fontSize: 12,
                }
            }
            : {
                primary: {
                    main: '#F1F2F3',
                },
                secondary: {
                    main: blue[500],
                },
                background: {
                    default: '#121212',
                    paper: '#121015',
                    modalPaper: '#1e1b23'

                },
                appVersion: {
                    marginLeft: 1,
                    fontWeight: 700,
                    fontSize: 12,
                }
            }
    }
})
// export const brightestBioTheme = createTheme(getDesignTokens('dark'));