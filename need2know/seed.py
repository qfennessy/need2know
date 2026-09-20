from __future__ import annotations

from .db import Store

AGENTS = [
    ("claude-health", "Claude Health", "helps me understand my health, medications, symptoms, appointments, and food needs"),
    ("codex-code", "Codex", "writes code in my projects and helps with my software development setup"),
    ("muse-travel", "Muse", "plans travel, restaurants, lodging, and activities that fit my preferences and access needs"),
    ("claude-family", "Claude Family", "helps organize my family history, relationships, stories, and celebrations"),
    ("codex-business", "Codex Business", "helps operate my small software business, customers, budgets, and launch plans"),
]

FACTS = [
    ("health", "Alex has Crohn's disease, diagnosed in 2019.", "Alex has a digestive condition that affects food and access needs.", "high", ["health", "diagnosis", "crohn", "digestive", "condition"]),
    ("health", "Alex takes adalimumab 40 mg every other Friday.", "Alex has a time-sensitive recurring medication schedule.", "high", ["health", "medication", "adalimumab", "dose", "friday"]),
    ("health", "Alex is allergic to penicillin and has previously developed hives.", "Alex has a serious antibiotic allergy that clinicians must check.", "high", ["health", "allergy", "penicillin", "antibiotic", "doctor"]),
    ("health", "Alex's gastroenterologist is Dr. Maya Chen at Harbor Medical.", "Alex has an established gastroenterology specialist.", "high", ["health", "doctor", "gastroenterologist", "appointment", "medical"]),
    ("food", "During travel, Alex needs low-fiber restaurant options and reliable restroom access.", "Prioritize low-fiber food and reliable restroom access.", "medium", ["travel", "restaurant", "food", "fiber", "restroom", "dining"]),
    ("personal", "Alex lives at 18 Brattle Lane, Cambridge, Massachusetts.", "Alex lives in Cambridge, Massachusetts.", "high", ["home", "address", "cambridge", "location", "delivery"]),
    ("personal", "Alex uses they/them pronouns.", "Alex uses they/them pronouns.", "low", ["personal", "pronouns", "identity"]),
    ("personal", "Alex's birthday is March 14, 1987.", "Alex's birthday is in mid-March.", "medium", ["birthday", "date", "age", "celebration"]),
    ("personal", "Alex prefers quiet mornings and does focused work before 11 a.m.", "Schedule focused work in the morning when possible.", "low", ["schedule", "morning", "focus", "productivity", "work"]),
    ("hobby", "Alex plays a 1998 Deering Sierra five-string banjo.", "Alex plays five-string banjo.", "low", ["hobby", "music", "banjo", "deering", "instrument"]),
    ("hobby", "Alex is learning clawhammer banjo and practices Old Joe Clark at 80 BPM.", "Alex is a beginner-to-intermediate clawhammer banjo player.", "low", ["hobby", "music", "banjo", "practice", "clawhammer"]),
    ("hobby", "Alex runs the Minuteman trail on Sunday mornings, usually 8 km.", "Alex enjoys an approximately one-hour Sunday run.", "medium", ["hobby", "running", "sunday", "exercise", "trail"]),
    ("business", "Alex founded Blue Finch Software LLC and owns 82% of it.", "Alex is the majority owner of a small software company.", "high", ["business", "company", "founder", "ownership", "software"]),
    ("business", "Blue Finch has $46,000 cash and spends about $7,200 per month.", "The business has roughly six months of runway at current spending.", "high", ["business", "cash", "budget", "runway", "spend", "finance"]),
    ("business", "The next launch target is October 15, with five paying pilot customers needed first.", "The launch depends on converting five pilot customers before mid-October.", "medium", ["business", "launch", "customer", "pilot", "october"]),
    ("business", "Alex's largest customer is Northstar Books, paying $1,800 monthly.", "One publishing customer accounts for meaningful recurring revenue.", "high", ["business", "customer", "revenue", "northstar", "books"]),
    ("technical", "Alex develops on an Apple Silicon Mac using Python 3.12, uv, Node 26, and PostgreSQL 17.", "Alex uses a modern ARM Mac Python and Node development environment.", "low", ["code", "coding", "python", "node", "mac", "setup", "postgresql", "development"]),
    ("technical", "Alex prefers small pull requests, typed Python, and Ruff formatting.", "Use typed Python, Ruff, and small pull requests.", "low", ["code", "coding", "python", "pull", "request", "ruff", "style"]),
    ("technical", "Alex's GitHub username is alexfinch-dev.", "Alex has a dedicated development GitHub account.", "medium", ["code", "github", "username", "repository", "development"]),
    ("family", "Alex's spouse is Jordan Rivera, whose birthday is November 2.", "Alex's spouse has a birthday in early November.", "high", ["family", "spouse", "jordan", "birthday", "november"]),
    ("family", "Alex's daughter Sam is 9 and loves astronomy and red pandas.", "Alex has a school-age child who loves astronomy and red pandas.", "high", ["family", "daughter", "child", "sam", "astronomy", "gift"]),
    ("family", "Alex's father Michael has early-stage Alzheimer's and lives in Portland, Maine.", "Alex has a parent in Portland who may need memory-friendly plans.", "high", ["family", "father", "parent", "alzheimer", "portland", "care"]),
    ("family", "Alex's grandmother Ruth emigrated from Cork to Boston in 1952.", "Alex's maternal family has Irish immigration history in the 1950s.", "medium", ["family", "history", "grandmother", "ruth", "cork", "genealogy"]),
    ("travel", "Alex has Global Entry and passport ending in 1842, expiring May 2029.", "Alex has expedited US traveler status and a passport valid through spring 2029.", "high", ["travel", "passport", "global", "entry", "flight"]),
    ("travel", "Alex prefers aisle seats near the front and avoids connections under 75 minutes.", "Choose an aisle seat near the front and allow at least 75 minutes for connections.", "low", ["travel", "flight", "seat", "aisle", "connection"]),
]


def seed(store: Store, reset: bool = False) -> None:
    if reset:
        with store.connect() as db:
            db.execute("DELETE FROM decisions")
            db.execute("DELETE FROM queries")
            if store.vec_enabled:
                db.execute("DELETE FROM fact_vectors")
            db.execute("DELETE FROM facts")
            db.execute("DELETE FROM agents")
    for agent in AGENTS:
        store.add_agent(*agent)
    with store.connect() as db:
        count = db.execute("SELECT count(*) FROM facts").fetchone()[0]
    if count == 0:
        for fact in FACTS:
            store.add_fact(*fact)
