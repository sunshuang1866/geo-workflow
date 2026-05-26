"""Clean code compliance tests.

Verifies that pipeline scripts honor the stdout/stderr protocol:
  - stdout: pure JSON only (or empty)
  - stderr: all human-readable progress/warning/error text
  - exit code 0 on success, 1 on failure

Each test runs the target script as a subprocess with minimal valid fixtures
and asserts stdout is parseable JSON.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


def _run(args, stdin_text=None):
    """Run a command and return (returncode, stdout_text, stderr_text)."""
    result = subprocess.run(
        args,
        input=stdin_text,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def _write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class TestStdoutIsJson:
    """Each script must emit only valid JSON (or nothing) on stdout."""

    def test_score_urls_stdout_is_json(self, tmp_path):
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
        _write_json(q_path, questions)
        _write_json(r_path, responses)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, stdout, _ = _run([sys.executable, str(script),
                               str(r_path), str(q_path), str(out_path)])

        assert rc == 0, f"score-urls.py exited {rc}"
        assert stdout.strip() == "", \
            f"score-urls.py wrote non-empty stdout: {stdout[:200]!r}"

    def test_validate_inputs_stdout_is_empty(self, tmp_path):
        questions = {
            "community": "test",
            "questions": [{"id": "q_001", "question": "How to install?",
                           "official_urls": []}],
        }
        responses = {"responses": [{"question_id": "q_001", "platform": "deepseek",
                                    "response_text": "some answer"}]}
        q_path = tmp_path / "questions.json"
        r_path = tmp_path / "responses.json"
        _write_json(q_path, questions)
        _write_json(r_path, responses)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "validate-inputs.py"
        rc, stdout, _ = _run([sys.executable, str(script),
                               str(r_path), str(q_path)])

        assert rc == 0, f"validate-inputs.py exited {rc}"
        assert stdout.strip() == "", \
            f"validate-inputs.py wrote non-empty stdout: {stdout[:200]!r}"

    def test_validate_questions_stdout_is_empty(self):
        questions = {"questions": [{"id": "q_001", "question": "How to install openEuler?"}]}
        stdin_text = json.dumps(questions, ensure_ascii=False)

        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, _ = _run([sys.executable, str(script)], stdin_text=stdin_text)

        assert rc == 0, f"validate-questions.py exited {rc}"
        assert stdout.strip() == "", \
            f"validate-questions.py wrote non-empty stdout: {stdout[:200]!r}"


class TestExitCodes:
    """Scripts must exit 1 on invalid input, never silently succeed."""

    def test_score_urls_exits_1_on_missing_responses(self, tmp_path):
        questions = {"community": "test", "questions": []}
        q_path = tmp_path / "questions.json"
        _write_json(q_path, questions)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, _, stderr = _run([sys.executable, str(script),
                               str(tmp_path / "nonexistent.json"),
                               str(q_path),
                               str(tmp_path / "out.json")])
        assert rc == 1, f"Expected exit 1, got {rc}"

    def test_score_urls_exits_1_on_wrong_arg_count(self):
        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, _, stderr = _run([sys.executable, str(script)])
        assert rc == 1

    def test_validate_inputs_exits_1_on_missing_file(self, tmp_path):
        questions = {"community": "test", "questions": []}
        q_path = tmp_path / "questions.json"
        _write_json(q_path, questions)

        script = SKILLS_DIR / "scoring-engine" / "scripts" / "validate-inputs.py"
        rc, _, _ = _run([sys.executable, str(script),
                         str(tmp_path / "nonexistent.json"),
                         str(q_path)])
        assert rc == 1

    def test_validate_questions_exits_1_on_bad_json(self):
        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, stderr = _run([sys.executable, str(script)],
                                   stdin_text="{not valid json")
        assert rc == 1
        assert stdout.strip() == "", \
            f"validate-questions.py leaked to stdout on error: {stdout[:200]!r}"

    def test_validate_questions_exits_1_on_bad_id(self):
        questions = {"questions": [{"id": "bad", "question": "How to install?"}]}
        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, _ = _run([sys.executable, str(script)],
                               stdin_text=json.dumps(questions))
        assert rc == 1
        assert stdout.strip() == "", \
            f"validate-questions.py leaked to stdout on validation error: {stdout[:200]!r}"


class TestErrorMessagesGoToStderr:
    """ERROR: messages must appear on stderr, never stdout."""

    def test_score_urls_error_on_stderr_not_stdout(self, tmp_path):
        script = SKILLS_DIR / "scoring-engine" / "scripts" / "score-urls.py"
        rc, stdout, stderr = _run([sys.executable, str(script),
                                    str(tmp_path / "missing.json"),
                                    str(tmp_path / "missing.json"),
                                    str(tmp_path / "out.json")])
        assert rc == 1
        assert "ERROR" in stderr, "Expected ERROR message in stderr"
        assert "ERROR" not in stdout, "ERROR message must not appear in stdout"

    def test_validate_questions_error_on_stderr_not_stdout(self):
        script = SKILLS_DIR / "get-question" / "scripts" / "validate-questions.py"
        rc, stdout, stderr = _run([sys.executable, str(script)],
                                   stdin_text="{bad json")
        assert rc == 1
        assert stdout.strip() == ""
        assert len(stderr.strip()) > 0, "Expected error message in stderr"
