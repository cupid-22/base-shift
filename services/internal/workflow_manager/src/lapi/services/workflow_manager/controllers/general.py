# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
from fastapi import APIRouter

from lapi.models.general import ServiceInfo
from lapi.models.settings import CommonSettings
from lapi.utils.settings import get_settings_as


def create_router() -> APIRouter:
    router = APIRouter(tags=["General"])

    @router.on_event("startup")
    async def on_startup():
        pass

    @router.on_event("shutdown")
    async def on_shutdown():
        pass

    @router.get("/info")
    async def get_info() -> ServiceInfo:
        return ServiceInfo(instance_id=get_settings_as(CommonSettings).instance_id)

    return router
