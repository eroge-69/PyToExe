import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# Use raw string for proper path formatting
DONUT_EXE = r"C:\Users\Administrator\Downloads\donut_v1.1\donut.exe"

def select_file():
    filepath = filedialog.askopenfilename(
        title="Select DLL File",
        filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
    )
    if filepath:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, filepath)

def convert_to_shellcode():
    dll_path = entry_file.get()
    if not dll_path or not os.path.isfile(dll_path):
        messagebox.showerror("Error", "Invalid DLL file selected.")
        return

    output_file = os.path.splitext(dll_path)[0] + "_shellcode.bin"
    save_txt = save_as_txt.get()  # Check checkbox value

    try:
        result = subprocess.run(
            [DONUT_EXE, "-i", dll_path, "-f", "1", "-a", "2", "-o", output_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            message = f"Shellcode saved to:\n{output_file}"

            if save_txt:
                txt_output = os.path.splitext(output_file)[0] + ".txt"
                try:
                    with open(output_file, "rb") as f_in, open(txt_output, "w") as f_out:
                        data = f_in.read()
                        f_out.write("unsigned char shellcode[] = {\n")
                        for i in range(0, len(data), 12):
                            chunk = data[i:i+12]
                            hex_bytes = ", ".join(f"0x{b:02X}" for b in chunk)
                            f_out.write("  " + hex_bytes + ",\n")
                        f_out.write("};\n")
                    message += f"\n\nC array saved to:\n{txt_output}"
                except Exception as e:
                    messagebox.showwarning("TXT Export Failed", f"Could not save .txt:\n{str(e)}")

            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Donut Error", result.stderr)
    except Exception as e:
        messagebox.showerror("Execution Error", str(e))

# --- UI Setup ---
root = tk.Tk()
root.title("DLL to Shellcode Converter (Donut)")

tk.Label(root, text="DLL File:").grid(row=0, column=0, padx=10, pady=10)
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=10, pady=10)

btn_browse = tk.Button(root, text="Browse", command=select_file)
btn_browse.grid(row=0, column=2, padx=10, pady=10)

# Add "Save as TXT" checkbox
save_as_txt = tk.BooleanVar()
chk_txt = tk.Checkbutton(root, text="Save as .txt (C array)", variable=save_as_txt)
chk_txt.grid(row=1, column=0, columnspan=3)

btn_convert = tk.Button(root, text="Convert to Shellcode", command=convert_to_shellcode, bg="#4CAF50", fg="white")
btn_convert.grid(row=2, column=0, columnspan=3, pady=20)

root.mainloop()
