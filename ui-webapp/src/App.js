import React, { useCallback } from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "./store.js";
import Dashboard from "./components/brightestBio/pages/dashboard.jsx";
import Layout from "./components/brightestBio/pages/layout.jsx";
import WebsocketClient from "./components/WebsocketClient.jsx";
import ViewAnalyses from "./components/brightestBio/pages/ViewAnalyses.jsx";
import BBSnackbar from "./components/brightestBio/BBSnackbar.jsx";
import ViewScans from "./components/brightestBio/pages/ViewScans.jsx";
import CreateScan from "./components/brightestBio/pages/CreateScan.jsx";
import BBViewReaders from "./components/brightestBio/pages/BBViewReaders.jsx";
import BBCreateAnalysis from "./components/brightestBio/pages/CreateAnalysis.jsx";
import BBViewDocuments from "./components/brightestBio/pages/BBViewDocuments.jsx";
import BBViewAnalysisTemplates from "./components/brightestBio/pages/BBViewAnalysisTemplates.jsx";
import CreateAnalysisTemplate from "./components/brightestBio/pages/CreateAnalysisTemplate.jsx";
import "@aws-amplify/ui-react/styles.css";
import PrivateRoute from "./components/auth/PrivateRoute.jsx";
import Login from "./components/auth/Login.jsx";
import ManageOrganization from "./components/brightestBio/pages/ManageOrganization.jsx";
import { Auth0Provider } from "@auth0/auth0-react";
import UserProfile from "./components/brightestBio/pages/UserProfile.jsx";

// TODO: look into RBAC for auth0 to not define scopes globally.
const scopes = [
  "openid",
  "offline_access",
  "read:readers",
  "write:readers",
  "read:scans",
  "write:scans",
  "read:analyses",
  "write:analyses",
  "read:analysisTemplates",
  "write:analysisTemplates",
  "read:products",
  "read:analysisAttachments",
  "read:scanAttachments",
  "read:plates",
  "read:featureFlagSets",
  "read:defaultPlateMaps",
  "write:defaultPlateMaps",
  "read:analysisAttachments",
  "read:scanAttachments,",
  "openid profile",
];

const App = () => {
  const createProtectedRoute = useCallback((path, Component, screenTitle) => {
    return (
      <Route
        path={path}
        element={
          <PrivateRoute>
            <Component screenTitle={screenTitle} />
          </PrivateRoute>
        }
      />
    );
  }, []);

  try {
    const app = (
      <Auth0Provider
        domain={process.env.REACT_APP_AUTH_DOMAIN}
        clientId={process.env.REACT_APP_AUTH_CLIENT_ID}
        authorizationParams={{
          redirect_uri: window.location.origin,
          audience: process.env.REACT_APP_AUTH_AUDIENCE,
          grant_type: "client_credentials",
          scope: scopes.join(" "),
        }}
        grant_type="client_credentials"
        useRefreshTokens={true}
        cacheLocation="localstorage"
      >
        <Provider store={store}>
          <PrivateRoute silent>
            <WebsocketClient />
          </PrivateRoute>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              {createProtectedRoute("/", Dashboard, "Dashboard")}
              {createProtectedRoute("/profile", UserProfile, "My Profile")}

              <Route path="/analyze" element={<Layout />}>
                {createProtectedRoute(
                  "/analyze/create",
                  BBCreateAnalysis,
                  "Create Analysis"
                )}
              </Route>

              <Route path="/analysis-template" element={<Layout />}>
                {createProtectedRoute(
                  "/analysis-template/view-all",
                  BBViewAnalysisTemplates,
                  "Analysis Templates"
                )}
                {createProtectedRoute(
                  "/analysis-template/create",
                  CreateAnalysisTemplate,
                  "Create Analysis Template"
                )}
              </Route>

              <Route path="/scan" element={<Layout />}>
                {createProtectedRoute(
                  "/scan/create",
                  CreateScan,
                  "Create Scan"
                )}
                {createProtectedRoute("/scan/view-all", ViewScans, "Scans")}
              </Route>

              <Route path="/reader" element={<Layout />}>
                {createProtectedRoute(
                  "/reader/view-all",
                  BBViewReaders,
                  "Readers"
                )}
              </Route>

              <Route path="/view-results" element={<Layout />}>
                {createProtectedRoute(
                  "/view-results/analyses",
                  ViewAnalyses,
                  "Analyses"
                )}
              </Route>

              <Route path="/documents" element={<Layout />}>
                {createProtectedRoute(
                  "/documents/view-all",
                  BBViewDocuments,
                  "Documents"
                )}
              </Route>

              <Route path="/organization" element={<Layout />}>
                {createProtectedRoute(
                  "/organization/manage",
                  ManageOrganization,
                  "Organization"
                )}
              </Route>
            </Routes>
          </BrowserRouter>
          <BBSnackbar />
        </Provider>
      </Auth0Provider>
    );
    return app;
  } catch (err) {
    console.debug(err);
    window.location.href = window.location.origin + "/login";
    return <></>;
  }
};

export default App;
