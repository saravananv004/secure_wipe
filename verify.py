from __future__ import annotations

import os


def verify_wipe(directory: str) -> bool:
    for _, _, files in os.walk(directory):
        if files:
            return False
    return True
