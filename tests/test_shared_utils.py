"""
tests/test_shared_utils.py

测试 _shared/utils.py 共享工具函数
"""
import pytest
from _shared.utils import load_json, resolve_platform_token


class TestLoadJson:
    """测试 JSON 文件加载功能"""

    def test_valid_object(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"key": "value"}', encoding="utf-8")
        assert load_json(str(f)) == {"key": "value"}

    def test_valid_array(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('[1, 2, 3]', encoding="utf-8")
        assert load_json(str(f)) == [1, 2, 3]

    def test_missing_file_exits_1(self, tmp_path):
        """文件不存在时应以 exit code 1 退出"""
        with pytest.raises(SystemExit) as exc:
            load_json(str(tmp_path / "nonexistent.json"))
        assert exc.value.code == 1

    def test_missing_optional_returns_none(self, tmp_path):
        """optional=True 时文件不存在返回 None，不退出"""
        result = load_json(str(tmp_path / "nonexistent.json"), optional=True)
        assert result is None

    def test_invalid_json_exits_1(self, tmp_path):
        """JSON 语法错误时应以 exit code 1 退出"""
        f = tmp_path / "bad.json"
        f.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            load_json(str(f))
        assert exc.value.code == 1

    def test_label_appears_in_error(self, tmp_path, capsys):
        """错误信息应包含用于定位的 label 名称"""
        with pytest.raises(SystemExit):
            load_json(str(tmp_path / "missing.json"), label="questions.json")
        assert "questions.json" in capsys.readouterr().err

    def test_unicode_content(self, tmp_path):
        """应正确读取包含中文字符的 JSON 文件"""
        f = tmp_path / "data.json"
        f.write_text('{"community": "openEuler中文"}', encoding="utf-8")
        assert load_json(str(f))["community"] == "openEuler中文"


class TestResolvePlatformToken:
    """测试平台 Token 解析功能"""

    def test_explicit_token_returned(self):
        """显式传入 token 时直接返回"""
        platform, token = resolve_platform_token(platform="github", token="mytoken")
        assert (platform, token) == ("github", "mytoken")

    def test_explicit_token_defaults_platform_to_github(self):
        """只传入 token 不传 platform 时，platform 默认为 github"""
        platform, token = resolve_platform_token(token="mytoken")
        assert platform == "github"
        assert token == "mytoken"

    def test_github_platform_reads_env(self, monkeypatch):
        """platform=github 时从 GITHUB_TOKEN 环境变量读取 token"""
        monkeypatch.setenv("GITHUB_TOKEN", "ghtoken")
        monkeypatch.delenv("GITCODE_TOKEN", raising=False)
        _, token = resolve_platform_token(platform="github")
        assert token == "ghtoken"

    def test_gitcode_platform_reads_env(self, monkeypatch):
        """platform=gitcode 时从 GITCODE_TOKEN 环境变量读取 token"""
        monkeypatch.setenv("GITCODE_TOKEN", "gctoken")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        platform, token = resolve_platform_token(platform="gitcode")
        assert (platform, token) == ("gitcode", "gctoken")

    def test_auto_detect_prefers_github(self, monkeypatch):
        """两个 token 都存在时，优先选择 GitHub"""
        monkeypatch.setenv("GITHUB_TOKEN", "ghtoken")
        monkeypatch.setenv("GITCODE_TOKEN", "gctoken")
        platform, token = resolve_platform_token()
        assert (platform, token) == ("github", "ghtoken")

    def test_auto_detect_falls_back_to_gitcode(self, monkeypatch):
        """GITHUB_TOKEN 不存在时，自动降级到 GitCode"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITCODE_TOKEN", "gctoken")
        platform, token = resolve_platform_token()
        assert (platform, token) == ("gitcode", "gctoken")

    def test_no_token_returns_none(self, monkeypatch):
        """两个环境变量均未设置时，返回 (github, None)"""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITCODE_TOKEN", raising=False)
        platform, token = resolve_platform_token()
        assert platform == "github"
        assert token is None
