import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

# Extensions considered "media" for metadata updates
MEDIA_EXTS = {
    ".arw", ".jpg", ".jpeg", ".png", ".tif", ".tiff",
    ".heic", ".heif", ".dng", ".cr2", ".cr3", ".nef",
    ".orf", ".rw2", ".raf", ".srw", ".psd"
}

def norm(s: str) -> str:
    """normalize strings for matching: lowercase + alphanum only"""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def join_and_norm(values):
    return norm("".join(v or "" for v in values))

def scan_media(folder: Path, recursive: bool):
    if recursive:
        it = folder.rglob("*")
    else:
        it = folder.glob("*")
    for p in it:
        if p.is_file() and p.suffix.lower() in MEDIA_EXTS:
            yield p

def run_exiftool_set_copyright(file_path: Path, value: str, exiftool_path: str, dry_run: bool):
    """
    Sets multiple tags for broad compatibility:
      - EXIF:Copyright
      - IPTC:CopyrightNotice
      - XMP-dc:Rights
    Returns (ok: bool, msg: str)
    """
    if dry_run:
        return True, "dry-run (no changes)"

    cmd = [
        exiftool_path,
        "-overwrite_original",
        f"-Copyright={value}",
        f"-IPTC:CopyrightNotice={value}",
        f"-XMP-dc:Rights={value}",
        str(file_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, shell=False)
        if res.returncode == 0:
            return True, "updated"
        else:
            err = (res.stderr or res.stdout or "").strip()
            return False, f"exiftool error: {err}"
    except FileNotFoundError:
        return False, "exiftool not found"
    except Exception as e:
        return False, f"exiftool exception: {e}"

def main():
    ap = argparse.ArgumentParser(
        description="Match athlete names from a roster CSV to filenames and set copyright via exiftool."
    )
    ap.add_argument("images_folder", help="Folder containing images to update")
    ap.add_argument("roster_csv", help="Input roster CSV (e.g., with FirstName,LastName,Copyright)")
    ap.add_argument("-o", "--output_roster_csv", default="roster_with_matches.csv",
                    help="Augmented roster CSV output (default: roster_with_matches.csv)")
    ap.add_argument("--per_file_log_csv", default="file_update_log.csv",
                    help="Detailed per-file update log CSV (default: file_update_log.csv)")
    ap.add_argument("-r", "--recursive", action="store_true", help="Recurse into subfolders")
    ap.add_argument("--name-columns", default="FirstName,LastName",
                    help="Comma-separated roster column names to build the match key (default: FirstName,LastName)")
    ap.add_argument("--value-column", default="Copyright",
                    help="Roster column containing the copyright value to write (default: Copyright)")
    ap.add_argument("--static-value", default=None,
                    help="If provided, use this static value instead of a roster column")
    ap.add_argument("--exiftool-path", default="exiftool",
                    help='Path to exiftool executable (default: "exiftool" on PATH)')
    ap.add_argument("--dry-run", action="store_true",
                    help="Plan updates but make no file changes")
    ap.add_argument("--relative-paths", action="store_true",
                    help="Write relative paths in logs (relative to images_folder)")
    args = ap.parse_args()

    images_root = Path(args.images_folder).expanduser().resolve(strict=True)
    roster_path = Path(args.roster_csv).expanduser().resolve(strict=True)
    out_roster = Path(args.output_roster_csv).expanduser().resolve()
    per_file_log = Path(args.per_file_log_csv).expanduser().resolve()

    # Build an index of images by normalized filename
    images = list(scan_media(images_root, args.recursive))
    image_index = []  # (norm_key, path)
    for p in images:
        norm_name = norm(p.stem)  # use filename without extension
        image_index.append((norm_name, p))

    # Read roster
    with open(roster_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit("Roster CSV has no header.")
        headers = reader.fieldnames
        rows = [row for row in reader]

    name_cols = [c.strip() for c in args.name_columns.split(",") if c.strip()]
    for c in name_cols:
        if c not in headers:
            raise SystemExit(f"Roster missing required name column: {c}")

    if args.static_value is None and args.value_column not in headers:
        raise SystemExit(
            f"Roster missing value column '{args.value_column}'. "
            "Use --static-value to override."
        )

    # Prepare outputs
    per_file_records = []
    augmented_headers = list(headers)
    for addcol in ["matched_files", "updated_count", "notes"]:
        if addcol not in augmented_headers:
            augmented_headers.append(addcol)

    total_attempts = 0
    total_success = 0

    for row in rows:
        # Build the athlete key (e.g., "FirstName"+"LastName")
        name_key = join_and_norm([row.get(c, "") for c in name_cols])

        # Determine value to write
        value_to_write = args.static_value if args.static_value is not None else (row.get(args.value_column, "") or "").strip()

        matched_paths = []
        # Simple substring rule: if athlete key appears within normalized filename
        for norm_name, path in image_index:
            if name_key and name_key in norm_name:
                matched_paths.append(path)

        updated_count = 0
        row_notes = []
        for p in matched_paths:
            file_disp = str(p.relative_to(images_root) if args.relative_paths else p)
            if value_to_write:
                ok, msg = run_exiftool_set_copyright(
                    file_path=p,
                    value=value_to_write,
                    exiftool_path=args.exiftool_path,
                    dry_run=args.dry_run
                )
                total_attempts += 1
                if ok and not args.dry_run:
                    updated_count += 1
                elif ok and args.dry_run:
                    # treat as planned
                    pass
                else:
                    row_notes.append(f"{file_disp}: {msg}")
                per_file_records.append({
                    "athlete_key": name_key,
                    "roster_row": "; ".join(f"{c}={row.get(c,'')}" for c in name_cols),
                    "file": file_disp,
                    "value_written": value_to_write,
                    "status": msg if not ok else ("planned" if args.dry_run else "updated")
                })
                if ok and not args.dry_run:
                    total_success += 1
            else:
                msg = "no value to write"
                row_notes.append(f"{file_disp}: {msg}")
                per_file_records.append({
                    "athlete_key": name_key,
                    "roster_row": "; ".join(f"{c}={row.get(c,'')}" for c in name_cols),
                    "file": file_disp,
                    "value_written": "",
                    "status": msg
                })

        row["matched_files"] = "; ".join(str(p.relative_to(images_root) if args.relative_paths else p) for p in matched_paths)
        row["updated_count"] = str(updated_count)
        row["notes"] = " | ".join(row_notes)

    # Write augmented roster
    with open(out_roster, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=augmented_headers)
        w.writeheader()
        w.writerows(rows)

    # Write per-file log
    if per_file_records:
        pf_headers = ["athlete_key", "roster_row", "file", "value_written", "status"]
        with open(per_file_log, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=pf_headers)
            w.writeheader()
            w.writerows(per_file_records)

    summary = (
        f"Processed {len(rows)} roster row(s); "
        f"scanned {len(images)} file(s). "
        f"Exif updates attempted: {total_attempts}"
    )
    if args.dry_run:
        summary += " (dry-run)."
    else:
        summary += f"; successful: {total_success}."
    print(summary)
    print(f"Wrote augmented roster: {out_roster}")
    print(f"Wrote per-file log: {per_file_log}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
