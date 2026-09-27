from datetime import datetime, timezone

from bson import ObjectId

from database.connection import get_customer_collection, get_mongodb_client


def _serialize_customer(customer: dict) -> dict:
    if "_id" in customer:
        customer["_id"] = str(customer["_id"])
    return customer


def save_customer(customer_data: dict, owner_email: str, customer_id: str | None = None) -> dict | None:
    client = get_mongodb_client()
    if client is None:
        return None

    collection = get_customer_collection(client)
    document = {
        **customer_data,
        "record_type": "customer_profile",
        "owner_email": owner_email,
        "updated_at": datetime.now(timezone.utc),
    }

    if customer_id:
        if not ObjectId.is_valid(customer_id):
            raise ValueError("Invalid customer id.")
        result = collection.update_one(
            {"_id": ObjectId(customer_id), "owner_email": owner_email},
            {"$set": document},
        )
        if result.matched_count == 0:
            raise ValueError("Customer not found.")
        saved = collection.find_one({"_id": ObjectId(customer_id), "owner_email": owner_email})
    else:
        document["created_at"] = document["updated_at"]
        result = collection.insert_one(document)
        saved = collection.find_one({"_id": result.inserted_id})

    return _serialize_customer(saved) if saved else None


def get_customer(customer_id: str, owner_email: str) -> dict | None:
    if not ObjectId.is_valid(customer_id):
        return None
    client = get_mongodb_client()
    if client is None:
        return None
    customer = get_customer_collection(client).find_one(
        {"_id": ObjectId(customer_id), "owner_email": owner_email}
    )
    return _serialize_customer(customer) if customer else None