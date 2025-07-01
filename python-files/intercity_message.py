
import tkinter as tk

def generate_message():
    day = entry_day.get()
    date = entry_date.get()
    from_where = entry_from.get()
    why = entry_why.get()
    reason = entry_reason.get()

    message = f"""Αγαπητοί,\n\nΘα θέλαμε να σας ενημερώσουμε για την ανάγκη που υπάρχει αύριο {day} {date} για μια κάρτα Intercity Λευκωσίας. Διαμένουσα του ΚΕΦ {from_where} πρέπει να παρευρεθεί στο {why} σχετικά με {reason}. Τα στοιχεία της αναγράφονται αναλυτικά πιο κάτω:\n\nΑναπτύχθηκε από τον Ibrahim. Καλή σας μέρα!"""

    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, message)

root = tk.Tk()
root.title("Δημιουργία Μηνύματος Intercity")

labels = ["Ημέρα:", "Ημερομηνία:", "Από:", "Πού:", "Λόγος:"]
entries = []

for i, label in enumerate(labels):
    tk.Label(root, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries.append(entry)

entry_day, entry_date, entry_from, entry_why, entry_reason = entries

btn = tk.Button(root, text="Δημιουργία Μηνύματος", command=generate_message)
btn.grid(row=5, column=0, columnspan=2, pady=10)

text_output = tk.Text(root, height=10, width=60)
text_output.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

root.mainloop()
