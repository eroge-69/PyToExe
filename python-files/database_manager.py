
import sqlite3

class DatabaseManager:
    def __init__(self, db_name="school_management.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        tables = {
            "students": """
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    date_of_birth TEXT,
                    gender TEXT,
                    address TEXT,
                    city_id INTEGER,
                    class_id INTEGER,
                    roll_number TEXT UNIQUE NOT NULL,
                    admission_date TEXT,
                    parent_contact_number TEXT,
                    parent_whatsapp_number TEXT
                )""",
            "parents": """
                CREATE TABLE IF NOT EXISTS parents (
                    parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    father_name TEXT,
                    mother_name TEXT,
                    contact_number TEXT,
                    whatsapp_number TEXT,
                    email TEXT
                )""",
            "classes": """
                CREATE TABLE IF NOT EXISTS classes (
                    class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT UNIQUE NOT NULL
                )""",
            "subjects": """
                CREATE TABLE IF NOT EXISTS subjects (
                    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_name TEXT UNIQUE NOT NULL
                )""",
            "fee_heads": """
                CREATE TABLE IF NOT EXISTS fee_heads (
                    fee_head_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fee_head_name TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL
                )""",
            "fee_payments": """
                CREATE TABLE IF NOT EXISTS fee_payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    fee_head_id INTEGER NOT NULL,
                    payment_date TEXT NOT NULL,
                    paid_amount REAL NOT NULL,
                    payment_month TEXT NOT NULL,
                    is_full_payment INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (fee_head_id) REFERENCES fee_heads(fee_head_id)
                )""",
            "attendance": """
                CREATE TABLE IF NOT EXISTS attendance (
                    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    attendance_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )""",
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    user_role TEXT NOT NULL
                )""",
            "cities": """
                CREATE TABLE IF NOT EXISTS cities (
                    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT UNIQUE NOT NULL
                )""",
            "sms_log": """
                CREATE TABLE IF NOT EXISTS sms_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    parent_contact TEXT,
                    message_type TEXT,
                    message_content TEXT,
                    timestamp TEXT,
                    status TEXT,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )"""
        }

        for table_name, create_sql in tables.items():
            try:
                self.cursor.execute(create_sql)
                self.conn.commit()
                print(f"Table '{table_name}' created or already exists.")
            except sqlite3.Error as e:
                print(f"Error creating table '{table_name}': {e}")

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            return False

    def fetch_all(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fetch all error: {e}")
            return []

    def fetch_one(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Fetch one error: {e}")
            return None

if __name__ == "__main__":
    db_manager = DatabaseManager()
    # You can add some initial data insertion here for testing purposes
    # For example, adding a default admin user
    # db_manager.execute_query("INSERT INTO users (username, password_hash, user_role) VALUES (?, ?, ?)", ("admin", "hashed_password", "Admin"))
    db_manager.disconnect()
    print("Database setup complete.")



