import re
import pandas as pd
import os
from tkinter import Tk, filedialog, messagebox

# GUI ဖိုင်ရွေး dialog box ဖွင့်မယ်
root = Tk()
root.withdraw()  # main tkinter window မပြချင်လို့
file_path = filedialog.askopenfilename(
    title="Select PPPoE Users .txt File",
    filetypes=[("Text Files", "*.txt")]
)

if not file_path:
    messagebox.showerror("Error", "No file selected!")
    exit()

rows = []
with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        comment = re.search(r'comment=(\"[^\"]+\"|\S+)', line)
        disabled = re.search(r'disabled=(\S+)', line)
        name = re.search(r'name=(\S+)', line)
        profile = re.search(r'profile=(\S+)', line)

        rows.append({
            "comment": comment.group(1).strip('"') if comment else "",
            "disabled": disabled.group(1) if disabled else "",
            "name": name.group(1) if name else "",
            "profile": profile.group(1) if profile else ""
        })

# output filename
output_file = os.path.splitext(file_path)[0] + "_parsed.xlsx"

df = pd.DataFrame(rows)
df.to_excel(output_file, index=False)

messagebox.showinfo("Done", f"✅ Parsed data saved to:\n{output_file}")
