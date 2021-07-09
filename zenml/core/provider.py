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

from zenml.service_store.base_store import BaseServiceStore

from zenml.artifact_store.base_artifact_store import BaseArtifactStore
from zenml.logger import get_logger
from zenml.metadata_store.base_metadata_store import BaseMetadataStore

logger = get_logger(__name__)


class BaseProvider:
    """ZenML provider definition.

    A ZenML provider defines an (allowed) combination of a Metadata Store +
    Service Store + Artifact Store.
    """

    def __init__(self,
                 service_store: BaseServiceStore = None,
                 metadata_store: BaseMetadataStore = None,
                 artifact_store: BaseArtifactStore = None):
        """
        Constructs a valid constructor.

        Args:
            service_store: Object of type `BaseServiceStore`.
            metadata_store: Object of type `BaseMetadataStore`.
            artifact_store: Object of type `BaseArtifactStore`.
        """
        self.service_store = service_store
        self.metadata_store = metadata_store
        self.artifact_store = artifact_store

    @property
    def service_store(self):
        return self.__service_store

    @service_store.setter
    def service_store(self, service_store: BaseServiceStore):
        self.__service_store = service_store

    @property
    def metadata_store(self):
        return self.metadata_store

    @metadata_store.setter
    def metadata_store(self, metadata_store: BaseMetadataStore):
        self.metadata_store = metadata_store

    @property
    def artifact_store(self):
        return self.__artifact_store

    @artifact_store.setter
    def artifact_store(self, artifact_store: BaseArtifactStore):
        self.__artifact_store = artifact_store

    @staticmethod
    def get_default():
        """Returns the default provider"""
        return BaseProvider(
            service_store=BaseServiceStore.get_default(),
            metadata_store=BaseMetadataStore.get_default(),
            artifact_store=BaseArtifactStore.get_default(),
        )
