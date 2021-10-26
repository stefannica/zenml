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

import os
from typing import Any, Type

import apache_beam as beam

from zenml.materializers.base_materializer import BaseMaterializer

DEFAULT_FILENAME = "data"


class BeamMaterializer(BaseMaterializer):
    """Materializer to read data to and from beam."""

    ASSOCIATED_TYPES = [beam.Pipeline, beam.PCollection]

    def handle_input(self, data_type: Type) -> Any:
        """Reads all files inside the artifact directory and materializes them
        as a beam compatible output."""
        super().handle_input(data_type)

        pipeline = beam.Pipeline()
        return pipeline | beam.io.ReadFromText(self.artifact.uri + "/*")

    def handle_return(self, pcollection: beam.PCollection):
        """Appends a beam.io.WriteToParquet at the end of a beam pipeline
        and therefore persists the results.

        Args:
            pcollection: A beam.PCollection object.
        """
        super().handle_return(pcollection)

        filepath = os.path.join(self.artifact.uri, DEFAULT_FILENAME)
        pcollection | f"WriteToText{self.artifact.name}" >> beam.io.WriteToText(
            filepath
        )
        pcollection.pipeline.run()
