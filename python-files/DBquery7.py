import tkinter as tk
import sqlite3
import os

# Try to import Pillow for photo support
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Path to your museum database
DB_PATH = r"C:\Users\Greg\Desktop\Museum\Database\SQLite\Query\museum.db"

# Connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ===== Functions =====

def search_person():
    """Search for people by last name and show results list."""
    query = search_var.get().strip()
    if not query:
        return

    results_list.delete(0, tk.END)

    cursor.execute("""
        SELECT personID, firstName, middleName, lastName, dateOfBirth
        FROM Person
        WHERE lastName LIKE ?
        ORDER BY lastName, firstName
    """, (f"%{query}%",))

    for row in cursor.fetchall():
        pid, fname, mname, lname, dob = row
        full_name = " ".join([n for n in [fname, mname, lname] if n])
        results_list.insert(tk.END, f"{pid} - {full_name} (b. {dob})")

def show_person_details(event=None):
    """Open fullscreen popup with detailed person info."""
    selection = results_list.curselection()
    if not selection:
        return

    selected = results_list.get(selection[0])
    person_id = int(selected.split(" - ")[0])
    display_details(person_id)

def display_details(person_id):
    """Display details about the person in a fullscreen popup."""
    details_win = tk.Toplevel(root)
    details_win.attributes("-fullscreen", True)
    details_win.title("Person Details")

    # Allow ESC key to exit detail view
    details_win.bind("<Escape>", lambda e: details_win.destroy())

    container = tk.Frame(details_win, padx=20, pady=20)
    container.pack(fill="both", expand=True)

    # ===== Person =====
    cursor.execute("""
        SELECT firstName, middleName, lastName, dateOfBirth, birthplace, notes
        FROM Person WHERE personID = ?
    """, (person_id,))
    person = cursor.fetchone()

    if person:
        person_frame = tk.LabelFrame(container, text=" Person Information ", bd=3, font=("Arial", 14, "bold"))
        person_frame.pack(fill="x", pady=10)

        full_name = " ".join([p for p in person[:3] if p])
        tk.Label(person_frame, text=f"Name: {full_name}", anchor="w").pack(fill="x")
        tk.Label(person_frame, text=f"Date of Birth: {person[3]}", anchor="w").pack(fill="x")
        tk.Label(person_frame, text=f"Birthplace: {person[4]}", anchor="w").pack(fill="x")
        tk.Label(person_frame, text=f"Notes: {person[5]}", anchor="w", wraplength=1000, justify="left").pack(fill="x")

    # ===== Occupations =====
    cursor.execute("""
        SELECT title, employer, startDate, endDate, notes
        FROM Occupation WHERE personID = ?
    """, (person_id,))
    occupations = cursor.fetchall()

    if occupations:
        occ_frame = tk.LabelFrame(container, text=" Occupation(s) ", bd=3, font=("Arial", 14, "bold"))
        occ_frame.pack(fill="x", pady=10)
        for occ in occupations:
            title, employer, start, end, notes = occ
            tk.Label(occ_frame, text=f"{title} at {employer} ({start} - {end})").pack(anchor="w")
            if notes:
                tk.Label(occ_frame, text=f"Notes: {notes}", wraplength=1000, justify="left").pack(anchor="w")

    # ===== Siblings =====
    cursor.execute("""
        SELECT P.firstName, P.middleName, P.lastName
        FROM Sibling S
        JOIN Person P ON S.relatedSiblingID = P.personID
        WHERE S.personID = ?
    """, (person_id,))
    siblings = cursor.fetchall()

    if siblings:
        sib_frame = tk.LabelFrame(container, text=" Siblings ", bd=3, font=("Arial", 14, "bold"))
        sib_frame.pack(fill="x", pady=10)
        for sib in siblings:
            name = " ".join([n for n in sib if n])
            tk.Label(sib_frame, text=name).pack(anchor="w")

    # ===== Photo =====
    cursor.execute("SELECT filePath FROM Photo WHERE personID = ?", (person_id,))
    photo = cursor.fetchone()
    if photo and PIL_AVAILABLE:
        try:
            if os.path.exists(photo[0]):
                img = Image.open(photo[0])
                img = img.resize((400, 400))
                img_tk = ImageTk.PhotoImage(img)
                tk.Label(container, image=img_tk).pack(pady=10)
                details_win.image = img_tk  # prevent garbage collection
            else:
                tk.Label(container, text=f"Photo not found: {photo[0]}", fg="red").pack()
        except Exception as e:
            tk.Label(container, text=f"Photo error: {e}", fg="red").pack()

    # ===== Back button =====
    tk.Button(container, text="Back to Search", command=details_win.destroy,
              font=("Arial", 16, "bold"), bg="lightgray").pack(pady=20)

# ===== Main App Window =====
root = tk.Tk()
root.attributes("-fullscreen", True)
root.title("Museum Visitor Lookup")

# ESC key closes main app
root.bind("<Escape>", lambda e: root.destroy())

search_var = tk.StringVar()

search_frame = tk.Frame(root, padx=20, pady=20)
search_frame.pack(fill="x")

tk.Label(search_frame, text="Search by Last Name:", font=("Arial", 16)).pack(side="left")
search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Arial", 16), width=30)
search_entry.pack(side="left", padx=10)
tk.Button(search_frame, text="Search", command=search_person, font=("Arial", 16)).pack(side="left")

results_list = tk.Listbox(root, font=("Arial", 14))
results_list.pack(fill="both", expand=True, padx=20, pady=20)
results_list.bind("<Double-1>", show_person_details)

root.mainloop()
    