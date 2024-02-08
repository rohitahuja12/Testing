/**
 * @typedef {{
 * productId: string,
 * selectedWells: Array<Object>,
 * name: string,
 * readerSerialNumber: string,
 * protocol: string,
 * protocolArgs: Object,
 * }} Scan
 *
 * @typedef {{
 * productId: string,
 * name: string,
 * readerSerialNumber: string,
 * protocol: 'calibrate',
 * protocolArgs: Object,
 * }} Calibration
 */

export const unused = {}; // dummy export to avoid DCE