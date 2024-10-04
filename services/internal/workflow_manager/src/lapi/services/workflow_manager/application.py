# =============================================================================
# C O P Y R I G H T
# -----------------------------------------------------------------------------
# Copyright (c) 2024 by Robert Bosch GmbH. All rights reserved.
#
# This file is property of Robert Bosch GmbH. Any unauthorized copy, use or
# distribution is an offensive act against international law and may be
# prosecuted under federal law. Its content is company confidential.
# =============================================================================
from fastapi import FastAPI

from lapi.models.settings import CommonSettings
from lapi.services.workflow_manager.controllers import workflows, jobs, general, jobs_instances
from lapi.services.workflow_manager.handlers.events import WorkflowEventHandler
from lapi.services.workflow_manager.handlers.job_instances import JobInstanceHandler
from lapi.utils import mongo, kafka
from lapi.utils.settings import get_settings_as


def create_app():
    app: FastAPI = FastAPI(title=f"Workflow Manager [{get_settings_as(CommonSettings).environment}]")
    app.include_router(workflows.create_router())
    app.include_router(jobs.create_router())
    app.include_router(jobs_instances.create_router())
    app.include_router(general.create_router())
    event_handler = WorkflowEventHandler()
    job_instance_handler = JobInstanceHandler()

    @app.on_event("startup")
    def on_startup():
        event_handler.start()
        job_instance_handler.start()

    @app.on_event("shutdown")
    def on_shutdown():
        mongo.client().close()
        kafka.producer().flush()
        job_instance_handler.shutdown()
        event_handler.shutdown()

    return app


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(create_app(),
                host="0.0.0.0",
                port=get_settings_as(CommonSettings).service_stack.workflow_manager.url.port,
                ssl_keyfile=get_settings_as(CommonSettings).service_stack.workflow_manager.ssl_key_file,
                ssl_certfile=get_settings_as(CommonSettings).service_stack.workflow_manager.ssl_cert_file)
