import pandas as pd
from thefuzz import process, fuzz
from tkinter import Tk, Label, Button, filedialog, StringVar, messagebox
import os

menu_file = ""
swiggy_file = ""

def browse_menu():
    global menu_file
    menu_file = filedialog.askopenfilename(
        title="Select Menu CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    menu_var.set(f"Menu file: {os.path.basename(menu_file)}" if menu_file else "Menu file: (not selected)")

def browse_swiggy():
    global swiggy_file
    swiggy_file = filedialog.askopenfilename(
        title="Select Swiggy Rating Names CSV file",
        filetypes=[("CSV files", "*.csv")]
    )
    swiggy_var.set(f"Swiggy file: {os.path.basename(swiggy_file)}" if swiggy_file else "Swiggy file: (not selected)")

def run_process():
    global menu_file, swiggy_file

    if not menu_file or not swiggy_file:
        messagebox.showwarning("Files missing", "कृपया दोनों files select करें।")
        return

    try:
        menu_df = pd.read_csv(menu_file)
    except Exception as e:
        messagebox.showerror("Error", f"Menu file पढ़ते समय error: {e}")
        return

    try:
        swiggy_df = pd.read_csv(swiggy_file)
    except Exception as e:
        messagebox.showerror("Error", f"Swiggy file पढ़ते समय error: {e}")
        return

    # Find Online Display Name column case-insensitively
    target_col = None
    for col in menu_df.columns:
        if col.strip().lower() == "online display name":
            target_col = col
            break

    if target_col is None:
        messagebox.showerror("Column missing", "Menu file में 'Online Display Name' column नहीं मिला। कृपया column name चेक करें।")
        return

    # Prepare swiggy names list (first column) and clean them
    swiggy_series = swiggy_df.iloc[:, 0].dropna().astype(str).apply(lambda x: x.strip())
    swiggy_names = swiggy_series.tolist()

    # Map lowercase -> original for case-insensitive exact matches
    swiggy_lower_to_orig = {s.lower(): s for s in swiggy_names}

    matched_names = []
    for val in menu_df[target_col]:
        if pd.isna(val):
            matched_names.append("")  # skip when NaN
            continue

        name = str(val).strip()
        if name == "":
            matched_names.append("")  # skip when empty/whitespace
            continue

        # Case-insensitive exact match
        lower_name = name.lower()
        if lower_name in swiggy_lower_to_orig:
            matched_names.append(swiggy_lower_to_orig[lower_name])
            continue

        # Fuzzy match (threshold 70)
        best = process.extractOne(name, swiggy_names, scorer=fuzz.ratio)
        if best:
            best_match, score = best
            if score >= 70:
                matched_names.append(best_match)
            else:
                matched_names.append("")
        else:
            matched_names.append("")

    # Add new column
    menu_df["Matched Online Name"] = matched_names

    # Save as dialog
    save_path = filedialog.asksaveasfilename(
        title="Save Output File",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile="menu_matched.csv"
    )

    if save_path:
        try:
            menu_df.to_csv(save_path, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Done", f"✅ Output saved at:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Save error", f"फ़ाइल save करते समय error: {e}")
    else:
        messagebox.showinfo("Cancelled", "Save cancelled by user.")


# ---------------- GUI ----------------
root = Tk()
root.title("Menu & Swiggy File Matcher")
root.geometry("480x260")

menu_var = StringVar(value="Menu file: (not selected)")
swiggy_var = StringVar(value="Swiggy file: (not selected)")

Label(root, text="1) Select Menu File (CSV)").pack(pady=(10,3))
Button(root, text="Browse Menu File", command=browse_menu).pack()
Label(root, textvariable=menu_var).pack()

Label(root, text="2) Select Swiggy Rating File (CSV)").pack(pady=(10,3))
Button(root, text="Browse Swiggy File", command=browse_swiggy).pack()
Label(root, textvariable=swiggy_var).pack()

Button(root, text="Run Matching", command=run_process, bg="green", fg="white", width=20).pack(pady=12)

# Footer text (Bottom Right Corner)
Label(root, text="Rights@RSG", fg="gray", font=("Arial", 8, "italic")).place(
    relx=1.0, rely=1.0, anchor="se", x=-10, y=-10
)

root.mainloop()
