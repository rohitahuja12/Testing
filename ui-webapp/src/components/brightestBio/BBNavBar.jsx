import React, { useMemo } from "react";
import AppBar from "@mui/material/AppBar";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import { useTheme } from "@mui/material/styles";
import { useNavigate } from "react-router-dom";
import { yellow } from "@mui/material/colors";
import { Auth } from "aws-amplify";
import { useAuth0 } from "@auth0/auth0-react";
import {
  getUrlFromDomainWithProtocol,
  httpResourceApiUrl,
} from "../../api/client";

const LoginButton = () => {
  const { loginWithRedirect } = useAuth0();

  return <button onClick={() => loginWithRedirect()}>Log In</button>;
};

/**
 *
 * @param {{title: string, version: string}} props
 * @returns
 */
const BBNavBar = (props) => {
  const { logout, user } = useAuth0();

  const appTitle = useMemo(
    () => props?.title || "Brightest Bio",
    [props?.title]
  );
  const appVersion = useMemo(() => props?.version || "1.0.0", [props?.version]);
  const navigate = useNavigate();
  const theme = useTheme();
  const renderChip = (themeMode) => {
    const isDarkTheme = themeMode === "dark";
    const options = {
      marginLeft: 1,
      fontWeight: 700,
      fontSize: 12,
    };
    if (isDarkTheme) {
      return (
        <Chip
          label={appVersion}
          sx={{ ...options, bgcolor: yellow[700], color: "black" }}
        />
      );
    }
    return <Chip label={appVersion} sx={options} color="secondary" />;
  };
  const modeAwareChip = useMemo(() => {
    return renderChip(theme.palette.mode);
  }, [theme.palette.mode]);

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="fixed" color="primary">
        <Toolbar>
          <Typography
            variant="h4"
            component="div"
            sx={{ flexGrow: 1, cursor: "pointer" }}
            onClick={() => {
              navigate("/");
            }}
          >
            {appTitle}
            {modeAwareChip}
          </Typography>
          {
            <>
              <Button
                onClick={() => {
                  logout({ returnTo: `${httpResourceApiUrl}/login` });
                }}
                color="secondary"
                variant="outlined"
              >
                Sign Out
              </Button>
              {user && (
                <IconButton
                  aria-label="profile"
                  onClick={() => {
                    navigate("/profile");
                  }}
                  style={{ marginLeft: 10 }}
                >
                  <img
                    src={user?.picture}
                    alt="profile"
                    style={{ borderRadius: "50%", maxWidth: 25 }}
                  />
                </IconButton>
              )}
            </>
          }
        </Toolbar>
      </AppBar>
    </Box>
  );
};

export default BBNavBar;
