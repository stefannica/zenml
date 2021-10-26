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
from typing import List, Text

import apache_beam as beam

from zenml.logger import get_logger
from zenml.steps.datasources.base_datasource import BaseDatasourceStep, \
    BaseDatasourceConfig
from zenml.utils import path_utils

logger = get_logger(__name__)


class TextDatasourceConfig(BaseDatasourceConfig):
    path: str
    skip_headers: bool = False
    allowed_file_extensions: List[Text] = [".csv", ".txt"]


class TextDatasource(BaseDatasourceStep):
    def process(
            self,
            config: TextDatasourceConfig
    ) -> beam.PCollection:
        dataset = self.ingest_fn(config)
        return dataset

    def ingest_fn(
            self,
            config: TextDatasourceConfig
    ) -> beam.PCollection:

        if path_utils.is_dir(config.path):
            files = path_utils.list_dir(config.path)
            if not files:
                raise RuntimeError(
                    'Pattern {} does not match any files.'.format(config.path))
        else:
            if path_utils.file_exists(config.path):
                files = [config.path]
            else:
                raise RuntimeError(f'{config.path} does not exist.')

        files = [uri for uri in files if os.path.splitext(uri)[-1]
                 in config.allowed_file_extensions]

        logger.info(f'Matched {len(files)}: {files}')

        logger.info(f'Using header from file: {files[0]}.')
        column_names = path_utils.load_csv_header(files[0])
        logger.info(f'Header: {column_names}.')

        pipeline = beam.Pipeline()
        data = (pipeline
                | 'Read' >> beam.io.ReadFromText(file_pattern=config.path,
                                                 skip_header_lines=1))

        return data
