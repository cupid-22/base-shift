# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
from fastapi import APIRouter, HTTPException, status, Query
from pymongo.errors import DuplicateKeyError

from lapi.models.workflows import Workflow
from lapi.services.workflow_manager.services.jobs import JobService
from lapi.services.workflow_manager.services.workflows import WorkflowService


def create_router() -> APIRouter:
    router = APIRouter(tags=["Workflows"], prefix="/workflows")

    workflow_service: WorkflowService = WorkflowService()
    job_service: JobService = JobService()

    @router.on_event("startup")
    async def on_startup():
        await workflow_service.on_startup()

    @router.on_event("shutdown")
    async def on_shutdown():
        await workflow_service.on_shutdown()

    @router.get("/")
    async def get_all(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)) -> list[Workflow]:
        return await workflow_service.get_all(skip, limit)

    @router.get("/{workflow_id}")
    async def get_by_id(workflow_id: str) -> Workflow:
        workflow = await workflow_service.get_by_id(workflow_id)

        if workflow is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Workflow not found: {workflow_id}")

        return workflow

    @router.post("/")
    async def register(workflow: Workflow) -> Workflow:
        # Validate workflow request

        non_existing_jobs = [f"{route.job_name}:{route.job_version}" for route in workflow.event_routes if
                             not job_service.is_job_existing(route.job_name, route.job_version)]

        if 0 < len(non_existing_jobs):
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail=f"Unregistered jobs: {non_existing_jobs}")

        # Register workflow
        try:
            await workflow_service.register(workflow)
        except DuplicateKeyError:
            raise HTTPException(status.HTTP_409_CONFLICT,
                                detail=f"Workflow is already existing: {workflow.workflow_id}")

        return await workflow_service.get_by_id(workflow.workflow_id)

    return router
