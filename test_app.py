"""
Integration and Unit Test Suite for PayPal AI Consensus Room
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "AnalystAgent" in data["agents"]


def test_index_page():
    res = client.get("/")
    assert res.status_code == 200
    assert "PayPal AI" in res.text


def test_evaluate_safe_transaction():
    payload = {
        "query": "Standard local coffee purchase at Starbucks Seattle",
        "amount": 4.50,
        "channel": "MERCHANT_CHECKOUT",
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROCESSED"
    assert data["verdict"] == "APPROVED"
    assert data["risk_score"] < 0.35
    assert len(data["findings"]) == 4
    assert len(data["audit_hash"]) == 64


def test_evaluate_fraud_transaction():
    payload = {
        "query": "Rapid cross-border withdrawal to unverified destination wallet in Zurich",
        "amount": 7500.00,
        "channel": "WIRE_TRANSFER",
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROCESSED"
    assert data["verdict"] == "BLOCKED"
    assert data["risk_score"] > 0.65
    assert "Unanimous Freeze" in data["consensus_ratio"]


def test_audit_log_merkle_chain():
    res = client.get("/api/audit-log")
    assert res.status_code == 200
    data = res.json()
    assert data["total_blocks"] >= 2
    assert len(data["blocks"]) >= 2
