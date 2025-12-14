import time
from fastapi.testclient import TestClient
from app.main import app
from app.auth.OAuth2 import create_jwt_token

client = TestClient(app)


def get_auth_headers(user_id: int, role: str):
    token = create_jwt_token({"user_id": user_id, "user_role": role})
    return {"Authorization": f"Bearer {token}"}


# =========================
# POSITIVE TEST CASES
# =========================

def test_register_user_success():
    username = f"user_{int(time.time())}"
    res = client.post(
        "/auth/register",
        json={"username": username, "password": "Test@123"}
    )
    assert res.status_code == 201


def test_register_same_user_twice_fail():
    username = f"user_{int(time.time())}"
    client.post("/auth/register", json={"username": username, "password": "Test@123"})
    res = client.post("/auth/register", json={"username": username, "password": "Test@123"})
    assert res.status_code == 409


def test_manager_create_product_forbidden():
    headers = get_auth_headers(user_id=1, role="manager")
    res = client.post(
        "/manager/create-product",
        json={
            "product_name": "TestProduct",
            "product_price": 100,
            "product_stockqty": 10
        },
        headers=headers
    )
    assert res.status_code == 403


# =========================
# NEGATIVE TEST CASES
# =========================

def test_user_create_cart_without_product_fail():
    headers = get_auth_headers(user_id=2, role="user")
    res = client.post(
        "/user/createcart",
        json={
            "cart_value": [
                {"product_name": "UnknownProduct", "quantity": 1}
            ]
        },
        headers=headers
    )
    assert res.status_code == 422


def test_manager_route_access_by_user_fail():
    headers = get_auth_headers(user_id=2, role="user")
    res = client.post(
        "/manager/create-product",
        json={
            "product_name": "BadProduct",
            "product_price": 10,
            "product_stockqty": 1
        },
        headers=headers
    )
    assert res.status_code == 403


def test_checkout_empty_cart_fail():
    headers = get_auth_headers(user_id=3, role="user")
    res = client.get("/user/cartcheckout", headers=headers)
    assert res.status_code == 500
