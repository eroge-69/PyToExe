import tkinter as tk
from tkinter import filedialog, messagebox
import time
import re
import os

def run_fdz(code):
    variables = {"$": 0}
    input_buffer = ""

    lines = code.strip().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("/*") and line.endswith("*/"):
            i += 1
            continue

        if line in ("Run", "End"):
            i += 1
            continue

        if line.startswith("SuperShow"):
            content = re.findall(r'"(.*?)"', line)
            if content:
                output(f"\n{'='*40}\n{content[0].upper()}\n{'='*40}\n")
            i += 1
            continue

        if line.startswith("Show"):
            content = re.findall(r'"(.*?)"', line)
            if content:
                msg = content[0].replace("(input)", input_buffer)
                if msg == "$":
                    output(str(variables["$"]))
                elif msg.startswith("$"):
                    var = msg.strip("$")
                    output(str(variables.get(var, f"[undefined variable {var}]")))
                else:
                    output(msg)
            i += 1
            continue

        if line.startswith("Set"):
            expr = re.findall(r'Set\s+\"?\$=?(.*?)\"?$', line)
            if expr:
                val = expr[0]
                if val.startswith("+"):
                    if val == "+input":
                        try:
                            delta = int(simple_input("입력: "))
                            variables["$"] += delta
                        except ValueError:
                            output("숫자 입력하라고, dumbass.")
                    else:
                        variables["$"] += int(val[1:])
                elif val.startswith("-"):
                    variables["$"] -= int(val[1:])
                else:
                    variables["$"] = int(val)
            i += 1
            continue

        if line.startswith("If \"input="):
            condition = re.findall(r'If \"input=(.*?)\"', line)
            if condition:
                user_input = simple_input("").strip().lower()
                if user_input == condition[0].lower():
                    i += 1
                else:
                    while i < len(lines) and not lines[i].strip().startswith("Else"):
                        i += 1
            else:
                i += 1
            continue

        if line.startswith("Wait"):
            seconds = re.findall(r'\"(\d+)s\"', line)
            if seconds:
                time.sleep(int(seconds[0]))
            i += 1
            continue

        i += 1

def simple_input(prompt):
    return simpledialog.askstring("FDZ Input", prompt)

def output(msg):
    output_box.insert(tk.END, str(msg) + "\n")
    output_box.see(tk.END)

def open_file():
    path = filedialog.askopenfilename(filetypes=[("FDZ Files", "*.fdz")])
    if path:
        with open(path, 'r', encoding='utf-8') as file:
            editor.delete("1.0", tk.END)
            editor.insert(tk.END, file.read())

def save_file():
    path = filedialog.asksaveasfilename(defaultextension=".fdz", filetypes=[("FDZ Files", "*.fdz")])
    if path:
        with open(path, 'w', encoding='utf-8') as file:
            file.write(editor.get("1.0", tk.END))

def run_code():
    output_box.delete("1.0", tk.END)
    code = editor.get("1.0", tk.END)
    run_fdz(code)

# GUI 구성
root = tk.Tk()
root.title("FDZ 인터프리터")
root.geometry("800x600")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True)

editor = tk.Text(frame, height=20, font=("Courier", 12))
editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack()

open_btn = tk.Button(btn_frame, text="불러오기", command=open_file)
open_btn.pack(side=tk.LEFT, padx=5)

save_btn = tk.Button(btn_frame, text="저장하기", command=save_file)
save_btn.pack(side=tk.LEFT, padx=5)

run_btn = tk.Button(btn_frame, text="실행", command=run_code)
run_btn.pack(side=tk.LEFT, padx=5)

output_box = tk.Text(root, height=10, bg="#111", fg="#0f0", font=("Courier", 11))
output_box.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

root.mainloop()
