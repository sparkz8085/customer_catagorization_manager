from typing import List
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError
from ml.predictor import predict_customer
from services.auth_session import verify_session_cookie

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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

@router.get("/")
async def predictGetRouteClient(request: Request):
    session_cookie = request.cookies.get("session")
    user = verify_session_cookie(session_cookie)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    try:
        return templates.TemplateResponse(
            request,
            "customer.html",
            {"context": None, "user_data": None, "cluster_averages": None, "error": None, "user": user},
        )
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "error": "Unable to render page."},
        )

CLUSTER_MAPPING = {
    0: "Budget",
    1: "Regular",
    2: "Premium",
    3: "Occasional"
}

CLUSTER_AVERAGES = {
    "Budget": {
        "Income": 32516.73,
        "Total_Spending": 59.57,
        "Wines": 22.62,
        "Fruits": 3.59,
        "Meat": 13.55,
        "Fish": 4.97,
        "Sweets": 3.75,
        "Gold": 11.09,
        "Web": 1.65,
        "Catalog": 0.34,
        "Store": 2.90,
        "Days_as_Customer": 4659.86,
        "Discount_Purchases": 1.73
    },
    "Regular": {
        "Income": 64326.89,
        "Total_Spending": 988.53,
        "Wines": 561.17,
        "Fruits": 41.34,
        "Meat": 215.33,
        "Fish": 53.69,
        "Sweets": 44.02,
        "Gold": 72.98,
        "Web": 6.68,
        "Catalog": 4.26,
        "Store": 8.72,
        "Days_as_Customer": 4790.19,
        "Discount_Purchases": 3.53
    },
    "Premium": {
        "Income": 76506.42,
        "Total_Spending": 1348.39,
        "Wines": 592.21,
        "Fruits": 64.34,
        "Meat": 455.79,
        "Fish": 95.90,
        "Sweets": 65.19,
        "Gold": 74.96,
        "Web": 4.86,
        "Catalog": 5.85,
        "Store": 8.26,
        "Days_as_Customer": 4699.26,
        "Discount_Purchases": 1.03
    },
    "Occasional": {
        "Income": 47458.73,
        "Total_Spending": 353.82,
        "Wines": 221.88,
        "Fruits": 8.65,
        "Meat": 63.04,
        "Fish": 13.08,
        "Sweets": 8.50,
        "Gold": 38.68,
        "Web": 4.94,
        "Catalog": 1.58,
        "Store": 5.22,
        "Days_as_Customer": 4763.66,
        "Discount_Purchases": 3.65
    }
}

@router.post("/")
async def predictRouteClient(request: Request):
    session_cookie = request.cookies.get("session")
    user = verify_session_cookie(session_cookie)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    try:
        customer_input = await parse_customer_input(request)
        input_data = customer_input.as_prediction_values()
        predicted_cluster = predict_customer(input_data)
        cluster_name = CLUSTER_MAPPING.get(predicted_cluster, str(predicted_cluster))
        
        user_data = customer_input.model_dump() if hasattr(customer_input, "model_dump") else customer_input.dict()

        return templates.TemplateResponse(
            request,
            "customer.html",
            {
                "context": cluster_name,
                "user_data": user_data,
                "cluster_averages": CLUSTER_AVERAGES,
                "error": None,
                "user": user
            },
        )

    except ValidationError:
        return templates.TemplateResponse(
            request,
            "customer.html",
            {
                "context": None,
                "user_data": None,
                "cluster_averages": None,
                "error": "Please enter valid non-negative customer values.",
                "user": user
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
                "user_data": None,
                "cluster_averages": None,
                "error": "Prediction failed. Check model storage and environment configuration.",
                "user": user
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
