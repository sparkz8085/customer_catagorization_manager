import os
import sys
from pandas import DataFrame
from src.cloud_storage.local_storage import LocalStorageService
from src.exception import CustomerException
from src.ml.model.estimator import CustomerSegmentationModel

class CustomerClusterEstimator:
    """
    This class is used to save and retrieve the model from local file storage and run predictions.
    """
    def __init__(self, model_dir: str, model_file_name: str):
        self.model_dir = model_dir
        self.model_file_name = model_file_name
        self.model_path = os.path.join(model_dir, model_file_name)
        self.storage = LocalStorageService()
        self.loaded_model: CustomerSegmentationModel = None

    def is_model_present(self) -> bool:
        try:
            return self.storage.file_exists(self.model_path)
        except Exception as e:
            print(e)
            return False

    def load_model(self) -> CustomerSegmentationModel:
        try:
            return self.storage.load_model(self.model_path)
        except Exception as e:
            raise CustomerException(e, sys) from e

    def save_model(self, from_file: str, remove: bool = False) -> None:
        try:
            self.storage.save_model(
                from_filepath=from_file,
                to_filepath=self.model_path,
                remove=remove
            )
        except Exception as e:
            raise CustomerException(e, sys) from e

    def predict(self, dataframe: DataFrame):
        try:
            if self.loaded_model is None:
                self.loaded_model = self.load_model()
            return self.loaded_model.predict(dataframe)
        except Exception as e:
            raise CustomerException(e, sys) from e
