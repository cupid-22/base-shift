# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
from typing import Optional

from lapi.models.settings import CommonSettings
from lapi.models.workflows import Workflow
from lapi.utils import mongo
from lapi.utils.common import Singleton
from lapi.utils.settings import get_settings_as


class WorkflowService(metaclass=Singleton):
    def __init__(self):
        self._workflows = mongo.client()[WorkflowService.get_db_name()]["workflows"]

    @classmethod
    def get_db_name(cls) -> str:
        return f"{get_settings_as(CommonSettings).name}-{get_settings_as(CommonSettings).environment}"

    async def on_startup(self):
        await self._workflows.create_index("workflow_id", unique=True)

    async def on_shutdown(self):
        pass

    @mongo.transactional
    async def register(self, workflow: Workflow, session=None) -> None:
        await self._workflows.insert_one(workflow.dict(), session=session)

    async def get_all(self, skip: int = 0, limit: int = 10) -> list[Workflow]:
        cursor = self._workflows.find().skip(skip).limit(limit)

        workflows: list[Workflow] = []
        async for workflow in cursor:
            workflows.append(Workflow.model_validate(workflow))

        return workflows

    async def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        result = await self._workflows.find_one({"workflow_id": workflow_id})

        if result is None:
            return None

        return Workflow.model_validate(result)
