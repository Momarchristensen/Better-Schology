import sys
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional

import httpx

REPO = "Momarchristensen/Better-Schology"
GITHUB_API_LATEST = f"https://api.github.com/repos/{REPO}/releases/latest"


__version__ = "1.0.4"


def _parse_version(v: str) -> tuple:
    v = v.strip().lstrip("vV")
    parts = []
    for p in v.split("."):
        num = ""
        for ch in p:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def find_exe_asset(assets: list) -> Optional[dict]:
    for asset in assets:
        if asset.get("name", "").lower().endswith(".exe"):
            return asset
    return None


def check_for_update(timeout: float = 5.0) -> Optional[dict]:
    try:
        resp = httpx.get(
            GITHUB_API_LATEST,
            timeout=timeout,
            headers={"Accept": "application/vnd.github+json"},
            follow_redirects=True,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    latest_tag = data.get("tag_name", "")
    if not latest_tag or _parse_version(latest_tag) <= _parse_version(__version__):
        return None

    asset = find_exe_asset(data.get("assets", []))
    if not asset:
        return None

    return {
        "version": latest_tag,
        "notes": data.get("body", "") or "",
        "download_url": asset["browser_download_url"],
        "size": asset.get("size", 0),
    }


def download_update(download_url: str, dest_path: Path):
    with httpx.stream("GET", download_url, follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_bytes(chunk_size=1024 * 256):
                f.write(chunk)


def apply_update_and_restart(download_url: str):
    current_exe = Path(sys.executable).resolve()
    tmp_dir = Path(tempfile.gettempdir()) / "Better-Schology-update"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    new_exe = tmp_dir / "update.exe"

    download_update(download_url, new_exe)

    pid = os.getpid()
    bat_path = tmp_dir / "apply_update.bat"
    bat_contents = f"""@echo off
:wait
tasklist /FI "PID eq {pid}" 2>NUL | find /I "{pid}" >NUL
if not errorlevel 1 (
    timeout /t 1 /nobreak >NUL
    goto wait
)
copy /Y "{new_exe}" "{current_exe}" >NUL
start "" "{current_exe}"
del "%~f0"
"""
    bat_path.write_text(bat_contents, encoding="utf-8")

    subprocess.Popen(
        ["cmd", "/c", str(bat_path)],
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )

    os._exit(0)


def prompt_update_dialog(release_info: dict) -> bool:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    answer = messagebox.askyesno(
        "Update available",
        f"A new version ({release_info['version']}) of Better Schology is "
        f"available.\nYou're running {__version__}.\n\n"
        "Download and install it now? The app will restart.",
        parent=root,
    )
    root.destroy()
    return answer


def show_error_dialog(title: str, message: str):
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message, parent=root)
    root.destroy()


def check_for_updates():
    if not getattr(sys, "frozen", False):
        return

    release = check_for_update()
    if not release:
        return

    if prompt_update_dialog(release):
        try:
            apply_update_and_restart(release["download_url"])
        except Exception as exc:
            show_error_dialog("Update failed", f"Could not install the update:\n{exc}")
