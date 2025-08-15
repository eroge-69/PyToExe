#!/usr/bin/env python3
"""
fflag_scanner.py — Search the whole machine for specific "illegal" FFlag lines in .txt/.log/.json files.

Usage examples:
  python fflag_scanner.py
  python fflag_scanner.py --roots C:\ D:\ --ci
  python fflag_scanner.py --include-ext .cfg .ini --exclude-dirs node_modules .git
  python fflag_scanner.py --max-size-mb 100 --workers 8 --report-name myscan

Outputs (in the current folder by default):
  - <report-name>_fflag_scan_results.csv
  - <report-name>_fflag_scan_results.json
"""
import argparse, csv, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ILLEGAL_FLAGS = [
    "DFIntRemoteEventSingleInvocationSizeLimit",
    "FIntUGCValidationLeftArmThresholdFront",
    "FIntUGCValidationRightArmThresholdFront",
    "FIntUGCValidationRightLegThresholdBack",
    "FIntUGCValidationLeftLegThresholdBack",
    "FIntUGCValidationHeadAttachmentThreshold",
    "FIntUGCValidationTorsoThresholdBack",
    "DFIntS2PhysicsSenderRate",
    "DFFlagDebugUseCustomSimHumanoidRadius",
    "DFIntTouchSenderMaxBandwidthBpsScaling",
    "DFIntTouchSenderMaxBandwidthBps",
    "FIntUGCValidateLegZMaxSlender",
    "DFIntMaxMissedWorldStepsRemembered",
    "DFIntGameNetOptimizeParallelPhysicsSendAssemblyBatch",
    "FIntUGCValidationRightLegThresholdSide",
    "FIntUGCValidationRightLegThresholdFront",
    "FIntUGCValidationTorsoThresholdSide",
    "FFlagHumanoidParallelFixTickleFloor2",
    "FFlagFixMemoryPriorizationCrash",
    "FIntUGCValidationTorsoThresholdFront",
    "FIntUGCValidationLeftArmThresholdBack",
    "FIntUGCValidationLeftArmThresholdSide",
    "FIntUGCValidationLeftLegThresholdFront",
    "FIntUGCValidationLeftLegThresholdSide",
    "FIntUGCValidationRightArmThresholdBack",
    "FIntUGCValidationRightArmThresholdSide",
    "DFIntSimAdaptiveHumanoidPDControllerSubstepMultiplier",
    "DFIntPhysicsCountLocalSimulatedTouchEventsHundredthsPercentage",
    "DFIntDataSenderRate",
    "DFIntMaxClientSimulationRadius",
    "DFIntSolidFloorPercentForceApplication",
    "DFIntNonSolidFloorPercentForceApplication",
    "DFIntGameNetPVHeaderTranslationZeroCutoffExponent",
    "FIntParallelDynamicPartsFastClusterBatchSize",
    "DFIntMaximumFreefallMoveTimeInTenths",
    "DFIntAssemblyExtentsExpansionStudHundredth",
    "DFIntSimBroadPhasePairCountMax",
    "DFIntPhysicsDecompForceUpgradeVersion",
    "DFIntMaxAltitudePDStickHipHeightPercent",
    "DFIntUnstickForceAttackInTenths",
    "DFIntMinClientSimulationRadius",
    "DFIntMinimalSimRadiusBuffer",
    "DFFlagDebugPhysicsSenderDoesNotShrinkSimRadius",
    "FFlagDebugUseCustomSimRadius",
    "FIntGameNetLocalSpaceMaxSendIndex",
    "DFFlagSimHumanoidTimestepModelUpdate",
    "FFlagSimAdaptiveTimesteppingDefault2",
]

DEFAULT_TEXT_EXTS = {".txt", ".log", ".json"}

def build_regex(flags, case_insensitive=False):
    escaped = [re.escape(f) for f in flags]
    pattern = r'(?:^|[^A-Za-z0-9_])(' + '|'.join(escaped) + r')(?:[^A-Za-z0-9_]|$)'
    return re.compile(pattern, re.IGNORECASE if case_insensitive else 0)

def iter_roots(custom_roots=None):
    if custom_roots:
        for r in custom_roots:
            yield os.path.abspath(r)
        return
    if os.name == "nt":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = f"{letter}:\\\\"
            if os.path.exists(root):
                yield root
    else:
        yield "/"

def is_probably_binary(path):
    try:
        with open(path, 'rb') as f:
            chunk = f.read(4096)
        return b'\\x00' in chunk
    except Exception:
        return True

def safe_read_text_lines(path, max_bytes):
    try:
        if os.path.getsize(path) > max_bytes:
            return None
        if is_probably_binary(path):
            return None
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f, 1):
                yield i, line.rstrip("\\n")
    except Exception:
        return None

def search_text_file(path, regex, results):
    lines = safe_read_text_lines(path, max_bytes=results["max_file_bytes"])
    if lines is None:
        return
    for lineno, line in lines:
        if regex.search(line):
            results["hits"].append({
                "file": path,
                "type": "text",
                "line": lineno,
                "snippet": line.strip()[:500]
            })

def scan_json_obj(obj, path_stack, regex, hits, file_path):
    if isinstance(obj, dict):
        for k, v in obj.items():
            k_str = str(k)
            if regex.search(k_str):
                hits.append({
                    "file": file_path,
                    "type": "json-key",
                    "json_path": ".".join(path_stack + [k_str]),
                    "snippet": k_str
                })
            scan_json_obj(v, path_stack + [k_str], regex, hits, file_path)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            scan_json_obj(v, path_stack + [f"[{i}]"], regex, hits, file_path)

def search_json_file(path, regex, results):
    try:
        if os.path.getsize(path) > results["max_file_bytes"]:
            return
        if is_probably_binary(path):
            return
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        data = json.loads(text)
    except Exception:
        return search_text_file(path, regex, results)
    scan_json_obj(data, [], regex, results["hits"], path)

def should_skip_dir(dirpath, exclude_dirs_lower):
    name = os.path.basename(dirpath).lower()
    if name in exclude_dirs_lower:
        return True
    # Additional heavy/irrelevant dirs skipped by default
    default_skips = {
        "$recycle.bin", "system volume information", "winsxs",
        "installer", "program files", "program files (x86)",
        "node_modules", ".git", ".svn", ".hg", "__pycache__", ".cache"
    }
    return name in default_skips

def find_candidate_files(root, include_exts, exclude_dirs_lower):
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if not should_skip_dir(os.path.join(dirpath, d), exclude_dirs_lower)]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in include_exts:
                yield os.path.join(dirpath, fn)

def worker(path, regex, results):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        search_json_file(path, regex, results)
    else:
        search_text_file(path, regex, results)

def write_reports(hits, report_name):
    csv_path = f"{report_name}_fflag_scan_results.csv"
    json_path = f"{report_name}_fflag_scan_results.json"
    fields = ["file", "type", "line", "json_path", "snippet"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for h in hits:
            w.writerow({k: h.get(k, "") for k in fields})
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(hits, f, ensure_ascii=False, indent=2)
    return csv_path, json_path

def main():
    ap = argparse.ArgumentParser(description="Scan the system for specific 'illegal' FFlag lines/keys.")
    ap.add_argument("--roots", nargs="*", help="Root paths to scan. Default: all drives on Windows or '/' on Unix.")
    ap.add_argument("--ci", action="store_true", help="Case-insensitive matching (default: exact case).")
    ap.add_argument("--max-size-mb", type=int, default=50, help="Skip files larger than this size (MB). Default: 50.")
    ap.add_argument("--workers", type=int, default=min(8, (os.cpu_count() or 4)), help="Thread workers. Default: CPU-based.")
    ap.add_argument("--include-ext", nargs="*", default=list(DEFAULT_TEXT_EXTS), help="Extra file extensions to include (e.g., .cfg .ini). .json is already parsed structurally.")
    ap.add_argument("--exclude-dirs", nargs="*", default=[], help="Directory names (exact) to exclude (e.g., node_modules .git).")
    ap.add_argument("--report-name", default="fflag", help="Prefix for output report files.")
    args = ap.parse_args()

    include_exts = set(e.lower() if e.startswith(".") else f".{e.lower()}" for e in args.include_ext)
    include_exts.update(DEFAULT_TEXT_EXTS)  # always include defaults
    exclude_dirs_lower = set([d.lower() for d in args.exclude_dirs])

    regex = build_regex(ILLEGAL_FLAGS, case_insensitive=args.ci)
    roots = list(iter_roots(args.roots))
    print(f"[i] Roots to scan: {roots}")

    results = {
        "hits": [],
        "max_file_bytes": args.max_size_mb * 1024 * 1024
    }

    candidates = []
    t0 = time.time()
    for r in roots:
        for p in find_candidate_files(r, include_exts, exclude_dirs_lower):
            candidates.append(p)
    t1 = time.time()
    print(f"[i] Indexed {len(candidates):,} candidate files in {t1 - t0:.1f}s")

    scanned = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(worker, p, regex, results) for p in candidates]
        for fut in as_completed(futures):
            scanned += 1
            if scanned % 500 == 0:
                print(f"[i] Scanned {scanned:,}/{len(candidates):,} files...")

    csv_path, json_path = write_reports(results["hits"], args.report_name)
    print(f"\\n=== Scan complete ===")
    print(f"Matches found: {len(results['hits']):,}")
    print(f"Report CSV:  {os.path.abspath(csv_path)}")
    print(f"Report JSON: {os.path.abspath(json_path)}")

if __name__ == "__main__":
    main()
