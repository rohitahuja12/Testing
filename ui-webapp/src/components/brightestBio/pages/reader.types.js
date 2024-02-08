/**
 * @typedef {{
 * _id: string,
 * cameraCenter: {
 *  x: number,
 *  y: number,
 * },
 * createdOn: string,
 * defaultZ: number,
 * imageMirrorX: boolean,
 * imageMirrorY: boolean,
 * imageRotation: number,
 * lastModified: string,
 * micronsPerMotorStep: {
 * x: number,
 * y: number,
 * z: number,
 * },
 * micronsPerPixel: {
 * x: number,
 * y: number,
 * },
 * objectiveFocalLength: number,
 * objectiveFovDims: {
 * x: number,
 * y: number,
 * },
 * serialNumber: string,
 * status: {
 * boardConnect: string,
 * boardPower: string,
 * door: string,
 * laser: string,
 * lastUpdated: string,
 * taskStatus: string,
 * },
 * totalMagnification: number,
 * tubeLensFocalLength: number,
 * }} Reader
 */

export const unused = {}; // dummy export to avoid DCE