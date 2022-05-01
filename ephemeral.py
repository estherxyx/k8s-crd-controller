import kopf
import logging
import os
import kubernetes
import yaml
    

@kopf.on.create('ephemeralvolumeclaims')
def create_fn(spec, name, namespace, logger, **kwargs):

    logging.debug(f"spec: {spec}")
    logging.debug(f"name: {name}")
    logging.debug(f"namespace: {namespace}")


@kopf.on.update('ephemeralvolumeclaims')
def update_fn(spec, name, status, namespace, logger, **kwargs):
    logging.info(f"log from update")
    logging.debug(f"spec: {spec}")
    logging.debug(f"status: {status}")
    logging.debug(f"namespace: {namespace}")

    api = kubernetes.client.CoreV1Api()
    logging.warn(api.list_namespaced_service(namespace))
    

    GROUP = "kopf.dev"
    VERSION = "v1"
    PLURAL = "ephemeralvolumeclaims"


    crd_api = kubernetes.client.CustomObjectsApi()
    tmp = crd_api.list_cluster_custom_object(
        GROUP, VERSION, PLURAL
    )
    logging.warn(tmp)

    size = spec.get('size')
    if not size:
        raise kopf.PermanentError(f"Size must be set. Got {size!r}.")

    path = os.path.join(os.path.dirname(__file__), 'evc-template.yaml')
    tmpl = open(path, 'rt').read()
    copy_name = name+"-copy"
    text = tmpl.format(name=copy_name, size=size)
    data = yaml.safe_load(text)

    try:
        crd_api.delete_namespaced_custom_object(
            GROUP, VERSION, namespace, PLURAL, copy_name, grace_period_seconds=5
        )
    except:
        logging.debug(f"delete failed")


    crd_api.create_namespaced_custom_object(
        GROUP, VERSION, namespace, PLURAL, data
    )


    