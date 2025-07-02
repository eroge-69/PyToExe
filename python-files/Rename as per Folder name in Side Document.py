import os
import sys
from datetime import datetime

# >>>>  1. CHANGE THIS TO THE FOLDER YOU WANT TO PROCESS  <<<<
root_dir = r"C:\Users\sravindra\Desktop\ScanFolder"

# ------------------------------------------------------------------
# You may leave everything below as‑is
# ------------------------------------------------------------------

issues = []          # collects folders / files that were NOT renamed
date_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

for dirpath, dirnames, filenames in os.walk(root_dir):
    folder_name = os.path.basename(dirpath)

    # If the folder is empty, note it and move on
    if not filenames:
        issues.append(
            {"Folder": folder_name, "File": "-", "Path": dirpath,
             "Reason": "Folder is empty"}
        )
        continue

    # Sort for predictable numbering
    filenames.sort()

    for index, filename in enumerate(filenames, start=1):
        file_path = os.path.join(dirpath, filename)
        ext       = os.path.splitext(filename)[1]
        new_name  = f"{folder_name}_{index}{ext}"
        new_path  = os.path.join(dirpath, new_name)

        # Skip if it already matches our pattern
        if file_path == new_path:
            issues.append(
                {"Folder": folder_name, "File": filename, "Path": file_path,
                 "Reason": "Already correctly named"}
            )
            continue

        # Try the rename and log any failure
        try:
            print(f"Renaming: {file_path}  ->  {new_path}")
            os.rename(file_path, new_path)

        except Exception as err:
            issues.append(
                {"Folder": folder_name, "File": filename, "Path": file_path,
                 "Reason": f"Failed: {err}"}
            )

# ------------------------------------------------------------------
# Write the report(s)
# ------------------------------------------------------------------
if issues:
    # 1) Plain‑text tab‑delimited
    txt_log = os.path.join(root_dir, f"rename_issues_{date_stamp}.txt")
    with open(txt_log, "w", encoding="utf‑8") as f:
        f.write("Folder\tFile\tPath\tReason\n")
        for row in issues:
            f.write(f"{row['Folder']}\t{row['File']}\t{row['Path']}\t{row['Reason']}\n")

    # 2) Excel (.xlsx) – if pandas & openpyxl are available
    try:
        import pandas as pd
        xls_log = os.path.join(root_dir, f"rename_issues_{date_stamp}.xlsx")
        pd.DataFrame(issues).to_excel(xls_log, index=False)
    except ImportError:
        xls_log = None
        print("⚠  pandas or openpyxl not installed – Excel report skipped.", file=sys.stderr)

    print("\nFinished with some issues.")
    print(f"Text report : {txt_log}")
    if xls_log:
        print(f"Excel report: {xls_log}")

else:
    print("\n✅ All files renamed successfully – no issues to report.")