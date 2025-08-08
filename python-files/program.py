import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from datetime import datetime, date
import os

# --- Dane użytkowników z historią (history jako lista słowników) ---
users = {
    "adam": {"password": "1234", "balance": 0.0, "history": []},
    "ewa":  {"password": "abcd", "balance": 0.0, "history": []},
    "jan":  {"password": "pass", "balance": 0.0, "history": []}
}

current_user = None

# --- Pomocniczne funkcje ---
def add_history_entry(username: str, amount: float):
    """Dodaje zapis do historii w postaci słownika z timestamp i amount."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users[username]["history"].append({"timestamp": ts, "amount": float(amount)})

def history_to_text(history):
    """Konwertuje historię (lista dictów lub stare stringi) na czytelny tekst."""
    lines = []
    for h in history:
        if isinstance(h, dict):
            lines.append(f"{h['timestamp']}: +{h['amount']:.2f} zł")
        else:
            # kompatybilność z poprzednimi formatami (stringami)
            lines.append(str(h))
    return "\n".join(lines)

def sum_history_amounts(history):
    """Sumuje kwoty z historii; obsługuje zarówno dicty jak i stringi (ostrożnie)."""
    total = 0.0
    for h in history:
        if isinstance(h, dict):
            total += float(h.get("amount", 0.0))
        else:
            # próbujemy wyciągnąć cyfrę ze stringa w formacie 'YYYY-...: +123.45 zł'
            s = str(h)
            if "+" in s:
                try:
                    part = s.split("+", 1)[1]
                    part = part.replace("zł", "").replace(",", ".").strip()
                    total += float(part)
                except Exception:
                    pass
    return total

# --- Funkcje akcji ---
def login():
    global current_user
    username = username_entry.get().strip().lower()   # przyjazne: ignorujemy przypadkowe wielkie litery
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Błąd", "Podaj login i hasło.")
        return

    if username in users and users[username]["password"] == password:
        current_user = username
        messagebox.showinfo("Sukces", f"Witaj, {username}!")
        show_main_menu()
    else:
        messagebox.showerror("Błąd", "Nieprawidłowy login lub hasło.")

def deposit():
    global current_user
    if not current_user:
        messagebox.showerror("Błąd", "Brak zalogowanego użytkownika.")
        return
    try:
        amount = simpledialog.askfloat("Wpłata", "Podaj kwotę do wpłaty:", minvalue=0.01)
        if amount is None:
            return
        users[current_user]["balance"] += float(amount)
        add_history_entry(current_user, amount)
        messagebox.showinfo("Wpłata", f"✅ Wpłacono {amount:.2f} zł.\nNowe saldo: {users[current_user]['balance']:.2f} zł")
    except Exception:
        messagebox.showerror("Błąd", "Nieprawidłowa kwota.")

def show_balance():
    if not current_user:
        messagebox.showerror("Błąd", "Brak zalogowanego użytkownika.")
        return
    balance = users[current_user]["balance"]
    messagebox.showinfo("Saldo", f"Saldo użytkownika {current_user}: {balance:.2f} zł")

def show_total_balance():
    total = sum(user["balance"] for user in users.values())
    today = date.today().strftime("%Y-%m-%d")
    messagebox.showinfo("Wspólne saldo",
                        f"📅 Data: {today}\n💰 Łączne saldo wszystkich użytkowników: {total:.2f} zł")

def logout():
    global current_user
    current_user = None
    main_menu_frame.pack_forget()
    login_frame.pack()

def show_history():
    if not current_user:
        messagebox.showerror("Błąd", "Brak zalogowanego użytkownika.")
        return
    history = users[current_user]["history"]
    text = history_to_text(history)
    if not text:
        messagebox.showinfo("Historia", "Brak wpłat.")
    else:
        # pokaż w okienku przewijalnym — użyj prostego okna z Text
        hist_win = tk.Toplevel(root)
        hist_win.title(f"Historia wpłat - {current_user}")
        txt = tk.Text(hist_win, width=60, height=20)
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", text)
        txt.config(state="disabled")

def generate_pdf_report():
    """Generuje PDF zawierający:
       - historię wpłat (data, kwota)
       - sumę wpłat
       - saldo końcowe użytkownika
       - wspólne saldo wszystkich użytkowników
    """
    if not current_user:
        messagebox.showerror("Błąd", "Musisz być zalogowany, aby wygenerować raport.")
        return

    # sprawdź, czy reportlab jest dostępny
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
    except Exception:
        messagebox.showerror(
            "Brak biblioteki",
            "Biblioteka 'reportlab' nie jest zainstalowana.\n\n"
            "Zainstaluj poleceniem:\n\npip install reportlab\n\n"
            "i uruchom program ponownie."
        )
        return

    history = users[current_user]["history"]
    today = date.today().strftime("%Y-%m-%d")
    # pozwól użytkownikowi wybrać miejsce zapisu i nazwę pliku
    default_fname = f"raport_{current_user}_{today}.pdf"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=default_fname,
        title="Zapisz raport PDF jako..."
    )
    if not file_path:
        return

    # budowa dokumentu
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph(f"Raport wpłat - {current_user}", styles["Title"]))
    content.append(Paragraph(f"Data generowania: {today}", styles["Normal"]))
    content.append(Spacer(1, 12))

    # Historia
    if not history:
        content.append(Paragraph("Brak wpłat.", styles["Normal"]))
    else:
        content.append(Paragraph("Historia wpłat:", styles["Heading2"]))
        for h in history:
            if isinstance(h, dict):
                line = f"{h['timestamp']}: +{h['amount']:.2f} zł"
            else:
                line = str(h)
            content.append(Paragraph(line, styles["Normal"]))
            content.append(Spacer(1, 4))

    content.append(Spacer(1, 12))

    # Suma wpłat użytkownika
    total_user_deposits = sum_history_amounts(history)
    content.append(Paragraph(f"Suma wpłat użytkownika: {total_user_deposits:.2f} zł", styles["Normal"]))

    # Saldo końcowe użytkownika
    content.append(Paragraph(f"Saldo końcowe użytkownika: {users[current_user]['balance']:.2f} zł", styles["Normal"]))

    # Wspólne saldo wszystkich użytkowników
    total_all = sum(user["balance"] for user in users.values())
    content.append(Paragraph(f"Wspólne saldo wszystkich użytkowników na dzień {today}: {total_all:.2f} zł", styles["Normal"]))

    try:
        doc.build(content)
        abs_path = os.path.abspath(file_path)
        messagebox.showinfo("Raport PDF", f"Raport zapisano jako:\n{abs_path}")
    except Exception as e:
        messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać raportu:\n{e}")

# --- Interfejs (GUI) ---
root = tk.Tk()
root.title("System kasowy")
root.geometry("420x520")

# Ekran logowania
login_frame = tk.Frame(root, padx=10, pady=10)

tk.Label(login_frame, text="🧾 System kasowy", font=('Arial', 18)).pack(pady=8)

tk.Label(login_frame, text="Login:").pack(anchor="w")
username_entry = tk.Entry(login_frame)
username_entry.pack(fill="x")

tk.Label(login_frame, text="Hasło:").pack(anchor="w", pady=(8,0))
password_entry = tk.Entry(login_frame, show="*")
password_entry.pack(fill="x")

tk.Button(login_frame, text="Zaloguj", width=20, command=login).pack(pady=12)
tk.Button(login_frame, text="Zobacz wspólne saldo (bez logowania)", width=30, command=show_total_balance).pack(pady=5)

login_frame.pack(fill="both", expand=True)

# Menu główne (po zalogowaniu)
main_menu_frame = tk.Frame(root, padx=10, pady=10)

tk.Label(main_menu_frame, text="📋 Menu główne", font=('Arial', 16)).pack(pady=8)
tk.Button(main_menu_frame, text="Wpłata", width=30, command=deposit).pack(pady=6)
tk.Button(main_menu_frame, text="Sprawdź saldo", width=30, command=show_balance).pack(pady=6)
tk.Button(main_menu_frame, text="Historia wpłat", width=30, command=show_history).pack(pady=6)
tk.Button(main_menu_frame, text="Generuj raport PDF", width=30, command=generate_pdf_report).pack(pady=6)
tk.Button(main_menu_frame, text="Wspólne saldo (wszyscy)", width=30, command=show_total_balance).pack(pady=6)
tk.Button(main_menu_frame, text="Wyloguj", width=30, command=logout).pack(pady=6)

def show_main_menu():
    login_frame.pack_forget()
    main_menu_frame.pack(fill="both", expand=True)

# --- Uruchomienie aplikacji ---
root.mainloop()