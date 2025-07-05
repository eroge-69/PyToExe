import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel
import pandas as pd
import pyreadstat

class DataCleanerStataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Data Cleaner with Command Prompt")

        self.df = None  # Dataset placeholder

        # Buttons
        tk.Button(root, text="Select Data File", command=self.load_data).pack(pady=5)
        tk.Button(root, text="Export to Stata (.dta)", command=self.export_to_dta).pack(pady=5)

        # Output area
        self.output_area = scrolledtext.ScrolledText(root, width=80, height=20)
        self.output_area.pack(pady=5)

        # Command entry
        self.cmd_entry = tk.Entry(root, width=80)
        self.cmd_entry.pack(pady=5)
        self.cmd_entry.bind("<Return>", self.process_command)

        self.print_output("Welcome to Stata-style Data Cleaner GUI.\nType 'help' for available commands.\n")

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV or Excel", "*.csv *.xlsx")])
        if not file_path:
            return

        header_option = messagebox.askyesno("Header Row", "Does the dataset have column headers?")

        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path, header=0 if header_option else None)
            else:
                self.df = pd.read_excel(file_path, header=0 if header_option else None)

            if not header_option:
                self.df.columns = [f"var_{i+1}" for i in range(self.df.shape[1])]

            self.print_output(f"Loaded dataset with {self.df.shape[0]} rows and {self.df.shape[1]} columns.\n")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def export_to_dta(self):
        if self.df is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".dta", filetypes=[("Stata Files", "*.dta")])
            if file_path:
                pyreadstat.write_dta(self.df, file_path)
                messagebox.showinfo("Export Successful", f"Dataset exported to {file_path}")
        else:
            messagebox.showerror("Error", "No dataset loaded.")

    def process_command(self, event=None):
        cmd = self.cmd_entry.get().strip()
        self.print_output(f">> {cmd}\n")
        self.cmd_entry.delete(0, tk.END)

        if cmd == "help":
            self.print_output("""
Available Commands:
  list                     Show dataset in popup
  dlt varname              Delete variable
  delval varname value     Delete rows where varname == value
  rename oldname newname   Rename variable
  summarize                Summary statistics
  export_dta filename.dta  Export to Stata .dta
  export_csv filename.csv  Export to CSV
""")

        elif cmd == "list":
            if self.df is not None:
                self.show_popup(self.df)
            else:
                self.print_output("No dataset loaded.\n")

        elif cmd.startswith("dlt "):
            if self.df is not None:
                var = cmd.split()[1]
                if var in self.df.columns:
                    self.df.drop(columns=var, inplace=True)
                    self.print_output(f"Variable '{var}' deleted.\n")
                else:
                    self.print_output(f"Variable '{var}' not found.\n")
            else:
                self.print_output("No dataset loaded.\n")

        elif cmd.startswith("delval "):
            if self.df is not None:
                parts = cmd.split()
                if len(parts) >= 3:
                    var = parts[1]
                    value = " ".join(parts[2:])
                    if var in self.df.columns:
                        before = len(self.df)
                        try:
                            try:
                                value_cast = float(value)
                                mask = self.df[var] != value_cast
                            except ValueError:
                                mask = self.df[var] != value
                            self.df = self.df[mask]
                            after = len(self.df)
                            self.print_output(f"Deleted {before - after} rows where {var} == {value}\n")
                        except Exception as e:
                            self.print_output(f"Error deleting values: {e}\n")
                    else:
                        self.print_output(f"Variable '{var}' not found.\n")
                else:
                    self.print_output("Usage: delval varname value\n")
            else:
                self.print_output("No dataset loaded.\n")

        elif cmd.startswith("rename "):
            if self.df is not None:
                parts = cmd.split()
                if len(parts) == 3 and parts[1] in self.df.columns:
                    self.df.rename(columns={parts[1]: parts[2]}, inplace=True)
                    self.print_output(f"Renamed '{parts[1]}' to '{parts[2]}'.\n")
                else:
                    self.print_output("Usage: rename oldname newname\n")
            else:
                self.print_output("No dataset loaded.\n")

        elif cmd == "summarize":
            if self.df is not None:
                self.print_output(f"{self.df.describe(include='all')}\n")
            else:
                self.print_output("No dataset loaded.\n")

        elif cmd.startswith("export_dta "):
            if self.df is not None:
                export_path = cmd.split()[1]
                try:
                    pyreadstat.write_dta(self.df, export_path)
                    self.print_output(f"Dataset exported to {export_path}\n")
                except Exception as e:
                    self.print_output(f"Export failed: {e}\n")
            else:
                self.print_output("No dataset loaded.\n")

        elif cmd.startswith("export_csv "):
            if self.df is not None:
                export_path = cmd.split()[1]
                try:
                    self.df.to_csv(export_path, index=False)
                    self.print_output(f"Dataset exported to {export_path}\n")
                except Exception as e:
                    self.print_output(f"Export failed: {e}\n")
            else:
                self.print_output("No dataset loaded.\n")

        else:
            self.print_output("Unknown command. Type 'help' for options.\n")

    def print_output(self, text):
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)

    def show_popup(self, data):
        popup = Toplevel(self.root)
        popup.title("Dataset Preview")
        text_area = scrolledtext.ScrolledText(popup, width=100, height=30)
        text_area.pack(padx=10, pady=10)
        text_area.insert(tk.END, data.to_string(index=False))
        text_area.config(state='disabled')

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanerStataGUI(root)
    root.mainloop()
