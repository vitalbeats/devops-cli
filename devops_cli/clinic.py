""" Allows direct manipulation of clinics themselves """
import base64
import boto3
import json
import psycopg2
import random
import string
import time
import uuid
from .k8s import k8s_port_forward
from .utils import eprint


def create_clinician(args):
    """ Creates a clinician in the clinic """
    if len(args) < 3:
        eprint('devops-cli clinic create-clinician [cluster path] [username] [name]')
        return 1
    _, username, name = args
    name = name.replace('_', ' ')
    cluster_name, namespace_name, iris_dsn, panacea_dsn = __get_clinic_info(args)
    local_port, tunnel = k8s_port_forward(cluster_name, namespace_name, 'postgres', 5432)
    time.sleep(5)
    id = str(uuid.uuid4())
    password = __random_string()
    salt = __random_string()
    panacea = psycopg2.connect(dsn=panacea_dsn, host='localhost', port=local_port)
    iris = psycopg2.connect(dsn=iris_dsn, host='localhost', port=local_port)
    iris_cur = iris.cursor()
    iris_cur.execute('INSERT INTO users VALUES (%s, %s, %s, %s, NOW(), NOW(), \'session_cookie\', NULL)', (id, username, password, salt))
    iris.commit()
    iris_cur.close()
    iris.close()
    panacea_cur = panacea.cursor()
    panacea_cur.execute('INSERT INTO clinicians SELECT %s, NOW(), NOW(), %s, %s, c.id FROM clinics c', (name, id, username))
    panacea.commit()
    panacea_cur.close()
    panacea.close()
    tunnel.kill()
    print(f"Created user {username} called {name} in {cluster_name}/{namespace_name}")
    return 0


def __get_clinic_info(args):
    """ Gets clinic information """
    cluster, _, _ = args
    cluster_name, namespace_name = cluster.split('/')
    iris_cred = boto3.client('secretsmanager').get_secret_value(SecretId=f"{cluster}/postgres-iris")
    iris = json.loads(iris_cred['SecretString'])
    iris_dsn = f"dbname={iris['POSTGRESQL_DATABASE']} user={iris['POSTGRESQL_USER']} password={iris['POSTGRESQL_PASSWORD']}"
    panacea_cred = boto3.client('secretsmanager').get_secret_value(SecretId=f"{cluster}/postgres-panacea")
    panacea = json.loads(panacea_cred['SecretString'])
    panacea_dsn = f"dbname={panacea['POSTGRESQL_DATABASE']} user={panacea['POSTGRESQL_USER']} password={panacea['POSTGRESQL_PASSWORD']}"
    return cluster_name, namespace_name, iris_dsn, panacea_dsn


def __random_string():
    """ Gets a random string, then encodes it """
    letters = string.ascii_letters
    passwd = ''.join(random.choice(letters) for i in range(16))
    return base64.b64encode(str.encode(passwd))
