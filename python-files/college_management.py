import sqlite3
import datetime

class CollegeDB:
    def __init__(self, dbname='college.db'):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        self.setup_tables()

    def setup_tables(self):
        # Students Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT,
                email TEXT UNIQUE,
                phone TEXT
            )
        ''')

        # Courses Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                duration TEXT,
                fee REAL
            )
        ''')

        # Enrollments Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                enrollment_date TEXT,
                FOREIGN KEY(student_id) REFERENCES students(student_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            )
        ''')

        # Fees Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fees (
                fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                amount_paid REAL,
                payment_date TEXT,
                receipt_no TEXT UNIQUE,
                FOREIGN KEY(student_id) REFERENCES students(student_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            )
        ''')

        # Results Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                course_id INTEGER,
                marks REAL,
                grade TEXT,
                FOREIGN KEY(student_id) REFERENCES students(student_id),
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
            )
        ''')

        # Cash Book Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cashbook (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                amount REAL,
                transaction_date TEXT
            )
        ''')
        self.conn.commit()

    # --- Student Methods ---
    def add_student(self, name, dob, email, phone):
        try:
            self.cursor.execute('''
                INSERT INTO students(name,dob,email,phone)
                VALUES (?, ?, ?, ?)
            ''', (name, dob, email, phone))
            self.conn.commit()
            print(f"Student '{name}' added successfully.")
        except sqlite3.IntegrityError:
            print("Error: Email must be unique!")

    def list_students(self):
        self.cursor.execute('SELECT * FROM students')
        students = self.cursor.fetchall()
        if not students:
            print("No students found.")
            return
        print("Student List:")
        print("ID  | Name           | DOB        | Email               | Phone")
        print("-"*60)
        for s in students:
            print(f"{s[0]:<4}| {s[1]:<14}| {s[2]:<11}| {s[3]:<20}| {s[4]}")

    # --- Course Methods ---
    def add_course(self, name, duration, fee):
        self.cursor.execute('''
            INSERT INTO courses(name, duration, fee)
            VALUES (?, ?, ?)
        ''', (name, duration, fee))
        self.conn.commit()
        print(f"Course '{name}' added successfully.")

    def list_courses(self):
        self.cursor.execute('SELECT * FROM courses')
        courses = self.cursor.fetchall()
        if not courses:
            print("No courses found.")
            return
        print("Course List:")
        print("ID  | Name           | Duration  | Fee")
        print("-"*45)
        for c in courses:
            print(f"{c[0]:<4}| {c[1]:<14}| {c[2]:<10}| {c[3]}")

    # --- Enrollment ---
    def enroll_student(self, student_id, course_id):
        enroll_date = datetime.date.today().isoformat()
        self.cursor.execute('''
            SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?
        ''', (student_id, course_id))
        if self.cursor.fetchone():
            print("Student already enrolled in this course.")
            return
        self.cursor.execute('''
            INSERT INTO enrollments(student_id, course_id, enrollment_date)
            VALUES (?, ?, ?)
        ''', (student_id, course_id, enroll_date))
        self.conn.commit()
        print(f"Student {student_id} enrolled in course {course_id}.")

    def list_enrollments(self):
        query = '''
            SELECT e.enrollment_id, s.name, c.name, e.enrollment_date
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN courses c ON e.course_id = c.course_id
        '''
        self.cursor.execute(query)
        enrollments = self.cursor.fetchall()
        if not enrollments:
            print("No enrollments found.")
            return
        print("Enrollments:")
        print("Enroll ID | Student Name    | Course Name     | Enrollment Date")
        print("-"*60)
        for e in enrollments:
            print(f"{e[0]:<9} | {e[1]:<14} | {e[2]:<14} | {e[3]}")

    # --- Fees and Receipt Generation ---
    def pay_fee(self, student_id, course_id, amount_paid):
        payment_date = datetime.date.today().isoformat()
        # Generate receipt no as "RCPT" + timestamp + studentid + courseid
        receipt_no = f"RCPT{int(datetime.datetime.now().timestamp())}{student_id}{course_id}"
        self.cursor.execute('''
            INSERT INTO fees(student_id, course_id, amount_paid, payment_date, receipt_no)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, course_id, amount_paid, payment_date, receipt_no))
        self.conn.commit()
        # Add to cashbook
        desc = f"Fee payment by student_id {student_id} for course_id {course_id}, receipt {receipt_no}"
        self.add_cashbook_entry(desc, amount_paid)
        print(f"Payment recorded. Receipt No: {receipt_no}")

    def generate_receipt(self, receipt_no):
        self.cursor.execute('''
            SELECT f.receipt_no, s.name, c.name, f.amount_paid, f.payment_date
            FROM fees f
            JOIN students s ON f.student_id = s.student_id
            JOIN courses c ON f.course_id = c.course_id
            WHERE f.receipt_no = ?
        ''', (receipt_no,))
        receipt = self.cursor.fetchone()
        if receipt:
            print("\n----- Fee Receipt -----")
            print(f"Receipt No: {receipt[0]}")
            print(f"Student Name: {receipt[1]}")
            print(f"Course Name: {receipt[2]}")
            print(f"Amount Paid: ${receipt[3]:.2f}")
            print(f"Payment Date: {receipt[4]}")
            print("-----------------------\n")
        else:
            print("Receipt not found.")

    # --- Results Management ---
    def add_result(self, student_id, course_id, marks, grade):
        # Check if result exists for student-course; update if yes
        self.cursor.execute('''
            SELECT * FROM results WHERE student_id = ? AND course_id = ?
        ''', (student_id, course_id))
        if self.cursor.fetchone():
            self.cursor.execute('''
                UPDATE results SET marks = ?, grade = ? WHERE student_id = ? AND course_id = ?
            ''', (marks, grade, student_id, course_id))
            print("Result updated.")
        else:
            self.cursor.execute('''
                INSERT INTO results(student_id, course_id, marks, grade)
                VALUES (?, ?, ?, ?)
            ''', (student_id, course_id, marks, grade))
            print("Result added.")
        self.conn.commit()

    def view_results(self, student_id):
        self.cursor.execute('''
            SELECT c.name, r.marks, r.grade FROM results r
            JOIN courses c ON r.course_id = c.course_id
            WHERE r.student_id = ?
        ''', (student_id,))
        results = self.cursor.fetchall()
        if not results:
            print("No results found for this student.")
            return
        print(f"Results for Student ID {student_id}:")
        print("Course Name     | Marks | Grade")
        print("-"*30)
        for r in results:
            print(f"{r[0]:<14} | {r[1]:<5} | {r[2]}")

    # --- Cashbook (Financial Transactions) ---
    def add_cashbook_entry(self, description, amount):
        transaction_date = datetime.date.today().isoformat()
        self.cursor.execute('''
            INSERT INTO cashbook(description, amount, transaction_date)
            VALUES (?, ?, ?)
        ''', (description, amount, transaction_date))
        self.conn.commit()

    def view_cashbook(self):
        self.cursor.execute('SELECT * FROM cashbook ORDER BY transaction_date DESC')
        entries = self.cursor.fetchall()
        if not entries:
            print("Cash book is empty.")
            return
        print("Cash Book Transactions:")
        print("ID | Description                                  | Amount   | Date")
        print("-"*70)
        for e in entries:
            print(f"{e[0]:<2} | {e[1]:<40} | ${e[2]:<7.2f} | {e[3]}")

    def close(self):
        self.conn.close()


# CLI Application to demonstrate:

def main():
    db = CollegeDB()

    menu = '''
    College Management System
    
    1. Add Student
    2. List Students
    3. Add Course
    4. List Courses
    5. Enroll Student in Course
    6. List Enrollments
    7. Pay Fees
    8. Generate Fee Receipt
    9. Add / Update Result
    10. View Student Results
    11. View Cash Book
    0. Exit
    '''

    while True:
        print(menu)
        choice = input("Enter choice: ").strip()
        if choice == '1':
            name = input("Enter student name: ")
            dob = input("Enter DOB (YYYY-MM-DD): ")
            email = input("Enter email: ")
            phone = input("Enter phone number: ")
            db.add_student(name, dob, email, phone)
        elif choice == '2':
            db.list_students()
        elif choice == '3':
            course_name = input("Enter course name: ")
            duration = input("Enter duration (e.g. 6 months): ")
            fee = float(input("Enter fee amount: "))
            db.add_course(course_name, duration, fee)
        elif choice == '4':
            db.list_courses()
        elif choice == '5':
            db.list_students()
            student_id = int(input("Enter student id to enroll: "))
            db.list_courses()
            course_id = int(input("Enter course id: "))
            db.enroll_student(student_id, course_id)
        elif choice == '6':
            db.list_enrollments()
        elif choice == '7':
            db.list_students()
            student_id = int(input("Enter student id: "))
            db.list_courses()
            course_id = int(input("Enter course id: "))
            amount = float(input("Enter amount paid: "))
            db.pay_fee(student_id, course_id, amount)
        elif choice == '8':
            receipt_no = input("Enter receipt number: ")
            db.generate_receipt(receipt_no)
        elif choice == '9':
            db.list_students()
            student_id = int(input("Enter student id: "))
            db.list_courses()
            course_id = int(input("Enter course id: "))
            marks = float(input("Enter marks: "))
            grade = input("Enter grade: ")
            db.add_result(student_id, course_id, marks, grade)
        elif choice == '10':
            db.list_students()
            student_id = int(input("Enter student id: "))
            db.view_results(student_id)
        elif choice == '11':
            db.view_cashbook()
        elif choice == '0':
            print("Exiting application.")
            db.close()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()