import { getHttpHeaders } from "../components/brightestBio/hooks/useAuth";
import { useAuth0 } from "@auth0/auth0-react";

const domain = process.env.REACT_APP_API_URL || "localhost:5000";
/**
 *
 * @param {string} domain
 * @param {"websocket" | "hypertext"} protocol
 */
const getUrlFromDomainWithProtocol = (domain, protocol) => {
  const prefixLessDomain = domain
    .replace("http://", "")
    .replace("https://", "");
  const isLocal = domain.includes("localhost");
  if (isLocal)
    return `${protocol === "websocket" ? "ws" : "http"}://${prefixLessDomain}`;
  else
    return `${
      protocol === "websocket" ? "wss" : "https"
    }://${prefixLessDomain}`;
};
export const httpResourceApiUrl = getUrlFromDomainWithProtocol(
  domain,
  "hypertext"
);
export const wsResourceApiUrl = getUrlFromDomainWithProtocol(
  domain,
  "websocket"
);

const getOmitFilter = (omissions) => {
  return omissions ? `omit=${omissions?.join(",")}` : "";
};

const authedHttpAction = async (accessToken, url, method, cache, body) => {
  const headers = new Headers([
    ["Content-Type", "application/json"],
    ["Authorization", `Bearer ${accessToken}`],
  ]);
  if (headers.length === 0) {
    throw new Error("User is not authenticated.");
  }

  if (!accessToken) console.debug(`No access token provided: ${method} ${url}`);

  const options =
    method === "POST"
      ? { headers, method, cache, body }
      : { headers, method, cache };

  return await fetch(url, options);
};

// product endpoints
export const getProducts = async (omissions, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/products?${getOmitFilter(omissions)}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// scan endpoints
export const postScan = async (scan, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/scans`,
    "POST",
    "no-cache",
    JSON.stringify(scan)
  );
  return await response.json();
};

// get scans
export const getScans = async (omissions, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/scans?${getOmitFilter(omissions)}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// get scan
export const getScan = async (id, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/scans/${id}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// delete scan
export const deleteScan = async (id, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/scans/${id}`,
    "DELETE",
    "no-cache"
  );
  return await response.text();
};

// analyses endpoints
export const postAnalysis = async (analysis, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analyses`,
    "POST",
    "no-cache",
    JSON.stringify(analysis)
  );
  return await response.json();
};

export const getAnalysisAttachments = async (analysisId, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analyses/${analysisId}/attachments`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

export const getAnalysisAttachmentByName = async (
  analysisId,
  filename,
  accessToken
) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analyses/${analysisId}/attachments/${filename}`,
    "GET",
    "no-cache"
  );
  return await response.blob();
};

export const getScanAttachments = async (scanId, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/scans/${scanId}/attachments`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

export const getScanAttachmentByName = async (
  scanId,
  filename,
  accessToken
) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/scans/${scanId}/attachments/${filename}`,
    "GET",
    "no-cache"
  );
  return await response.blob();
};

/**
 * @param { string[] } omissions
 * @returns Array of analysis objects
 *  [{
        "_id": "62e0210b1f09ce377e13125e",
        "createdOn": "2022-08-02T15:10:18.645759",
        "name": "trest",
        "productId": "62bf133245f9c2edcba774bb",
        "productName": "plate 96 well",
        "protocol": "pArrayFluoro",
        "scanId": "62bb3f4cfbc943fa5b82065d",
        "status": "QUEUED",
        "templateId": "62e0210b1f09ce377e13125e",
        "protocolArgs": {}
    }]
 */
export const getAnalyses = async (omissions, accessToken) => {
  // const response = await fetch(`${httpResourceApiUrl}/analyses?omit=${omissions?.join(',')}`);
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analyses?${getOmitFilter(omissions)}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

export const getAnalysis = async (id, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analyses/${id}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// delete analysis
export const deleteAnalysis = async (id, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analyses/${id}`,
    "DELETE",
    "no-cache"
  );
  return await response.text();
};

// analysis template endpoints
export const postAnalysisTemplate = async (analysisTemplate, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analysisTemplates`,
    "POST",
    "no-cache",
    JSON.stringify(analysisTemplate)
  );
  return await response.json();
};

export const getAnalysisTemplates = async (omissions, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analysisTemplates?${getOmitFilter(omissions)}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

export const getAnalysisTemplate = async (id, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analysisTemplates/${id}`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

export const getDefaultPlateMaps = async (accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/defaultPlateMaps`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// delete analysis template
export const deleteAnalysisTemplate = async (id, accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/analysisTemplates/${id}`,
    "DELETE",
    "no-cache"
  );
  return await response.text();
};

// reader endpoints
export const getReaders = async (accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/readers`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// featureFlagSets endpoints
/**
 *
 * @returns {Promise<[{
 * _id: string,
 * createdOn: string,
 * features: [{ feature: string, enabled: boolean }],
 * }]>}
 */
export const getFeatureFlagSets = async (accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/featureFlagSets`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// plates
export const getPlates = async (accessToken) => {
  const response = await authedHttpAction(
    accessToken,
    `${httpResourceApiUrl}/plates`,
    "GET",
    "no-cache"
  );
  return await response.json();
};

// users

export const createUser = async (newUser, accessToken) => {
  const response = await authedHttpAction(
    `https://754hv5bsvdc3drn3dwdjydukhm0irnls.lambda-url.us-east-2.on.aws?email=${newUser.email}&organization=${newUser.organization}&group=${newUser.group}&username=${newUser.username}&&name=${newUser.name}`,
    "POST",
    "no-cache",
    JSON.stringify({})
  );
  return await response.text();
};
