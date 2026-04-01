#!/usr/bin/env python3
"""Batch sampler for multiple questions x multiple platforms.

Usage examples:
  python3 run-sampler.py --community MindSpore
  python3 run-sampler.py --community MindSpore --questions q_001,q_002 --platforms deepseek,qwen
  python3 run-sampler.py --community MindSpore --output-mode append
"""

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


PLATFORMS = ["chatgpt", "deepseek", "doubao", "qwen", "gemini"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k and k not in os.environ:
            os.environ[k] = v


def load_questions(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        questions = data.get("questions", [])
    elif isinstance(data, list):
        questions = data
    else:
        raise ValueError("questions.json must be an object or array")
    if not isinstance(questions, list) or not questions:
        raise ValueError("questions list is empty")
    return questions


def parse_csv_ids(value: str | None) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def latest_date_dir(community_dir: Path) -> Path | None:
    if not community_dir.exists():
        return None
    candidates = [p for p in community_dir.iterdir() if p.is_dir() and DATE_RE.match(p.name)]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.name)[-1]


def load_existing_responses(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        responses = data.get("responses", [])
    elif isinstance(data, list):
        responses = data
    else:
        responses = []
    return responses if isinstance(responses, list) else []


def merge_responses(existing: list[dict], incoming: list[dict]) -> list[dict]:
    merged = {(x.get("question_id"), x.get("platform")): x for x in existing if isinstance(x, dict)}
    for x in incoming:
        merged[(x.get("question_id"), x.get("platform"))] = x
    return list(merged.values())


def call_sample_platform(script: Path, platform: str, query: str, question_id: str) -> dict:
    cmd = [
        sys.executable,
        str(script),
        "--platform",
        platform,
        "--query",
        query,
        "--question-id",
        question_id,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.stdout.strip():
        try:
            result = json.loads(proc.stdout)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    return {
        "question_id": question_id,
        "platform": platform,
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_response": "",
        "citations": [],
        "model": "",
        "status": "error",
        "error": (proc.stderr.strip() or "sample-platform returned invalid JSON"),
    }


def write_output(path: Path, community: str, platforms: list[str], skipped_platforms: list[dict], responses: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "community": community,
            "sampled_at": datetime.now(timezone.utc).isoformat(),
            "platforms": platforms,
            "skipped_platforms": skipped_platforms,
            "total_questions": len({r.get("question_id") for r in responses if isinstance(r, dict)}),
            "total_responses": len(responses),
        },
        "responses": responses,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent
    load_dotenv(project_root / ".env")

    parser = argparse.ArgumentParser(description="Batch sample multiple questions across multiple platforms")
    parser.add_argument("--community", default=os.environ.get("GEO_COMMUNITY", ""))
    parser.add_argument("--platforms", default="")
    parser.add_argument("--questions", default="")
    parser.add_argument("--output-mode", choices=["new_run", "append"], default="new_run")
    parser.add_argument("--group-size", type=int, default=5)
    args = parser.parse_args()

    community = args.community.strip()
    if not community:
        print("ERROR: community not set. Provide --community or set GEO_COMMUNITY in .env.", file=sys.stderr)
        return 1

    requested_platforms = parse_csv_ids(args.platforms)
    available_platforms = []
    skipped_platforms = []
    for p in PLATFORMS:
        key = os.environ.get(f"{p.upper()}_API_KEY", "").strip()
        if key:
            available_platforms.append(p)
    if requested_platforms:
        active_platforms = []
        for p in requested_platforms:
            if p in available_platforms:
                active_platforms.append(p)
            else:
                skipped_platforms.append({"platform": p, "reason": "API key missing or platform unknown"})
    else:
        active_platforms = available_platforms

    if not active_platforms:
        print("ERROR: No configured platforms available. Check .env tokens.", file=sys.stderr)
        return 1

    community_dir = project_root / "assessments" / community
    questions_path = community_dir / "questions.json"
    if not questions_path.exists():
        print(f"ERROR: questions.json not found: {questions_path}", file=sys.stderr)
        return 1

    questions = load_questions(questions_path)
    requested_qids = set(parse_csv_ids(args.questions))
    if requested_qids:
        qmap = {q.get("id"): q for q in questions if isinstance(q, dict) and q.get("id")}
        missing = sorted(requested_qids - set(qmap.keys()))
        if missing:
            print(f"WARNING: Question IDs not found and skipped: {', '.join(missing)}", file=sys.stderr)
        selected_questions = [qmap[qid] for qid in requested_qids if qid in qmap]
    else:
        selected_questions = questions

    if not selected_questions:
        print("ERROR: No questions selected for sampling.", file=sys.stderr)
        return 1

    today = datetime.now().strftime("%Y-%m-%d")
    if args.output_mode == "append":
        latest = latest_date_dir(community_dir)
        target_dir = latest if latest else (community_dir / today)
    else:
        target_dir = community_dir / today
    output_path = target_dir / "responses.json"

    existing = load_existing_responses(output_path)
    all_new: list[dict] = []
    write_lock = threading.Lock()
    rate_lock = threading.Lock()
    last_call_at = {p: 0.0 for p in active_platforms}
    sample_script = script_dir / "sample-platform.py"

    print(f"Questions loaded: {len(selected_questions)}")
    print(f"Platforms: {', '.join(active_platforms)}")
    print(f"Output: {output_path} (mode: {args.output_mode})")

    def sample_one_question(q: dict) -> tuple[str, list[dict]]:
        qid = str(q.get("id", ""))
        query = str(q.get("question", "")).strip()
        results = []
        for p in active_platforms:
            with rate_lock:
                now = time.time()
                wait = max(0.0, last_call_at[p] + 1.0 - now)
            if wait > 0:
                time.sleep(wait)
            with rate_lock:
                last_call_at[p] = time.time()

            r = call_sample_platform(sample_script, p, query, qid)
            if r.get("status") == "error":
                err = str(r.get("error", ""))
                if "429" in err:
                    time.sleep(30)
                    r = call_sample_platform(sample_script, p, query, qid)
            results.append(r)
        return qid, results

    group_size = max(1, args.group_size)
    groups = [selected_questions[i : i + group_size] for i in range(0, len(selected_questions), group_size)]

    for gi, group in enumerate(groups, start=1):
        ids = [str(q.get("id", "")) for q in group]
        print(f"-- Group {gi}/{len(groups)} ({', '.join(ids)}) --")
        with ThreadPoolExecutor(max_workers=min(group_size, len(group))) as pool:
            futures = [pool.submit(sample_one_question, q) for q in group]
            for f in as_completed(futures):
                qid, result_rows = f.result()
                status_line = []
                for r in result_rows:
                    mark = "✓" if r.get("status") == "success" else "✗"
                    status_line.append(f"{r.get('platform')}{mark}")

                with write_lock:
                    all_new.extend(result_rows)
                    merged = merge_responses(existing, all_new)
                    write_output(output_path, community, active_platforms, skipped_platforms, merged)
                print(f"✓ {qid} — {' '.join(status_line)}")

        print(f"Group {gi} done")

    final_responses = merge_responses(existing, all_new)
    write_output(output_path, community, active_platforms, skipped_platforms, final_responses)

    success_count = sum(1 for r in final_responses if r.get("status") == "success")
    print("Sampling complete:")
    print(f"  Questions: {len({r.get('question_id') for r in final_responses})}")
    print(f"  Platforms: {', '.join(active_platforms)}")
    print(f"  Total responses: {len(final_responses)}")
    print(f"  Success: {success_count}")
    print(f"Output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
