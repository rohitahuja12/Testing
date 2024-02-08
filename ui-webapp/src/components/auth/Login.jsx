import React, { useState, useCallback, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Auth } from "aws-amplify";
import {
  Grid,
  TextField,
  Button,
  IconButton,
  InputAdornment,
  Typography,
} from "@mui/material";
import Logo from "../../assets/logo/primary small-use_full color.png";
import {
  Visibility,
  VisibilityOff,
  AlternateEmail,
  Dialpad,
} from "@mui/icons-material";
// import { useAuth } from "../brightestBio/hooks/useAuth.js";
import { useAuth0 } from "@auth0/auth0-react";

const Login = () => {
  const { loginWithRedirect } = useAuth0();

  return (
    <Grid
      container
      direction="column"
      justifyContent="center"
      alignItems="center"
      spacing={2}
    >
      <>
        <Grid item>
          <Typography variant="h6" sx={{ marginBottom: "20px" }}>
            Welcome to Brightest Bio
          </Typography>
        </Grid>

        <Grid item>
          <Button variant="contained" onClick={() => loginWithRedirect()}>
            Log In
          </Button>
        </Grid>
      </>
    </Grid>
  );
};

const LoginCard = () => {
  return (
    <Grid
      container
      direction="column"
      justifyContent="center"
      alignItems="center"
      sx={{
        height: "100vh",
        width: "100vw",
        backgroundColor: "#f5f5f5",
      }}
    >
      <Grid
        item
        sx={{
          backgroundColor: "#f5f5f5",
          borderRadius: "10px",
          padding: "20px",
          boxShadow: "0px 0px 10px 0px rgba(0,0,0,0.2)",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          width: "400px",
        }}
      >
        <img
          style={{
            width: "175px",
            height: "auto",
            marginBottom: "40px",
          }}
          src={Logo}
          alt="Brightest Bio Logo"
        />
        <Login />
      </Grid>
    </Grid>
  );
};

export default LoginCard;
