
import React, { useState, useMemo, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid, Typography, Paper, Button, List, ListItem, ListItemAvatar, Avatar, ListItemText, IconButton
} from '@mui/material';
import { useNavigate, useSearchParams } from 'react-router-dom';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import BBViewShell from '../BBViewShell';
import { Article, Download } from '@mui/icons-material';

/**
 * 
 * @param {
 * screenTitle: string,
 * signOut: function
 * } props 
 * @returns 
 */
const BBViewDocuments = (props) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const createDocListItem = (text, secondaryText, url) => (
    <ListItem
      secondaryAction={
        <IconButton edge="end" aria-label="delete" onClick={() => {
          console.debug('Documents do not exist yet.');
        }}>
          <Download />
        </IconButton>
      }
    >
      <ListItemAvatar>
        <Avatar>
          <Article />
        </Avatar>
      </ListItemAvatar>
      <ListItemText
        primary={text}
        secondary={secondaryText}
      />
    </ListItem>
  );

  return (
    <BBViewShell alignItems='start' signOut={props?.signOut}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h2" component="h1" mb={0} mt={5} color="textPrimary" gutterBottom>
            {props.screenTitle}
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Button color="secondary" variant="contained" onClick={() => { navigate('/') }} sx={{ marginRight: 1 }}>
            <ArrowBackIcon sx={{ fontSize: 24 }} />
            Back to Dashboard
          </Button>
        </Grid>
        <Grid item xs={0} md={3} lg={4}>
        </Grid>
        <Grid item xs={12} md={6} lg={4} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <List>
              {createDocListItem('Connnect to the Empower Reader', 'Provides instructions onn how to connect to the Empower Reader.', '')}
              {createDocListItem('Load a plate', 'Provides instructions on how to load a plate.', '')}
              {createDocListItem('Product Kit', 'Provides instructions on how to use the product kit.', '')}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </BBViewShell>
  );
}

export default BBViewDocuments;