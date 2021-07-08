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
from typing import Text

from app.store.base_store import BaseServiceStore
from zenml.logger import get_logger

logger = get_logger(__name__)



class MySQLServiceStore(BaseServiceStore):
    """Definition of MySQL Service DB, to be used in production."""

    def __init__(self,
                 address: Text = 'localhost',
                 port: int = 5432,
                 db: Text = 'app',
                 user: Text = 'postgres',
                 password: Text = 'notsecureatall'):
        self.address = address
        self.port = port
        self.db = db
        self.user = user
        self.password = password

    def get_sqlalchemy_db_uri(self):
        return (
            f"mysql://{self.user}:{self.password}@{self.address}:"
            f"{self.port}/"
            f"{self.db}"
        )

    @property
    def exists(self):
        return True

    def do_initialization_asserts(self):
        # check if `libraries` are installed
        pass