import React, { useState, useMemo, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import BBViewShell from "../BBViewShell.jsx";
import {
  Grid,
  Typography,
  Paper,
  Button,
  IconButton,
  TextField,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
} from "@mui/material";
import { useNavigate, useSearchParams, Navigate } from "react-router-dom";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useAuth } from "../hooks/useAuth.js";
import { saveNewUser } from "../../../actions/organizationActions.js";

/**
 *
 * @param {{
 * screenTitle: string,
 * signOut: function
 * }} props
 */
const ManageOrganization = (props) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { getUserAttributes } = useAuth();
  const [newUser, setNewUser] = useState(null);
  const userAttributes = getUserAttributes();

  useEffect(() => {
    if (
      userAttributes?.group !== "devs" &&
      userAttributes?.group !== "admins"
    ) {
      navigate("/");
    }
  }, [userAttributes]);

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
          <Paper style={{ padding: 25 }}>
            <Grid container spacing={3}>
              <Grid
                item
                xs={12}
                style={{
                  display: "flex",
                  flexDirection: "row",
                  justifyContent: "space-between",
                }}
              >
                <Typography variant="h6">Create New User</Typography>
                <Button
                  color="secondary"
                  variant="outlined"
                  disabled={
                    !newUser ||
                    !newUser?.name ||
                    !newUser?.email ||
                    !newUser?.organization ||
                    !newUser?.group ||
                    !newUser?.username
                  }
                  onClick={() => {
                    dispatch(saveNewUser(newUser));
                    setNewUser({
                      name: "",
                      email: "",
                      organization: "",
                      group: "",
                      username: "",
                    });
                  }}
                >
                  Create
                </Button>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  id="email"
                  label="Email"
                  variant="outlined"
                  color="secondary"
                  required
                  value={newUser?.email}
                  // error={}
                  // helperText={}
                  onChange={(event) => {
                    setNewUser((user) => ({
                      ...user,
                      email: event.target.value,
                    }));
                  }}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  id="username"
                  label="Username"
                  variant="outlined"
                  color="secondary"
                  required
                  value={newUser?.username}
                  // error={}
                  // helperText={}
                  onChange={(event) => {
                    setNewUser((user) => ({
                      ...user,
                      username: event.target.value,
                    }));
                  }}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  id="fullname"
                  label="Full Name"
                  variant="outlined"
                  color="secondary"
                  required
                  value={newUser?.name}
                  // error={}
                  // helperText={}
                  onChange={(event) => {
                    setNewUser((user) => ({
                      ...user,
                      name: event.target.value,
                    }));
                  }}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel
                    required
                    color="secondary"
                    id="group-select-label"
                  >
                    Role
                  </InputLabel>
                  <Select
                    color="secondary"
                    variant="outlined"
                    labelId="group-select-label"
                    id="group-select"
                    label="Role"
                    value={newUser?.group || ""}
                    defaultValue={""}
                    onChange={(event) => {
                      setNewUser((user) => ({
                        ...user,
                        group: event.target.value,
                        organization: userAttributes?.organization,
                      }));
                    }}
                  >
                    <MenuItem value=""></MenuItem>
                    <MenuItem value="admins">Administrator</MenuItem>
                    <MenuItem value="devs">Developer</MenuItem>
                    <MenuItem value="labusers">Lab User</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </BBViewShell>
  );
};

export default ManageOrganization;
