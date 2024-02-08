import bson
import boto3
import flask
import log
import os
from werkzeug.wsgi import FileWrapper
from auth_validator import require_auth

logger = log.getLogger("resource-api.src.attachmentsControllerGeneratorS3")

s3AttachmentBucket = os.environ['ATTACHMENTS_BUCKET']
s3 = boto3.client('s3')


def generateAttachmentPrefix(collectionName,docId):
    return f"{collectionName}/{docId}/"


def createAttachment(collectionName):

    @require_auth(f"write:{collectionName}")
    def _controller(docId, fileName):

        try:
            try:
                docIdBson = bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            data = flask.request.get_data()

            s3prefix = generateAttachmentPrefix(collectionName,docId)
            s3key = s3prefix+fileName
            res = s3.put_object(
                Bucket=s3AttachmentBucket,
                Key=s3key,
                Body=data
            )

            if not res:
                return "Not found", 404
            return "Attachment Created", 201

        except:
            logger.exception('boom.')
            return 'Server Error', 500

    return _controller


def getAttachment(collectionName):

    @require_auth(f"read:{collectionName}")
    def _controller(docId, fileName):

        try:
            try:
                docIdBson = bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            s3prefix = generateAttachmentPrefix(collectionName,docId)
            s3key = s3prefix+fileName
            res = s3.get_object(
                Bucket=s3AttachmentBucket,
                Key=s3key
            )

            w = FileWrapper(res['Body'])
            return flask.Response(w, mimetype="application/octet-stream", direct_passthrough=True)

        except Exception as e:
            logger.exception(f'Exception in getAttachment. {e}')
            return 'Server Error', 500

    return _controller


def getAllAttachments(collectionName):

    @require_auth(f"read:{collectionName}")
    def _controller(docId):

        try:
            try:
                docIdBson = bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            prefix = generateAttachmentPrefix(
                collectionName,
                docId
            )

            res = s3.list_objects_v2(
                Bucket=s3AttachmentBucket,
                Prefix=prefix
            )
            if res.get('Contents', False):
                out = [
                    {
                        'filename': r['Key'].replace(prefix, ""),
                        'size':r['Size']
                    }
                    for r in res['Contents']
                ]
            else:
                out = []

            return flask.jsonify(out), 200

        except:
            logger.exception('boom.')
            return 'Server Error', 500

    return _controller


def deleteAttachment(collectionName):

    @require_auth(f"write:{collectionName}")
    def _controller(docId, fileName):

        try:
            try:
                docIdBson = bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            s3prefix = generateAttachmentPrefix(collectionName,docId)
            s3key = s3prefix+fileName
            res = s3.delete_object(
                Bucket=s3AttachmentBucket,
                Key=s3key
            )
            return "Attachment deleted", 200

        except:
            logger.exception('boom.')
            return 'Server Error', 500


    return _controller
