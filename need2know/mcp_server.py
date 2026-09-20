from __future__ import annotations

from fastmcp import FastMCP

from .config import Settings
from .service import make_store, query
from .soften import generate_memory_metadata

settings = Settings.from_env()
store = make_store(settings)
mcp = FastMCP("Need to Know")


@mcp.tool
def identity() -> dict:
    """Show this MCP connection's fixed identity and user-defined purpose."""
    if not settings.agent_id:
        return {"configured": False, "message": "Set N2K_AGENT_ID in this MCP client's environment."}
    agent = store.get_agent(settings.agent_id)
    return {"configured": bool(agent), "agent": agent}


@mcp.tool
async def recall(request: str, max_memories: int = 8) -> dict:
    """Ask for user memories needed for one specific task. Every candidate decision is audited."""
    if not settings.agent_id:
        raise ValueError("This MCP connection has no N2K_AGENT_ID")
    return await query(settings, store, settings.agent_id, request, max(1, min(max_memories, 12)), client="mcp")


@mcp.tool
def propose_memory(
    fact: str,
    source: str,
    confidence: float,
) -> dict:
    """Stage a possible durable user fact for human review; this never saves it as a memory.

    Use only for a direct user statement or a cited user-provided record. Do not submit an
    inference. Source must be either 'user_statement' or 'user_provided_record'.
    """
    if not settings.agent_id:
        raise ValueError("This MCP connection has no N2K_AGENT_ID")
    if source not in {"user_statement", "user_provided_record"}:
        raise ValueError("source must be 'user_statement' or 'user_provided_record'; inferences cannot be stored")
    if not (0 <= confidence <= 1):
        raise ValueError("confidence must be between 0 and 1")
    for label, value in (("fact", fact),):
        if not value.strip() or len(value) > 2_000:
            raise ValueError(f"{label} must contain 1 to 2,000 characters")
    metadata = generate_memory_metadata(fact)
    proposal = store.create_memory_proposal(
        settings.agent_id,
        fact.strip(),
        metadata["soft_fact"],
        metadata["category"],
        source,
        confidence,
    )
    return {
        "proposal_id": proposal["id"],
        "status": "pending_review",
        **metadata,
        "message": "Proposed fact is not saved or retrievable until the user reviews it.",
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
