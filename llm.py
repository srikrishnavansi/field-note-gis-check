"""Minimal Claude caller with a spend log and a hard budget stop. Key comes from ANTHROPIC_API_KEY."""
import json, os
from datetime import datetime, timezone
from pathlib import Path
import anthropic

USAGE = Path(__file__).parent / "runs" / "usage.jsonl"
CAP_USD = float(os.environ.get("CAP_USD", "2.0"))
RESERVE_USD = 0.0
PRICE = {"claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}  # $ per MTok in/out
_client = anthropic.Anthropic(max_retries=4, timeout=90.0)


def spent(pack=None):
    if not USAGE.exists():
        return 0.0
    rows = [json.loads(l) for l in USAGE.read_text().splitlines() if l.strip()]
    return sum(r["usd"] for r in rows if pack is None or r["pack"] == pack)


def call(pack, stage, model, system, user, schema=None, max_tokens=6000, effort="medium"):
    if spent() + RESERVE_USD > CAP_USD:
        raise SystemExit(f"budget stop: ${spent():.2f} spent of ${CAP_USD}")
    oc = {"effort": effort}
    if schema:
        oc["format"] = {"type": "json_schema", "schema": schema}
    with _client.messages.stream(model=model, max_tokens=max_tokens, system=system, output_config=oc,
                                 messages=[{"role": "user", "content": user}]) as s:
        r = s.get_final_message()
    u = r.usage
    pin, pout = PRICE[model]
    USAGE.parent.mkdir(exist_ok=True)
    with USAGE.open("a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "pack": pack, "stage": stage,
                            "model": model, "in": u.input_tokens, "out": u.output_tokens,
                            "usd": round((u.input_tokens * pin + u.output_tokens * pout) / 1e6, 6)}) + "\n")
    if r.stop_reason in ("refusal", "max_tokens"):
        raise RuntimeError(f"{stage}: stop_reason={r.stop_reason}")
    text = "".join(b.text for b in r.content if b.type == "text").strip()
    return json.loads(text) if schema else text
