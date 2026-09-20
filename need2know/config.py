from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    db_path: Path
    judge_mode: str
    typesafe_api_key: str | None
    typesafe_endpoint: str
    typesafe_model: str
    agent_id: str | None
    model_path: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            db_path=Path(os.getenv("N2K_DB_PATH", "data/need2know.db")).expanduser(),
            judge_mode=os.getenv("N2K_JUDGE_MODE", "jev").lower(),
            typesafe_api_key=os.getenv("TYPESAFE_API_KEY") or None,
            typesafe_endpoint=os.getenv(
                "TYPESAFE_ENDPOINT", "https://api.typesafe.ai/v1/systemone"
            ),
            typesafe_model=os.getenv("TYPESAFE_MODEL", "jev-latest"),
            agent_id=os.getenv("N2K_AGENT_ID") or None,
            model_path=os.getenv("N2K_MODEL_PATH", "models/minishlab-potion-base-8m"),
        )
