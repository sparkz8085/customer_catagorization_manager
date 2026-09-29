from datetime import datetime, timezone

from bson import ObjectId

from database.connection import get_analysis_history_collection, get_mongodb_client


def _serialize(document: dict | None) -> dict | None:
    if not document:
        return None
    document["_id"] = str(document["_id"])
    return document


def record_analysis(owner_id: str, customer_id: str, model: str, result: dict, input_snapshot: dict) -> dict | None:
    client = get_mongodb_client()
    if client is None:
        return None
    now = datetime.now(timezone.utc)
    document = {
        "owner_id": owner_id,
        "customer_id": customer_id,
        "model": model,
        "result": result,
        "input_snapshot": input_snapshot,
        "created_at": now,
        "updated_at": now,
    }
    saved = get_analysis_history_collection(client).insert_one(document)
    document["_id"] = saved.inserted_id
    return _serialize(document)


def list_analyses(owner_id: str, customer_id: str | None = None, page: int = 1, page_size: int = 25) -> dict:
    client = get_mongodb_client()
    if client is None:
        return {"items": [], "page": page, "page_size": page_size, "total": 0}
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    query = {"owner_id": owner_id}
    if customer_id:
        query["customer_id"] = customer_id
    collection = get_analysis_history_collection(client)
    total = collection.count_documents(query)
    items = list(collection.find(query).sort("created_at", -1).skip((page - 1) * page_size).limit(page_size))
    return {"items": [_serialize(item) for item in items], "page": page, "page_size": page_size, "total": total}


def get_analysis(analysis_id: str, owner_id: str) -> dict | None:
    if not ObjectId.is_valid(analysis_id):
        return None
    client = get_mongodb_client()
    if client is None:
        return None
    document = get_analysis_history_collection(client).find_one({"_id": ObjectId(analysis_id), "owner_id": owner_id})
    return _serialize(document)


def ensure_indexes() -> None:
    client = get_mongodb_client()
    if client is None:
        return
    collection = get_analysis_history_collection(client)
    collection.create_index("owner_id")
    collection.create_index([("owner_id", 1), ("customer_id", 1)])
    collection.create_index([("owner_id", 1), ("created_at", -1)])