import os
import subprocess


def list_dir(path: str = ".") -> str:
    try:
        items = os.listdir(path)
        if not items:
            return "(empty)"
        return "\n".join(items[:200])
    except Exception as e:
        return f"error: {e}"


def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read(8000)
    except Exception as e:
        return f"error: {e}"


def run_shell(command: str) -> str:
    allowed_prefixes = (
        "dir",
        "echo",
        "type",
        "findstr",
        "cd",
    )

    command = command.strip()
    if not command.startswith(allowed_prefixes):
        return "error: command not allowed"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        return f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    except Exception as e:
        return f"error: {e}"