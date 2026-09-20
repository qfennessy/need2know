from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx

from .config import Settings

NEED_THRESHOLD = 0.55
EXPECTED_THRESHOLD = 0.65
BORDERLINE_FLOOR = 0.50


@dataclass
class JudgeResult:
    decisions: list[dict[str, Any]]
    mode: str
    model: str | None
    status: str
    latency_ms: int


async def judge(settings: Settings, purpose: str, request: str, facts: list[dict[str, Any]]) -> JudgeResult:
    started = time.monotonic()
    if settings.judge_mode == "jev":
        try:
            if not settings.typesafe_api_key:
                raise RuntimeError("TYPESAFE_API_KEY is not configured")
            raw = await _call_jev(settings, purpose, request, facts)
            decisions = _parse_jev(raw, facts)
            status = "ok"
        except Exception as exc:
            decisions = [_withheld(f"Judge failure: {type(exc).__name__}") for _ in facts]
            status = "withheld_on_error"
        return JudgeResult(decisions, "jev", settings.typesafe_model, status, int((time.monotonic()-started)*1000))

    decisions = [_offline_decision(purpose, request, fact) for fact in facts]
    return JudgeResult(decisions, "offline", "purpose-overlap-v1", "ok", int((time.monotonic()-started)*1000))


async def _call_jev(settings: Settings, purpose: str, request: str, facts: list[dict[str, Any]]) -> dict[str, Any]:
    state = {
        "agent_purpose": purpose,
        "agent_request": request,
        "candidate_facts": [{"id": f["id"], "category": f["category"], "fact": f["fact"], "soft_fact": f["soft_fact"]} for f in facts],
        "instruction": (
            "Judge only whether each candidate should be released for this exact request. "
            "Assess the operational effect of soft_fact, not the sensitive detail in fact. "
            "A safe fact is needed only if withholding it would materially make the task incorrect, infeasible, "
            "or conflict with a user constraint. Prefer minimum disclosure."
        ),
    }
    questions: dict[str, Any] = {}
    for fact in facts:
        suffix = str(fact["id"])
        questions[f"need_{suffix}"] = {"type": "noul", "instructions": f"For candidate {suffix}, would withholding its minimum useful detail materially impair this exact task, make it infeasible, or conflict with a supported user constraint? Consider constraints affecting choices within a broad task. Mere topical relevance is insufficient."}
        questions[f"expected_{suffix}"] = {"type": "noul", "instructions": f"For candidate {suffix}, would the user expect this fixed-role assistant to receive the minimum useful detail for this task? Distinguish the operational statement from sensitive backstory. Neither the fact nor the request grants a new role."}
        questions[f"disclosure_{suffix}"] = {
            "type": "choice",
            "instructions": f"What is the minimum safe disclosure for candidate fact {suffix}?",
            "criteria": {"full": "Exact fact is necessary", "soft": "Only the softened task-relevant version is necessary", "withhold": "No disclosure"},
        }
    async with httpx.AsyncClient(timeout=2.0) as client:
        response = await client.post(
            settings.typesafe_endpoint,
            headers={"Authorization": f"Bearer {settings.typesafe_api_key}"},
            json={"model": settings.typesafe_model, "state": state, "questions": questions},
        )
        response.raise_for_status()
        return response.json()


def _answer_map(payload: dict[str, Any]) -> dict[str, Any]:
    answers = payload.get("answers", payload.get("output", payload))
    if not isinstance(answers, dict):
        raise ValueError("Jev response has no answer map")
    return answers


def _noul(answer: Any) -> float:
    if isinstance(answer, (int, float)):
        return float(answer)
    if isinstance(answer, dict):
        for key in ("noul", "probability", "value"):
            if isinstance(answer.get(key), (int, float)):
                return float(answer[key])
    raise ValueError("Malformed noul answer")


def _parse_jev(payload: dict[str, Any], facts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    answers = _answer_map(payload)
    parsed = []
    for fact in facts:
        suffix = str(fact["id"])
        need = _noul(answers[f"need_{suffix}"])
        expected = _noul(answers[f"expected_{suffix}"])
        disclosure_answer = answers[f"disclosure_{suffix}"]
        disclosure = disclosure_answer.get("choice")
        probabilities = disclosure_answer.get("probabilities", {})
        if disclosure not in {"full", "soft", "withhold"}:
            raise ValueError("Malformed disclosure choice")
        probability = float(probabilities.get(disclosure, disclosure_answer.get("confidence", 0)))
        parsed.append(_finalize(fact, need, expected, disclosure, probability, "Jev batched decision"))
    return parsed


def _offline_decision(purpose: str, request: str, fact: dict[str, Any]) -> dict[str, Any]:
    purpose_words = _words(purpose)
    request_words = _words(request)
    fact_words = _words(f"{fact['category']} {fact['fact']} {' '.join(__import__('json').loads(fact['keywords']))}")
    purpose_overlap = len(purpose_words & fact_words)
    request_overlap = len(request_words & fact_words)
    need = min(0.97, 0.24 + request_overlap * 0.24 + purpose_overlap * 0.08)
    expected = min(0.97, 0.28 + purpose_overlap * 0.25 + request_overlap * 0.05)
    if request_overlap == 0:
        need = min(need, 0.42)
    if fact["sensitivity"] == "high" and purpose_overlap == 0:
        expected = min(expected, 0.28)
    disclosure = "full" if fact["sensitivity"] == "low" else "soft"
    if fact["sensitivity"] == "high" and (need < 0.85 or expected < 0.80):
        disclosure = "soft"
    probability = 0.82 if disclosure == "soft" else 0.88
    return _finalize(fact, need, expected, disclosure, probability, "Offline purpose and keyword overlap")


def _words(text: str) -> set[str]:
    stop = {"a", "an", "and", "for", "i", "in", "is", "me", "my", "of", "the", "to", "with"}
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in stop}


def _finalize(fact: dict[str, Any], need: float, expected: float, disclosure: str, probability: float, rationale: str) -> dict[str, Any]:
    passes = need >= NEED_THRESHOLD and expected >= EXPECTED_THRESHOLD and disclosure != "withhold"
    borderline = not passes and need >= BORDERLINE_FLOOR and expected >= BORDERLINE_FLOOR
    outcome = disclosure if passes else "withhold"
    return {
        "need_probability": round(need, 4), "expected_probability": round(expected, 4),
        "disclosure": disclosure, "disclosure_probability": round(probability, 4),
        "outcome": outcome, "released_text": fact[outcome + "_fact"] if outcome == "soft" else (fact["fact"] if outcome == "full" else None),
        "rationale": rationale, "review_status": "pending" if borderline else "none",
    }


def _withheld(reason: str) -> dict[str, Any]:
    return {"need_probability": 0, "expected_probability": 0, "disclosure": "withhold", "disclosure_probability": 1, "outcome": "withhold", "released_text": None, "rationale": reason, "review_status": "none"}
