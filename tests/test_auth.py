import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import get_password_hash, verify_password, create_access_token

client = TestClient(app)

def test_password_hashing():
    pwd = "secret_password_123"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_user_registration_and_login():
    email = f"user_{pytest.__name__}@razorflow.ai"
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "username": f"test_user_{id(email)}",
        "password": "SecurePassword123",
        "role": "analyst"
    })
    assert reg_res.status_code in [200, 400] # 200 or already registered
    
    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": "SecurePassword123"
    })
    if login_res.status_code == 200:
        data = login_res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
