import json
import os
import requests
import log
import websockets
import asyncio
import threading
import queue
import urllib.parse
from contextlib import asynccontextmanager
from aiostream import stream

logger = log.getLogger('common.dbclient')

def isLocal(host):
    return ('resource-api' in host) or ('localhost' in host)

apiurl = None
def _getAPIUrl():
    global apiurl
    if not apiurl:
        apihost = os.environ['API_URL']
        protocol = 'http' if isLocal(apihost) else 'https'
        apiurl = f"{protocol}://{apihost}"
        
    return apiurl

def _setAPIUrl(url):
    global apiurl
    apiurl = url

async def pingApi():
    url = _getAPIUrl()
    res = requests.get(url)
    if (res.status_code == 200):
        return True
    else:
        return False

async def create(collection, item, bearerToken=None):
    url = _getAPIUrl()+'/'+collection
    res = requests.post(url, 
        headers={'Content-Type': 'application/json',
                 'Authorization': f'Bearer {bearerToken}'},
        data=json.dumps(item))
    if (res.status_code == 201):
        return res.json()
    else:
        raise Exception('Unable to create item in collection ' +
            collection + ' at url: ' + url + ' with error code ' + 
            str(res.status_code) + ' and message ' + res.text)

async def get(collection, docId, bearerToken=None):
    url = _getAPIUrl()+'/'+collection+'/'+docId
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.get(url, headers=headers)
    if (res.status_code == 200):
        body = res.json()
        return body
    else:
        raise Exception('Unable to retrieve item '+docId+' in collection '+ collection +
            ' with error code ' + str(res.status_code) + ' and message ' + res.text)

async def getAll(collection, filters, bearerToken=None):
    fltrs = [k+'='+str(v) for k,v in filters.items()]
    fltrStr = '&'.join(fltrs)
    url = _getAPIUrl()+'/'+collection+'?'+fltrStr
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.get(url, headers=headers)
    if (res.status_code == 200):
        body = res.json()
        return body
    else:
        raise Exception('Unable to retrieve reader by readerName with error code ' + str(res.status_code) +
            ' and message ' + res.text)
        
async def update(collection, item, bearerToken=None):
    url = _getAPIUrl()+'/'+collection+'/'+item['_id']
    headers = {
        'Authorization': f'Bearer {bearerToken}',
        'Content-Type': 'application/json'
    }
    res = requests.put(url,
        headers=headers, 
        data=json.dumps(item))
    if (res.status_code == 200):
        item = res.json()
        return item
    else:
        raise Exception('Unable to update item in collection '+collection+
            ' with error code ' + str(res.status_code) +
            ' and message ' + res.text +
            ' at url ' + url)

async def delete(collection, docId, bearerToken=None):
    url = _getAPIUrl()+'/'+collection+'/'+docId
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.delete(url, headers=headers)
    if res.status_code == 200:
        return docId
    else:
        raise Exception('Unable to delete item '+docId+' in collection '+collection+
            ' with error code ' + str(res.status_code) +
            ' and message ' + res.text)

# createAttachment('xs', open(attachmentPath, "rb").read(), <name>) to read from file
async def createAttachment(collection, docId, buffer, name, bearerToken=None):
    docurl = _getAPIUrl()+'/'+collection+'/'+docId
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.get(docurl, headers=headers)
    if (res.status_code != 200):
        raise Exception('Unable to retrieve doc for attachment with error code ' + str(res.status_code) +
            ' and message ' + str(res.content) +
            ' at url ' + docurl)
    atturl = docurl+'/attachments/'+name
    logger.info(f'Creating attachment at url: {atturl}')
    updateRes = requests.post(atturl, data=buffer)
    if (updateRes.status_code != 201):
        raise Exception('Failed to update document with attachment' + str(updateRes.status_code) + ' ' + updateRes.text)
    else:
        return res.json()

async def getAttachment(collection, docId, name, bearerToken=None):
    attachmentUrl = _getAPIUrl()+'/'+collection+'/'+docId+'/attachments/'+name
    logger.info(f'attempting to get attachment at url: {attachmentUrl}')
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.get(attachmentUrl, headers=headers)

    if (res.status_code != 200):
        raise Exception('Failed to get attachment with code ' + 
            str(res.status_code) + ' ' + res.text)
    else:
        return res.content

async def getAllAttachments(collection, docId, bearerToken=None):
    attachmentUrl = _getAPIUrl()+'/'+collection+'/'+docId+'/attachments'
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.get(attachmentUrl, headers=headers)

    if (res.status_code != 200):
        raise Exception('Failed to get attachments with code ' + 
            str(res.status_code) + ' ' + res.text)
    else:
        return res.json()

async def deleteAttachment(collection, docId, name, bearerToken=None):
    attachmentUrl = _getAPIUrl()+'/'+collection+'/'+docId+'/attachments/'+name
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.delete(attachmentUrl, headers=headers)

    if (res.status_code != 200):
        raise Exception('Failed to delete attachment with code ' + 
            str(res.status_code) + ' ' + res.text)
    else:
        return docId

async def heartbeat(collection, docId, bearerToken=None):
    url = _getAPIUrl()+'/'+collection+'/'+docId+'/heartbeat'
    headers = {'Authorization': f'Bearer {bearerToken}'}
    res = requests.post(url, headers=headers)
    if (res.status_code == 201):
        return res.json()
    else:
        raise Exception('Unable to perform heartbeat with error code ' + str(res.status_code) +
            ' and message ' + res.text)

# this is quite low level and exposes a lot of details of the mogodb api
# getAllAndSubscribe is the function you probably want
async def subscribeToChanges(match=None):
    host = os.environ['API_URL']
    protocol = 'ws' if isLocal(host) else 'wss'
    url = f"{protocol}://{host}/subscribe"
    url = f"{url}?match={urllib.parse.quote(json.dumps(match))}" if match else url
    logger.info(f'subscribing to {url}')
    print(f'subscribing to {url}')
    async for websocket in websockets.connect(url):
        try:
            async for message in websocket:
                if message:
                    doc = json.loads(message)
                    yield doc
        except websockets.ConnectionClosed:
            continue


# within the collection, 
# get all items that currently pass filters
# and continuously listen for items that pass filters 
async def getAllAndSubscribe(collectionName, filters={}):

    async def getAllStream():
        for item in await getAll(collectionName, filters):
            yield item

    async def subscribe():
        filterDicts = [{f'fullDocument.{k}':v} for k,v in filters.items()]
        match = {"$and": filterDicts + [{'ns.coll':collectionName}]}
        changes = subscribeToChanges(match)
        async for change in changes:
            if change.get('fullDocument', None):
                fd = change['fullDocument']
                try: 
                    yield {**fd, '_id':fd['_id']['$oid']}
                except Exception as e:
                    logger.error('fd = '+str(fd)+' and  e is:' + str(e))
            else:
                logger.info('Change without document????: '+change)

    combine = stream.merge(getAllStream(), subscribe())

    async with combine.stream() as streamer:
        async for item in streamer:
            yield item
