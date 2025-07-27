
import os
import pandas as pd
from tkinter import *
from tkinter import messagebox
from datetime import datetime

def get_employee_name():
    with open("config.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

class WorkLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PROJMANG - Work Log Manager")
        self.root.configure(bg='white')
        self.employee_name = get_employee_name()
        self.start_time = None
        self.end_time = None

        Label(root, text=f"Hello {self.employee_name}!", bg='white', font=("Arial", 14)).pack(pady=10)

        Button(root, text="Start Work", command=self.start_work, bg="green", fg="white", width=20, height=2).pack(pady=10)
        Button(root, text="End Work", command=self.prompt_end_options, bg="red", fg="white", width=20, height=2).pack(pady=10)

        self.status = Label(root, text="", font=("Arial", 12), bg='white')
        self.status.pack(pady=10)

    def start_work(self):
        self.start_time = datetime.now().strftime("%H:%M")
        self.status.config(text=f"Start time recorded: {self.start_time}")

    def prompt_end_options(self):
        if not self.start_time:
            messagebox.showwarning("Error", "Please start work first.")
            return

        top = Toplevel(self.root)
        top.title("End Work")
        Label(top, text="Please choose an action before ending the day:", font=("Arial", 12)).pack(pady=10)

        Button(top, text="Fill Table", command=lambda: [top.destroy(), self.open_table()], width=20).pack(pady=5)
        Button(top, text="I Filled – Finish Work", command=lambda: [top.destroy(), self.finalize_work()], width=20).pack(pady=5)

    def open_table(self):
        self.table_window = Toplevel(self.root)
        self.table_window.title("Project Table")
        headers = ["Work Description", "Hours", "Project Number"]
        for col, text in enumerate(headers):
            Label(self.table_window, text=text, font=("Arial", 12, "bold")).grid(row=0, column=col, padx=10, pady=5)

        self.entries = []
        for i in range(7):
            row_entries = []
            for j in range(3):
                width = 60 if j == 0 else 30
                e = Entry(self.table_window, width=width, bg='#f0f0f0')
                e.grid(row=i+1, column=j, padx=5, pady=2)
                row_entries.append(e)
            self.entries.append(row_entries)

        Button(self.table_window, text="Save Table", command=self.save_table).grid(row=10, column=0, columnspan=3, pady=10)

    def save_table(self):
        self.records = []
        for row in self.entries:
            desc = row[0].get().strip()
            hours_str = row[1].get().strip()
            proj = row[2].get().strip()

            if proj and hours_str:
                try:
                    hours = float(hours_str)
                    self.records.append({
                        "Employee Name": self.employee_name,
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Start Time": self.start_time,
                        "End Time": "",
                        "Project Number": proj,
                        "Hours": hours,
                        "Work Description": desc,
                        "Total Daily Hours": 0
                    })
                except ValueError:
                    messagebox.showerror("Error", f"Invalid hours value for project: {proj}")
                    return
        self.table_window.destroy()
        messagebox.showinfo("Saved", "Project table saved temporarily. Please click 'I Filled – Finish Work' to finalize.")

    def finalize_work(self):
        self.end_time = datetime.now().strftime("%H:%M")
        if not hasattr(self, 'records') or not self.records:
            messagebox.showwarning("Warning", "No table filled. Please click 'Fill Table' first.")
            return

        total_hours = sum(r["Hours"] for r in self.records)
        for r in self.records:
            r["End Time"] = self.end_time
            r["Total Daily Hours"] = total_hours

        month_str = datetime.now().strftime("%Y-%m")
        file_name = f"PROJMANG_{month_str}.xlsx"
        folder = os.path.expanduser("~/Desktop/PROJMANG")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file_name)

        if os.path.exists(path):
            df_old = pd.read_excel(path)
            df_all = pd.concat([df_old, pd.DataFrame(self.records)], ignore_index=True)
        else:
            df_all = pd.DataFrame(self.records)

        df_all.to_excel(path, index=False)
        messagebox.showinfo("Done", "Work day completed and data saved.")
        self.root.quit()

if __name__ == "__main__":
    root = Tk()
    app = WorkLoggerApp(root)
    root.mainloop()
