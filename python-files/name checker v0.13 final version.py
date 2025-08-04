import subprocess
import sys
import os

# Auto-install missing packages
required = ["pandas", "openpyxl"]
for package in required:
    try:
        __import__(package)
    except ImportError:
        print(f"📦 Installing missing package: {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from tkinter import Tk, filedialog
import pandas as pd
import re
from collections import defaultdict
from itertools import combinations

# === Helper Functions ===

def get_unique_filename(base_name, ext=".xlsx"):
    filename = f"{base_name}{ext}"
    count = 1
    while os.path.exists(filename):
        filename = f"{base_name}_{count}{ext}"
        count += 1
    return filename

def normalize_word(w):
    w = w.lower()
    equivalents = {
        "lawyers": "law", "solicitors": "law", "sol": "law", "legal": "law",
        "ltd": "ltd", "limited": "ltd", "plc": "ltd"
    }
    return equivalents.get(w, w)

def split_by_space(text):
    return re.findall(r'\b\w+\b', text.lower())

def filter_words(words):
    return [w for w in words if len(w) > 1]

def clean_name(text, exclusion_words):
    words = filter_words(split_by_space(text))
    return ''.join(w for w in words if w not in exclusion_words)

def shares_word(a, b):
    wa = set(split_by_space(a))
    wb = set(split_by_space(b))
    return not wa.isdisjoint(wb)

def let_substrings(txt):
    substrings = set()
    for k in range(2, len(txt)+1):
        for i in range(len(txt)-k+1):
            substrings.add(txt[i:i+k])
    return substrings

def normalize_and_filter(words):
    return [normalize_word(w) for w in filter_words(words)]

def words_overlap_100(name1, name2):
    arr1 = normalize_and_filter(split_by_space(name1))
    arr2 = normalize_and_filter(split_by_space(name2))
    smaller, larger = (arr1, arr2) if len(arr1) <= len(arr2) else (arr2, arr1)
    return all(normalize_word(w) in larger for w in smaller)

def name_without_spaces(name):
    return ''.join(split_by_space(name))

def is_name_longer(n1, n2):
    c1, c2 = name_without_spaces(n1), name_without_spaces(n2)
    return len(c1) > len(c2) or (len(c1) == len(c2) and len(n1) > len(n2))

def single_letter_initials_match(short, long):
    if not is_name_longer(long, short):
        return False
    short_words = split_by_space(short)
    long_words = split_by_space(long)
    initials = [w for w in short_words if len(w) == 1]
    used = set()
    for ch in initials:
        matched = False
        for i, lw in enumerate(long_words):
            if i not in used and lw.startswith(ch):
                used.add(i)
                matched = True
                break
        if not matched:
            combined = ''.join(['and' if c == '&' else c for c in initials])
            return combined in long_words
    return True

# === Custom normalization ===

normalization_map = {
    "engineers": "engineer", "engineering": "engineer",
    "consultants": "consultant", "consulting": "consultant",
    "services": "service", "solutions": "solution",
    "limited": "ltd", "ltd": "ltd", "plc": "ltd"
}

def clean_and_normalize_words(name, exclusion_words=None):
    if exclusion_words is None:
        exclusion_words = set()
    words = split_by_space(name)
    result = []
    for word in words:
        w = word.lower()
        if w in exclusion_words:
            continue
        norm = normalization_map.get(w, w)
        if norm.endswith('s') and len(norm) > 3:
            norm = norm[:-1]
        result.append(norm)
    return result

def is_special_name(name):
    words = split_by_space(name)
    return any(w.startswith("other") for w in words) or name.lower().strip().endswith("others")

# === Main Processing Function ===

def process_file(file_path):
    print("📂 Loading file...")
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    if df.empty or df.shape[1] == 0:
        print("❌ No valid data found in the file.")
        return

    names = df.iloc[:, 0].dropna().astype(str).tolist()

    # Split names
    special_names = [n for n in names if is_special_name(n)]
    core_names = [n for n in names if not is_special_name(n)]

    print(f"🔍 Processing {len(core_names)} core names and {len(special_names)} special names...")

    # Top 80 words from core names
    word_counts = defaultdict(int)
    for name in core_names:
        words = filter_words(split_by_space(name))
        for word in words:
            word_counts[normalize_word(word)] += 1
    top_words = set(sorted(word_counts, key=word_counts.get, reverse=True)[:80])

    name_freq = defaultdict(int)
    for name in core_names:
        name_freq[name] += 1

    results = []
    seen = set()

    # === Original matching (core names only) ===
    for name1, name2 in combinations(core_names, 2):
        if name1 == name2:
            continue

        key = tuple(sorted((name1.lower(), name2.lower())))
        if key in seen:
            continue
        seen.add(key)

        count1, count2 = name_freq[name1], name_freq[name2]
        main_name, other_name = (name1, name2) if count1 > count2 or (
            count1 == count2 and len(name1) <= len(name2)) else (name2, name1)

        if not shares_word(main_name, other_name):
            continue

        if not words_overlap_100(main_name, other_name):
            continue

        if not single_letter_initials_match(main_name, other_name):
            continue

        clean_main = clean_name(main_name, top_words)
        clean_other = clean_name(other_name, top_words)

        if not clean_main or not clean_other:
            continue

        common_chars = sum(1 for ch in clean_other if ch in clean_main)
        wpct = common_chars / len(clean_main) if clean_main else 0

        subs_main = let_substrings(clean_main)
        subs_other = let_substrings(clean_other)
        common_subs = len(subs_main & subs_other)
        spct = common_subs / len(subs_main) if subs_main else 0

        if not (wpct == 1 and spct == 1) and (wpct > 0.5 and spct > 0.5):
            results.append([main_name, other_name])

    # === Second loop: Special names matched to core names or others ===
    special_pairs_added = 0
    for s_name in special_names:
        s_clean = ' '.join(clean_and_normalize_words(s_name, {"other", "others"}))
        for c_name in names:
            if s_name == c_name:
                continue

            key = tuple(sorted((s_name.lower(), c_name.lower())))
            if key in seen:
                continue

            c_clean = ' '.join(clean_and_normalize_words(c_name, {"other", "others"}))
            if len(s_clean) < 3 or len(c_clean) < 3:
                continue

            if s_clean in c_clean or c_clean in s_clean:
                results.append([s_name, c_name])
                seen.add(key)
                special_pairs_added += 1
                print(f"🟢 Added special pair: '{s_name}' <--> '{c_name}'")

    print(f"✅ Added {special_pairs_added} new pairs from special names.")

    # === Save output ===
    if results:
        filename = get_unique_filename("name_comparisons")
        df_output = pd.DataFrame(results, columns=["Main Name", "Similar Name"])
        df_output.to_excel(filename, index=False)
        print(f"✅ {len(results)} name pairs written to {filename}")
    else:
        print("❌ No name comparisons found.")

# === File Picker and Run ===

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Excel or CSV file with names",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
    )
    root.update()

    if file_path:
        print(f"📂 Selected file: {file_path}")
        process_file(file_path)
    else:
        print("⚠️ No file selected.")
