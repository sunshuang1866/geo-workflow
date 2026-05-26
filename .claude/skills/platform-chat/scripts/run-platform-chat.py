#!/usr/bin/env python3
"""
Batch orchestrator for platform-chat skill.

Runs ask-{platform}.py for each question sequentially, appending results to
output/{community}/{date}/responses.json after each question.

Usage:
  python3 run-platform-chat.py \\
    --platform deepseek-web \\
    --community openEuler \\
    --date 2026-04-13 \\
    --timeout 120

  python3 run-platform-chat.py \\
    --platform qwen-web \\
    --community openEuler \\
    --date 2026-04-13 \\
    --questions q_001,q_002,q_003

Output mode: always 'append' — merges by (question_id, platform) key.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone


def load_env(env_path: Path) -> dict:
    env = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
    return env


def load_responses(path: Path) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("responses", [])
    return []


def save_responses(path: Path, responses: list) -> None:
    # Preserve existing format if it's a dict with metadata
    if path.exists():
        with open(path) as f:
            existing = json.load(f)
        if isinstance(existing, dict) and "metadata" in existing:
            existing["responses"] = responses
            # Update metadata
            platforms = sorted(set(r.get("platform", "") for r in responses))
            qids = set(r.get("question_id", "") for r in responses)
            existing["metadata"]["platforms"] = platforms
            existing["metadata"]["total_questions"] = len(qids)
            existing["metadata"]["total_responses"] = len(responses)
            existing["metadata"]["sampled_at"] = datetime.now(timezone.utc).isoformat()
            with open(path, "w") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
            return

    # New file or flat list format
    with open(path, "w") as f:
        json.dump(responses, f, ensure_ascii=False, indent=2)


def merge_result(responses: list, new_result: dict) -> list:
    """Replace existing entry with same (question_id, platform), or append."""
    key = (new_result.get("question_id"), new_result.get("platform"))
    replaced = False
    out = []
    for r in responses:
        if (r.get("question_id"), r.get("platform")) == key:
            out.append(new_result)
            replaced = True
        else:
            out.append(r)
    if not replaced:
        out.append(new_result)
    return out


def run_question(
    script_path: Path,
    question_text: str,
    question_id: str,
    timeout: int,
    env: dict,
    session: str = None,
) -> dict:
    cmd = [
        sys.executable,
        str(script_path),
        "--question",
        question_text,
        "--question-id",
        question_id,
        "--timeout",
        str(timeout),
    ]
    if session:
        cmd += ["--session", session]

    merged_env = {**os.environ, **env}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout * 2
            + 90,  # login(~30s) + response(timeout) + follow-up(timeout) + buffer
            env=merged_env,
        )
        stderr = result.stderr.strip()
        if stderr:
            # Print relevant stderr lines
            for line in stderr.splitlines():
                if line.strip():
                    print(f"    [stderr] {line}", file=sys.stderr)

        if result.returncode in (0, 4):  # 0=success, 4=timeout-with-content
            try:
                return json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                print(f"    JSON parse error: {e}", file=sys.stderr)
                print(f"    stdout: {result.stdout[:200]}", file=sys.stderr)
                return None
        else:
            print(f"    Script exited {result.returncode}", file=sys.stderr)
            return None
    except subprocess.TimeoutExpired:
        print(f"    Process timed out after {timeout + 120}s", file=sys.stderr)
        return None
    except Exception as e:
        print(f"    Subprocess error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform",
        required=True,
        choices=["deepseek-web", "qwen-web", "chatgpt-web", "gemini-web"],
    )
    parser.add_argument("--community", default=None)
    parser.add_argument("--date", required=True, help="Output date folder, e.g. 2026-04-13")
    parser.add_argument(
        "--questions",
        default=None,
        help="Comma-separated question IDs to sample (default: all not yet done)",
    )
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    # Resolve paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent.parent  # geo-workflow/
    env_path = project_root / ".env"

    env = load_env(env_path)
    community = args.community or env.get("GEO_COMMUNITY")
    if not community:
        print("ERROR: community not set.", file=sys.stderr)
        sys.exit(1)

    community_dir = project_root / "assessments" / community
    questions_path = community_dir / "questions.json"
    output_dir = community_dir / args.date
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "responses.json"

    # Load questions
    with open(questions_path) as f:
        q_data = json.load(f)
    all_questions = q_data if isinstance(q_data, list) else q_data.get("questions", [])

    # Normalize question ID field
    for q in all_questions:
        if "id" in q and "question_id" not in q:
            q["question_id"] = q["id"]

    # Determine which script to use
    platform_map = {
        "deepseek-web": script_dir / "ask-deepseek.py",
        "qwen-web": script_dir / "ask-qwen.py",
        "chatgpt-web": script_dir / "ask-chatgpt.py",
        "gemini-web": script_dir / "ask-gemini.py",
    }
    script_path = platform_map[args.platform]

    # Resolve session file
    session_files = {
        "chatgpt-web": community_dir / ".chatgpt-session.json",
        "gemini-web": community_dir / ".gemini-session.json",
        "deepseek-web": community_dir / ".deepseek-session.json",
        "qwen-web": community_dir / ".qwen-session.json",
    }
    session = str(session_files[args.platform]) if session_files[args.platform].exists() else None

    # Load existing responses
    existing = load_responses(output_path)
    done_set = {(r.get("question_id"), r.get("platform")) for r in existing}

    # Determine question list
    if args.questions:
        requested_ids = set(args.questions.split(","))
        questions = [q for q in all_questions if q["question_id"] in requested_ids]
        unknown = requested_ids - {q["question_id"] for q in questions}
        if unknown:
            print(f"  WARNING: unknown question IDs skipped: {unknown}", file=sys.stderr)
    else:
        # Skip already done
        questions = [q for q in all_questions if (q["question_id"], args.platform) not in done_set]

    print(f"Platform: {args.platform}")
    print(f"Community: {community}")
    print(f"Output: {output_path} (mode: append)")
    print(f"Questions loaded: {len(questions)} (of {len(all_questions)} total)")
    print()

    responses = list(existing)
    success_count = 0
    error_count = 0
    cited_count = 0

    for idx, q in enumerate(questions, 1):
        qid = q["question_id"]
        qtxt = q.get("question", q.get("text", ""))
        print(f"── [{idx}/{len(questions)}] {qid}: {qtxt[:60]}… ──")

        result = run_question(
            script_path=script_path,
            question_text=qtxt,
            question_id=qid,
            timeout=args.timeout,
            env=env,
            session=session,
        )

        if result is None:
            error_count += 1
            print(f"  ✗ {qid} {args.platform} — script returned no output")
            continue

        status = result.get("status", "error")
        citations = result.get("citations", [])
        n_citations = len(citations)

        if status in ("success", "timeout"):
            if status == "success":
                success_count += 1
                cited_count += 1 if n_citations > 0 else 0
                print(f"  ✓ {qid} {args.platform} — {n_citations} citations")
            else:
                error_count += 1
                print(f"  ⚠ {qid} {args.platform} — timeout ({n_citations} citations captured)")
        else:
            error_count += 1
            err_msg = result.get("error", "unknown error")
            print(f"  ✗ {qid} {args.platform} — {err_msg}")

        # Re-read file fresh before merge to avoid overwriting concurrent writes
        fresh = load_responses(output_path)
        fresh = merge_result(fresh, result)
        save_responses(output_path, fresh)

    total = len(questions)
    print()
    print("Sampling complete:")
    print(f"  Platform:    {args.platform}")
    print(f"  Questions:   {total}")
    print(f"  Successful:  {success_count}")
    print(f"  With citations: {cited_count}")
    print(f"  Errors:      {error_count}")
    print(f"  Output:      {output_path}")

    if error_count > total * 0.5:
        print(
            f"\nWARNING: >50% questions failed ({error_count}/{total}). "
            "Check credentials or re-run with --questions for failed IDs.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
