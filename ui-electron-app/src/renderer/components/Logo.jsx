import React, { useState, useCallback } from 'react';
import {
  createStyles,
  Code,
  Group
} from '@mantine/core';
import { useAppStyles } from '../styles/appStyles';

const useStyles = createStyles(useAppStyles);

export function Logo() {
  const { classes } = useStyles();

  return (
    <div className={classes.logo}>
      Auragent
      {' '}
      <span>Bioscience</span>
    </div>
  );
}
