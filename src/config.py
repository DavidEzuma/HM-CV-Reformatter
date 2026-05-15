"""Persistent config stored in %APPDATA%/HMCVReformatter/config.json."""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(os.environ.get("APPDATA", ".")) / "HMCVReformatter" / "config.json"


def load() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(data, indent=2))


def get_api_key() -> str:
    return load().get("deepseek_api_key") or os.environ.get("DEEPSEEK_API_KEY", "")


def set_api_key(key: str) -> None:
    cfg = load()
    cfg["deepseek_api_key"] = key.strip()
    save(cfg)
