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
        "owner_id": owner_email,
        "owner_email": owner_email,
        "updated_at": datetime.now(timezone.utc),
    }

    if customer_id:
        if not ObjectId.is_valid(customer_id):
            raise ValueError("Invalid customer id.")
        result = collection.update_one(
            {"_id": ObjectId(customer_id), "$or": [{"owner_id": owner_email}, {"owner_email": owner_email}]},
            {"$set": document},
        )
        if result.matched_count == 0:
            raise ValueError("Customer not found.")
        saved = collection.find_one({"_id": ObjectId(customer_id), "$or": [{"owner_id": owner_email}, {"owner_email": owner_email}]})
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
        {"_id": ObjectId(customer_id), "$or": [{"owner_id": owner_email}, {"owner_email": owner_email}]}
    )
    return _serialize_customer(customer) if customer else None

def list_customers(owner_id: str, search: str = "", page: int = 1, page_size: int = 25) -> dict:
    client = get_mongodb_client()
    if client is None:
        return {"items": [], "page": page, "page_size": page_size, "total": 0}
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    owner_filter = {"$or": [{"owner_id": owner_id}, {"owner_email": owner_id}]}
    if search:
        owner_filter["$and"] = [{"$or": [
            {"Customer Name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"customer_id": {"$regex": search, "$options": "i"}},
        ]}]
    collection = get_customer_collection(client)
    total = collection.count_documents(owner_filter)
    items = list(collection.find(owner_filter).sort("updated_at", -1).skip((page - 1) * page_size).limit(page_size))
    return {"items": [_serialize_customer(item) for item in items], "page": page, "page_size": page_size, "total": total}

def delete_customer(customer_id: str, owner_id: str) -> bool:
    if not ObjectId.is_valid(customer_id):
        return False
    client = get_mongodb_client()
    if client is None:
        return False
    result = get_customer_collection(client).delete_one(
        {"_id": ObjectId(customer_id), "$or": [{"owner_id": owner_id}, {"owner_email": owner_id}]}
    )
    return result.deleted_count == 1

def get_customer_summary(owner_id: str) -> dict:
    client = get_mongodb_client()
    if client is None:
        return {"total": 0, "analyzed": 0, "pending": 0, "segments": {}}
    collection = get_customer_collection(client)
    owner_filter = {"$or": [{"owner_id": owner_id}, {"owner_email": owner_id}]}
    total = collection.count_documents(owner_filter)
    analyzed = collection.count_documents({**owner_filter, "predicted_category": {"$exists": True, "$ne": None}})
    segments = {row["_id"]: row["count"] for row in collection.aggregate([
        {"$match": {**owner_filter, "predicted_category": {"$exists": True}}},
        {"$group": {"_id": "$predicted_category", "count": {"$sum": 1}}},
    ])}
    return {"total": total, "analyzed": analyzed, "pending": max(total - analyzed, 0), "segments": segments}

def ensure_indexes() -> None:
    client = get_mongodb_client()
    if client is None:
        return
    collection = get_customer_collection(client)
    collection.create_index("owner_id")
    collection.create_index([("owner_id", 1), ("customer_id", 1)])
    collection.create_index([("owner_id", 1), ("email", 1)])