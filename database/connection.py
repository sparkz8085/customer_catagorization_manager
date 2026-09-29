import os
import certifi
import pymongo
import numpy as np
import pandas as pd
from config import (
    CUSTOMER_COLLECTION_NAME,
    DATABASE_NAME,
    ANALYSIS_HISTORY_COLLECTION_NAME,
    MONGO_DB_URL_KEY,
    SUBSCRIPTION_COLLECTION_NAME,
    USER_COLLECTION_NAME,
    is_production,
)

ca = certifi.where()

import time
import re

# Cache connection failure to avoid blocking local runs
_last_connection_check = 0.0
_mongodb_available = True
_mongodb_client = None

def _safe_mongodb_error(error):
    """Remove connection-string credentials from driver error messages."""
    message = str(error)
    return re.sub(r"mongodb(?:\+srv)?://[^\s]+", "<redacted-mongodb-uri>", message)

def get_mongodb_client():
    """
    Attempts to connect to MongoDB Atlas database.
    Returns MongoClient object or None if connection fails or is not configured.
    """
    global _last_connection_check, _mongodb_available, _mongodb_client

    if _mongodb_client is not None:
        return _mongodb_client
    
    mongo_db_url = os.getenv(MONGO_DB_URL_KEY)
    if not mongo_db_url:
        print("[WARN] MongoDB connection URL (MONGO_DB_URL) not found in env.")
        return None

    current_time = time.time()
    # If MongoDB failed recently, don't try again for 60 seconds to prevent blocking
    if not _mongodb_available and (current_time - _last_connection_check) < 60:
        return None

    try:
        client = pymongo.MongoClient(
            mongo_db_url,
            tlsCAFile=ca,
            serverSelectionTimeoutMS=10000,
        )
        # Test connection
        client.admin.command('ping')
        database = client[DATABASE_NAME]
        database[CUSTOMER_COLLECTION_NAME].create_index("owner_id")
        database[CUSTOMER_COLLECTION_NAME].create_index([("owner_id", 1), ("customer_id", 1)])
        database[CUSTOMER_COLLECTION_NAME].create_index([("owner_id", 1), ("email", 1)])
        database[ANALYSIS_HISTORY_COLLECTION_NAME].create_index("owner_id")
        database[ANALYSIS_HISTORY_COLLECTION_NAME].create_index([("owner_id", 1), ("customer_id", 1)])
        database[ANALYSIS_HISTORY_COLLECTION_NAME].create_index([("owner_id", 1), ("created_at", -1)])
        database[SUBSCRIPTION_COLLECTION_NAME].create_index("user_id")
        database[SUBSCRIPTION_COLLECTION_NAME].create_index("status")
        _mongodb_available = True
        _mongodb_client = client
        print(
            "[MONGO] Connection successful; "
            f"database={DATABASE_NAME}, user_collection={USER_COLLECTION_NAME}, "
            f"customer_collection={CUSTOMER_COLLECTION_NAME}"
        )
        return client
    except Exception as e:
        print(
            "[MONGO] Connection failed: "
            f"{_safe_mongodb_error(e)}; "
            f"error_type={type(e).__name__}; target_database={DATABASE_NAME}, "
            f"target_customer_collection={CUSTOMER_COLLECTION_NAME}, "
            f"target_user_collection={USER_COLLECTION_NAME}. Database access is unavailable."
        )
        _mongodb_available = False
        _last_connection_check = current_time
        return None

def get_database(client=None):
    """Return the configured application database from the shared client."""
    client = client or get_mongodb_client()
    return client[DATABASE_NAME] if client is not None and DATABASE_NAME else None

def get_collection(client=None, collection_name=None):
    """Return a configured application collection from the shared client."""
    database = get_database(client)
    collection_name = collection_name or CUSTOMER_COLLECTION_NAME
    return database[collection_name] if database is not None and collection_name else None

def get_customer_collection(client=None):
    return get_collection(client, CUSTOMER_COLLECTION_NAME)

def get_analysis_history_collection(client=None):
    return get_collection(client, ANALYSIS_HISTORY_COLLECTION_NAME)

def get_subscription_collection(client=None):
    return get_collection(client, SUBSCRIPTION_COLLECTION_NAME)

def get_user_collection(client=None):
    return get_collection(client, USER_COLLECTION_NAME)

def close_mongodb_client():
    """Close and clear the shared client, primarily for one-shot scripts."""
    global _mongodb_client, _mongodb_available
    if _mongodb_client is not None:
        _mongodb_client.close()
        _mongodb_client = None
    _mongodb_available = True

def get_customer_dataframe() -> pd.DataFrame:
    """
    Retrieves customer records from the configured MongoDB collection.
    The local CSV is used only when MongoDB cannot be reached in development.
    """
    client = get_mongodb_client()
    if client is not None:
        try:
            print("[OK] Fetching dataset from MongoDB Cloud...")
            collection = get_customer_collection(client)
            training_filter = {"record_type": {"$ne": "customer_profile"}}
            document_count = collection.count_documents(training_filter)
            print(
                "[INFO] MongoDB customer source: "
                f"database={DATABASE_NAME}, collection={CUSTOMER_COLLECTION_NAME}, "
                f"document_count={document_count}"
            )
            if document_count == 0:
                raise RuntimeError(
                    "Configured MongoDB customer collection is empty: "
                    f"database={DATABASE_NAME}, collection={CUSTOMER_COLLECTION_NAME}, "
                    "document_count=0. Seed the customers collection before training."
                )

            df = pd.DataFrame(list(collection.find(training_filter)))
            if not df.empty:
                if "_id" in df.columns:
                    df = df.drop(columns=["_id"])
                df.replace({"na": np.nan}, inplace=True)
                print(f"[OK] Successfully loaded {len(df)} records from MongoDB.")
                return df
        except Exception as e:
            if isinstance(e, RuntimeError) and "customer collection is empty" in str(e):
                raise
            print(
                "[WARN] MongoDB customer read failed; "
                f"error_type={type(e).__name__}. Falling back to local CSV only because "
                "MongoDB could not be read."
            )

    if is_production():
        raise RuntimeError("MongoDB is required for customer data in production.")

    # Fallback to local CSV for development only.
    csv_path = os.path.join("notebooks", "marketing_campaign.csv")
    if not os.path.exists(csv_path):
        # Resolve path relative to module location if running elsewhere
        csv_path = os.path.join(os.path.dirname(__file__), "..", "notebooks", "marketing_campaign.csv")
        
    if os.path.exists(csv_path):
        print(f"[OK] Loading dataset from local CSV file: {csv_path}")
        df = pd.read_csv(csv_path, sep="\t")
        if "_id" in df.columns:
            df = df.drop(columns=["_id"])
        df.replace({"na": np.nan}, inplace=True)
        return df
    else:
        raise FileNotFoundError(f"Could not find local CSV file at: {csv_path} and MongoDB connection failed.")
