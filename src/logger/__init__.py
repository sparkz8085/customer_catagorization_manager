import logging
import os
from pathlib import Path

from src.constant.training_pipeline import (
    ARTIFACT_DIR,
    LOG_DIR,
    LOG_FILE,
    PIPELINE_NAME,
)

BASE_DIR = Path(__file__).resolve().parents[2]

logs_path = os.path.join(
    str(BASE_DIR),
    PIPELINE_NAME,
    ARTIFACT_DIR,
    LOG_DIR
)

os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)