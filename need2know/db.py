from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import sqlite_vec

from .embeddings import DIMENSIONS, LocalEmbedder


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: Path, embedder: LocalEmbedder):
        self.path = path
        self.embedder = embedder
        self.vec_enabled = False

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        if hasattr(db, "enable_load_extension"):
            db.enable_load_extension(True)
            sqlite_vec.load(db)
            db.enable_load_extension(False)
            self.vec_enabled = True
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        finally:
            db.close()

    def initialize(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS agents (
                  id TEXT PRIMARY KEY, name TEXT NOT NULL, purpose TEXT NOT NULL,
                  created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS facts (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT NOT NULL, fact TEXT NOT NULL, soft_fact TEXT NOT NULL,
                  sensitivity TEXT NOT NULL, keywords TEXT NOT NULL,
                  embedding BLOB NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS queries (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT NOT NULL,
                  request TEXT NOT NULL, judge_mode TEXT NOT NULL,
                  judge_model TEXT, embedder TEXT NOT NULL, status TEXT NOT NULL,
                  latency_ms INTEGER NOT NULL, client TEXT NOT NULL DEFAULT 'api', created_at TEXT NOT NULL,
                  FOREIGN KEY(agent_id) REFERENCES agents(id)
                );
                CREATE TABLE IF NOT EXISTS decisions (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, query_id INTEGER NOT NULL,
                  fact_id INTEGER NOT NULL, rank INTEGER NOT NULL,
                  distance REAL NOT NULL, need_probability REAL NOT NULL,
                  expected_probability REAL NOT NULL, disclosure TEXT NOT NULL,
                  disclosure_probability REAL NOT NULL, outcome TEXT NOT NULL,
                  released_text TEXT, rationale TEXT NOT NULL,
                  review_status TEXT NOT NULL DEFAULT 'none', created_at TEXT NOT NULL,
                  FOREIGN KEY(query_id) REFERENCES queries(id),
                  FOREIGN KEY(fact_id) REFERENCES facts(id)
                );
                CREATE TABLE IF NOT EXISTS memory_proposals (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  agent_id TEXT NOT NULL,
                  fact TEXT NOT NULL,
                  soft_fact TEXT NOT NULL,
                  suggested_category TEXT NOT NULL,
                  source TEXT NOT NULL,
                  confidence REAL NOT NULL,
                  status TEXT NOT NULL DEFAULT 'pending',
                  created_at TEXT NOT NULL,
                  reviewed_at TEXT,
                  accepted_fact_id INTEGER,
                  FOREIGN KEY(agent_id) REFERENCES agents(id),
                  FOREIGN KEY(accepted_fact_id) REFERENCES facts(id),
                  CHECK (confidence >= 0 AND confidence <= 1),
                  CHECK (status IN ('pending', 'accepted', 'rejected'))
                );
                """
            )
            columns = {row[1] for row in db.execute("PRAGMA table_info(queries)")}
            if "client" not in columns:
                db.execute("ALTER TABLE queries ADD COLUMN client TEXT NOT NULL DEFAULT 'api'")
            if self.vec_enabled:
                db.execute(f"CREATE VIRTUAL TABLE IF NOT EXISTS fact_vectors USING vec0(fact_id INTEGER PRIMARY KEY, embedding float[{DIMENSIONS}] distance_metric=cosine)")
                indexed = {row[0] for row in db.execute("SELECT fact_id FROM fact_vectors")}
                for fact_id, embedding in db.execute("SELECT id, embedding FROM facts"):
                    if fact_id not in indexed:
                        vector = np.frombuffer(embedding, dtype=np.float32)
                        db.execute("INSERT INTO fact_vectors(fact_id, embedding) VALUES (?, ?)", (fact_id, vector))

    def add_agent(self, agent_id: str, name: str, purpose: str) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO agents VALUES (?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET name=excluded.name, purpose=excluded.purpose",
                (agent_id, name, purpose, utcnow()),
            )

    def add_fact(self, category: str, fact: str, soft_fact: str, sensitivity: str, keywords: list[str]) -> int:
        vector = self.embedder.embed(" ".join([category, fact, *keywords])).astype(np.float32)
        with self.connect() as db:
            cursor = db.execute(
                "INSERT INTO facts(category,fact,soft_fact,sensitivity,keywords,embedding,created_at) VALUES(?,?,?,?,?,?,?)",
                (category, fact, soft_fact, sensitivity, json.dumps(keywords), vector.tobytes(), utcnow()),
            )
            fact_id = int(cursor.lastrowid)
            if self.vec_enabled:
                db.execute("INSERT INTO fact_vectors(fact_id, embedding) VALUES (?, ?)", (fact_id, vector))
            return fact_id

    def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM agents WHERE id=?", (agent_id,)).fetchone()
            return dict(row) if row else None

    def candidates(self, request: str, limit: int = 10) -> list[dict[str, Any]]:
        query = self.embedder.embed(request).astype(np.float32)
        words = set(request.lower().split())
        with self.connect() as db:
            if self.vec_enabled:
                rows = db.execute(
                    """SELECT f.*, v.distance FROM fact_vectors v JOIN facts f ON f.id=v.fact_id
                       WHERE v.embedding MATCH ? AND k = ? ORDER BY v.distance""",
                    (query, min(limit * 2, 30)),
                ).fetchall()
                items = [dict(row) for row in rows]
            else:
                items = []
                for row in db.execute("SELECT * FROM facts"):
                    item = dict(row)
                    vector = np.frombuffer(item["embedding"], dtype=np.float32)
                    item["distance"] = float(1 - np.dot(query, vector))
                    items.append(item)
        for item in items:
            keyword_overlap = len(words & set(json.loads(item["keywords"])))
            item["retrieval_score"] = (1 - float(item["distance"])) + keyword_overlap * 0.15
            item.pop("embedding", None)
        return sorted(items, key=lambda x: x["retrieval_score"], reverse=True)[:limit]

    def log_query(self, agent_id: str, request: str, mode: str, model: str | None, status: str, latency_ms: int, client: str) -> int:
        with self.connect() as db:
            cursor = db.execute(
                "INSERT INTO queries(agent_id,request,judge_mode,judge_model,embedder,status,latency_ms,client,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                (agent_id, request, mode, model, self.embedder.name, status, latency_ms, client, utcnow()),
            )
            return int(cursor.lastrowid)

    def log_decisions(self, query_id: int, candidates: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> None:
        with self.connect() as db:
            for rank, (fact, decision) in enumerate(zip(candidates, decisions), 1):
                db.execute(
                    """INSERT INTO decisions(query_id,fact_id,rank,distance,need_probability,expected_probability,
                       disclosure,disclosure_probability,outcome,released_text,rationale,review_status,created_at)
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (query_id, fact["id"], rank, fact["distance"], decision["need_probability"],
                     decision["expected_probability"], decision["disclosure"], decision["disclosure_probability"],
                     decision["outcome"], decision.get("released_text"), decision["rationale"],
                     decision["review_status"], utcnow()),
                )

    def audit(self, limit: int = 100) -> dict[str, Any]:
        with self.connect() as db:
            agents = [dict(r) for r in db.execute("SELECT * FROM agents ORDER BY name")]
            decisions = [dict(r) for r in db.execute(
                """SELECT d.*, q.request, q.agent_id, q.judge_mode, q.latency_ms, q.client, q.created_at AS query_at,
                   f.category, f.fact, f.soft_fact, a.name AS agent_name, a.purpose
                   FROM decisions d JOIN queries q ON q.id=d.query_id JOIN facts f ON f.id=d.fact_id
                   JOIN agents a ON a.id=q.agent_id ORDER BY d.id DESC LIMIT ?""", (limit,)
            )]
            return {"agents": agents, "decisions": decisions}

    def list_facts(self) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT id, category, fact, soft_fact, sensitivity, created_at FROM facts ORDER BY category, id"
            ).fetchall()
            return [dict(row) for row in rows]

    def create_memory_proposal(
        self,
        agent_id: str,
        fact: str,
        soft_fact: str,
        suggested_category: str,
        source: str,
        confidence: float,
    ) -> dict[str, Any]:
        with self.connect() as db:
            cursor = db.execute(
                """INSERT INTO memory_proposals(
                   agent_id, fact, soft_fact, suggested_category, source, confidence, status, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
                (agent_id, fact, soft_fact, suggested_category, source, confidence, utcnow()),
            )
            proposal_id = int(cursor.lastrowid)
            row = db.execute("SELECT * FROM memory_proposals WHERE id=?", (proposal_id,)).fetchone()
            return dict(row)

    def list_memory_proposals(self, status: str = "pending") -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(
                """SELECT p.*, a.name AS agent_name, a.purpose AS agent_purpose
                   FROM memory_proposals p JOIN agents a ON a.id=p.agent_id
                   WHERE p.status=? ORDER BY p.id DESC""",
                (status,),
            ).fetchall()
            return [dict(row) for row in rows]
