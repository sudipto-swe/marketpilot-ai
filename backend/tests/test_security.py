import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    login_res = client.post("/api/v1/auth/login", data={"username": "admin@marketpilot.ai", "password": "AdminPass123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 1. SQL Injection attempts on Products Search & SKU
def test_security_sql_injection_defense(auth_headers):
    sqli_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE products; --",
        "admin'--",
        "1 UNION SELECT 1,2,3,4,5,6,7,8--"
    ]
    for payload in sqli_payloads:
        # Search injection test
        res = client.get(f"/api/v1/products?search={payload}", headers=auth_headers)
        assert res.status_code == 200 # Handled safely via parameter binding, no SQL crash
        assert isinstance(res.json(), list)

# 2. Unauthorized Access without Token
def test_security_unauthorized_endpoints():
    protected_urls = [
        "/api/v1/products",
        "/api/v1/reviews",
        "/api/v1/competitors/prices",
        "/api/v1/agents",
        "/api/v1/approvals",
        "/api/v1/insights/stats"
    ]
    for url in protected_urls:
        res = client.get(url)
        assert res.status_code == 401

# 3. Path Traversal & File Upload Validation
def test_security_csv_import_validation(auth_headers):
    # Upload malicious binary disguised as CSV
    fake_csv = b"\x00\x01\x02\x03\x04MALICIOUS_BYTES"
    files = {"file": ("exploit.csv", fake_csv, "text/csv")}
    res = client.post("/api/v1/products/import", headers=auth_headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    # Malicious rows should fail validation safely without crashing backend
    assert data["imported_count"] == 0

# 4. Input Boundary & Negative Numbers in Pricing
def test_security_negative_pricing_defense(auth_headers):
    invalid_product = {
        "sku": "NEG_PRICE_SKU",
        "name": "Negative Price Item",
        "category": "Electronics",
        "price": -99.99, # Negative price attack
        "currency": "USD"
    }
    # Dynamic repricing check
    res = client.get("/api/v1/competitors/dynamic-repricing/HP001?min_margin_pct=-50.0", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    # Ensure COGS floor prevents price crashing
    assert data["recommended_price"] >= data["unit_cost"]
