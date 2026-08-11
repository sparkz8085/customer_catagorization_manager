import os
import sys
import time
import requests
import subprocess
from pathlib import Path

# Ensure MODEL_TRUSTED is set
os.environ["MODEL_TRUSTED"] = "1"

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

CSV_1 = BASE_DIR / "artifacts" / "dummy_test_customers.csv"
CSV_2 = BASE_DIR / "artifacts" / "dummy_test_raw_kaggle.csv"

PYTHON_EXE = str(BASE_DIR / "venv312" / "Scripts" / "python.exe")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

def run_tests():
    print("--- Testing Bulk Upload Functionality ---")
    
    # 1. Test backend logic directly by importing router / functions or making live server requests
    from routes.bulk import api_bulk_upload
    from fastapi import UploadFile
    import asyncio
    from fastapi.requests import Request
    
    from services.auth_session import create_session_cookie
    valid_cookie = create_session_cookie({"email": "test@example.com", "name": "Test User"})
    
    # Mock FastAPI Request with cookie
    class DummyRequest:
        def __init__(self):
            self.cookies = {"session": valid_cookie}
            self.url = type("Url", (), {"path": "/api/bulk-upload"})()
    
    async def test_file(file_path):
        print(f"\nTesting file: {file_path.name}")
        with open(file_path, "rb") as f:
            upload_file = UploadFile(filename=file_path.name, file=f)
            req = DummyRequest()
            res = await api_bulk_upload(req, upload_file)
            if hasattr(res, 'body'):
                import json
                res_data = json.loads(res.body.decode('utf-8'))
            else:
                res_data = res
            print(f"Response data: {res_data}")
            assert res_data.get("status") == "success", f"Bulk upload failed: {res_data}"
            bulk_id = res_data.get("bulk_id")
            
            from routes.bulk import get_bulk_results, download_bulk_results
            results_data = await get_bulk_results(bulk_id)
            print(f"Total: {results_data['total']}, Success: {results_data['success']}, Failed: {results_data['failed']}")
            for r in results_data['results']:
                print(f"  Row {r['row_index']} ({r['Customer Name']}): Category={r['Predicted Category']}, Status={r['Status']}, Remarks={r['Remarks']}")
            assert results_data['failed'] == 0, f"Some rows failed: {results_data['results']}"
            
            # Test download formats
            dl_csv = await download_bulk_results(bulk_id, "csv")
            assert dl_csv.status_code == 200
            print("CSV download endpoint OK")
            
            dl_excel = await download_bulk_results(bulk_id, "excel")
            assert dl_excel.status_code == 200
            print("Excel download endpoint OK")
            
    asyncio.run(test_file(CSV_1))
    asyncio.run(test_file(CSV_2))
    
    print("\nAll unit tests for bulk upload passed successfully!")

if __name__ == "__main__":
    run_tests()
