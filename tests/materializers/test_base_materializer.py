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


def test_check_materializer_registry_with_artifacts():
    """Tests that the base materializer class is not registered as a usable materializer."""
    from zenml.artifacts.base_artifact import BaseArtifact

    artifact = BaseArtifact()
    materializer_types = artifact.materializers.get_types()

    assert "base" not in materializer_types