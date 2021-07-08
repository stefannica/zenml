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
from abc import abstractmethod

from zenml.logger import get_logger

logger = get_logger(__name__)


class BaseServiceStore:
    """ZenML Service DB definition.

    This defines the implementation of the DB the service is using.
    """

    @abstractmethod
    def get_sqlalchemy_db_uri(self):
        pass

    @abstractmethod
    @property
    def exists(self):
        pass

    @abstractmethod
    def do_initialization_asserts(self):
        pass

    def bootstrap(self):
        pass
