import subprocess
from pathlib import Path

script_dir = Path(__file__).resolve().parent

subprocess.run(
    [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--name", "Better-Schology",
        "--collect-all", "lxml",
        "--hidden-import", "updater",
        "--add-data", "HTML;HTML",
        "--add-data", "libreoffice;libreoffice",
        "--add-binary", "update.exe;.",
        "server.py",
    ],
    cwd=script_dir,
    check=True,
)