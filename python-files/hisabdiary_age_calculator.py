import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_age():
    try:
        birth_date = datetime.strptime(entry.get(), "%d-%m-%Y")
        now = datetime.now()
        if birth_date > now:
            messagebox.showerror("Invalid Date", "Birth date can't be in the future!")
            return

        delta = relativedelta(now, birth_date)
        total_seconds = int((now - birth_date).total_seconds())

        years = delta.years
        months = delta.months
        days = delta.days
        hours = now.hour
        minutes = now.minute
        seconds = now.second

        result_label.config(text=f"""
Age Result:
🗓 {years} Years
📆 {months} Months
📅 {days} Days
⏰ {hours} Hours
🕐 {minutes} Minutes
🧭 {seconds} Seconds
        """, justify='left', fg='darkgreen')
    except Exception as e:
        messagebox.showerror("Error", "Enter your birth date in format DD-MM-YYYY")

# GUI Setup
root = tk.Tk()
root.title("HisabDiary - Age Calculator")
root.geometry("400x350")
root.resizable(False, False)
root.configure(bg='white')

tk.Label(root, text="🎂 Enter your Date of Birth (DD-MM-YYYY):", font=('Arial', 12, 'bold'), bg='white').pack(pady=15)
entry = tk.Entry(root, font=('Arial', 14), width=20, justify='center')
entry.pack(pady=5)

tk.Button(root, text="Calculate Age", command=calculate_age, font=('Arial', 12, 'bold'), bg="navy", fg="white").pack(pady=15)

result_label = tk.Label(root, text="", font=('Arial', 12), bg='white')
result_label.pack(pady=10)

root.mainloop()