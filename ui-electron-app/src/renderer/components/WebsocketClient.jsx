import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { w3cwebsocket } from "websocket";
import { setLastAnalysisUpdate } from '../features/analysis/analysisSlice';
import { setLastCalibrateUpdate, setLastScanUpdate } from '../features/scan/scanSlice';

const WebsocketClient = (props) => {
    const dispatch = useDispatch();
    const onScanMessage = (message) => {
        try {
            const scanUpdate = JSON.parse(message?.data)?.fullDocument;
            if (scanUpdate?.protocol === 'calibrate') {
                dispatch(setLastCalibrateUpdate(scanUpdate));
            } else {
                dispatch(setLastScanUpdate(scanUpdate));
            }
        } catch (error) {
            console.log('could not store message in redux');
            console.log(error);
        }
    }
    const onAnalysisMessage = (message) => {
        try {
            const analysisUpdate = JSON.parse(message?.data)?.fullDocument;
            console.log('received analysis message', analysisUpdate);
            dispatch(setLastAnalysisUpdate(analysisUpdate));

        } catch (error) {
            console.log('could not store message in redux');
            console.log(error);
        }
    }
    const createWebSocket = (resource, onMessage) => {
        const client = new w3cwebsocket(`ws://localhost:5000/subscribe?match={"$and":[{"ns.coll":"${resource}"}]}`);
        client.onopen = () => {
            console.log(`${resource} connection opened`);
        }
        client.onmessage = onMessage;
        client.onclose = (args) => {
            console.log(`closing ${resource} connection`, args);
        }
        client.onerror = (args) => {
            console.log('ws error', args);
        }
    }

    useEffect(() => {
        createWebSocket('scans', onScanMessage);
        createWebSocket('analyses', onAnalysisMessage);
    }, []);

    return (<></>);
}

export default WebsocketClient