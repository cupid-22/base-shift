# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
import sys

import json
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional
from threading import Thread, Lock

from azure.identity import ClientSecretCredential
from kubernetes.client import CoreV1Api

from lapi.models.jobs import Job
from lapi.services.workflow_manager.handlers.k8s import K8sClient
from lapi.services.workflow_manager.handlers.registry import RegistryClientWrapper
from lapi.services.workflow_manager.models.settings import ServiceSettings
from lapi.utils.common import Singleton
from lapi.utils.settings import get_settings_as


class JobService(metaclass=Singleton):
    def __init__(self):
        self._settings = get_settings_as(ServiceSettings)

        self._core_v1_api: CoreV1Api = K8sClient.get()

        self._credential = ClientSecretCredential(
            tenant_id=self._settings.identity.tenant_id,
            client_id=self._settings.identity.client_id,
            client_secret=self._settings.identity.client_secret
        ) if self._settings.identity is not None else None

        self._job_registry: dict[str, Job] = dict()

        self._registry_access_lock = Lock()

        self._shutdown: bool = False

        self._job_registry_update_thread: Thread = Thread(target=self._recurrent_job_registry_update)

        self._last_registry_update_time: Optional[datetime] = None

    async def on_startup(self):
        self._job_registry_update_thread.start()

    async def on_shutdown(self):
        self._shutdown = True
        self._job_registry_update_thread.join()

    def get_all(self, skip: int = 0, limit: int = 10) -> list[Job]:
        with self._registry_access_lock:
            jobs = list(self._job_registry.values())

            return jobs[skip:skip + limit] if skip < len(jobs) else []

    def get_by_name(self, job_name: str) -> Optional[Job]:
        with self._registry_access_lock:
            if job_name not in self._job_registry:
                return None

            return self._job_registry[job_name]

    def is_job_existing(self, name: str, version: str):
        with self._registry_access_lock:
            return (name in self._job_registry) and (version in self._job_registry[name].versions)

    def _refresh_job_update(self) -> None:
        """
        This method attempts to refresh the in-memory job registry by retrieving all available
        repositories in the DTR, retrieving the project config file and updating the registry
        with the combined information.
        """

        try:
            """ If we are just starting up, then we want to lock the entire process to prevent
                request processing until the registry is updated. """
            if 0 == len(self._job_registry):
                self._registry_access_lock.acquire()

            repositories = {}

            with RegistryClientWrapper(url=self._settings.dtr_endpoint, credential=self._credential) as client:
                for repo_name in client.list_repository_names():
                    if "jobs/" in repo_name:
                        repositories[repo_name] = {
                            "image": f"{self._settings.dtr_endpoint}/{repo_name}",
                            "versions": client.list_tag_names(repo_name)
                        }

            """ If the lock is not yet acquired i.e., we are not at the startup,
                then we need to lock only the in-memory update process. The reason
                for that is that the repository retrieval might take up couple of
                seconds and locking that process as well would unnecessarily delay
                the request processing during update. """
            if not self._registry_access_lock.locked():
                self._registry_access_lock.acquire()

            with open(get_settings_as(ServiceSettings).project_config_path, "r") as project_config:
                project_config = json.load(project_config)

                for project in project_config["projects"]:
                    if project["path"] in repositories:
                        self._job_registry[project["name"]] = \
                            Job(job_name=project["name"],
                                image=repositories[project["path"]]["image"],
                                versions=repositories[project["path"]]["versions"],
                                identity_name=project["identity_name"] if "identity_name" in project else None)
        except Exception:
            # log only, the thread needs to live on
            traceback.print_exc(file=sys.stderr)
        finally:
            if self._registry_access_lock.locked():
                self._registry_access_lock.release()

    def _recurrent_job_registry_update(self):
        while not self._shutdown:
            if (self._last_registry_update_time is None) or \
                    ((datetime.now() - self._last_registry_update_time) >=
                     timedelta(seconds=self._settings.job_registry_update_interval_in_sec)):
                self._refresh_job_update()
                self._last_registry_update_time = datetime.now()
            time.sleep(2)
