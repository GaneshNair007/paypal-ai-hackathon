"""
PayPal AI — SQLite Persistent Ledger & Merkle Audit Store
ACID-compliant storage for all evaluated transactions, consensus votes, and Merkle root seals.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "ledger.db"


class LedgerDatabase:
    """
    Local SQLite ledger maintaining immutable audit trails and transaction state.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_schema()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    amount REAL NOT NULL,
                    channel TEXT NOT NULL,
                    destination_country TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    consensus_ratio TEXT NOT NULL,
                    audit_hash TEXT NOT NULL UNIQUE,
                    duration_ms REAL NOT NULL,
                    created_at REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS agent_debates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_id INTEGER NOT NULL,
                    agent_name TEXT NOT NULL,
                    finding TEXT NOT NULL,
                    FOREIGN KEY (tx_id) REFERENCES transactions (id)
                );

                CREATE TABLE IF NOT EXISTS merkle_seals (
                    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    previous_hash TEXT NOT NULL,
                    block_hash TEXT NOT NULL,
                    tx_count INTEGER NOT NULL,
                    sealed_at REAL NOT NULL
                );
            """)

    def insert_transaction(
        self,
        query: str,
        amount: float,
        channel: str,
        destination_country: str,
        verdict: str,
        risk_score: float,
        consensus_ratio: str,
        audit_hash: str,
        duration_ms: float,
        findings: List[str],
    ) -> int:
        now = time.time()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO transactions (
                    query, amount, channel, destination_country, verdict,
                    risk_score, consensus_ratio, audit_hash, duration_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query, amount, channel, destination_country, verdict,
                risk_score, consensus_ratio, audit_hash, duration_ms, now
            ))
            tx_id = cur.lastrowid
            for f in findings:
                cur.execute("INSERT INTO agent_debates (tx_id, agent_name, finding) VALUES (?, ?, ?)", (tx_id, "ConsensusAgent", f))
            conn.commit()
            return tx_id

    def list_recent_transactions(self, limit: int = 25) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cur.fetchall()]

    def count_transactions(self) -> int:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM transactions")
            return cur.fetchone()[0]


ledger_db = LedgerDatabase()
