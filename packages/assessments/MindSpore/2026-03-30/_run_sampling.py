#!/usr/bin/env python3
"""Batch sampling script for MindSpore questions q_001-q_010 across platforms."""
import json, time, sys, os
from datetime import datetime, timezone

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: pip install openai", file=sys.stderr)
    sys.exit(1)

PLATFORM_CONFIG = {
    "deepseek": {
        "base_url": "https://api.lingyaai.cn/v1",
        "model": "deepseek-v3.2",
        "delay": 1.5,
    },
    "doubao": {
        "base_url": "https://api.lingyaai.cn/v1",
        "model": "doubao-seed-2.0-pro",
        "delay": 1.0,
    },
    "qwen": {
        "base_url": "https://api.lingyaai.cn/v1",
        "model": "qwen3.5-plus",
        "delay": 1.5,
    },
}

API_KEY = "sk-ko98bBxz6mIIrZR3ruPOhB3vy7KZq8p1GMceWQxmNK2ODQRb"
QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "questions.json")
RAW_OUTPUT = os.path.join(os.path.dirname(__file__), "_responses_raw.json")

def load_questions():
    with open(QUESTIONS_FILE) as f:
        all_q = json.load(f)
    return [q for q in all_q if q["id"] in [f"q_{i:03d}" for i in range(1, 11)]]

def load_existing():
    if os.path.exists(RAW_OUTPUT):
        with open(RAW_OUTPUT) as f:
            return json.load(f)
    return []

def save_responses(responses):
    with open(RAW_OUTPUT, "w") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)

def sample_one(client, config, question, platform_name):
    qid = question["id"]
    query = question["question"]
    timestamp = datetime.now(timezone.utc).isoformat()
    
    try:
        response = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": query}],
            timeout=90,
        )
        return {
            "question_id": qid,
            "platform": platform_name,
            "query": query,
            "timestamp": timestamp,
            "raw_response": response.choices[0].message.content,
            "citations": [],
            "model": config["model"],
            "status": "success",
        }
    except Exception as e:
        return {
            "question_id": qid,
            "platform": platform_name,
            "query": query,
            "timestamp": timestamp,
            "raw_response": "",
            "citations": [],
            "model": config["model"],
            "status": "error",
            "error": str(e),
        }

def main():
    questions = load_questions()
    print(f"Loaded {len(questions)} questions")
    
    # Load existing results to support resume
    existing = load_existing()
    done_keys = {(r["question_id"], r["platform"]) for r in existing if r.get("status") == "success"}
    responses = existing[:]
    
    # Build clients
    clients = {}
    for pname, cfg in PLATFORM_CONFIG.items():
        clients[pname] = OpenAI(api_key=API_KEY, base_url=cfg["base_url"])
    
    total = len(questions) * len(PLATFORM_CONFIG)
    remaining = total - len(done_keys)
    print(f"Already done: {len(done_keys)}, remaining: {remaining}")
    
    count = 0
    for q in questions:
        for pname, cfg in PLATFORM_CONFIG.items():
            key = (q["id"], pname)
            if key in done_keys:
                count += 1
                print(f"[skip] {q['id']} → {pname} (already done)")
                continue
            
            count += 1
            print(f"[{count}/{total}] {q['id']} → {pname}...", end=" ", flush=True)
            
            result = sample_one(clients[pname], cfg, q, pname)
            status = result["status"]
            
            if status == "success":
                preview = result["raw_response"][:50].replace("\n", " ")
                print(f"✓ {preview}...")
            else:
                err = result.get("error", "unknown")[:80]
                print(f"✗ {err}")
                # Retry once on error after 5s
                time.sleep(5)
                print(f"  retrying...", end=" ", flush=True)
                result = sample_one(clients[pname], cfg, q, pname)
                if result["status"] == "success":
                    preview = result["raw_response"][:50].replace("\n", " ")
                    print(f"✓ {preview}...")
                else:
                    print(f"✗ still failed")
            
            # Remove any previous error entry for this key
            responses = [r for r in responses if not (r["question_id"] == q["id"] and r["platform"] == pname)]
            responses.append(result)
            save_responses(responses)  # Save after each call
            
            time.sleep(cfg["delay"])
    
    # Summary
    success = sum(1 for r in responses if r.get("status") == "success")
    errors = sum(1 for r in responses if r.get("status") == "error")
    print(f"\nSampling complete:")
    print(f"  Questions: {len(questions)}")
    print(f"  Platforms: {list(PLATFORM_CONFIG.keys())}")
    print(f"  Total responses: {len(responses)}")
    print(f"  Success: {success}")
    print(f"  Errors: {errors}")
    print(f"  Coverage: {success/total*100:.0f}%")

if __name__ == "__main__":
    main()
