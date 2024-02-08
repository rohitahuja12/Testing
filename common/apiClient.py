import json
import log
import os
import requests

logger = log.getLogger('common.apiclient')
localtoken = os.environ.get('AUTH_TOKEN', None)

def isLocal(host):
    return ('resource-api' in host) or ('localhost' in host)

class APIClient:

    def __init__(self, authProvider):
        self.apiurl = self._getAPIUrl()
        self.authProvider = authProvider

    def _getAPIUrl(self):
        apihost = os.environ['API_URL']
        protocol = 'http' if isLocal(apihost) else 'https'
        apiurl = f"{protocol}://{apihost}"
        return apiurl

    async def pingApi(self):
        url = self._getAPIUrl()
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.get(url, headers=headers)
        if (res.status_code == 200):
            return True
        else:
            return False

    async def create(self, collection, item):
        url = self.apiurl+'/'+collection
        bearerToken = localtoken or self.authProvider.getToken()
        res = requests.post(
            url, 
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {bearerToken}'
            },
            data=json.dumps(item))
        if (res.status_code == 201):
            return res.json()
        else:
            raise Exception('Unable to create item in collection ' +
                collection + ' at url: ' + url + ' with error code ' + 
                str(res.status_code) + ' and message ' + res.text)

    async def get(self, collection, docId):
        url = self.apiurl+'/'+collection+'/'+docId
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.get(url, headers=headers)
        if (res.status_code == 200):
            body = res.json()
            return body
        else:
            raise Exception('Unable to retrieve item '+docId+' in collection '+ collection +
                ' with error code ' + str(res.status_code) + ' and message ' + res.text)

    async def getAll(self, collection, filters):
        fltrs = [k+'='+str(v) for k,v in filters.items()]
        fltrStr = '&'.join(fltrs)
        url = self.apiurl+'/'+collection+'?'+fltrStr
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.get(url, headers=headers)
        if (res.status_code == 200):
            body = res.json()
            return body
        else:
            raise Exception('Unable to retrieve reader by readerName with error code ' + str(res.status_code) +
                ' and message ' + res.text)
            
    async def update(self, collection, item):
        url = self.apiurl+'/'+collection+'/'+item['_id']
        bearerToken = localtoken or self.authProvider.getToken()
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

    async def delete(self, collection, docId):
        url = self.apiurl+'/'+collection+'/'+docId
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.delete(url, headers=headers)
        if res.status_code == 200:
            return docId
        else:
            raise Exception('Unable to delete item '+docId+' in collection '+collection+
                ' with error code ' + str(res.status_code) +
                ' and message ' + res.text)

    # createAttachment('xs', open(attachmentPath, "rb").read(), <name>) to read from file
    async def createAttachment(self, collection, docId, buffer, name):
        docurl = self.apiurl+'/'+collection+'/'+docId
        bearerToken = localtoken or self.authProvider.getToken()
        res = requests.get(
            docurl, 
            headers={'Authorization': f'Bearer {bearerToken}'})
        if (res.status_code != 200):
            raise Exception('Unable to retrieve doc for attachment with error code ' + str(res.status_code) +
                ' and message ' + str(res.content) +
                ' at url ' + docurl)
        atturl = docurl+'/attachments/'+name
        logger.info(f'Creating attachment at url: {atturl}')
        bearerToken = localtoken or self.authProvider.getToken()
        updateRes = requests.post(
            atturl, 
            headers={'Authorization': f'Bearer {bearerToken}'},
            data=buffer
        )
        if (updateRes.status_code != 201):
            raise Exception('Failed to update document with attachment' + str(updateRes.status_code) + ' ' + updateRes.text)
        else:
            return res.json()

    async def getAttachment(self, collection, docId, name):
        attachmentUrl = self.apiurl+'/'+collection+'/'+docId+'/attachments/'+name
        logger.info(f'attempting to get attachment at url: {attachmentUrl}')
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.get(attachmentUrl, headers=headers)

        if (res.status_code != 200):
            raise Exception('Failed to get attachment with code ' + 
                str(res.status_code) + ' ' + res.text)
        else:
            return res.content

    async def getAllAttachments(self, collection, docId):
        attachmentUrl = self.apiurl+'/'+collection+'/'+docId+'/attachments'
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.get(attachmentUrl, headers=headers)

        if (res.status_code != 200):
            raise Exception('Failed to get attachments with code ' + 
                str(res.status_code) + ' ' + res.text)
        else:
            return res.json()

    async def deleteAttachment(self, collection, docId, name):
        attachmentUrl = self.apiurl+'/'+collection+'/'+docId+'/attachments/'+name
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.delete(attachmentUrl, headers=headers)

        if (res.status_code != 200):
            raise Exception('Failed to delete attachment with code ' + 
                str(res.status_code) + ' ' + res.text)
        else:
            return docId

    async def heartbeat(self, collection, docId):
        url = self.apiurl+'/'+collection+'/'+docId+'/heartbeat'
        bearerToken = localtoken or self.authProvider.getToken()
        headers = {'Authorization': f'Bearer {bearerToken}'}
        res = requests.post(url, headers=headers)
        if (res.status_code == 201):
            return res.json()
        else:
            raise Exception('Unable to perform heartbeat with error code ' + str(res.status_code) +
                ' and message ' + res.text)
