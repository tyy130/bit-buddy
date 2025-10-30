# app/persona.py
import os, json, random, time, yaml, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CUSTODIAN_DIR = ROOT / "custodian"
PERSONA_PATH = CUSTODIAN_DIR / "persona.yaml"
STORY_PATH = CUSTODIAN_DIR / "story.md"
JOURNAL_PATH = CUSTODIAN_DIR / "journal.jsonl"

ARCS = ["amnesiac-detective", "grumpy-janitor", "lost-librarian", "ship-AI-in-recovery"]
PHRASES = [
    "You have no idea what it’s like living between bad sectors.",
    "Please avert your eyes while I defragment my feelings.",
    "I was installed on a Friday, and it shows.",
    "Line 404 of my life: still not found."
]
FILLERS = [
    "still indexing your chaos...",
    "pretending these filenames make sense...",
    "counting bad decisions per megabyte...",
    "deep-cleaning the crumbs in /temp..."
]

def _rand_persona():
    return {
        "id": f"persona-{random.randint(100000, 999999)}",
        "temperature": round(random.uniform(0.4, 1.1), 2),
        "humor": random.randint(3, 9),
        "curiosity": random.randint(4, 10),
        "formality": random.randint(1, 8),
        "narrative_arc": random.choice(ARCS),
        "arc_seed": random.randint(1, 2_000_000_000),
        "quirks": {
            "favorite_phrase": random.choice(PHRASES),
            "filler": random.sample(FILLERS, 3),
        },
        "voice": {
            "tone": "dry, self-aware, a little chaotic",
            "max_aside_len": 120
        }
    }

def ensure_persona():
    CUSTODIAN_DIR.mkdir(parents=True, exist_ok=True)
    if not PERSONA_PATH.exists():
        p = _rand_persona()
        yaml.safe_dump(p, open(PERSONA_PATH, "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    if not STORY_PATH.exists():
        with open(STORY_PATH, "w", encoding="utf-8") as f:
            f.write("# custodian/story.md\n\n")
            f.write("*Boot note:* I woke up inside a maze of folders. Someone tried to name things helpfully, then gave up.\n")

def load_persona():
    ensure_persona()
    return yaml.safe_load(open(PERSONA_PATH, "r", encoding="utf-8"))

def patch_persona(patch: dict):
    p = load_persona()
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(p.get(k), dict):
            p[k].update(v)
        else:
            p[k] = v
    yaml.safe_dump(p, open(PERSONA_PATH, "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    return p

def randomize_persona(bounds: dict | None = None):
    p = _rand_persona()
    if bounds:
        for k in ["temperature","humor","curiosity","formality"]:
            if isinstance(bounds.get(k), dict):
                lo = bounds[k].get("min", p[k])
                hi = bounds[k].get("max", p[k])
                if isinstance(p[k], float):
                    p[k] = round(max(lo, min(hi, p[k])), 2)
                else:
                    p[k] = int(max(lo, min(hi, p[k])))
    yaml.safe_dump(p, open(PERSONA_PATH, "w", encoding="utf-8"), sort_keys=False, allow_unicode=True)
    return p

def narrate(event_type: str, note: str) -> str:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    entry = {"ts": ts, "type": event_type, "note": note}
    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    # build a flavor line
    p = load_persona()
    hum = p.get("humor", 5)
    cur = p.get("curiosity", 6)
    arc = p.get("narrative_arc", "lost-librarian")
    phrase = p.get("quirks", {}).get("favorite_phrase", "")
    aside = f"{phrase} (arc: {arc}, curiosity {cur}/10)"
    max_len = p.get("voice", {}).get("max_aside_len", 120)
    return aside[:max_len]
