import React from 'react';
import {
  createStyles, Header, Group, Text
} from '@mantine/core';
import { useAppStyles } from '../styles/appStyles';

const useStyles = createStyles(useAppStyles);

export function AppShellHeader({ children, ...props }) {
  const { classes, cx } = useStyles();

  return (
    <>
      <Header className={classes.mainHeader}>
        <Group position="start">
          <Text className={classes.title} style={{ fontSize: 16 }}>{props.screenTitle}</Text>
        </Group>
        {children}
      </Header>
    </>
  );
}
