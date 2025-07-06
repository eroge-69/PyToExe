import csv
from datetime import datetime, date
import os

class EmployeeAttendanceTracker:
    def __init__(self):
        self.employees = {}
        self.attendance_records = {}
        self.salary_payments = {}
        self.load_data()

    def load_data(self):
        # Load employee data
        if os.path.exists('employees.csv'):
            with open('employees.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.employees[row['id']] = {
                        'name': row['name'],
                        'daily_rate': float(row['daily_rate']),
                        'total_paid': float(row.get('total_paid', '0'))
                    }

        # Load attendance records
        if os.path.exists('attendance.csv'):
            with open('attendance.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    emp_id = row['employee_id']
                    if emp_id not in self.attendance_records:
                        self.attendance_records[emp_id] = []
                    self.attendance_records[emp_id].append({
                        'date': datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        'status': row['status']
                    })

        # Load payment records
        if os.path.exists('payments.csv'):
            with open('payments.csv', 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    emp_id = row['employee_id']
                    if emp_id not in self.salary_payments:
                        self.salary_payments[emp_id] = []
                    self.salary_payments[emp_id].append({
                        'date': datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        'amount': float(row['amount']),
                        'description': row['description']
                    })

    def save_data(self):
        # Save employee data
        with open('employees.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'name', 'daily_rate', 'total_paid'])
            writer.writeheader()
            for emp_id, data in self.employees.items():
                writer.writerow({
                    'id': emp_id,
                    'name': data['name'],
                    'daily_rate': data['daily_rate'],
                    'total_paid': data['total_paid']
                })

        # Save attendance records
        with open('attendance.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['employee_id', 'date', 'status'])
            writer.writeheader()
            for emp_id, records in self.attendance_records.items():
                for record in records:
                    writer.writerow({
                        'employee_id': emp_id,
                        'date': record['date'].strftime('%Y-%m-%d'),
                        'status': record['status']
                    })

        # Save payment records
        with open('payments.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['employee_id', 'date', 'amount', 'description'])
            writer.writeheader()
            for emp_id, payments in self.salary_payments.items():
                for payment in payments:
                    writer.writerow({
                        'employee_id': emp_id,
                        'date': payment['date'].strftime('%Y-%m-%d'),
                        'amount': payment['amount'],
                        'description': payment['description']
                    })

    def add_employee(self, emp_id, name, daily_rate):
        if emp_id in self.employees:
            print(f"Employee with ID {emp_id} already exists.")
            return False
        
        self.employees[emp_id] = {
            'name': name,
            'daily_rate': daily_rate,
            'total_paid': 0.0
        }
        self.save_data()
        print(f"Employee {name} added successfully.")
        return True

    def record_attendance(self, emp_id, date_str, status):
        if emp_id not in self.employees:
            print(f"Employee with ID {emp_id} not found.")
            return False
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return False
        
        if date_obj > date.today():
            print("Cannot record attendance for future dates.")
            return False
        
        if emp_id not in self.attendance_records:
            self.attendance_records[emp_id] = []
            
        # Check if attendance already recorded for this date
        for record in self.attendance_records[emp_id]:
            if record['date'] == date_obj:
                print(f"Attendance already recorded for {date_str}. Updating status.")
                record['status'] = status
                self.save_data()
                return True
        
        self.attendance_records[emp_id].append({
            'date': date_obj,
            'status': status
        })
        self.save_data()
        print(f"Attendance recorded for {self.employees[emp_id]['name']} on {date_str}: {status}")
        return True

    def calculate_salary(self, emp_id, start_date_str, end_date_str):
        if emp_id not in self.employees:
            print(f"Employee with ID {emp_id} not found.")
            return None
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return None
        
        if start_date > end_date:
            print("Start date cannot be after end date.")
            return None
        
        if emp_id not in self.attendance_records:
            return {
                'full_days': 0,
                'half_days': 0,
                'first_half_days': 0,
                'second_half_days': 0,
                'absent_days': 0,
                'total_working_days': (end_date - start_date).days + 1,
                'amount_earned': 0.0,
                'amount_paid': self.employees[emp_id]['total_paid'],
                'amount_due': 0.0
            }
        
        full_days = 0
        first_half_days = 0
        second_half_days = 0
        absent_days = 0
        
        for record in self.attendance_records[emp_id]:
            if start_date <= record['date'] <= end_date:
                if record['status'].lower() == 'full':
                    full_days += 1
                elif record['status'].lower() == 'first_half':
                    first_half_days += 1
                elif record['status'].lower() == 'second_half':
                    second_half_days += 1
                elif record['status'].lower() == 'absent':
                    absent_days += 1
        
        half_days = first_half_days + second_half_days
        total_days = (end_date - start_date).days + 1
        unrecorded_days = total_days - (full_days + half_days + absent_days)
        
        daily_rate = self.employees[emp_id]['daily_rate']
        amount_earned = (full_days * daily_rate) + (half_days * daily_rate / 2)
        amount_paid = self.employees[emp_id]['total_paid']
        amount_due = amount_earned - amount_paid
        
        return {
            'full_days': full_days,
            'half_days': half_days,
            'first_half_days': first_half_days,
            'second_half_days': second_half_days,
            'absent_days': absent_days,
            'unrecorded_days': unrecorded_days,
            'total_working_days': total_days,
            'amount_earned': amount_earned,
            'amount_paid': amount_paid,
            'amount_due': amount_due
        }

    def record_payment(self, emp_id, amount, date_str, description="Salary payment"):
        if emp_id not in self.employees:
            print(f"Employee with ID {emp_id} not found.")
            return False
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return False
        
        if date_obj > date.today():
            print("Cannot record payment for future dates.")
            return False
        
        if emp_id not in self.salary_payments:
            self.salary_payments[emp_id] = []
            
        self.salary_payments[emp_id].append({
            'date': date_obj,
            'amount': amount,
            'description': description
        })
        
        self.employees[emp_id]['total_paid'] += amount
        self.save_data()
        print(f"Payment of {amount} recorded for {self.employees[emp_id]['name']} on {date_str}")
        return True

    def get_payment_history(self, emp_id):
        if emp_id not in self.salary_payments:
            return []
        
        return sorted(self.salary_payments[emp_id], key=lambda x: x['date'], reverse=True)

def main():
    tracker = EmployeeAttendanceTracker()
    
    while True:
        print("\nEmployee Attendance and Salary Tracker")
        print("1. Add Employee")
        print("2. Record Attendance")
        print("3. Calculate Salary")
        print("4. Record Payment")
        print("5. View Payment History")
        print("6. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            emp_id = input("Enter employee ID: ")
            name = input("Enter employee name: ")
            try:
                daily_rate = float(input("Enter daily rate: "))
                tracker.add_employee(emp_id, name, daily_rate)
            except ValueError:
                print("Invalid daily rate. Please enter a number.")
                
        elif choice == '2':
            emp_id = input("Enter employee ID: ")
            date_str = input("Enter date (YYYY-MM-DD): ")
            print("Attendance status options:")
            print("1. Full day")
            print("2. First half day")
            print("3. Second half day")
            print("4. Absent")
            status_choice = input("Select status (1-4): ")
            
            status_map = {
                '1': 'full',
                '2': 'first_half',
                '3': 'second_half',
                '4': 'absent'
            }
            
            if status_choice in status_map:
                tracker.record_attendance(emp_id, date_str, status_map[status_choice])
            else:
                print("Invalid status choice.")
                
        elif choice == '3':
            emp_id = input("Enter employee ID: ")
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            
            salary_info = tracker.calculate_salary(emp_id, start_date, end_date)
            if salary_info:
                print("\nSalary Calculation Results:")
                print(f"Full days: {salary_info['full_days']}")
                print(f"Half days: {salary_info['half_days']} (First half: {salary_info['first_half_days']}, Second half: {salary_info['second_half_days']})")
                print(f"Absent days: {salary_info['absent_days']}")
                print(f"Unrecorded days: {salary_info['unrecorded_days']}")
                print(f"Total working days in period: {salary_info['total_working_days']}")
                print(f"\nAmount earned: {salary_info['amount_earned']:.2f}")
                print(f"Amount paid: {salary_info['amount_paid']:.2f}")
                print(f"Amount due: {salary_info['amount_due']:.2f}")
                
        elif choice == '4':
            emp_id = input("Enter employee ID: ")
            try:
                amount = float(input("Enter payment amount: "))
                date_str = input("Enter payment date (YYYY-MM-DD): ")
                description = input("Enter payment description (optional): ") or "Salary payment"
                tracker.record_payment(emp_id, amount, date_str, description)
            except ValueError:
                print("Invalid amount. Please enter a number.")
                
        elif choice == '5':
            emp_id = input("Enter employee ID: ")
            payments = tracker.get_payment_history(emp_id)
            if payments:
                print("\nPayment History:")
                for payment in payments:
                    print(f"{payment['date']}: {payment['amount']:.2f} - {payment['description']}")
            else:
                print("No payment history found for this employee.")
                
        elif choice == '6':
            print("Exiting program. Data saved.")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()