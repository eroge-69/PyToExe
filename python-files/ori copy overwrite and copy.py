import os
import re
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import islice
from tqdm import tqdm

# CONFIG
source_folder = r"\\192.168.1.201\ORI-Storage"
six_digit_txt_name = r"C:\Users\souser02\Desktop\PYTHON\copy 6 digit code.txt"
destination_folder = r"E:\BASTI_ORI"

# MATCHING POLICY
match_mode = "any"       # "any", "all", "at_least_n"
min_matches = 2          # used only if match_mode == "at_least_n"

# PERFORMANCE
MAX_WORKERS = 8
READ_BUF_SIZE = 8 * 1024 * 1024
BATCH_SIZE = 6000

os.makedirs(destination_folder, exist_ok=True)

# Regex
token_txt_re = re.compile(r'\b\d{6}\b')  # exact 6-digit codes in notepad
token_name_re = re.compile(r'\d{6}')     # any 6-digit sequence in filenames


def read_codes(txt_path):
    codes = set()
    try:
        with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                codes.update(token_txt_re.findall(line))
    except Exception as e:
        print(f"Failed to read codes from {txt_path}: {e}")
    return codes


def fast_copy_to_unique_name(src, dst_dir, base_name):
    start = time.perf_counter()
    base, ext = os.path.splitext(base_name)
    dst_path = os.path.join(dst_dir, base_name)

    if os.path.exists(dst_path):
        try:
            src_size = os.path.getsize(src)
            dst_size = os.path.getsize(dst_path)

            if src_size == dst_size:
                # Skip if same name + same size
                return dst_path, None
            else:
                # If size differs, create a new unique name
                idx = 2
                while True:
                    cand_name = f"{base} ({idx}){ext}"
                    cand_path = os.path.join(dst_dir, cand_name)
                    if not os.path.exists(cand_path):
                        dst_path = cand_path
                        break
                    idx += 1
        except Exception:
            # If size check fails, fallback to unique name
            idx = 2
            while True:
                cand_name = f"{base} ({idx}){ext}"
                cand_path = os.path.join(dst_dir, cand_name)
                if not os.path.exists(cand_path):
                    dst_path = cand_path
                    break
                idx += 1

    # Copy file
    with open(src, 'rb', buffering=READ_BUF_SIZE) as fsrc, open(dst_path, 'wb', buffering=READ_BUF_SIZE) as fdst:
        shutil.copyfileobj(fsrc, fdst, length=READ_BUF_SIZE)

    try:
        shutil.copystat(src, dst_path, follow_symlinks=True)
    except Exception:
        pass

    end = time.perf_counter()
    return dst_path, (end - start)


def iter_files(root):
    stack = [root]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for entry in it:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            yield entry
                    except OSError:
                        continue
        except (PermissionError, FileNotFoundError):
            continue


def filename_tokens(name):
    return token_name_re.findall(name)


def file_matches(name, code_set):
    tokens = filename_tokens(name)
    if not tokens:
        return False
    if match_mode == "any":
        return any(t in code_set for t in tokens)
    elif match_mode == "all":
        return all(t in code_set for t in tokens)
    elif match_mode == "at_least_n":
        hits = sum(1 for t in tokens if t in code_set)
        return hits >= min_matches
    else:
        return any(t in code_set for t in tokens)


def copy_if_match_flat(entry, code_set, six_txt_basename):
    name = entry.name
    # Skip the notepad file itself if it happens to be under the source tree
    if name.lower() == six_txt_basename.lower():
        return 1, 0, None
    if not file_matches(name, code_set):
        return 1, 0, None
    try:
        _, dur = fast_copy_to_unique_name(entry.path, destination_folder, name)
        if dur is None:
            # skipped (same name + same size)
            return 1, 0, None
        return 1, 1, dur
    except Exception:
        return 1, 0, None


def batched(iterable, n):
    it = iter(iterable)
    while True:
        batch = list(islice(it, n))
        if not batch:
            break
        yield batch


def main():
    codes = read_codes(six_digit_txt_name)
    if not codes:
        print("No valid 6-digit codes found in the notepad file.")
        return

    six_txt_basename = os.path.basename(six_digit_txt_name)

    total_scanned = 0
    total_copied = 0
    copy_times = []

    entries = iter_files(source_folder)
    overall_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for batch in batched(entries, BATCH_SIZE):
            futures = [executor.submit(copy_if_match_flat, e, codes, six_txt_basename) for e in batch]
            scanned_in_batch = 0
            copied_in_batch = 0
            with tqdm(total=len(futures), desc="Batch progress", unit="file", leave=False) as pbar:
                for fut in as_completed(futures):
                    scanned, copied, dur = fut.result()
                    scanned_in_batch += scanned
                    copied_in_batch += copied
                    if dur is not None:
                        copy_times.append(dur)
                    pbar.update(1)
            total_scanned += scanned_in_batch
            total_copied += copied_in_batch
            tqdm.write(f"Cumulative scanned: {total_scanned:,} | copied: {total_copied:,}")

    overall_end = time.perf_counter()
    total_elapsed = overall_end - overall_start

    if copy_times:
        avg_time = sum(copy_times) / len(copy_times)
        min_time = min(copy_times)
        max_time = max(copy_times)
    else:
        avg_time = min_time = max_time = 0.0

    print("\n=== Summary ===")
    print(f"Match mode: {match_mode}" + (f" (min_matches={min_matches})" if match_mode == "at_least_n" else ""))
    print(f"Total files scanned (all subfolders): {total_scanned:,}")
    print(f"Total files copied (flat, duplicates kept if size differs): {total_copied:,}")
    print(f"Total elapsed time: {total_elapsed:.2f}s")
    print(f"Per-file copy time: avg {avg_time:.4f}s | min {min_time:.4f}s | max {max_time:.4f}s")
    print(f"THANKS FOR USING VISHAL SINGH CODE")


if __name__ == "__main__":
    main()
