# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
from fastapi import APIRouter, HTTPException, Query
from starlette import status

from lapi.models.jobs import Job
from lapi.services.workflow_manager.services.jobs import JobService


def create_router() -> APIRouter:
    router = APIRouter(tags=["Jobs"], prefix="/jobs")

    job_service: JobService = JobService()

    @router.on_event("startup")
    async def on_startup():
        await job_service.on_startup()

    @router.on_event("shutdown")
    async def on_shutdown():
        await job_service.on_shutdown()

    @router.get("/")
    async def get_all(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)) -> list[Job]:
        return job_service.get_all(skip, limit)

    @router.get("/get-by-name/{job_name}")
    async def get_by_name(job_name: str) -> Job:
        job = job_service.get_by_name(job_name)

        if job is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Job not found: {job_name}")

        return job

    return router
