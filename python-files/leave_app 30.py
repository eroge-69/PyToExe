import tkinter as tk
from tkinter import messagebox
import csv
import os

class LeaveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leave and Salary Application")
        
        labels = ["Batch Number", "Leave Status (Approved/Rejected)", "Comment", "Days of Leave", "Salary"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(root, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = tk.Entry(root, width=30)
            entry.grid(row=i, column=1, pady=2)
            self.entries[label] = entry
        
        tk.Label(root, text="Salary Deduction:").grid(row=len(labels), column=0, sticky=tk.W)
        self.salary_deduction_var = tk.StringVar()
        tk.Label(root, textvariable=self.salary_deduction_var).grid(row=len(labels), column=1, sticky=tk.W)
        
        tk.Button(root, text="Calculate", command=self.calculate).grid(row=len(labels)+1, column=0, columnspan=2, pady=10)

        # CSV file setup
        self.csv_file = "leave_records.csv"
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Batch Number", "Leave Status", "Comment", "Days of Leave", "Salary", "Salary Deduction"])
        
    def calculate(self):
        try:
            batch_number = self.entries["Batch Number"].get()
            leave_status = self.entries["Leave Status (Approved/Rejected)"].get().strip().lower()
            comment = self.entries["Comment"].get()
            days_of_leave = int(self.entries["Days of Leave"].get())
            salary = float(self.entries["Salary"].get())
            
            if leave_status == 'yes':
                salary_deduction = (salary / 30) * days_of_leave
            else:
                salary_deduction = 0.0
            
            self.salary_deduction_var.set(f"{salary_deduction:.2f} SAR")
            
            summary = (
                f"Batch Number: {batch_number}\n"
                f"Leave Status: {leave_status.capitalize()}\n"
                f"Comment: {comment}\n"
                f"Days of Leave: {days_of_leave}\n"
                f"Salary: {salary:.2f} SAR\n"
                f"Salary Deduction: {salary_deduction:.2f} SAR"
            )
            messagebox.showinfo("Leave and Salary Summary", summary)
            
            # Save to CSV
            with open(self.csv_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([batch_number, leave_status, comment, days_of_leave, f"{salary:.2f}", f"{salary_deduction:.2f}"])
        
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LeaveApp(root)
    root.mainloop()
