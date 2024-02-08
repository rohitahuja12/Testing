import React, { useState, useCallback } from 'react';
import { createStyles, Badge } from '@mantine/core';

export const useStyles = createStyles((theme, _params, getRef) => ({
  indicatorBadge: {
    height: '8px',
    width: '8px',
    fontSize: 0,
    lineHeight: 0,
    padding: 0
  }
}));

export function IndicatorBadge({ status }) {
  const { classes, cx } = useStyles();
  let statusColor;

  switch(status) {
    case 'ok':
      statusColor = 'green';
      break;
    case 'warning':
      statusColor = 'yellow';
      break;
    case 'error':
      statusColor = 'red';
      break;
    default:
      statusColor = 'green';
      break;
  }
  return <Badge variant="filled" color={statusColor} className={classes.indicatorBadge} />;
}
