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
import time
import traceback
from pathlib import Path
from threading import Thread

from kubernetes.client import ApiException

from lapi.models.jobs import JobInstance
from lapi.services.workflow_manager.handlers.k8s import KubernetesHandler
from lapi.services.workflow_manager.models.settings import ServiceSettings
from lapi.services.workflow_manager.services.job_instances import JobInstanceService
from lapi.utils.settings import get_settings_as


class JobInstanceHandler:

    def __init__(self):
        self._job_instance_service: JobInstanceService = JobInstanceService()

        self._settings: ServiceSettings = get_settings_as(ServiceSettings)

        self._k8s_handler: KubernetesHandler = KubernetesHandler()

        self._shutdown: bool = False

        self._job_monitor_thread: Thread = Thread(target=self._job_monitor)

        self._log_store_path = Path(self._settings.log_store_path)
        self._log_store_path.mkdir(exist_ok=True)

    def _job_monitor(self):
        while not self._shutdown:
            try:
                job_instances: list[JobInstance] = self._k8s_handler.get_job_instances()
                for job_instance in job_instances:
                    self._job_instance_service.update(job_instance.instance_id, {"status": job_instance.status})
 
                    if ("Succeeded" == job_instance.status) or ("Failed" == job_instance.status):
                        try:
                            request_log_path = self._log_store_path / job_instance.request_id
                            request_log_path.mkdir(exist_ok=True)

                            self._k8s_handler.stream_log_to_file(
                                job_instance,
                                f"{request_log_path / job_instance.instance_id}"
                            )

                            self._k8s_handler.delete_job(job_instance)
                        except ApiException as e:
                            # log only, if other issues than not found, since the job shall be deleted as well
                            if 404 != e.status:
                                traceback.print_exc()

                        try:
                            self._k8s_handler.delete_job_settings(job_instance)
                        except ApiException as e:
                            # log only, if other issues than not found
                            if 404 != e.status:
                                traceback.print_exc(file=sys.stderr)

                time.sleep(5)
            except Exception:
                # log only, the thread needs to live on
                traceback.print_exc(file=sys.stderr)

    def start(self):
        self._job_monitor_thread.start()

    def shutdown(self):
        self._shutdown = True
        self._job_monitor_thread.join()
