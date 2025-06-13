import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import datetime
import pandas as pd
from compare_articles import compare_articles_auto_sheets, get_excel_file_path

class ExcelToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Filtering & Table Generator")
        self.root.geometry("800x600")
        self.file_path = get_excel_file_path()

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        self.build_main_menu()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def build_main_menu(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Select an action:", font=("Arial", 16)).pack(pady=20)

        tk.Button(self.main_frame, text="Compare Articles", command=self.manual_filter_ui, width=30).pack(pady=10)
        tk.Button(self.main_frame, text="Generate Tables", command=self.run_tables_py, width=30).pack(pady=10)
        tk.Button(self.main_frame, text="Generate Pareto Weight Charts", command=self.run_pareto_weights_py, width=30).pack(pady=10)
        tk.Button(self.main_frame, text="Generate Pareto Price Charts", command=self.run_pareto_prices_py, width=30).pack(pady=10)
        tk.Button(self.main_frame, text="How do I work?", command=self.run_how_do_i_work, width=30).pack(pady=10)
        tk.Button(self.main_frame, text="Run Clean Script", command=self.run_clean_py, width=30).pack(pady=10)

    def run_how_do_i_work(self):
        subprocess.run(["python", "HowDoIWork.py"])

    def manual_filter_ui(self):
        self.clear_frame()

        tk.Button(self.main_frame, text="← Back", command=self.build_main_menu).pack(anchor="nw", padx=10, pady=5)

        tk.Label(self.main_frame, text="Manual Filter", font=("Arial", 14)).pack(pady=10)

        self.filter_choice_var = tk.StringVar()
        choice_box = ttk.Combobox(self.main_frame, textvariable=self.filter_choice_var)
        choice_box["values"] = ["artnr", "description"]
        choice_box.current(0)
        choice_box.pack(pady=5)

        self.filter_value_entry = tk.Entry(self.main_frame, width=40)
        self.filter_value_entry.insert(0, "Enter values, separated by commas...")
        self.filter_value_entry.config(fg="grey")

        def on_focus(event):
            if self.filter_value_entry.get() == "Enter values, separated by commas...":
                self.filter_value_entry.delete(0, tk.END)
                self.filter_value_entry.config(fg="black")

        def on_unfocus(event):
            if self.filter_value_entry.get() == "":
                self.filter_value_entry.insert(0, "Enter values, separated by commas...")
                self.filter_value_entry.config(fg="grey")

        self.filter_value_entry.bind("<FocusIn>", on_focus)
        self.filter_value_entry.bind("<FocusOut>", on_unfocus)
        self.filter_value_entry.pack(pady=5)

        self.save_excel_var = tk.BooleanVar()
        self.save_excel_check = tk.Checkbutton(self.main_frame, text="Save result to Excel", variable=self.save_excel_var)
        self.save_excel_check.pack(pady=5)

        tk.Button(self.main_frame, text="Run Filter", command=self.run_manual_filter).pack(pady=10)

        self.result_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
        self.result_area.pack(fill="both", expand=True, padx=10, pady=10)

    def save_to_excel(self, df, filter_choice, filter_value):
        results_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Results")
        os.makedirs(results_folder, exist_ok=True)
        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        output_file_path = os.path.join(results_folder, f"filtered_result_{filter_value}_{timestamp}.xlsx")
        df.to_excel(output_file_path, index=False)
        return output_file_path

    def run_manual_filter(self):
        choice = self.filter_choice_var.get()
        value = self.filter_value_entry.get()

        if value == "Enter values, separated by commas...":
            messagebox.showwarning("Input Error", "Please enter a value to filter.")
            return

        values_list = [val.strip() for val in value.split(",")]

        try:
            result_df = None
            for val in values_list:
                partial_result = compare_articles_auto_sheets(self.file_path, choice, val)
                if result_df is None:
                    result_df = partial_result
                else:
                    result_df = pd.concat([result_df, partial_result])

            self.result_area.delete(1.0, tk.END)
            if result_df is None or result_df.empty:
                self.result_area.insert(tk.END, "No matching articles found.")
            else:
                self.result_area.insert(tk.END, result_df.to_string(index=False))

                if self.save_excel_var.get():
                    output_file_path = self.save_to_excel(result_df, choice, value)
                    messagebox.showinfo("Success", f"Filtered data saved to:\n{output_file_path}")
                    os.startfile(output_file_path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def run_tables_py(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Generating Tables...", font=("Arial", 14)).pack(pady=10)

        self.result_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
        self.result_area.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            # Run tables.py as subprocess
            result = subprocess.run(["python", "tables.py"], capture_output=True, text=True)

            if result.stdout:
                self.result_area.insert(tk.END, result.stdout)
            if result.stderr:
                self.result_area.insert(tk.END, "\n[ERRORS]\n" + result.stderr)

            # Look for latest Excel file in Results folder
            results_folder = "Results"
            excel_files = sorted(
                [os.path.join(results_folder, f) for f in os.listdir(results_folder) if f.endswith(".xlsx")],
                key=os.path.getmtime,
                reverse=True
            )

            if excel_files:
                latest_file = excel_files[0]
                self.result_area.insert(tk.END, f"\nLatest generated file: {latest_file}")
                ask = messagebox.askyesno("Open File?", f"Generated tables saved to:\n{latest_file}\n\nOpen it?")
                if ask:
                    os.startfile(latest_file)
            else:
                messagebox.showwarning("No Output", "No Excel file was generated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

        tk.Button(self.main_frame, text="← Back", command=self.build_main_menu).pack(pady=10)

    def run_pareto_weights_py(self):
      self.clear_frame()
      tk.Label(self.main_frame, text="Generating Pareto Charts...", font=("Arial", 14)).pack(pady=10)

      self.result_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
      self.result_area.pack(fill="both", expand=True, padx=10, pady=10)

      try:
          result = subprocess.run(["python", "pareto_weights.py"], capture_output=True, text=True)

          if result.stdout:
              self.result_area.insert(tk.END, result.stdout)
          if result.stderr:
              self.result_area.insert(tk.END, "\n[ERRORS]\n" + result.stderr)

          results_folder = "Results"
          png_files = sorted(
              [os.path.join(results_folder, f) for f in os.listdir(results_folder) if f.endswith(".png")],
              key=os.path.getmtime,
              reverse=True
          )

          if png_files:
              for png in png_files[:5]:
                  self.result_area.insert(tk.END, f"{png}\n")
                  os.startfile(png)  # Automatically open each PNG
          else:
              self.result_area.insert(tk.END, "No charts were created.")
      except Exception as e:
          messagebox.showerror("Error", str(e))

      tk.Button(self.main_frame, text="← Back", command=self.build_main_menu).pack(pady=20)

    def run_pareto_prices_py(self):
      self.clear_frame()
      tk.Label(self.main_frame, text="Generating Pareto Charts...", font=("Arial", 14)).pack(pady=10)

      self.result_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
      self.result_area.pack(fill="both", expand=True, padx=10, pady=10)

      try:
          result = subprocess.run(["python", "pareto_prices.py"], capture_output=True, text=True)

          if result.stdout:
              self.result_area.insert(tk.END, result.stdout)
          if result.stderr:
              self.result_area.insert(tk.END, "\n[ERRORS]\n" + result.stderr)

          results_folder = "Results"
          png_files = sorted(
              [os.path.join(results_folder, f) for f in os.listdir(results_folder) if f.endswith(".png")],
              key=os.path.getmtime,
              reverse=True
          )

          if png_files:
              for png in png_files[:5]:
                  self.result_area.insert(tk.END, f"{png}\n")
                  os.startfile(png)  # Automatically open each PNG
          else:
              self.result_area.insert(tk.END, "No charts were created.")
      except Exception as e:
          messagebox.showerror("Error", str(e))

      tk.Button(self.main_frame, text="← Back", command=self.build_main_menu).pack(pady=20)


    def run_clean_py(self):
        self.clear_frame()
        tk.Label(self.main_frame, text="Running Clean Script...", font=("Arial", 14)).pack(pady=10)

        self.result_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
        self.result_area.pack(fill="both", expand=True, padx=10, pady=10)

        try:
            result = subprocess.run(["python", "clean.py"], capture_output=True, text=True)

            if result.stdout:
                self.result_area.insert(tk.END, result.stdout)
            if result.stderr:
                self.result_area.insert(tk.END, "\n[ERRORS]\n" + result.stderr)
        except Exception as e:
            messagebox.showerror("Error", str(e))

        tk.Button(self.main_frame, text="← Back", command=self.build_main_menu).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelToolApp(root)
    root.mainloop()
