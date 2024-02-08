import bson
import flask
import io
import log
import mongoClient
from werkzeug.wsgi import FileWrapper
import gridfs
import os
from auth_validator import require_auth

logger = log.getLogger("resource-api.src.attachmentsControllerGeneratorMongo")


def createAttachment(collectionName):

    @require_auth(f"write:{collectionName}")
    def _controller(docId, fileName):

        try:
            try:
                docIdBson = bson.objectid.ObjectId(docId)
            except:
                return 'Id not valid', 400 

            data = flask.request.get_data()
            res = mongoClient.createAttachment(
                collectionName,
                docId,
                fileName,
                data)

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

            res = mongoClient.getAttachment(collectionName, docId, fileName)
            b = io.BytesIO(res)
            w = FileWrapper(b)
            return flask.Response(w, mimetype="application/octet-stream", direct_passthrough=True)

        except gridfs.errors.NoFile:
            return 'Not found', 404

        except:
            logger.exception('boom.')
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

            out = mongoClient.getAllAttachments(
                collectionName,
                docId)

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

            res = mongoClient.deleteAttachment(
                collectionName,
                docId,
                fileName)

            return "Attachment deleted", 200

        except:
            logger.exception('boom.')
            return 'Server Error', 500


    return _controller
