"""Shared test fixtures and helpers for geo-workflow tests."""

import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"

# Make _shared importable in all test modules
if str(SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_DIR))


def load_skill_script(relative_path: str):
    """Import a skill script whose filename contains hyphens.

    Args:
        relative_path: Path relative to .claude/skills/
                       e.g. "scoring-engine/scripts/score-urls.py"

    Returns the loaded module.
    """
    script_path = SKILLS_DIR / relative_path
    module_name = relative_path.replace("/", "_").replace("-", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
