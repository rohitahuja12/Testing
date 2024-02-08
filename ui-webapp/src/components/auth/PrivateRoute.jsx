import React, { useEffect } from "react";
import { withAuthenticationRequired } from "@auth0/auth0-react";
import { BBLoader } from "../brightestBio/BBLoader";
import { useAuth } from "../brightestBio/hooks/useAuth";
import { useDispatch, useSelector } from "react-redux";
import { setToken } from "../../features/system/systemSlice";
import { BBViewPageLoader } from "../brightestBio/BBViewPageLoader";

const PrivateRoute = withAuthenticationRequired(
  ({ children, silent = false }) => {
    const { getAccessToken } = useAuth();
    const dispatch = useDispatch();
    const { token } = useSelector((state) => state?.system) || {};

    useEffect(() => {
      try {
        const getAccessTokenSilently = async () => {
          const token = await getAccessToken();
          dispatch(setToken(token));
        };
        getAccessTokenSilently();
      } catch (error) {
        if (window.location.pathname.includes("/login")) return;
        window.location.href = window.location.origin + "/login";
      }
    }, [getAccessToken]);

    return token ? children : silent ? <></> : <></>;
  },
  {
    returnTo: () => window.location.pathname,
    onRedirecting: () => (
      <div style={{ position: "absolute", left: "50%", top: "50%" }}>
        <div
          style={{
            position: "relative",
            left: "-50%",
            top: "50%",
          }}
        >
          <BBLoader size="lg" />
        </div>
      </div>
    ),
  }
);

export default PrivateRoute;
