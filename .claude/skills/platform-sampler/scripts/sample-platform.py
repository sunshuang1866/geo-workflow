#!/usr/bin/env python3
"""Sample a single AI platform with a question and return the response.

Usage: python3 sample-platform.py --platform <name> --api-key <key> --query "<query>" --question-id <id> [--base-url <url>]

Supported platforms: perplexity, chatgpt, deepseek, doubao, qwen

Output: JSON to stdout with fields: question_id, platform, query, timestamp, raw_response, citations, model.
Errors: stderr with descriptive messages, exits with code 1.
"""

import argparse
import json
import sys
from datetime import datetime, timezone

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)


PLATFORM_CONFIG = {
    "perplexity": {
        "base_url": "https://api.perplexity.ai",
        "model": "sonar",
    },
    "chatgpt": {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "doubao": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-1.5-pro-32k",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
}


def sample(platform: str, api_key: str, query: str, question_id: str, base_url: str | None = None) -> dict:
    if platform not in PLATFORM_CONFIG:
        print(f"ERROR: Unknown platform '{platform}'. Supported: {list(PLATFORM_CONFIG.keys())}", file=sys.stderr)
        sys.exit(1)

    config = PLATFORM_CONFIG[platform]
    client = OpenAI(
        api_key=api_key,
        base_url=base_url or config["base_url"],
    )

    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        response = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": query}],
        )

        result = {
            "question_id": question_id,
            "platform": platform,
            "query": query,
            "timestamp": timestamp,
            "raw_response": response.choices[0].message.content,
            "citations": [],
            "model": config["model"],
            "status": "success",
        }

        # Extract citations if available (Perplexity)
        if hasattr(response, "citations") and response.citations:
            result["citations"] = response.citations

        return result

    except Exception as e:
        return {
            "question_id": question_id,
            "platform": platform,
            "query": query,
            "timestamp": timestamp,
            "raw_response": "",
            "citations": [],
            "model": config["model"],
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample AI platform")
    parser.add_argument("--platform", required=True, choices=list(PLATFORM_CONFIG.keys()))
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--question-id", required=True)
    parser.add_argument("--base-url", default=None)
    args = parser.parse_args()

    result = sample(args.platform, args.api_key, args.query, args.question_id, args.base_url)

    if result["status"] == "error":
        print(f"WARNING: {args.platform} call failed: {result['error']}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))
