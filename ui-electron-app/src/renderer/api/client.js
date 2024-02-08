
const resourceApiUrl = 'http://localhost:5000';

const getOmitFilter = (omissions) => {
    return omissions ? `omit=${omissions?.join(',')}` : '';
}
// #####  #####   ####  #####  #    #  ####  #####  ####  
// #    # #    # #    # #    # #    # #    #   #   #      
// #    # #    # #    # #    # #    # #        #    ####  
// #####  #####  #    # #    # #    # #        #        # 
// #      #    #  ####  #####   ####   ####    #    ####  
export const getProducts = async (omissions) => {
    const response = await fetch(`${resourceApiUrl}/products?${getOmitFilter(omissions)}`);
    return await response.json();
}

//  ####   ####    ##   #    #  ####  
// #      #    #  #  #  ##   # #      
//  ####  #      #    # # #  #  ####  
//      # #      ###### #  # #      # 
//  ####   ####  #    # #    #  ####  
export const postScan = async (scan) => {
    const headers = new Headers([
        ['Content-Type', 'application/json']
    ]);

    const response = await fetch(`${resourceApiUrl}/scans`, {
        method: 'POST',
        cache: 'no-cache',
        headers,
        body: JSON.stringify(scan)
    });
    return await response.json();
}

export const getScans = async (omissions) => {
    const response = await fetch(`${resourceApiUrl}/scans?omit=${omissions?.join(',')}`);
    return await response.json();
}

export const getScan = async (id) => {
    const response = await fetch(`${resourceApiUrl}/scans/${id}`);
    return await response.json();
}

//   ##   #    #   ##   #      #   #  ####  ######  ####  
//  #  #  ##   #  #  #  #       # #  #      #      #      
// #    # # #  # #    # #        #    ####  #####   ####  
// ###### #  # # ###### #        #        # #           # 
// #    # #    # #    # ######   #    ####  ######  ####
export const postAnalysis = async (analysis) => {
    const headers = new Headers([
        ['Content-Type', 'application/json']
    ]);

    const response = await fetch(`${resourceApiUrl}/analyses`, {
        method: 'POST',
        cache: 'no-cache',
        headers,
        body: JSON.stringify(analysis)
    });
    return await response.json();
}

export const getAnalysisAttachments = async (analysisId) => {
    const response = await fetch(`${resourceApiUrl}/analyses/${analysisId}/attachments`);
    // const sampleAttachmentsResponse = [{
    //     "_id": "analysisAttachments62e9b220a5a951791882cc1fheat_map_IFG-y2.jpg",
    //         "filename": "heat_map_IFG-y2.jpg",
    //             "size": 247181
    // }]
    return await response.json();
}

export const getAnalysisAttachmentByName = async (analysisId, filename) => {
    const response = await fetch(`${resourceApiUrl}/analyses/${analysisId}/attachments/${filename}`);
    return await response.blob();
}

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
export const getAnalyses = async (omissions) => {
    const response = await fetch(`${resourceApiUrl}/analyses?omit=${omissions?.join(',')}`);
    return await response.json();
}

export const getAnalysis = async (id) => {
    const response = await fetch(`${resourceApiUrl}/analyses/${id}`);
    return await response.json();
}

// ##### ###### #    # #####  #        ##   ##### ######  ####  
//   #   #      ##  ## #    # #       #  #    #   #      #      
//   #   #####  # ## # #    # #      #    #   #   #####   ####  
//   #   #      #    # #####  #      ######   #   #           # 
//   #   ###### #    # #      ###### #    #   #   ######  ####  
export const postAnalysisTemplate = async (analysisTemplate) => {
    const headers = new Headers([
        ['Content-Type', 'application/json']
    ]);

    const response = await fetch(`${resourceApiUrl}/analysisTemplates`, {
        method: 'POST',
        cache: 'no-cache',
        headers,
        body: JSON.stringify(analysisTemplate)
    });
    return await response.json();
}

export const getAnalysisTemplates = async (omissions) => {
    const response = await fetch(`${resourceApiUrl}/analysisTemplates?omit=${omissions?.join(',')}`);
    return await response.json();
}

export const getAnalysisTemplate = async (id) => {
    const response = await fetch(`${resourceApiUrl}/analysisTemplates/${id}`);
    return await response.json();
}

export const getDefaultPlateMaps = async () => {
    const response = await fetch(`${resourceApiUrl}/defaultPlateMaps`);
    return await response.json();
}

// #####  ######   ##   #####  ###### #####   ####  
// #    # #       #  #  #    # #      #    # #      
// #    # #####  #    # #    # #####  #    #  ####  
// #####  #      ###### #    # #      #####       # 
// #    # ###### #    # #####  ###### #    #  ####  

export const getReaders = async () => {
    const response = await fetch(`${resourceApiUrl}/readers`);
    return await response.json();
}