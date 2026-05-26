"""Tests for _shared/utils.py — load_json and resolve_platform_token."""

import pytest
from _shared.utils import load_json, resolve_platform_token


class TestLoadJson:
    def test_valid_object(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"key": "value"}', encoding="utf-8")
        assert load_json(str(f)) == {"key": "value"}

    def test_valid_array(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('[1, 2, 3]', encoding="utf-8")
        assert load_json(str(f)) == [1, 2, 3]

    def test_missing_file_exits_1(self, tmp_path):
        with pytest.raises(SystemExit) as exc:
            load_json(str(tmp_path / "nonexistent.json"))
        assert exc.value.code == 1

    def test_missing_optional_returns_none(self, tmp_path):
        result = load_json(str(tmp_path / "nonexistent.json"), optional=True)
        assert result is None

    def test_invalid_json_exits_1(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(SystemExit) as exc:
            load_json(str(f))
        assert exc.value.code == 1

    def test_label_appears_in_error(self, tmp_path, capsys):
        with pytest.raises(SystemExit):
            load_json(str(tmp_path / "missing.json"), label="questions.json")
        assert "questions.json" in capsys.readouterr().err

    def test_unicode_content(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"community": "openEuler中文"}', encoding="utf-8")
        assert load_json(str(f))["community"] == "openEuler中文"


class TestResolvePlatformToken:
    def test_explicit_token_returned(self):
        platform, token = resolve_platform_token(platform="github", token="mytoken")
        assert (platform, token) == ("github", "mytoken")

    def test_explicit_token_defaults_platform_to_github(self):
        platform, token = resolve_platform_token(token="mytoken")
        assert platform == "github"
        assert token == "mytoken"

    def test_github_platform_reads_env(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghtoken")
        monkeypatch.delenv("GITCODE_TOKEN", raising=False)
        _, token = resolve_platform_token(platform="github")
        assert token == "ghtoken"

    def test_gitcode_platform_reads_env(self, monkeypatch):
        monkeypatch.setenv("GITCODE_TOKEN", "gctoken")
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        platform, token = resolve_platform_token(platform="gitcode")
        assert (platform, token) == ("gitcode", "gctoken")

    def test_auto_detect_prefers_github(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghtoken")
        monkeypatch.setenv("GITCODE_TOKEN", "gctoken")
        platform, token = resolve_platform_token()
        assert (platform, token) == ("github", "ghtoken")

    def test_auto_detect_falls_back_to_gitcode(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITCODE_TOKEN", "gctoken")
        platform, token = resolve_platform_token()
        assert (platform, token) == ("gitcode", "gctoken")

    def test_no_token_returns_none(self, monkeypatch):
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITCODE_TOKEN", raising=False)
        platform, token = resolve_platform_token()
        assert platform == "github"
        assert token is None
