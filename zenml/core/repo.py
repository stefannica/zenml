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
"""Base ZenML repository"""

import os
from pathlib import Path
from typing import Text, List, Dict, Any, Optional, Union, Type

from zenml.exceptions import InitializationException
from zenml.logger import get_logger
from zenml.metadata import BaseMetadataStore
from zenml.repo import ArtifactStore, GitWrapper, GlobalConfig, ZenMLConfig
from zenml.repo.constants import ZENML_DIR_NAME
from zenml.standards import standard_keys as keys
from zenml.utils import path_utils, yaml_utils
from zenml.utils.analytics_utils import track, CREATE_REPO, GET_PIPELINES, \
    GET_DATASOURCES, GET_STEPS_VERSIONS, \
    REGISTER_PIPELINE, GET_STEP_VERSION

logger = get_logger(__name__)


class Repository:
    """ZenML repository definition. This is a Singleton class.

    Every ZenML project exists inside a ZenML repository.
    """

    def __init__(self, path: Text = None):
        """
        Construct reference a ZenML repository

        Args:
            path (str): Path to root of repository
        """
        if Repository.__instance__ is None:
            if path is None:
                try:
                    # Start from cwd and traverse up until find zenml config.
                    path = Repository.get_zenml_dir(os.getcwd())
                except Exception:
                    # If there isnt a zenml.config, use the cwd
                    path = os.getcwd()

            if not path_utils.is_dir(path):
                raise Exception(f'{path} does not exist or is not a dir!')
            self.path = path

            # Hook up git, path needs to have a git folder.
            self.git_wrapper = GitWrapper(self.path)

            # Load the ZenML config
            try:
                self.zenml_config = ZenMLConfig(self.path)
            except InitializationException:
                # We allow this because we of the GCP orchestrator for now
                self.zenml_config = None

            Repository.__instance__ = self
        else:
            raise Exception("You cannot create another Repository class!")

    @staticmethod
    @track(event=CREATE_REPO)
    def init_repo(repo_path: Text, artifact_store_path: Text = None,
                  metadata_store: Optional[BaseMetadataStore] = None,
                  pipelines_dir: Text = None,
                  analytics_opt_in: bool = None):
        """
        Initializes a git repo with zenml.

        Args:
            repo_path (str): path to root of a git repo
            metadata_store: metadata store definition
            artifact_store_path (str): path where to store artifacts
            pipelines_dir (str): path where to store pipeline configs.
            analytics_opt_in (str): opt-in flag for analytics code.

        Raises:
            InvalidGitRepositoryError: If repository is not a git repository.
            NoSuchPathError: If the repo_path does not exist.
        """
        # check whether its a git repo by initializing GitWrapper
        git_wrapper = GitWrapper(repo_path)
        # TODO [LOW] Do proper checks and add to .gitignore
        git_wrapper.add_gitignore([ZENML_DIR_NAME + '/'])

        # use the underlying ZenMLConfig class to create the config
        ZenMLConfig.to_config(
            repo_path, artifact_store_path, metadata_store, pipelines_dir)

        # create global config
        global_config = GlobalConfig.get_instance()
        if analytics_opt_in is not None:
            global_config.set_analytics_opt_in(analytics_opt_in)
