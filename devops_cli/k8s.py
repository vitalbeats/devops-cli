""" Kubernetes specific functions """
from kubernetes import config
from kubernetes.client.api import core_v1_api
from subprocess import Popen, DEVNULL
import socket


def k8s_port_forward(cluster_name, ns, svc, port):
    """ Creates a port forward with a dynamic local port """
    g = (x['name'] for x in config.list_kube_config_contexts()[0] if cluster_name in x['name'])
    ctx = next(g)
    config.load_kube_config(context=ctx)
    api = core_v1_api.CoreV1Api()
    endpoint = api.read_namespaced_endpoints(svc, ns).subsets[0].addresses[0]
    pod_name = endpoint.target_ref.name
    local_port = __free_port()
    cmd = f"kubectl port-forward --context={ctx} -n {ns} pod/{pod_name} {local_port}:{port}"
    proc = Popen(cmd.split(' '), stdout=DEVNULL, stderr=DEVNULL, text=True)
    return local_port, proc


def __free_port():
    """
    Determines a free port using sockets.
    """
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind(('0.0.0.0', 0))
    free_socket.listen(5)
    port = free_socket.getsockname()[1]
    free_socket.close()
    return port
