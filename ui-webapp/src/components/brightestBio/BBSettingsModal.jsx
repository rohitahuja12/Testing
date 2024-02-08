
import React, { useMemo } from 'react';
import { systemSelector, toggleStyleSystem, toggleAppTheme } from '../../features/system/systemSlice';
import { useSelector, useDispatch } from 'react-redux';
import BrushIcon from '@mui/icons-material/Brush';
import PaletteIcon from '@mui/icons-material/Palette';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import Backdrop from '@mui/material/Backdrop';

import {
  Modal,
  List,
  ListItem,
  ListItemText,
  Box,
  Fade,
} from '@mui/material';
import ListItemIcon from '@mui/material/ListItemIcon';
import Switch from '@mui/material/Switch';
import ListSubheader from '@mui/material/ListSubheader';
import { grey } from '@mui/material/colors';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.modalPaper',
  boxShadow: 24,
  borderRadius: 1,
  borderColor: 'secondary',
  pt: 2,
  px: 4,
  pb: 3,
};

/**
 * 
 * @param {{ open: Function, onClose: Function }} props 
 * @returns 
 */
const BBSettingsModal = ({
  open,
  onClose
}) => {
  const { useMUIStyleSystem, useDarkTheme } = useSelector(systemSelector);
  const dispatch = useDispatch();

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="modal-modal-title"
      aria-describedby="modal-modal-description"
      closeAfterTransition
      BackdropComponent={Backdrop}
      BackdropProps={{
        timeout: 500,
      }}
    >
      <Fade in={open}>
        <Box sx={{ ...style, width: 300 }}>
          <List
            sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.modalPaper' }}
            subheader={<ListSubheader sx={{ bgcolor: 'background.modalPaper' }}>Settings</ListSubheader>}
          >
            <ListItem>
              <ListItemIcon>
                <BrushIcon />
              </ListItemIcon>
              <ListItemText primary="Style System" sx={{ color: grey[600] }} />
              <Switch
                edge="end"
                disabled
                onChange={() => {
                  dispatch(toggleStyleSystem());
                  onClose();
                }}
                checked={useMUIStyleSystem}
                color="secondary"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                {useDarkTheme ? <Brightness4Icon /> : <Brightness7Icon />}
              </ListItemIcon>
              <ListItemText primary="App Theme" sx={{ color: grey[600] }} />
              <Switch
                edge="end"
                onChange={() => {
                  dispatch(toggleAppTheme());
                }}
                checked={useDarkTheme}
                color="secondary"
              />
            </ListItem>
          </List>
        </Box>
      </Fade>
    </Modal>
  );
}

export default BBSettingsModal;