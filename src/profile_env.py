import argparse, json, os, platform, re, subprocess, sys
from salt import get_student_params

def sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

def parse_size(s):
    m = re.match(r"(\d+)\s*([KMG]?)", s.strip().upper())
    if not m: return None
    return int(m.group(1)) * {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}[m.group(2)]

_WIN = None
def win_query():
    global _WIN
    if _WIN is not None: return _WIN
    res = {"cpu": {}, "l1d_bytes": None}
    out = sh('powershell -NoProfile -Command "Get-CimInstance Win32_Processor | '
             'Select-Object Name,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors,'
             'L2CacheSize,L3CacheSize | ConvertTo-Json"')
    if out:
        try:
            d = json.loads(out)
            res["cpu"] = d[0] if isinstance(d, list) else d
        except Exception:
            pass
    out = sh('powershell -NoProfile -Command "Get-CimInstance Win32_CacheMemory | '
             'Select-Object Level,InstalledSize | ConvertTo-Json"')
    if out:
        try:
            d = json.loads(out)
            d = d if isinstance(d, list) else [d]
            l1 = [x["InstalledSize"] for x in d if x.get("Level") == 3 and x.get("InstalledSize")]
            if l1: res["l1d_bytes"] = int(l1[0]) * 1024
        except Exception:
            pass
    _WIN = res
    return res

def windows_caches():
    q = win_query(); c = q["cpu"]
    kb = lambda v: int(v) * 1024 if v else None
    return {"l1d_bytes": q["l1d_bytes"], "l2_bytes": kb(c.get("L2CacheSize")),
            "l3_bytes": kb(c.get("L3CacheSize")), "line_bytes": 64}

def linux_caches():
    out = {"l1d_bytes": None, "l2_bytes": None, "l3_bytes": None, "line_bytes": None}
    base = "/sys/devices/system/cpu/cpu0/cache"
    if not os.path.isdir(base): return out
    for d in sorted(os.listdir(base)):
        if not d.startswith("index"): continue
        rd = lambda f: open(f"{base}/{d}/{f}").read().strip()
        try:
            level, typ, size = int(rd("level")), rd("type"), parse_size(rd("size"))
            line = int(rd("coherency_line_size"))
        except Exception:
            continue
        out["line_bytes"] = line
        if level == 1 and typ == "Data": out["l1d_bytes"] = size
        elif level == 2: out["l2_bytes"] = size
        elif level == 3: out["l3_bytes"] = size
    return out

def mac_caches():
    g = lambda k: (lambda v: int(v) if v and v.isdigit() else None)(sh(f"sysctl -n {k}"))
    return {"l1d_bytes": g("hw.l1dcachesize"), "l2_bytes": g("hw.l2cachesize"),
            "l3_bytes": g("hw.l3cachesize"), "line_bytes": g("hw.cachelinesize")}

def cpu_info():
    sysname = platform.system()
    logical = os.cpu_count()
    info = {"model": None, "microarchitecture": None, "base_freq_mhz": None, "physical_cores": None}
    if sysname == "Linux":
        txt = open("/proc/cpuinfo").read()
        g = lambda k: (re.search(rf"^{k}\s*:\s*(.+)$", txt, re.M) or [None, None])[1]
        info["model"] = g("model name") or g("Model") or g("Hardware")
        fam, mod, step = g("cpu family"), g("model"), g("stepping")
        info["microarchitecture"] = f"family {fam} model {mod} stepping {step}" if fam else platform.machine()
        mx = sh("lscpu | awk -F: '/CPU max MHz/{print $2}'")
        mhz = g("cpu MHz")
        info["base_freq_mhz"] = float(mx) if mx else (float(mhz) if mhz else None)
        pairs = sh("lscpu -p=core,socket | grep -v '^#' | sort -u | wc -l")
        info["physical_cores"] = int(pairs) if pairs and pairs.isdigit() else None
    elif sysname == "Darwin":
        info["model"] = sh("sysctl -n machdep.cpu.brand_string")
        info["microarchitecture"] = sh("sysctl -n hw.cpufamily") or platform.machine()
        f = sh("sysctl -n hw.cpufrequency")
        info["base_freq_mhz"] = int(f) / 1e6 if f and f.isdigit() else None
        p = sh("sysctl -n hw.physicalcpu")
        info["physical_cores"] = int(p) if p and p.isdigit() else None
    elif sysname == "Windows":
        c = win_query()["cpu"]
        info["model"] = (c.get("Name") or "").strip() or platform.processor()
        info["microarchitecture"] = platform.processor()
        info["base_freq_mhz"] = c.get("MaxClockSpeed")
        info["physical_cores"] = c.get("NumberOfCores")
    try:
        import psutil
        info["physical_cores"] = info["physical_cores"] or psutil.cpu_count(logical=False)
        if not info["base_freq_mhz"] and psutil.cpu_freq():
            info["base_freq_mhz"] = psutil.cpu_freq().max or psutil.cpu_freq().current
    except ImportError:
        pass
    info["physical_cores"] = info["physical_cores"] or logical
    info["logical_threads"] = logical
    info["smt_enabled"] = logical > info["physical_cores"]
    info["threads_per_core"] = logical // info["physical_cores"]
    return info

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--student-id", default="230103216")
    ap.add_argument("--l1d-kb", type=int, default=None, help="override L1D size, KB")
    ap.add_argument("--l2-kb", type=int, default=None, help="override L2 size, KB")
    ap.add_argument("--l3-kb", type=int, default=None, help="override L3 size, KB")
    a = ap.parse_args()
    os.makedirs("results", exist_ok=True)
    caches = {"Linux": linux_caches, "Darwin": mac_caches,
              "Windows": windows_caches}.get(platform.system(), lambda: {})()
    for k, v in (("l1d_bytes", a.l1d_kb), ("l2_bytes", a.l2_kb), ("l3_bytes", a.l3_kb)):
        if v: caches[k] = v * 1024
    if not caches.get("line_bytes"): caches["line_bytes"] = 64
    prof = {
        "cpu": cpu_info(), "cache": caches,
        "os": {"system": platform.system(), "kernel": platform.release(),
               "version": platform.version(), "machine": platform.machine()},
        "python": {"implementation": platform.python_implementation(),
                   "version": sys.version, "compiler": platform.python_compiler()},
    }
    json.dump(prof, open("results/host_profile.json", "w"), indent=2)
    json.dump(get_student_params(a.student_id), open("results/salted_params.json", "w"), indent=2)
    print(json.dumps(prof, indent=2))

if __name__ == "__main__":
    main()