# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
import json
import os
import time
from typing import Optional

import certifi
import yaml
from kubernetes import config
from kubernetes.client import CoreV1Api, ApiException, V1PodList, V1Pod, CustomObjectsApi, ApiClient, Configuration

from lapi.models.identities import ServiceIdentity
from lapi.models.messages import EventMessage
from lapi.models.settings import CommonJobSettings, IdentitySettings
from lapi.models.jobs import JobInstance, Job
from lapi.services.workflow_manager.models.settings import ServiceSettings
from lapi.utils.settings import get_settings_as


class K8sClient:
    """
    This class realizes a singleton like kubernetes client initialization.
    Once initialized, the client can be reused in different places.
    """

    _core_v1_api = None

    @classmethod
    def get(cls) -> CoreV1Api:
        if cls._core_v1_api is None:
            settings = get_settings_as(ServiceSettings)

            """ If explicit config has been set through the settings, then
                it has the highest priority. If not and the runtime is inside
                the cluster, then the specific in-cluster config will be
                initialized. This is using the specific service account. For
                any other cases either a provided config file will be used
                or the default config '~/.kube/config' will be used. """
            if settings.kubernetes.explicit_config is not None:
                config.load_kube_config_from_dict(settings.kubernetes.explicit_config)
            elif os.getenv("KUBERNETES_SERVICE_HOST") and os.getenv("KUBERNETES_SERVICE_PORT"):
                config.load_incluster_config()
            else:
                config.load_kube_config(config_file=settings.kubernetes.config_file)

            """ We need to copy the configuration to alter it. Altering means to
                update SSL certificates, proxies etc. """
            configuration = Configuration.get_default_copy()

            configuration.ssl_ca_cert = settings.kubernetes.cacert_file or certifi.where()
            configuration.verify_ssl = settings.kubernetes.verify_ssl

            if settings.inherit_proxy_settings:
                configuration.proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
                configuration.no_proxy = os.getenv("NO_PROXY") or os.getenv("no_proxy")

            cls._core_v1_api: CoreV1Api = CoreV1Api(api_client=ApiClient(configuration=configuration))

        return cls._core_v1_api


class KubernetesHandler:
    _label_key_part_of = "app.kubernetes.io/part-of"
    _label_key_name = "app.kubernetes.io/name"
    _label_key_instance = "app.kubernetes.io/instance"
    _label_key_component = "app.kubernetes.io/component"
    _label_key_request_id = "lapi.io/request_id"
    _label_key_workflow_id = "lapi.io/workflow_id"
    _label_key_job_name = "lapi.io/job_name"
    _label_key_job_version = "lapi.io/job_version"

    _label_lapi_value = "LAPI"
    _label_job_value = "JOB"

    def __init__(self):
        self._settings: ServiceSettings = get_settings_as(ServiceSettings)

        self._core_v1_api: CoreV1Api = K8sClient.get()

    def get_job_instances(self, request_id: Optional[str] = None,
                          workflow_id: Optional[str] = None) -> list[JobInstance]:
        label_selector = (
            f"{KubernetesHandler._label_key_part_of}={KubernetesHandler._label_lapi_value},"
            f"{KubernetesHandler._label_key_component}={KubernetesHandler._label_job_value}")

        if request_id is not None:
            label_selector += f",{KubernetesHandler._label_key_request_id}={request_id}"
        if workflow_id is not None:
            label_selector += f",{KubernetesHandler._label_key_workflow_id}={workflow_id}"

        pod_list: V1PodList = self._core_v1_api.list_namespaced_pod(
            namespace=self._settings.kubernetes.namespace,
            label_selector=label_selector
        )

        job_instance_list: list[JobInstance] = []

        for pod in pod_list.items:  # type: V1Pod
            job_info = JobInstance(request_id=pod.metadata.labels[KubernetesHandler._label_key_request_id],
                                   workflow_id=pod.metadata.labels[KubernetesHandler._label_key_workflow_id],
                                   job_name=pod.metadata.labels[KubernetesHandler._label_key_job_name],
                                   job_version=pod.metadata.labels[KubernetesHandler._label_key_job_version],
                                   instance_id=pod.metadata.name,
                                   status="Unknown"
                                   if (pod.status is None) or (pod.status.phase is None) else pod.status.phase)
            job_instance_list.append(job_info)

        return job_instance_list

    def get_aad_identity_by_name(self, name: str) -> Optional[ServiceIdentity]:
        """
        This method attempts to retrieve an AzureIdentity
        resource by name and populates a ServiceIdentity database.py.

        :param name: name of the identity
        :return: ServiceIdentity or None, if identity is not existing
        """

        crd_client = CustomObjectsApi(self._core_v1_api.api_client)

        try:
            api_response = crd_client.get_namespaced_custom_object(
                group="aadpodidentity.k8s.io",
                version="v1",
                namespace="aad-pod-identity",
                plural="azureidentities",
                name=name
            )

            return ServiceIdentity(
                client_id=api_response["metadata"]["labels"]["client_id"],
                tenant_id=api_response["metadata"]["labels"]["tenant_id"],
                object_id=api_response["metadata"]["labels"]["object_id"]
            )

        except ApiException as e:
            if 404 == e.status:
                return None
            raise

    def get_aad_identity_binding_by_name(self, name: str) -> Optional[dict]:
        """
        This method attempts to retrieve an AzureIdentityBinding and return as dict.

        :param name: name of the identity binding
        :return: dict or None, if identity binding is not existing
        """

        crd_client = CustomObjectsApi(self._core_v1_api.api_client)

        try:
            return crd_client.get_namespaced_custom_object(
                group="aadpodidentity.k8s.io",
                version="v1",
                namespace="aad-pod-identity",
                plural="azureidentitybindings",
                name=name
            )

        except ApiException as e:
            if 404 == e.status:
                return None
            raise

    def deploy_job_settings(self, event_message: EventMessage, job_instance: JobInstance, job: Job):
        settings: CommonJobSettings = CommonJobSettings(name=job.job_name,
                                                        environment=self._settings.environment,
                                                        service_stack=self._settings.service_stack,
                                                        kafka=self._settings.kafka,
                                                        trigger_event=event_message,
                                                        storages=self._settings.storages)

        if job.identity_name is not None:
            identity = self.get_aad_identity_by_name(job.identity_name)
            settings.identity = IdentitySettings(client_id=identity.client_id, tenant_id=identity.tenant_id)

        self._core_v1_api.create_namespaced_config_map(
            namespace=self._settings.kubernetes.namespace,
            body={
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": job_instance.instance_id,
                    "labels": {
                        KubernetesHandler._label_key_part_of: KubernetesHandler._label_lapi_value,
                        KubernetesHandler._label_key_request_id: event_message.request_id,
                        KubernetesHandler._label_key_workflow_id: event_message.workflow_id,
                        KubernetesHandler._label_key_component: KubernetesHandler._label_job_value,
                        KubernetesHandler._label_key_job_name: job_instance.job_name,
                        KubernetesHandler._label_key_job_version: job_instance.job_version
                    }
                },
                "data": {
                    "settings.yml": yaml.dump(json.loads(settings.model_dump_json()))
                }
            }
        )

        for attempt in range(30):
            try:
                self._core_v1_api.read_namespaced_config_map(name=job_instance.instance_id,
                                                             namespace=self._settings.kubernetes.namespace)

                return
            except ApiException as e:
                if 404 != e.status:
                    raise
            time.sleep(2)

        raise TimeoutError(f"Event config deployment timeout: {event_message}")

    def is_job_settings_deployed(self, job_instance: JobInstance) -> bool:
        try:
            self._core_v1_api.read_namespaced_config_map(name=job_instance.instance_id,
                                                         namespace=self._settings.kubernetes.namespace)
            return True
        except ApiException as e:
            if 404 == e.status:
                return False
            raise

    def delete_job_settings(self, job_instance: JobInstance):
        self._core_v1_api.delete_namespaced_config_map(name=job_instance.instance_id,
                                                       namespace=self._settings.kubernetes.namespace)

    def deploy_job(self, event_message: EventMessage, job_instance: JobInstance, job: Job):
        env = [
            {
                "name": "LAPI_LABEL_REQUEST_ID",
                "value": event_message.request_id
            }
        ]

        volumes = [
            {
                'name': job_instance.instance_id,
                'configMap': {
                    'name': job_instance.instance_id
                }
            }
        ]

        containers = [
            {
                "name": job_instance.instance_id,
                "env": env,
                "image": f"{job.image}:{job_instance.job_version}",
                "imagePullPolicy": "Always",
                "volumeMounts": [
                    {
                        "name": job_instance.instance_id,
                        "mountPath": "/job/settings"
                    }
                ]
            }
        ]

        topology_spread_constraints = [
            {
                'labelSelector': {
                    'matchLabels': {
                        KubernetesHandler._label_key_part_of: "lapi"
                    }
                },
                'maxSkew': 1,
                'topologyKey': 'kubernetes.io/hostname',
                'whenUnsatisfiable': 'ScheduleAnyway'
            }
        ]

        spec = {
            'containers': containers,
            'restartPolicy': 'Never',
            'terminationGracePeriodSeconds': 300,
            'topologySpreadConstraints': topology_spread_constraints,
            "volumes": volumes
        }

        labels = {
            KubernetesHandler._label_key_part_of: KubernetesHandler._label_lapi_value,
            KubernetesHandler._label_key_request_id: event_message.request_id,
            KubernetesHandler._label_key_workflow_id: event_message.workflow_id,
            KubernetesHandler._label_key_component: KubernetesHandler._label_job_value,
            KubernetesHandler._label_key_job_name: job_instance.job_name,
            KubernetesHandler._label_key_job_version: job_instance.job_version
        }

        if job.identity_name is not None:
            labels["aadpodidbinding"] = job.identity_name

        metadata = {
            'labels': labels,
            'name': job_instance.instance_id,
        }

        pod = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': metadata,
            'spec': spec
        }

        self._core_v1_api.create_namespaced_pod(self._settings.kubernetes.namespace, body=pod)

    def is_job_deployed(self, job_instance: JobInstance) -> bool:
        try:
            self._core_v1_api.read_namespaced_pod(name=job_instance.instance_id,
                                                  namespace=self._settings.kubernetes.namespace)
            return True
        except ApiException as e:
            if 404 == e.status:
                return False
            raise

    def delete_job(self, job_instance: JobInstance):
        self._core_v1_api.delete_namespaced_pod(name=job_instance.instance_id,
                                                namespace=self._settings.kubernetes.namespace)

    def stream_log_to_file(self, job_instance: JobInstance, log_file_path: str):
        with open(log_file_path, 'a') as log_file:
            for line in self._core_v1_api.read_namespaced_pod_log(namespace=self._settings.kubernetes.namespace,
                                                                  name=job_instance.instance_id,
                                                                  follow=True,
                                                                  _preload_content=False):
                log_file.write(line.decode('utf-8'))
