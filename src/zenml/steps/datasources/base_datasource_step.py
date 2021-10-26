#  Copyright (c) ZenML GmbH 2020. All Rights Reserved.
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

import types
from abc import abstractmethod
from typing import Callable, Type

import apache_beam as beam
from typing import Dict, List, Text

from zenml.steps.base_step import BaseStep
from zenml.steps.base_step_config import BaseStepConfig
from zenml.artifacts.data_artifact import DataArtifact

# Configuration for the split step ############################################
class BaseDatasourceConfig(BaseStepConfig):
    """Base class for datasource configs to inherit from"""


# Base implementation of the split step #######################################
class BaseDatasourceStep(BaseStep):
    """Base step implementation for any Datasource step implementation on ZenML

    The process function of this step is set to not include any input
    artifacts. Moreover, it utilizes the ingest_fn to read the data from the
    source and returns a Beam.PCollection.
    """

    def process(
            self,
            datasource_config: DataArtifact
    ) -> DataArtifact:
        ingest_fn = self.ingest_fn(datasource_config)
        return dataset

    @abstractmethod
    def ingest_fn(self, datasource_config):
        pass
