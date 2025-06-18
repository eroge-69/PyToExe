import pandas as pd
import re
from rapidfuzz import process, fuzz
from tkinter import filedialog, Tk

# --- Extract uppercase letters and digits only ---
def extract_caps_digits(s):
    return ''.join(re.findall(r'[A-Z0-9]', str(s)))

# --- Main Matching Function ---
def match_columns():
    # Hide the main Tkinter window
    root = Tk()
    root.withdraw()

    # File dialogs for input/output
    SHEET1_PATH = filedialog.askopenfilename(title="Select Excel file for Sheet1")
    SHEET2_PATH = filedialog.askopenfilename(title="Select Excel file for Sheet2")
    OUTPUT_PATH = filedialog.asksaveasfilename(title="Save matched output as", defaultextension=".xlsx")

    SHEET1_NAME = "Sheet1"
    SHEET2_NAME = "Sheet2"
    SIMILARITY_THRESHOLD = 80  # percent

    # Load Excel data
    df1 = pd.read_excel(SHEET1_PATH, sheet_name=SHEET1_NAME)
    df2 = pd.read_excel(SHEET2_PATH, sheet_name=SHEET2_NAME)

    col1 = df1.iloc[:, 0].astype(str).tolist()
    col2 = df2.iloc[:, 0].astype(str).tolist()

    # Pre-process: extract capital+digit versions
    col1_proc = [(original, extract_caps_digits(original)) for original in col1]
    col2_proc = [(original, extract_caps_digits(original)) for original in col2]

    choices_proc = [proc for _, proc in col2_proc]
    orig_lookup = {proc: orig for orig, proc in col2_proc}

    total = len(col1_proc)
    results = []

    for i, (orig1, proc1) in enumerate(col1_proc):
        match_proc, score, match_idx = process.extractOne(
            proc1, choices_proc, scorer=fuzz.ratio
        )

        if score >= SIMILARITY_THRESHOLD:
            orig2 = orig_lookup[match_proc]
            results.append([
                orig1,
                orig2,
                proc1,
                match_proc,
                f"{score:.2f}%"
            ])

        # Print progress to console
        print(f"Processed {i + 1}/{total} rows", end='\r')

    print("\nMatching complete!")

    # Output results
    out_df = pd.DataFrame(results, columns=[
        "Sheet1 Original",
        "Best Match from Sheet2",
        "Sheet1 Caps+Digits",
        "Sheet2 Caps+Digits",
        "Similarity %"
    ])
    out_df.to_excel(OUTPUT_PATH, index=False)
    print(f"Results saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    match_columns()
