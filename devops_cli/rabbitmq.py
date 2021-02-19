""" RabbitMQ cluster manipulation functions """
import boto3
import json
import pika
from .utils import eprint


def replay(args):
    """ Replays messages, effectively retrying anything on the graveyard queue """
    if len(args) < 2:
        eprint('devops-cli rabbitmq replay [cluster path] [graveyard queue name]')
        return 1
    cluster, queue = args
    exchange = queue[:queue.index('.')]
    out_queue = queue[:-10]
    secret = boto3.client('secretsmanager').get_secret_value(SecretId=f"{cluster}-password")
    credentials = json.loads(secret['SecretString'])
    login = pika.PlainCredentials(credentials['RABBITMQ_DEFAULT_USER'],
                                  credentials['RABBITMQ_DEFAULT_PASS'])
    params = pika.ConnectionParameters('localhost', 5672, '/', login)
    connection = pika.BlockingConnection(params)
    graveyard = connection.channel()
    graveyard.queue_declare(queue=queue, durable=True)
    output = connection.channel()
    while True:
        method_frame, header_frame, body = graveyard.basic_get(queue=queue)
        if method_frame is None or method_frame.NAME == 'Basic.GetEmpty':
            break
        output.basic_publish(exchange,
                             out_queue,
                             body,
                             pika.BasicProperties(content_type='text/plain',
                                                  delivery_mode=2))
        graveyard.basic_ack(delivery_tag=method_frame.delivery_tag)
    connection.close()
    return 0