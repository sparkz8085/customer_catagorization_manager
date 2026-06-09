import os
import certifi
import pymongo
import numpy as np
import pandas as pd
from config import MONGO_DB_URL_KEY, DATABASE_NAME, COLLECTION_NAME

ca = certifi.where()

def get_mongodb_client():
    """
    Attempts to connect to MongoDB Atlas database.
    Returns MongoClient object or None if connection fails or is not configured.
    """
    mongo_db_url = os.getenv(MONGO_DB_URL_KEY)
    if not mongo_db_url:
        print("[WARN] MongoDB connection URL (MONGO_DB_URL) not found in env.")
        return None
    try:
        client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return None

def get_customer_dataframe() -> pd.DataFrame:
    """
    Retrieves the customer records from MongoDB database,
    falling back to the local CSV dataset if the database is unavailable.
    """
    client = get_mongodb_client()
    if client is not None:
        try:
            print("[OK] Fetching dataset from MongoDB Cloud...")
            db = client[DATABASE_NAME]
            collection = db[COLLECTION_NAME]
            df = pd.DataFrame(list(collection.find()))
            if not df.empty:
                if "_id" in df.columns:
                    df = df.drop(columns=["_id"])
                df.replace({"na": np.nan}, inplace=True)
                print(f"[OK] Successfully loaded {len(df)} records from MongoDB.")
                return df
            else:
                print("[WARN] MongoDB collection is empty. Falling back to local CSV...")
        except Exception as e:
            print(f"[WARN] Error fetching from MongoDB ({e}). Falling back to local CSV...")
        finally:
            client.close()
            
    # Fallback to local CSV
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
