import sqlite3
from datetime import datetime, date
import hashlib

class HospitalManagementSystem:
    def __init__(self):
        self.conn = sqlite3.connect('hospital.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.current_user = None
        
    def create_tables(self):
        # Users table (for staff)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL
            )
        ''')
        
        # Patients table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Appointments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status TEXT DEFAULT 'Scheduled',
                reason TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        ''')
        
        # Medical records table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                visit_date DATE NOT NULL,
                diagnosis TEXT,
                prescription TEXT,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (doctor_id) REFERENCES users (id)
            )
        ''')
        
        # Insert default admin user if not exists
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
        if self.cursor.fetchone()[0] == 0:
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute(
                "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                ('admin', hashed_password, 'admin', 'System Administrator')
            )
            self.conn.commit()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        print("=== Hospital Management System Login ===")
        username = input("Username: ")
        password = input("Password: ")
        
        hashed_password = self.hash_password(password)
        self.cursor.execute(
            "SELECT id, username, role, full_name FROM users WHERE username=? AND password=?",
            (username, hashed_password)
        )
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'full_name': user[3]
            }
            print(f"Welcome, {user[3]} ({user[2]})!")
            return True
        else:
            print("Invalid username or password.")
            return False
    
    def add_patient(self):
        if not self.current_user:
            print("Please log in first.")
            return
            
        print("\n=== Add New Patient ===")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        dob = input("Date of Birth (YYYY-MM-DD): ")
        gender = input("Gender (M/F/O): ").upper()
        phone = input("Phone: ")
        email = input("Email: ")
        address = input("Address: ")
        
        try:
            self.cursor.execute(
                '''INSERT INTO patients 
                (first_name, last_name, date_of_birth, gender, phone, email, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (first_name, last_name, dob, gender, phone, email, address)
            )
            self.conn.commit()
            print("Patient added successfully!")
        except Exception as e:
            print(f"Error adding patient: {e}")
    
    def schedule_appointment(self):
        if not self.current_user:
            print("Please log in first.")
            return
            
        print("\n=== Schedule Appointment ===")
        
        # List patients
        self.cursor.execute("SELECT id, first_name, last_name FROM patients")
        patients = self.cursor.fetchall()
        if not patients:
            print("No patients found. Please add a patient first.")
            return
            
        print("Patients:")
        for patient in patients:
            print(f"{patient[0]}: {patient[1]} {patient[2]}")
        
        patient_id = input("Select Patient ID: ")
        
        # List doctors
        self.cursor.execute("SELECT id, full_name FROM users WHERE role='doctor'")
        doctors = self.cursor.fetchall()
        if not doctors:
            print("No doctors found.")
            return
            
        print("Doctors:")
        for doctor in doctors:
            print(f"{doctor[0]}: {doctor[1]}")
        
        doctor_id = input("Select Doctor ID: ")
        appointment_date = input("Appointment Date (YYYY-MM-DD): ")
        appointment_time = input("Appointment Time (HH:MM): ")
        reason = input("Reason for visit: ")
        
        try:
            self.cursor.execute(
                '''INSERT INTO appointments 
                (patient_id, doctor_id, appointment_date, appointment_time, reason) 
                VALUES (?, ?, ?, ?, ?)''',
                (patient_id, doctor_id, appointment_date, appointment_time, reason)
            )
            self.conn.commit()
            print("Appointment scheduled successfully!")
        except Exception as e:
            print(f"Error scheduling appointment: {e}")
    
    def add_medical_record(self):
        if not self.current_user or self.current_user['role'] not in ['doctor', 'admin']:
            print("Access denied. Doctor or admin privileges required.")
            return
            
        print("\n=== Add Medical Record ===")
        
        # List patients
        self.cursor.execute("SELECT id, first_name, last_name FROM patients")
        patients = self.cursor.fetchall()
        if not patients:
            print("No patients found.")
            return
            
        print("Patients:")
        for patient in patients:
            print(f"{patient[0]}: {patient[1]} {patient[2]}")
        
        patient_id = input("Select Patient ID: ")
        visit_date = input("Visit Date (YYYY-MM-DD): ")
        diagnosis = input("Diagnosis: ")
        prescription = input("Prescription: ")
        notes = input("Notes: ")
        
        try:
            self.cursor.execute(
                '''INSERT INTO medical_records 
                (patient_id, doctor_id, visit_date, diagnosis, prescription, notes) 
                VALUES (?, ?, ?, ?, ?, ?)''',
                (patient_id, self.current_user['id'], visit_date, diagnosis, prescription, notes)
            )
            self.conn.commit()
            print("Medical record added successfully!")
        except Exception as e:
            print(f"Error adding medical record: {e}")
    
    def view_patients(self):
        if not self.current_user:
            print("Please log in first.")
            return
            
        print("\n=== Patient List ===")
        self.cursor.execute("SELECT * FROM patients")
        patients = self.cursor.fetchall()
        
        if not patients:
            print("No patients found.")
            return
            
        for patient in patients:
            print(f"ID: {patient[0]}, Name: {patient[1]} {patient[2]}, DOB: {patient[3]}, Gender: {patient[4]}")
            print(f"Phone: {patient[5]}, Email: {patient[6]}")
            print(f"Address: {patient[7]}, Registered: {patient[8]}")
            print("-" * 40)
    
    def main_menu(self):
        while True:
            print("\n=== Hospital Management System ===")
            print("1. Add Patient")
            print("2. Schedule Appointment")
            print("3. Add Medical Record")
            print("4. View Patients")
            print("5. Logout")
            print("6. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.add_patient()
            elif choice == '2':
                self.schedule_appointment()
            elif choice == '3':
                self.add_medical_record()
            elif choice == '4':
                self.view_patients()
            elif choice == '5':
                self.current_user = None
                print("Logged out successfully.")
                if not self.login():
                    break
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

# Run the system
if __name__ == "__main__":
    hospital_system = HospitalManagementSystem()
    if hospital_system.login():
        hospital_system.main_menu()