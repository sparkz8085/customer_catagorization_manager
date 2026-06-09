import pandas as pd
import pymongo
import json
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL", "")

DATABASE = None
COLLECTION = None
MONGO_CLIENT = None

# Try to connect to MongoDB, but don't fail if connection fails
if MONGO_DB_URL and MONGO_DB_URL != "":
    try:
        # Try with SSL certificate verification
        MONGO_CLIENT = pymongo.MongoClient(
            MONGO_DB_URL,
            serverSelectionTimeoutMS=5000,
            retryWrites=True
        )
        
        # Test connection
        MONGO_CLIENT.admin.command('ping')
        DATABASE = MONGO_CLIENT["customer_db"]
        COLLECTION = DATABASE["marketing_records"]
        print("[OK] Successfully connected to MongoDB")
        
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        print("  Proceeding without MongoDB (data will be saved locally)")
        MONGO_CLIENT = None
else:
    print("[WARN] MONGO_DB_URL not set in .env file")
    print("  Proceeding without MongoDB (data will be saved locally)")

# Read and process data
try:
    df = pd.read_csv("notebooks/marketing_campaign.csv", sep="\t")
    df.reset_index(drop=True, inplace=True)

    json_record = list(json.loads(df.T.to_json()).values())

    # Try to insert into MongoDB if connected
    if COLLECTION is not None:
        try:
            COLLECTION.insert_many(json_record)
            print("[OK] Data successfully migrated to MongoDB Cloud Atlas!")
            print(f"  Inserted {len(json_record)} records")
        except Exception as e:
            print(f"[FAIL] Failed to insert data into MongoDB: {e}")
            print("  Saving data locally instead...")
            # Fallback: save to local JSON file
            with open("notebooks/data_backup.json", "w") as f:
                json.dump(json_record, f, indent=2)
            print("[OK] Data backed up to notebooks/data_backup.json")
    else:
        # No MongoDB connection, save locally
        with open("notebooks/data_backup.json", "w") as f:
            json.dump(json_record, f, indent=2)
        print("[OK] Data saved locally to notebooks/data_backup.json")
        print(f"  Total records: {len(json_record)}")
    
except Exception as e:
    print(f"[FAIL] Error during data processing: {e}")
    raise
    
finally:
    if MONGO_CLIENT is not None:
        MONGO_CLIENT.close()