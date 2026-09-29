import os

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from database.analysis_store import get_analysis, list_analyses
from database.customer_store import delete_customer, get_customer_summary, list_customers, save_customer
from routes.prediction import CustomerInput
from services.auth_session import session_owner_id, verify_session_cookie

router = APIRouter()
templates = Jinja2Templates(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates")))


def _user(request: Request) -> dict:
    user = verify_session_cookie(request.cookies.get("session"))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user


def _customer_payload(payload: dict) -> dict:
    allowed = set(CustomerInput.model_fields.keys())
    data = {key: value for key, value in payload.items() if key in allowed or key in {"Customer Name", "email", "phone", "customer_id"}}
    validated = CustomerInput(**{key: value for key, value in data.items() if key in allowed})
    normalized = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
    for key in ("Customer Name", "email", "phone", "customer_id"):
        if key in data:
            normalized[key] = data[key]
    return normalized


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = _user(request)
    owner_id = session_owner_id(user)
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": user,
        "summary": get_customer_summary(owner_id),
        "customers": list_customers(owner_id, page_size=8)["items"],
        "history": list_analyses(owner_id, page_size=8)["items"],
    })


@router.get("/customers", response_class=HTMLResponse)
async def customer_management_page(request: Request, search: str = ""):
    user = _user(request)
    return templates.TemplateResponse(request, "customers.html", {
        "user": user,
        "customers": list_customers(session_owner_id(user), search=search, page_size=100)["items"],
        "search": search,
    })


@router.get("/analysis-history", response_class=HTMLResponse)
async def analysis_history_page(request: Request):
    user = _user(request)
    return templates.TemplateResponse(request, "analysis_history.html", {
        "user": user,
        "history": list_analyses(session_owner_id(user), page_size=100)["items"],
    })


@router.get("/api/customers")
async def customers(request: Request, search: str = "", page: int = 1, page_size: int = 25):
    user = _user(request)
    return list_customers(session_owner_id(user), search=search, page=page, page_size=page_size)


@router.post("/api/customers")
async def create_customer(request: Request):
    user = _user(request)
    try:
        customer = save_customer(_customer_payload(await request.json()), session_owner_id(user))
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not customer:
        return JSONResponse(status_code=503, content={"detail": "Customer storage is unavailable."})
    return customer


@router.put("/api/customers/{customer_id}")
async def update_customer(request: Request, customer_id: str):
    user = _user(request)
    try:
        customer = save_customer(_customer_payload(await request.json()), session_owner_id(user), customer_id)
    except (ValidationError, ValueError) as exc:
        raise HTTPException(status_code=404 if "not found" in str(exc).lower() else 422, detail=str(exc)) from exc
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.delete("/api/customers/{customer_id}")
async def remove_customer(request: Request, customer_id: str):
    user = _user(request)
    if not delete_customer(customer_id, session_owner_id(user)):
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "deleted"}


@router.get("/api/analysis-history")
async def analysis_history(request: Request, customer_id: str | None = None, page: int = 1, page_size: int = 25):
    user = _user(request)
    return list_analyses(session_owner_id(user), customer_id=customer_id, page=page, page_size=page_size)


@router.get("/api/analysis-history/{analysis_id}")
async def analysis_detail(request: Request, analysis_id: str):
    user = _user(request)
    analysis = get_analysis(analysis_id, session_owner_id(user))
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis