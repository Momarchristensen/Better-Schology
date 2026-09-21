import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_BASE_URL = "https://ca-net.schoology.com"


def _config_directory() -> Path:
    if getattr(sys, "frozen", False):
        app_data = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return app_data / "Better-Schology"
    return Path(__file__).resolve().parent


CONFIG_PATH = _config_directory() / "config.json"


def _validate_base_url(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("schoology_base_url must be a non-empty URL")

    base_url = value.strip().rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("schoology_base_url must use an HTTPS URL")
    if parsed.query or parsed.fragment:
        raise ValueError("schoology_base_url must not include a query or fragment")
    return base_url


def load_base_url() -> str:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps({"schoology_base_url": DEFAULT_BASE_URL}, indent=2) + "\n",
            encoding="utf-8",
        )
        return DEFAULT_BASE_URL

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {CONFIG_PATH}: {exc}") from exc

    try:
        return _validate_base_url(config.get("schoology_base_url"))
    except AttributeError as exc:
        raise RuntimeError(f"Configuration in {CONFIG_PATH} must be a JSON object") from exc
    except ValueError as exc:
        raise RuntimeError(f"Invalid configuration in {CONFIG_PATH}: {exc}") from exc


base_url = load_base_url()