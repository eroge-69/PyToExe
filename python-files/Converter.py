import csv
from icalendar import Calendar, Event, vText
from datetime import datetime
import os
import uuid
import tkinter as tk
from tkinter import messagebox

def csv_to_ics():
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Find all CSV files in the folder
    csv_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.csv')]

    if not csv_files:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "No CSV files found in the folder.")
        return

    converted_files = []

    for csv_file in csv_files:
        full_csv_path = os.path.join(script_dir, csv_file)

        try:
            with open(full_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header row

                cal = Calendar()

                for row in reader:
                    event = Event()

                    # Expecting date in DD/MM/YYYY and time in 24-hour HH:MM
                    start_datetime = datetime.strptime(row[0] + ' ' + row[1], '%d/%m/%Y %H:%M')
                    end_datetime = datetime.strptime(row[2] + ' ' + row[3], '%d/%m/%Y %H:%M')
                    summary = row[4]
                    location = row[5]
                    description = row[6]

                    event.add('summary', summary)
                    event.add('location', location)
                    event.add('description', description)
                    event.add('dtstart', start_datetime)
                    event.add('dtend', end_datetime)
                    event.add('uid', vText(str(uuid.uuid4())))

                    cal.add_component(event)

                # Output .ics file
                ics_filename = os.path.splitext(csv_file)[0] + '.ics'
                ics_path = os.path.join(script_dir, ics_filename)

                with open(ics_path, 'wb') as f:
                    f.write(cal.to_ical())

                converted_files.append(ics_filename)

        except Exception as e:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to convert '{csv_file}':\n{e}")
            continue

    # Show final success message with list of converted files
    if converted_files:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Success", "Converted the following files:\n" + "\n".join(converted_files))
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "No CSV files were successfully converted.")

if __name__ == "__main__":
    csv_to_ics()
