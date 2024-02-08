import React, { useMemo } from 'react';
import {
  Modal,
  List,
  ListItem,
  Box,
  Fade,
  Typography,
  Paper
} from '@mui/material';
import Backdrop from '@mui/material/Backdrop';
import { WellPlateMini } from '../WellPlateMini';
import { getWellsFromAnalysis, getWellsFromScan } from '../../utils/wellUtils';
import useMediaQuery from '@mui/material/useMediaQuery';
import { BBLoader } from './BBLoader';

const style = {
  position: 'absolute',
  top: '52%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '80%',
  bgcolor: 'background.modalPaper',
  boxShadow: 24,
  borderRadius: 1,
  border: 'none',
  pt: 2,
  px: 4,
  pb: 3,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center'
};


/**
 * 
 * @param {{
 * open: boolean, 
 * onClose: Function, 
 * analysisTemplate: {
 * name: { isAction: boolean, value: string | Date }, 
 * createdOn: { isAction: boolean, value: string | Date }, 
 * productId: { isAction: boolean, value: string | Date }, 
 * _id: { isAction: boolean, value: string | Date }, 
 * protocolArgs: any
 * }}} props 
 * @returns 
 */
const BBViewAnalysisTemplateModal = ({
  open,
  onClose,
  analysisTemplate
}) => {
  const isPhoneView = useMediaQuery('(max-width:600px)');
  const miniPlateStyles = useMemo(() => {
    if (isPhoneView) {
      return {
        width: '100%',
        paddingRight: '20px',
        paddingLeft: '10px',
        paddingTop: '20px',
        paddingBottom: '20px'
      }
    }
    return {
      padding: 5
    }
  }, [isPhoneView])

  const renderPlateMini = (template) => {
    if (template?.protocolArgs) {
      const wells = getWellsFromAnalysis(template);
      return (<WellPlateMini wells={wells} />);
    }
  }

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
        <Box sx={{ ...style }}>
          <List
            sx={{ width: '90%', bgcolor: 'background.modalPaper' }}
          >
            <ListItem>
              <Typography variant="h4" component="h1" mb={0} color="textPrimary" >
                {analysisTemplate?.name}
              </Typography>
            </ListItem>
            <ListItem>
            </ListItem>
            <ListItem>
              {analysisTemplate &&
                <Typography variant="h6" component="h1" mb={0} color="textSecondary">
                  Created on: {(new Date(analysisTemplate?.createdOn)).toLocaleString()}
                </Typography>
              }
            </ListItem>
            <ListItem>
            </ListItem>
          </List>
          {analysisTemplate?.protocolArgs &&
            <Paper elevation={2} sx={miniPlateStyles}>
              {renderPlateMini(analysisTemplate)}
            </Paper>
          }
          {(!analysisTemplate || !analysisTemplate?.protocolArgs) && <BBLoader size='md' />}
        </Box>
      </Fade>
    </Modal>
  );
}

export default BBViewAnalysisTemplateModal;