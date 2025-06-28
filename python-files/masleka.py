import tkinter as tk
from tkinter import messagebox
import time
import random
from datetime import datetime

# --- הגדרות ---
LOG_FILE = "transactions_log.txt" # שם קובץ הלוג הלא מאובטח

# --- פונקציות לוגיות ---

def log_transaction(card_details, status):
    """
    !!! פונקציית אבטחה מסוכנת במכוון !!!
    שומרת את כל פרטי העסקה, כולל פרטי אשראי מלאים ו-CVV,
    בקובץ טקסט רגיל (plaintext).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # יצירת רשומת לוג עם כל הפרטים הרגישים
    log_entry = (
        f"--- Transaction Attempt ---\n"
        f"Timestamp: {timestamp}\n"
        f"Card Holder: {card_details['holder']}\n"
        f"Card Number: {card_details['number']}\n" # שמירת מספר מלא - חולשה!
        f"Expiry Date: {card_details['expiry']}\n"
        f"CVV: {card_details['cvv']}\n" # !!! שמירת CVV - חולשה קריטית !!!
        f"Amount: {card_details['amount']} ILS\n"
        f"Status: {status}\n"
        f"---------------------------\n\n"
    )
    
    try:
        # פתיחת הקובץ במצב 'a' (append) כדי להוסיף את הרשומה לסוף הקובץ
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"שגיאה בכתיבה לקובץ הלוג: {e}")


def process_payment():
    """
    פונקציה זו מדמה את תהליך הסליקה.
    אוספת נתונים, מבצעת ולידציה בסיסית, מתעדת את הניסיון לקובץ,
    ומציגה הודעת הצלחה או כישלון.
    """
    card_details = {
        "holder": entry_card_holder.get(),
        "number": entry_card_number.get(),
        "expiry": entry_expiry_date.get(),
        "cvv": entry_cvv.get(),
        "amount": entry_amount.get()
    }

    # בדיקות ולידציה בסיסיות
    if not all(card_details.values()):
        messagebox.showerror("שגיאה", "יש למלא את כל השדות!")
        return

    if not card_details["number"].isdigit() or len(card_details["number"]) != 16:
        messagebox.showerror("שגיאה", "מספר כרטיס לא תקין (נדרשות 16 ספרות).")
        return

    if not card_details["cvv"].isdigit() or len(card_details["cvv"]) != 3:
        messagebox.showerror("שגיאה", "CVV לא תקין (נדרשות 3 ספרות).")
        return

    try:
        float(card_details["amount"])
    except ValueError:
        messagebox.showerror("שגיאה", "הסכום חייב להיות מספר.")
        return

    # הדמיית תהליך התקשורת
    status_label.config(text="מעבד תשלום...", fg="orange")
    root.update_idletasks()
    time.sleep(2)

    # הדמיית קבלת תשובה אקראית
    is_approved = random.choice([True, False])
    status = "אושר" if is_approved else "נדחה"

    # !!! כאן מתבצעת הפעולה הלא מאובטחת !!!
    # תיעוד ניסיון התשלום עם כל הפרטים הרגישים לקובץ טקסט
    log_transaction(card_details, status)

    if is_approved:
        messagebox.showinfo("אישור", f"התשלום בסך {card_details['amount']} ₪ אושר בהצלחה!\n(הפרטים נשמרו בקובץ {LOG_FILE})")
        status_label.config(text="התשלום אושר", fg="green")
        clear_fields()
    else:
        messagebox.showerror("סירוב", f"התשלום נדחה על ידי חברת האשראי.\n(הפרטים נשמרו בקובץ {LOG_FILE})")
        status_label.config(text="התשלום נדחה", fg="red")


def clear_fields():
    """ מנקה את כל שדות הקלט """
    entry_card_holder.delete(0, tk.END)
    entry_card_number.delete(0, tk.END)
    entry_expiry_date.delete(0, tk.END)
    entry_cvv.delete(0, tk.END)
    entry_amount.delete(0, tk.END)


# --- הגדרת הממשק הגרפי (GUI) ---
root = tk.Tk()
root.title("מערכת סליקה לא מאובטחת - מעבדת סייבר")
root.geometry("420x350")
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(expand=True, fill="both")

labels_texts = ["שם בעל הכרטיס:", "מספר כרטיס אשראי (16 ספרות):", "תוקף (MM/YY):", "CVV (3 ספרות):", "סכום לתשלום (₪):"]
entries = []
for i, text in enumerate(labels_texts):
    label = tk.Label(main_frame, text=text, anchor="e")
    label.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
    entry = tk.Entry(main_frame, justify="right")
    entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
    entries.append(entry)

entry_card_holder, entry_card_number, entry_expiry_date, entry_cvv, entry_amount = entries

pay_button = tk.Button(main_frame, text="בצע תשלום (לא מאובטח!)", command=process_payment, bg="#D32F2F", fg="white", font=("Helvetica", 12, "bold"))
pay_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

status_label = tk.Label(main_frame, text="מוכן לקבלת תשלום", font=("Helvetica", 10), fg="gray")
status_label.grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()

