
import React, { useMemo, useState, useEffect } from 'react';
import { systemSelector } from '../../features/system/systemSlice';
import { getDesignTokens } from '../../components/brightestBio/BBTheme.js';
import { useSelector } from 'react-redux';
import BBNavBar from '../../components/brightestBio/BBNavBar.jsx';
import { Transition } from 'react-transition-group';
import { CssBaseline } from '@mui/material';

import {
  createTheme,
  ThemeProvider,
  Box,
  Grid,
} from '@mui/material';

/**
 * 
 * @param {{children: any, justifyContent: string, alignItems: string, signOut: function}} param0 
 * @returns 
 */
const BBViewShell = ({ children, justifyContent, alignItems, signOut }) => {
  const { useMUIStyleSystem, useDarkTheme } = useSelector(systemSelector);
  const theme = useMemo(() => createTheme(getDesignTokens(useDarkTheme ? 'dark' : 'light')));
  const sidePadding = useMemo(() => '7.5vw', []);
  const transitionPaddingOffset = useMemo(() => '16px', []);
  const [transitionState, setTransitionState] = useState(false)

  useEffect(() => {
    setTimeout(() => {
      setTransitionState(true)
    }, 100)
  }, [])

  const transitions = useMemo(() => ({
    entering: {
      display: 'block'
    },
    entered: {
      opacity: 1,
      display: 'block'
    },
    exiting: {
      opacity: 0,
      display: 'block'
    },
    exited: {
      opacity: '0',
      display: 'none'
    }
  }), []);

  return (
    <>
      {useMUIStyleSystem
        && (
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <BBNavBar title='Brightest Bio' version='1.1.0'/>
            <Box
              sx={{ backgroundColor: 'background.default', overflowY: "scroll", minHeight: '100vh' }}
              display="flex"
              justifyContent={justifyContent || "center"}
              alignItems={alignItems || "center"}
              minHeight="calc(100vh - 100px)"
              pl={`calc(${sidePadding} + ${transitionPaddingOffset})`} pr={sidePadding} pt='84px' pb='16px'
              >
              <Transition
                in={transitionState}
                timeout={10}
              >
                {state => (
                  <Grid container spacing={2} style={{
                    transition: 'opacity 50ms, display 100ms',
                    opacity: 0,
                    display: 'none',
                    ...transitions[state],
                  }}
                  >
                    {children}
                  </Grid>
                )}
              </Transition>
            </Box>
          </ThemeProvider>
        )}
    </>
  )
}

export default BBViewShell;