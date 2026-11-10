"""
Comprehensive Test Suite for PayPal AI Consensus Room
Validates ML detection, GPU tensor execution, graph cycle analysis, and SQLite persistence.
"""

from fastapi.testclient import TestClient
from main import app
from core.gpu_engine import gpu_engine
from core.graph_engine import TransactionGraph
from core.db import ledger_db

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "AnalystAgent" in data["agents"]
    assert "NVIDIA" in data["compute_device"] or "CPU" in data["compute_device"]


def test_index_page():
    res = client.get("/")
    assert res.status_code == 200
    assert "PayPal AI" in res.text


def test_evaluate_safe_transaction():
    payload = {
        "query": "Standard local coffee purchase at Starbucks Seattle",
        "amount": 4.50,
        "channel": "MERCHANT_CHECKOUT",
        "destination_country": "US",
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROCESSED"
    assert data["verdict"] == "APPROVED"
    assert data["risk_score"] < 0.40
    assert data["gpu_accelerated"] is True or gpu_engine.is_cuda is False
    assert len(data["audit_hash"]) == 64


def test_evaluate_fraud_transaction():
    payload = {
        "query": "Rapid cross-border withdrawal to unverified destination wallet in Zurich",
        "amount": 7500.00,
        "channel": "WIRE_TRANSFER",
        "destination_country": "CH",
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "PROCESSED"
    assert data["verdict"] in ("BLOCKED", "FLAGGED_FOR_REVIEW")
    assert data["risk_score"] > 0.50
    assert "gpu_telemetry" in data


def test_gpu_tensor_acceleration():
    risk, cluster, telem = gpu_engine.compute_gpu_risk([0.9, 0.8, 0.7, 0.9, 1.0, 1.0])
    assert 0.0 <= risk <= 1.0
    assert isinstance(cluster, str)
    assert "device" in telem
    if gpu_engine.is_cuda:
        assert telem["device"] == "cuda:0"
        assert "NVIDIA" in telem["device_name"]


def test_graph_cycle_detection():
    tg = TransactionGraph()
    tg.record_edge("wallet_A", "wallet_B", 500.0)
    tg.record_edge("wallet_B", "wallet_C", 500.0)
    tg.record_edge("wallet_C", "wallet_A", 500.0)
    cycles = tg.detect_cycles("wallet_A")
    assert len(cycles) > 0
    assert cycles[0] == ["wallet_A", "wallet_B", "wallet_C", "wallet_A"]


def test_sqlite_persistence():
    count_before = ledger_db.count_transactions()
    payload = {
        "query": "Test persistence verification",
        "amount": 100.0,
        "channel": "P2P_INSTANT",
    }
    res = client.post("/api/evaluate", json=payload)
    assert res.status_code == 200
    count_after = ledger_db.count_transactions()
    assert count_after == count_before + 1


def test_audit_log_endpoint():
    res = client.get("/api/audit-log")
    assert res.status_code == 200
    data = res.json()
    assert "total_records" in data
    assert "recent_transactions" in data
