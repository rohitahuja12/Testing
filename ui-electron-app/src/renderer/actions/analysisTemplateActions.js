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
    setLoadedAnalysisTemplate
} from "../features/analysis/analysisSlice";
import * as client from './../api/client';

export const getAnalysisTemplates = createAsyncThunk('resource-api/analysisTemplates',
    async (omissions, thunkAPI) => {
        try {

            const analysisTemplates = await client.getAnalysisTemplates(omissions);
            thunkAPI.dispatch(setAnalysisTemplates(analysisTemplates));
        } catch (e) {
            console.error(e);
        }
    }
);

export const getAnalysisTemplate = createAsyncThunk('resource-api/analysisTemplates',
    async (id, thunkAPI) => {
        try {
            const analysisTemplate = await client.getAnalysisTemplate(id);
            thunkAPI.dispatch(setLoadedAnalysisTemplate(analysisTemplate));
        } catch (e) {
            console.error(e);
        }
    }
);


export const getDefaultPlateMaps = createAsyncThunk('resource-api/defaultPlateMaps',
    async (args, thunkAPI) => {
        try {
            const defaultPlateMaps = await client.getDefaultPlateMaps();
            thunkAPI.dispatch(setDefaultPlateMaps(defaultPlateMaps));
        } catch (e) {
            console.error(e);
        }
    }
);

export const saveAnalysisTemplate = createAsyncThunk('resource-api/analysisTemplate',
    async (template, thunkAPI) => {
        try {
            const state = thunkAPI.getState();
            const savedTemplate = await client.postAnalysisTemplate(template);
            thunkAPI.dispatch(setSavedAnalysisTemplate(savedTemplate));

        } catch (e) {
            console.error(e);
        }
    }
);

export const saveAnalysis = createAsyncThunk('resource-api/analysis',
    async (analysis, thunkAPI) => {
        try {
            console.log('getting template data for analysis...', analysis);
            const template = await client.getAnalysisTemplate(analysis.templateId);
            console.log('saving analysis with template', template);
            const analysisWithProtocolArgs = { 
                ...template,
                ...analysis,
                _id: undefined
            }
            console.log('saving analysis...', analysisWithProtocolArgs)
            const savedAnalysis = await client.postAnalysis(analysisWithProtocolArgs);
            if (savedAnalysis && savedAnalysis._id) {
                thunkAPI.dispatch(setSavedAnalysisStatus(200));
                thunkAPI.dispatch(setLastSavedAnalysis(savedAnalysis));
            } else {
                //TODO: actually handle error cases
                thunkAPI.dispatch(setSavedAnalysisStatus(400));
            }
        } catch (e) {
            console.error(e);
        }

    }
);

export const getAttachments = createAsyncThunk('resource-api/attachments',
    async (analysisId, thunkAPI) => {
        try {
            console.log('getting attachments')
            const attachments = await client.getAnalysisAttachments(analysisId);
            const images = await Promise.all(attachments.map(async (attachment) => {
                const blob = await client.getAnalysisAttachmentByName(analysisId, attachment.filename);
                console.log('blob', blob);
                return URL.createObjectURL(blob);
            }))
            console.log('attempting to save images', images);
            thunkAPI.dispatch(setAnalysisImages(images));
        } catch (e) {
            console.error(e);
        }
    }
);

export const getAnalysesWithoutWellData = createAsyncThunk('resource-api/analyses',
    async (args, thunkAPI) => {
        try {
            const analyses = await client.getAnalyses(['protocolArgs']);
            thunkAPI.dispatch(setAnalyses(analyses));
        } catch (e) {
            console.error(e);
        }
    }
);

export const getAnalysis = createAsyncThunk('resource-api/analysis',
    async (id, thunkAPI) => {
        try {
            const analysis = await client.getAnalysis(id);
            thunkAPI.dispatch(setLoadedAnalysis(analysis));
        } catch (e) {
            console.error(e);
        }
    }
);