import { getNonCalibrationScansFromScanList } from './scanActions';

const mockScans = [
    {
        "_id": "631cc7fabf2ade8f964a6f4a",
        "createdOn": "2022-09-10T17:23:06.117689",
        "errors": [
        ],
        "name": "config",
        "productId": "",
        "protocol": "calibrate",
        "protocolArgs": {},
        "readerSerialNumber": "reader456",
        "status": "ERROR"
    }
]

test('Calibration scans are filtered out', () => {
    const nonCalibrationScans = getNonCalibrationScansFromScanList(mockScans);
    expect(nonCalibrationScans.length).toBe(0);
});