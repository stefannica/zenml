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

from zenml.logger import get_logger
from zenml.metadata import ZenMLMetadataStore
from zenml.core.artifact_store import ArtifactStore
from zenml.service.app.store.base_store import BaseServiceStore

logger = get_logger(__name__)


class Provider:
    """ZenML provider definition.

    A ZenML provider defines an (allowed) combination of a Metadata Store +
    Service Store + Artifact Store.
    """

    def __init__(self,
                 service_store: BaseServiceStore = None,
                 metadata_store: ZenMLMetadataStore = None,
                 artifact_store: ArtifactStore = None):
        """
        Constructs a valid constructor.

        Args:
            service_store: Object of type `BaseServiceStore`.
            metadata_store: Object of type `ZenMLMetadataStore`.
            artifact_store: Object of type `ArtifactStore`.
        """
        self.service_store = service_store
        self.metadata_store = metadata_store
        self.artifact_store = artifact_store
