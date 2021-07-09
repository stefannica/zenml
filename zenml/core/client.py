#  Copyright (c) maiot GmbH 2020. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""Base ZenML repository"""

from zenml.core.provider import BaseProvider
from zenml.logger import get_logger

logger = get_logger(__name__)


class Client:
    """ZenML client definition.

    ZenML Client is responsible for communication with the ZenML Service.
    """

    def __init__(self, provider: BaseProvider = None):
        """
        Construct a reference ZenML client.

        Args:
            provider (BaseProvider): A provider that defines the three stores.
            If None, then set to the default local provider.
        """
        if provider is None:
            provider = BaseProvider.get_default()
        self.provider = provider

    @property
    def provider(self):
        return self.__provider

    @provider.setter
    def provider(self, provider: BaseProvider):
        self.__provider = provider

    @property
    def metadata_store(self):
        return self.provider.metadata_store

    @property
    def artifact_store(self):
        return self.provider.artifact_store

    @property
    def service_store(self):
        return self.provider.service_store
