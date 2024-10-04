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

import pytest_asyncio

from lapi.models.jobs import Job
from lapi.services.workflow_manager.services.workflows import WorkflowService
from starlette import status
import pytest


@pytest_asyncio.fixture(autouse=True)
async def cleanup(mongo_client):
    await mongo_client.drop_database(WorkflowService.get_db_name())
    yield
    await mongo_client.drop_database(WorkflowService.get_db_name())


@pytest.mark.asyncio
async def test_get_all(client, mongo_client):
    job = Job(job_name="test-job",
              image="localhost:5000/jobs/test-job",
              versions=["latest"],
              identity_name="id-test-job")

    response = client.get("/jobs/")

    assert response.status_code == status.HTTP_200_OK

    retrieved_jobs = json.loads(response.text)

    assert 1 == len(retrieved_jobs)

    retrieved_job = Job.model_validate(retrieved_jobs[0])

    assert job == retrieved_job


@pytest.mark.asyncio
async def test_get_by_name(client, mongo_client):
    job = Job(job_name="test-job",
              image="localhost:5000/jobs/test-job",
              versions=["latest"],
              identity_name="id-test-job")

    response = client.get("/jobs/get-by-name/test-job")

    assert response.status_code == status.HTTP_200_OK

    retrieved_job = Job.model_validate(json.loads(response.text))

    assert job == retrieved_job
