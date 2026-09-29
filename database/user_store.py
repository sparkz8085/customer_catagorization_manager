import os
import json
import datetime
import bcrypt
from database.connection import get_mongodb_client, get_user_collection
from config import is_production

def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    # bcrypt expects bytes, so we encode strings
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    # Hash password and return as string
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# Local database file path
LOCAL_USERS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "users.json"))

def _load_local_users() -> dict:
    """Loads users from the local JSON file fallback."""
    if not os.path.exists(LOCAL_USERS_FILE):
        return {}
    try:
        with open(LOCAL_USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Error reading local users file: {e}")
        return {}

def _save_local_users(users: dict):
    """Saves users to the local JSON file fallback."""
    try:
        os.makedirs(os.path.dirname(LOCAL_USERS_FILE), exist_ok=True)
        with open(LOCAL_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4, default=str)
    except Exception as e:
        print(f"[WARN] Error saving local users file: {e}")

def get_user_by_email(email: str) -> dict | None:
    """
    Finds a user profile by email address.
    Checks MongoDB, falling back to the local users.json if unavailable.
    """
    if not email:
        return None

    email_lower = email.lower()
    
    # Try MongoDB first
    client = get_mongodb_client()
    if client is not None:
        try:
            collection = get_user_collection(client)
            user = collection.find_one({"email": email_lower})
            if user:
                # Remove MongoDB ObjectId for session serialization
                if "_id" in user:
                    user["_id"] = str(user["_id"])
                return user
        except Exception as e:
            raise RuntimeError(
                "[MONGO] User query failed; local JSON fallback is disabled after "
                f"a successful connection (error_type={type(e).__name__})."
            ) from e

    if is_production():
        return None
    print("[MONGO] MongoDB unavailable - using local users.json fallback")
    users = _load_local_users()
    return users.get(email_lower)

def create_user_with_password(email: str, name: str, nickname: str, plain_password: str) -> dict | None:
    """
    Creates a standard user with an email and hashed password. 
    Returns None if email already exists.
    """
    email_lower = email.lower()
    
    # Check if user already exists
    existing_user = get_user_by_email(email_lower)
    if existing_user:
        return None

    hashed_password = get_password_hash(plain_password)
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    avatar_url = f"https://api.dicebear.com/7.x/initials/svg?seed={name}"
    
    user_data = {
        "email": email_lower,
        "name": name,
        "avatar_url": avatar_url,
        "provider": "email",
        "provider_uid": email_lower,
        "created_at": now_str,
        "last_login": now_str,
        "nickname": nickname,
        "password": hashed_password,
        "subscription": {"plan": "starter", "status": "active", "payment_status": "not_required"},
    }
    
    # Try MongoDB first
    client = get_mongodb_client()
    if client is not None:
        try:
            collection = get_user_collection(client)
            result = collection.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            print(f"[MONGO] User inserted successfully; email={email_lower}")
            return user_data
        except Exception as e:
            raise RuntimeError(
                "[MONGO] User insert failed; local JSON fallback is disabled after "
                f"a successful connection (error_type={type(e).__name__})."
            ) from e

    if is_production():
        raise RuntimeError("MongoDB is required for user storage in production.")

    # Fallback to local JSON for development only.
    print("[MONGO] MongoDB unavailable - using local users.json fallback")
    users = _load_local_users()
    users[email_lower] = user_data
    _save_local_users(users)
    return user_data

def upsert_user(provider: str, provider_uid: str, email: str, name: str, avatar_url: str, nickname: str = None, password: str = None) -> dict:
    """
    Creates or updates a user profile.
    Saves to MongoDB, falling back to local users.json if MongoDB is unavailable.
    Returns the user document.
    """
    email_lower = email.lower()
    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Check if user already exists to preserve created_at
    existing_user = get_user_by_email(email_lower)
    created_at = existing_user.get("created_at") if existing_user else now_str
    
    # Preserve existing nickname/password if not provided in the current call
    final_nickname = nickname if nickname is not None else (existing_user.get("nickname") if existing_user else None)
    final_password = password if password is not None else (existing_user.get("password") if existing_user else None)
    final_subscription = existing_user.get("subscription") if existing_user else None
    
    user_data = {
        "email": email_lower,
        "name": name,
        "avatar_url": avatar_url,
        "provider": provider,
        "provider_uid": provider_uid,
        "created_at": created_at,
        "last_login": now_str,
        "nickname": final_nickname,
        "password": final_password,
        "subscription": final_subscription or {"plan": "starter", "status": "active", "payment_status": "not_required"},
    }
    
    # Try MongoDB first
    client = get_mongodb_client()
    if client is not None:
        try:
            collection = get_user_collection(client)
            collection.update_one(
                {"email": email_lower},
                {"$set": user_data},
                upsert=True
            )
            # Fetch back the saved document to return
            saved_user = collection.find_one({"email": email_lower})
            if saved_user:
                if "_id" in saved_user:
                    saved_user["_id"] = str(saved_user["_id"])
                print(f"[MONGO] User upserted successfully; email={email_lower}")
                return saved_user
            raise RuntimeError(
                "MongoDB user upsert completed but the saved user could not be read back."
            )
        except Exception as e:
            raise RuntimeError(
                "[MONGO] User upsert failed; local JSON fallback is disabled after "
                f"a successful connection (error_type={type(e).__name__})."
            ) from e

    if is_production():
        raise RuntimeError("MongoDB is required for user storage in production.")

    # Fallback to local JSON for development only.
    print("[MONGO] MongoDB unavailable - using local users.json fallback")
    users = _load_local_users()
    users[email_lower] = user_data
    _save_local_users(users)
    return user_data
