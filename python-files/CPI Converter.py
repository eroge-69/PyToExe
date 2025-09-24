#!/usr/bin/env python3
"""
cpp_builder_cli.py

Interactive CLI and one-shot commands to compile C++ sources into executables,
with basic cross-compilation support and toolchain registration.

Features:
 - Interactive REPL with commands: help, targets, use, register, unregister,
   compile, build-matrix, fetch-winlibs, show, exit.
 - Predefined target entries (host, windows-x86_64, linux-x86_64, linux-aarch64, macos-arm64, etc).
 - Register an explicit compiler command (or path) for a target: `register windows-x86_64 C:\toolchains\mingw\bin\g++`
 - Compile to one or more targets at once: `compile src.cpp --targets windows-x86_64,host -o outname --flags "-static -s"`
 - The script may attempt to download a portable WinLibs for Windows when you run `fetch-winlibs` (only on Windows host).
 - Toolchains downloaded are stored in `./toolchains/` and are used only for the script runs (PATH modified for subprocesses).
 - Uses pip auto-install for `requests` and `py7zr` only when absolutely necessary (download/extract).

Caveats:
 - Cross-compiling macOS builds from non-macOS hosts is non-trivial; support is limited.
 - The script prefers existing installed cross-compilers (e.g., x86_64-w64-mingw32-g++).
 - Installing real system packages (apt/dnf, Xcode CLI) still requires manual admin interaction in many cases.
"""

import os
import sys
import shlex
import shutil
import subprocess
import platform
import argparse
from pathlib import Path
from typing import Dict, Optional, List

# --- Helpers ----------------------------------------------------------------

def which(exe: str) -> Optional[str]:
    return shutil.which(exe)

def run(cmd: List[str], capture=False, env=None, check=True):
    print(f"> {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, stdout=(subprocess.PIPE if capture else None),
                          stderr=(subprocess.PIPE if capture else None), env=env)

def ensure_pip_packages(pkgs: List[str]):
    """Install pip packages in current environment if missing."""
    import importlib
    missing = []
    for p in pkgs:
        try:
            importlib.import_module(p)
        except Exception:
            missing.append(p)
    if missing:
        print("[*] Installing missing Python packages:", ", ".join(missing))
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

# --- Basic toolchain setup (winlibs downloader as optional helper) -----------

GITHUB_RELEASES_API = "https://api.github.com/repos/brechtsanders/winlibs_mingw/releases"

def download_and_extract_winlibs(dest_dir: Path) -> Optional[str]:
    """
    Attempt to download a winlibs (mingw-w64) release and extract. Returns bin path string.
    Only call this on Windows hosts or when you want mingw for windows targets.
    """
    ensure_pip_packages(["requests", "py7zr"])
    import requests
    dest_dir.mkdir(parents=True, exist_ok=True)
    print("[*] Querying GitHub for winlibs releases...")
    r = requests.get(GITHUB_RELEASES_API, timeout=30)
    r.raise_for_status()
    releases = r.json()
    chosen = None
    chosen_url = None
    for rel in releases:
        for a in rel.get("assets", []):
            name = a.get("name", "")
            if "x86_64-posix-seh" in name and (name.endswith(".zip") or name.endswith(".7z")):
                chosen = a
                chosen_url = a.get("browser_download_url")
                chosen_name = name
                break
        if chosen:
            break
    if not chosen:
        print("[!] No suitable winlibs asset found in releases.")
        return None
    local_archive = dest_dir / chosen_name
    if not local_archive.exists():
        print("[*] Downloading", chosen_url)
        with requests.get(chosen_url, stream=True, timeout=60) as resp:
            resp.raise_for_status()
            with open(local_archive, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    extract_dir = dest_dir / (chosen_name + "_extracted")
    if extract_dir.exists():
        print("[*] Already extracted:", extract_dir)
    else:
        print("[*] Extracting", local_archive)
        if chosen_name.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(local_archive, "r") as z:
                z.extractall(path=extract_dir)
        elif chosen_name.endswith(".7z"):
            import py7zr
            with py7zr.SevenZipFile(local_archive, mode='r') as ar:
                ar.extractall(path=extract_dir)
    # find bin
    for p in extract_dir.rglob("*/bin"):
        if (p / "g++.exe").exists() or (p / "gcc.exe").exists():
            return str(p.resolve())
    print("[!] Could not find compiler bin inside extracted archive.")
    return None

# --- Targets & registration --------------------------------------------------

DEFAULT_TARGETS: Dict[str, Dict] = {
    # "name": {"triple": ..., "compiler": None or command, "notes": ...}
    "host": {"triple": None, "compiler": None, "notes": "native toolchain (use g++/clang++/cl in PATH)"},
    "windows-x86_64": {"triple": "x86_64-w64-mingw32", "compiler": None, "notes": "mingw-w64 target; prefer x86_64-w64-mingw32-g++"},
    "linux-x86_64": {"triple": "x86_64-linux-gnu", "compiler": None, "notes": "linux x86_64 (native g++ normally)"},
    "linux-aarch64": {"triple": "aarch64-linux-gnu", "compiler": None, "notes": "ARM64 Linux; prefer aarch64-linux-gnu-g++ cross-compiler"},
    "macos-x86_64": {"triple": "x86_64-apple-darwin", "compiler": None, "notes": "macOS x86_64 — cross-compiling from non-macOS may be limited"},
    "macos-arm64": {"triple": "arm64-apple-darwin", "compiler": None, "notes": "macOS arm64 (M1) — cross-compiling from non-macOS is usually hard"},
}

TOOLCHAINS_DIR = Path.cwd() / "toolchains"

class Registry:
    def __init__(self):
        # target_name -> compiler_command (string or None)
        self.targets = DEFAULT_TARGETS.copy()

    def list_targets(self):
        rows = []
        for name, data in self.targets.items():
            rows.append((name, data.get("compiler"), data.get("triple"), data.get("notes")))
        return rows

    def show(self, name: str):
        data = self.targets.get(name)
        if not data:
            return None
        return data

    def register(self, name: str, compiler_cmd: str):
        if name not in self.targets:
            self.targets[name] = {"triple": None, "compiler": None, "notes": "user-registered"}
        self.targets[name]["compiler"] = compiler_cmd
        return True

    def unregister(self, name: str):
        if name in self.targets:
            self.targets[name]["compiler"] = None
            return True
        return False

REG = Registry()

# --- Compile logic ----------------------------------------------------------

def resolve_compiler_for_target(target: str) -> Optional[str]:
    """
    Return a compiler executable/command for the target.
    Priority:
      1) user-registered explicit compiler in registry
      2) well-known cross compiler name by triple (e.g. x86_64-w64-mingw32-g++)
      3) fallback to 'g++'/'clang++' on host if target is host or linux-x86_64
    """
    entry = REG.targets.get(target)
    if not entry:
        return None
    if entry.get("compiler"):
        # allow quoting; return raw string
        return entry["compiler"]
    triple = entry.get("triple")
    # attempt heuristics
    if target == "host":
        # prefer g++ then clang++ then cl
        for c in ("g++", "clang++", "clang", "cl"):
            if which(c):
                return c
        return None
    if triple:
        # common naming: <triple>-g++
        candidate = triple + "-g++"
        if which(candidate):
            return candidate
        # try g++-<triple> or with gcc prefix
        alt = f"g++-{triple}"
        if which(alt):
            return alt
        # mingw special case
        if "w64-mingw32" in triple:
            if which("x86_64-w64-mingw32-g++"):
                return "x86_64-w64-mingw32-g++"
    # last resort: use clang with -target if available
    if which("clang++"):
        return "clang++"
    return None

def compile_for_target(source: Path, target: str, output: Optional[str] = None,
                       extra_flags: Optional[List[str]] = None) -> bool:
    """
    Compile `source` for `target`.
    Returns True on success.
    """
    extra_flags = extra_flags or []
    compiler = resolve_compiler_for_target(target)
    if not compiler:
        print(f"[!] No compiler resolved for target '{target}'. Use 'register {target} <compiler_cmd>' to set one.")
        return False

    # determine output name
    if output:
        out = Path(output)
    else:
        base = source.stem
        ext = ".exe" if "windows" in target or output and str(output).lower().endswith(".exe") else ""
        out = Path(base + "_" + target + ext)

    env = os.environ.copy()
    # If compiler is a path inside our toolchains dir (for downloaded winlibs), ensure PATH includes its folder
    # If compiler contains spaces or is a complex command, we will use shell invocation via shlex.split
    cmd_list = []
    is_shell_invocation = False

    # If compiler is clang++ and triple available, use -target
    entry = REG.targets.get(target, {})
    triple = entry.get("triple")

    # If compiler is clang++ and triple exists -> use -target triple
    if compiler.endswith("clang++") and triple:
        cmd_list = [compiler, str(source), "-o", str(out), "-std=c++17", "-O2", "--target=" + triple, *extra_flags]
    elif compiler.endswith("clang") and triple:
        cmd_list = [compiler, str(source), "-o", str(out), "-std=c++17", "-O2", "--target=" + triple, *extra_flags]
    else:
        # generic: try to call compiler directly
        # If compiler contains spaces or is a path, split it
        comp_parts = shlex.split(compiler)
        cmd_list = [*comp_parts, str(source), "-o", str(out), "-std=c++17", "-O2", *extra_flags]

    # If compiler appears to be a Windows .exe inside toolchains, ensure its bin dir added to PATH for this run
    try:
        comp_exec = shutil.which(comp_parts[0]) if comp_parts else shutil.which(compiler)
        if not comp_exec:
            # maybe it's a path (absolute or relative) provided by user
            if os.path.isabs(comp_parts[0]) and Path(comp_parts[0]).exists():
                binp = str(Path(comp_parts[0]).parent.resolve())
                env["PATH"] = binp + os.pathsep + env.get("PATH", "")
                comp_exec = comp_parts[0]
    except Exception:
        comp_exec = None

    # On Windows, if compiling with mingw toolchain we may want -static or -static-libgcc etc (left to user)
    # Run
    try:
        run(cmd_list, env=env)
        print(f"[+] Build for target '{target}' succeeded -> {out.resolve()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[!] Build for target '{target}' FAILED.")
        if e.stdout:
            print("STDOUT:", e.stdout.decode(errors="ignore"))
        if e.stderr:
            print("STDERR:", e.stderr.decode(errors="ignore"))
        return False

# --- CLI / REPL -------------------------------------------------------------

PROMPT = "cpp-builder> "

def print_help():
    print("""
Available commands:
  help
      Show this help.

  targets
      List known targets and their registered compilers.

  show <target>
      Show details for a specific target.

  use <target>
      Set the 'current' target (useful for shorthand compile).

  register <target> <compiler_cmd>
      Register a compiler command or full path for a target.
      Example: register windows-x86_64 C:\\toolchains\\mingw\\bin\\g++.exe
      Example (unix): register linux-aarch64 aarch64-linux-gnu-g++

  unregister <target>
      Remove registered compiler for target (falls back to heuristics).

  fetch-winlibs
      (Windows host) Attempt to download a portable WinLibs (mingw-w64) into ./toolchains/winlibs
      After fetching, you can register the compiler path.

  compile <source> [--targets t1,t2] [-o outname] [--flags "<flags>"]
      Compile the source file for one or more targets. If --targets omitted uses current target or 'host'.

  build-matrix <source> --targets t1,t2,t3 [-o prefix] [--flags "<flags>"]
      Compile the source for multiple targets, producing distinct outputs.

  exit
      Quit the CLI.
""")

def repl():
    current_target = "host"
    print("C++ Builder CLI — interactive mode. Type 'help' for commands.")
    while True:
        try:
            line = input(PROMPT)
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if not line.strip():
            continue
        parts = shlex.split(line)
        if not parts:
            continue
        cmd = parts[0].lower()
        args = parts[1:]
        if cmd == "help":
            print_help()
        elif cmd == "targets":
            rows = REG.list_targets()
            for name, compiler, triple, notes in rows:
                print(f"- {name}: compiler={compiler} triple={triple} note={notes}")
        elif cmd == "show":
            if not args:
                print("Usage: show <target>")
                continue
            info = REG.show(args[0])
            if not info:
                print("Target not known.")
            else:
                print(info)
        elif cmd == "use":
            if not args:
                print("Usage: use <target>")
                continue
            if args[0] not in REG.targets:
                print("Unknown target", args[0])
                continue
            current_target = args[0]
            print("Current target set to", current_target)
        elif cmd == "register":
            if len(args) < 2:
                print("Usage: register <target> <compiler_cmd>")
                continue
            target = args[0]
            comp = " ".join(args[1:])
            REG.register(target, comp)
            print(f"Registered compiler for {target}: {comp}")
        elif cmd == "unregister":
            if not args:
                print("Usage: unregister <target>")
                continue
            REG.unregister(args[0])
            print("Unregistered", args[0])
        elif cmd == "fetch-winlibs":
            # only attempt on non-windows hosts if user insists? We'll allow it but warn
            dest = TOOLCHAINS_DIR / "winlibs"
            try:
                print("[*] Attempting to download/extract winlibs to", dest)
                binp = download_and_extract_winlibs(dest)
                if binp:
                    print("[+] Extracted winlibs bin at:", binp)
                    print("Tip: register windows-x86_64", str(Path(binp) / "g++.exe"))
                else:
                    print("[!] winlibs not available or extraction failed.")
            except Exception as e:
                print("[!] Error while fetching winlibs:", e)
        elif cmd == "compile":
            # parse options manually (simple)
            import argparse as _ap
            p = _ap.ArgumentParser(prog="compile", add_help=False)
            p.add_argument("source")
            p.add_argument("--targets", default=None)
            p.add_argument("-o", "--output", default=None)
            p.add_argument("--flags", default=None)
            try:
                ns = p.parse_args(args)
            except SystemExit:
                continue
            src = Path(ns.source)
            if not src.exists():
                print("Source not found:", ns.source)
                continue
            targets = [current_target] if not ns.targets else [t.strip() for t in ns.targets.split(",")]
            flags = shlex.split(ns.flags) if ns.flags else []
            for t in targets:
                ok = compile_for_target(src, t, output=ns.output, extra_flags=flags)
                if not ok:
                    print(f"[!] Compilation failed for {t}")
        elif cmd == "build-matrix":
            import argparse as _ap
            p = _ap.ArgumentParser(prog="build-matrix", add_help=False)
            p.add_argument("source")
            p.add_argument("--targets", required=True)
            p.add_argument("-o", "--output-prefix", default=None)
            p.add_argument("--flags", default=None)
            try:
                ns = p.parse_args(args)
            except SystemExit:
                continue
            src = Path(ns.source)
            if not src.exists():
                print("Source not found:", ns.source)
                continue
            targets = [t.strip() for t in ns.targets.split(",")]
            flags = shlex.split(ns.flags) if ns.flags else []
            prefix = ns.output_prefix
            for t in targets:
                outname = None
                if prefix:
                    outname = f"{prefix}_{t}"
                    if "windows" in t and not outname.lower().endswith(".exe"):
                        outname += ".exe"
                compile_for_target(src, t, output=outname, extra_flags=flags)
        elif cmd == "exit" or cmd == "quit":
            break
        else:
            print("Unknown command. Type 'help'.")

# --- CLI one-shot via argparse ----------------------------------------------

def handle_one_shot_compile(source: str, targets: List[str], output: Optional[str], flags: Optional[str]):
    src = Path(source)
    if not src.exists():
        print("[!] Source file not found:", source)
        return 2
    targets = targets or ["host"]
    flags_list = shlex.split(flags) if flags else []
    overall_success = True
    for t in targets:
        ok = compile_for_target(src, t, output=output, extra_flags=flags_list)
        overall_success = overall_success and ok
    return 0 if overall_success else 1

def main():
    ap = argparse.ArgumentParser(description="C++ builder CLI with cross-compilation support")
    ap.add_argument("-c", "--command", help="Run single command and exit (e.g. 'compile src.cpp --targets windows-x86_64,host')")
    ap.add_argument("--compile", nargs="+", help="One-shot compile: provide source and optional flags. Example: --compile hello.cpp --targets windows-x86_64,host --output hello")
    ap.add_argument("--targets", help="Comma separated targets for one-shot compile")
    ap.add_argument("-o", "--output", help="Output name for one-shot compile")
    ap.add_argument("--flags", help="Extra flags for compiler (quoted)")
    ap.add_argument("--repl", action="store_true", help="Start interactive CLI (default if nothing else specified)")
    args = ap.parse_args()

    if args.command:
        # naive execute: we only support the compile subcommand for simplicity
        # allow: -c "compile src.cpp --targets windows-x86_64,host -o out --flags \"-static\""
        parts = shlex.split(args.command)
        if parts and parts[0] == "compile":
            # forward to compile handler
            import argparse as _ap
            p = _ap.ArgumentParser(add_help=False)
            p.add_argument("compile")
            p.add_argument("source")
            p.add_argument("--targets", default=None)
            p.add_argument("-o", "--output", default=None)
            p.add_argument("--flags", default=None)
            try:
                ns = p.parse_args(parts)
            except SystemExit:
                print("Bad compile command")
                sys.exit(2)
            targets = [t.strip() for t in ns.targets.split(",")] if ns.targets else ["host"]
            sys.exit(handle_one_shot_compile(ns.source, targets, ns.output, ns.flags))
        else:
            print("Only 'compile' command supported via -c for now.")
            sys.exit(2)
    if args.compile:
        # one-shot usage: --compile src.cpp --targets t1,t2 -o name --flags "-static -s"
        src = args.compile[0]
        targets = [t.strip() for t in (args.targets.split(",") if args.targets else ["host"])]
        rc = handle_one_shot_compile(src, targets, args.output, args.flags)
        sys.exit(rc)

    # default: start REPL
    repl()

if __name__ == "__main__":
    main()
