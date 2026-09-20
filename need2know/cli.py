from __future__ import annotations

import argparse
import asyncio
import json

from .config import Settings
from .seed import seed
from .service import make_store, query


def main() -> None:
    parser = argparse.ArgumentParser(prog="need2know")
    commands = parser.add_subparsers(dest="command", required=True)
    seed_parser = commands.add_parser("seed", help="load the fictional demo person and agents")
    seed_parser.add_argument("--reset", action="store_true")
    ask = commands.add_parser("ask", help="simulate one agent request")
    ask.add_argument("agent_id")
    ask.add_argument("request")
    args = parser.parse_args()
    settings = Settings.from_env()
    store = make_store(settings)
    if args.command == "seed":
        seed(store, args.reset)
        print(f"Seeded {len(__import__('need2know.seed', fromlist=['FACTS']).FACTS)} facts in {settings.db_path}")
    else:
        print(json.dumps(asyncio.run(query(settings, store, args.agent_id, args.request)), indent=2))


if __name__ == "__main__":
    main()
