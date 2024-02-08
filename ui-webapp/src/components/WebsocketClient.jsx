import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { w3cwebsocket } from "websocket";
import { getDefaultReader } from '../actions/readerActions';
import { wsResourceApiUrl } from '../api/client';
import { getAnalysesWithoutWellData } from '../actions/analysisTemplateActions';
import { setLastAnalysisUpdate } from '../features/analysis/analysisSlice';
import { setLastCalibrateUpdate, setLastScanUpdate } from '../features/scan/scanSlice';
import { getScansWithoutWellData } from '../actions/scanActions';
import { useFeatureFlags } from './brightestBio/hooks/useFeatureFlags';
import { isFeatureFlagEnabled } from '../actions/featureFlagActions';

const WebsocketClient = (props) => {
    const dispatch = useDispatch();
    const { featureFlags } = useFeatureFlags();

    const onScanMessage = (message) => {
        try {
            dispatch(getScansWithoutWellData());
        } catch (error) {
            console.error(error);
        }
    }
    const onAnalysisMessage = (message) => {
        try {
            dispatch(getAnalysesWithoutWellData())

        } catch (error) {
            console.error(error);
        }
    }

    const onReaderMessage = (message) => {
        try {
            dispatch(getDefaultReader());
        } catch (error) {
            console.error(error);
        }
    }

    const createWebSocket = (resource, onMessage) => {
        console.debug("Attempting to create websocket for resource: ", resource);
        const client = new w3cwebsocket(`${wsResourceApiUrl}/subscribe?match={"$and":[{"ns.coll":"${resource}"}]}`);
        client.onopen = () => {
            console.debug('resource websocket opened: ', resource);
        }
        client.onmessage = onMessage;
        client.onerror = (args) => {
            console.error('resource websocket error: ', resource, args);
        }
        client.onclose = (args) => {
            console.warn('resource websocket closed:', resource);
            if (resource === 'scans') createWebSocket('scans', onScanMessage);
            if (resource === 'analyses') createWebSocket('analyses', onAnalysisMessage);
            if (resource === 'readers') createWebSocket('readers', onReaderMessage);
        }
    }

    useEffect(() => {
        if (isFeatureFlagEnabled('useWebsockets', featureFlags)) {
            createWebSocket('scans', onScanMessage);
            createWebSocket('analyses', onAnalysisMessage);
            createWebSocket('readers', onReaderMessage);
        }
    }, [createWebSocket, onAnalysisMessage, onReaderMessage, onScanMessage]);

    return (<></>);
}

export default WebsocketClient