"""Tests for get-question/scripts/validate-questions.py — validate() function."""

from conftest import load_skill_script

_mod = load_skill_script("get-question/scripts/validate-questions.py")
validate = _mod.validate


def _q(id="q_001", question="How to install openEuler on ARM?"):
    return {"id": id, "question": question}


class TestValidateQuestions:
    def test_valid_single_question(self):
        assert validate([_q()]) == []

    def test_valid_multiple_questions(self):
        questions = [_q(f"q_{i:03d}", f"Question number {i}?") for i in range(1, 4)]
        assert validate(questions) == []

    def test_valid_with_optional_fields(self):
        q = _q()
        q["doc_form"] = "H"
        q["official_urls"] = ["https://docs.openeuler.org/install.html"]
        q["note"] = "path is correct"
        assert validate([q]) == []

    def test_missing_id_field(self):
        errors = validate([{"question": "How to install?"}])
        assert any("Missing fields" in e for e in errors)

    def test_missing_question_field(self):
        errors = validate([{"id": "q_001"}])
        assert any("Missing fields" in e for e in errors)

    def test_missing_both_fields(self):
        errors = validate([{"doc_form": "H"}])
        assert any("Missing fields" in e for e in errors)

    def test_invalid_id_no_prefix(self):
        errors = validate([_q(id="001")])
        assert any("q_NNN" in e for e in errors)

    def test_invalid_id_too_few_digits(self):
        errors = validate([_q(id="q_01")])
        assert any("q_NNN" in e for e in errors)

    def test_invalid_id_too_many_digits(self):
        errors = validate([_q(id="q_0001")])
        assert any("q_NNN" in e for e in errors)

    def test_invalid_id_letters_in_number(self):
        errors = validate([_q(id="q_00a")])
        assert any("q_NNN" in e for e in errors)

    def test_duplicate_id(self):
        errors = validate([_q("q_001"), _q("q_001")])
        assert any("Duplicate" in e for e in errors)

    def test_empty_question_text(self):
        errors = validate([_q(question="")])
        assert any("empty" in e.lower() or "short" in e.lower() for e in errors)

    def test_question_too_short(self):
        errors = validate([_q(question="Hi")])
        assert any("short" in e.lower() for e in errors)

    def test_whitespace_only_question(self):
        errors = validate([_q(question="   ")])
        assert any("empty" in e.lower() or "short" in e.lower() for e in errors)

    def test_non_dict_item(self):
        errors = validate(["not a dict"])
        assert any("object" in e.lower() for e in errors)

    def test_non_list_input(self):
        errors = validate({"id": "q_001", "question": "test question?"})
        assert any("array" in e.lower() for e in errors)

    def test_multiple_errors_all_reported(self):
        questions = [
            {"id": "bad_id", "question": "x"},   # bad id + too short
            _q("q_002"),                           # valid
            _q("q_002"),                           # duplicate
        ]
        errors = validate(questions)
        assert len(errors) >= 2   # bad_id + duplicate (short question may also be flagged)

    def test_empty_list_valid(self):
        assert validate([]) == []
