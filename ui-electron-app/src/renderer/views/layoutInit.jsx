import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  createStyles,
  AppShell,
  Navbar,
  Group,
  Code,
  ScrollArea,
  Timeline
} from '@mantine/core';
import { Logo } from '../components/Logo.jsx';
import { WellPlateAdvanced } from '../components/WellPlateAdvanced.jsx';

const useStyles = createStyles((theme, _params, getRef) => {
  const icon = getRef('icon');
  return {
    navbar: {
      height: '100%',
      backgroundColor: theme.white
    },

    version: {
      backgroundColor: theme.colors[theme.primaryColor][7],
      color: theme.white,
      fontWeight: 700
    },

    header: {
      paddingBottom: theme.spacing.md,
      marginBottom: theme.spacing.md * 1.5,
      borderBottom: `1px solid ${theme.colors.gray[7]}`
    },

    footer: {
      paddingTop: theme.spacing.md,
      marginTop: theme.spacing.md,
      borderTop: `1px solid ${theme.colors.gray[7]}`
    },

    link: {
      ...theme.fn.focusStyles(),
      display: 'flex',
      alignItems: 'center',
      textDecoration: 'none',
      fontSize: theme.fontSizes.sm,
      color: theme.colors.dark[9],
      padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
      borderRadius: theme.radius.sm,
      fontWeight: 500,

      '&:hover': {
        backgroundColor: theme.colors.gray[3]
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
    }
  };
});

const linkData = [
  { link: '/', label: 'Back to Dashboard' }
];

const stepsData = [
  { step: '1', label: 'Step 1', description: 'Step 1 description' },
  { step: '2', label: 'Step 2', description: 'Step 2 description' },
  { step: '3', label: 'Step 3', description: 'Step 3 description' },
  { step: '4', label: 'Step 4', description: 'Step 4 description' }
];

export default function LayoutInit() {
  const { classes, cx } = useStyles();
  const [active, setActive] = useState('Layout');

  const links = linkData.map((item) => (
    <Link
      className={cx(classes.link, { [classes.linkActive]: item.label === active })}
      to={item.link}
      key={item.label}
      // onClick={(event) => {
      //   event.preventDefault();
      //   setActive(item.label);
      // }}
    >
      <span>{item.label}</span>
    </Link>
  ));

  return (
    <AppShell
      navbar={(
        <Navbar height={700} width={{ sm: 300 }} p="md" className={classes.navbar}>
          <Navbar.Section mb={40}>
            <Group className={classes.header} position="apart">
              <Logo />
              <Code className={classes.version}>v1.0.0</Code>
            </Group>
            {links}
          </Navbar.Section>

          <Navbar.Section grow="true">
            <Timeline
              active={1}
              bulletSize={12}
              lineWidth={2}
            >
              {stepsData.map((item) => (
                <Timeline.Item key={item.step} title={item.label}>
                  <p>{item.description}</p>
                </Timeline.Item>
              ))}
            </Timeline>
          </Navbar.Section>

          <Navbar.Section className={classes.footer}>
            <span>Progress Bar Section</span>
          </Navbar.Section>
        </Navbar>

      )}
      styles={{
        body: { height: '100%' }
      }}
    >
      <ScrollArea style={{ height: '100%' }}>
        <h1>Application Page View</h1>
        <WellPlate />

      </ScrollArea>

    </AppShell>
  );
}
