""" MinIO cluster manipulation functions """
import boto3
import json
import minio
import time
from .k8s import k8s_port_forward
from .utils import eprint


def get_transmission(args):
    """ Connects to the specified MinIO cluster, and download the given transmission + PDF """
    if len(args) < 2:
        eprint('devops-cli minio get-transmission [cluster path] [transmission id] <extension>')
        return 1
    cluster, id, extension = args[0], args[1], args[2] if len(args) > 2 else 'xml'
    cluster_name, namespace_name, service_name, login = __get_cluster_info(cluster)
    local_port, tunnel = k8s_port_forward(cluster_name, namespace_name, service_name, 9000)
    time.sleep(5)
    client = minio.Minio(f"localhost:{local_port}",
                         secure=False,
                         access_key=login['username'],
                         secret_key=login['password'])                    
    if not client.bucket_exists('transmissions'):
        eprint(f"transmissions bucket does not exist in {cluster}")
        return 2
    client.fget_object('transmissions', f"{namespace_name}/{id}", f"{id}.{extension}")
    client.fget_object('transmissions', f"{namespace_name}/{id}.pdf", f"{id}.pdf")
    return 0


def __get_cluster_info(cluster):
    """ Gets info we need to operate MinIO """
    cluster_name, namespace_name, service_name = cluster.split('/')
    secret = boto3.client('secretsmanager').get_secret_value(SecretId=f"{cluster}")
    credentials = json.loads(secret['SecretString'])
    login = {'username': credentials['MINIO_ACCESS_KEY'],
             'password': credentials['MINIO_SECRET_KEY']}
    return cluster_name, namespace_name, service_name, login
