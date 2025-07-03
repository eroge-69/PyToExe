import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import time

# Dropdown display labels and actual pump numbers
pump_display = {
    "6 (17240)": "6",
    "7 (28104)": "7",
    "8 (17242)": "8",
    "9 (12185)": "9",
    "10 (17241)": "10",
    "11 (23482)": "11",
    "12 (17239)": "12",
    "13 (12186)": "13"
}

def clear_transaction():
    try:
        val = float(entry.get())
        result = val * 0.675
        result_textbox.config(state='normal')
        result_textbox.delete('1.0', tk.END)
        result_textbox.insert(tk.END, f"{result:.3f}")
        result_textbox.config(state='disabled')
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter a valid number")
        return

    try:
        from pywinauto import Application
        from pywinauto.controls.uia_controls import ComboBoxWrapper, EditWrapper
    except ImportError:
        messagebox.showerror("Import Error", "pywinauto is not installed.\nRun: pip install pywinauto")
        return

    entered_value = entry.get().strip()
    result_text = result_textbox.get('1.0', tk.END).strip()
    if not entered_value or not result_text:
        messagebox.showwarning("Missing Data", "Both input and result must be present.")
        return

    selected_display = combo.get()
    selected_pump = pump_display.get(selected_display)
    if not selected_pump:
        messagebox.showerror("Pump Error", "Invalid pump selection")
        return

    root.clipboard_clear()
    root.clipboard_append(result_text)

    exe_path = r"C:\Users\a.shraim\Desktop\PrepayTrxClear2025\PrepayTrxClear2025\PrepayTrxClearance.exe"
    if not os.path.isfile(exe_path):
        messagebox.showerror("Error", f"Executable not found:\n{exe_path}")
        return

    try:
        app = Application(backend="uia").start(exe_path)

        window = None
        for _ in range(20):
            try:
                window = app.window(title_re=".*")
                if window.exists(timeout=1):
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if window is None:
            messagebox.showerror("Error", "Could not find the application window.")
            return

        try:
            load_btn = window.child_window(title="Load", control_type="Button")
            load_btn.wait("enabled ready", timeout=10)
            load_btn.click_input()

            time.sleep(3)

            combo_boxes = window.children(control_type="ComboBox")
            static_texts = window.children(control_type="Text")

            def top_position(ctrl):
                try:
                    return ctrl.rectangle().top
                except Exception:
                    return 0

            combo_boxes_sorted = sorted(combo_boxes, key=top_position)
            static_texts_sorted = sorted(static_texts, key=top_position)

            pump_combo = None

            for cb in combo_boxes_sorted:
                cb_top = cb.rectangle().top
                possible_labels = [lbl for lbl in static_texts_sorted if lbl.rectangle().top < cb_top]
                if not possible_labels:
                    continue
                label = possible_labels[-1]
                label_text = label.window_text()
                if label_text.strip().lower() in ["pump no:", "pump no", "pump number:", "pump number"]:
                    pump_combo = ComboBoxWrapper(cb.element_info)
                    break

            if pump_combo is None and len(combo_boxes_sorted) >= 2:
                pump_combo = ComboBoxWrapper(combo_boxes_sorted[1].element_info)

            if pump_combo:
                pump_combo.select(selected_pump)

            # Fill the external EXE fields
            text_inputs = window.descendants(control_type="Edit")
            text_labels = window.descendants(control_type="Text")

            def find_textbox_by_label(label_text):
                label_text = label_text.lower().strip()
                for label in text_labels:
                    try:
                        text = label.window_text().lower().strip()
                        if label_text in text:
                            label_rect = label.rectangle()
                            for edit in text_inputs:
                                edit_rect = edit.rectangle()
                                if abs(edit_rect.top - label_rect.top) < 30 and edit_rect.left > label_rect.right:
                                    return EditWrapper(edit.element_info)
                    except Exception:
                        continue
                return None

            qty_box = find_textbox_by_label("actual filled qty")
            amt_box = find_textbox_by_label("actual filled amt")

            if qty_box:
                qty_box.set_edit_text(entered_value)
            else:
                messagebox.showwarning("Warning", "'Actual Filled Qty:' box not found.")

            if amt_box:
                amt_box.set_edit_text(result_text)
            else:
                messagebox.showwarning("Warning", "'Actual Filled Amt:' box not found.")

        except Exception as e:
            messagebox.showerror("Automation Error", f"Failed to control EXE:\n{e}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch EXE:\n{e}")

def reset():
    entry.delete(0, tk.END)
    combo.current(0)
    result_textbox.config(state='normal')
    result_textbox.delete('1.0', tk.END)
    result_textbox.config(state='disabled')

# --- UI Setup ---
root = tk.Tk()
root.title("Pump Calculator")
root.geometry("400x450")

bold_font = font.Font(weight="bold", size=11)

tk.Label(root, text="Select Pump #", font=bold_font).pack(pady=5)
combo = ttk.Combobox(root, values=list(pump_display.keys()), font=bold_font, state="readonly")
combo.current(0)
combo.pack(pady=5)

tk.Label(root, text="Enter Value:", font=bold_font).pack(pady=5)
entry = tk.Entry(root, font=bold_font)
entry.pack(pady=5)

tk.Button(root, text="Clear Transaction", command=clear_transaction, font=bold_font).pack(pady=10)
tk.Button(root, text="Reset", command=reset, font=bold_font).pack(pady=5)

tk.Label(root, text="Result:", font=bold_font).pack(pady=5)
result_textbox = tk.Text(root, height=1, width=20, font=bold_font)
result_textbox.pack(pady=10)
result_textbox.config(state='disabled')

root.mainloop()
