import os
import math
import time
import threading
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.staticfiles import StaticFiles

from config import APP_HOST, APP_PORT
from routes.prediction import router as prediction_router
from routes.training import router as training_router
from routes.auth import router as auth_router
from routes.bulk import router as bulk_router
from routes.management import router as management_router
from routes.subscription import router as subscription_router

import warnings
warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent

def get_allowed_origins() -> List[str]:
    origins = os.getenv("CORS_ORIGINS", "")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]

app = FastAPI(title="Customer Categorizer", docs_url=None, redoc_url=None)
origins = get_allowed_origins()

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=bool(origins),
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# Per-process baseline rate limits for authentication endpoints.
# For multi-instance/serverless production, use a shared Redis/API-gateway limiter as well.
_AUTH_RATE_LIMITS = {
    ("POST", "/login/email"): (8, 15 * 60),
    ("POST", "/register"): (5, 60 * 60),
    ("GET", "/auth/mock-callback"): (8, 15 * 60),
    ("GET", "/login/google"): (10, 15 * 60),
    ("GET", "/login/facebook"): (10, 15 * 60),
    ("GET", "/auth/callback/google"): (10, 15 * 60),
    ("GET", "/auth/callback/facebook"): (10, 15 * 60),
}
_AUTH_RATE_BUCKETS = {}
_AUTH_RATE_LOCK = threading.Lock()


def _rate_limit_client_key(request: Request) -> str:
    # Only trust forwarding headers when deployment is behind a configured trusted proxy.
    trust_proxy = os.getenv("TRUST_PROXY_HEADERS", "").lower() in {"1", "true", "yes"}
    forwarded_for = request.headers.get("x-forwarded-for", "") if trust_proxy else ""
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip() or "unknown"
    return request.client.host if request.client else "unknown"


def _consume_auth_rate_limit(request: Request) -> int | None:
    limit = _AUTH_RATE_LIMITS.get((request.method, request.url.path))
    if not limit:
        return None
    max_requests, window_seconds = limit
    now = time.monotonic()
    key = (request.url.path, _rate_limit_client_key(request))
    with _AUTH_RATE_LOCK:
        timestamps = [stamp for stamp in _AUTH_RATE_BUCKETS.get(key, []) if now - stamp < window_seconds]
        if len(timestamps) >= max_requests:
            _AUTH_RATE_BUCKETS[key] = timestamps
            return max(1, math.ceil(window_seconds - (now - timestamps[0])))
        timestamps.append(now)
        _AUTH_RATE_BUCKETS[key] = timestamps
        # Bound memory usage under many distinct client IPs.
        if len(_AUTH_RATE_BUCKETS) > 5000:
            _AUTH_RATE_BUCKETS.clear()
    return None


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    retry_after = _consume_auth_rate_limit(request)
    if retry_after is not None:
        response = JSONResponse(
            status_code=429,
            content={"status": False, "message": "Too many authentication attempts. Please try again later."},
            headers={"Retry-After": str(retry_after)},
        )
    elif request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.cookies.get("session"):
        origin = request.headers.get("origin")
        expected_origin = f"{request.url.scheme}://{request.url.netloc}"
        if origin and origin.rstrip("/") != expected_origin.rstrip("/"):
            response = JSONResponse(status_code=403, content={"status": False, "message": "Cross-origin request rejected."})
        else:
            response = await call_next(request)
    else:
        response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data: https://lh3.googleusercontent.com https://graph.facebook.com https://platform-lookaside.fbsbx.com https://images.unsplash.com https://api.dicebear.com; "
        "style-src 'self' https://cdn.jsdelivr.net https://fonts.googleapis.com 'unsafe-inline'; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    return response

# Register routers
app.include_router(auth_router)
app.include_router(prediction_router)
app.include_router(training_router)
app.include_router(bulk_router)
app.include_router(management_router)
app.include_router(subscription_router)

import logging
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Global Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": False, "message": "An unexpected internal server error occurred."}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)
