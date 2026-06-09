import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.staticfiles import StaticFiles

from config import APP_HOST, APP_PORT
from routes.prediction import router as prediction_router
from routes.training import router as training_router

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
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "script-src 'self' https://code.jquery.com; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    return response

# Register routers
app.include_router(prediction_router)
app.include_router(training_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)
