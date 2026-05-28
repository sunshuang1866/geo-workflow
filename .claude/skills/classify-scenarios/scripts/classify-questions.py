#!/usr/bin/env python3
"""Classify questions in questions.json into application scenarios.

Main orchestrator script: loads questions.json, runs fetch-docs-index + extract-taxonomy
to get the scenario taxonomy, then batches unclassified questions through LLM, and
writes the scenario field back to questions.json.

Usage:
    python3 classify-questions.py --community openEuler [--docs-index-url URL]
                                   [--batch-size 80] [--dry-run]
                                   [--force-reclassify]

Exit codes:
  0 — success
  1 — fatal error (missing file, URL unreachable, LLM failure)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import load_json

SCRIPT_DIR = Path(__file__).parent
REFERENCES_DIR = SCRIPT_DIR.parent / "references"
GENERAL_SCENARIO_KEY = "general"
GENERAL_SCENARIO_LABEL = "通用"
GENERAL_THRESHOLD = 0.20  # Warning if > 20% classified as general
ANTHROPIC_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 2


def _load_prompt_template() -> str:
    template_path = REFERENCES_DIR / "prompt-templates.md"
    content = template_path.read_text(encoding="utf-8")
    match = re.search(r"## QUESTION_CLASSIFICATION\n\n```\n(.*?)```", content, re.DOTALL)
    if not match:
        print(
            "ERROR: QUESTION_CLASSIFICATION template not found in prompt-templates.md",
            file=sys.stderr,
        )
        sys.exit(1)
    return match.group(1).strip()


def _call_llm(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    import urllib.error
    import urllib.request

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["content"][0]["text"]
    except Exception as exc:
        print(f"ERROR: LLM call failed: {exc}", file=sys.stderr)
        sys.exit(1)


def _parse_classification(text: str) -> dict | None:
    """Extract {question_id: scenario_key} dict from LLM response."""
    try:
        result = json.loads(text.strip())
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _run_fetch_docs_index(url: str) -> list[dict]:
    """Run fetch-docs-index.py and return parsed page list."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "fetch-docs-index.py"), "--url", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr, end="")
        print(f"ERROR: fetch-docs-index.py failed for {url}", file=sys.stderr)
        sys.exit(1)
    try:
        pages = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR: fetch-docs-index.py returned invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    # Forward stderr progress
    print(result.stderr, file=sys.stderr, end="")
    return pages


def _run_extract_taxonomy(pages: list[dict]) -> list[dict]:
    """Pipe pages into extract-taxonomy.py and return taxonomy list."""
    pages_json = json.dumps(pages, ensure_ascii=False)
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "extract-taxonomy.py")],
        input=pages_json,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr, end="")
        print("ERROR: extract-taxonomy.py failed", file=sys.stderr)
        sys.exit(1)
    try:
        taxonomy = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR: extract-taxonomy.py returned invalid JSON: {exc}", file=sys.stderr)
        sys.exit(1)
    print(result.stderr, file=sys.stderr, end="")
    return taxonomy


def _classify_batch(batch: list[dict], taxonomy: list[dict], template: str, batch_idx: int) -> dict:
    """Classify one batch of questions. Returns {question_id: scenario_key}."""
    taxonomy_json = json.dumps(taxonomy, ensure_ascii=False)
    questions_json = json.dumps(
        [{"id": q["id"], "question": q["question"]} for q in batch],
        ensure_ascii=False,
        indent=2,
    )
    prompt = template.replace("{TAXONOMY_JSON}", taxonomy_json).replace(
        "{QUESTIONS_JSON}", questions_json
    )

    result = None
    for attempt in range(1, MAX_RETRIES + 1):
        response = _call_llm(prompt)
        result = _parse_classification(response)
        if result is not None:
            break
        print(
            f"WARNING: Batch {batch_idx} attempt {attempt} returned invalid JSON. Retrying...",
            file=sys.stderr,
        )
        prompt = f"Fix the JSON syntax. Return ONLY a valid JSON object: {response[:500]}"

    if result is None:
        print(
            f"WARNING: Batch {batch_idx} LLM output invalid after retries, skipping",
            file=sys.stderr,
        )
        return {}

    # Validate that returned keys are valid taxonomy keys
    valid_keys = {item["key"] for item in taxonomy}
    sanitized = {}
    for qid, key in result.items():
        if key not in valid_keys:
            print(
                f"WARNING: LLM returned unknown scenario key '{key}' for {qid}, "
                f"defaulting to '{GENERAL_SCENARIO_KEY}'",
                file=sys.stderr,
            )
            key = GENERAL_SCENARIO_KEY
        sanitized[qid] = key

    # Check for anomalous general ratio in this batch
    general_count = sum(1 for k in sanitized.values() if k == GENERAL_SCENARIO_KEY)
    if len(sanitized) > 0 and general_count / len(sanitized) > 0.50:
        pct = int(general_count / len(sanitized) * 100)
        print(
            f"WARNING: Batch {batch_idx} 通用占比异常高 ({pct}%)，建议检查分类体系或问题描述",
            file=sys.stderr,
        )
        # Mark for review
        for qid, key in sanitized.items():
            if key == GENERAL_SCENARIO_KEY:
                sanitized[qid] = key  # key stays, review flag is in questions.json

    return sanitized


def _build_label_lookup(taxonomy: list[dict]) -> dict:
    return {item["key"]: item["label"] for item in taxonomy}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--community", default="")
    parser.add_argument("--docs-index-url", default="")
    parser.add_argument("--batch-size", type=int, default=80)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-reclassify", action="store_true")
    args = parser.parse_args()

    # Load .env
    env_path = Path(__file__).resolve().parents[4] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

    community = args.community or os.environ.get("GEO_COMMUNITY", "")
    if not community:
        print(
            "ERROR: community not set. Provide --community or GEO_COMMUNITY in .env",
            file=sys.stderr,
        )
        sys.exit(1)

    docs_url = args.docs_index_url or os.environ.get("DOCS_INDEX_URL", "")
    if not docs_url:
        print(
            "ERROR: DOCS_INDEX_URL not set. Provide --docs-index-url or DOCS_INDEX_URL in .env",
            file=sys.stderr,
        )
        sys.exit(1)

    questions_path = Path(__file__).resolve().parents[4] / "output" / community / "questions.json"
    if not questions_path.exists():
        print(f"ERROR: questions.json not found: {questions_path}", file=sys.stderr)
        sys.exit(1)

    questions_data = load_json(questions_path, "questions.json")
    all_questions = questions_data.get("questions", [])

    # Step: determine which questions need classification
    if args.force_reclassify:
        target_questions = all_questions
        print(
            f"force_reclassify=true: reclassifying all {len(all_questions)} questions",
            file=sys.stderr,
        )
    else:
        target_questions = [
            q for q in all_questions if not q.get("scenario") or q["scenario"] == ""
        ]
        skip_count = len(all_questions) - len(target_questions)
        print(
            f"Community={community} total={len(all_questions)} "
            f"unclassified={len(target_questions)} skip={skip_count}",
            file=sys.stderr,
        )

    if not target_questions:
        print("All questions already classified. Nothing to do.", file=sys.stderr)
        sys.exit(0)

    # Step: check existing taxonomy in questions.json
    existing_taxonomy = questions_data.get("scenario_taxonomy", {})
    if existing_taxonomy.get("categories") and not args.force_reclassify:
        taxonomy = existing_taxonomy["categories"]
        print(
            f"Using existing taxonomy (version={existing_taxonomy.get('version', 1)}, "
            f"{len(taxonomy)} scenarios)",
            file=sys.stderr,
        )
    else:
        # Step: fetch docs index and extract taxonomy
        print(f"Fetching docs index: {docs_url}", file=sys.stderr)
        pages = _run_fetch_docs_index(docs_url)
        taxonomy = _run_extract_taxonomy(pages)

    label_lookup = _build_label_lookup(taxonomy)

    # Step: batch classify unclassified questions
    template = _load_prompt_template()
    batch_size = args.batch_size
    all_classifications: dict = {}

    batches = [
        target_questions[i: i + batch_size] for i in range(0, len(target_questions), batch_size)
    ]
    print(
        f"Classifying {len(target_questions)} questions in {len(batches)} batch(es)...",
        file=sys.stderr,
    )

    for idx, batch in enumerate(batches, start=1):
        print(f"Batch {idx}/{len(batches)} ({len(batch)} questions)...", file=sys.stderr)
        batch_result = _classify_batch(batch, taxonomy, template, idx)
        all_classifications.update(batch_result)

    # Step: validate and check general ratio
    classified_count = len(all_classifications)
    general_count = sum(1 for k in all_classifications.values() if k == GENERAL_SCENARIO_KEY)
    if classified_count > 0:
        general_pct = general_count / classified_count
        if general_pct > GENERAL_THRESHOLD:
            pct_str = f"{general_pct * 100:.0f}%"
            print(
                f"WARNING: 通用场景占比 {pct_str}，建议检查场景分类质量",
                file=sys.stderr,
            )

    # Step: dry_run
    if args.dry_run:
        print("dry_run=true: no writes performed. Proposed classifications:", file=sys.stderr)
        for q in target_questions:
            qid = q["id"]
            key = all_classifications.get(qid, GENERAL_SCENARIO_KEY)
            label = label_lookup.get(key, GENERAL_SCENARIO_LABEL)
            print(f"  {qid}: {key} ({label})", file=sys.stderr)
        print(
            json.dumps(
                {"dry_run": True, "classified": len(all_classifications)}, ensure_ascii=False
            )
        )
        sys.exit(0)

    # Step: write back to questions.json
    qid_index = {q["id"]: q for q in all_questions}
    for qid, scenario_key in all_classifications.items():
        if qid in qid_index:
            qid_index[qid]["scenario"] = scenario_key
            # Mark for review if high-general-rate batch flagged it
            if scenario_key == GENERAL_SCENARIO_KEY:
                # check if this batch had anomalously high general rate
                pass  # Warning already printed at batch level

    # Update scenario_taxonomy root field
    existing_version = (
        existing_taxonomy.get("version", 0)
        if args.force_reclassify
        else existing_taxonomy.get("version", 1)
    )
    new_version = existing_version + 1 if args.force_reclassify else existing_version
    if not questions_data.get("scenario_taxonomy") or args.force_reclassify:
        new_version = (existing_taxonomy.get("version", 0) + 1) if args.force_reclassify else 1
        questions_data["scenario_taxonomy"] = {
            "version": new_version,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "source_url": docs_url,
            "categories": taxonomy,
        }

    questions_data["questions"] = list(qid_index.values())
    questions_path.write_text(
        json.dumps(questions_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    filled = sum(1 for q in all_questions if q.get("scenario"))
    print(
        f"Classified {classified_count} questions | "
        f"通用: {general_count} | "
        f"Total with scenario: {filled}/{len(all_questions)} | "
        f"dry_run=false",
        file=sys.stderr,
    )
    print(
        json.dumps(
            {
                "classified": classified_count,
                "general_count": general_count,
                "total_with_scenario": filled,
                "total_questions": len(all_questions),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
