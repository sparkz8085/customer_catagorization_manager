import os
import hmac
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import PLAN_CONFIG
from database.connection import get_mongodb_client, get_user_collection
from services.auth_session import session_owner_id, verify_session_cookie
from services.subscriptions import current_subscription, pending_upgrade

router = APIRouter()
templates = Jinja2Templates(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates")))


def _user(request: Request) -> dict:
    user = verify_session_cookie(request.cookies.get("session"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user


@router.get("/subscription", response_class=HTMLResponse)
async def subscription_page(request: Request):
    user = _user(request)
    return templates.TemplateResponse(request, "subscription.html", {
        "user": user,
        "subscription": current_subscription(user),
        "plans": PLAN_CONFIG,
    })


@router.get("/api/subscription")
async def subscription_state(request: Request):
    return current_subscription(_user(request))


@router.post("/api/subscription/upgrade")
async def submit_upgrade(request: Request):
    user = _user(request)
    body = await request.json()
    try:
        subscription = pending_upgrade(user, str(body.get("plan", "")), str(body.get("payment_reference", "")))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    client = get_mongodb_client()
    if client is None:
        raise HTTPException(status_code=503, detail="Subscription storage is unavailable.")
    get_user_collection(client).update_one({"_id": user.get("_id")} if user.get("_id") else {"email": user["email"]}, {"$set": {"subscription": subscription}})
    return {"status": "pending", "message": "Payment submitted for manual verification.", "subscription": subscription}


@router.post("/api/admin/subscriptions/{email}/verify")
async def verify_payment(request: Request, email: str):
    admin_key = os.getenv("PAYMENT_ADMIN_KEY", "")
    supplied_key = request.headers.get("x-payment-admin-key", "")
    if not admin_key or not hmac.compare_digest(supplied_key, admin_key):
        raise HTTPException(status_code=403, detail="Payment verification is restricted.")
    body = await request.json()
    plan = str(body.get("plan", ""))
    if plan not in {"professional", "enterprise"}:
        raise HTTPException(status_code=422, detail="Invalid paid plan.")
    client = get_mongodb_client()
    if client is None:
        raise HTTPException(status_code=503, detail="Subscription storage is unavailable.")
    subscription = {"plan": plan, "status": "active", "payment_status": "verified", "verified_at": datetime.now(timezone.utc).isoformat()}
    result = get_user_collection(client).update_one({"email": email.lower()}, {"$set": {"subscription": subscription}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"status": "active", "subscription": subscription}