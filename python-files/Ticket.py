import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import date

FILENAME = "tickets_gui_multiline.csv"

# Load tickets, auto-create CSV if missing
def load_tickets():
    tickets = []
    if not os.path.exists(FILENAME):
        # Create CSV with headers if it doesn't exist
        with open(FILENAME, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["ID","Date","BusinessName","Caller","Issue","Notes"])
            writer.writeheader()
    else:
        with open(FILENAME, "r", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tickets.append(row)
    return tickets


# Save tickets
def save_tickets(tickets):
    with open(FILENAME, "w", newline='') as f:
        fieldnames = ["ID","Date","BusinessName","Caller","Issue","Notes"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tickets)

# GUI App
class TicketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TechTicketingV1 by Mel")
        self.root.geometry("920x700")
        self.tickets = load_tickets()
        self.selected_ticket = None

        # --- Counters ---
        self.today = date.today().strftime("%Y-%m-%d")
        self.daily_count = 0
        self.total_count = len(self.tickets)

        # Grand total
        self.total_label = tk.Label(
            root,
            text=f"Total Tickets: {self.total_count}",
            font=("Arial", 18, "bold"),
            fg="blue",
            bg="lightyellow",
            padx=10, pady=5
        )
        self.total_label.grid(row=0, column=0, sticky="ne", padx=10, pady=10)

        # Daily counter
        self.counter_label = tk.Label(
            root,
            text="",
            font=("Arial", 18, "bold"),
            fg="red",
            bg="lightyellow",
            padx=10, pady=5
        )
        self.counter_label.grid(row=0, column=1, sticky="ne", padx=10, pady=10)
        self.update_daily_counter()       # initial update
        self.schedule_counter_update()    # auto-refresh every minute

        # --- Form fields ---
        labels = ["Date", "Business Name", "Caller", "Issue", "Notes"]
        self.entries = {}
        for i, label in enumerate(labels, start=1):  # start=1 to avoid counter row
            tk.Label(root, text=label, anchor='w', font=("Arial", 11)).grid(
                row=i, column=0, padx=8, pady=5, sticky='w')
            if label == "Notes":
                text = tk.Text(root, width=80, height=15, wrap='word')
                text.grid(row=i, column=1, padx=8, pady=5, sticky='w')
                self.entries[label] = text
            elif label == "Date":
                entry = tk.Entry(root, width=70)
                entry.grid(row=i, column=1, padx=8, pady=5, sticky='w')
                entry.insert(0, self.today)
                self.entries[label] = entry
            else:
                entry = tk.Entry(root, width=70)
                entry.grid(row=i, column=1, padx=8, pady=5, sticky='w')
                self.entries[label] = entry

        # --- Buttons ---
        button_frame = tk.Frame(root)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        tk.Button(button_frame, text="Save Ticket", width=18, command=self.add_ticket).grid(row=0, column=0, padx=30)
        tk.Button(button_frame, text="Update Ticket", width=18, command=self.update_ticket).grid(row=0, column=1, padx=30)
        tk.Button(button_frame, text="Delete Ticket", width=18, command=self.delete_ticket).grid(row=0, column=2, padx=30)
        tk.Button(button_frame, text="Add New Ticket", width=18, command=self.clear_fields).grid(row=0, column=3, padx=30)

        # --- Ticket list ---
        self.tree = ttk.Treeview(root, columns=("ID","Date","BusinessName","Caller","Issue"), show='headings', height=15)
        for col in ("ID","Date","BusinessName","Caller","Issue"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.refresh_tree()

    # --- Daily counter ---
    def update_daily_counter(self):
        today_str = date.today().strftime("%Y-%m-%d")
        if today_str != self.today:
            self.today = today_str
            self.daily_count = 0
        self.daily_count = sum(1 for t in self.tickets if t["Date"] == self.today)
        self.counter_label.config(text=f"Today's Tickets: {self.daily_count}")

    def schedule_counter_update(self):
        self.update_daily_counter()
        self.root.after(60000, self.schedule_counter_update)  # refresh every 60 sec

    # --- Form functions ---
    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in self.tickets:
            self.tree.insert("", "end", values=(t["ID"], t["Date"], t["BusinessName"], t["Caller"], t["Issue"]))

    def clear_fields(self):
        for key, entry in self.entries.items():
            if key == "Notes":
                entry.delete("1.0", tk.END)
            else:
                entry.delete(0, tk.END)
        self.selected_ticket = None

    def add_ticket(self):
        ticket_id = str(int(self.tickets[-1]["ID"]) + 1) if self.tickets else "1"
        ticket = {"ID": ticket_id}
        for key, entry in self.entries.items():
            if key == "Notes":
                ticket[key.replace(" ", "")] = entry.get("1.0", tk.END).strip() or "-"
            else:
                ticket[key.replace(" ", "")] = entry.get().strip() or "-"
        self.tickets.append(ticket)
        save_tickets(self.tickets)
        self.refresh_tree()
        self.update_daily_counter()
        self.total_count = len(self.tickets)
        self.total_label.config(text=f"Total Tickets: {self.total_count}")
        self.clear_fields()
        messagebox.showinfo("Success", f"Ticket {ticket_id} added!")

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        ticket_id = values[0]
        for t in self.tickets:
            if t["ID"] == ticket_id:
                self.selected_ticket = t
                break
        for key, entry in self.entries.items():
            if key == "Notes":
                entry.delete("1.0", tk.END)
                entry.insert(tk.END, self.selected_ticket.get(key.replace(" ", ""), ""))
            else:
                entry.delete(0, tk.END)
                entry.insert(0, self.selected_ticket.get(key.replace(" ", ""), ""))

    def update_ticket(self):
        if not self.selected_ticket:
            messagebox.showwarning("Select Ticket", "Please select a ticket to update.")
            return
        for key, entry in self.entries.items():
            if key == "Notes":
                self.selected_ticket[key.replace(" ", "")] = entry.get("1.0", tk.END).strip() or "-"
            else:
                self.selected_ticket[key.replace(" ", "")] = entry.get().strip() or "-"
        save_tickets(self.tickets)
        self.refresh_tree()
        self.update_daily_counter()
        self.total_count = len(self.tickets)
        self.total_label.config(text=f"Total Tickets: {self.total_count}")
        messagebox.showinfo("Updated", f"Ticket {self.selected_ticket['ID']} updated!")
        self.clear_fields()

    def delete_ticket(self):
        if not self.selected_ticket:
            messagebox.showwarning("Select Ticket", "Please select a ticket to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ticket {self.selected_ticket['ID']}?")
        if confirm:
            self.tickets.remove(self.selected_ticket)
            save_tickets(self.tickets)
            self.refresh_tree()
            self.update_daily_counter()
            self.total_count = len(self.tickets)
            self.total_label.config(text=f"Total Tickets: {self.total_count}")
            self.clear_fields()
            messagebox.showinfo("Deleted", f"Ticket {self.selected_ticket['ID']} deleted!")

# Run the GUI
root = tk.Tk()
app = TicketApp(root)
root.mainloop()
