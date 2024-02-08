import sys
sys.path.insert(0, '/phoenix/common')
import pymongo
import gridfs
import log
import datetime
import os
from bson.json_util import dumps
from bson.objectid import ObjectId

logger = log.getLogger("resource-api.src.mongoClient")

dbhost = os.environ['DB_HOST']
dbuser = os.environ['DB_USER']
dbpassword = os.environ['DB_PASSWORD']
dbprotocol = os.environ['DB_PROTOCOL']
client = pymongo.MongoClient(
    # f'mongodb://{dbuser}:{dbpassword}@{dbhost}/?retryWrites=true&w=majority', # Cloudy 
    # f'mongodb://{dbuser}:{dbpassword}@{dbhost}/?ssl=true&authSource=admin&replicaSet=Cluster0-shard-0-shard-0', # Cloudy 
    f'{dbprotocol}://{dbuser}:{dbpassword}@{dbhost}', # Cloudy 
    # f'mongodb://root:password@db', 
    )
db = client['reader']

def createDocument(collectionName, data):
    
    collection = db[collectionName]

    doc_id = collection.insert_one(data).inserted_id
    logger.info('creating one with id: '+str(doc_id))
    x = collection.find_one({"_id":doc_id})

    return {**x, '_id':str(x['_id'])}


def getDocument(collectionName, docId):

    collection = db[collectionName]

    filters = {"_id":ObjectId(docId)}
    x = collection.find_one(filters)

    if not x:
        return None
    return {**x, '_id': str(x['_id'])}


def getAllDocuments(collectionName, filters, skip=0, limit=0):

    collection = db[collectionName]

    cs = list(collection.find(filters).skip(skip).limit(limit))
    cs = [{**c, '_id': str(c['_id'])} for c in cs]

    return cs


def countDocuments(collectionName, filters):

    collection = db[collectionName]

    count = collection.count_documents(filters)

    return count



def updateDocument(collectionName, docId, data):

    collection = db[collectionName]

    if data.get('_id', None):
        data.pop('_id')

    res = collection.find_one_and_update(
        {'_id': ObjectId(docId)},
        { "$set": {k:v for k,v in data.items()} },
        return_document=pymongo.ReturnDocument.AFTER
    )
    logger.info(f'update result: {res}')
    if res:
        res = {**res, '_id': str(res['_id'])}
        return res
    else:
        return None


def deleteDocument(collectionName, docId):

    collection = db[collectionName]
    res = collection.delete_one({"_id":ObjectId(docId)})

    return res


def createAttachment(collectionName, docId, fileName, data):

    fs = gridfs.GridFS(db)
    attachmentId = collectionName+docId+fileName

    try:
        f = fs.new_file(_id=attachmentId, filename=fileName)
        f.write(data)
        return True
    except:
        logger.exception('boom in create attachment...')
        return False
    finally:
        f.close()


def getAttachment(collectionName, docId, fileName):

    fs = gridfs.GridFS(db)
    attachmentId = collectionName+docId+fileName

    res = fs.get(attachmentId).read()

    return res


def getAllAttachments(collectionName, docId):

    fs = gridfs.GridFS(db)
    attachmentRangeId = collectionName+str(docId)

    res = fs.find({"_id":{"$regex":attachmentRangeId}})
    out = [{'_id':str(r._id), 'filename':r.name, 'size':r.length} for r in res]

    return out


def deleteAttachment(collectionName, docId, fileName):
    
    fs = gridfs.GridFS(db)
    attachmentId = collectionName+str(docId)+fileName

    res = fs.delete(attachmentId)

    return res


def subscribeToChanges(match):

    with db.watch([{"$match":match}]) as stream:
        for change in stream:
            yield dumps(change)


def heartbeat(collectionName, docId):

    collection = db[collectionName]

    nowstamp = datetime.datetime.now().isoformat()
    res = collection.find_one_and_update(
        {'_id':ObjectId(docId)},
        {'$set':{'lastHeartbeat':nowstamp}},
        return_document = pymongo.ReturnDocument.AFTER)

    res = {**res, '_id': str(res['_id'])}
    return res
