import os
from typing import Dict, List, Text

import apache_beam as beam

from zenml.logger import get_logger
from zenml.steps.datasources.base_datasource_step import BaseDatasourceStep, \
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
