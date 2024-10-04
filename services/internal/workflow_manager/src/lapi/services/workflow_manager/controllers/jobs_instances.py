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

from fastapi import APIRouter, HTTPException, Query
from starlette import status
from starlette.responses import FileResponse

from lapi.models.jobs import JobInstance
from lapi.services.workflow_manager.services.job_instances import JobInstanceService


def create_router() -> APIRouter:
    router = APIRouter(tags=["Jobs Instances"], prefix="/job-instances")

    job_instance_service: JobInstanceService = JobInstanceService()

    @router.on_event("startup")
    async def on_startup():
        await job_instance_service.on_startup()

    @router.on_event("shutdown")
    async def on_shutdown():
        await job_instance_service.on_shutdown()

    @router.get("/")
    async def get_all(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)) -> list[JobInstance]:
        return await job_instance_service.get_all(skip, limit)

    @router.get("/{instance_id}")
    async def get_by_instance_id(instance_id: str) -> JobInstance:
        job_instance = await job_instance_service.get_by_instance_id(instance_id)
        if job_instance is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Job instance not found: {instance_id}")

        return job_instance

    @router.get("/label-request/{request_id}")
    async def get_by_request_id(request_id: str,
                                skip: int = Query(0, ge=0),
                                limit: int = Query(10, ge=1)) -> list[JobInstance]:
        return await job_instance_service.get_by_request_id(request_id, skip, limit)

    @router.get("/logs/{instance_id}")
    async def get_logs_by_id(instance_id: str) -> FileResponse:
        job_instance = await job_instance_service.get_by_instance_id(instance_id)
        if job_instance is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Job instance not found: {instance_id}")

        log_file_path = await job_instance_service.get_log_file_path(job_instance)

        if log_file_path is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Log file for job instance not found: {instance_id}")

        return FileResponse(path=log_file_path,
                            media_type="application/octet-stream",
                            filename=log_file_path.name)

    return router
