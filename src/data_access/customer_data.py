import os
import sys
from typing import Optional

import numpy as np
import pandas as pd

from src.configuration.mongo_db_connection import MongoDBClient
from src.constant.database import DATABASE_NAME
from src.exception import CustomerException
from src.logger import logging


class CustomerData:
    """
    This class helps to export entire MongoDB records as a pandas DataFrame, 
    with a fallback to a local CSV file if MongoDB is unavailable.
    """

    def __init__(self):
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            logging.warning(f"MongoDB client initialization failed: {e}. Will fallback to local CSV file.")
            self.mongo_client = None

    def export_collection_as_dataframe(
        self, collection_name: str, database_name: Optional[str] = None
    ) -> pd.DataFrame:
        try:
            """
            export entire collection as dataframe:
            return pd.DataFrame of collection
            """
            if self.mongo_client is None:
                raise Exception("MongoDB client is not connected.")

            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]
            
            df = pd.DataFrame(list(collection.find()))
            if df.empty:
                raise Exception("MongoDB collection is empty.")

            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            logging.warning(f"Failed to fetch data from MongoDB ({e}). Falling back to local CSV file.")
            csv_path = os.path.join("notebooks", "marketing_campaign.csv")
            if not os.path.exists(csv_path):
                # Try standard relative path search
                csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "notebooks", "marketing_campaign.csv")
            
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, sep="\t")
                if "_id" in df.columns.to_list():
                    df = df.drop(columns=["_id"], axis=1)
                df.replace({"na": np.nan}, inplace=True)
                logging.info(f"Successfully loaded {len(df)} records from local CSV: {csv_path}")
                return df
            else:
                raise CustomerException(f"Failed to find local CSV at {csv_path} and MongoDB connection failed.", sys)

