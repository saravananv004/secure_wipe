from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Callable

ProgressCallback = Callable[[int, int, str | None, int], None]


BLOCKED_PATH_NAMES = {
    "/",
    "C:\\",
    "C:/",
    "/home",
    "/usr",
    "/bin",
    "/sbin",
    "/etc",
    "/var",
    "/System",
    "/Library",
    "/Applications",
    "/Windows",
    "/Program Files",
    "/Program Files (x86)",
    "/Users",
}


def is_path_allowed(target_path: str) -> tuple[bool, str]:
    path = Path(target_path).resolve()
    path_str = str(path)

    if path_str in BLOCKED_PATH_NAMES:
        return False, "Wiping root or system directories is blocked for safety. Choose a normal project/demo folder."

    if len(path.parts) <= 1:
        return False, "The selected path is too broad. Choose a subfolder created for demonstration."

    return True, "Allowed"



def overwrite_file(filepath: str, passes: int = 3) -> int:
    file_size = os.path.getsize(filepath)
    if file_size == 0:
        os.remove(filepath)
        return 0

    with open(filepath, "r+b", buffering=0) as handle:
        for _ in range(passes):
            handle.seek(0)
            remaining = file_size
            block_size = 1024 * 1024
            while remaining > 0:
                chunk = min(block_size, remaining)
                handle.write(secrets.token_bytes(chunk))
                remaining -= chunk
            handle.flush()
            os.fsync(handle.fileno())

    directory = os.path.dirname(filepath)
    randomized_name = secrets.token_hex(8)
    renamed_path = os.path.join(directory, randomized_name)
    os.replace(filepath, renamed_path)
    os.remove(renamed_path)
    return file_size



def wipe_directory(directory: str, passes: int = 3, progress_callback: ProgressCallback | None = None) -> dict:
    files: list[str] = []
    bytes_wiped = 0

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            if not os.path.islink(full_path):
                files.append(full_path)

    total_files = len(files)

    for index, filepath in enumerate(files, start=1):
        bytes_wiped += overwrite_file(filepath, passes=passes)
        if progress_callback:
            progress_callback(index, total_files, filepath, bytes_wiped)

    return {
        "total_files": total_files,
        "files_wiped": total_files,
        "bytes_wiped": bytes_wiped,
    }
