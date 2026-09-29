from datetime import datetime, timezone

from config import PLAN_CONFIG


def current_subscription(user: dict) -> dict:
    subscription = user.get("subscription") or {}
    return {
        "plan": subscription.get("plan", "starter"),
        "status": subscription.get("status", "active"),
        "payment_status": subscription.get("payment_status", "not_required"),
        "started_at": subscription.get("started_at"),
        "expires_at": subscription.get("expires_at"),
    }


def has_feature(user: dict, feature: str) -> bool:
    subscription = current_subscription(user)
    if subscription["status"] != "active":
        return False
    return feature in PLAN_CONFIG.get(subscription["plan"], PLAN_CONFIG["starter"])["features"]


def pending_upgrade(user: dict, plan: str, payment_reference: str) -> dict:
    if plan not in {"professional", "enterprise"}:
        raise ValueError("Only Professional and Enterprise plans require payment verification.")
    if not payment_reference.strip():
        raise ValueError("A payment reference is required.")
    now = datetime.now(timezone.utc).isoformat()
    return {
        "plan": plan,
        "status": "pending",
        "payment_status": "pending_verification",
        "payment_reference": payment_reference.strip(),
        "started_at": now,
        "expires_at": None,
    }