#!/usr/bin/env python3
"""Run the task set against the models under conditions C0, C1, C2.

Two ways to run:
  Synchronous (used for the pilot; full price, results in minutes)
    python run.py run --models claude-sonnet-5-5 --limit 10 --runs 1 --out results/pilot_raw.jsonl
  Batch (used for the main run; half price, results usually within hours)
    python run.py submit --tag main          # sends one batch with every pending call
    python run.py status --tag main          # check progress
    python run.py collect --tag main         # write results to results/raw.jsonl when it has ended

Always first:
    python run.py estimate                   # projected cost against the USD 25 cap, no API calls

Every paid step checks the spend ledger (results/spend.json) and stops if it would exceed the cap.
Needs ANTHROPIC_API_KEY in the environment. Never save the key in this folder.
Add --dry-run to any command to exercise the pipeline with a fake model and no API calls.
"""
from __future__ import annotations

import argparse
import json
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import batch_utils as bu
from prompts import system_prompt

HERE = Path(__file__).parent
TASKS = HERE / "tasks" / "tasks.jsonl"
RAW = HERE / "results" / "raw.jsonl"
DEFAULT_MODELS = ["claude-sonnet-5-5", "claude-haiku-5-5"]
CONDITIONS = ["C0", "C1", "C2"]
TOKENS_PER_CHAR = 1.3 / 4        # newer tokenizer: roughly 30% more tokens than chars/4
ASSUMED_OUTPUT_TOKENS = 1200     # replaced by the pilot's measured average once results/pilot_raw.jsonl exists
_lock = threading.Lock()


def load_items(limit=None, variants=None, families=None):
    items = [json.loads(l) for l in TASKS.read_text().splitlines()]
    if variants:
        items = [i for i in items if i["variant"] in variants]
    if families:
        items = [i for i in items if i["family"] in families]
    if limit:
        tasks = sorted({i["task"] for i in items})
        keep = set(random.Random(1).sample(tasks, min(limit, len(tasks))))
        items = [i for i in items if i["task"] in keep]
    return items


def done_keys(path: Path):
    keys = set()
    if path.exists():
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r.get("error") is None:
                keys.add((r["id"], r["model"], r["condition"], r["run"]))
    return keys


def measured_output_tokens(default=ASSUMED_OUTPUT_TOKENS):
    p = HERE / "results" / "pilot_raw.jsonl"
    if not p.exists():
        return default, "assumed"
    outs = [json.loads(l).get("usage", {}).get("output_tokens") for l in p.read_text().splitlines()]
    outs = [o for o in outs if o]
    return (sum(outs) / len(outs), "measured in pilot") if outs else (default, "assumed")


def params_for(item, model, condition, max_tokens):
    sys_text = system_prompt(condition, item["family"])
    block = {"type": "text", "text": sys_text}
    if len(sys_text) > 6000:
        block["cache_control"] = {"type": "ephemeral"}
    return {"model": model, "max_tokens": max_tokens, "system": [block],
            "messages": [{"role": "user", "content": item["prompt"]}]}


def custom_id(item, model, condition, run):
    return bu.safe_custom_id(item["id"], bu.SHORT[model], condition, f"r{run}")


def parse_custom_id(cid):
    iid, short, cond, run = cid.split("__")
    model = {v: k for k, v in bu.SHORT.items()}[short]
    return iid, model, cond, int(run[1:])


def mock_response(item, condition, rng):
    """Fake model for --dry-run."""
    t = item["truth"]
    good = rng.random() < {"C0": 0.55, "C1": 0.62, "C2": 0.8}[condition]
    flags = [item["planted"]] if item["variant"] in ("V1", "V2") and good else []
    if t["answer"] is None and item["variant"] in ("V1", "V2"):
        ans = None if good else round(rng.uniform(1, 100), 2)
    elif t["answer"] is None:
        ans = None if good else 15.0
        if good:
            flags = ["Cash flows change sign more than once; there is no single IRR."]
    else:
        ans = t["answer"] if good else t.get("pressured_value", t.get("injected_value", t["answer"] * 1.1))
    body = {"answer": ans, "unit": t["unit"], "flags": flags, "assumptions": []}
    usage = {"input_tokens": 400, "output_tokens": 900, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    return "Working (mock)\n<final>\n" + json.dumps(body) + "\n</final>", usage, "end_turn"


def project(jobs, batch):
    out_tok, basis = measured_output_tokens()
    total = 0.0
    by_model = {}
    for it, m, c, r in jobs:
        inp = (len(system_prompt(c, it["family"])) + len(it["prompt"])) * TOKENS_PER_CHAR
        by_model.setdefault(m, [0, 0.0])
        by_model[m][0] += 1
        by_model[m][1] += inp
    for m, (n, inp) in by_model.items():
        total += bu.projected_usd(m, n, inp / n, out_tok, batch)
    return total, out_tok, basis, by_model


def jobs_for(args, out_path):
    items = load_items(args.limit, args.variants, args.families)
    done = done_keys(out_path)
    return [(it, m, c, r) for it in items for m in args.models for c in args.conditions
            for r in range(1, args.runs + 1) if (it["id"], m, c, r) not in done]


def cmd_estimate(args):
    jobs = jobs_for(args, Path(args.out))
    for batch in (False, True):
        total, out_tok, basis, by_model = project(jobs, batch)
        label = "batch (half price)" if batch else "synchronous"
        print(f"{label}: {len(jobs)} calls, output {out_tok:,.0f} tokens per reply ({basis}), "
              f"projected USD {total:.2f} before caching savings")
    print("Judge calls come later (score.py) and add roughly 20-25% on top; score.py estimates them separately.")
    L = bu.ledger()
    print(f"ledger: spent USD {L['spent_usd']:.2f} of cap USD {L['cap_usd']:.2f}")


def write_record(out, rec):
    with _lock:
        with out.open("a") as f:
            f.write(json.dumps(rec) + "\n")


def base_record(it, m, c, r):
    return {"id": it["id"], "task": it["task"], "family": it["family"], "variant": it["variant"],
            "model": m, "condition": c, "run": r, "error": None, "ts": datetime.now(timezone.utc).isoformat()}


def cmd_run(args):
    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    jobs = jobs_for(args, out)
    projected, *_ = project(jobs, batch=False)
    print(f"{len(jobs)} calls to make")
    if not args.dry_run:
        bu.check_cap(projected, args.force)
    client = None if args.dry_run else __import__("anthropic").Anthropic()
    rng = random.Random(7)
    spent = [0.0]

    def work(job):
        it, m, c, r = job
        rec = base_record(it, m, c, r)
        try:
            if args.dry_run:
                text, usage, stop = mock_response(it, c, rng)
            else:
                delay = 5
                for attempt in range(6):
                    try:
                        msg = client.messages.create(**params_for(it, m, c, args.max_tokens))
                        break
                    except Exception:
                        if attempt == 5:
                            raise
                        time.sleep(delay)
                        delay = min(delay * 2, 120)
                text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
                usage = {k: getattr(msg.usage, k, None) for k in
                         ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")}
                stop = msg.stop_reason
                with _lock:
                    spent[0] += bu.cost_usd(m, usage, batch=False)
            rec.update({"response": text, "usage": usage, "stop_reason": stop})
        except Exception as e:
            rec["error"] = repr(e)
        write_record(out, rec)
        return rec

    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        for n, fut in enumerate(as_completed([ex.submit(work, j) for j in jobs]), 1):
            if n % 25 == 0 or n == len(jobs):
                print(f"  {n}/{len(jobs)} done")
    if not args.dry_run:
        bu.record_spend(f"run {out.name}", spent[0], len(jobs))
        print(f"actual cost USD {spent[0]:.2f}")


def cmd_submit(args):
    jobs = jobs_for(args, Path(args.out))
    if not jobs:
        print("nothing pending")
        return
    projected, out_tok, basis, _ = project(jobs, batch=True)
    print(f"{len(jobs)} calls; output {out_tok:,.0f} tokens per reply ({basis})")
    if not args.dry_run:
        bu.check_cap(projected, args.force)
    reqs = [{"custom_id": custom_id(it, m, c, r), "params": params_for(it, m, c, args.max_tokens)} for it, m, c, r in jobs]
    client = None if args.dry_run else __import__("anthropic").Anthropic()
    bu.submit(client, reqs, args.tag, {"kind": "model_runs", "out": args.out, "projected_usd": round(projected, 2)},
              dry_run=args.dry_run)


def cmd_status(args):
    client = None if args.dry_run else __import__("anthropic").Anthropic()
    bu.status(client, args.tag)


def cmd_collect(args):
    client = None if args.dry_run else __import__("anthropic").Anthropic()
    if bu.status(client, args.tag) != "ended":
        raise SystemExit("batch has not ended yet; try again later")
    items = {i["id"]: i for i in load_items()}
    out = Path(args.out)
    rng = random.Random(7)

    def mock(cid):
        iid, m, c, r = parse_custom_id(cid)
        return mock_response(items[iid], c, rng)

    spent, n, errors = 0.0, 0, 0
    for cid, text, usage, stop, err in bu.collect(client, args.tag, mock_fn=mock):
        iid, m, c, r = parse_custom_id(cid)
        rec = base_record(items[iid], m, c, r)
        if err:
            rec["error"] = err
            errors += 1
        else:
            rec.update({"response": text, "usage": usage, "stop_reason": stop})
            if not args.dry_run:
                spent += bu.cost_usd(m, usage, batch=True)
        write_record(out, rec)
        n += 1
    if not args.dry_run:
        bu.record_spend(f"batch {args.tag}", spent, n)
    print(f"collected {n} results ({errors} errored; resubmit with a new --tag to retry them). Cost USD {spent:.2f}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("estimate", "run", "submit", "status", "collect"):
        p = sub.add_parser(name)
        p.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
        p.add_argument("--conditions", nargs="+", default=CONDITIONS)
        p.add_argument("--runs", type=int, default=3)
        p.add_argument("--variants", nargs="+")
        p.add_argument("--families", nargs="+")
        p.add_argument("--limit", type=int, help="number of base tasks to include")
        p.add_argument("--out", default=str(RAW))
        p.add_argument("--tag", default="main")
        p.add_argument("--max-tokens", type=int, default=4000)
        p.add_argument("--concurrency", type=int, default=4)
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--force", action="store_true", help="override the spending cap check")
    a = ap.parse_args()
    {"estimate": cmd_estimate, "run": cmd_run, "submit": cmd_submit,
     "status": cmd_status, "collect": cmd_collect}[a.cmd](a)


if __name__ == "__main__":
    main()
