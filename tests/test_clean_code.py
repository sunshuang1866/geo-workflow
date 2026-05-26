"""
tests/test_clean_code.py

测试各管道脚本的 stdout/stderr 协议合规性：
  - stdout：仅输出纯 JSON（或为空）
  - stderr：所有进度信息、警告、错误信息
  - 成功退出码为 0，失败退出码为 1
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


class TestStdoutIsJson:
    """测试各脚本 stdout 输出符合纯 JSON 协议"""

    def test_score_urls_stdout_is_empty(self, tmp_path, write_json, run_script):
        """score-urls.py 正常运行时 stdout 应为空（结果写入文件，不打印到 stdout）"""
        url = "https://docs.example.com/install"
        questions = {
            "community": "test",
            "questions": [{"id": "q_001", "question": "How to install?",
                           "official_urls": [url]}],
        }
        responses = [{"question_id": "q_001", "platform": "deepseek",
                      "response_text": f"See {url}"}]
        q_path = tmp_path / "questions.json"
        r_path = tmp_path / "responses.json"
        out_path = tmp_path / "scoring-results.json"
        write_json(q_path, questions)
        write_json(r_path, responses)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, stdout, _ = run_script([sys.executable, str(script),
                                    str(r_path), str(q_path), str(out_path)])

        assert rc == 0, f"score-urls.py 以非零退出码退出：{rc}"
        assert stdout.strip() == "", \
            f"score-urls.py 向 stdout 写入了非 JSON 内容：{stdout[:200]!r}"

    def test_validate_inputs_stdout_is_empty(self, tmp_path, write_json, run_script):
        """validate-inputs.py 正常运行时 stdout 应为空"""
        questions = {
            "community": "test",
            "questions": [{"id": "q_001", "question": "How to install?",
                           "official_urls": []}],
        }
        responses = {"responses": [{"question_id": "q_001", "platform": "deepseek",
                                    "response_text": "some answer"}]}
        q_path = tmp_path / "questions.json"
        r_path = tmp_path / "responses.json"
        write_json(q_path, questions)
        write_json(r_path, responses)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "validate-inputs.py"
        rc, stdout, _ = run_script([sys.executable, str(script),
                                    str(r_path), str(q_path)])

        assert rc == 0, f"validate-inputs.py 以非零退出码退出：{rc}"
        assert stdout.strip() == "", \
            f"validate-inputs.py 向 stdout 写入了非 JSON 内容：{stdout[:200]!r}"

    def test_validate_questions_stdout_is_empty(self, run_script):
        """validate-questions.py 正常运行时 stdout 应为空"""
        questions = {"questions": [{"id": "q_001", "question": "How to install openEuler?"}]}
        stdin_text = json.dumps(questions, ensure_ascii=False)

        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, _ = run_script([sys.executable, str(script)], stdin_text=stdin_text)

        assert rc == 0, f"validate-questions.py 以非零退出码退出：{rc}"
        assert stdout.strip() == "", \
            f"validate-questions.py 向 stdout 写入了非 JSON 内容：{stdout[:200]!r}"


class TestExitCodes:
    """测试无效输入时各脚本以 exit code 1 退出"""

    def test_score_urls_exits_1_on_missing_responses(self, tmp_path, write_json, run_script):
        """responses.json 不存在时，score-urls.py 应以 exit code 1 退出"""
        questions = {"community": "test", "questions": []}
        q_path = tmp_path / "questions.json"
        write_json(q_path, questions)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, _, _ = run_script([sys.executable, str(script),
                                str(tmp_path / "nonexistent.json"),
                                str(q_path),
                                str(tmp_path / "out.json")])
        assert rc == 1, f"期望 exit code 1，实际为 {rc}"

    def test_score_urls_exits_1_on_wrong_arg_count(self, run_script):
        """参数数量不足时，score-urls.py 应以 exit code 1 退出"""
        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, _, _ = run_script([sys.executable, str(script)])
        assert rc == 1

    def test_validate_inputs_exits_1_on_missing_file(self, tmp_path, write_json, run_script):
        """输入文件缺失时，validate-inputs.py 应以 exit code 1 退出"""
        questions = {"community": "test", "questions": []}
        q_path = tmp_path / "questions.json"
        write_json(q_path, questions)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "validate-inputs.py"
        rc, _, _ = run_script([sys.executable, str(script),
                                str(tmp_path / "nonexistent.json"),
                                str(q_path)])
        assert rc == 1

    def test_validate_questions_exits_1_on_bad_json(self, run_script):
        """JSON 语法错误时，validate-questions.py 应以 exit code 1 退出"""
        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, _ = run_script([sys.executable, str(script)],
                                   stdin_text="{not valid json")
        assert rc == 1
        assert stdout.strip() == "", \
            f"validate-questions.py 在错误时向 stdout 泄露了内容：{stdout[:200]!r}"

    def test_validate_questions_exits_1_on_bad_id(self, run_script):
        """问题 id 格式不合法时，validate-questions.py 应以 exit code 1 退出"""
        questions = {"questions": [{"id": "bad", "question": "How to install?"}]}
        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, _ = run_script([sys.executable, str(script)],
                                   stdin_text=json.dumps(questions))
        assert rc == 1
        assert stdout.strip() == "", \
            f"validate-questions.py 在验证失败时向 stdout 泄露了内容：{stdout[:200]!r}"


class TestErrorMessagesGoToStderr:
    """测试错误信息严格输出到 stderr，不污染 stdout"""

    def test_score_urls_error_on_stderr_not_stdout(self, tmp_path, run_script):
        """score-urls.py 的 ERROR 消息应在 stderr，不应出现在 stdout"""
        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, stdout, stderr = run_script([sys.executable, str(script),
                                         str(tmp_path / "missing.json"),
                                         str(tmp_path / "missing.json"),
                                         str(tmp_path / "out.json")])
        assert rc == 1
        assert "ERROR" in stderr, "期望 stderr 中包含 ERROR 消息"
        assert "ERROR" not in stdout, "ERROR 消息不应出现在 stdout"

    def test_validate_questions_error_on_stderr_not_stdout(self, run_script):
        """validate-questions.py 的错误消息应在 stderr，stdout 应为空"""
        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, stderr = run_script([sys.executable, str(script)],
                                        stdin_text="{bad json")
        assert rc == 1
        assert stdout.strip() == ""
        assert len(stderr.strip()) > 0, "期望 stderr 中包含错误消息"
