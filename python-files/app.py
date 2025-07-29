import pandas as pd
import json
import tkinter as tk
from tkinter import filedialog, messagebox


json_template = {
    "label": "Add Employee",
    "reorder": False,
    "addAnotherPosition": "bottom",
    "layoutFixed": False,
    "enableRowGroups": False,
    "initEmpty": False,
    "tableView": False,
    "defaultValue": [],
    "protected": True,
    "validateWhenHidden": False,
    "key": "addEmployee",
    "conditional": {
        "show": True,
        "when": "coCode",
        "eq": "43444"
    },
    "type": "datagrid",
    "input": True,
    "components": [
        {"label": "SITEID", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "name", "type": "textfield", "input": True},
        {"label": "PERSONID", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "personid", "type": "textfield", "input": True},
        {"label": "FIRSTNAME", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "firstname", "type": "textfield", "input": True},
        {"label": "LASTNAME", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "lastname", "type": "textfield", "input": True},
        {"label": "COMPANY_CODE", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "companyCode", "type": "textfield", "input": True},
        {
            "label": "MOBILISATION STATUS",
            "widget": "choicesjs",
            "tableView": True,
            "data": {
                "values": [
                    {"label": "Demobilised", "value": "demobilised"},
                    {"label": "Mobilised", "value": "mobilised"}
                ]
            },
            "validateWhenHidden": False,
            "key": "mobilisationStatus",
            "type": "select",
            "input": True
        },
        {"label": "CONTRACT NO", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "contractNo", "type": "textfield", "input": True},
        {"label": "Hours", "applyMaskOn": "change", "tableView": True, "validateWhenHidden": False, "key": "hours", "type": "textfield", "input": True}
    ]
}

def convert_csv_to_json():
    try:
        csv_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
        if not csv_path:
            return

        df = pd.read_csv(csv_path)
        if 'hours' in df.columns:
            df['hours'] = df['hours'].fillna("")

        records = df.to_dict(orient='records')
        json_template['defaultValue'] = records

        json_path = filedialog.asksaveasfilename(title="Save JSON File", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not json_path:
            return

        with open(json_path, 'w') as f:
            json.dump(json_template, f, indent=2)

        messagebox.showinfo("Success", f"JSON file saved to:\n{json_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")


root = tk.Tk()
root.title("CSV to JSON Converter")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

label = tk.Label(frame, text="Click below to convert CSV to JSON", font=("Arial", 12))
label.pack(pady=10)

convert_button = tk.Button(frame, text="Convert CSV", command=convert_csv_to_json, font=("Arial", 10), width=20)
convert_button.pack(pady=10)

root.mainloop()
