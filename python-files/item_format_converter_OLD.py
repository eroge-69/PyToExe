import tkinter as tk
from tkinter import ttk

def convert_qb_to_ox_and_sql_and_new_format(qb_format):
    qb_format = qb_format.split("\n")
    ox_format = ""
    sql_format = ""
    new_format = ""

    for line in qb_format:
        if "=" in line:
            key = line.split("=")[0].strip()
            name = line.split("['name'] = ")[1].split(",")[0].replace("'", "").strip()
            label = line.split("['label'] = ")[1].split(",")[0].replace("'", "").strip()
            weight = line.split("['weight'] = ")[1].split(",")[0].strip()
            desc = line.split("['description'] = ")[1].split("}")[0].strip()
            stack = "true"
            close = "true"
            rare = "0"
            can_remove = "1"

            ox_format += f"{key} = {{\n\tlabel = \"{label}\",\n\tweight = {weight},\n\tstack = {stack},\n\tclose = {close},\n\tdescription = {desc}\n}},\n\n"
            sql_format += f"('{name}', '{label}', {weight}, {rare}, {can_remove}),\n"
            new_format += f'["{name}"] = "{label}",\n'

    return ox_format, sql_format, new_format

def convert():
    input_text = input_box.get("1.0", "end-1c")
    ox_output_text, sql_output_text, new_output_text = convert_qb_to_ox_and_sql_and_new_format(input_text)
    ox_output_box.delete("1.0", tk.END)
    ox_output_box.insert(tk.END, ox_output_text)
    sql_output_box.delete("1.0", tk.END)
    sql_output_box.insert(tk.END, sql_output_text)
    new_output_box.delete("1.0", tk.END)
    new_output_box.insert(tk.END, new_output_text)

root = tk.Tk()
root.title("QB, ESX, SQL Item Converter, by @d3MBA#0001")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

input_box = tk.Text(frame, wrap=tk.NONE, width=80, height=50)
input_box.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=input_box.yview)
scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
input_box["yscrollcommand"] = scrollbar.set

convert_button = ttk.Button(frame, text="Convert", command=convert)
convert_button.grid(row=1, column=0, columnspan=3, pady=10)

ox_output_box = tk.Text(frame, wrap=tk.NONE, width=80, height=50)
ox_output_box.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

scrollbar2 = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=ox_output_box.yview)
scrollbar2.grid(row=0, column=3, sticky=(tk.N, tk.S))
ox_output_box["yscrollcommand"] = scrollbar2.set

sql_output_box = tk.Text(frame, wrap=tk.NONE, width=80, height=50)
sql_output_box.grid(row=0, column=4, sticky=(tk.W, tk.E, tk.N, tk.S))

scrollbar3 = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=sql_output_box.yview)
scrollbar3.grid(row=0, column=5, sticky=(tk.N, tk.S))
sql_output_box["yscrollcommand"] = scrollbar3.set

new_output_box = tk.Text(frame, wrap=tk.NONE, width=80, height=50)
new_output_box.grid(row=0, column=6, sticky=(tk.W, tk.E, tk.N, tk.S))

scrollbar4 = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=new_output_box.yview)
scrollbar4.grid(row=0, column=7, sticky=(tk.N, tk.S))
new_output_box["yscrollcommand"] = scrollbar4.set

root.mainloop()
