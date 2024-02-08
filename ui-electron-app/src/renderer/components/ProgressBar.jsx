import React, { useCallback, useState } from 'react';
import {
  createStyles,
  Button,
  Progress,
  Text,
  Modal,
  Group
} from '@mantine/core';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import {
  start, stop, complete, tick
} from '../features/scan/scanSlice.js';
import { useAppStyles } from '../styles/appStyles.js';

const useStyles = createStyles(useAppStyles);

export function ProgressBar({
  completed = 0,
  total = 0,
  clickHandler,
  error,
  runningText,
  completedText,
  buttonText
}) {
  const [modalOpen, setModalOpen] = useState(false);
  const { classes, cx } = useStyles();
  const navigate = useNavigate();
  // // dispatch to redux
  const dispatch = useDispatch();
  // get state from redux
  const { scan } = useSelector((state) => state.scan);

  const progress = Math.ceil((completed / total) * 100);

  const handleStopClick = () => {
    if (scan.isRunning) {
      setModalOpen(true);
    } else {
      clickHandler();
    }
  };

  return (
    <>
      <div className={classes.progressBarContainer}>
        <Progress
          radius="md"
          size="lg"
          value={error ? 100 : progress}
          color={error ? 'red' : 'blue'}
          striped={!error && progress !== 100}
          animate={!error && progress !== 100}
          mb={15}
          sx={{
            width: '100%',
            maxWidth: '200px'
          }}
        />
        <Text className={classes.text} size="sm" weight={600} mb={15} color={error && 'red'}>{progress !== 100 ? runningText : completedText}</Text>

        {(!error && progress !== 100) && (
          <Button
            className={classes.navigationButton}
            color="dark" radius="xl" onClick={handleStopClick}>
            {buttonText}
          </Button>
        )}
      </div>

      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        closeOnClickOutside={false}
        closeOnEscape={false}
        size={441}
        centered={true}
        styles={{
          header: { marginBottom: 0 },
          body: { textAlign: 'center' },
        }}
        sx={(t) => ({
          
        })}
      >
        <Text size="lg" weight={600} mb={28}>
          Stop Scan?
        </Text>

        <Text size="sm" color="dimmed" mb={15} mt={28}>
          By stopping the scan, you will have to start over from the beginning with naming and selecting the plate area to be read.
        </Text>

        <Text size="sm" mb={15} mt={28}>
          Are you sure you want to stop this scan
          at this time?
        </Text>

        <Group position="center">
          <Button
            type="button"
            variant="default"
            size="md"
            onClick={() => setModalOpen(false)}
            mt={30}
            mb={20}
          >
            No, continue scan
          </Button>

          <Button
            type="button"
            color="red"
            size="md"
            onClick={() => {
              dispatch(stop());
              setModalOpen(false);
              navigate('/', { replace: true });
            }}
            mt={30}
            mb={20}
          >
            Yes, stop scan
          </Button>
        </Group>
      </Modal>
    </>
  );
}
