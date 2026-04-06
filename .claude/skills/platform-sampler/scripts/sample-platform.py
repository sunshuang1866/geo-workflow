#!/usr/bin/env python3
"""Sample a single AI platform with a question and return the response.

Usage: python3 sample-platform.py --platform <name> --query "<query>" --question-id <id>

Supported platforms: chatgpt, deepseek, doubao, qwen, gemini

API keys and base URLs are read from .env in the project root:
  {PLATFORM}_API_KEY   — required
  {PLATFORM}_BASE_URL  — optional, overrides the built-in default

The model is always instructed to include reference links in its response.

Output: JSON to stdout with fields: question_id, platform, query, timestamp, raw_response, citations, model, status.
Errors: stderr with descriptive messages, exits with code 1.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


PLATFORM_CONFIG = {
    "chatgpt": {
        "default_base_url": "https://api.ikuncode.cc",
        "model": "gpt-5.4",
    },
    "deepseek": {
        "default_base_url": "https://api.lingyaai.cn/v1",
        "model": "deepseek-v3.2",
    },
    "doubao": {
        "default_base_url": "https://www.packyapi.com/v1",
        "model": "doubao-seed-2.0-pro",
    },
    "qwen": {
        "default_base_url": "https://api.lingyaai.cn/v1",
        "model": "qwen3.5-plus",
    },
    "gemini": {
        "default_base_url": "https://www.packyapi.com/v1",
        "model": "gemini-2.5-pro",
    },
}


SYSTEM_PROMPT = (
    "你的回答必须包含引用来源的链接。在回答末尾，列出所有引用源的完整 URL，格式为：\n\n"
    "参考链接：\n"
    "- https://...\n"
    "- https://...\n\n"
    "要求：\n"
    "1. 每条引用必须是完整的 URL（以 http:// 或 https:// 开头），不接受纯文字来源名称。\n"
    "2. 链接不限来源。\n"
    "3. 至少提供 7 条引用链接。"
)


def load_dotenv(env_path: Path) -> None:
    """Parse .env file and set variables into os.environ (does not overwrite existing)."""
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


def resolve_config(platform: str) -> tuple[str, str, str]:
    """Return (api_key, base_url, model) for the given platform, reading from env."""
    env_key = f"{platform.upper()}_API_KEY"
    env_url = f"{platform.upper()}_BASE_URL"
    env_model = f"{platform.upper()}_MODEL"

    api_key = os.environ.get(env_key, "")
    if not api_key:
        print(f"ERROR: {env_key} is not set in .env", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get(env_url, "") or PLATFORM_CONFIG[platform]["default_base_url"]
    model = os.environ.get(env_model, "") or PLATFORM_CONFIG[platform]["model"]
    return api_key, base_url, model


def extract_citations(text: str) -> list[str]:
    """Extract all https?:// URLs from the response text, deduplicated, order-preserved."""
    urls = re.findall(r'https?://[^\s\)\]>\'"，。；、]+', text)
    seen: set[str] = set()
    result = []
    for u in urls:
        u = u.rstrip('.,;:`')
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result


def sample(platform: str, query: str, question_id: str) -> dict:
    if platform not in PLATFORM_CONFIG:
        print(f"ERROR: Unknown platform '{platform}'. Supported: {list(PLATFORM_CONFIG.keys())}", file=sys.stderr)
        sys.exit(1)

    api_key, base_url, model = resolve_config(platform)

    client = OpenAI(api_key=api_key, base_url=base_url)
    timestamp = datetime.now(timezone.utc).isoformat()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        raw = response.choices[0].message.content
        return {
            "question_id": question_id,
            "platform": platform,
            "query": query,
            "timestamp": timestamp,
            "raw_response": raw,
            "citations": extract_citations(raw),
            "model": model,
            "status": "success",
        }

    except Exception as e:
        return {
            "question_id": question_id,
            "platform": platform,
            "query": query,
            "timestamp": timestamp,
            "raw_response": "",
            "citations": [],
            "model": model,
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    # Load .env from project root (two levels up from this script)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent  # skills/platform-sampler/scripts -> project root
    load_dotenv(project_root / ".env")

    parser = argparse.ArgumentParser(description="Sample AI platform")
    parser.add_argument("--platform", required=True, choices=list(PLATFORM_CONFIG.keys()))
    parser.add_argument("--query", required=True)
    parser.add_argument("--question-id", required=True)
    args = parser.parse_args()

    result = sample(args.platform, args.query, args.question_id)

    if result["status"] == "error":
        print(f"WARNING: {args.platform} call failed: {result['error']}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))
