import customtkinter as ctk
from tkinter import messagebox
import pyodbc
from datetime import datetime

# Цветовая схема кнопок в стиле "византия"
button_style = {
    "fg_color": "#702963",      # византия
    "hover_color": "#5A1E4A",   # чуть темнее для наведения
    "text_color": "white"       # белый текст
}

# Подключение к БД
conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=DESKTOP-O62EQ2K;"
    "Database=TicketsDB;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

ctk.set_appearance_mode("light")


app = ctk.CTk()
app.title("Карточка заявки")
app.geometry("900x750")

current_user = None
tickets = []  # список заявок текущего пользователя
ticket_label = None

categories = [
    "Программа или оборудование не работает или работает неправильно",
    "Необходимо внести изменение в функционал программы",
    "Необходимо установить оборудование, программное обеспечение"
]


def format_ticket_number(num):
    return str(num).zfill(8)


def get_next_ticket_number():
    cursor.execute("SELECT ISNULL(MAX(id), 0) + 1 FROM Tickets")
    next_id = cursor.fetchone()[0]
    return next_id


def save_ticket():
    global current_user, ticket_label

    if not current_user:
        messagebox.showerror("Ошибка", "Сначала необходимо войти в систему.")
        return

    internal = gor_number.get().strip()
    mobile = cell_number.get().strip()
    address = address_entry.get().strip()
    content = content_text.get("0.0", "end").strip()
    category = category_combo.get().strip()

    if not internal or not mobile or not address or not content or not category:
        messagebox.showerror("Ошибка", "Заполните все обязательные поля.")
        return

    # Получаем куратора из БД для текущего пользователя
    curator = None

    executor = ""
    status = "Новая"
    date = datetime.now()

    cursor.execute("""
        INSERT INTO Tickets (address, curator, executor, category, status, date, applicant, content, mobile_phone, internal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (address, curator, executor, category, status, date, current_user, content, mobile, internal))

    conn.commit()

    cursor.execute("SELECT MAX(id) FROM Tickets")
    ticket_id = cursor.fetchone()[0]

   # ticket_label.configure(text=f"№Заявки: {format_ticket_number(int(ticket_id))}")
    messagebox.showinfo("Сохранено", f"Заявка №{format_ticket_number(int(ticket_id))} успешно сохранена!")


def build_ticket_table():
    # Создаем новое окно с таблицей заявок пользователя
    tickets_win = ctk.CTkToplevel()
    tickets_win.title("Мои заявки")
    tickets_win.geometry("1100x500")

    headers = ["ID", "Кабинет", "Куратор", "Исполнитель", "Категория", "Статус", "Дата"]
    for col, h in enumerate(headers):
        lbl = ctk.CTkLabel(tickets_win, text=h, font=("Arial", 12, "bold"))
        lbl.grid(row=0, column=col, padx=10, pady=5)  # Добавлен padx=10

    for row_idx, t in enumerate(tickets, start=1):
        ctk.CTkLabel(tickets_win, text=t["id"]).grid(row=row_idx, column=0, padx=10)
        ctk.CTkLabel(tickets_win, text=t["address"]).grid(row=row_idx, column=1, padx=10)
        ctk.CTkLabel(tickets_win, text=t["curator"]).grid(row=row_idx, column=2, padx=10)
        ctk.CTkLabel(tickets_win, text=t["executor"]).grid(row=row_idx, column=3, padx=10)
        ctk.CTkLabel(tickets_win, text=t["category"]).grid(row=row_idx, column=4, padx=10)
        ctk.CTkLabel(tickets_win, text=t["status"]).grid(row=row_idx, column=5, padx=10)
        ctk.CTkLabel(tickets_win, text=t["date"]).grid(row=row_idx, column=6, padx=10)



def open_profile():
    global current_user, tickets
    if not current_user:
        messagebox.showwarning("Профиль", "Вы не авторизованы")
        return

    profile_win = ctk.CTkToplevel()
    profile_win.title("Профиль")
    profile_win.geometry("400x400")

    cursor.execute("SELECT name, email FROM Users WHERE name=?", current_user)
    user_data = cursor.fetchone()

    ctk.CTkLabel(profile_win, text=f"Пользователь: {user_data.name}").pack(pady=5)
    ctk.CTkLabel(profile_win, text=f"Email: {user_data.email}").pack(pady=5)

    new_name_entry = ctk.CTkEntry(profile_win, placeholder_text="Новое имя")
    new_name_entry.pack(pady=5)

    old_password_entry = ctk.CTkEntry(profile_win, placeholder_text="Старый пароль", show="*")
    old_password_entry.pack(pady=5)

    new_password_entry = ctk.CTkEntry(profile_win, placeholder_text="Новый пароль", show="*")
    new_password_entry.pack(pady=5)

    def update_profile():
        global current_user
        new_name = new_name_entry.get().strip()
        old_pass = old_password_entry.get().strip()
        new_pass = new_password_entry.get().strip()

        cursor.execute("SELECT password FROM Users WHERE name=?", current_user)
        db_pass = cursor.fetchone()[0]

        if new_name:
            cursor.execute("UPDATE Users SET name=? WHERE name=?", new_name, current_user)
            current_user = new_name

        if old_pass and new_pass:
            if old_pass == db_pass:
                cursor.execute("UPDATE Users SET password=? WHERE name=?", new_pass, current_user)
            else:
                messagebox.showerror("Ошибка", "Старый пароль неверен")
                return

        conn.commit()
        messagebox.showinfo("Успех", "Профиль обновлён")
        profile_win.destroy()

    ctk.CTkButton(profile_win, text="Сохранить", command=update_profile, **button_style).pack(pady=10)

    def view_user_tickets():
        global tickets
        tickets.clear()

        try:
            cursor.execute("""
                SELECT id, address, curator, executor, category, status, date
                FROM Tickets
                WHERE applicant = ?
            """, (current_user,))
            for row in cursor.fetchall():
                tickets.append({
                    "id": row.id,
                    "address": row.address,
                    "curator": row.curator,
                    "executor": row.executor,
                    "category": row.category,
                    "status": row.status,
                    "date": str(row.date),
                })
            build_ticket_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заявки:\n{e}")

    ctk.CTkButton(profile_win, text="Мои заявки", command=view_user_tickets, **button_style).pack(pady=10)


def open_login_window():
    global current_user

    login_win = ctk.CTkToplevel()
    login_win.title("Вход")
    login_win.geometry("300x200")

    username_entry = ctk.CTkEntry(login_win, placeholder_text="Email")
    username_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(login_win, placeholder_text="Пароль", show="*")
    password_entry.pack(pady=10)

    def attempt_login():
        global current_user
        email = username_entry.get().strip()
        password = password_entry.get().strip()
        cursor.execute("SELECT name, email FROM Users WHERE email=? AND password=?", email, password)
        row = cursor.fetchone()
        if row:
            current_user = row.name
            messagebox.showinfo("Успех", "Вход выполнен")
            login_win.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверный email или пароль")

    ctk.CTkButton(login_win, text="Войти", command=attempt_login, **button_style).pack(pady=10)


def open_registration_window():
    reg_win = ctk.CTkToplevel()
    reg_win.title("Регистрация")
    reg_win.geometry("300x250")

    username_entry = ctk.CTkEntry(reg_win, placeholder_text="ФИО")
    username_entry.pack(pady=10)

    email_entry = ctk.CTkEntry(reg_win, placeholder_text="Email")
    email_entry.pack(pady=10)

    password_entry = ctk.CTkEntry(reg_win, placeholder_text="Пароль", show="*")
    password_entry.pack(pady=10)

    def register_user():
        username = username_entry.get().strip()
        email = email_entry.get().strip()
        password = password_entry.get().strip()
        try:
            cursor.execute("INSERT INTO Users (name, email, password) VALUES (?, ?, ?)", username, email, password)
            conn.commit()
            messagebox.showinfo("Успех", "Регистрация выполнена")
            reg_win.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Пользователь уже существует или другая ошибка:\n{e}")

    ctk.CTkButton(reg_win, text="Зарегистрироваться", command=register_user, **button_style).pack(pady=10)


# Интерфейс
button_y = 10
button_spacing = 120

ctk.CTkButton(app, text="Сохранить", command=save_ticket, **button_style).place(x=10 + 0 * button_spacing, y=button_y)
ctk.CTkButton(app, text="Профиль", command=open_profile, **button_style).place(x=10 + 1 * button_spacing, y=button_y)
ctk.CTkButton(app, text="Вход", command=open_login_window, **button_style).place(x=10 + 2 * button_spacing, y=button_y)
ctk.CTkButton(app, text="Регистрация", command=open_registration_window, **button_style).place(x=10 + 3 * button_spacing, y=button_y)


#ticket_label = ctk.CTkLabel(app, text="№Заявки: " + format_ticket_number(get_next_ticket_number()))
#ticket_label.place(x=10, y=50)

ctk.CTkLabel(app, text="Вн. номер").place(x=10, y=70)
gor_number = ctk.CTkEntry(app, width=200)
gor_number.place(x=150, y=70)

ctk.CTkLabel(app, text="Сотовый").place(x=10, y=100)
cell_number = ctk.CTkEntry(app, width=200)
cell_number.place(x=150, y=100)

ctk.CTkLabel(app, text="Кабинет").place(x=10, y=130)
address_entry = ctk.CTkEntry(app, width=300)
address_entry.place(x=150, y=130)

ctk.CTkLabel(app, text="Содержание").place(x=10, y=160)
content_text = ctk.CTkTextbox(app, width=600, height=100)
content_text.place(x=150, y=160)

ctk.CTkLabel(app, text="Категория").place(x=10, y=280)
category_combo = ctk.CTkComboBox(app, width=600, values=categories)
category_combo.place(x=150, y=280)

app.mainloop()
