"""Collect host hardware facts (Task 24). Prints Markdown bullet lines; unknowns say 'not detected'."""
from __future__ import annotations

import os
import platform
import subprocess
from pathlib import Path


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def cpu_model() -> str:
    if Path("/proc/cpuinfo").exists():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    if platform.system() == "Windows":
        out = _run(["wmic", "cpu", "get", "name"])
        lines = [x.strip() for x in out.splitlines() if x.strip() and x.strip() != "Name"]
        if lines:
            return lines[0]
    return platform.processor() or "not detected"


def collect() -> dict[str, str]:
    import psutil
    info = {
        "CPU model": cpu_model(),
        "Physical cores": str(psutil.cpu_count(logical=False) or "not detected"),
        "Logical processors": str(psutil.cpu_count(logical=True)),
        "Usable by this process": str(len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()),
        "Architecture": platform.machine(),
        "Operating system": f"{platform.system()} {platform.release()} ({platform.version()})",
        "Python": platform.python_version(),
        "Total memory (GiB)": f"{psutil.virtual_memory().total / 2**30:.2f}",
        "Available memory (GiB)": f"{psutil.virtual_memory().available / 2**30:.2f}",
    }
    lscpu = _run(["lscpu"])
    caches = [l.strip() for l in lscpu.splitlines() if "cache" in l.lower()]
    info["Cache sizes"] = "; ".join(caches) if caches else "not detected"
    numa = [l.strip() for l in lscpu.splitlines() if l.lower().startswith("numa")]
    info["NUMA"] = "; ".join(numa) if numa else "not detected"
    info["Memory channels"] = "not detected (not reliably exposed without root/dmidecode)"
    freq = psutil.cpu_freq()
    info["CPU frequency"] = f"{freq.current:.0f} MHz" if freq and freq.current else "not detected"
    return info


if __name__ == "__main__":
    for key, value in collect().items():
        print(f"- **{key}:** {value}")
