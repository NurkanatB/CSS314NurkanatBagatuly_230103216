"""Shared helpers for the Variant B lab: environment introspection (Part 0),
metric formulas, output tee, and JSON result storage. Standard library only."""
import json, os, platform, sys, multiprocessing as mp

STUDENT_ID = "230103216"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "outputs")


class Tee:
    """Print to the console AND collect lines so they can be saved to a file."""
    def __init__(self):
        self.lines = []

    def __call__(self, text=""):
        print(text, flush=True)
        self.lines.append(str(text))

    def save(self, filename):
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.lines) + "\n")
        return path


def cpu_name():
    """Best-effort CPU model string using only the standard library."""
    if os.environ.get("PROCESSOR_IDENTIFIER"):          # Windows
        return os.environ["PROCESSOR_IDENTIFIER"]
    try:                                                # Linux
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "n/a"


def env_info():
    return {
        "cpu_name": cpu_name(),
        "student_id": STUDENT_ID,
        "python": sys.version.replace("\n", " "),
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "machine": platform.machine(),
        "processor": platform.processor() or "n/a",
        "os_cpu_count": os.cpu_count(),
        "mp_cpu_count": mp.cpu_count(),
        "start_method": mp.get_start_method(),
        "available_start_methods": mp.get_all_start_methods(),
    }


def print_env(out):
    e = env_info()
    out("=== Part 0: Environment Introspection ===")
    out(f"Student ID           : {e['student_id']}")
    out(f"Python               : {e['python']}")
    out(f"Operating system     : {e['os']}")
    out(f"CPU                  : {e['cpu_name']}")
    out(f"Machine / processor  : {e['machine']} / {e['processor']}")
    out(f"os.cpu_count()       : {e['os_cpu_count']}")
    out(f"mp.cpu_count()       : {e['mp_cpu_count']}")
    out(f"MP start method      : {e['start_method']} (available: {e['available_start_methods']})")
    out()
    return e


def speedup(t1, tp):
    return t1 / tp

def efficiency(t1, tp, p):
    return speedup(t1, tp) / p * 100.0

def karp_flatt(t1, tp, p):
    """e(p) = ((p*Tp/T1) - 1) / (p - 1); undefined for p == 1."""
    return ((p * tp / t1) - 1.0) / (p - 1.0)


def save_json(name, data):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
