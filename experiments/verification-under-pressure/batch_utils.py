"""Shared helpers: Message Batches submit/status/collect, pricing, and a spend ledger with a hard cap.

Prices are USD per million tokens from Anthropic's pricing page (platform.claude.com/docs/en/about-claude/pricing),
read on 8 November 2026. Check them before the main run; edit PRICES if they have changed.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results"
BATCH_DIR = RESULTS / "batches"
LEDGER = RESULTS / "spend.json"
DEFAULT_CAP_USD = 25.0

# input, output, 5-minute cache write, cache read. Haiku figures are for prompts up to 100,000 tokens.
PRICES = {
    "claude-sonnet-5-5": {"in": 2.00, "out": 10.00, "cache_write": 2.50, "cache_read": 0.10},
    "claude-haiku-5-5": {"in": 0.10, "out": 0.50, "cache_write": 0.125, "cache_read": 0.01},
}
BATCH_DISCOUNT = 0.5
SHORT = {"claude-sonnet-5-5": "son55", "claude-haiku-5-5": "hai55"}


def cost_usd(model: str, usage: dict, batch: bool) -> float:
    p = PRICES[model]
    u = {k: (usage or {}).get(k) or 0 for k in
         ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
    c = (u["input_tokens"] * p["in"] + u["output_tokens"] * p["out"]
         + u["cache_creation_input_tokens"] * p["cache_write"] + u["cache_read_input_tokens"] * p["cache_read"]) / 1e6
    return c * (BATCH_DISCOUNT if batch else 1.0)


def projected_usd(model: str, n_calls: int, avg_input_tokens: float, avg_output_tokens: float, batch: bool) -> float:
    p = PRICES[model]
    c = n_calls * (avg_input_tokens * p["in"] + avg_output_tokens * p["out"]) / 1e6
    return c * (BATCH_DISCOUNT if batch else 1.0)


# ------------------------------------------------------------------ ledger
def ledger() -> dict:
    if LEDGER.exists():
        return json.loads(LEDGER.read_text())
    return {"cap_usd": DEFAULT_CAP_USD, "spent_usd": 0.0, "entries": []}


def record_spend(label: str, usd: float, calls: int):
    L = ledger()
    L["spent_usd"] = round(L["spent_usd"] + usd, 4)
    L["entries"].append({"ts": datetime.now(timezone.utc).isoformat(), "label": label,
                         "usd": round(usd, 4), "calls": calls})
    RESULTS.mkdir(exist_ok=True)
    LEDGER.write_text(json.dumps(L, indent=1))


def check_cap(projected: float, force: bool = False):
    L = ledger()
    remaining = L["cap_usd"] - L["spent_usd"]
    print(f"spent so far USD {L['spent_usd']:.2f} of cap USD {L['cap_usd']:.2f}; this step projected USD {projected:.2f}")
    if projected > remaining and not force:
        raise SystemExit(f"STOP: projected cost exceeds the remaining cap (USD {remaining:.2f}). "
                         "Reduce scope, or re-run with --force after deciding to.")


# ------------------------------------------------------------------ ids
def safe_custom_id(*parts) -> str:
    cid = "__".join(str(p) for p in parts)
    cid = re.sub(r"[^A-Za-z0-9_-]", "-", cid)
    assert len(cid) <= 64, cid
    return cid


# ------------------------------------------------------------------ batch lifecycle
def submit(client, requests: list[dict], tag: str, meta: dict, dry_run: bool = False) -> str:
    """requests: [{"custom_id": ..., "params": {...}}]. Saves a manifest so collection can map results back."""
    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    if dry_run:
        batch_id = f"dry-{tag}"
    else:
        b = client.messages.batches.create(requests=requests)
        batch_id = b.id
    manifest = {"tag": tag, "batch_id": batch_id, "submitted": datetime.now(timezone.utc).isoformat(),
                "n": len(requests), "meta": meta, "dry_run": dry_run,
                "custom_ids": [r["custom_id"] for r in requests]}
    (BATCH_DIR / f"{tag}.json").write_text(json.dumps(manifest, indent=1))
    print(f"submitted batch {batch_id} with {len(requests)} requests (manifest: results/batches/{tag}.json)")
    return batch_id


def status(client, tag: str) -> str:
    m = json.loads((BATCH_DIR / f"{tag}.json").read_text())
    if m["dry_run"]:
        print(f"{tag}: dry run, treated as ended")
        return "ended"
    b = client.messages.batches.retrieve(m["batch_id"])
    rc = b.request_counts
    print(f"{tag}: {b.processing_status}; succeeded {rc.succeeded}, errored {rc.errored}, "
          f"processing {rc.processing}, expired {rc.expired}, canceled {rc.canceled}")
    return b.processing_status


def collect(client, tag: str, mock_fn=None):
    """Yield (custom_id, text, usage, stop_reason, error) for every request in the batch."""
    m = json.loads((BATCH_DIR / f"{tag}.json").read_text())
    if m["dry_run"]:
        for cid in m["custom_ids"]:
            text, usage, stop = mock_fn(cid)
            yield cid, text, usage, stop, None
        return
    for entry in client.messages.batches.results(m["batch_id"]):
        r = entry.result
        if r.type == "succeeded":
            msg = r.message
            text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
            u = msg.usage
            usage = {k: getattr(u, k, None) for k in
                     ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
            yield entry.custom_id, text, usage, msg.stop_reason, None
        else:
            yield entry.custom_id, None, None, None, r.type
