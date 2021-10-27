#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
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

import apache_beam as beam

from zenml.steps.split_steps.base_split_step import BaseSplitStep, \
    BaseSplitStepConfig
from zenml.steps.step_output import Output


class BeamSplitConfig(BaseSplitStepConfig):
    train_ratio: float = 0.7
    test_ratio: float = 0.15
    validation_ration: float = 0.15
    batch_size: int = 10


class BeamSplit(BaseSplitStep):

    @staticmethod
    def partition_fn(element, num_partition, config):
        return 0

    def split_fn(self,
                 dataset: beam.PCollection,
                 config: BeamSplitConfig,
                 ) -> Output(train=beam.PCollection,
                             test=beam.PCollection,
                             validation=beam.PCollection):
        train, test, validation = (
                dataset
                | "Batch" >> beam.BatchElements(config.batch_size)
                | 'Split' >> beam.Partition(self.partition_fn, 3, config)
        )

        return train, test, validation