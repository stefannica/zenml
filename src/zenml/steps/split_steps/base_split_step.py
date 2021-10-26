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

import apache_beam as beam

from zenml.steps.base_step import BaseStep
from zenml.steps.base_step_config import BaseStepConfig
from zenml.steps.step_output import Output


# Configuration for the split step ############################################
class BaseSplitStepConfig(BaseStepConfig):
    """Base class for split configs to inherit from"""


# Base implementation of the split step #######################################
class BaseSplitStep(BaseStep):
    """Base step implementation for any split step implementation on ZenML
    """

    def process(
            self,
            dataset: beam.PCollection,
            config: BaseSplitStepConfig,
    ) -> Output(train=beam.PCollection,
                test=beam.PCollection,
                validation=beam.PCollection):

        split_fn = getattr(self, "split_fn")

        train, test, validation = (
                dataset
                | 'Split' >> beam.Partition(split_fn, 3, config)
        )

        return train, test, validation

    @abstractmethod
    def split_fn(self):
        pass
