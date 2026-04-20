"""tests/test_config.py — configuration precedence and demo-mode behavior."""

import importlib
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))


def _reload_config():
    import config as cfg

    importlib.reload(cfg)
    return cfg.Config


def test_ai_env_overrides_legacy_openai_env(monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "ai-key")
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-key")
    monkeypatch.setenv("AI_MODEL", "ai-model")
    monkeypatch.setenv("OPENAI_MODEL", "legacy-model")
    monkeypatch.setenv("AI_EMBEDDING_MODEL", "ai-embed")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "legacy-embed")

    config = _reload_config()

    assert config.ACTIVE_AI_API_KEY == "ai-key"
    assert config.OPENAI_API_KEY == "ai-key"
    assert config.AI_MODEL == "ai-model"
    assert config.OPENAI_MODEL == "ai-model"
    assert config.AI_EMBEDDING_MODEL == "ai-embed"
    assert config.OPENAI_EMBEDDING_MODEL == "ai-embed"


def test_legacy_openai_env_still_supported(monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-key")
    monkeypatch.delenv("AI_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "legacy-model")
    monkeypatch.delenv("AI_EMBEDDING_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "legacy-embed")

    config = _reload_config()

    assert config.ACTIVE_AI_API_KEY == "legacy-key"
    assert config.AI_MODEL == "legacy-model"
    assert config.AI_EMBEDDING_MODEL == "legacy-embed"


def test_demo_mode_uses_demo_key_when_no_byok(monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.setenv("DEMO_AI_API_KEY", "demo-key")

    config = _reload_config()

    assert config.DEMO_KEY_ACTIVE is True
    assert config.ACTIVE_AI_API_KEY == "demo-key"
    assert any("evaluation-only" in warning for warning in config.warnings())
