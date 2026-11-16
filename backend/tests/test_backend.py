import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.entities import User, Workspace, Product, Review, Competitor, PriceAlert, ApprovalRequest
from app.analytics.nlp_engine import calculate_review_sentiment, extract_topics, analyze_reviews_dataset
from app.validators.claim_validator import validate_seo_claims

client = TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    login_res = client.post("/api/v1/auth/login", data={"username": "admin@marketpilot.ai", "password": "AdminPass123!"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 1. System Health & Infrastructure Test
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "MarketPilot AI"
    assert data["llm_provider"] in ["mock", "ollama"]

# 2. Authentication & User Profile Tests
def test_auth_me(auth_headers):
    me_res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "admin@marketpilot.ai"
    assert user_data["role"] == "admin"
    assert user_data["workspace_id"] is not None

def test_auth_invalid_credentials():
    login_res = client.post("/api/v1/auth/login", data={"username": "admin@marketpilot.ai", "password": "WrongPassword!"})
    assert login_res.status_code == 401

# 3. Deterministic NLP & Sentiment Analysis Tests
def test_nlp_engine_deterministic():
    # Positive test
    pos_text = "The audio quality is fantastic and outstanding!"
    pos_sent, pos_score = calculate_review_sentiment(pos_text, 5.0)
    assert pos_sent == "positive"
    assert pos_score > 0.15

    # Negative test with repeated complaints
    neg_text = "Battery life is disappointing and terrible, battery drains in 3 hours"
    neg_sent, neg_score = calculate_review_sentiment(neg_text, 1.0)
    assert neg_sent == "negative"
    assert neg_score < -0.15

    # Topic extraction
    topics = extract_topics(neg_text)
    assert "battery" in topics

def test_reviews_dataset_statistical_accuracy():
    sample_corpus = [
        {"rating": 5.0, "review_text": "Great headphones with high quality sound", "sentiment": "positive", "topics": ["sound_audio"]},
        {"rating": 1.0, "review_text": "Battery drains quickly and battery died", "sentiment": "negative", "topics": ["battery"]},
        {"rating": 2.0, "review_text": "Battery charging is broken and slow", "sentiment": "negative", "topics": ["battery"]}
    ]
    analytics = analyze_reviews_dataset(sample_corpus)
    assert analytics["total_reviews"] == 3
    assert analytics["total_negative_reviews"] == 2
    assert "battery" in analytics["complaint_breakdown"]
    assert analytics["complaint_breakdown"]["battery"]["percentage"] == 100.0

# 4. Claim Validation & Grounding Guardrail Tests
def test_grounding_claim_validator():
    # Valid claim matching database attributes
    valid_text = "MarketPilot Headphones with verified 30 hours battery life and comfortable earcups."
    is_valid, details = validate_seo_claims(valid_text, {"battery_hours": 30}, "Verified wireless headphones")
    assert is_valid is True

    # Exaggerated specification violation
    invalid_text = "Enjoy 80 hours battery life with miraculous lifetime warranty."
    is_invalid, details = validate_seo_claims(invalid_text, {"battery_hours": 30}, "Verified wireless headphones")
    assert is_invalid is False
    assert len(details["violations"]) >= 1

# 5. Product Catalog CRUD & Validation Tests
def test_product_crud_lifecycle(auth_headers):
    # Create product
    new_prod = {
        "sku": "TEST_PROD_99",
        "name": "Test Wireless Gaming Earbuds",
        "category": "Gaming",
        "description": "Ultra low-latency gaming earbuds",
        "price": 45.0,
        "currency": "USD",
        "brand": "MarketPilot",
        "attributes": {"latency_ms": 25, "battery_hours": 18}
    }
    create_res = client.post("/api/v1/products", headers=auth_headers, json=new_prod)
    assert create_res.status_code == 200
    prod_id = create_res.json()["id"]

    # Read product
    get_res = client.get(f"/api/v1/products/{prod_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == new_prod["name"]

    # Update product
    update_res = client.put(f"/api/v1/products/{prod_id}", headers=auth_headers, json={"price": 39.99})
    assert update_res.status_code == 200
    assert update_res.json()["price"] == 39.99

    # Delete product
    del_res = client.delete(f"/api/v1/products/{prod_id}", headers=auth_headers)
    assert del_res.status_code == 200

# 6. CSV Export Tests
def test_csv_export(auth_headers):
    res = client.get("/api/v1/products/export/csv", headers=auth_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "sku,name,category" in res.text

# 7. AI Multi-Agent Execution & Workflow Tests
def test_all_five_agents_and_full_orchestration(auth_headers):
    agents = [
        "review_analysis",
        "competitor_price_monitoring",
        "seo_content_generation",
        "marketing_campaign",
        "business_insights"
    ]
    for agent_id in agents:
        res = client.post(f"/api/v1/agents/{agent_id}/run?product_id=HP001", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert "summary" in data
        assert "evidence" in data

    # Test full 5-agent coordinated workflow
    full_wf = client.post("/api/v1/agents/orchestrate/full?product_id=HP001", headers=auth_headers)
    assert full_wf.status_code == 200
    wf_data = full_wf.json()
    assert wf_data["status"] == "success"
    assert len(wf_data["pipeline_stages"]) >= 4

# 8. Human-in-the-Loop Approval Center Tests
def test_human_approval_workflow(auth_headers):
    # Fetch pending approvals
    list_res = client.get("/api/v1/approvals", headers=auth_headers)
    assert list_res.status_code == 200
    approvals = list_res.json()
    assert len(approvals) >= 1

    # Approve item
    first_id = approvals[0]["id"]
    approve_res = client.post(f"/api/v1/approvals/{first_id}/approve", headers=auth_headers, json={"notes": "Master SQA Verification"})
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "success"

# 9. Executive Dashboard Statistics Test
def test_dashboard_stats(auth_headers):
    stats_res = client.get("/api/v1/insights/stats", headers=auth_headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_products"] >= 1
    assert stats["total_reviews"] >= 1
    assert "recent_agent_runs" in stats
    assert "latest_business_insights" in stats
