#  Copyright (c) maiot GmbH 2021. All Rights Reserved.
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
from pathlib import Path
from typing import Text

from app.store.base_store import BaseServiceStore
from zenml.logger import get_logger
from zenml.utils import path_utils

logger = get_logger(__name__)


class SqliteServiceStore(BaseServiceStore):
    """Definition of SQLite Service DB, mainly used for local development."""

    def __init__(self, path: Text = None):
        if path is None:
            self.path = 'db/sql_app.db'
        else:
            self.path = path

        path_utils.create_dir_recursive_if_not_exists(
            str(Path(self.path).parent))

    def get_sqlalchemy_db_uri(self):
        return f'sqlite:///./db/sql_app.db'

    @property
    def exists(self):
        if path_utils.file_exists(self.path):
            return True
        return False

    def do_initialization_asserts(self):
        pass
