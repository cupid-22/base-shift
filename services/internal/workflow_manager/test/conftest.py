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

import pytest
import pytest_asyncio
from confluent_kafka.admin import AdminClient
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.testclient import TestClient

from lapi.models.settings import get_local_common_service_settings, CommonServiceSettings, CommonSettings
from lapi.services.workflow_manager.application import create_app
from lapi.utils.common import get_project_root_path
from lapi.utils.kafka import get_event_topic_id
from lapi.utils.settings import SettingsLoader, get_settings_as


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup():
    test_settings = get_local_common_service_settings(service_name="workflow-manager", environment="test")
    test_settings["log_store_path"] = \
        str(get_project_root_path() / "services" / "workflow_manager" / "test" / "log")
    test_settings["project_config_path"] = str(
        get_project_root_path() / "services" / "workflow_manager" / "test" / "resources" / "test-projects.json")
    test_settings["inherit_proxy_settings"] = True
    test_settings["dtr_endpoint"] = "localhost:5000"
    test_settings["kubernetes"] = {
        "namespace": "default",
        "verify_ssl": False
    }
    SettingsLoader.load(test_settings)
    yield


@pytest_asyncio.fixture(scope="session", autouse=True)
async def kafka_admin_client(setup):
    admin_client = AdminClient({"bootstrap.servers": get_settings_as(CommonSettings).kafka.bootstrap_servers})
    if get_event_topic_id() in admin_client.list_topics().topics:
        admin_client.delete_topics([get_event_topic_id()])
    yield admin_client
    if get_event_topic_id() in admin_client.list_topics().topics:
        admin_client.delete_topics([get_event_topic_id()])


@pytest_asyncio.fixture(scope="session")
async def client():
    with TestClient(app=create_app()) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def mongo_client():
    client = AsyncIOMotorClient(get_settings_as(CommonServiceSettings).mongodb.connection_string)
    yield client
    client.close()
