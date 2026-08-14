from pathlib import Path

def get_process_cwd(pid: int):
    try:
        return Path(f"/proc/{pid}/cwd").resolve()
    except (FileNotFoundError, PermissionError, OSError):
        return None