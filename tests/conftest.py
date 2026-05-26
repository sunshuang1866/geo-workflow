"""
测试配置文件
Pytest 共享 fixtures 和配置
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"

# 将 _shared 模块目录加入 Python 路径
if str(SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_DIR))


# ---------------------------------------------------------------------------
# 通用工具 fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def write_json():
    """将 Python 对象序列化为 JSON 并写入文件。"""

    def _write(path, data):
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    return _write


@pytest.fixture
def run_script():
    """以子进程方式运行脚本，返回 (returncode, stdout, stderr)。"""

    def _run(args, stdin_text=None):
        result = subprocess.run(
            args,
            input=stdin_text,
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout, result.stderr

    return _run


# ---------------------------------------------------------------------------
# 预置测试数据 fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def official_url():
    """单个官方文档 URL fixture。"""
    return "https://docs.openeuler.org/zh/docs/22.03/install.html"


@pytest.fixture
def all_platforms():
    """所有支持的 AI 采样平台列表 fixture。"""
    return ["chatgpt", "deepseek", "doubao", "qwen", "gemini", "kimi"]


@pytest.fixture
def sample_questions(official_url):
    """基础问题集 fixture，包含 1 个带有官方 URL 的问题。"""
    return {
        "community": "test",
        "questions": [
            {
                "id": "q_001",
                "question": "How to install openEuler on ARM?",
                "official_urls": [official_url],
            }
        ],
    }


@pytest.fixture
def sample_responses(official_url, all_platforms):
    """基础平台回答 fixture，所有平台均引用官方 URL。"""
    return [
        {
            "question_id": "q_001",
            "platform": p,
            "response_text": f"参见 {official_url} 获取安装指南。",
        }
        for p in all_platforms
    ]
