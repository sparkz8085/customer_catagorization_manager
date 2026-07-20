import os
import io
import uuid
import pandas as pd
from typing import Dict, Any
from fastapi import APIRouter, Request, status, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import time
from services.auth_session import verify_session_cookie
from routes.prediction import CLUSTER_MAPPING, CustomerInput
import logging
from ml.predictor import predict_customer

logger = logging.getLogger(__name__)

router = APIRouter()
templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
templates = Jinja2Templates(directory=templates_dir)

# Simple in-memory storage for bulk sessions. In production, use MongoDB or Redis.
BULK_SESSIONS: Dict[str, Any] = {}

@router.get("/bulk-upload")
async def bulk_upload_page(request: Request):
    session_cookie = request.cookies.get("session")
    user = verify_session_cookie(session_cookie)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse(
        request,
        "bulk_upload.html",
        {"user": user}
    )

@router.post("/api/bulk-upload")
async def api_bulk_upload(request: Request, file: UploadFile = File(...)):
    session_cookie = request.cookies.get("session")
    user = verify_session_cookie(session_cookie)
    if not user:
        return JSONResponse(status_code=401, content={"status": "error", "message": "Unauthorized", "detail": "User not authenticated."})
        
    if not file.filename:
        return JSONResponse(status_code=400, content={"status": "error", "message": "No file selected."})
        
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".xls", ".xlsx"]:
        return JSONResponse(status_code=400, content={"status": "error", "message": f"Unsupported file format '{ext}'. Please upload CSV or Excel."})
        
    try:
        logger.info(f"Starting processing for bulk upload file: {file.filename}")
        contents = await file.read()
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
            
        if df.empty:
            return JSONResponse(status_code=400, content={"status": "error", "message": "The uploaded file is empty."})
            
        # Ensure column headers are strings to prevent AttributeError on .str operations
        df.columns = df.columns.astype(str).str.strip().str.lower()
        
        # Check for duplicate headers
        if len(df.columns) != len(set(df.columns)):
            return JSONResponse(status_code=400, content={"status": "error", "message": "File contains duplicate column headers."})
        
        # Simple Column Mapping logic
        mapping = {
            "customer name": "Customer Name",
            "name": "Customer Name",
            "age": "Age",
            "gender": "Gender",
            "annual income": "Income",
            "income": "Income",
            "income (usd)": "Income",
            "spending score": "Total_Spending",
            "spending": "Total_Spending"
        }
        
        # Rename matching columns
        new_cols = {}
        for col in df.columns:
            if col in mapping:
                new_cols[col] = mapping[col]
            else:
                new_cols[col] = col.title()
        df.rename(columns=new_cols, inplace=True)
        
        # Validate that essential columns exist
        required_columns = ["Income", "Total_Spending"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return JSONResponse(status_code=400, content={"status": "error", "message": f"Missing required columns: {', '.join(missing_columns)}."})
            
        start_time = time.time()
        
        results = []
        success_count = 0
        failed_count = 0
        category_counts = {}
        
        for idx, row in df.iterrows():
            try:
                # Build payload, falling back to defaults if missing
                payload = {}
                for field in CustomerInput.model_fields.keys():
                    if field in row and pd.notna(row[field]):
                        # Validate no negative values for financial/metric fields
                        val = row[field]
                        if isinstance(val, (int, float)) and val < 0:
                            raise ValueError(f"Field '{field}' cannot be negative.")
                        payload[field] = val
                        
                customer_input = CustomerInput(**payload)
                input_data = customer_input.as_prediction_values()
                
                # Predict
                predicted_cluster = predict_customer(input_data)
                category = CLUSTER_MAPPING.get(predicted_cluster, str(predicted_cluster))
                
                customer_name = row.get("Customer Name", f"Customer_{idx+1}")
                if pd.isna(customer_name):
                    customer_name = f"Customer_{idx+1}"
                    
                age = row.get("Age", "N/A")
                income = row.get("Income", payload.get("Income", "N/A"))
                spending = row.get("Total_Spending", payload.get("Total_Spending", "N/A"))
                
                results.append({
                    "row_index": idx + 1,
                    "Customer Name": customer_name,
                    "Age": age,
                    "Income": income,
                    "Spending Score": spending,
                    "Predicted Category": category,
                    "Status": "Success",
                    "Remarks": ""
                })
                success_count += 1
                category_counts[category] = category_counts.get(category, 0) + 1
                
            except Exception as e:
                failed_count += 1
                customer_name = row.get("Customer Name", f"Row_{idx+1}")
                if pd.isna(customer_name):
                    customer_name = f"Row_{idx+1}"
                results.append({
                    "row_index": idx + 1,
                    "Customer Name": customer_name,
                    "Age": row.get("Age", "N/A"),
                    "Income": row.get("Income", "N/A"),
                    "Spending Score": row.get("Total_Spending", "N/A"),
                    "Predicted Category": "N/A",
                    "Status": "Failed",
                    "Remarks": str(e)
                })
                
        processing_time = round(time.time() - start_time, 2)
        
        bulk_id = str(uuid.uuid4())
        BULK_SESSIONS[bulk_id] = {
            "id": bulk_id,
            "filename": file.filename,
            "total": len(df),
            "success": success_count,
            "failed": failed_count,
            "processing_time": processing_time,
            "category_counts": category_counts,
            "results": results
        }
        
        logger.info(f"Completed bulk upload '{file.filename}'. Total: {len(df)}, Success: {success_count}, Failed: {failed_count}")
        return {"status": "success", "bulk_id": bulk_id}
        
    except pd.errors.EmptyDataError:
        logger.error(f"Failed to read file {file.filename}: File is completely empty.")
        return JSONResponse(status_code=400, content={"status": "error", "message": "The uploaded file is empty or corrupted."})
    except Exception as e:
        logger.error(f"Exception during bulk upload: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"status": "error", "message": "An error occurred while processing the file.", "detail": str(e)})

@router.get("/api/bulk-results/{bulk_id}")
async def get_bulk_results(bulk_id: str):
    if bulk_id not in BULK_SESSIONS:
        raise HTTPException(status_code=404, detail="Bulk session not found")
    return BULK_SESSIONS[bulk_id]

@router.get("/api/download/{bulk_id}")
async def download_bulk_results(bulk_id: str, format: str = "csv"):
    if bulk_id not in BULK_SESSIONS:
        raise HTTPException(status_code=404, detail="Bulk session not found")
        
    data = BULK_SESSIONS[bulk_id]["results"]
    df = pd.DataFrame(data)
    
    # Reorder/rename columns for export
    if "row_index" in df.columns:
        df.drop(columns=["row_index"], inplace=True)
    
    if format == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return StreamingResponse(
            output, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=bulk_results_{bulk_id}.xlsx"}
        )
    else:
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return StreamingResponse(
            output, 
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=bulk_results_{bulk_id}.csv"}
        )
