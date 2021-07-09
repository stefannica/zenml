#  Copyright (c) maiot GmbH 2020. All Rights Reserved.
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
"""Env Utilities"""

import os
from pathlib import Path
from typing import Text

from zenml.logger import get_logger
from zenml.repo.constants import ZENML_CONFIG_NAME, \
    ZENML_DIR_NAME
from zenml.utils import path_utils

logger = get_logger(__name__)

ENV_LOCAL_CONFIG_STR = 'ZENML_LOCAL_CONFIG_PATH'
ENV_GLOBAL_CONFIG_STR = 'ZENML_GLOBAL_CONFIG_PATH'


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


def get_zenml_dir(starting_path: Text):
    """
    Recursive function to find the zenml config starting from `starting_path`.

    Args:
        starting_path (str): Root path to start the search.
    """
    if is_zenml_dir(starting_path):
        return starting_path

    if path_utils.is_root(starting_path):
        raise Exception(
            'Looks like you used ZenML outside of a ZenML repo. '
            'Please init a ZenML repo first before you using '
            'the framework.')
    return get_zenml_dir(str(Path(starting_path).parent))


def is_zenml_dir(path: Text):
    """
    Check if dir is a zenml dir or not.

    Args:
        path (str): path to the root.
    """
    config_path = os.path.join(path, ZENML_DIR_NAME, ZENML_CONFIG_NAME)
    if not path_utils.file_exists(config_path):
        return False
    return True
