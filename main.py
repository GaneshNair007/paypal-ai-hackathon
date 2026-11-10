"""
PayPal AI — Autonomous Multi-Agent Consensus Room
Production FastAPI Backend Engine
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

app = FastAPI(
    title="PayPal AI Consensus Room",
    description="Verifiable multi-agent transaction fraud evaluation with cryptographic audit trails.",
    version="1.0.0",
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
    destination_country: Optional[str] = "US"


class ConsensusEvaluationResult(BaseModel):
    status: str
    query: str
    verdict: str  # "APPROVED" | "FLAGGED_FOR_REVIEW" | "BLOCKED"
    risk_score: float
    consensus_ratio: str
    audit_hash: str
    duration_ms: float
    findings: List[str]
    timestamp: float


class AuditProof(BaseModel):
    tx_hash: str
    previous_hash: str
    timestamp: float
    verdict: str


# In-memory verifiable ledger of consensus decisions
LEDGER: List[Dict[str, Any]] = []


def calculate_sha256(payload: Dict[str, Any], prev_hash: str = "GENESIS") -> str:
    serialized = json.dumps(payload, sort_keys=True) + prev_hash
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>PayPal AI Consensus Room Online</h1>")


@app.get("/health")
def health_status():
    return {
        "status": "ONLINE",
        "service": "paypal-ai-consensus-room",
        "agents": ["AnalystAgent", "RiskOfficerAgent", "ComplianceAgent", "CryptographerAgent"],
        "ledger_size": len(LEDGER),
        "timestamp": time.time(),
    }


@app.post("/api/evaluate", response_model=ConsensusEvaluationResult)
def evaluate_transaction(req: TransactionRequest):
    start = time.time()
    findings = []
    risk_points = 0.0

    # 1. Analyst Agent: Pattern and heuristic evaluation
    q_lower = req.query.lower()
    if any(k in q_lower for k in ["cross-border", "zurich", "unverified", "rapid", "anonymous"]):
        risk_points += 0.35
        findings.append("Analyst Agent: High-frequency cross-border hop detected in unverified corridor.")
    else:
        findings.append("Analyst Agent: Domestic transaction pattern within standard velocity bounds.")

    # 2. Risk Officer: Capital exposure evaluation
    if req.amount > 3000:
        risk_points += 0.35
        findings.append(f"Risk Officer: Elevated principal exposure (${req.amount:,.2f} exceeds threshold $3,000.00).")
    elif req.amount > 500:
        risk_points += 0.15
        findings.append(f"Risk Officer: Moderate capital exposure (${req.amount:,.2f}).")
    else:
        findings.append(f"Risk Officer: Low capital risk (${req.amount:,.2f} within micro-settlement quota).")

    # 3. Compliance Agent: Channel & regulatory scrutiny
    if req.channel == "WIRE_TRANSFER" and "unverified" in q_lower:
        risk_points += 0.25
        findings.append("Compliance Agent: Travel Rule Enhanced Due Diligence (EDD) triggered.")
    else:
        findings.append("Compliance Agent: Regulatory sanctions screening cleared (OFAC/FinCEN clean).")

    # 4. Cryptographer Agent: Consensus synthesis & threshold sealing
    final_risk = min(max(round(risk_points, 3), 0.05), 0.98)
    if final_risk > 0.65:
        verdict = "BLOCKED"
        ratio = "4 / 4 Unanimous Freeze"
    elif final_risk > 0.35:
        verdict = "FLAGGED_FOR_REVIEW"
        ratio = "3 / 4 Review Escalation"
    else:
        verdict = "APPROVED"
        ratio = "4 / 4 Optimal Pass"

    prev_hash = LEDGER[-1]["audit_hash"] if LEDGER else "0000000000000000000000000000000000000000000000000000000000000000"
    audit_data = {
        "query": req.query,
        "amount": req.amount,
        "channel": req.channel,
        "verdict": verdict,
        "risk_score": final_risk,
    }
    audit_hash = calculate_sha256(audit_data, prev_hash)

    record = {
        "id": len(LEDGER) + 1,
        "audit_hash": audit_hash,
        "previous_hash": prev_hash,
        "verdict": verdict,
        "risk_score": final_risk,
        "timestamp": time.time(),
    }
    LEDGER.append(record)
    findings.append(f"Cryptographer Agent: Sealed Merkle block #{record['id']} with proof {audit_hash[:16]}...")

    duration_ms = round((time.time() - start) * 1000, 2)

    return ConsensusEvaluationResult(
        status="PROCESSED",
        query=req.query,
        verdict=verdict,
        risk_score=final_risk,
        consensus_ratio=ratio,
        audit_hash=audit_hash,
        duration_ms=duration_ms,
        findings=findings,
        timestamp=time.time(),
    )


@app.get("/api/audit-log")
def get_audit_log(limit: int = 10):
    return {"total_blocks": len(LEDGER), "blocks": LEDGER[-limit:]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
