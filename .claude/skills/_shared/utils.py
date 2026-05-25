import json
import os
import sys
from pathlib import Path


def add_skills_to_path():
    """Add .claude/skills/ to sys.path so _shared modules are importable.

    Call this before any _shared imports in skill scripts.
    Usage:
        add_skills_to_path()
        from _shared.utils import load_json
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[0]))


def load_json(filepath, label=None, optional=False):
    """Load and parse a JSON file.

    Args:
        filepath: Path to JSON file.
        label: Human-readable label for error messages (defaults to filepath).
        optional: If True, returns None when file not found instead of exiting.

    Returns parsed JSON, or None if optional=True and file missing.
    Exits with code 1 on error (unless optional=True and file missing).
    """
    p = Path(filepath)
    if not p.exists():
        if optional:
            return None
        print(f"ERROR: {label or 'File'} not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {label or filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def resolve_platform_token(platform=None, token=None):
    """Resolve target platform and API token from args and environment.

    Returns (platform, token) tuple. Falls back to "github" for platform.
    Does NOT check for missing token — caller handles dry_run / error.
    """
    if token:
        return platform or "github", token

    gh_token = os.environ.get("GITHUB_TOKEN", "")
    gc_token = os.environ.get("GITCODE_TOKEN", "")

    if platform == "github":
        token = gh_token
    elif platform == "gitcode":
        token = gc_token
    else:
        if gh_token:
            platform, token = "github", gh_token
        elif gc_token:
            platform, token = "gitcode", gc_token

    return platform or "github", token
