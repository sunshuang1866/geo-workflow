#!/usr/bin/env python3
"""Batch sampling script for MindSpore assessment.
Calls doubao and qwen for each question, with rate limiting.
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)

# Load .env
env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

PLATFORMS = {}
if env_vars.get("DOUBAO_API_KEY"):
    PLATFORMS["doubao"] = {
        "api_key": env_vars["DOUBAO_API_KEY"],
        "base_url": "https://www.packyapi.com/v1",
        "model": "doubao-seed-2.0-pro",
        "delay": 1.0,
    }
if env_vars.get("QWEN_API_KEY"):
    PLATFORMS["qwen"] = {
        "api_key": env_vars["QWEN_API_KEY"],
        "base_url": "https://www.packyapi.com/v1",
        "model": "qwen3.5-plus",
        "delay": 1.5,
    }

if len(PLATFORMS) < 2:
    print("ERROR: Need at least 2 platforms. Check .env API keys.", file=sys.stderr)
    sys.exit(1)

print(f"Detected platforms: {list(PLATFORMS.keys())}")

# Load questions
questions_path = Path(__file__).resolve().parent / "questions.json"
with open(questions_path) as f:
    questions = json.load(f)

print(f"Questions: {len(questions)}")
print(f"Total calls: {len(questions) * len(PLATFORMS)}")

# Initialize clients
clients = {}
for name, cfg in PLATFORMS.items():
    clients[name] = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])

# Sampling
responses = []
total = len(questions) * len(PLATFORMS)
done = 0
errors = 0

for q in questions:
    qid = q["id"]
    query = q["question"]

    for pname, cfg in PLATFORMS.items():
        done += 1
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"  [{done}/{total}] {pname} <- {qid}: {query[:40]}...", flush=True)

        result = {
            "question_id": qid,
            "platform": pname,
            "query": query,
            "timestamp": timestamp,
            "raw_response": "",
            "citations": [],
            "model": cfg["model"],
            "status": "success",
        }

        try:
            resp = clients[pname].chat.completions.create(
                model=cfg["model"],
                messages=[{"role": "user", "content": query}],
                timeout=60,
            )
            result["raw_response"] = resp.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            result["status"] = "error"
            result["error"] = err_msg
            errors += 1
            print(f"    ERROR: {err_msg[:100]}", file=sys.stderr, flush=True)

            # Retry on 429
            if "429" in err_msg:
                print("    Retrying in 30s...", flush=True)
                time.sleep(30)
                try:
                    resp = clients[pname].chat.completions.create(
                        model=cfg["model"],
                        messages=[{"role": "user", "content": query}],
                        timeout=60,
                    )
                    result["raw_response"] = resp.choices[0].message.content
                    result["status"] = "success"
                    del result["error"]
                    errors -= 1
                except Exception as e2:
                    result["error"] = str(e2)

        if not result["raw_response"] and result["status"] != "error":
            result["status"] = "empty"

        responses.append(result)
        time.sleep(cfg["delay"])

# Save
output_path = Path(__file__).resolve().parent / "responses.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(responses, f, ensure_ascii=False, indent=2)

# Summary
error_pct = (errors / total * 100) if total > 0 else 0
print(f"\nSampling complete:")
print(f"  Questions: {len(questions)}")
print(f"  Platforms: {list(PLATFORMS.keys())}")
print(f"  Total responses: {len(responses)}")
print(f"  Errors: {errors} ({error_pct:.0f}%)")
print(f"  Output: {output_path}")

if error_pct > 50:
    print("WARNING: >50% errors. Check API tokens and network.", file=sys.stderr)
