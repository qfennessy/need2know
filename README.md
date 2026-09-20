# Need to Know

Need to Know is one private door in front of the facts AI assistants learn about a person. Each assistant has one user-written purpose, such as “writes code in my projects” or “helps me with my health.” For every request, Need to Know retrieves a small set of relevant facts, asks Jev whether the fact is needed and reasonably expected for that role, and releases the exact fact, a safer version, or nothing.

This is a fast local prototype for [Sundai Hack 141: Agent Memory Frontier](https://www.sundai.club/events/boston/sundai-hack-141-agent-memory-frontier).

## Where facts live

Everything is stored on the user's machine in one SQLite database. By default that file is:

```text
~/.config/need2know/need2know.db
```

Set `N2K_DB_PATH` to put it somewhere else. All worktrees share this default path.
The database lives outside Git; it is the user's private data, not an application artifact.
Existing `.env` files with an old `N2K_DB_PATH` override should be updated to this path.

| Table | What it contains |
| --- | --- |
| `facts` | Canonical fact text, a safer alternative, category, sensitivity, keywords, and a local embedding blob. |
| `fact_vectors` | sqlite-vec's local vector index used to narrow each request to a few candidate facts. |
| `agents` | Registered agent names and their fixed user-written roles. |
| `queries` | Every request made through the door. |
| `decisions` | One audit record for every fact considered: probabilities, disclosure choice, released text, and review state. |
| `memory_proposals` | Agent-submitted candidate facts awaiting human review. These are not searchable or retrievable memories. |

There is no separate cloud memory store. When `N2K_JUDGE_MODE=jev`, only the candidate facts, the agent role, and the active request are sent to Jev for the access decision; an unavailable or malformed Jev response releases nothing.

## Run the prototype

Use Homebrew Python 3.13, which can load the sqlite-vec extension:

```bash
uv venv --clear --python /opt/homebrew/opt/python@3.13/bin/python3.13
uv sync
uv run need2know seed --reset
uv run uvicorn need2know.api:app --host 127.0.0.1 --port 8000 --reload --reload-dir need2know
```

Open `http://127.0.0.1:8000` to see the agent-session wall.

## Run a command-line demo

The terminal demo asks the same local memory switch used by MCP clients, then
prints the agent’s fixed role, the request, the minimum released detail (if
any), and the audit record number:

```bash
uv run need2know demo --agent muse-travel "Find a good restaurant for my trip to Lisbon."
```

Use `--offline` for a free, fully local rehearsal of the flow. It uses the
prototype’s local overlap judge instead of making a Jev HTTP call:

```bash
uv run need2know demo --offline
```

Use `need2know ask AGENT_ID "REQUEST"` when you need the raw JSON tool-shaped
response instead.

## Claude Code MCP connection

The project includes a Claude Code MCP configuration named `need2know-claude`. It runs the local FastMCP service under the fixed `claude-health` identity:

```bash
claude mcp get need2know-claude
claude
```

Muse Code uses a client-specific user configuration instead of the shared project `.mcp.json`, so Claude never receives a travel-role server and Muse never receives a health-role server. Its `need2know-muse` entry uses the fixed `muse-travel` identity. Start a new Muse session after adding that entry:

```bash
muse --trust-workspace
```

`MUSE_API_KEY` authenticates Muse Code's model provider; it is not passed to Need to Know. Need to Know loads only its own local Jev key from `.env`. The dashboard’s review actions are also cleared by `need2know seed --reset`, along with the facts they may have created.

The server exposes `identity`, `recall`, and `propose_memory`.

## Codex MCP connection

Codex has a separate local stdio entry named `need2know-codex`, fixed to the
`codex-code` role. From this project directory, confirm the installed
connection and start a new Codex session:

```bash
codex mcp get need2know-codex
codex
```

The connection runs `uv --directory . run need2know-mcp` with
`N2K_AGENT_ID=codex-code`. Keep it as a Codex-specific configuration: a client
must never select a more privileged role by changing tool input. Codex supports
local stdio MCP servers through its MCP configuration; see the [official Codex
MCP documentation](https://developers.openai.com/docs/extend/mcp).

- `recall` receives a narrowly scoped task, applies the role-aware access decision, and writes the audit record to the same local SQLite file.
- `propose_memory` requires a full fact, source, and confidence. The app uses the installed, authenticated Claude Sonnet client to derive its category and a short, privacy-minimized statement. This sends the proposed fact to Claude with tools disabled. Generation failures create no proposal. Both generated fields appear in the review queue; the proposal remains unretrievable until a human accepts it.
- The local dashboard’s review queue lets the user approve a proposal with a chosen sensitivity (`low`, `medium`, or `high`) or reject it. Approval atomically creates the canonical fact and its sqlite-vec entry, marks the proposal `accepted`, and records the accepted fact ID. Rejection records `rejected` and never creates a fact.

Example proposal:

```json
{
  "fact": "Alex prefers aisle seats near the front.",
  "source": "user_statement",
  "confidence": 1.0
}
```

Allowed sources are `user_statement` and `user_provided_record`. The MCP server rejects inferences, empty fields, oversized fields, and confidence values outside 0–1.

## Evaluate access decisions

Live disclosure now checks task scope against the fixed role and evaluates need
and expected access separately for the exact and softened text. A full release
cannot borrow the softer version's access scores. All checks remain in one Jev
batch; scope and both versions' scores are retained in the audit rationale.

Run `uv run python scripts/evaluate_memory.py` for a live Jev matrix using
fictional facts in a separate database. See [evaluation instructions](docs/evaluation.md)
for cases, retrieval-versus-judge comparison, repetitions, and report formats.

## Environment

Copy `.env.example` to `.env` and set `TYPESAFE_API_KEY`. `N2K_JUDGE_MODE=jev` uses TypeSafe Jev over HTTP with a two-second timeout. Keep `.env` local; it must never be committed.
