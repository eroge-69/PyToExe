import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from datetime import datetime
import json
import os # For checking if file exists

class Employee:
    def __init__(self, name, position, monthly_salary, remaining_salary=None, payment_history=None):
        self.name = name
        self.position = position
        self.monthly_salary = float(monthly_salary)
        # If remaining_salary is not provided (e.g., for new employees), set it to monthly_salary
        self.remaining_salary = float(remaining_salary) if remaining_salary is not None else float(monthly_salary)
        self.payment_history = payment_history if payment_history is not None else [] # List of tuples: (date, reason, amount)

    def record_payment(self, amount, reason):
        if amount > self.remaining_salary:
            return False # Not enough funds
        self.remaining_salary -= amount
        # Store date, reason, amount as a dictionary for easier JSON serialization
        self.payment_history.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "reason": reason, "amount": amount})
        return True

    def to_dict(self):
        """Converts the Employee object to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "position": self.position,
            "monthly_salary": self.monthly_salary,
            "remaining_salary": self.remaining_salary,
            "payment_history": self.payment_history
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an Employee object from a dictionary (for JSON deserialization)."""
        return cls(
            name=data["name"],
            position=data["position"],
            monthly_salary=data["monthly_salary"],
            remaining_salary=data["remaining_salary"],
            payment_history=data["payment_history"]
        )

class SalaryManagerApp:
    DATA_FILE = "employees.json"

    def __init__(self, master):
        self.master = master
        master.title("Employee Salary Manager")

        self.employees = []
        self.load_data() # Load data when the application starts

        # --- Configure window close protocol ---
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Employee Input Frame ---
        self.input_frame = tk.LabelFrame(master, text="Employee Details")
        self.input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(self.input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Position:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.position_entry = tk.Entry(self.input_frame, width=30)
        self.position_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.input_frame, text="Monthly Salary:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.salary_entry = tk.Entry(self.input_frame, width=30)
        self.salary_entry.grid(row=2, column=1, padx=5, pady=5)

        # --- Buttons for Employee Management ---
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(padx=10, pady=5)

        self.add_button = tk.Button(self.button_frame, text="Add Employee", command=self.add_employee)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(self.button_frame, text="Edit Employee", command=self.edit_employee)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete Employee", command=self.delete_employee)
        self.delete_button.pack(side="left", padx=5)

        # --- Employee List Display ---
        self.employee_list_frame = tk.LabelFrame(master, text="Employees")
        self.employee_list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.employee_listbox = tk.Listbox(self.employee_list_frame)
        self.employee_listbox.pack(side="left", fill="both", expand=True)
        self.employee_listbox.bind("<<ListboxSelect>>", self.display_selected_employee_info)

        self.scrollbar = tk.Scrollbar(self.employee_list_frame, orient="vertical")
        self.scrollbar.config(command=self.employee_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.employee_listbox.config(yscrollcommand=self.scrollbar.set)

        # --- Employee Info Display ---
        self.info_frame = tk.LabelFrame(master, text="Selected Employee Details")
        self.info_frame.pack(padx=10, pady=10, fill="x")

        self.info_name = tk.Label(self.info_frame, text="Name: ")
        self.info_name.pack(anchor="w", padx=5, pady=2)
        self.info_position = tk.Label(self.info_frame, text="Position: ")
        self.info_position.pack(anchor="w", padx=5, pady=2)
        self.info_monthly_salary = tk.Label(self.info_frame, text="Monthly Salary: ")
        self.info_monthly_salary.pack(anchor="w", padx=5, pady=2)
        self.info_remaining_salary = tk.Label(self.info_frame, text="Remaining Salary: ")
        self.info_remaining_salary.pack(anchor="w", padx=5, pady=2)

        # --- Payment and Export Buttons ---
        self.action_button_frame = tk.Frame(master)
        self.action_button_frame.pack(padx=10, pady=5)

        self.pay_button = tk.Button(self.action_button_frame, text="Record Payment", command=self.record_payment)
        self.pay_button.pack(side="left", padx=5)

        self.history_button = tk.Button(self.action_button_frame, text="View Payment History", command=self.view_payment_history)
        self.history_button.pack(side="left", padx=5)

        self.export_button = tk.Button(self.action_button_frame, text="Export Employee Data", command=self.export_employee_data)
        self.export_button.pack(side="left", padx=5)

        self.update_employee_listbox() # Populate listbox after loading data

    def on_closing(self):
        """Called when the user tries to close the window."""
        if messagebox.askokcancel("Quit", "Do you want to save data and quit?"):
            self.save_data()
            self.master.destroy()

    def save_data(self):
        """Saves employee data to a JSON file."""
        try:
            with open(self.DATA_FILE, "w") as f:
                # Convert list of Employee objects to list of dictionaries
                employee_data = [emp.to_dict() for emp in self.employees]
                json.dump(employee_data, f, indent=4)
            print(f"Data saved to {self.DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {e}")

    def load_data(self):
        """Loads employee data from a JSON file."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as f:
                    employee_data = json.load(f)
                    # Reconstruct Employee objects from loaded dictionaries
                    self.employees = [Employee.from_dict(data) for data in employee_data]
                print(f"Data loaded from {self.DATA_FILE}")
            except json.JSONDecodeError as e:
                messagebox.showerror("Load Error", f"Error decoding JSON data from {self.DATA_FILE}: {e}\nStarting with empty data.")
                self.employees = [] # Start fresh if data is corrupted
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load data: {e}\nStarting with empty data.")
                self.employees = [] # Start fresh if any other error occurs
        else:
            print(f"No data file found: {self.DATA_FILE}. Starting with empty data.")
            self.employees = [] # Initialize as empty if file doesn't exist

    def update_employee_listbox(self):
        self.employee_listbox.delete(0, tk.END)
        for emp in self.employees:
            self.employee_listbox.insert(tk.END, emp.name)
        # Clear info display if no employee is selected or list is empty
        if not self.employees:
            self.clear_employee_info_display()

    def clear_entry_fields(self):
        self.name_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.salary_entry.delete(0, tk.END)

    def get_selected_employee(self):
        selected_index = self.employee_listbox.curselection()
        if selected_index:
            return self.employees[selected_index[0]]
        return None

    def add_employee(self):
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        salary_str = self.salary_entry.get().strip()

        if not name or not position or not salary_str:
            messagebox.showerror("Input Error", "All fields must be filled.")
            return
        try:
            monthly_salary = float(salary_str)
            if monthly_salary < 0:
                messagebox.showerror("Input Error", "Monthly salary cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Monthly Salary must be a number.")
            return

        # Check for duplicate names (optional, but good practice)
        for emp in self.employees:
            if emp.name.lower() == name.lower():
                messagebox.showwarning("Duplicate Employee", f"An employee with the name '{name}' already exists.")
                return

        new_employee = Employee(name, position, monthly_salary)
        self.employees.append(new_employee)
        self.update_employee_listbox()
        self.clear_entry_fields()
        messagebox.showinfo("Success", f"Employee '{name}' added successfully.")
        self.save_data() # Save data after adding

    def edit_employee(self):
        selected_employee = self.get_selected_employee()
        if not selected_employee:
            messagebox.showwarning("Selection Error", "Please select an employee to edit.")
            return

        # Populate fields for editing
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, selected_employee.name)
        self.position_entry.delete(0, tk.END)
        self.position_entry.insert(0, selected_employee.position)
        self.salary_entry.delete(0, tk.END)
        self.salary_entry.insert(0, str(selected_employee.monthly_salary))

        # Change Add button to Save Changes and disable other buttons
        self.add_button.config(text="Save Changes", command=lambda: self._save_edited_employee(selected_employee))
        self.edit_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.pay_button.config(state=tk.DISABLED)
        self.history_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)


    def _save_edited_employee(self, employee_to_edit):
        name = self.name_entry.get().strip()
        position = self.position_entry.get().strip()
        salary_str = self.salary_entry.get().strip()

        if not name or not position or not salary_str:
            messagebox.showerror("Input Error", "All fields must be filled.")
            return
        try:
            new_monthly_salary = float(salary_str)
            if new_monthly_salary < 0:
                messagebox.showerror("Input Error", "Monthly salary cannot be negative.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Monthly Salary must be a number.")
            return

        # Check for duplicate names (excluding the employee being edited)
        for emp in self.employees:
            if emp != employee_to_edit and emp.name.lower() == name.lower():
                messagebox.showwarning("Duplicate Employee", f"An employee with the name '{name}' already exists.")
                return

        # If monthly salary changes, ask to reset remaining or leave as is
        if new_monthly_salary != employee_to_edit.monthly_salary:
            confirm = messagebox.askyesno("Salary Change", "Monthly salary changed. Do you want to reset remaining balance to the new monthly salary?")
            if confirm:
                employee_to_edit.remaining_salary = new_monthly_salary

        employee_to_edit.name = name
        employee_to_edit.position = position
        employee_to_edit.monthly_salary = new_monthly_salary

        self.update_employee_listbox()
        self.clear_entry_fields()
        self.display_selected_employee_info() # Update info display
        messagebox.showinfo("Success", f"Employee '{name}' updated successfully.")
        self.save_data() # Save data after editing

        # Revert buttons to normal state
        self.add_button.config(text="Add Employee", command=self.add_employee)
        self.edit_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.pay_button.config(state=tk.NORMAL)
        self.history_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)

    def delete_employee(self):
        selected_employee = self.get_selected_employee()
        if not selected_employee:
            messagebox.showwarning("Selection Error", "Please select an employee to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected_employee.name}'?")
        if confirm:
            self.employees.remove(selected_employee)
            self.update_employee_listbox()
            self.clear_employee_info_display()
            messagebox.showinfo("Success", f"Employee '{selected_employee.name}' deleted.")
            self.save_data() # Save data after deleting

    def display_selected_employee_info(self, event=None):
        selected_employee = self.get_selected_employee()
        if selected_employee:
            self.info_name.config(text=f"Name: {selected_employee.name}")
            self.info_position.config(text=f"Position: {selected_employee.position}")
            self.info_monthly_salary.config(text=f"Monthly Salary: TMT {selected_employee.monthly_salary:.2f}")
            self.info_remaining_salary.config(text=f"Remaining Salary: TMT {selected_employee.remaining_salary:.2f}")
        else:
            self.clear_employee_info_display()

    def clear_employee_info_display(self):
        self.info_name.config(text="Name: ")
        self.info_position.config(text="Position: ")
        self.info_monthly_salary.config(text="Monthly Salary: ")
        self.info_remaining_salary.config(text="Remaining Salary: ")

    def record_payment(self):
        selected_employee = self.get_selected_employee()
        if not selected_employee:
            messagebox.showwarning("Selection Error", "Please select an employee to record a payment for.")
            return

        payment_amount_str = simpledialog.askstring("Record Payment", "Enter payment amount:", parent=self.master)
        if payment_amount_str is None: # User cancelled
            return

        try:
            payment_amount = float(payment_amount_str)
            if payment_amount <= 0:
                messagebox.showerror("Invalid Amount", "Payment amount must be positive.")
                return
        except ValueError:
            messagebox.showerror("Invalid Amount", "Payment amount must be a number.")
            return

        reason = simpledialog.askstring("Record Payment", "Enter reason for payment:", parent=self.master)
        if reason is None: # User cancelled
            return
        if not reason.strip():
            messagebox.showwarning("Missing Information", "Please provide a reason for the payment.")
            return

        if selected_employee.record_payment(payment_amount, reason):
            messagebox.showinfo("Payment Recorded", f"Payment of TMT {payment_amount:.2f} recorded for {selected_employee.name}.\nRemaining Salary: TMT {selected_employee.remaining_salary:.2f}")
            self.display_selected_employee_info() # Update the display
            self.save_data() # Save data after payment
        else:
            messagebox.showerror("Insufficient Funds", f"{selected_employee.name} does not have enough remaining salary for this payment.")

    def view_payment_history(self):
        selected_employee = self.get_selected_employee()
        if not selected_employee:
            messagebox.showwarning("Selection Error", "Please select an employee to view payment history.")
            return

        if not selected_employee.payment_history:
            messagebox.showinfo("No History", f"No payment history for {selected_employee.name}.")
            return

        history_text = f"Payment History for {selected_employee.name}:\n\n"
        for payment in selected_employee.payment_history:
            history_text += f"Date: {payment['date']}\nReason: {payment['reason']}\nAmount: TMT {payment['amount']:.2f}\n"
            history_text += "-" * 30 + "\n"

        # Create a new window to display history
        history_window = tk.Toplevel(self.master)
        history_window.title(f"Payment History - {selected_employee.name}")
        text_widget = tk.Text(history_window, wrap="word", width=60, height=20)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, history_text)
        text_widget.config(state=tk.DISABLED) # Make it read-only

    def export_employee_data(self):
        selected_employee = self.get_selected_employee()
        if not selected_employee:
            messagebox.showwarning("Selection Error", "Please select an employee to export data.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{selected_employee.name}_salary_data.txt"
        )
        if not file_path: # User cancelled the dialog
            return

        try:
            with open(file_path, "w") as f:
                f.write(f"--- Employee Salary Data ---\n")
                f.write(f"Name: {selected_employee.name}\n")
                f.write(f"Position: {selected_employee.position}\n")
                f.write(f"Monthly Salary: TMT {selected_employee.monthly_salary:.2f}\n")
                f.write(f"Remaining Salary: TMT {selected_employee.remaining_salary:.2f}\n")
                f.write("\n--- Payment History ---\n")
                if not selected_employee.payment_history:
                    f.write("No payment history.\n")
                else:
                    for payment in selected_employee.payment_history:
                        f.write(f"  Date: {payment['date']}\n  Reason: {payment['reason']}\n  Amount: TMT {payment['amount']:.2f}\n")
                        f.write("  --------------------\n")
            messagebox.showinfo("Export Successful", f"Data for {selected_employee.name} exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SalaryManagerApp(root)
    root.mainloop()

