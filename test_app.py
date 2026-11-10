"""
Test Suite for PayPal AI Hackathon
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ONLINE"

def test_evaluate():
    res = client.post("/api/evaluate", json={"query": "ping"})
    assert res.status_code == 200
    assert res.json()["verdict"] == "OPTIMAL"
