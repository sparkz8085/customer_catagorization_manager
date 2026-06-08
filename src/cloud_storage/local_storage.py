import os
import sys
import pickle
from src.logger import logging
from src.exception import CustomerException

class SafeUnpickler(pickle.Unpickler):
    ALLOWED_MODULES = {
        "numpy",
        "numpy.core.multiarray",
        "pandas",
        "pandas.core.frame",
        "pandas.core.internals.managers",
        "sklearn",
        "sklearn.pipeline",
        "sklearn.preprocessing",
        "xgboost",
        "src.ml.model.estimator",
        "copyreg",
    }
    
    ALLOWED_BUILTINS = {
        "dict",
        "list",
        "set",
        "tuple",
        "str",
        "int",
        "float",
        "bool",
        "bytes",
        "object",
    }

    def find_class(self, module, name):
        # Allow checking in submodules of allowed packages
        base_module = module.split('.')[0]
        if module in self.ALLOWED_MODULES or base_module in self.ALLOWED_MODULES:
            return super().find_class(module, name)
        if module == "builtins" and name in self.ALLOWED_BUILTINS:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"Refusing to unpickle unsafe global: {module}.{name}")


class LocalStorageService:
    def __init__(self):
        pass

    def file_exists(self, filepath: str) -> bool:
        try:
            return os.path.exists(filepath)
        except Exception as e:
            raise CustomerException(e, sys)

    def load_model(self, filepath: str) -> object:
        logging.info(f"Loading model locally from: {filepath}")
        try:
            model_trusted = os.getenv("MODEL_TRUSTED", "") in {"1", "true", "TRUE", "yes", "YES"}
            if not model_trusted:
                raise CustomerException(
                    "Refusing to unpickle local model without trust. Set MODEL_TRUSTED=1 to allow.",
                    sys
                )
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Model file does not exist at: {filepath}")
            with open(filepath, "rb") as file_obj:
                return SafeUnpickler(file_obj).load()
        except Exception as e:
            raise CustomerException(e, sys) from e

    def save_model(self, from_filepath: str, to_filepath: str, remove: bool = True):
        logging.info(f"Saving model from {from_filepath} to {to_filepath}")
        try:
            os.makedirs(os.path.dirname(to_filepath), exist_ok=True)
            import shutil
            shutil.copy(from_filepath, to_filepath)
            if remove:
                os.remove(from_filepath)
                logging.info(f"Removed source file {from_filepath}")
        except Exception as e:
            raise CustomerException(e, sys) from e
