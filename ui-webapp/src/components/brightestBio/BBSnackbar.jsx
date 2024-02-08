import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Snackbar from '@mui/material/Snackbar';
import { hideSnackbar, systemSelector } from '../../features/system/systemSlice';
import { Alert } from '@mui/material';

const BBSnackbar = (props) => {
    const { open, message, severity } = useSelector(systemSelector)?.snackbar;

    const dispatch = useDispatch();

    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }

        dispatch(hideSnackbar());
    };

    return (
        <Snackbar
            open={open}
            autoHideDuration={6000}
            onClose={handleClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
            <Alert onClose={handleClose} variant="filled" severity={severity || 'success'} color={severity || 'success'} sx={{ width: '100%' }}>
                {message}
            </Alert>
        </Snackbar>
    );
}

export default BBSnackbar;