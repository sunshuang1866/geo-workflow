"""
测试夹具和工具函数
"""
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"

PLATFORMS = ["chatgpt", "deepseek", "doubao", "qwen", "gemini", "kimi"]
DEFAULT_OFFICIAL_URL = "https://docs.openeuler.org/zh/docs/22.03/install.html"


def load_skill_script(relative_path: str):
    """导入技能脚本模块（支持文件名包含连字符的脚本）。

    Args:
        relative_path: 相对于 .claude/skills/ 的路径，
                       例如 "scoring-engine/scripts/score-urls.py"

    Returns:
        已加载的模块对象。
    """
    script_path = SKILLS_DIR / relative_path
    module_name = relative_path.replace("/", "_").replace("-", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeoTestData:
    """GEO 工作流测试数据生成器"""

    @staticmethod
    def make_question(
        id: str = "q_001",
        question: str = "How to install openEuler on ARM?",
        official_urls: Optional[List[str]] = None,
        doc_form: Optional[str] = None,
    ) -> Dict[str, Any]:
        """生成单个问题条目"""
        entry: Dict[str, Any] = {"id": id, "question": question}
        if official_urls is not None:
            entry["official_urls"] = official_urls
        if doc_form is not None:
            entry["doc_form"] = doc_form
        return entry

    @staticmethod
    def make_questions_file(
        questions: List[Dict[str, Any]],
        community: str = "test",
    ) -> Dict[str, Any]:
        """生成 questions.json 文件结构"""
        return {"community": community, "questions": questions}

    @staticmethod
    def make_response(
        question_id: str = "q_001",
        platform: str = "deepseek",
        response_text: str = "some answer",
        cited_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """生成单条平台回答；传入 cited_url 则回答中包含该 URL"""
        text = f"参见 {cited_url} 获取详情。" if cited_url else response_text
        return {
            "question_id": question_id,
            "platform": platform,
            "response_text": text,
        }

    @staticmethod
    def make_responses_all_platforms(
        question_id: str = "q_001",
        cited_url: Optional[str] = None,
        platforms: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """为所有（或指定）平台生成回答，可选统一引用某 URL"""
        if platforms is None:
            platforms = PLATFORMS
        return [
            GeoTestData.make_response(question_id, p, cited_url=cited_url)
            for p in platforms
        ]

    @staticmethod
    def make_scoring_fixture(
        url: str = DEFAULT_OFFICIAL_URL,
        platforms: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """生成用于评分管道集成测试的完整 questions + responses 数据"""
        if platforms is None:
            platforms = PLATFORMS
        questions = GeoTestData.make_questions_file(
            [GeoTestData.make_question(official_urls=[url])]
        )
        responses = GeoTestData.make_responses_all_platforms(cited_url=url, platforms=platforms)
        return {"questions": questions, "responses": responses}
