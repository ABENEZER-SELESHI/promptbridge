from pathlib import Path

from promptbridge.config import load_config


def test_load_config_defaults(tmp_path: Path):
    config_path = tmp_path / "config.conf"
    config_path.write_text(
        """
[server]
host = 127.0.0.1
port = 9090

[auth]
api_key = local-key
require_auth = false

[providers]
default = echo
enabled = echo

[provider.echo]
prefix = test:

[storage]
database_path = ./data/test.sqlite3
persist_conversations = false
""".strip()
    )
    cfg = load_config(config_path)
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 9090
    assert cfg.api_key == "local-key"
    assert cfg.require_auth is False
    assert cfg.default_provider == "echo"
    assert cfg.enabled_providers == ["echo"]
    assert cfg.provider_configs["echo"].options["prefix"] == "test:"
