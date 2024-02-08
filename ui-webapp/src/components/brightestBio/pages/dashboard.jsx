import React, { useState, useCallback, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch } from "react-redux";
import { setFlowType, flowTypes } from "../../../features/flow/flowSlice.js";
import { setCalibrationStatus } from "../../../features/system/systemSlice.js";
import { getDefaultReader } from "../../../actions/readerActions.js";
import { reset } from "../../../features/scan/scanSlice.js";
import { reset as analysisReset } from "../../../features/analysis/analysisSlice.js";
import { Grid as MUIGrid, Typography } from "@mui/material";
import BBDashboardActionCard from "../BBDashboardActionCard.jsx";
import BBViewShell from "../BBViewShell.jsx";
import BBSettingsModal from "../BBSettingsModal.jsx";

/**
 *
 * @param {signOut: function} props
 * @returns
 */
export default function Dashboard(props) {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  // const { getUserAttributes } = useAuth();
  const [openSettingsModal, setOpenSettingsModal] = useState(false);
  // const userAttributes = getUserAttributes();

  const getInitialCalibrationData = async () => {
    dispatch(setCalibrationStatus(String(new Date())));
  };

  useEffect(() => {
    getInitialCalibrationData();
    dispatch(setFlowType({ type: flowTypes.NONE }));
    dispatch(reset());
    dispatch(getDefaultReader());
    dispatch(analysisReset());
  }, []);

  const toScanCreation = useCallback(() => {
    //MUI scan creation page
    dispatch(setFlowType({ type: flowTypes.SCAN }));
    navigate("/scan/create", { replace: true });
  }, [navigate]);
  const toAnalysisCreation = useCallback(() => {
    //MUI analysis creation page
    navigate("/analyze/create", { replace: true });
  }, [navigate]);
  const toViewAnalysisTemplates = useCallback(() => {
    //MUI view analysis templates page
    navigate("/analysis-template/view-all", { replace: true });
  }, [navigate]);
  const toCreateAnalysisTemplate = useCallback(() => {
    //MUI create analysis template page
    navigate("/analysis-template/create", { replace: true });
  }, [navigate]);
  const toViewResults = useCallback(() => {
    dispatch(setFlowType({ type: flowTypes.VIEW_RESULTS }));
    navigate("/view-results/analyses", { replace: true });
  }, [navigate]);
  const toViewScans = useCallback(() => {
    dispatch(setFlowType({ type: flowTypes.VIEW_SCANS }));
    navigate("/scan/view-all", { replace: true });
  }, [navigate]);
  const toViewReaders = useCallback(() => {
    navigate("/reader/view-all", { replace: true });
  }, [navigate]);
  const toViewDocuments = useCallback(() => {
    navigate("/documents/view-all", { replace: true });
  }, [navigate]);
  const toManageOrganization = useCallback(() => {
    navigate("/organization/manage", { replace: true });
  }, [navigate]);

  const scanImage = useMemo(
    () => require("./../../../assets/setupscan.png"),
    []
  );
  const analysisImage = useMemo(
    () => require("./../../../assets/analyzescan.png"),
    []
  );

  const templateImage = useMemo(
    () => require("./../../../assets/template.png"),
    []
  );

  /**
   * Creates a Dashboard Action Card
   * @param {string} title
   * @param {string} description
   * @param {string} image
   * @param {string} imageAlt
   * @param {Array} actionButtons
   * @param {boolean} compact
   * @returns {JSX.Element}
   */
  const createActionCard = useCallback(
    (
      title,
      description,
      image,
      imageAlt,
      actionButtons,
      defaultAction,
      compact = false
    ) => {
      return (
        <BBDashboardActionCard
          title={title}
          description={description}
          image={image}
          imageAlt={imageAlt}
          actionButtons={actionButtons}
          defaultAction={defaultAction}
          compact={compact}
        />
      );
    },
    []
  );

  return (
    <>
      {
        <BBViewShell alignItems="start" signOut={props?.signOut}>
          <MUIGrid container spacing={3}>
            <MUIGrid item xs={12}>
              <Typography
                variant="h2"
                component="h1"
                mt={5}
                color="textPrimary"
                gutterBottom
              >
                Empower Dashboard
              </Typography>
            </MUIGrid>
            {/* scan card */}
            <MUIGrid item xs={12} md={6} lg={4}>
              {createActionCard(
                "Scans",
                "Scan a plate on a reader.",
                scanImage,
                "Set up Scan",
                [
                  {
                    name: "View",
                    action: () => toViewScans(),
                  },
                  {
                    name: "Create",
                    action: () => toScanCreation(),
                  },
                ],
                () => toViewScans()
              )}
            </MUIGrid>

            {/* analysis templates card  */}
            <MUIGrid item xs={12} md={6} lg={4}>
              {createActionCard(
                "Analysis Templates",
                "Create, upload, copy, or modify an analysis template.",
                templateImage,
                "Analysis Templates",
                [
                  {
                    name: "View",
                    action: () => toViewAnalysisTemplates(),
                  },
                  {
                    name: "Create",
                    action: () => toCreateAnalysisTemplate(),
                  },
                ],
                () => toViewAnalysisTemplates()
              )}
            </MUIGrid>

            {/* analyses card */}
            <MUIGrid item xs={12} md={6} lg={4}>
              {createActionCard(
                "Analyses",
                "Select a scan and an analysis template to set up an analysis.",
                analysisImage,
                "Analysis",
                [
                  {
                    name: "View",
                    action: () => toViewResults(),
                  },
                  {
                    name: "Create",
                    action: () => toAnalysisCreation(),
                  },
                ],
                () => toViewResults()
              )}
            </MUIGrid>

            {/* readers and potentially products in the future? */}
            <MUIGrid item xs={12} md={6} lg={4}>
              <MUIGrid container spacing={3}>
                <MUIGrid item xs={12}>
                  {createActionCard(
                    "Readers",
                    "Manage your Brightest Bio Readers.",
                    null,
                    null,
                    [
                      {
                        name: "View",
                        action: () => toViewReaders(),
                      },
                    ],
                    () => toViewReaders(),
                    true
                  )}
                </MUIGrid>
                {/* docs card */}
                <MUIGrid item xs={12}>
                  {createActionCard(
                    "Documents",
                    "Learn about your Brightest Bio Readers.",
                    null,
                    null,
                    [
                      {
                        name: "View",
                        action: () => toViewDocuments(),
                      },
                    ],
                    () => toViewDocuments(),
                    true
                  )}
                </MUIGrid>
              </MUIGrid>
            </MUIGrid>
            <MUIGrid item xs={12} md={6} lg={4}>
              <MUIGrid container spacing={3}>
                {("userAttributes?.group" === "devs" ||
                  "userAttributes?.group " === "admins") && (
                  <MUIGrid item xs={12}>
                    {createActionCard(
                      "Organization",
                      "Manage your organization.",
                      null,
                      null,
                      [
                        {
                          name: "Open",
                          action: () => {
                            toManageOrganization();
                          },
                        },
                      ],
                      () => {
                        toManageOrganization();
                      },
                      true
                    )}
                  </MUIGrid>
                )}
              </MUIGrid>
            </MUIGrid>
          </MUIGrid>
        </BBViewShell>
      }
    </>
  );
}
