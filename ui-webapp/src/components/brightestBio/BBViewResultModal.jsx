import React, { useMemo } from "react";
import {
  Modal,
  List,
  ListItem,
  ListItemText,
  Box,
  Fade,
  Typography,
} from "@mui/material";
import Backdrop from "@mui/material/Backdrop";
import ListSubheader from "@mui/material/ListSubheader";
import ImageList from "@mui/material/ImageList";
import ImageListItem from "@mui/material/ImageListItem";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import Button from "@mui/material/Button";

const style = {
  position: "absolute",
  top: "52%",
  left: "50%",
  transform: "translate(-50%, -50%)",
  width: "80%",
  bgcolor: "background.modalPaper",
  boxShadow: 24,
  borderRadius: 1,
  border: "none",
  pt: 2,
  px: 4,
  pb: 3,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
};

/**
 *
 * @param {{
 * open: boolean,
 * onClose: Function,
 * images: Array<any>,
 * result: {
 * name: { isAction: boolean, value: string | Date },
 * date: { isAction: boolean, value: string | Date },
 * product: { isAction: boolean, value: string | Date },
 * id: { isAction: boolean, value: string | Date },
 * }}} props
 * @returns
 */
const BBViewResultModal = ({ open, onClose, images, result, onExport }) => {
  if (!result) {
    return <Box visibility={false}></Box>;
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
          <List sx={{ width: "90%", bgcolor: "background.modalPaper" }}>
            <ListItem>
              <Typography
                variant="h4"
                component="h1"
                mb={0}
                color="textPrimary"
              >
                {result.name.value}
                <Button
                  color="secondary"
                  sx={{ marginLeft: 2 }}
                  variant="outlined"
                  onClick={onExport}
                >
                  <FileDownloadIcon
                    sx={{ cursor: "pointer", marginRight: "5px" }}
                    color="textPrimary"
                    onClick={onExport}
                  />
                  Export
                </Button>
              </Typography>
            </ListItem>
            <ListItem>
              {/* <Typography variant="h4" component="h1" mb={0} color="textPrimary" > */}

              {/* </Typography> */}
            </ListItem>
            <ListItem>
              <Typography
                variant="h6"
                component="h1"
                mb={0}
                color="textSecondary"
              >
                Created on: {new Date(result.date.value).toLocaleString()}
              </Typography>
            </ListItem>
            <ListItem>
              <Typography
                variant="h6"
                component="h1"
                mb={0}
                color="textSecondary"
              >
                Product: {result.product.value}
              </Typography>
            </ListItem>
            <ListItem>
              {images && images?.length > 0 && (
                <ImageList sx={{ height: "50vh" }} cols={3} gap={20}>
                  {images?.map((image, i) => (
                    <ImageListItem key={i}>
                      <img
                        style={{ borderRadius: 10 }}
                        src={`${image}`}
                        alt={i}
                        loading="lazy"
                      />
                    </ImageListItem>
                  ))}
                </ImageList>
              )}
            </ListItem>
          </List>
        </Box>
      </Fade>
    </Modal>
  );
};

export default BBViewResultModal;
