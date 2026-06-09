import os
from pathlib import Path
from typing import List

from fastapi import FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from uvicorn import run as app_run
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError

from config import APP_HOST, APP_PORT

import warnings
warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent

def get_allowed_origins() -> List[str]:
    origins = os.getenv("CORS_ORIGINS", "")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]

app = FastAPI(title="Customer Categorizer", docs_url=None, redoc_url=None)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
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

class CustomerInput(BaseModel):
    Age: int = Field(ge=0, le=120)
    Education: int = Field(ge=0, le=4)
    Marital_Status: int = Field(ge=0, le=1)
    Parental_Status: int = Field(ge=0, le=1)
    Children: int = Field(ge=0, le=20)
    Income: float = Field(ge=0)
    Total_Spending: float = Field(ge=0)
    Days_as_Customer: int = Field(ge=0)
    Recency: int = Field(ge=0)
    Wines: int = Field(ge=0)
    Fruits: int = Field(ge=0)
    Meat: int = Field(ge=0)
    Fish: float = Field(ge=0)
    Sweets: int = Field(ge=0)
    Gold: float = Field(ge=0)
    Web: int = Field(ge=0)
    Catalog: int = Field(ge=0)
    Store: int = Field(ge=0)
    Discount_Purchases: int = Field(ge=0)
    Total_Promo: int = Field(ge=0)
    NumWebVisitsMonth: int = Field(ge=0)

    def as_prediction_values(self) -> List[object]:
        data = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        fields = ["Age", "Education", "Marital_Status", "Parental_Status", "Children", "Income",
                  "Total_Spending", "Days_as_Customer", "Recency", "Wines", "Fruits", "Meat",
                  "Fish", "Sweets", "Gold", "Web", "Catalog", "Store", "Discount_Purchases",
                  "Total_Promo", "NumWebVisitsMonth"]
        return [data[field] for field in fields]

async def parse_customer_input(request: Request) -> CustomerInput:
    form = await request.form()
    fields = ["Age", "Education", "Marital_Status", "Parental_Status", "Children", "Income",
              "Total_Spending", "Days_as_Customer", "Recency", "Wines", "Fruits", "Meat",
              "Fish", "Sweets", "Gold", "Web", "Catalog", "Store", "Discount_Purchases",
              "Total_Promo", "NumWebVisitsMonth"]
    payload = {field: form.get(field) for field in fields}
    return CustomerInput(**payload)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/train")
async def trainRouteClient(x_training_api_key: str = Header(default="")):
    expected_key = os.getenv("TRAINING_API_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training is disabled in this environment.",
        )
    if x_training_api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        from services.training import train_model
        train_model()
        return Response("Training successful !!")
    except Exception as e:
        import logging as app_logging
        app_logging.exception("Training failed:")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "error": f"Training failed: {str(e)}"},
        )

@app.get("/")
async def predictGetRouteClient(request: Request):
    try:
        return templates.TemplateResponse(
            request,
            "customer.html",
            {"context": None, "error": None},
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "error": "Unable to render page."},
        )

@app.post("/")
async def predictRouteClient(request: Request):
    try:
        customer_input = await parse_customer_input(request)
        input_data = customer_input.as_prediction_values()
        
        from services.prediction import predict_customer
        predicted_cluster = predict_customer(input_data)

        return templates.TemplateResponse(
            request,
            "customer.html",
            {"context": predicted_cluster, "error": None},
        )

    except ValidationError:
        return templates.TemplateResponse(
            request,
            "customer.html",
            {
                "context": None,
                "error": "Please enter valid non-negative customer values.",
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    except Exception as e:
        import logging as app_logging
        app_logging.exception("Prediction failed with error:")
        return templates.TemplateResponse(
            request,
            "customer.html",
            {
                "context": None,
                "error": "Prediction failed. Check model storage and environment configuration.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

if __name__ == "__main__":
    app_run(app, host=APP_HOST, port=APP_PORT)
