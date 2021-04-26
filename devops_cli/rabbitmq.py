""" RabbitMQ cluster manipulation functions """
from os import name
import boto3
import json
import pika
import time
from .k8s import k8s_port_forward
from .utils import eprint


def replay(args):
    """ Replays messages, effectively retrying anything on the graveyard queue """
    if len(args) < 2:
        eprint('devops-cli rabbitmq replay [cluster path] [graveyard queue name]')
        return 1
    _, queue = args
    cluster_name, namespace_name, service_name, login = __get_queue_info(args)
    local_port, tunnel = k8s_port_forward(cluster_name, namespace_name, service_name, 5672)
    time.sleep(5)
    params = pika.ConnectionParameters('localhost', local_port, '/', login)
    connection = pika.BlockingConnection(params)
    graveyard = connection.channel()
    graveyard.queue_declare(queue=queue, passive=True)
    output = connection.channel()
    exchange = queue[:queue.index('.')]
    out_queue = queue[:-10]
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
    tunnel.kill()
    return 0


def purge(args):
    """ Purges all message from a queue """
    if len(args) < 2:
        eprint('devops-cli rabbitmq purge [cluster path] [queue name]')
        return 1
    _, queue = args
    cluster_name, namespace_name, service_name, login = __get_queue_info(args)
    local_port, tunnel = k8s_port_forward(cluster_name, namespace_name, service_name, 5672)
    time.sleep(5)
    params = pika.ConnectionParameters('localhost', local_port, '/', login)
    connection = pika.BlockingConnection(params)
    queue_con = connection.channel()
    queue_con.queue_declare(queue=queue, passive=True)
    queue_con.queue_purge(queue=queue)
    connection.close()
    tunnel.kill()
    return 0


def __get_queue_info(args):
    """ Gets info we need to operate a queue """
    cluster, _ = args
    cluster_name, namespace_name, service_name = cluster.split('/')
    secret = boto3.client('secretsmanager').get_secret_value(SecretId=f"{cluster}-password")
    credentials = json.loads(secret['SecretString'])
    login = pika.PlainCredentials(credentials['RABBITMQ_DEFAULT_USER'],
                                  credentials['RABBITMQ_DEFAULT_PASS'])
    return cluster_name, namespace_name, service_name, login
