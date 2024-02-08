import { createAsyncThunk } from "@reduxjs/toolkit";
import {
  setAnalysisImages,
  setAnalysisTemplates,
  setDefaultPlateMaps,
  setLastSavedAnalysis,
  setSavedAnalysisStatus,
  setSavedAnalysisTemplate,
  setAnalyses,
  setLoadedAnalysis,
  setLoadedAnalysisTemplate,
  analysisTemplateDeleted,
  setDownloadFileUrl,
  analysisDeleted,
} from "../features/analysis/analysisSlice";
import { setLoadingData, showSnackbar } from "../features/system/systemSlice";
import * as client from "./../api/client";
import { getAccessToken } from "./authenticationHelper";
import { blobToDataURL } from "../utils/fileUtils";

export const getAnalysisTemplates = createAsyncThunk(
  "resource-api/analysisTemplates",
  async (omissions, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      thunkAPI.dispatch(setLoadingData(true));
      const analysisTemplates = await client.getAnalysisTemplates(
        omissions,
        accessToken
      );
      thunkAPI.dispatch(setAnalysisTemplates(analysisTemplates));
      thunkAPI.dispatch(setLoadingData(false));
    } catch (e) {
      thunkAPI.dispatch(setLoadingData(false));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Cannot load templates. Try again later.",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);

export const getAnalysisTemplate = createAsyncThunk(
  "resource-api/analysisTemplates",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const analysisTemplate = await client.getAnalysisTemplate(
        id,
        accessToken
      );
      thunkAPI.dispatch(setLoadedAnalysisTemplate(analysisTemplate));
    } catch (e) {
      console.error(e);
    }
  }
);

export const getDefaultPlateMaps = createAsyncThunk(
  "resource-api/defaultPlateMaps",
  async (args, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const defaultPlateMaps = await client.getDefaultPlateMaps(accessToken);
      thunkAPI.dispatch(setDefaultPlateMaps(defaultPlateMaps));
    } catch (e) {
      console.error(e);
    }
  }
);

export const saveAnalysisTemplate = createAsyncThunk(
  "resource-api/analysisTemplate",
  async (template, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const savedTemplate = await client.postAnalysisTemplate(
        template,
        accessToken
      );
      thunkAPI.dispatch(setSavedAnalysisTemplate(savedTemplate));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Template saved",
          severity: "success",
        })
      );
    } catch (e) {
      thunkAPI.dispatch(
        showSnackbar({
          message: "Template save failed",
          severity: "error",
        })
      );
      thunkAPI.dispatch(setSavedAnalysisTemplate({ error: true }));
      console.error(e);
    }
  }
);

export const deleteAnalysisTemplate = createAsyncThunk(
  "resource-api/analysisTemplate",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const deletedTemplateResponse = await client.deleteAnalysisTemplate(
        id,
        accessToken
      );
      if (deletedTemplateResponse) {
        thunkAPI.dispatch(analysisTemplateDeleted(id));
        thunkAPI.dispatch(
          showSnackbar({
            message: "Template deleted",
            severity: "success",
          })
        );
      } else {
        thunkAPI.dispatch(
          showSnackbar({
            message: "Template failed",
            severity: "error",
          })
        );
      }
    } catch (e) {
      thunkAPI.dispatch(
        showSnackbar({
          message: "Template delete failed",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);

export const deleteAnalysis = createAsyncThunk(
  "resource-api/analysis",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const deletedAnalysisResponse = await client.deleteAnalysis(
        id,
        accessToken
      );
      thunkAPI.dispatch(analysisDeleted(id));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Analysis deleted",
          severity: "success",
        })
      );
    } catch (e) {
      console.error(e);
    }
  }
);

export const saveAnalysis = createAsyncThunk(
  "resource-api/analysis",
  async (analysis, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const template = await client.getAnalysisTemplate(
        analysis.templateId,
        accessToken
      );
      const analysisWithProtocolArgs = {
        ...template,
        ...analysis,
        _id: undefined,
      };
      const savedAnalysis = await client.postAnalysis(
        analysisWithProtocolArgs,
        accessToken
      );
      if (savedAnalysis && savedAnalysis._id) {
        thunkAPI.dispatch(setSavedAnalysisStatus(200));
        thunkAPI.dispatch(setLastSavedAnalysis(savedAnalysis));
        thunkAPI.dispatch(
          showSnackbar({
            message: "Analysis created",
            severity: "success",
          })
        );
      } else {
        thunkAPI.dispatch(
          showSnackbar({
            message: "Analysis creation failed",
            severity: "error",
          })
        );
        thunkAPI.dispatch(setSavedAnalysisStatus(400));
        thunkAPI.dispatch(setLastSavedAnalysis({ error: true }));
      }
    } catch (e) {
      console.error(e);
      thunkAPI.dispatch(
        showSnackbar({
          message: "Analysis creation failed",
          severity: "error",
        })
      );
      thunkAPI.dispatch(setSavedAnalysisStatus(400));
      thunkAPI.dispatch(setLastSavedAnalysis({ error: true }));
    }
  }
);

export const getFileUrl = (analysisId, filename) =>
  `${client.httpResourceApiUrl}/analyses/${analysisId}/attachments/${filename}`;

export const getAttachments = createAsyncThunk(
  "resource-api/attachments",
  async (analysisId, thunkAPI) => {
    // file url example
    // https://dev.api.brightestbio.com/analyses/${collapse?.analyses?.id}/attachments/${image}
    try {
      const accessToken = getAccessToken(thunkAPI);
      const attachments = await client.getAnalysisAttachments(
        analysisId,
        accessToken
      );

      // phoen 82: https://brightestbio.atlassian.net/jira/software/projects/PHOEN/boards/1?selectedIssue=PHOEN-82
      const promises = attachments
        .filter(
          (attachment) =>
            attachment.filename.includes("preview") &&
            attachment.filename.includes("jpg") &&
            !attachment.filename.includes("jpg_preview")
        )
        .map(async (attachment) => {
          const blob = await client.getAnalysisAttachmentByName(
            analysisId,
            attachment.filename,
            accessToken
          );

          return await blobToDataURL(blob);
        });

      const imageUrls = await Promise.all(promises);
      const downloadFileName = attachments.find((attachment) =>
        attachment.filename.includes(".zip")
      )?.filename;

      const downloadFileBlob = await client.getAnalysisAttachmentByName(
        analysisId,
        downloadFileName,
        accessToken
      );
      const downloadFileUrl = await blobToDataURL(downloadFileBlob);

      thunkAPI.dispatch(setAnalysisImages(imageUrls));
      thunkAPI.dispatch(setDownloadFileUrl(downloadFileUrl));
    } catch (e) {
      console.error(e);
    }
  }
);

export const getAnalysesWithoutWellData = createAsyncThunk(
  "resource-api/analyses",
  async (args, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      thunkAPI.dispatch(setLoadingData(true));
      const analyses = await client.getAnalyses(["protocolArgs"], accessToken);
      thunkAPI.dispatch(setAnalyses(analyses));
      thunkAPI.dispatch(setLoadingData(false));
    } catch (e) {
      thunkAPI.dispatch(setLoadingData(false));
      thunkAPI.dispatch(
        showSnackbar({
          message: "Cannot load scans. Try again later.",
          severity: "error",
        })
      );
      console.error(e);
    }
  }
);

export const getAnalysis = createAsyncThunk(
  "resource-api/analysis",
  async (id, thunkAPI) => {
    try {
      const accessToken = getAccessToken(thunkAPI);
      const analysis = await client.getAnalysis(id, accessToken);
      thunkAPI.dispatch(setLoadedAnalysis(analysis));
    } catch (e) {
      console.error(e);
    }
  }
);
