import os
import re
import shutil
import sys
import calendar
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

def compile_patterns():
    month_abbr = "(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    month_full = ("(January|February|March|April|May|June|July|August|"
                  "September|October|November|December)")
    patterns = [
        r"(?P<Y>\d{4})(?P<M>\d{2})(?P<D>\d{2})",  # YYYYMMDD
        r"(?P<Y>\d{4})[-_](?P<M>\d{2})[-_](?P<D>\d{2})",  # YYYY-MM-DD, YYYY_MM_DD
        r"(?P<D>\d{2})[-_](?P<M>\d{2})[-_](?P<Y>\d{4})",  # DD-MM-YYYY, DD_MM_YYYY
        r"(?P<M>\d{2})[-_](?P<D>\d{2})[-_](?P<Y>\d{4})",  # MM-DD-YYYY, MM_DD_YYYY
        r"(?P<Y>\d{4})" + month_abbr + r"(?P<D>\d{2})",   # YYYYMMMDD
        r"(?P<Y>\d{4})[-_]" + month_abbr + r"[-_](?P<D>\d{2})",  # YYYY-MMM-DD, YYYY_MMM_DD
        r"(?P<Y>\d{4})" + month_full + r"(?P<D>\d{2})",    # YYYYMMMMDD
        r"(?P<Y>\d{4})[-_]" + month_full + r"[-_](?P<D>\d{2})",  # YYYY-MMMM-DD, YYYY_MMMM_DD
    ]
    return [re.compile(p, re.IGNORECASE) for p in patterns]

DATE_PATTERNS = compile_patterns()
MONTHS_ABBR = list(calendar.month_abbr)[1:]
ABBR2NUM = {m.lower(): i for i, m in enumerate(MONTHS_ABBR, 1)}
FULL2NUM = {m.lower(): i for i, m in enumerate(calendar.month_name[1:], 1)}

def ask(prompt: str, valid=None):
    while True:
        val = input(prompt).strip()
        if not valid or val.lower() in valid:
            return val.lower()
        print(f"Please enter one of: {', '.join(valid)}.")

def get_dir(prompt: str) -> Path:
    while True:
        p = Path(input(prompt).strip(' "\'')).expanduser()
        if p.exists():
            return p
        try:
            p.mkdir(parents=True, exist_ok=True)
            return p
        except Exception as e:
            print(f"❌ {e}")

def ask_year(prev_year=None) -> int:
    this_year = datetime.now().year
    while True:
        default = f" ({this_year})" if prev_year is None else f" ({prev_year})"
        y = input(f"\nEnter year for folder creation eg.,{default}: ").strip()
        if not y:
            y = prev_year if prev_year and str(prev_year).isdigit() else str(this_year)
        if y.isdigit() and 1900 <= int(y) <= 2100:
            return int(y)
        print("Please enter a valid 4-digit year (e.g., 2025).")

def month_folder(num: int, year: int) -> str:
    return f"({num:02d}){MONTHS_ABBR[num-1]}-{year}"

def ensure_month_folders(base: Path, year: int) -> List[str]:
    folders = []
    for i in range(1, 13):
        folder = base / month_folder(i, year)
        folder.mkdir(parents=True, exist_ok=True)
        folders.append(str(folder))
    return folders

def rename_month_folders(base: Path, old_year: int, new_year: int):
    for i in range(1, 13):
        old_name = month_folder(i, old_year)
        new_name = month_folder(i, new_year)
        old_path = base / old_name
        new_path = base / new_name
        if old_path.exists() and old_path.is_dir():
            if new_path.exists():
                continue  # Already renamed
            old_path.rename(new_path)

def parse(name: str, year: int) -> Optional[datetime]:
    for rx in DATE_PATTERNS:
        m = rx.search(name)
        if not m:
            continue
        gd = m.groupdict()
        if not ("Y" in gd and "D" in gd):
            continue
        y = int(gd["Y"])
        d = int(gd["D"])
        mon = None
        if "M" in gd and gd["M"]:
            try: mon = int(gd["M"])
            except: continue
        elif "Ma" in gd and gd.get("Ma"):
            mon = ABBR2NUM.get(gd["Ma"].lower())
        elif "Mf" in gd and gd.get("Mf"):
            mon = FULL2NUM.get(gd["Mf"].lower())
        if not mon:
            continue
        try:
            dt = datetime(y, mon, d)
            if dt.year == year:
                return dt
        except Exception:
            continue
    return None

def scan_all_files(src: Path, year: int) -> List[Tuple[Path, datetime]]:
    # All files at all folder levels
    dated = []
    for root, dirs, files in os.walk(src):
        for f in files:
            fpath = Path(root) / f
            dt = parse(f, year)
            if dt:
                dated.append((fpath, dt))
    return dated

def append_suffix(fp: Path, dt: datetime) -> Path:
    suffix = f"-{dt.strftime('%Y%m%d')}"
    if suffix not in fp.stem:
        new = fp.with_stem(fp.stem + suffix)
        try:
            fp.rename(new)
        except Exception:
            # If already exists, try with counts
            new = fp.with_stem(fp.stem + suffix + "_1")
            cnt = 2
            while new.exists():
                new = fp.with_stem(fp.stem + suffix + f"_{cnt}")
                cnt += 1
            fp.rename(new)
        return new
    return fp

def print_file_table(filelist, title="Matched files", start=0, end=50):
    from prettytable import PrettyTable
    tbl = PrettyTable()
    tbl.field_names = ["Title", "Date", "Directory Path"]
    for f, dt in filelist[start:end]:
        tbl.add_row([f.name, dt.strftime("%Y-%m-%d"), str(f.parent)])
    print(f'\n{title} (showing rows {start+1} to {min(len(filelist), end)} of {len(filelist)})')
    print(tbl)

def print_operation_table(fileops):
    from prettytable import PrettyTable
    tbl = PrettyTable()
    tbl.field_names = ["Original Name", "Suffix to Add", "Date", "Original Directory", "New Directory"]
    for orig, dt, srcdir, tardir in fileops:
        suffix = "-" + dt.strftime("%Y%m%d")
        tbl.add_row([orig, suffix, dt.strftime("%Y-%m-%d"), srcdir, tardir])
    print("\nPlanned Operations:")
    print(tbl)

def process_all(files: List[Tuple[Path, datetime]], dest: Path, year: int, op: str) -> List[Tuple[str, datetime, str, str]]:
    ensure_month_folders(dest, year)
    ops_record = []
    for src, dt in files:
        pre_rename_path = src
        # append suffix to file name in source first
        temp_file = append_suffix(src, dt)
        # Prepare target directory (month folder)
        month_dir = dest / month_folder(dt.month, year)
        target = month_dir / temp_file.name
        c = 1
        while target.exists():
            target = month_dir / f"{target.stem}_{c}{target.suffix}"
            c += 1
        if op == "move":
            shutil.move(str(temp_file), target)
        else:
            shutil.copy2(str(temp_file), target)
        ops_record.append((pre_rename_path.name, dt, pre_rename_path.parent, month_dir))
    return ops_record

def main():
    from prettytable import PrettyTable

    print("=== Monthly Folder Manager + File Sorter (Year-select version) ===")
    base = get_dir("Base directory for 'All Month'-'Entered Year' folders: ")

    # Loop to allow sorting more files at end
    first_run = True
    prev_year = None
    while True:
        # Ask year, create/display folders
        year = ask_year(prev_year)
        folders = ensure_month_folders(base, year)
        print("\nCreated/verified these Month-Year folders:")
        for f in folders:
            print("    - " + f)
        print("Folders ready.")

        # Ask for directory to scan recursively
        src = get_dir("\nDirectory to scan recursively: ")
        # show files table
        dated_files = scan_all_files(src, year)
        if not dated_files:
            print(f"\nNo files found in {src} matching year {year}.")
            # Option to retry a different year, rename folders if needed
            retry = ask("Try with a different year? [y/n]: ", ['y', 'n'])
            if retry == "y":
                new_year = ask_year()
                if new_year != year:
                    rename_month_folders(base, year, new_year)
                    prev_year = new_year
                continue
            else:
                print("\nNo matching files found. Exiting.")
                return

        # File table (up to 50 rows); option to show more
        show_rows = 50
        print_file_table(dated_files, "Matched files", 0, show_rows)
        if len(dated_files) > show_rows:
            see_all = ask(f"\nThere are {len(dated_files)} files. See all? [y/n]: ", ['y', 'n'])
            if see_all == "y":
                print_file_table(dated_files, "All matched files", 0, len(dated_files))

        # File Operation Choice: move / copy
        op = ""
        while op not in ("move", "copy"):
            print("\nFILE OPERATION CHOICE:")
            print("  MOVE = Cut files from source (saves space, files disappear from source folder)")
            print("  COPY = Copy files to destination (uses more space, keeps originals)")
            op = input("Do you want to MOVE or COPY files? [move/copy]: ").strip().lower()

        # Destination
        if ask("\nSort to A) base dir or B) another dir? [a/b]: ", ["a", "b"]) == "a":
            target = base
        else:
            target = get_dir("Destination directory: ")

        # Show file operations in tabular format (original, suffix, date, paths)
        fileops = []
        for f, dt in dated_files:
            month_dir = target / month_folder(dt.month, year)
            suffix = "-" + dt.strftime("%Y%m%d")
            fileops.append((f.name, dt, str(f.parent), str(month_dir)))
        show_ops = min(50, len(fileops))
        print_operation_table(fileops[:show_ops])
        if len(fileops) > show_ops:
            see_all_ops = ask(f"\nShow all {len(fileops)} planned file operations? [y/n]: ", ["y","n"])
            if see_all_ops == "y":
                print_operation_table(fileops)

        proceed = ask("\nProceed with file operation? [y/n]: ", ['y', 'n'])
        if proceed == "y":
            operations = process_all(dated_files, target, year, op)
            print(f"\n✅ {len(operations)} files {'moved' if op=='move' else 'copied'} successfully!")
        else:
            print("Operation canceled.")

        # Repeat option
        more = ask("\nDo you want to sort more files? [y/n]: ", ["y", "n"])
        if more == "y":
            prev_year = year
            continue
        else:
            print("\n🌟 All done! Your folders and files are now beautifully organized. Have an awesome day! 🌟")
            break

if __name__ == "__main__":
    try:
        # Ensure "prettytable" package is installed
        try:
            import prettytable
        except ImportError:
            print("\nInstalling 'prettytable' for better tables. Please wait...")
            os.system(f"{sys.executable} -m pip install prettytable")
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)
