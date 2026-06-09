from typing import List
from fastapi import APIRouter, Request, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError
from ml.predictor import predict_customer

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
    try:
        return templates.TemplateResponse(
            request,
            "customer.html",
            {"context": None, "error": None},
        )
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "error": "Unable to render page."},
        )

CLUSTER_MAPPING = {
    0: "Budget-Conscious Families",
    1: "Deal-Hunting Loyalists",
    2: "Affluent VIP Customers"
}

@router.post("/")
async def predictRouteClient(request: Request):
    try:
        customer_input = await parse_customer_input(request)
        input_data = customer_input.as_prediction_values()
        predicted_cluster = predict_customer(input_data)
        cluster_name = CLUSTER_MAPPING.get(predicted_cluster, str(predicted_cluster))

        return templates.TemplateResponse(
            request,
            "customer.html",
            {"context": cluster_name, "error": None},
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
