# new comment, new build

import os
import time
import json
import flask
from flask_cors import CORS
import simple_websocket
import controllerGenerator as generate
import mongoClient
import sys
sys.path.insert(0, '/phoenix/common')
import log
import glob

logger = log.getLogger("resource-api.src.app")
# tf cloud defines 'environment' as a tf build variable (i.e. dev, test, prod)
environment = os.environ.get('ENVIRONMENT', 'localhost')


app = flask.Flask(__name__)


# per the docs, origins must be a list, string, or regex
# https://flask-cors.corydolphin.com/en/latest/api.html#extension
corsAllowedOrigins = "http://" + environment + ":8081" if environment == "localhost" else ["https://" + environment + "-app.brightestbio.com", "https://app." + environment + ".brightestbio.com"]
cors = CORS(app, resources={r"/*": {"origins": corsAllowedOrigins}})

@app.after_request
def log_request_info(response):
    logger.info(f'{response.status_code} {flask.request.method} {flask.request.url}')
    return response

@app.route('/')
def status():
    return "<h1>We're up!!!</h1>"

routes = []
logger.info(f'cwd:{os.getcwd()}')
for filename in glob.iglob(f"./json_routes/*"):
    with open(filename) as f:
        routes.append(json.load(f))

for route in routes:

    app.route(
        f'/{route["pluralEntity"]}',
        methods=['GET'],
        endpoint=f'getAll{route["singularEntity"]}'
    )(generate.getAll(route["pluralEntity"]))

    app.route(
        f'/{route["pluralEntity"]}',
        methods=['POST'],
        endpoint=f'create{route["singularEntity"]}'
    )(generate.create(
        route["pluralEntity"],
        modifiers=[eval(x) for x in route["onCreate"]] if route.get("onCreate",None) else None,
        schema=route["jsonSchema"],
        allowIdOnCreate=route.get("allowIdOnCreate", False)))

    app.route(
        f'/{route["pluralEntity"]}/<docId>',
        methods=['GET'],
        endpoint=f'get{route["singularEntity"]}'
    )(generate.get(route["pluralEntity"]))

    app.route(
        f'/{route["pluralEntity"]}/<docId>',
        methods=['PUT'],
        endpoint=f'update{route["singularEntity"]}'
    )(generate.update(
        route["pluralEntity"],
        schema=route["jsonSchema"]))

    app.route(
        f'/{route["pluralEntity"]}/<docId>',
        methods=['DELETE'],
        endpoint=f'delete{route["singularEntity"]}'
    )(generate.delete(
        route["pluralEntity"], 
        f'{route["singularEntity"]}Attachments' if route.get("hasAttachments", None) else None))

    if route["hasHeartbeat"]:
        app.route(
            f'/{route["pluralEntity"]}/<cid>/heartbeat', 
            methods=['POST'],
            endpoint=f'heartbeat{route["singularEntity"]}'
        )(generate.heartbeat(route["pluralEntity"]))


    if route.get("hasAttachments", None):

        app.route(f'/{route["pluralEntity"]}/<docId>/attachments', 
            methods=['GET'], 
            endpoint=f'getAll{route["singularEntity"]}Attachments'
        )(generate.getAllAttachments(f'{route["singularEntity"]}Attachments'))

        app.route(f'/{route["pluralEntity"]}/<docId>/attachments/<fileName>', 
            methods=['POST'], 
            endpoint=f'create{route["singularEntity"]}Attachment'
        )(generate.createAttachment(f'{route["singularEntity"]}Attachments'))

        app.route(f'/{route["pluralEntity"]}/<docId>/attachments/<fileName>', 
            methods=['DELETE'], 
            endpoint=f'delete{route["singularEntity"]}Attachment'
        )(generate.deleteAttachment(f'{route["singularEntity"]}Attachments'))

        app.route(f'/{route["pluralEntity"]}/<docId>/attachments/<fileName>', 
            methods=['GET'], 
            endpoint=f'get{route["singularEntity"]}Attachment'
        )(generate.getAttachment(f'{route["singularEntity"]}Attachments'))


@app.route('/subscribe', websocket=True)
def subscribe():
    ws = simple_websocket.Server(flask.request.environ)
    try:
        match = flask.request.args.get('match', "{}")
        match = json.loads(match)
        logger.info('match filter is '+str(match))
        for change in mongoClient.subscribeToChanges(match):
            ws.send(change)
    # except simple_websocket.ConnectionClosed:
        # pass
    except Exception as e:
        logger.error(f'Error occured in subscribe: {e}')
        ws.send(str(e))
    finally:
        ws.close()
    return ''



if __name__ == "__main__":

    app.run(debug=True, host='0.0.0.0', port=80)
