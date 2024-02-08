import { useState, useCallback, useEffect, useMemo } from "react";
import { useAuth0 } from "@auth0/auth0-react";

import {
  CognitoUserPool,
  CognitoUserAttribute,
  CognitoUser,
  AuthenticationDetails,
} from "amazon-cognito-identity-js";

const COGNITO_POOL = {
  UserPoolId: "us-east-2_gFx4baNIP",
  ClientId: "31051lqjare1fh3aqolff6u71g",
};

const getUserAttributes = () => {
  const userPool = new CognitoUserPool(COGNITO_POOL);
  const cognitoUser = userPool.getCurrentUser();
  const attributes = cognitoUser.getSession((err, session) => {
    if (err) {
      console.error(err || JSON.stringify(err));
      return;
    }
    const idToken = session?.idToken?.payload;
    return {
      userName: idToken?.["cognito:username"],
      group: idToken?.["custom:group"],
      organization: idToken?.["custom:organization"],
      email: idToken?.["email"],
    };
  });
  return attributes;
};

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const poolData = useMemo(() => COGNITO_POOL, [COGNITO_POOL]);
  const userPool = useMemo(() => new CognitoUserPool(poolData), [poolData]);
  const [mutableUserAttributes, setMutableUserAttributes] = useState({});
  const [AuthedCognitoUser, setAuthedCognitoUser] = useState(null);
  const [newPasswordRequired, setNewPasswordRequired] = useState(false);
  const [authError, setAuthError] = useState(null);
  const { getAccessTokenSilently } = useAuth0();

  const getAccessToken = useCallback(async () => {
    try {
      const accessToken = await getAccessTokenSilently();
      return accessToken;
    } catch (error) {
      if (window.location.pathname.includes("/login")) return;
      window.location.href = window.location.origin + '/login';
    }

  }, [getAccessTokenSilently]);

  const getAuthedUserIfExists = () => {
    if (AuthedCognitoUser) return AuthedCognitoUser;
    if (!localStorage.getItem("username")) return null;
    const userData = {
      Username: localStorage.getItem("username"),
      Pool: userPool,
    };
    const cognitoUser = new CognitoUser(userData);
    setAuthedCognitoUser(cognitoUser);
    return cognitoUser;
  };

  const checkAuth = useCallback(
    (onSuccess, onFailure) => {
      if (isAuthenticated) {
        onSuccess();
        return;
      }
      {
        const cognitoUser = getAuthedUserIfExists();
        if (!cognitoUser) {
          onFailure();
          return;
        }
        cognitoUser.getSession((err, session) => {
          if (err) {
            // alert(err.message || JSON.stringify(err));
            setAuthError(err.message || JSON.stringify(err));
            onFailure();
            return;
          }
          setIsAuthenticated(true);
          onSuccess();
        });
      }
    },
    [
      isAuthenticated,
      userPool,
      setAuthedCognitoUser,
      AuthedCognitoUser,
      setAuthError,
    ]
  );

  const handleNewPassword = useCallback(
    (password, onSuccess) => {
      if (!AuthedCognitoUser) {
        // alert('Please contact your administrator.');
        setAuthError("Please contact your administrator.");
        return;
      }
      AuthedCognitoUser.completeNewPasswordChallenge(
        password,
        mutableUserAttributes,
        {
          onSuccess: (result) => {
            setIsAuthenticated(true);
            setNewPasswordRequired(false);
            onSuccess();
          },
          onFailure: (err) => {
            setAuthError(err.message || JSON.stringify(err));
          },
        }
      );
    },
    [
      mutableUserAttributes,
      AuthedCognitoUser,
      setIsAuthenticated,
      setNewPasswordRequired,
      setAuthError,
    ]
  );

  const loginWithCredentials = useCallback(
    (username, password, onSuccess) => {
      const authenticationData = {
        Username: username,
        Password: password,
      };
      const authenticationDetails = new AuthenticationDetails(
        authenticationData
      );
      const poolData = {
        UserPoolId: "us-east-2_gFx4baNIP",
        ClientId: "31051lqjare1fh3aqolff6u71g",
      };
      const userPool = new CognitoUserPool(poolData);
      const userData = {
        Username: username,
        Pool: userPool,
      };
      const cognitoUser = new CognitoUser(userData);
      setAuthedCognitoUser(cognitoUser);
      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (result) {
          localStorage.setItem("username", username);
          setIsAuthenticated(true);
          onSuccess();
        },
        onFailure: function (err) {
          setAuthError(err.message || JSON.stringify(err));
        },
        newPasswordRequired: function (userAttributes, requiredAttributes) {
          delete userAttributes.email_verified;
          delete userAttributes.phone_number_verified;
          delete userAttributes.phone_number;
          delete userAttributes.email;
          setMutableUserAttributes(userAttributes);
          setNewPasswordRequired(true);
        },
      });
    },
    [
      setNewPasswordRequired,
      setIsAuthenticated,
      setMutableUserAttributes,
      AuthedCognitoUser,
      setAuthedCognitoUser,
      setAuthError,
    ]
  );

  return {
    loginWithCredentials,
    isAuthenticated,
    checkAuth,
    newPasswordRequired,
    handleNewPassword,
    setNewPasswordRequired,
    authError,
    setAuthError,
    getUserAttributes,
    getAccessToken,
  };
};
