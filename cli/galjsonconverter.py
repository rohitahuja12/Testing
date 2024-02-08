import json
    
top_left_spot_to_center_um = 1500

exposures = [ 2500 ]
units = 'microns'
productDescription = {
    "description": "Inflammatory Marker Kit, V3"
}
productId = "V3IK051923"
productName = "V3_Inflammatory_Kit_12P_051923"
productSchemaVersion = 1
spotDiameterUm = 200
spotDistanceUm = 500
initialConcentrationUnits = "pg/ml",
recommendedInitialConcentrations = {
    "IFN-gamma": 2000,
    "IL-10": 600,
    "IL-13": 600,
    "IL-1alpha": 200,
    "IL-1beta": 2000,
    "IL-2": 600,
    "IL-4": 30,
    "IL-5": 600,
    "IL-6": 200,
    "IL-8": 600,
    "MCP-1": 2000,
    "TNF-alpha": 2000
}
recommendedStandardDilutionFactor = 3



async def handle(args):

    galJsonPath = args["<galJsonPath>"]
    # outPath = args["<outputFilePath>"]

    with open(galJsonPath, 'r') as f:
        gal = json.load(f)

    features = {
            name[0]+name[1:].zfill(2): {
            "features": {
                "microArray": { 
                    "$ref": "#/relativeFeatures/microArray" 
                }
            },
            "x": int(details['topLeftX']) + top_left_spot_to_center_um,
            "y": int(details['topLeftY']) + top_left_spot_to_center_um
        } 
        for name, details in gal['blocks'].items()
    }   

    microArrayFeatures = {
        f"{spot['name']}_{spot['row']}_{spot['col']}": {
            "attrs": {
                "analyte": spot['name'],
                "col": spot['col'],
                "row": spot['row']
            },
            "x": (int(spot['col'])-1) * spotDistanceUm,
            "y": (int(spot['row'])-1) * spotDistanceUm
        }
        for spot in gal['blockDescription']['spots']
    }

    product = {
        "productDescription": productDescription,
        "productName": productName,
        "productSchemaVersion": productSchemaVersion,
        "spotDiameterUm": spotDiameterUm,
        "spotDistanceUm": spotDistanceUm,
        "initialConcentrationUnits": initialConcentrationUnits,
        "exposures": exposures,
        "recommendedInitialConcentrations": recommendedInitialConcentrations,
        "recommendedStandardDilutionFactor": recommendedStandardDilutionFactor,
        "features": features,
        "relativeFeatures": {
            "microArray": {
                "features": microArrayFeatures,
                "x": -1500,
                "y": -1500
            }
        }  
    }
    
    print(json.dumps(product, indent=4))

