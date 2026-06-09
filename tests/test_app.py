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

def test_prediction_endpoint_success():
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
    # Since we have pre-trained model artifacts, prediction should succeed
    assert response.status_code == 200
    assert "Customer is in Cluster" in response.text
