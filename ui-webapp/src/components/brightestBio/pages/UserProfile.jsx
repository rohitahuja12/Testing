import React from "react";
import { useDispatch, useSelector } from "react-redux";
import BBViewShell from "../BBViewShell.jsx";
import {
  Grid,
  Typography,
  Paper,
  Button,
  FormLabel,
  Stack,
  TextField,
  List,
  ListItem,
  ListItemText,
  Box,
  Fade,
} from "@mui/material";
import { useNavigate, useSearchParams, Navigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { BBViewPageLoader } from "../BBViewPageLoader.jsx";
import { useAuth0 } from "@auth0/auth0-react";
import {
  systemSelector,
  toggleStyleSystem,
  toggleAppTheme,
} from "../../../features/system/systemSlice.js";
import ListSubheader from "@mui/material/ListSubheader";
import { grey } from "@mui/material/colors";
import Switch from "@mui/material/Switch";
import ListItemIcon from "@mui/material/ListItemIcon";
import BrushIcon from "@mui/icons-material/Brush";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";

const UserProfile = (props) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { user } = useAuth0();
  const { useMUIStyleSystem, useDarkTheme } = useSelector(systemSelector);

  return (
    <BBViewShell alignItems="start" signOut={props?.signOut}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography
            variant="h2"
            component="h1"
            mb={0}
            mt={5}
            color="textPrimary"
            gutterBottom
          >
            {props.screenTitle}
          </Typography>
        </Grid>
        <Grid item xs={12}>
          <Button
            color="secondary"
            variant="contained"
            onClick={() => {
              navigate("/");
            }}
            sx={{ marginRight: 1 }}
          >
            <ArrowBackIcon sx={{ fontSize: 24 }} />
            Back to Dashboard
          </Button>
        </Grid>
        <Grid item xs={12} mt={5}>
          <Paper style={{ paddingBottom: 20 }}>
            {/* <BBViewPageLoader loadingText="Loading Settings"> */}
            <Grid container spacing={3}>
              <Grid
                item
                xs={2}
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "start",
                }}
              >
                <img
                  src={user.picture}
                  alt={user.name}
                  style={{
                    borderRadius: "50%",
                    width: "100%",
                    maxWidth: 100,
                    marginLeft: 50,
                  }}
                />
              </Grid>
              <Grid item xs={10}>
                <Grid container spacing={3}>
                  <Grid
                    item
                    xs={12}
                    md={6}
                    lg={4}
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Stack spacing={1} style={{ minWidth: "80%" }}>
                      <FormLabel>Nickname</FormLabel>
                      <TextField
                        disabled
                        variant="outlined"
                        label={user?.nickname}
                        color="secondary"
                      />
                    </Stack>
                  </Grid>
                  <Grid
                    item
                    xs={12}
                    md={6}
                    lg={4}
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Stack spacing={1} style={{ minWidth: "80%" }}>
                      <FormLabel>Email</FormLabel>
                      <TextField
                        disabled
                        variant="outlined"
                        label={user?.name}
                        color="secondary"
                      />
                    </Stack>
                  </Grid>
                  <Grid
                    item
                    xs={12}
                    md={6}
                    lg={4}
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Stack spacing={1} style={{ minWidth: "80%" }}>
                      <FormLabel>Organization</FormLabel>
                      <TextField
                        disabled
                        variant="outlined"
                        label={user?.[`${window.location.origin}/organization`]}
                        color="secondary"
                      />
                    </Stack>
                  </Grid>
                  <Grid
                    item
                    xs={12}
                    md={6}
                    lg={4}
                    sx={{
                      display: "flex",
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Stack spacing={1} style={{ minWidth: "80%" }}>
                      <FormLabel>Groups</FormLabel>
                      <TextField
                        disabled
                        variant="outlined"
                        label={user?.[`${window.location.origin}/groups`]?.join(
                          ", "
                        )}
                        color="secondary"
                      />
                    </Stack>
                  </Grid>
                </Grid>
              </Grid>
            </Grid>
            {/* </BBViewPageLoader> */}
          </Paper>
          <Paper
            style={{
              marginTop: 10,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Box sx={{ width: 300 }}>
              <List
                sx={{
                  width: "100%",
                }}
              >
                <ListItem>
                  <ListItemIcon>
                    <BrushIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Style System"
                    sx={{ color: grey[600] }}
                  />
                  <Switch
                    edge="end"
                    disabled
                    onChange={() => {
                      dispatch(toggleStyleSystem());
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
          </Paper>
        </Grid>
      </Grid>
    </BBViewShell>
  );
};

export default UserProfile;

/**
 * @typedef {import('../../../store.js').Store} Store
 */
