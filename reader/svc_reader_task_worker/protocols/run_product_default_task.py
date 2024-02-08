import sys
sys.path.insert(0, './common')
sys.path.insert(0, '.')
import apiClient
import log
import lib_hardware_interface.client as hwclient
import time
import os
from reader.utils.apiAuthProvider import APIAuthProvider
from readerCacheHelper import getEncodedCachedValueOrRunFetch


api = apiClient.APIClient(APIAuthProvider())
logger = log.getLogger("reader_task_worker.runProductDefaultTask")
board_transport = os.environ['CONTROLLER_BOARD_REQUEST_TRANSPORT']

async def getReaderSerial(boardTransport):

    async def _fetch():

        board = hwclient.HardwareClient(board_transport)
        while True:
            try:
                readerSerial = board.getSerialNumber()
                break
            except Exception as e:
                logger.warn(f'Error connecting to board, retrying. {e}')
                time.sleep(1)
        return readerSerial

    readerSerial = await getEncodedCachedValueOrRunFetch(
        key = 'readerSerial',
        fetch = _fetch)

    return readerSerial


async def getProductFromShortId(productShortId):
    products = await api.getAll('products', {'shortId': productShortId})
    if not products:
        raise Exception(f"No products found with short id {productShortId}")
    elif len(products) > 1:
        raise Exception(f"More than one product found with short id {productShortId}")
    return products[0]


async def execute(ctx):

    invoke_protocol = ctx['invokeProtocol']
    barcode = ctx['args']['plateBarcode']

    # this is likely not future-proof
    product_short_id = barcode[:2]

    product = await getProductFromShortId(product_short_id)

    # create a scan
    product_description = product['productDescription']['description']
    reader_serial = await getReaderSerial(board_transport)
    scan = {
        'name': f'{barcode} - {product_description}',
        'readerSerialNumber': reader_serial,
        'plateBarcode': barcode,
        'productId': product['_id'],
        'protocol': product['defaultScanProtocol'],
        'protocolArgs': product['defaultScanProtocolArgs'],
        'status': 'NOT_QUEUED'
    }
    scan = await api.create('scans', scan)

    # invoke that scan
    return await invoke_protocol(taskId=scan['_id'])
