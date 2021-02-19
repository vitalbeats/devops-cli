""" General AWS functions, secrets etc """
import boto3
import json
from .utils import eprint


def get_secret_value(args):
    """ Gets a secret value as JSON """
    if len(args) < 1:
        eprint('devops-cli aws get-secret-value [secret path] <secret path ...>')
        return 1
    client = boto3.client('secretsmanager')
    for secret_path in args:
        secret = client.get_secret_value(SecretId=secret_path)
        print(secret['SecretString'])
    return 0


def get_secret_as_vars(args):
    """ Gets a secret value as variables"""
    if len(args) < 1:
        eprint('devops-cli aws get-secret-as-vars [secret path] <secret path ...>')
        return 1
    client = boto3.client('secretsmanager')
    output = []
    for secret_path in args:
        secret = client.get_secret_value(SecretId=secret_path)
        [output.append(f"{k}={v}") for k, v in json.loads(secret['SecretString']).items()]
    print(' '.join(output))
    return 0


def get_secret_as_env(args):
    """ Gets a secret value as export statements"""
    if len(args) < 1:
        eprint('devops-cli aws get-secret-as-env [secret path] <secret path ...>')
        return 1
    client = boto3.client('secretsmanager')
    for secret_path in args:
        secret = client.get_secret_value(SecretId=secret_path)
        [print(f"export {k}={v}") for k, v in json.loads(secret['SecretString']).items()]
    return 0
