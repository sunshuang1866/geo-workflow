"""
tests/test_score_urls.py

测试 scoring-engine/scripts/score-urls.py
涵盖 URL 标准化、引用判断和完整评分管道
"""
import json
import sys
import pytest
from .fixtures import load_skill_script

_mod = load_skill_script("scoring-engine/scripts/score-urls.py")
normalize_url = _mod.normalize_url
is_cited = _mod.is_cited


class TestNormalizeUrl:
    """测试 URL 标准化处理"""

    def test_strips_https_scheme(self):
        assert normalize_url("https://example.com/page") == "example.com/page"

    def test_strips_http_scheme(self):
        assert normalize_url("http://example.com/page") == "example.com/page"

    def test_http_and_https_equivalent(self):
        assert normalize_url("http://example.com/page") == normalize_url("https://example.com/page")

    def test_strips_www_prefix(self):
        assert normalize_url("https://www.example.com/page") == "example.com/page"

    def test_strips_trailing_slash(self):
        assert normalize_url("https://example.com/page/") == "example.com/page"

    def test_lowercases_entire_url(self):
        assert normalize_url("https://Example.COM/Page") == "example.com/page"

    def test_strips_surrounding_whitespace(self):
        assert normalize_url("  https://example.com/page  ") == "example.com/page"

    def test_deep_path_preserved(self):
        """多级路径中的版本号等信息应完整保留"""
        url = "https://docs.openeuler.org/zh/docs/22.03_LTS/install.html"
        assert normalize_url(url) == "docs.openeuler.org/zh/docs/22.03_lts/install.html"


class TestIsCited:
    """测试 AI 回答中的官方 URL 引用判断"""

    URL = "https://docs.openeuler.org/zh/docs/22.03/install.html"

    def test_exact_url_in_response(self):
        cited, matched = is_cited(f"See {self.URL} for details.", [self.URL])
        assert cited is True
        assert self.URL in matched

    def test_no_match_returns_false(self):
        cited, matched = is_cited("See https://other-site.com/page for details.", [self.URL])
        assert cited is False
        assert matched == []

    def test_case_insensitive_match(self):
        """URL 大小写不同时仍应匹配"""
        cited, _ = is_cited(self.URL.upper(), [self.URL])
        assert cited is True

    def test_http_and_https_treated_as_same(self):
        """回答使用 http:// 而官方 URL 为 https:// 时仍应匹配"""
        http_version = self.URL.replace("https://", "http://")
        cited, _ = is_cited(http_version, [self.URL])
        assert cited is True

    def test_empty_official_urls_not_cited(self):
        """官方 URL 列表为空时，结果应为未引用"""
        cited, matched = is_cited("any response text", [])
        assert cited is False
        assert matched == []

    def test_empty_string_urls_skipped(self):
        """官方 URL 列表中的空字符串应被跳过，不触发匹配"""
        cited, matched = is_cited("any text", ["", "   "])
        assert cited is False

    def test_partial_url_does_not_match(self):
        """官方 URL 的子串不应触发匹配（防止误报）"""
        partial = "docs.openeuler.org/zh/docs"
        cited, _ = is_cited(f"See {partial} for more.", [self.URL])
        assert cited is False

    def test_multiple_urls_any_match_counts(self):
        """多个官方 URL 中任意一个被引用即视为已引用"""
        urls = [
            "https://docs.openeuler.org/page-a.html",
            "https://docs.openeuler.org/page-b.html",
        ]
        text = "See docs.openeuler.org/page-b.html for info."
        cited, matched = is_cited(text, urls)
        assert cited is True
        assert urls[1] in matched
        assert urls[0] not in matched

    def test_multiple_urls_all_matched(self):
        """多个官方 URL 全部被引用时，matched 应包含全部"""
        urls = [
            "https://docs.openeuler.org/page-a.html",
            "https://docs.openeuler.org/page-b.html",
        ]
        text = "See docs.openeuler.org/page-a.html and docs.openeuler.org/page-b.html"
        cited, matched = is_cited(text, urls)
        assert len(matched) == 2

    def test_url_in_markdown_link_matches(self):
        """Markdown [text](url) 语法中的 URL 应能被正常识别"""
        cited, _ = is_cited(f"See [安装指南]({self.URL}) for details.", [self.URL])
        assert cited is True

    def test_url_with_query_params_matches(self):
        """回答 URL 附加查询参数时仍应匹配官方 URL"""
        cited, _ = is_cited(f"See {self.URL}?lang=zh for details.", [self.URL])
        assert cited is True

    def test_url_with_fragment_matches(self):
        """回答 URL 附加锚点时仍应匹配官方 URL"""
        cited, _ = is_cited(f"See {self.URL}#installation-steps for details.", [self.URL])
        assert cited is True


class TestScoringPipeline:
    """测试完整评分管道（通过 main() 调用，使用临时文件）"""

    def _run_pipeline(self, tmp_path, questions, responses, write_json):
        """辅助方法：写入测试文件并调用 score-urls.py main()"""
        q_path = tmp_path / "questions.json"
        r_path = tmp_path / "responses.json"
        out_path = tmp_path / "scoring-results.json"
        write_json(q_path, questions)
        write_json(r_path, responses)

        old_argv = sys.argv
        sys.argv = ["score-urls.py", str(r_path), str(q_path), str(out_path)]
        try:
            _mod.main()
        finally:
            sys.argv = old_argv

        return json.loads(out_path.read_text())

    def test_not_cited_when_no_platform_matches(self, tmp_path, write_json):
        """所有平台均未引用官方 URL 时，状态应为 not_cited（P0）"""
        questions = {
            "community": "test",
            "questions": [
                {"id": "q_001", "question": "How to install?",
                 "official_urls": ["https://docs.example.com/install"]}
            ],
        }
        responses = [
            {"question_id": "q_001", "platform": p, "response_text": "no citation"}
            for p in ["deepseek", "qwen", "kimi", "chatgpt", "gemini", "doubao"]
        ]
        result = self._run_pipeline(tmp_path, questions, responses, write_json)
        q001 = result["results"][0]
        assert q001["status"] == "not_cited"
        assert q001["severity"] == "P0"
        assert q001["citation_rate"] == 0.0

    def test_no_official_content_when_urls_empty(self, tmp_path, write_json):
        """official_urls 为空时，状态应为 no_official_content（P1）"""
        questions = {
            "community": "test",
            "questions": [
                {"id": "q_001", "question": "What is it?", "official_urls": []}
            ],
        }
        responses = [
            {"question_id": "q_001", "platform": "deepseek", "response_text": "some answer"}
        ]
        result = self._run_pipeline(tmp_path, questions, responses, write_json)
        q001 = result["results"][0]
        assert q001["status"] == "no_official_content"
        assert q001["severity"] == "P1"

    def test_satisfied_when_all_platforms_cite(self, tmp_path, write_json):
        """所有平台均引用官方 URL 时，状态应为 satisfied（OK，citation_rate=1.0）"""
        url = "https://docs.example.com/install"
        questions = {
            "community": "test",
            "questions": [
                {"id": "q_001", "question": "How to install?", "official_urls": [url]}
            ],
        }
        responses = [
            {"question_id": "q_001", "platform": p,
             "response_text": f"See {url} for details."}
            for p in ["deepseek", "qwen", "kimi", "chatgpt", "gemini", "doubao"]
        ]
        result = self._run_pipeline(tmp_path, questions, responses, write_json)
        q001 = result["results"][0]
        assert q001["status"] == "satisfied"
        assert q001["severity"] == "OK"
        assert q001["citation_rate"] == 1.0

    def test_sort_order_p0_before_p1_before_ok(self, tmp_path, write_json):
        """输出结果应按 P0 → P1 → OK 排序"""
        url = "https://docs.example.com/page"
        questions = {
            "community": "test",
            "questions": [
                {"id": "q_001", "question": "Q1?", "official_urls": [url]},   # → satisfied
                {"id": "q_002", "question": "Q2?", "official_urls": []},       # → P1
                {"id": "q_003", "question": "Q3?", "official_urls": [url]},   # → P0
            ],
        }
        responses = [
            {"question_id": "q_001", "platform": "deepseek",
             "response_text": f"See {url}"},
            {"question_id": "q_002", "platform": "deepseek",
             "response_text": "answer"},
            {"question_id": "q_003", "platform": "deepseek",
             "response_text": "no mention"},
        ]
        # 补足 q_001 的其余 5 个平台回答，使 citation_rate = 6/6
        for p in ["qwen", "kimi", "chatgpt", "gemini", "doubao"]:
            responses.append({"question_id": "q_001", "platform": p,
                               "response_text": f"See {url}"})

        result = self._run_pipeline(tmp_path, questions, responses, write_json)
        severities = [r["severity"] for r in result["results"]]
        assert severities.index("P0") < severities.index("P1")
        assert severities.index("P1") < severities.index("OK")

    def test_threshold_below_75pct_is_not_cited(self, tmp_path, write_json):
        """4/6 ≈ 0.667 < 0.75 阈值时，状态应为 not_cited"""
        url = "https://docs.example.com/page"
        questions = {
            "community": "test",
            "questions": [{"id": "q_001", "question": "Q?", "official_urls": [url]}],
        }
        platforms = ["deepseek", "qwen", "kimi", "chatgpt", "gemini", "doubao"]
        non_citing = {"gemini", "doubao"}
        responses = [
            {"question_id": "q_001", "platform": p,
             "response_text": f"See {url}" if p not in non_citing else "no mention"}
            for p in platforms
        ]
        result = self._run_pipeline(tmp_path, questions, responses, write_json)
        q001 = result["results"][0]
        assert q001["citation_rate"] == pytest.approx(4 / 6, abs=1e-4)
        assert q001["status"] == "not_cited"

    def test_threshold_exactly_75pct_is_satisfied(self, tmp_path, write_json):
        """3/4 = 0.75 恰好达到阈值时，状态应为 satisfied"""
        url = "https://docs.example.com/page"
        questions = {
            "community": "test",
            "questions": [{"id": "q_001", "question": "Q?", "official_urls": [url]}],
        }
        platforms = ["deepseek", "qwen", "kimi", "chatgpt"]
        responses = [
            {"question_id": "q_001", "platform": p,
             "response_text": f"See {url}" if p != "chatgpt" else "no mention"}
            for p in platforms
        ]
        result = self._run_pipeline(tmp_path, questions, responses, write_json)
        q001 = result["results"][0]
        assert q001["citation_rate"] == pytest.approx(3 / 4, abs=1e-4)
        assert q001["status"] == "satisfied"
