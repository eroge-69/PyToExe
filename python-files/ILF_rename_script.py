import os
import re

# ── Chapter keywords and their sorting prefixes ──
chapter_prefix_map = {
    "a_": ["forward", "foreword", "fwd"],
    "b_": ["intro", "title", "cover"],
    "c_": ["contents", "toc", "index"],
    "d_": ["package", "pkg", "overview"],
    "e_": ["start", "startup"],
    "f_": ["fuel", "fuel_sys"],
    "g_": ["gov"],
    "h_": ["electrical", "elec", "power"],
    "i_": ["lube", "lube_", "oil", "lubrication"],
    "j_": ["encl", "anc", "housing"],
    "k_": ["turbine", "engine", "eng"],
    "l_": ["reduction", "gear", "rg"],
    "m_": ["drvn", "comp", "gen", "de"],
    "n_": ["accessories", "acc", "accs"],
    "o_": ["seal"],
    "p_": ["a"],
    "q_": ["b"],
    "r_": ["c"],
    "s_": ["d"],
    "y_": ["asc"],
    "z_": []  # fallback for unmatched
}

# ── Title page prefix map (midpoint sections) ──
section_titles = {
    "st1.doc": "cd_",  "st2.doc": "de_",  "st3.doc": "ef_",  "st4.doc": "fg_",
    "st5.doc": "gh_",  "st6.doc": "hi_",  "st7.doc": "ij_",  "st8.doc": "jk_",
    "st9.doc": "kl_",  "st10.doc": "mn_", "st11.doc": "no_", "sta.doc": "op_",
    "stb.doc": "pq_",  "stc.doc": "qr_",  "std.doc": "rs_"
}

# ── Detect chapter prefix based on keywords ──
def detect_chapter_prefix(filename):
    lowered = filename.lower()
    for prefix, keywords in chapter_prefix_map.items():
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b|_' + re.escape(keyword) + r'_|-' + re.escape(keyword) + r'-'
            if re.search(pattern, lowered) and not lowered.startswith(prefix):
                return prefix
    return "z_"  # fallback for unmatched

# ── Rename folders and files ──
def rename_files_and_folders(root_dir):
    # Step 1: Rename folders (.boo → .ilboo)
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for dirname in dirnames:
            if dirname.endswith('.boo'):
                old_folder = os.path.join(dirpath, dirname)
                new_folder = os.path.join(dirpath, dirname[:-4] + '.ilboo')
                os.rename(old_folder, new_folder)
                print(f"Renamed folder: {old_folder} → {new_folder}")

    # Step 2: Rename files
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)
            new_name = None

            # Title pages with midpoint prefixes
            if filename in section_titles:
                prefix = section_titles[filename]
                new_name = prefix + filename[:-4] + '.ildoc'  # remove .doc

            # Standard IPL .doc files
            elif filename.endswith('.doc'):
                prefix = detect_chapter_prefix(filename)
                new_name = prefix + filename[:-4] + '.ildoc'

            elif filename.endswith('.ildoc'):
                prefix = detect_chapter_prefix(filename)
                new_name = prefix + filename[:-6] + '.ildoc'

            # Other file types
            elif filename.endswith('.boo'):
                new_name = filename[:-4] + '.ilboo'
            elif filename.endswith('.fdr'):
                new_name = filename[:-4] + '.ilfdr'
            elif filename.endswith('.cab'):
                new_name = filename[:-4] + '.ilcab'
            elif filename.endswith('.drw'):
                new_name = filename[:-4] + '.ildrw'
            else:
                continue  # Skip unrelated file types

            new_path = os.path.join(dirpath, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} → {new_path}")

# ── Example usage ──
# ── Prompt user for path ──
if __name__ == "__main__":
    user_path = input("Enter the root directory path for renaming: ").strip()
    if os.path.isdir(user_path):
        rename_files_and_folders(user_path)
    else:
        print(f"Invalid path: '{user_path}' does not exist or is not a directory.")

