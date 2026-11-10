"""
PayPal AI — Graph Intelligence & Velocity Engine
Advanced fraud ring detection using directed graph cycle analysis and sliding-window velocity checks.
"""

from __future__ import annotations

import collections
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class TransactionGraph:
    """
    Directed transaction graph tracking money flow across accounts
    to detect mule networks and circular wash-trading loops.
    """

    def __init__(self):
        self.adj: Dict[str, List[Tuple[str, float, float]]] = collections.defaultdict(list)
        self.history: List[Dict[str, Any]] = []

    def record_edge(self, source: str, destination: str, amount: float, timestamp: Optional[float] = None) -> None:
        ts = timestamp or time.time()
        self.adj[source].append((destination, amount, ts))
        self.history.append({"source": source, "destination": destination, "amount": amount, "timestamp": ts})

    def detect_cycles(self, start_node: str, max_depth: int = 5) -> List[List[str]]:
        """
        Detects circular transaction paths (e.g. A -> B -> C -> A) indicating
        layered money laundering or wash trading.
        """
        cycles: List[List[str]] = []
        visited: Set[str] = set()

        def dfs(current: str, path: List[str]):
            if len(path) > max_depth:
                return
            for neighbor, amt, _ in self.adj.get(current, []):
                if neighbor == start_node and len(path) >= 2:
                    cycles.append(path + [start_node])
                elif neighbor not in visited and len(path) < max_depth:
                    visited.add(neighbor)
                    dfs(neighbor, path + [neighbor])
                    visited.remove(neighbor)

        visited.add(start_node)
        dfs(start_node, [start_node])
        return cycles


class VelocityTracker:
    """
    Sliding window velocity monitor identifying abnormal burst withdrawals.
    """

    def __init__(self, window_sec: float = 300.0, max_events: int = 5):
        self.window_sec = window_sec
        self.max_events = max_events
        self.user_events: Dict[str, collections.deque] = collections.defaultdict(collections.deque)

    def record_and_evaluate(self, user_id: str, amount: float) -> Tuple[bool, float, int]:
        now = time.time()
        dq = self.user_events[user_id]

        # Evict expired events
        while dq and (now - dq[0][0]) > self.window_sec:
            dq.popleft()

        dq.append((now, amount))
        total_amount = sum(a for _, a in dq)
        event_count = len(dq)

        is_velocity_breach = event_count > self.max_events or total_amount > 10000.0
        return is_velocity_breach, total_amount, event_count


graph_engine = TransactionGraph()
velocity_tracker = VelocityTracker()
