import sqlite3
from datetime import datetime

# Database initialization and helper functions
class CollegeDB:
    def __init__(self, db_name="college.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Students table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT
        )
        ''')

        # Courses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL UNIQUE,
            course_fees REAL NOT NULL
        )
        ''')

        # Enrollment table (many-to-many between students and courses)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollment (
            enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id),
            UNIQUE(student_id, course_id)
        )
        ''')

        # Fees Payment table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees_payment (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            amount_paid REAL NOT NULL,
            payment_date TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        )
        ''')

        # Results table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            marks REAL NOT NULL,
            grade TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id),
            UNIQUE(student_id, course_id)
        )
        ''')

        # Cash Book table: records of cash inflow/outflow
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cash_book (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL
        )
        ''')

        self.conn.commit()

    # Student related methods
    def add_student(self, name, email, phone):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO students (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
            self.conn.commit()
            print(f"Student '{name}' added successfully.")
        except sqlite3.IntegrityError:
            print("Error: Email must be unique. Student not added.")

    def list_students(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT student_id, name, email, phone FROM students')
        rows = cursor.fetchall()
        if not rows:
            print("No students found.")
        else:
            print("Students:")
            for r in rows:
                print(f"ID: {r[0]}, Name: {r[1]}, Email: {r[2]}, Phone: {r[3]}")

    # Course related methods
    def add_course(self, course_name, fees):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO courses (course_name, course_fees) VALUES (?, ?)', (course_name, fees))
            self.conn.commit()
            print(f"Course '{course_name}' added successfully.")
        except sqlite3.IntegrityError:
            print("Error: Course name must be unique.")

    def list_courses(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT course_id, course_name, course_fees FROM courses')
        rows = cursor.fetchall()
        if not rows:
            print("No courses found.")
        else:
            print("Courses:")
            for r in rows:
                print(f"ID: {r[0]}, Name: {r[1]}, Fees: {r[2]}")

    # Enrollment
    def enroll_student(self, student_id, course_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute('INSERT INTO enrollment (student_id, course_id) VALUES (?, ?)', (student_id, course_id))
            self.conn.commit()
            print(f"Student {student_id} enrolled in course {course_id} successfully.")
        except sqlite3.IntegrityError:
            print("Error: Student already enrolled in this course or invalid ID.")

    def list_enrollments(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT e.enrollment_id, s.name, c.course_name 
        FROM enrollment e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
        ''')
        rows = cursor.fetchall()
        if not rows:
            print("No enrollments found.")
        else:
            print("Enrollments:")
            for r in rows:
                print(f"Enrollment ID: {r[0]}, Student: {r[1]}, Course: {r[2]}")

    # Fees Payment
    def add_fees_payment(self, student_id, course_id, amount_paid):
        cursor = self.conn.cursor()

        # Validate that student is enrolled in the course
        cursor.execute('SELECT * FROM enrollment WHERE student_id=? AND course_id=?', (student_id, course_id))
        if not cursor.fetchone():
            print("Student is not enrolled in this course.")
            return

        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            'INSERT INTO fees_payment (student_id, course_id, amount_paid, payment_date) VALUES (?, ?, ?, ?)',
            (student_id, course_id, amount_paid, payment_date)
        )
        self.conn.commit()

        # Add entry to cash book
        description = f"Fees payment from student ID {student_id} for course ID {course_id}"
        cursor.execute('INSERT INTO cash_book (entry_date, description, amount) VALUES (?, ?, ?)',
                       (payment_date, description, amount_paid))
        self.conn.commit()

        print(f"Fees payment of amount {amount_paid} added for student {student_id} in course {course_id}.")
        # Generate receipt
        self.generate_fee_receipt(student_id, course_id, amount_paid, payment_date)

    def list_fees_payments(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT p.payment_id, s.name, c.course_name, p.amount_paid, p.payment_date
        FROM fees_payment p
        JOIN students s ON p.student_id = s.student_id
        JOIN courses c ON p.course_id = c.course_id
        ORDER BY p.payment_date DESC
        ''')
        rows = cursor.fetchall()
        if not rows:
            print("No fees payment records found.")
        else:
            print("Fees Payments:")
            for r in rows:
                print(f"Payment ID: {r[0]}, Student: {r[1]}, Course: {r[2]}, Amount: {r[3]}, Date: {r[4]}")

    # Result management
    def add_result(self, student_id, course_id, marks):
        cursor = self.conn.cursor()
        # Validate enrollment
        cursor.execute('SELECT * FROM enrollment WHERE student_id=? AND course_id=?', (student_id, course_id))
        if not cursor.fetchone():
            print("Student is not enrolled in this course.")
            return

        # Grade calculation (simple example)
        grade = self.calculate_grade(marks)

        # Insert or update result
        cursor.execute('SELECT * FROM results WHERE student_id=? AND course_id=?', (student_id, course_id))
        if cursor.fetchone():
            cursor.execute('UPDATE results SET marks=?, grade=? WHERE student_id=? AND course_id=?',
                           (marks, grade, student_id, course_id))
            print("Result updated.")
        else:
            cursor.execute('INSERT INTO results (student_id, course_id, marks, grade) VALUES (?, ?, ?, ?)',
                           (student_id, course_id, marks, grade))
            print("Result added.")
        self.conn.commit()

    def calculate_grade(self, marks):
        if marks >= 90:
            return 'A+'
        elif marks >= 80:
            return 'A'
        elif marks >= 70:
            return 'B+'
        elif marks >= 60:
            return 'B'
        elif marks >= 50:
            return 'C'
        else:
            return 'F'

    def list_results(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT r.result_id, s.name, c.course_name, r.marks, r.grade
        FROM results r
        JOIN students s ON r.student_id = s.student_id
        JOIN courses c ON r.course_id = c.course_id
        ''')
        rows = cursor.fetchall()
        if not rows:
            print("No results found.")
        else:
            print("Results:")
            for r in rows:
                print(f"Result ID: {r[0]}, Student: {r[1]}, Course: {r[2]}, Marks: {r[3]}, Grade: {r[4]}")

    # Cash Book (simple income list)
    def list_cash_book(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT entry_id, entry_date, description, amount FROM cash_book ORDER BY entry_date DESC')
        rows = cursor.fetchall()
        if not rows:
            print("No cash book entries found.")
        else:
            print("Cash Book Entries:")
            for r in rows:
                print(f"ID: {r[0]}, Date: {r[1]}, Description: {r[2]}, Amount: {r[3]}")

    # Fees receipt generator (prints simple receipt)
    def generate_fee_receipt(self, student_id, course_id, amount_paid, payment_date):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM students WHERE student_id=?', (student_id,))
        student = cursor.fetchone()
        cursor.execute('SELECT course_name FROM courses WHERE course_id=?', (course_id,))
        course = cursor.fetchone()

        if student is None or course is None:
            print("Invalid student or course ID for receipt generation.")
            return

        receipt_text = f"""
        -------------------------------
        COLLEGE FEES RECEIPT
        -------------------------------
        Date: {payment_date}
        
        Student Name: {student[0]}
        Course: {course[0]}
        
        Amount Paid: ${amount_paid:.2f}
        
        Thank you for your payment.
        -------------------------------
        """
        filename = f"receipt_{student_id}_{course_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        with open(filename, "w") as file:
            file.write(receipt_text.strip())
        print(f"Receipt generated: {filename}")


# CLI Menu-driven interface
def main_menu():
    db = CollegeDB()
    while True:
        print("\n--- College Management System ---")
        print("1. Add Student")
        print("2. List Students")
        print("3. Add Course")
        print("4. List Courses")
        print("5. Enroll Student in Course")
        print("6. List Enrollments")
        print("7. Add Fees Payment")
        print("8. List Fees Payments")
        print("9. Add Result")
        print("10. List Results")
        print("11. View Cash Book")
        print("12. Exit")

        choice = input("Enter choice: ")
        if choice == '1':
            name = input("Student Name: ")
            email = input("Student Email: ")
            phone = input("Student Phone: ")
            db.add_student(name, email, phone)

        elif choice == '2':
            db.list_students()

        elif choice == '3':
            name = input("Course Name: ")
            fees = float(input("Course Fees: "))
            db.add_course(name, fees)

        elif choice == '4':
            db.list_courses()

        elif choice == '5':
            student_id = int(input("Student ID: "))
            course_id = int(input("Course ID: "))
            db.enroll_student(student_id, course_id)

        elif choice == '6':
            db.list_enrollments()

        elif choice == '7':
            student_id = int(input("Student ID: "))
            course_id = int(input("Course ID: "))
            amount = float(input("Amount Paid: "))
            db.add_fees_payment(student_id, course_id, amount)

        elif choice == '8':
            db.list_fees_payments()

        elif choice == '9':
            student_id = int(input("Student ID: "))
            course_id = int(input("Course ID: "))
            marks = float(input("Marks: "))
            db.add_result(student_id, course_id, marks)

        elif choice == '10':
            db.list_results()

        elif choice == '11':
            db.list_cash_book()

        elif choice == '12':
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()