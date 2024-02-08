import client
import json

with client.taskQueue(1) as q:
    obj = { "a": 1 }
    q.publish(json.dumps(obj))
