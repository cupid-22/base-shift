# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
import asyncio
import sys
import traceback
import uuid

from lapi.models.jobs import JobInstance
from lapi.models.messages import EventMessage
from lapi.services.workflow_manager.models.settings import ServiceSettings
from lapi.services.workflow_manager.services.job_instances import JobInstanceService
from lapi.services.workflow_manager.services.jobs import JobService
from lapi.services.workflow_manager.services.workflows import WorkflowService
from lapi.services.workflow_manager.handlers.k8s import KubernetesHandler
from lapi.utils.kafka import EventHandler
from lapi.utils.settings import get_settings_as


class WorkflowEventHandler(EventHandler):

    def __init__(self):
        super().__init__()
        self._workflow_service: WorkflowService = WorkflowService()

        self._job_service: JobService = JobService()

        self._job_instance_service: JobInstanceService = JobInstanceService()

        self._settings: ServiceSettings = get_settings_as(ServiceSettings)

        self._k8s_handler: KubernetesHandler = KubernetesHandler()

        self._event_loop = None

    def _process_event(self, event_message: EventMessage) -> None:
        """
        This method implements the logic to schedule the async wrapper method, which
        contains the event processor operation. Notice that since the async scheduling
        does not block, we need to synchronize the async method execution i.e., we
        need to block until the async operation in FastAPI's event loop finishes.
        :param event_message: event message to be processed
        """

        asyncio.run_coroutine_threadsafe(self._async_processor_wrapper(event_message), self._event_loop).result()

    async def _async_processor_wrapper(self, event_message: EventMessage) -> None:
        """
        This method implements the event processing logic for the workflow manager.
        The following actions are taken for all events without filtering:
        1. Get the workflow id from the event
        2. Retrieve the workflow from the database
        3. Retrieve the event config for the received event
        4. Check source filter
        5. Extract the jobs to be deployed
        6. Deploy the jobs on K8s

        :param event_message: event message received from the bus
        """

        if event_message.source_id != self._settings.name:
            workflow = await self._workflow_service.get_by_id(event_message.workflow_id)

            if workflow is None:
                raise LookupError(f"Workflow not found: {event_message.workflow_id}")

            active_routes = [route for route in workflow.event_routes
                             if (route.event_name == event_message.event) and
                             ((route.event_source is None) or (route.event_source == event_message.source_id))]

            missing_jobs = list()
            for route in active_routes:
                if not self._job_service.is_job_existing(route.job_name, route.job_version):
                    missing_jobs.append((route.job_name, route.job_version))

            if 0 < len(missing_jobs):
                raise LookupError(f"Missing jobs: {missing_jobs}")

            for route in active_routes:
                job_instance = JobInstance(instance_id=f"{route.job_name}-{uuid.uuid4()}",
                                           request_id=event_message.request_id,
                                           workflow_id=event_message.workflow_id,
                                           job_name=route.job_name,
                                           job_version=route.job_version,
                                           status="Unknown")

                await self._job_instance_service.register(job_instance)

                try:
                    self._k8s_handler.deploy_job_settings(event_message,
                                                          job_instance,
                                                          self._job_service.get_by_name(route.job_name))

                    self._k8s_handler.deploy_job(event_message,
                                                 job_instance,
                                                 self._job_service.get_by_name(route.job_name))
                except Exception as e:
                    traceback.print_exc(file=sys.stderr)

                    self._job_instance_service.update(job_instance.instance_id,
                                                      {
                                                          "status": "Failed",
                                                          "details": str(e)
                                                      })

                    # rollback -> delete deployed setting
                    if self._k8s_handler.is_job_deployed(job_instance):
                        self._k8s_handler.delete_job(job_instance)
                    if self._k8s_handler.is_job_settings_deployed(job_instance):
                        self._k8s_handler.delete_job_settings(job_instance)

                    raise

    def start(self):
        self._event_loop = asyncio.get_event_loop()
        super().start()
