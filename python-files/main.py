import tkinter as tk
from tkinter import messagebox, PhotoImage
import csv
import os

# Constants
QUEUE_FILE = 'patient_queue.txt'
CLINIC_NAME = 'Your Clinic Name'  # Replace with actual clinic name
DOCTOR_NAME = 'Dr. Your Name'    # Replace with actual doctor name
LOGO_PATH = 'clinic_logo.png'    # Replace with actual path to logo image (PNG format)

# Load queue from file
def load_queue():
    queue = []
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    queue.append({
                        'number': int(row[0]),
                        'name': row[1],
                        'age': int(row[2]),
                        'gender': row[3]
                    })
    return queue

# Save queue to file
def save_queue(queue):
    with open(QUEUE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        for patient in queue:
            writer.writerow([patient['number'], patient['name'], patient['age'], patient['gender']])

# Get next queue number
def get_next_number(queue):
    if not queue:
        return 1
    return max(p['number'] for p in queue) + 1

# Management Window Class
class ManagementWindow:
    def __init__(self, root, queue, display_window):
        self.root = root
        self.queue = queue
        self.display_window = display_window
        self.root.title("Queue Management")
        self.root.geometry("400x300")

        # Entries
        tk.Label(self.root, text="Name:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        tk.Label(self.root, text="Age:").pack()
        self.age_entry = tk.Entry(self.root)
        self.age_entry.pack()

        tk.Label(self.root, text="Gender (M/F/O):").pack()
        self.gender_entry = tk.Entry(self.root)
        self.gender_entry.pack()

        # Buttons
        tk.Button(self.root, text="Add Patient", command=self.add_patient).pack(pady=10)
        tk.Button(self.root, text="Call Next", command=self.call_next).pack(pady=10)

        # Queue Listbox
        self.queue_list = tk.Listbox(self.root, height=10, width=50)
        self.queue_list.pack()
        self.update_queue_list()

    def add_patient(self):
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_entry.get().strip().upper()

        if not name or not age_str or not gender:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            age = int(age_str)
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")
            return

        if gender not in ['M', 'F', 'O']:
            messagebox.showerror("Error", "Gender must be M, F, or O.")
            return

        number = get_next_number(self.queue)
        patient = {'number': number, 'name': name, 'age': age, 'gender': gender}
        self.queue.append(patient)
        save_queue(self.queue)
        self.update_queue_list()
        self.display_window.update_display()
        self.clear_entries()

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.gender_entry.delete(0, tk.END)

    def call_next(self):
        if not self.queue:
            messagebox.showinfo("Info", "No patients in queue.")
            return
        next_patient = self.queue.pop(0)
        messagebox.showinfo("Next Patient", f"Calling Patient {next_patient['number']}: {next_patient['name']}")
        save_queue(self.queue)
        self.update_queue_list()
        self.display_window.update_display()

    def update_queue_list(self):
        self.queue_list.delete(0, tk.END)
        for p in self.queue:
            self.queue_list.insert(tk.END, f"{p['number']}: {p['name']}, Age: {p['age']}, Gender: {p['gender']}")

# Display Window Class
class DisplayWindow:
    def __init__(self, root, queue):
        self.root = root
        self.queue = queue
        self.root.title("Patient Queue Display")
        self.root.geometry("600x800")  # Vertical aspect ratio (portrait)
        # self.root.attributes('-fullscreen', True)  # Uncomment for full screen

        # Clinic Name
        self.clinic_label = tk.Label(self.root, text=CLINIC_NAME, font=("Arial", 24, "bold"))
        self.clinic_label.pack(pady=20)

        # Clinic Logo
        if os.path.exists(LOGO_PATH):
            self.logo_image = PhotoImage(file=LOGO_PATH)
            self.logo_label = tk.Label(self.root, image=self.logo_image)
            self.logo_label.pack()
        else:
            tk.Label(self.root, text="Logo not found", font=("Arial", 12)).pack()

        # Doctor Name
        self.doctor_label = tk.Label(self.root, text=DOCTOR_NAME, font=("Arial", 18))
        self.doctor_label.pack(pady=10)

        # Next Patients Title
        tk.Label(self.root, text="Next Patients:", font=("Arial", 16, "bold")).pack(pady=20)

        # Next 3 Patients Labels
        self.patient_labels = []
        for i in range(3):
            label = tk.Label(self.root, text="", font=("Arial", 14))
            label.pack(pady=5)
            self.patient_labels.append(label)

        self.update_display()

    def update_display(self):
        for i in range(3):
            if i < len(self.queue):
                p = self.queue[i]
                self.patient_labels[i].config(text=f"Queue {p['number']}: {p['name']}")
            else:
                self.patient_labels[i].config(text="")

# Main
if __name__ == "__main__":
    queue = load_queue()

    display_root = tk.Tk()
    display_window = DisplayWindow(display_root, queue)

    management_root = tk.Toplevel(display_root)
    management_window = ManagementWindow(management_root, queue, display_window)

    display_root.mainloop()