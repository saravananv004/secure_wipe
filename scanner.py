from __future__ import annotations

import psutil


def scan_devices() -> list[dict]:
    devices = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = round(usage.total / (1024 ** 3), 2)
            free_gb = round(usage.free / (1024 ** 3), 2)
        except PermissionError:
            total_gb = None
            free_gb = None

        devices.append(
            {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "filesystem": partition.fstype or "Unknown",
                "total_gb": total_gb,
                "free_gb": free_gb,
            }
        )
    return devices
