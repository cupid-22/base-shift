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

from pydantic import BaseModel

from lapi.models.settings import CommonServiceSettings


class KubernetesSettings(BaseModel):
    config_file: Optional[str] = None
    namespace: Optional[str] = "default"
    cacert_file: Optional[str] = None
    explicit_config: Optional[dict] = None
    verify_ssl: Optional[bool] = True


class ServiceSettings(CommonServiceSettings):
    kubernetes: Optional[KubernetesSettings] = KubernetesSettings()
    log_store_path: str
    project_config_path: str
    job_registry_update_interval_in_sec: Optional[int] = 60
    dtr_endpoint: Optional[str] = None
