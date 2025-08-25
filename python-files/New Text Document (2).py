import csv
import os

FILE_NAME = "D:\\outpatient data\\outpatient_data.csv"

# Initialize file with headers if it doesn't exist
if not os.path.exists(FILE_NAME):
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Patient ID", "Name", "Age", "Gender", "Diagnosis", "Visit date", "Start time", "End time", "Remarks"])

def add_patient():
    print("\n--- Add New Patient Record ---")
    patient_id = input("Patient ID: ")
    name = input("Name: ")
    age = input("Age: ")
    gender = input("Gender: ")
    diagnosis = input("Diagnosis: ")
    visit_date = input("Visit Date (YYYY-MM-DD): ")
    start_time = input("Start time: ")
    end_time = input("End time: ")
    remarks = input("Remarks: ")

    with open(FILE_NAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([patient_id, name, age, gender, diagnosis, visit_date, start_time, end_time, remarks])
    print("✅ Record added successfully.\n")

def view_patients():
    print("\n--- Outpatient Records ---")
    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

        if len(rows) <= 1:
            print("No records found.\n")
            return

        header = rows[0]
        print("{:<12} {:<20} {:<5} {:<8} {:<25} {:<12} {:<12} {:<12} {:<30}".format(*header))
        print("-" * 140)

        for row in rows[1:]:
            print("{:<12} {:<20} {:<5} {:<8} {:<25} {:<12} {:<12} {:<12} {:<30}".format(*row))

def search_patient_by_name():
    print("\n--- Search Patient Records ---")
    search_name = input("Enter patient name to search: ").strip().lower()

    found = False
    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)

        header = rows[0]
        print("{:<12} {:<20} {:<5} {:<8} {:<25} {:<12} {:<12} {:<12} {:<30}".format(*header))
        print("-" * 140)

        for row in rows[1:]:
            if row[1].strip().lower() == search_name:
                print("{:<12} {:<20} {:<5} {:<8} {:<25} {:<12} {:<12} {:<12} {:<30}".format(*row))
                found = True

    if not found:
        print("❌ No records found for that name.\n")
    else:
        print()

def edit_patient_record():
    print("\n--- Edit Patient Record ---")
    patient_id = input("Enter Patient ID to edit: ").strip()

    updated_rows = []
    found = False

    with open(FILE_NAME, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        header = rows[0]
        updated_rows.append(header)

        for row in rows[1:]:
            if row[0].strip() == patient_id:
                found = True
                print("Current record:")
                print("{:<12} {:<20} {:<5} {:<8} {:<25} {:<12} {:<12} {:<12} {:<30}".format(*row))

                print("\nEnter new values (leave blank to keep current):")
                row[1] = input(f"Name [{row[1]}]: ") or row[1]
                row[2] = input(f"Age [{row[2]}]: ") or row[2]
                row[3] = input(f"Gender [{row[3]}]: ") or row[3]
                row[4] = input(f"Diagnosis [{row[4]}]: ") or row[4]
                row[5] = input(f"Visit Date [{row[5]}]: ") or row[5]
                row[6] = input(f"Start Time [{row[6]}]: ") or row[6]
                row[7] = input(f"End Time [{row[7]}]: ") or row[7]
                row[8] = input(f"Remarks [{row[8]}]: ") or row[8]

            updated_rows.append(row)

    if found:
        with open(FILE_NAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(updated_rows)
        print("✅ Record updated successfully.\n")
    else:
        print("❌ No record found with that Patient ID.\n")

def main():
    while True:
        print("📋 Outpatient Data Management")
        print("1. Add New Patient")
        print("2. View All Records")
        print("3. Exit")
        print("4. Get Patient Record")
        print("5. Edit Patient Record")
        choice = input("Enter your choice (1/2/3/4/5): ")

        if choice == '1':
            add_patient()
        elif choice == '2':
            view_patients()
        elif choice == '3':
            print("👋 Exiting program.")
            break
        elif choice == '4':
            search_patient_by_name()
        elif choice == '5':
            edit_patient_record()
        else:
            print("❌ Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
