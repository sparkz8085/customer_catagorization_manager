import os
import sys
import shutil

from src.entity.artifact_entity import (ModelPusherArtifact,
                                           ModelTrainerArtifact,
                                           DataTransformationArtifact)
from src.entity.config_entity import ModelPusherConfig
from src.exception import CustomerException
from src.logger import logging
from src.ml.model.local_estimator import CustomerClusterEstimator


class ModelPusher:
    def __init__(
        self,
        model_trainer_artifact: ModelTrainerArtifact,
        data_transformation_artifact: DataTransformationArtifact,
        model_pusher_config: ModelPusherConfig,
    ):
        self.model_trainer_artifact = model_trainer_artifact
        self.data_transformation_artifact = data_transformation_artifact
        self.model_pusher_config = model_pusher_config
        self.src_estimator = CustomerClusterEstimator(
            model_dir=model_pusher_config.model_dir,
            model_file_name=model_pusher_config.model_file_name,
        )

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        logging.info("Entered initiate_model_pusher method of ModelPusher class")

        try:
            logging.info("Saving model to local disk")
            self.src_estimator.save_model(
                from_file=self.model_trainer_artifact.trained_model_file_path,
                remove=False
            )
            
            logging.info("Saving preprocessor object to local disk")
            preprocessor_dest_path = os.path.join(
                self.model_pusher_config.preprocessor_dir,
                self.model_pusher_config.preprocessor_file_name
            )
            os.makedirs(os.path.dirname(preprocessor_dest_path), exist_ok=True)
            shutil.copy(
                self.data_transformation_artifact.transformed_object_file_path,
                preprocessor_dest_path
            )
            
            model_pusher_artifact = ModelPusherArtifact(
                saved_model_path=self.src_estimator.model_path,
            )
            logging.info("Saved artifacts to local disk successfully")
            logging.info(f"Model pusher artifact: [{model_pusher_artifact}]")
            logging.info("Exited initiate_model_pusher method of ModelPusher class")
            return model_pusher_artifact
        except Exception as e:
            raise CustomerException(e, sys) from e
