import tkinter as tk
from tkinter import messagebox
import webbrowser

# ---- Offline Short Notes ---- #
notes = {
    "Physics": {
        "Physical World": "Scope of physics, role in technology & society.",
        "Units and Measurement": "SI units, dimensional analysis, accuracy & errors.",
        "Motion in a Straight Line": "Displacement, velocity, acceleration, equations of motion."
    },
    "Chemistry": {
        "Some Basic Concepts of Chemistry": "Mole concept, stoichiometry, percentage composition.",
        "Structure of Atom": "Dalton, Thomson, Rutherford, Bohr models, quantum numbers.",
        "Classification of Elements": "Mendeleev, Modern Periodic Law, periodic trends."
    },
    "Biology": {
        "The Living World": "Definition of living, taxonomy, classification, nomenclature.",
        "Biological Classification": "Five kingdoms: Monera, Protista, Fungi, Plantae, Animalia.",
        "Plant Kingdom": "Algae, Bryophytes, Pteridophytes, Gymnosperms, Angiosperms."
    },
    "Mathematics": {
        "Sets": "Sets, subsets, power set, universal set, Venn diagrams.",
        "Relations and Functions": "Ordered pairs, domain, codomain, range.",
        "Trigonometric Functions": "Angles, trigonometric ratios, identities."
    }
}

# ---- NCERT PDF Links ---- #
ncert_links = {
    "Physics": "https://ncert.nic.in/textbook.php?keph1=0",
    "Chemistry": "https://ncert.nic.in/textbook.php?kech1=0",
    "Biology": "https://ncert.nic.in/textbook.php?kebo1=0",
    "Mathematics": "https://ncert.nic.in/textbook.php?kemh1=0",
    "Practicals": "https://ncert.nic.in/labmanual.php"
}

# ---- Functions ---- #
def show_subject(subject):
    chapter_window = tk.Toplevel(root)
    chapter_window.title(subject)

    tk.Label(chapter_window, text=f"{subject} Chapters", font=("Arial", 12, "bold")).pack(pady=5)

    # Show chapter buttons
    for chapter, content in notes.get(subject, {}).items():
        btn = tk.Button(chapter_window, text=chapter,
                        command=lambda c=content, ch=chapter: show_notes(ch, c))
        btn.pack(pady=3, fill="x")

    # Add link to full NCERT book
    if subject in ncert_links:
        tk.Button(chapter_window, text=f"📖 Open Full NCERT {subject} Book",
                  command=lambda: webbrowser.open(ncert_links[subject])).pack(pady=10)

def show_notes(chapter, content):
    messagebox.showinfo(chapter, content + "\n\n📘 Read full NCERT for details.")

def open_practicals():
    webbrowser.open(ncert_links["Practicals"])

# ---- Main Window ---- #
root = tk.Tk()
root.title("NCERT Study Explorer - Class 11")
root.geometry("400x400")

tk.Label(root, text="📚 Class 11 NCERT Study App", font=("Arial", 14, "bold")).pack(pady=10)

for subject in ["Physics", "Chemistry", "Biology", "Mathematics"]:
    btn = tk.Button(root, text=subject, width=25, height=2,
                    command=lambda s=subject: show_subject(s))
    btn.pack(pady=5)

tk.Button(root, text="🧪 Practicals (Physics/Chemistry/Bio)", width=30, height=2,
          command=open_practicals).pack(pady=15)

root.mainloop()
