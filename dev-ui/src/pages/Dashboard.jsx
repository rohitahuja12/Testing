
import * as React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Grid2 from '@mui/material/Unstable_Grid2';
import { css } from '@emotion/react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';

export const Dashboard = ({ props }) => {

    return (
        <React.Fragment>
            <CssBaseline />
            <Grid2 container spacing={2}>
                <Grid2 item lg={12}>
                    <h2>Dev UI</h2>
                </Grid2>

                <Grid2 item lg={8}>
                    <img style={{
                        objectFit: 'cover',
                        maxWidth: '100%',
                        padding: 20,
                    }} src="https://dummyimage.com/1200x800/000/ffbf00" alt="random" />
                </Grid2>
                <Grid2 container pt={5} spacing={2} lg={4} xs={12} direction="column" alignItems="center" justifyContent="start">
                    <ButtonGroup variant="text" aria-label="text button group">
                        <Button>Up</Button>
                        <Button>Down</Button>
                        <Button>Left</Button>
                        <Button>Right</Button>
                    </ButtonGroup>

                    <Button style={{ marginTop: 20 }} variant="contained">Take Picture</Button>
                </Grid2>
            </Grid2>
        </React.Fragment>
    )
}