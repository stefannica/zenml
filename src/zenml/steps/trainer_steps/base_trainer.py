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
from abc import abstractmethod
from typing import Any

from zenml.artifacts import DataArtifact, ModelArtifact
from zenml.steps.base_step import BaseStep
from zenml.steps.base_step_config import BaseStepConfig


class BaseTrainerConfig(BaseStepConfig):
    """Base class for trainer configs to inherit from"""


class BaseTrainer(BaseStep):
    """Base step implementation for any trainer step implementation on ZenML
    """

    def process(
            self,
            train_dataset: DataArtifact,
            validation_dataset: DataArtifact,
            config: BaseTrainerConfig,
    ) -> ModelArtifact:
        model = self.train_fn(train_dataset, validation_dataset)
        return model

    @abstractmethod
    def train_fn(self, train_dataset, validation_dataset) -> Any:
        pass
