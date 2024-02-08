import sys
sys.path.insert(0, "./common")
import dbclient

async def handle(args):

    with open(args["<barcodesFilePath>"], 'r') as f:
        barcodes = f.readlines()
        barcodes = [b.replace('\n','') for b in barcodes]

    product_id = args["<productId>"]

    for b in barcodes:
        plate_body = {
            "productId": product_id,
            "barcode": b
        }
        await dbclient.create('plates', plate_body)
