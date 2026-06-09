from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_page_has_security_headers():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_train_route_disabled_without_secret():
    response = client.get("/train")

    assert response.status_code == 404


def test_safe_unpickler_allowed():
    import io
    import pickle
    from src.cloud_storage.local_storage import SafeUnpickler
    
    # Test builtins and numpy types (allowed)
    data = pickle.dumps({"key": (1, 2, "value")})
    unpickled = SafeUnpickler(io.BytesIO(data)).load()
    assert unpickled["key"] == (1, 2, "value")


def test_safe_unpickler_blocked():
    import io
    import pickle
    # pyrefly: ignore [missing-import]
    import pytest
    from src.cloud_storage.local_storage import SafeUnpickler
    
    # Test blocked classes (like subprocess.Popen)
    import subprocess
    data = pickle.dumps(subprocess.Popen)
    with pytest.raises(pickle.UnpicklingError) as exc_info:
        SafeUnpickler(io.BytesIO(data)).load()
    assert "Refusing to unpickle unsafe global" in str(exc_info.value)


def test_prediction_endpoint_error_handling_sanitization():
    # If the database or models fail, it must return 500 without disclosing the trace
    response = client.post("/", data={
        "Age": "25",
        "Education": "2",
        "Marital_Status": "0",
        "Parental_Status": "0",
        "Children": "0",
        "Income": "50000",
        "Total_Spending": "1000",
        "Days_as_Customer": "300",
        "Recency": "15",
        "Wines": "100",
        "Fruits": "50",
        "Meat": "200",
        "Fish": "50.5",
        "Sweets": "20",
        "Gold": "10.5",
        "Web": "5",
        "Catalog": "2",
        "Store": "3",
        "Discount_Purchases": "1",
        "Total_Promo": "0",
        "NumWebVisitsMonth": "8"
    })
    # Since AWS access is unconfigured/untrusted, prediction pipeline should fail
    assert response.status_code == 500
    assert "Prediction failed. Check model storage and environment configuration." in response.text
    # Ensure sensitive stack trace or code references are not present in the HTML
    assert "local_storage.py" not in response.text
    assert "Traceback" not in response.text
