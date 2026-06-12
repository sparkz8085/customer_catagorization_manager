from fastapi.testclient import TestClient
from app import app
from services.auth_session import create_session_cookie

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login_page_loads():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign in with Google" in response.text
    assert "Sign in with Facebook" in response.text

def test_unauthenticated_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

def test_home_page_has_security_headers():
    mock_user = {
        "email": "test.user@example.com",
        "name": "Test User",
        "avatar_url": "https://lh3.googleusercontent.com/a/default-user",
        "provider": "mock"
    }
    cookie_value = create_session_cookie(mock_user)
    auth_client = TestClient(app)
    auth_client.cookies.set("session", cookie_value)
    
    response = auth_client.get("/")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]

def test_train_route_disabled_without_secret(monkeypatch):
    monkeypatch.delenv("TRAINING_API_KEY", raising=False)
    response = client.get("/train")
    assert response.status_code == 404

def test_prediction_endpoint_success():
    mock_user = {
        "email": "test.user@example.com",
        "name": "Test User",
        "avatar_url": "https://lh3.googleusercontent.com/a/default-user",
        "provider": "mock"
    }
    cookie_value = create_session_cookie(mock_user)
    auth_client = TestClient(app)
    auth_client.cookies.set("session", cookie_value)

    response = auth_client.post("/", data={
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
    assert response.status_code == 200
    assert "Customer is in Cluster" in response.text

def test_mock_callback_auth():
    response = client.get("/auth/mock-callback?provider=google", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/?welcome=true"
    assert "session" in response.cookies


def test_custom_info_login():
    response = client.post("/login/email", data={
        "name": "King Arthur",
        "nickname": "Arthur",
        "email": "arthur@camelot.org",
        "password": "Password123!"
    }, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/?welcome=true"
    assert "session" in response.cookies


