import sys
sys.path.insert(0, '/phoenix/common')
import bson.objectid
import datetime
import flask
import functools
import jsonschema
import log
import mongoClient
import os
from auth_validator import require_auth

logger = log.getLogger("resource-api.src.controllerGenerator")


def create(collectionName, **kwargs):

    @require_auth(f"write:{collectionName}")
    def _controller():

        try:

            body = flask.request.json
            # allows calling code to modify incoming payload
            mods = kwargs.get('modifiers')
            if mods:
                body = functools.reduce(
                    lambda acc, item: item(acc),
                    mods,
                    body)
            
            # add a createdOn field
            dateStr = datetime.datetime.utcnow().isoformat()
            body = {**body, "createdOn": dateStr, "lastModified": dateStr}

            if body.get('_id', None): 
                if not kwargs.get('allowIdOnCreate', None):
                    msg = "Cannot create document with an _id field provided. Please omit this field and try again or update an existing document using the `PUT` verb."
                    logger.error(msg)
                    return msg, 400
                else:
                    body['_id'] = str(bson.objectid.ObjectId(body['_id']))
                    logger.info(f'parsed body id into :{body["_id"]}')
            
            try:
                jsonschema.validate(instance=body, schema=kwargs["schema"])
            except jsonschema.exceptions.ValidationError as err:
                logger.error(str(err))
                return str(err), 400

            res = mongoClient.createDocument(
                collectionName,
                body)

            return res, 201
        
        except:
            logger.exception('boom!')
            return 'Server Error', 500

    return _controller


def get(collectionName):

    @require_auth(f"read:{collectionName}")
    def _controller(docId):

        try:

            try:
                bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            res = mongoClient.getDocument(collectionName, docId)
            if not res:
                return 'Not found', 404
            return res, 200
        except:
            logger.exception('boom.')
            return 'Server Error', 500

    return _controller


def getAll(collectionName, **kwargs):

    @require_auth(f"read:{collectionName}")
    def _controller():

        try:
            args = flask.request.args.to_dict()
            omitFields = args.pop('omit', "").split(",")
            skip = int(args.pop('skip', 0))
            limit = int(args.pop('limit', 0))
            totalCount = bool(args.pop('totalCount', False))

            filterObjs = {
                    ### Does this work? please test!!!!!!
                x:{"$eq":args.get(x) if x != '_id' 
                    else bson.objectid.ObjectId(args.get(x))} 
                for x in args 
            }

            if totalCount: # return a count
                res = mongoClient.countDocuments(
                    collectionName, 
                    filterObjs)
                logger.info(f'doc count is :{res}')

            else: # return a collection
                res = mongoClient.getAllDocuments(
                    collectionName, 
                    filterObjs,
                    skip,
                    limit)

                # remove 'omitFields' from results
                for field in omitFields:
                    for item in res:
                        item.pop(field, None)

            return flask.jsonify(res), 200

        except:
            logger.exception(f'Failed getAll{collectionName}()')
            return 'Server Error', 500

    return _controller


def update(collectionName, **kwargs):

    @require_auth(f"write:{collectionName}")
    def _controller(docId):

        try:

            try:
                bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            body = flask.request.json

            preupdate = mongoClient.getDocument(collectionName, docId)
            postupdate = {**preupdate, **body}

            try:
                jsonschema.validate(instance=postupdate, schema=kwargs["schema"])
            except jsonschema.exceptions.ValidationError as err:
                logger.error(str(err))
                return str(err), 400

            res = mongoClient.updateDocument(
                collectionName,
                docId,
                body)

            if res:
                return res, 200
            else:
                return 'Not found', 404

        except Exception as e:
            logger.exception(f'boom:{e}')
            return 'Server Error', 500

    return _controller


def delete(collectionName, attachmentCollectionName=None):

    @require_auth(f"write:{collectionName}")
    def _controller(docId):

        try:

            try:
                bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            found = mongoClient.getDocument(collectionName, docId)
            if not found:
                return 'Not found', 404

            res = mongoClient.deleteDocument(collectionName, docId)

            if attachmentCollectionName:
                atts = mongoClient.getAllAttachments(
                    attachmentCollectionName,
                    docId)
                fnames = [f['filename'] for f in atts]
                for name in fnames:
                    mongoClient.deleteAttachment(
                        attachmentCollectionName,
                        docId, 
                        name)

            if res.deleted_count != 1:
                return 'Delete failed', 500
            else:
                return 'Deleted', 200
        except:
            logger.exception('boom.')
            return 'Server Error', 500

    return _controller


def subscribe():

    @require_auth(f"read:{collectionName}")
    def _controller():

        mongoClient.subscribeToChanges()

    return _controller


def heartbeat(collectionName):

    @require_auth(f"write:{collectionName}")
    def _controller(cid=None):

        try:
            try:
                cid = bson.objectid.ObjectId(cid)
            except:
                return 'Id not valid', 400 

            res = mongoClient.heartbeat(
                collectionName,
                cid)
            if res:
                res = {**res, '_id': str(res['_id'])}
                return res, 201
            else:
                return 'Not found', 404
        except:
            logger.exception('boom.')
            return 'Server Error', 500

    return _controller


######################
#  Attachments stuff #
######################

attachmentsDriver = os.environ['ATTACHMENTS_DRIVER']
logger.info(f'Loading attachments backend {attachmentsDriver}.')

if attachmentsDriver == 'mongo':
    import attachmentsControllerGeneratorMongo as attachmentsControllerGenerator
elif attachmentsDriver == 's3':
    import attachmentsControllerGeneratorS3 as attachmentsControllerGenerator
else:
    raise Exception("Attachments driver not configured.")

createAttachment = attachmentsControllerGenerator.createAttachment
getAttachment = attachmentsControllerGenerator.getAttachment
getAllAttachments = attachmentsControllerGenerator.getAllAttachments
deleteAttachment = attachmentsControllerGenerator.deleteAttachment
