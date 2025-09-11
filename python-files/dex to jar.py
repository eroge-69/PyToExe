#!/usr/bin/env python3
"""
mini_decompile.py

A small orchestrator to decompile APK/DEX files using external tools:
 - jadx (recommended for Java source)
 - baksmali (for smali)
 - dex2jar (optional)

Place tool executables/jars under ./tools/ or ensure they are in PATH.

Usage examples:
  python3 mini_decompile.py -i myapp.apk -o outdir
  python3 mini_decompile.py -i classes.dex -o outdir --smali-only
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")

def find_tool(name, jar_name=None):
    # First check PATH
    p = shutil.which(name)
    if p:
        return p
    # Then check tools dir for executable or jar
    if jar_name:
        candidate = os.path.join(TOOLS_DIR, jar_name)
        if os.path.exists(candidate):
            return candidate
    candidate_exec = os.path.join(TOOLS_DIR, name)
    if os.path.exists(candidate_exec):
        return candidate_exec
    return None

def extract_dex_from_apk(apk_path, tmpdir):
    dex_files = []
    with zipfile.ZipFile(apk_path, 'r') as z:
        for name in z.namelist():
            if name.endswith('.dex'):
                out = os.path.join(tmpdir, os.path.basename(name))
                with open(out, 'wb') as f:
                    f.write(z.read(name))
                dex_files.append(out)
    return dex_files

def run_jadx(input_path, out_dir, jadx_bin):
    # Support both CLI executable or jar.
    if jadx_bin.endswith('.jar'):
        cmd = ['java', '-jar', jadx_bin, '-d', out_dir, input_path]
    else:
        cmd = [jadx_bin, '-d', out_dir, input_path]
    print("Running jadx:", " ".join(cmd))
    subprocess.check_call(cmd)

def run_baksmali(dex_path, out_dir, baksmali_jar):
    os.makedirs(out_dir, exist_ok=True)
    cmd = ['java', '-jar', baksmali_jar, 'd', dex_path, '-o', out_dir]
    print("Running baksmali:", " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    p = argparse.ArgumentParser(description="Mini DEX/APK decompiler orchestrator")
    p.add_argument('-i', '--input', required=True, help='APK or DEX file')
    p.add_argument('-o', '--out', required=True, help='output directory')
    p.add_argument('--smali-only', action='store_true', help='only produce smali')
    p.add_argument('--java-only', action='store_true', help='only produce Java (jadx)')
    p.add_argument('--keep-temp', action='store_true', help='don\'t delete temporary extracted files')
    args = p.parse_args()

    inp = os.path.abspath(args.input)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)

    jadx = find_tool('jadx', jar_name='jadx.jar')
    baksmali = find_tool('baksmali', jar_name='baksmali.jar')

    if not jadx and not args.smali_only:
        print("Warning: jadx not found. Java decompilation will be skipped unless --smali-only is set.")
    if not baksmali and not args.java_only:
        print("Warning: baksmali.jar not found. Smali output will be skipped unless --java-only is set.")

    tmp = tempfile.mkdtemp(prefix='mini_decomp_')
    dex_files = []

    try:
        if zipfile.is_zipfile(inp) or inp.lower().endswith('.apk'):
            print("Input looks like an APK / zip. Extracting DEX files...")
            dlist = extract_dex_from_apk(inp, tmp)
            if not dlist:
                print("No .dex files found inside the APK. Exiting.")
                return
            dex_files = dlist
        elif inp.lower().endswith('.dex'):
            dex_files = [inp]
        else:
            # try to handle raw input by extension fallback
            print("Input not recognized as .apk or .dex; attempting as .dex")
            dex_files = [inp]

        for i, dex in enumerate(dex_files):
            base_name = os.path.splitext(os.path.basename(dex))[0]
            if not args.smali_only and jadx:
                dest_j = os.path.join(out, f'jadx_{base_name}')
                os.makedirs(dest_j, exist_ok=True)
                try:
                    run_jadx(dex, dest_j, jadx)
                except subprocess.CalledProcessError as e:
                    print("jadx failed for", dex, e)
            if not args.java_only and baksmali:
                dest_s = os.path.join(out, f'smali_{base_name}')
                os.makedirs(dest_s, exist_ok=True)
                try:
                    run_baksmali(dex, dest_s, baksmali)
                except subprocess.CalledProcessError as e:
                    print("baksmali failed for", dex, e)

        print("Done. Outputs in:", out)
    finally:
        if args.keep_temp:
            print("Temporary files kept at:", tmp)
        else:
            try:
                shutil.rmtree(tmp)
            except Exception:
                pass

if __name__ == '__main__':
    main()
