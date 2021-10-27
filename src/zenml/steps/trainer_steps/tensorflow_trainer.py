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

import numpy as np
import tensorflow as tf

from zenml.steps.trainer_steps.base_trainer import BaseTrainer, \
    BaseTrainerConfig


class TensorflowTrainerConfig(BaseTrainerConfig):
    epochs: int = 5
    learning_rate: float = 1e-4


class TensorflowTrainer(BaseTrainer):
    def train_fn(self,
                 train_dataset: np.ndarray,
                 validation_dataset: np.ndarray,
                 config: TensorflowTrainerConfig,
                 ) -> tf.keras.Model:
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(10, activation="relu"),
            tf.keras.layers.Dense(10)])

        model.compile(
            optimizer=tf.keras.optimizers.Adam(config.learning_rate),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(
                from_logits=True),
            metrics=["accuracy"],
        )

        model.fit(train_dataset,
                  validation_data=validation_dataset,
                  epochs=config.epochs)

        return model

#
# @trainer
# def train_fn(
#         train_dataset: np.ndarray,
#         validation_dataset: np.ndarray,
#         config: TensorflowTrainerConfig,
# ) -> tf.keras.Model:
#     model = tf.keras.Sequential([
#         tf.keras.layers.Dense(10, activation="relu"),
#         tf.keras.layers.Dense(10)])
#
#     model.compile(
#         optimizer=tf.keras.optimizers.Adam(config.learning_rate),
#         loss=tf.keras.losses.SparseCategoricalCrossentropy(
#             from_logits=True),
#         metrics=["accuracy"],
#     )
#
#     model.fit(train_dataset,
#               validation_data=validation_dataset,
#               epochs=config.epochs)
#
#     return model
