import React, { useState, useEffect } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import {
    createStyles,
    AppShell,
    Header,
    Navbar,
    Text,
    Group,
    Code,
    Card,
    ScrollArea,
    Timeline
} from '@mantine/core';
import { ArrowLeft } from 'tabler-icons-react';
import { useDispatch, useSelector } from 'react-redux';
import {
    start,
    stop,
    complete,
    tick,
    scanSelector
} from '../features/scan/scanSlice.js';
import { Logo } from '../components/Logo.jsx';
import { ProgressBar } from '../components/ProgressBar.jsx';
import { formatTime } from '../../lib/util/formatTime.js';
import { useAppStyles } from '../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);
// const useStyles = createStyles((theme, _params, getRef) => {
//     const icon = getRef('icon');
//     return {
//         main: {
//             paddingTop: 0
//         },
//         navbar: {
//             height: '100%',
//             backgroundColor: theme.white
//         },

//         version: {
//             backgroundColor: theme.colors[theme.primaryColor][7],
//             color: theme.white,
//             fontWeight: 700
//         },

//         header: {
//             paddingBottom: theme.spacing.md,
//             marginBottom: theme.spacing.md * 1.5,
//             borderBottom: `1px solid ${theme.colors.gray[3]}`
//         },

//         footer: {
//             paddingTop: theme.spacing.md,
//             marginTop: theme.spacing.md
//             // borderTop: `1px solid ${theme.colors.gray[3]}`
//         },

//         link: {
//             ...theme.fn.focusStyles(),
//             display: 'flex',
//             alignItems: 'center',
//             textDecoration: 'none',
//             fontSize: theme.fontSizes.sm,
//             color: theme.colors.dark[9],
//             padding: `${theme.spacing.xs}px ${theme.spacing.sm}px`,
//             borderRadius: theme.radius.sm,
//             fontWeight: 500,

//             '&:hover': {
//                 backgroundColor: theme.colors.gray[3]
//             },
//             span: {
//                 display: 'flex',
//                 alignItems: 'center',
//                 svg: {
//                     paddingRight: 10
//                 }
//             }
//         },

//         linkIcon: {
//             ref: icon,
//             color: theme.white,
//             opacity: 0.75,
//             marginRight: theme.spacing.sm
//         },

//         linkActive: {
//             '&, &:hover': {
//                 backgroundColor: theme.colors.gray[4],
//                 [`& .${icon}`]: {
//                     opacity: 0.9
//                 }
//             }
//         }
//     };
// });

const linkData = [
    { link: '/', label: 'Back to Dashboard', icon: <ArrowLeft size={18} /> }
];

export default function Layout({ ...props }) {
    const { classes, cx } = useStyles();
    const [active, setActive] = useState('Layout');
    const location = useLocation();
    // console.log('location', location);
    // dispatch to redux
    const dispatch = useDispatch();
    // get state from redux
    const { scan, lastScanUpdate } = useSelector(scanSelector);
    const flowType = useSelector((state) => (state.flow.type));

    console.log('lastscanupdate', lastScanUpdate);
    // progress bar ticking
    const links = linkData.map((item) => (
        <Link
            className={cx(classes.link, { [classes.linkActive]: item.label === active })}
            to={item.link}
            key={item.label}
        >
            <span>
                {item.icon && item.icon}
                {' '}
                {item.label}
            </span>
        </Link>
    ));

    let stepsData = [];
    if (location.pathname.includes('/analyze')) {
        if (flowType === 'ANALYZE') {
            stepsData = [
                {
                    step: '1',
                    label: 'Select Scan + Analysis Template',
                    description: 'Select a scan and an analysis template to start analyzing.',
                    active: !!location.pathname.includes('/analyze-one')
                },
                {
                    step: '2',
                    label: 'Analysis Results',
                    description: 'View the results of the analysis.',
                    active: !!location.pathname.includes('/analyze-two')
                }
            ];
        }

        if (flowType === 'SCAN_TO_ANALYSIS') {
            stepsData = [
                {
                    step: '1',
                    label: 'Select Product/Kit & Load Plate',
                    description: 'Step 1 description',
                    active: !!location.pathname.includes('/scan-one')
                },
                {
                    step: '2',
                    label: 'Set Up Scan',
                    description: 'Step 2 description',
                    active: !!location.pathname.includes('/scan-two')
                },
                {
                    step: '3',
                    label: 'Analysis Template Selection',
                    description: 'Step 3 description',
                    active: !!location.pathname.includes('/analyze-three')
                },
                {
                    step: '4',
                    label: 'Analysis Template Name & Notes',
                    description: 'Step 4 description',
                    active: !!location.pathname.includes('/analyze-four')
                },
                {
                    step: '5',
                    label: 'Set Up Plate Configuration',
                    description: 'Step 5 description',
                    active: !!location.pathname.includes('/analyze-five')
                },
                {
                    step: '6',
                    label: 'Standard Concentrations',
                    description: 'Step 6 description',
                    active: !!location.pathname.includes('/analyze-six')
                },
                {
                    step: '7',
                    label: 'Analysis Results',
                    description: 'Step 7 description',
                    active: !!location.pathname.includes('/analyze-two')
                }
            ];
        }
    }

    if (location.pathname.includes('/manage-templates')) {
        stepsData = [
            {
                step: '1',
                label: 'Manage Analysis Templates',
                description: 'Step 1 description',
                active: !!location.pathname.includes('/analysis-temps-one')
            },
            {
                step: '2',
                label: 'Select Product/Kit',
                description: 'Step 2 description',
                active: !!location.pathname.includes('/analysis-temps-two')
            },
            {
                step: '3',
                label: 'Analysis Template Name & Notes',
                description: 'Step 3 description',
                active: !!location.pathname.includes('/analysis-temps-three')
            },
            {
                step: '4',
                label: 'Set Up Plate Configuration',
                description: 'Step 4 description',
                active: !!location.pathname.includes('/analysis-temps-four')
            },
            {
                step: '5',
                label: 'Standard Concentrations',
                description: 'Step 5 description',
                active: !!location.pathname.includes('/analysis-temps-five')
            },
            {
                step: '6',
                label: 'Analysis Template Summary',
                description: 'Step 6 description',
                active: !!location.pathname.includes('/analysis-temps-six')
            }
        ];
    }

    if (location.pathname.includes('/scan')) {
        stepsData = [
            {
                step: '1',
                label: 'Select Product/Kit & Load Plate',
                description: 'Step 1 description',
                active: !!location.pathname.includes('/scan-one')
            },
            {
                step: '2',
                label: 'Set Up Scan',
                description: 'Step 2 description',
                active: !!location.pathname.includes('/scan-two')
            }
        ];

        if (location.pathname.includes('/scan/scan-two')) {
            stepsData.push({
                step: '3',
                label: '...',
                description: '',
                active: false
            });
        }
        if (location.pathname.includes('/scan/scan-three')) {
            stepsData.push({
                step: '3',
                label: 'Scan Summary',
                description: 'Step 3 description',
                active: !!location.pathname.includes('/scan/scan-three')
            });
        }
    }

    return (
        <AppShell
            navbar={(
                <Navbar height={700} width={{ sm: 300 }} p="md" className={classes.navbar}>
                    <Navbar.Section mb={40}>
                        <Group className={classes.layoutHeader} position="apart">
                            <Logo />
                            <Code className={classes.version}>v1.0.0</Code>
                        </Group>
                        {links}
                    </Navbar.Section>

                    <Navbar.Section grow="true" component={ScrollArea}>
                        <Timeline
                            active={stepsData.findIndex((item) => item.active)}
                            bulletSize={12}
                            lineWidth={2}
                            className={classes.title}
                            styles={{
                                itemTitle: {
                                    fontSize: 12
                                }
                            }}
                        >
                            {stepsData.map((item) => (
                                <Timeline.Item
                                    key={item.step}
                                    title={item.label}
                                    lineVariant="solid"
                                    sx={(theme) => (item.active
                                        ? ({ '.mantine-Timeline-itemBullet': { backgroundColor: theme.colorScheme === 'dark' ? theme.colors.blue[7] : theme.colors.blue[3] } })
                                        : ({ '.mantine-Timeline-itemBullet': { backgroundColor: theme.colorScheme === 'dark' ? theme.colors.gray[7] : theme.colors.gray[0] } })
                                    )}
                                >
                                    <Text className={classes.dimmedText} size="xs">{item.description}</Text>
                                </Timeline.Item>
                            ))}
                        </Timeline>
                    </Navbar.Section>
                    {lastScanUpdate
                        && (
                            <Navbar.Section className={classes.footer}>
                                <Card withBorder style={{ padding: '20px 16px 30px 16px' }}>
                                    <ProgressBar // TODO: refactor this whole thing
                                        total={20}
                                        completed={lastScanUpdate?.status === "COMPLETE"
                                            ? 20
                                            : 1}
                                        error={lastScanUpdate?.status === "ABORTED" || lastScanUpdate?.status === "ERROR"}
                                        clickHandler={() => dispatch(stop())}
                                        runningText={lastScanUpdate?.status === "QUEUED" || lastScanUpdate?.status === "RUNNING"
                                            ? 'estimated completion time 20 minutes'
                                            : 'Scan stopped'}
                                        completedText="Scan Complete"
                                        buttonText="Stop Scan"
                                    />
                                </Card>
                            </Navbar.Section>
                        )}
                </Navbar>

            )}
            styles={{
                body: { height: '100%' },
                main: { padding: 0 }
            }}
        >
            <Outlet />
        </AppShell>
    );
}
