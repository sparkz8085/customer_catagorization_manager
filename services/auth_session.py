import hmac
import hashlib
import json
import base64
import os
import logging
import secrets
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load secret key from environment or fallback with warning
SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("APP_ENV", "").lower() in {"prod", "production"}:
        raise RuntimeError("SESSION_SECRET_KEY must be set in production.")
    logger.warning("SESSION_SECRET_KEY is not set; using a generated development-only session key.")
    SECRET_KEY = secrets.token_urlsafe(32)

def _sign_data(data: str) -> str:
    """Creates a SHA256 HMAC signature of the data string."""
    signature = hmac.new(SECRET_KEY.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode('utf-8').rstrip("=")

def create_session_cookie(payload: dict) -> str:
    """
    Serializes payload into JSON, base64 encodes it, and appends an HMAC signature.
    Returns: A signed session string formatted as: {encoded_payload}.{signature}
    """
    try:
        safe_payload = {
            key: value for key, value in payload.items()
            if key not in {"password", "hashed_password", "access_token"}
        }
        safe_payload["iat"] = int(time.time())
        safe_payload["exp"] = int(time.time()) + 60 * 60 * 24 * 30
        serialized = json.dumps(safe_payload)
        encoded = base64.urlsafe_b64encode(serialized.encode('utf-8')).decode('utf-8').rstrip("=")
        signature = _sign_data(encoded)
        return f"{encoded}.{signature}"
    except Exception as e:
        logger.error(f"Error creating session cookie: {e}")
        return ""

def verify_session_cookie(cookie_value: str) -> dict | None:
    """
    Verifies the signature of the cookie value and decodes the payload back to a dict.
    Returns: The decoded session dict if valid, else None.
    """
    if not cookie_value:
        return None
    try:
        parts = cookie_value.split(".")
        if len(parts) != 2:
            return None
        encoded_payload, signature = parts
        
        # Verify signature matches
        expected_signature = _sign_data(encoded_payload)
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid session cookie signature detected!")
            return None
            
        # Decode payload
        # Pad base64 encoded string if needed
        padding_needed = len(encoded_payload) % 4
        if padding_needed:
            encoded_payload += "=" * (4 - padding_needed)
            
        decoded_bytes = base64.urlsafe_b64decode(encoded_payload)
        payload = json.loads(decoded_bytes.decode('utf-8'))
        if not isinstance(payload, dict):
            return None
        if payload.get("exp", 0) and int(payload["exp"]) < int(time.time()):
            return None
        return payload
    except Exception as e:
        logger.error(f"Failed to verify or decode session cookie: {e}")
        return None

def session_owner_id(user: dict) -> str:
    """Return the server-derived stable owner key used by scoped data queries."""
    return str(user.get("_id") or user.get("email") or "")
