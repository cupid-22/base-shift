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

from lapi.models.identities import ServiceIdentity
from lapi.models.workflows import Workflow, EventRoute
from lapi.services.workflow_manager.services.workflows import WorkflowService
from starlette import status
import pytest


@pytest_asyncio.fixture(autouse=True)
async def cleanup(mongo_client):
    await mongo_client.drop_database(WorkflowService.get_db_name())
    yield
    await mongo_client.drop_database(WorkflowService.get_db_name())


@pytest.mark.asyncio
async def test_register(client, mongo_client):
    workflow = Workflow(workflow_id="test-workflow",
                        event_routes=[
                            EventRoute(event_name="TEST",
                                       job_name="test-job",
                                       job_version="latest")
                        ],
                        created_by=ServiceIdentity(
                            object_id="N/A",
                            tenant_id="N/A",
                            client_id="N/A"
                        ))

    response = client.post("/workflows/", json=workflow.model_dump())

    assert response.status_code == status.HTTP_200_OK

    assert workflow == Workflow.model_validate(json.loads(response.text))


@pytest.mark.asyncio
async def test_get_all(client, mongo_client):
    workflow1 = Workflow(workflow_id="test-workflow",
                         event_routes=[
                             EventRoute(event_name="TEST",
                                        job_name="test-job",
                                        job_version="latest")
                         ],
                         created_by=ServiceIdentity(
                             object_id="N/A",
                             tenant_id="N/A",
                             client_id="N/A"
                         ))

    workflow2 = Workflow(workflow_id="test-workflow",
                         event_routes=[
                             EventRoute(event_name="TEST",
                                        job_name="test-job",
                                        job_version="latest")
                         ],
                         created_by=ServiceIdentity(
                             object_id="N/A",
                             tenant_id="N/A",
                             client_id="N/A"
                         ))

    workflows = mongo_client[WorkflowService.get_db_name()]["workflows"]
    await workflows.insert_many([workflow1.model_dump(), workflow2.model_dump()])

    response = client.get("/workflows/")

    assert response.status_code == status.HTTP_200_OK

    retrieved_workflows = [Workflow.model_validate(obj) for obj in json.loads(response.text)]

    assert 2 == len(retrieved_workflows)
    assert workflow1 == retrieved_workflows[0]
    assert workflow2 == retrieved_workflows[1]


@pytest.mark.asyncio
async def test_get_by_id(client, mongo_client):
    workflow = Workflow(workflow_id="test-workflow",
                        event_routes=[
                            EventRoute(event_name="TEST",
                                       job_name="test-job",
                                       job_version="latest")
                        ],
                        created_by=ServiceIdentity(
                            object_id="N/A",
                            tenant_id="N/A",
                            client_id="N/A"
                        ))

    workflows = mongo_client[WorkflowService.get_db_name()]["workflows"]
    await workflows.insert_one(workflow.model_dump())

    response = client.get("/workflows/test-workflow")

    assert response.status_code == status.HTTP_200_OK

    assert workflow == Workflow.model_validate(json.loads(response.text))
