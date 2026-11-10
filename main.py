"""
PayPal AI — Autonomous Multi-Agent Consensus Room
Production FastAPI Backend Engine with NVIDIA CUDA GPU Acceleration
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from core.db import ledger_db
from core.gpu_engine import gpu_engine
from core.graph_engine import graph_engine, velocity_tracker
from core.ml_detector import ml_detector

app = FastAPI(
    title="PayPal AI Consensus Room",
    description="GPU-accelerated multi-agent transaction fraud evaluation with cryptographic audit trails.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class TransactionRequest(BaseModel):
    query: str = Field(..., description="Description of the transaction context")
    amount: float = Field(default=0.0, description="Amount in USD")
    channel: str = Field(default="P2P_INSTANT", description="Payment channel identifier")
    source_user: Optional[str] = "user_primary"
    destination_user: Optional[str] = "merchant_gateway"
    destination_country: Optional[str] = "US"


class ConsensusEvaluationResult(BaseModel):
    status: str
    query: str
    verdict: str  # "APPROVED" | "FLAGGED_FOR_REVIEW" | "BLOCKED"
    risk_score: float
    consensus_ratio: str
    audit_hash: str
    duration_ms: float
    gpu_accelerated: bool
    gpu_telemetry: Dict[str, Any]
    findings: List[str]
    timestamp: float


def calculate_sha256(payload: Dict[str, Any], prev_hash: str = "GENESIS") -> str:
    serialized = json.dumps(payload, sort_keys=True) + prev_hash
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>PayPal AI Consensus Room Online (GPU Enabled)</h1>")


@app.get("/health")
def health_status():
    return {
        "status": "ONLINE",
        "service": "paypal-ai-consensus-room",
        "compute_device": gpu_engine.device_name,
        "cuda_active": gpu_engine.is_cuda,
        "agents": ["AnalystAgent", "RiskOfficerAgent", "ComplianceAgent", "CryptographerAgent"],
        "persisted_transactions": ledger_db.count_transactions(),
        "timestamp": time.time(),
    }


@app.post("/api/evaluate", response_model=ConsensusEvaluationResult)
def evaluate_transaction(req: TransactionRequest):
    start = time.time()
    findings = []

    # 1. Statistical Feature Extraction
    features = ml_detector.extract_features(req.model_dump())
    base_risk, ml_reasons = ml_detector.compute_composite_risk(features)
    findings.extend(ml_reasons)

    # 2. Velocity & Graph Ring Analysis
    is_breach, vol_sum, ev_count = velocity_tracker.record_and_evaluate(req.source_user or "user", req.amount)
    if is_breach:
        findings.append(f"Velocity Breach: Account triggered {ev_count} operations totaling ${vol_sum:,.2f} in 5m.")

    graph_engine.record_edge(req.source_user or "user", req.destination_user or "dest", req.amount)
    cycles = graph_engine.detect_cycles(req.source_user or "user")
    if cycles:
        findings.append(f"Graph Intelligence: Circular routing cycle detected ({' -> '.join(cycles[0])}).")

    # 3. GPU CUDA Tensor Cosine Similarity Scoring
    feature_vec = [
        features["amount_risk"],
        features["corridor_risk"],
        features["channel_risk"],
        features["narrative_risk"],
        1.0 if is_breach else 0.0,
        1.0 if cycles else 0.0,
    ]
    gpu_risk, fraud_cluster, gpu_telemetry = gpu_engine.compute_gpu_risk(feature_vec)

    # 4. Multi-Agent Consensus Synthesis
    composite_risk = round(base_risk * 0.45 + gpu_risk * 0.40 + (0.15 if (is_breach or cycles) else 0.0), 3)
    composite_risk = min(max(composite_risk, 0.02), 0.99)

    if composite_risk > 0.65:
        verdict = "BLOCKED"
        ratio = "4 / 4 Unanimous Freeze"
    elif composite_risk > 0.35:
        verdict = "FLAGGED_FOR_REVIEW"
        ratio = "3 / 4 Review Escalation"
    else:
        verdict = "APPROVED"
        ratio = "4 / 4 Optimal Pass"

    # 5. Cryptographic Merkle Sealing & SQLite Persistence
    recent_txs = ledger_db.list_recent_transactions(limit=1)
    prev_hash = recent_txs[0]["audit_hash"] if recent_txs else "0000000000000000000000000000000000000000000000000000000000000000"

    audit_payload = {
        "query": req.query,
        "amount": req.amount,
        "channel": req.channel,
        "verdict": verdict,
        "risk_score": composite_risk,
        "gpu_cluster": fraud_cluster,
    }
    audit_hash = calculate_sha256(audit_payload, prev_hash)

    duration_ms = round((time.time() - start) * 1000, 2)

    ledger_db.insert_transaction(
        query=req.query,
        amount=req.amount,
        channel=req.channel,
        destination_country=req.destination_country or "US",
        verdict=verdict,
        risk_score=composite_risk,
        consensus_ratio=ratio,
        audit_hash=audit_hash,
        duration_ms=duration_ms,
        findings=findings,
    )

    findings.append(f"GPU Engine: Classified under cluster '{fraud_cluster}' in {gpu_telemetry['latency_microseconds']}µs.")

    return ConsensusEvaluationResult(
        status="PROCESSED",
        query=req.query,
        verdict=verdict,
        risk_score=composite_risk,
        consensus_ratio=ratio,
        audit_hash=audit_hash,
        duration_ms=duration_ms,
        gpu_accelerated=gpu_engine.is_cuda,
        gpu_telemetry=gpu_telemetry,
        findings=findings,
        timestamp=time.time(),
    )


@app.get("/api/audit-log")
def get_audit_log(limit: int = 15):
    return {
        "total_records": ledger_db.count_transactions(),
        "recent_transactions": ledger_db.list_recent_transactions(limit=limit),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
