import sys
sys.path.insert(0, './common')
import pika
from contextlib import contextmanager
import log
logger = log.getLogger('lib_queue_task_results.client')


class TaskQueue():

    def __init__(self, taskId):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.qname = f"task_{taskId}"
        self.channel.queue_declare(
            queue=self.qname, 
            durable=True)

    def publish(self, msg):
        self.channel.basic_publish(exchange='',
            routing_key=self.qname,
            body=msg)

    def close(self):
        self.connection.close()



@contextmanager
def taskQueue(taskId):

    try:
        t = TaskQueue(taskId)
        yield t

    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Unable to connect to AMQP broker: {e}")

    finally:
        if t:
            t.close()
