from __future__ import annotations

from .config import Settings
from .db import Store
from .embeddings import LocalEmbedder
from .judge import judge


def make_store(settings: Settings) -> Store:
    store = Store(settings.db_path, LocalEmbedder(settings.model_path))
    store.initialize()
    return store


async def query(settings: Settings, store: Store, agent_id: str, request: str, limit: int = 8, client: str = "api") -> dict:
    agent = store.get_agent(agent_id)
    if not agent:
        raise ValueError(f"Unknown agent '{agent_id}'. Register it before connecting the MCP client.")
    candidates = store.candidates(request, limit)
    judged = await judge(settings, agent["purpose"], request, candidates)
    query_id = store.log_query(agent_id, request, judged.mode, judged.model, judged.status, judged.latency_ms, client)
    store.log_decisions(query_id, candidates, judged.decisions)
    released = [
        {"category": fact["category"], "memory": decision["released_text"], "disclosure": decision["outcome"]}
        for fact, decision in zip(candidates, judged.decisions) if decision["released_text"]
    ]
    return {
        "query_id": query_id,
        "agent": {"id": agent_id, "purpose": agent["purpose"]},
        "request": request,
        "memories": released,
        "candidate_count": len(candidates),
        "withheld_count": len(candidates) - len(released),
        "status": judged.status,
    }
