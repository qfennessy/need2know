from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import replace

from .config import Settings
from .seed import seed
from .service import make_store, query


def _demo_report(result: dict) -> str:
    """Render the same disclosure result as a short, human-readable terminal demo."""
    agent = result["agent"]
    lines = [
        "Need to Know · local memory switch",
        f"Agent: {agent['id']}",
        f"Fixed role: {agent['purpose']}",
        f"Request: {result['request']}",
        "",
    ]
    if result["memories"]:
        lines.append("Released (minimum useful detail):")
        lines.extend(
            f"  - [{memory['disclosure']}] {memory['memory']}"
            for memory in result["memories"]
        )
    else:
        lines.append("Released: nothing")
    lines.extend(
        [
            "",
            f"Checked {result['candidate_count']} local candidates; kept {result['withheld_count']} private.",
            f"Audit record: #{result['query_id']} · judge status: {result['status']}",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(prog="need2know")
    commands = parser.add_subparsers(dest="command", required=True)
    seed_parser = commands.add_parser("seed", help="load the fictional demo person and agents")
    seed_parser.add_argument("--reset", action="store_true")
    ask = commands.add_parser("ask", help="simulate one agent request")
    ask.add_argument("agent_id")
    ask.add_argument("request")
    demo = commands.add_parser("demo", help="show a readable local memory-switch demo")
    demo.add_argument(
        "request",
        nargs="?",
        default="Find a good restaurant for my trip to Lisbon.",
        help="the task the selected agent needs help with",
    )
    demo.add_argument("--agent", default="muse-travel", help="registered agent id (default: muse-travel)")
    demo.add_argument(
        "--offline",
        action="store_true",
        help="use the local overlap judge; makes no Jev HTTP request",
    )
    args = parser.parse_args()
    settings = Settings.from_env()
    store = make_store(settings)
    if args.command == "seed":
        seed(store, args.reset)
        print(f"Seeded {len(__import__('need2know.seed', fromlist=['FACTS']).FACTS)} facts in {settings.db_path}")
    elif args.command == "demo":
        if args.offline:
            settings = replace(settings, judge_mode="offline")
        result = asyncio.run(query(settings, store, args.agent, args.request, client="cli-demo"))
        print(_demo_report(result))
    else:
        print(json.dumps(asyncio.run(query(settings, store, args.agent_id, args.request)), indent=2))


if __name__ == "__main__":
    main()
