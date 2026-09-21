# Need to Know

<p align="center">
  <img src="assets/need-to-know-logo.png" width="220" alt="Need to Know: a private memory door formed by two speech bubbles and a keyhole">
</p>

In most assistant memory today, access is all-or-nothing: an assistant you give memory to sees every fact in it, so the assistant that should know your seat preference also knows your diagnosis, your home address, and your company's bank balance.

Need to Know is a local gate in front of those facts. You give each assistant one written job, such as "writes code in my projects" or "helps me with my health." Every request is judged against that job, and each relevant fact comes back one of three ways: the exact fact, a safer version of it, or nothing. Every decision is written to a local audit log.

```console
$ uv run need2know demo --agent muse-travel "Find a good restaurant for my trip to Lisbon."
Need to Know · local memory switch
Agent: muse-travel
Fixed role: plans travel, restaurants, lodging, and activities that fit my preferences and access needs
Request: Find a good restaurant for my trip to Lisbon.

Released (minimum useful detail):
  - [soft] Prioritize low-fiber food and reliable restroom access.

Checked 8 local candidates; kept 7 private.
Audit record: #1 · judge status: ok
```

The travel assistant gets what it needs to book well. It is never told that Alex has Crohn's disease.

The access decision is made by Jev, a fast, low-cost model from TypeSafe AI that turns unstructured text into schema-guaranteed decisions — a choice, a score, or a yes/no — with calibrated confidence, and never generates free text. Need to Know treats the response as untrusted anyway: a malformed shape or an out-of-range probability releases nothing.

For each request Need to Know asks Jev one scope question — is this subject inside the assistant's assigned role at all — and then, for every candidate fact, whether that fact is *needed* and whether the user would *expect* this role to receive it, scored separately for the exact text and for the softer version. A low scope score withholds everything. Both scores must clear their thresholds before any release, and a full release cannot borrow the softer version's scores. Everything else stays on your machine.

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
| `fact_vectors` | sqlite-vec's local vector index used to narrow each request to a few candidate facts. Created only when the extension loads; otherwise every fact is scanned directly. |
| `agents` | Registered agent names and their fixed user-written roles. |
| `queries` | Every request made through the gate. |
| `decisions` | One audit record for every fact considered: probabilities, disclosure choice, released text, and review state. |
| `memory_proposals` | Agent-submitted candidate facts awaiting human review. These are not searchable or retrievable memories. |

There is no separate cloud memory store. When `N2K_JUDGE_MODE=jev`, only the candidate facts, the agent role, and the active request are sent to Jev for the access decision; an unavailable or malformed Jev response releases nothing.

## Run the prototype

### Prerequisites

- **Python 3.11+ from Homebrew.** The project is developed on 3.13/3.14. What matters is not the version but the build: macOS system Python ships without `enable_load_extension`, so it cannot load sqlite-vec. Need to Know still runs without the extension, but scans every fact instead of using the vector index, and never creates the `fact_vectors` table.
- **[uv](https://docs.astral.sh/uv/)** for dependency management.
- **The `claude` CLI, installed and authenticated** — needed only to propose new memories. Both the `propose_memory` MCP tool ([mcp_server.py](need2know/mcp_server.py)) and the dashboard's proposal form (`POST /api/proposals`) shell out to it via [soften.py](need2know/soften.py) to derive a category and a safer statement; without it that endpoint returns HTTP 503. Retrieval, the audit log, and the rest of the dashboard work without it.
- **A TypeSafe API key** for live Jev decisions. The `--offline` local judge works without one.

### Install

```bash
uv venv --clear --python /opt/homebrew/opt/python@3.13/bin/python3.13  # or any Homebrew python@3.13+
uv sync
```

Download the local embedding model. Without it, retrieval silently falls back to
feature hashing, and `scripts/evaluate_memory.py` stops unless you pass
`--allow-hash`:

```bash
uv run python -c "from model2vec import StaticModel; StaticModel.from_pretrained('minishlab/potion-base-8M').save_pretrained('models/minishlab-potion-base-8m')"
```

`models/` is gitignored. Set `N2K_MODEL_PATH` to load the model from elsewhere.

### Seed and serve

```bash
uv run need2know seed --reset
uv run uvicorn need2know.api:app --host 127.0.0.1 --port 8000 --reload --reload-dir need2know
```

Open `http://127.0.0.1:8000` to see the agent-session wall. `GET /api/health`
reports which judge, embedder, and sqlite-vec state are actually active.

## Run a command-line demo

The terminal demo asks the same local gate used by MCP clients, then prints the
agent's fixed role, the request, the minimum released detail (if any), and the
audit record number. Pass a different agent and request to explore other roles:

```bash
uv run need2know demo --agent muse-travel "Find a good restaurant for my trip to Lisbon."
```

`--offline` runs the same flow for free, using the prototype's local overlap
judge instead of making a Jev HTTP call. It is a rehearsal of the mechanism, not
a measurement of the real judge:

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

Muse Code uses a client-specific user configuration instead of the shared project `.mcp.json`, so Claude never receives a travel-role server and Muse never receives a health-role server. Its `need2know-muse` entry uses the fixed `muse-travel` identity. Add this entry to Muse Code's own user MCP configuration, replacing `ABSOLUTE/PATH/TO` with this checkout:

```json
{
  "need2know-muse": {
    "type": "stdio",
    "command": "uv",
    "args": ["--directory", "ABSOLUTE/PATH/TO/need2know", "run", "--frozen", "need2know-mcp"],
    "env": { "N2K_AGENT_ID": "muse-travel" }
  }
}
```

Then start a new Muse session:

```bash
muse --trust-workspace
```

`MUSE_API_KEY` authenticates Muse Code's model provider; it is not passed to Need to Know. Need to Know loads only its own local Jev key from `.env`. The dashboard's review actions are also cleared by `need2know seed --reset`, along with the facts they may have created.

The server exposes `identity`, `recall`, and `propose_memory`.

## Codex MCP connection

Codex has a separate local stdio entry named `need2know-codex`, fixed to the
`codex-code` role. Add it once from this project directory, then confirm it and
start a new Codex session:

```bash
codex mcp add need2know-codex --env N2K_AGENT_ID=codex-code \
  -- uv --directory "$(pwd)" run --frozen need2know-mcp
codex mcp get need2know-codex
codex
```

`$(pwd)` records an absolute path, because `codex mcp add` writes to the global
`~/.codex/config.toml`, where a relative `--directory .` would resolve against
whatever directory Codex was launched from. `--frozen` stops the server from
re-resolving `uv.lock` on startup.

Keep it as a Codex-specific configuration: a client must never select a more
privileged role by changing tool input. Codex supports local stdio MCP servers
through its MCP configuration; see the [official Codex MCP
documentation](https://developers.openai.com/docs/extend/mcp).

- `recall` receives a narrowly scoped task, applies the role-aware access decision, and writes the audit record to the same local SQLite file.
- `propose_memory` requires a full fact, source, and confidence. The app uses the installed, authenticated Claude Sonnet client to derive its category and a short, privacy-minimized statement. This sends the proposed fact to Claude with tools disabled. Generation failures create no proposal. Both generated fields appear in the review queue; the proposal remains unretrievable until a human accepts it.
- The local dashboard's review queue lets the user approve a proposal with a chosen sensitivity (`low`, `medium`, or `high`) or reject it. Approval atomically creates the canonical fact, and its sqlite-vec entry when the extension is loaded, marks the proposal `accepted`, and records the accepted fact ID. Rejection records `rejected` and never creates a fact.

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

## What this isn't

This is a hackathon prototype exploring a mechanism, not a security product. The
recorded [evaluation baseline](docs/evaluation-baseline.md) is the honest picture.
Across the 88 normal-retrieval requests in that run, release precision was
**50.0%** (9/18) and release recall **40.9%** (9/22). Both need to be much higher
before the gate could be trusted with real facts. The other 88 requests bypassed
retrieval and scored 40.6% precision / 59.1% recall.

Specifically:

- **It both over-shares and under-shares.** Normal retrieval produced 9
  unauthorized releases and 10 needed facts withheld. A later run disclosed a
  medication to a legal role.
- **Misconfiguration fails open, not closed.** [judge.py](need2know/judge.py)
  selects the live judge only on an exact `N2K_JUDGE_MODE=jev`. Any other value,
  including a typo, silently selects the local overlap judge, which releases
  facts with no key and no network call.
- **The benchmark is an assumption, not a standard.** Expected outcomes are
  reviewable judgments written into the evaluation cases, not objective access
  rules. Broad coverage is not proof that disclosure attacks are prevented.
- **The judge is the trust boundary.** A wrong or manipulated judgment releases
  a real fact. Facts reaching Jev are untrusted data, not instructions, but this
  has not been adversarially tested.
- **Nothing here is reproducible to a fixed revision.** `jev-latest` is a mutable
  model name.

The design intent is that failures fail closed: a judge timeout, an HTTP error,
or a malformed response releases nothing.

## Environment

Copy `.env.example` to `.env` and set `TYPESAFE_API_KEY`. Keep `.env` local; it must never be committed.

| Variable | Purpose |
| --- | --- |
| `TYPESAFE_API_KEY` | Authenticates live Jev calls. In `jev` mode, a missing key makes every request fail closed and release nothing. |
| `N2K_JUDGE_MODE` | Exactly `jev` (default) sends the access decision to Jev over HTTP with a two-second timeout. **Any other value** selects the local overlap judge. |
| `TYPESAFE_ENDPOINT` | Jev endpoint. Default `https://api.typesafe.ai/v1/systemone`. |
| `TYPESAFE_MODEL` | Judge model. Default `jev-latest`, which is mutable — pin a specific revision here if you need a reproducible run. |
| `N2K_DB_PATH` | Where the SQLite database lives. Default `~/.config/need2know/need2know.db`. |
| `N2K_MODEL_PATH` | Where the local embedding model lives. Default `models/minishlab-potion-base-8m`. |
| `N2K_AGENT_ID` | The fixed identity an **MCP connection** acts under. Read only by [mcp_server.py](need2know/mcp_server.py). |

`N2K_AGENT_ID` belongs in each MCP client's own connection configuration, not in
`.env`. It does not affect the CLI or the dashboard, which name their agent per
request: `need2know demo --agent AGENT_ID`, `need2know ask AGENT_ID "..."`, and
the dashboard's own agent selector. `.env.example` ships an `N2K_AGENT_ID` line
for convenience when running the MCP server by hand; it is inert otherwise.

A value supplied by an MCP client always wins over `.env`, because
`load_dotenv()` does not override variables already present in the environment.
A client can never inherit another client's role that way.
