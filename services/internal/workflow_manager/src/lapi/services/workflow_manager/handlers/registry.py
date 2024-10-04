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
from typing import Union, Optional
from urllib.parse import urlparse

from azure.containerregistry import ContainerRegistryClient
from azure.identity import ManagedIdentityCredential, ClientSecretCredential
from httpx import Client, RequestError
from starlette import status


class RegistryClientWrapper:

    def __init__(self,
                 url: str,
                 credential: Optional[Union[ManagedIdentityCredential, ClientSecretCredential]] = None):

        self._is_local: bool = any([local_spec in url for local_spec in ['localhost', '127.0.0.1', '::1']])

        self._url: str = url if not self._is_local else url if url.startswith("http://") else f"http://{url}"

        self._credential: Union[ManagedIdentityCredential, ClientSecretCredential] = credential

        self._client: Union[Client, ContainerRegistryClient] = \
            Client() if self._is_local else ContainerRegistryClient(endpoint=url, credential=credential)

    def list_repository_names(self):
        if self._is_local:
            response = self._client.get(url=f"{self._url}/v2/_catalog")
            if status.HTTP_200_OK != response.status_code:
                raise RequestError(response.text)
            return json.loads(response.text)["repositories"]
        else:
            return [repository for repository in self._client.list_repository_names()]

    def list_tag_names(self, repository: str):
        if self._is_local:
            response = self._client.get(url=f"{self._url}/v2/{repository}/tags/list")
            if status.HTTP_200_OK != response.status_code:
                raise RequestError(response.text)
            return json.loads(response.text)["tags"]
        else:
            return [tag.name for tag in self._client.list_tag_properties(repository)]

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
