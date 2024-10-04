# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
from pathlib import Path
from typing import Optional

from azure.identity import ClientSecretCredential

from lapi.models.jobs import JobInstance
from lapi.models.settings import CommonSettings
from lapi.services.workflow_manager.models.settings import ServiceSettings
from lapi.utils import mongo
from lapi.utils.common import Singleton
from lapi.utils.settings import get_settings_as


class JobInstanceService(metaclass=Singleton):
    def __init__(self):
        self._settings = get_settings_as(ServiceSettings)

        self._job_instances = mongo.client()[JobInstanceService.get_db_name()]["job_instances"]

        self._credential = ClientSecretCredential(
            tenant_id=self._settings.identity.tenant_id,
            client_id=self._settings.identity.client_id,
            client_secret=self._settings.identity.client_secret
        ) if self._settings.identity is not None else None

        self._log_store_path = Path(self._settings.log_store_path)

    @classmethod
    def get_db_name(cls) -> str:
        return f"{get_settings_as(CommonSettings).name}-{get_settings_as(CommonSettings).environment}"

    async def on_startup(self):
        await self._job_instances.create_index("instance_id", unique=True)
        await self._job_instances.create_index("request_id")
        await self._job_instances.create_index("workflow_id")

    async def on_shutdown(self):
        pass

    @mongo.transactional
    async def register(self, job_instance: JobInstance, session=None) -> None:
        await self._job_instances.insert_one(job_instance.dict(), session=session)

    def update(self, instance_id: str, attributes: dict, session=None) -> None:
        self._job_instances.update_one({"instance_id": instance_id}, {"$set": attributes}, session=session)

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[JobInstance]:
        cursor = self._job_instances.find().skip(skip).limit(limit)

        job_instances: list[JobInstance] = []
        async for job in cursor:
            job_instances.append(JobInstance.model_validate(job))

        return job_instances

    async def get_by_request_id(self, request_id: str, skip: int = 0, limit: int = 10) -> list[JobInstance]:
        cursor = self._job_instances.find({"request_id": request_id}).skip(skip).limit(limit)

        job_instances: list[JobInstance] = []
        async for job in cursor:
            job_instances.append(JobInstance.model_validate(job))

        return job_instances

    async def get_by_instance_id(self, instance_id: str) -> Optional[JobInstance]:
        result = await self._job_instances.find_one({"instance_id": instance_id})

        if result is None:
            return None

        return JobInstance.model_validate(result)

    async def get_log_file_path(self, job_instance: JobInstance) -> Optional[Path]:
        log_file_path = self._log_store_path / job_instance.request_id / job_instance.instance_id
        return log_file_path if log_file_path.exists() else None
