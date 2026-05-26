"""
tests/test_validate_questions.py

测试 get-question/scripts/validate-questions.py 问题集验证函数
"""
from .fixtures import load_skill_script

_mod = load_skill_script("get-question/scripts/validate-questions.py")
validate = _mod.validate


def _q(id="q_001", question="How to install openEuler on ARM?"):
    """构造最小合法问题条目的工厂函数"""
    return {"id": id, "question": question}


class TestValidateQuestions:
    """测试问题集合法性校验功能"""

    # ------------------------------------------------------------------
    # 合法输入
    # ------------------------------------------------------------------

    def test_valid_single_question(self):
        assert validate([_q()]) == []

    def test_valid_multiple_questions(self):
        questions = [_q(f"q_{i:03d}", f"Question number {i}?") for i in range(1, 4)]
        assert validate(questions) == []

    def test_valid_with_optional_fields(self):
        """包含可选字段 doc_form、official_urls、note 时仍应通过验证"""
        q = _q()
        q["doc_form"] = "H"
        q["official_urls"] = ["https://docs.openeuler.org/install.html"]
        q["note"] = "path is correct"
        assert validate([q]) == []

    def test_empty_list_valid(self):
        """空问题列表应视为合法"""
        assert validate([]) == []

    # ------------------------------------------------------------------
    # 必填字段缺失
    # ------------------------------------------------------------------

    def test_missing_id_field(self):
        errors = validate([{"question": "How to install?"}])
        assert any("Missing fields" in e for e in errors)

    def test_missing_question_field(self):
        errors = validate([{"id": "q_001"}])
        assert any("Missing fields" in e for e in errors)

    def test_missing_both_fields(self):
        errors = validate([{"doc_form": "H"}])
        assert any("Missing fields" in e for e in errors)

    # ------------------------------------------------------------------
    # id 格式校验（必须符合 q_NNN）
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # 重复 id
    # ------------------------------------------------------------------

    def test_duplicate_id(self):
        errors = validate([_q("q_001"), _q("q_001")])
        assert any("Duplicate" in e for e in errors)

    # ------------------------------------------------------------------
    # 问题文本校验
    # ------------------------------------------------------------------

    def test_empty_question_text(self):
        errors = validate([_q(question="")])
        assert any("empty" in e.lower() or "short" in e.lower() for e in errors)

    def test_question_too_short(self):
        errors = validate([_q(question="Hi")])
        assert any("short" in e.lower() for e in errors)

    def test_whitespace_only_question(self):
        errors = validate([_q(question="   ")])
        assert any("empty" in e.lower() or "short" in e.lower() for e in errors)

    # ------------------------------------------------------------------
    # 输入类型校验
    # ------------------------------------------------------------------

    def test_non_dict_item(self):
        """列表元素不是字典时应报错"""
        errors = validate(["not a dict"])
        assert any("object" in e.lower() for e in errors)

    def test_non_list_input(self):
        """输入不是列表时应报错"""
        errors = validate({"id": "q_001", "question": "test question?"})
        assert any("array" in e.lower() for e in errors)

    # ------------------------------------------------------------------
    # 多错误同时上报
    # ------------------------------------------------------------------

    def test_multiple_errors_all_reported(self):
        """多个问题同时存在时，所有错误均应被收集上报"""
        questions = [
            {"id": "bad_id", "question": "x"},  # id 非法 + 文本过短
            _q("q_002"),                          # 合法
            _q("q_002"),                          # 重复 id
        ]
        errors = validate(questions)
        assert len(errors) >= 2
