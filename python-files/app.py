import sqlite3
#csv feature to open student data in excell
import csv

# Connect to database (creates file if not exists)
conn = sqlite3.connect("Uigt_registration.db")
cursor = conn.cursor()

# Create table if not exists to store student data in database
#the table is students.
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    course TEXT NOT NULL,
    phone_number INTEGER NOT NULL,
    duration TEXT NOT NULL
)
""")
conn.commit()

def register_student():
    print("\n=== Register Student ===")
    first_name = input("Enter First Name: ")
    last_name = input("Enter Last Name: ")
    course = input("Enter Course Name: ")
    phone_number = input("Enter Phone number: ")

    while True:
        duration = input("Enter Course Duration (long/short): ").lower()
        if duration in ["long", "short"]:
            break
        else:
            print("Invalid input! Please type 'long' or 'short'.")
    
    cursor.execute(
        "INSERT INTO students (first_name, last_name, course, phone_number, duration) VALUES (?, ?, ?, ?, ?)",
        (first_name, last_name, course,phone_number,duration)
    )
    conn.commit()
    print("\n✅ Registration Successful!")

def view_students():
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    print("\n=== Registered Students ===")
    if not students:
        print("No students registered yet.")
    for student in students:
        print(f"ID: {student[0]}, Name: {student[1]} {student[2]}, Course: {student[3]}, phone_number: {student[4]}, Duration: {student[5]}")

def search_student():
    print("\n=== Search Student ===")
    print("1. Search by ID")
    print("2. Search by Name")
    choice = input("Choose option: ")
    
    if choice == "1":
        student_id = input("Enter Student ID: ")
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        result = cursor.fetchone()
        if result:
            print(f"\nFound → ID: {result[0]}, Name: {result[1]} {result[2]}, Course: {result[3]}, phone_number {result[4]}, Duration: {result[5]}")
        else:
            print("❌ No student found with that ID.")
    
    elif choice == "2":
        name = input("Enter First or Last Name: ")
        cursor.execute("SELECT * FROM students WHERE first_name LIKE ? OR last_name LIKE ?", 
                       (f"%{name}%", f"%{name}%"))
        results = cursor.fetchall()
        if results:
            print("\nSearch Results:")
            for student in results:
                print(f"ID: {student[0]}, Name: {student[1]} {student[2]}, Course: {student[3]}, phone_number: {student[4]}, Duration: {student[5]}")
        else:
            print("❌ No student found with that name.")
    else:
        print("Invalid option.")

        #for updating uigt student's information using student_id

def update_student():
    student_id = input("\nEnter Student ID to Update: ")
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    #if the student_id is not found, error message is printed
    if not student:
        print("❌ Student not found.")
        return
    #if the student_id is found,new information will be asked for as new update 
    print(f"\nEditing → ID: {student[0]}, Name: {student[1]} {student[2]}, Course: {student[3]},phone_number: {student[4]}, Duration: {student[5]}")
    
    new_first = input("Enter New First Name (leave blank to keep current): ") or student[1]
    new_last = input("Enter New Last Name (leave blank to keep current): ") or student[2]
    new_course = input("Enter New Course (leave blank to keep current): ") or student[3]
    new_phone_number = input("Enter New Phone Number (leave blank to keep current): ") or student[4]
    
    while True:
        new_duration = input("Enter New Duration (long/short, leave blank to keep current): ").lower()
        if new_duration in ["long", "short", ""]:
            if new_duration == "":
                new_duration = student[5]
            break
        else:
            print("Invalid input! Please type 'long', 'short', or leave blank.")
    
    cursor.execute("""
        UPDATE students 
        SET first_name = ?, last_name = ?, course = ?, phone_number = ?, duration = ?
        WHERE id = ?
    """, (new_first, new_last, new_course, new_phone_number, new_duration, student_id))
    conn.commit()
    print("✅ Student updated successfully!")

#to delete student information using student_id
#it will first ask for student_id

def delete_student():
    student_id = input("\nEnter Student ID to Delete: ")
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    
    #if student with that student_id is not found,error message will be displayed
    if not student:
        print("❌ Student not found.")
        return
    
    #but if student with that id is found,user will be asked to approve data deletion

    confirm = input(f"Are you sure you want to delete {student[1]} {student[2]}? (y/n): ").lower()
    if confirm == "y":
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

        #when data is successfully deleted

        print("✅ Student deleted successfully!")

        #or else is the deleting was cancelled and not approved
    else:
        print("❌ Delete cancelled.")

def export_to_csv():
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    
    if not students:
        print("❌ No students to export.")
        return
    
    #if you want to export a cvs file into excell.

    with open("students_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "First Name", "Last Name", "Course","phone_number","Duration"])  # header
        writer.writerows(students)

    #on successfull export of student.csv file.

    print("✅ Students exported successfully to students_export.csv")

# Main loop: for user to choose options.
while True:
    print("\n=== School Registration Menu ===")
    print("1. Register Student")
    print("2. View Students")
    print("3. Search Student")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Export Students to CSV")
    print("7. Exit")
    choice = input("Choose an option: ")

    #each choice and what it does.
    
    if choice == "1": #register new student
        register_student()
    elif choice == "2": #view student
        view_students()
    elif choice == "3": #3 to search student
        search_student()
    elif choice == "4": #update student
        update_student()
    elif choice == "5": #to delete student
        delete_student()
    elif choice == "6": #5 is to export ascsv file
        export_to_csv()
    elif choice == "7": #is to exit
        print("Goodbye!")
        break
    else:
        print("Invalid choice, try again.")
