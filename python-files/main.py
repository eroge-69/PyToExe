import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os, json, base64, sys, random
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# ---------------- AES / RSA ----------------
def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()
    return private_key, public_key

def save_private_key(private_key, path):
    with open(path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

def load_private_key(path):
    if not os.path.isfile(path):
        messagebox.showerror("Ошибка", f"Файл приватного ключа {path} не найден. Программа будет закрыта.")
        sys.exit(1)
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def encrypt_aes_key_rsa(aes_key, public_key):
    return public_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

def decrypt_aes_key_rsa(encrypted_key, private_key):
    return private_key.decrypt(
        encrypted_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

def encrypt_data_aes(data: dict):
    key = os.urandom(32)  # AES-256
    iv = os.urandom(16)
    json_bytes = json.dumps(data).encode()
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(json_bytes) + encryptor.finalize()
    return key, iv, ct

def decrypt_data_aes(ciphertext, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    json_bytes = decryptor.update(ciphertext) + decryptor.finalize()
    return json.loads(json_bytes.decode())

# ---------------- Генератор пароля ----------------
keyboard_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
shift_symbols = "!@#$%^&*()_+"

def generate_password():
    def two_letters():
        row = random.choice(keyboard_rows)
        start = random.randint(0, len(row) - 2)
        return row[start:start + 2]
    letters = two_letters() + two_letters() + two_letters()
    letters = letters[:6]
    idx_upper = random.randint(0, 5)
    letters = letters[:idx_upper] + letters[idx_upper].upper() + letters[idx_upper+1:]
    digit = str(random.randint(0, 9))
    symbol = random.choice(shift_symbols)
    return letters + digit + symbol

# ---------------- GUI ----------------
class PasswordManagerGUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Менеджер паролей")
        self.master.geometry("800x500")
        self.pack(fill=tk.BOTH, expand=True)

        self.private_key = None
        self.public_key = None
        self.key_path = None
        self.records = []
        self.data_file = os.path.join(os.path.dirname(__file__), "passwords.dat")

        self._build_login_ui()
        self._start_key_check()

    # ---------------- Экран загрузки ключа ----------------
    def _build_login_ui(self):
        self.clear_frame()
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(container, text="Добро пожаловать в Менеджер паролей", font=("Arial", 18, "bold")).pack(pady=20)
        ttk.Label(container, text="Чтобы войти, загрузите приватный ключ или создайте новый", font=("Arial", 12)).pack(
            pady=10)

        data_exists = os.path.isfile(self.data_file) and os.path.getsize(self.data_file) > 0

        btn_load = ttk.Button(container, text="Загрузить приватный ключ", width=30, command=self.load_private_key)
        btn_create = ttk.Button(container, text="Создать новый приватный ключ", width=30, command=self.create_rsa_keys)

        if data_exists:
            # Если база есть, доступна только загрузка
            btn_load.pack(pady=10)
            btn_create.state(["disabled"])
        else:
            # Если базы нет, доступно только создание нового ключа
            btn_create.pack(pady=10)
            btn_load.state(["disabled"])

    # ---------------- Основной экран ----------------
    def build_main_ui(self):
        self.clear_frame()
        ttk.Label(self, text="Список ресурсов", font=("Arial", 16, "bold")).pack(pady=10)

        # Поле поиска
        search_frame = ttk.Frame(self)
        search_frame.pack(pady=5, fill=tk.X)
        ttk.Label(search_frame, text="Поиск: ").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self.update_tree())

        # Treeview
        self.tree = ttk.Treeview(self, columns=("dummy",), show="tree")
        self.tree.heading("#0", text="Папки / Ресурсы")
        self.tree.column("#0", width=750, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Контекстное меню
        self.menu = tk.Menu(self.master, tearoff=0)
        self.menu.add_command(label="Копировать пароль", command=self.copy_password)
        self.menu.add_command(label="Изменить пароль", command=self.edit_password)
        self.tree.bind("<Button-3>", self.show_context_menu)  # правая кнопка мыши

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Добавить запись", width=20, command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Удалить выделенный", width=20, command=self.delete_selected).pack(side=tk.LEFT,
                                                                                                      padx=5)
        ttk.Button(btn_frame, text="Сменить ключ", width=20, command=self.rotate_keys).pack(side=tk.LEFT,
                                                                                            padx=5)  # Новая кнопка
        self.load_file_auto()
        self.update_tree()

    # ---------------- Общие функции ----------------
    def rotate_keys(self):
        if not self.private_key:
            messagebox.showerror("Ошибка", "Сначала загрузите приватный ключ.")
            return

        # Сохраняем старый приватный ключ
        old_private_key = self.private_key

        # 1. Генерируем новую пару ключей
        new_private, new_public = generate_rsa_keys()

        # 2. Перешифровываем все AES-ключи
        for entry in self.records:
            # Расшифровываем старый AES-ключ
            old_aes_key = decrypt_aes_key_rsa(base64.b64decode(entry["aes_key"]), old_private_key)
            # Шифруем его новым публичным ключом
            new_enc_key = encrypt_aes_key_rsa(old_aes_key, new_public)
            entry["aes_key"] = base64.b64encode(new_enc_key).decode()

        # 3. Обновляем текущие ключи
        self.private_key = new_private
        self.public_key = new_public

        # 4. Сохраняем новый приватный ключ
        path = filedialog.asksaveasfilename(title="Сохранить новый приватный ключ", defaultextension=".pem")
        if path:
            save_private_key(new_private, path)
            self.key_path = path
            self.save_file_auto()
            messagebox.showinfo("Успех",
                                f"Приватный ключ обновлён и все пароли перешифрованы.\nНовый ключ сохранён: {path}")
        else:
            messagebox.showwarning("Внимание", "Новый ключ не сохранён. Старый ключ всё ещё работает.")

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_rsa_keys(self):
        private_key, public_key = generate_rsa_keys()
        path = filedialog.asksaveasfilename(title="Сохранить приватный ключ", defaultextension=".pem")
        if not path:
            return
        save_private_key(private_key, path)
        messagebox.showinfo("Успех", f"Приватный ключ сохранен в {path}")
        self.private_key = private_key
        self.public_key = public_key
        self.key_path = path
        self.build_main_ui()

    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.menu.post(event.x_root, event.y_root)

    def copy_password(self):
        item_id = self.tree.focus()
        if not item_id:
            return
        text = self.tree.item(item_id, "text")
        if text.startswith("Пароль: "):
            password = text.replace("Пароль: ", "")
            self.master.clipboard_clear()
            self.master.clipboard_append(password)
            messagebox.showinfo("Скопировано", "Пароль скопирован в буфер обмена")

    def edit_password(self):
        item_id = self.tree.focus()
        if not item_id:
            return
        text = self.tree.item(item_id, "text")
        if not text.startswith("Пароль: "):
            messagebox.showwarning("Ошибка", "Выберите запись с паролем")
            return
        # Получаем индекс родительской записи ресурса
        parent_id = self.tree.parent(item_id)
        idx = int(parent_id)
        # Дешифруем запись
        entry = self.records[idx]
        aes_key = decrypt_aes_key_rsa(base64.b64decode(entry["aes_key"]), self.private_key)
        data = decrypt_data_aes(base64.b64decode(entry["data"]), aes_key, base64.b64decode(entry["iv"]))

        # Запрашиваем новый пароль
        new_pass = simpledialog.askstring("Изменить пароль", "Введите новый пароль:", initialvalue=data["password"])
        if not new_pass:
            return

        # Обновляем данные
        data["password"] = new_pass
        new_aes_key, new_iv, new_ct = encrypt_data_aes(data)
        new_enc_aes_key = encrypt_aes_key_rsa(new_aes_key, self.public_key)
        self.records[idx] = {
            "data": base64.b64encode(new_ct).decode(),
            "aes_key": base64.b64encode(new_enc_aes_key).decode(),
            "iv": base64.b64encode(new_iv).decode(),
            "folder": entry.get("folder", "Без папки")
        }
        self.save_file_auto()
        self.update_tree()
    # ---------------- Проверка ключа ----------------
    def _check_key_exists(self):
        if self.key_path and not os.path.isfile(self.key_path):
            messagebox.showerror("Ошибка", "Приватный ключ недоступен. Программа будет закрыта.")
            self.master.destroy()
            sys.exit(1)

    def _start_key_check(self):
        self._check_key_exists()
        self.after(3000, self._start_key_check)

    # ---------------- Загрузка ключа ----------------
    def load_private_key(self):
        from cryptography.exceptions import InvalidKey
        path = filedialog.askopenfilename(title="Выберите приватный ключ", filetypes=[("PEM files", "*.pem")])
        if not path or not os.path.isfile(path):
            messagebox.showerror("Ошибка", "Приватный ключ не найден. Программа будет закрыта.")
            self.master.destroy()
            sys.exit(1)
        self.key_path = path
        self.private_key = load_private_key(path)
        self.public_key = self.private_key.public_key()

        # Проверка ключа на существующих данных
        try:
            if os.path.isfile(self.data_file):
                with open(self.data_file, "r") as f:
                    records = json.load(f)
                if records:
                    first_entry = records[0]
                    aes_key = decrypt_aes_key_rsa(base64.b64decode(first_entry["aes_key"]), self.private_key)
                    decrypt_data_aes(
                        base64.b64decode(first_entry["data"]),
                        aes_key,
                        base64.b64decode(first_entry["iv"])
                    )
        except (ValueError, InvalidKey, Exception):
            messagebox.showerror(
                "Ошибка",
                "Приватный ключ не подходит для расшифровки данных. Программа будет закрыта."
            )
            self.master.destroy()
            sys.exit(1)

        self.build_main_ui()

    # ---------------- Добавление записи ----------------
    def add_record(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("Добавить запись")

        dialog.geometry("500x350")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Ресурс:").pack(pady=5)
        resource_entry = ttk.Entry(dialog, width=50)
        resource_entry.pack(pady=5)

        ttk.Label(dialog, text="Логин:").pack(pady=5)
        login_entry = ttk.Entry(dialog, width=50)
        login_entry.pack(pady=5)

        ttk.Label(dialog, text="Пароль:").pack(pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(dialog, width=50, textvariable=password_var, show="")
        password_entry.pack(pady=5)

        def gen_pass():
            password_var.set(generate_password())
        ttk.Button(dialog, text="Сгенерировать пароль", command=gen_pass).pack(pady=5)

        # Выбор папки
        folders = list({r.get("folder", "Без папки") for r in self.records})
        folders.append("Создать новую...")
        folder_var = tk.StringVar(value=folders[0] if folders else "Без папки")
        ttk.Label(dialog, text="Папка:").pack(pady=5)
        folder_combo = ttk.Combobox(dialog, textvariable=folder_var, values=folders, state="readonly")
        folder_combo.pack(pady=5)

        def on_folder_change(event):
            if folder_var.get() == "Создать новую...":
                new_folder = simpledialog.askstring("Новая папка", "Введите название новой папки:")
                if new_folder:
                    folder_var.set(new_folder)
        folder_combo.bind("<<ComboboxSelected>>", on_folder_change)

        def save_record():
            resource = resource_entry.get().strip()
            login = login_entry.get().strip()
            password = password_var.get().strip()
            folder = folder_var.get().strip()
            if not resource or not login or not password:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                return
            data = {"resource": resource, "login": login, "password": password}
            aes_key, iv, ct = encrypt_data_aes(data)
            enc_aes_key = encrypt_aes_key_rsa(aes_key, self.public_key)
            self.records.append({
                "data": base64.b64encode(ct).decode(),
                "aes_key": base64.b64encode(enc_aes_key).decode(),
                "iv": base64.b64encode(iv).decode(),
                "folder": folder
            })
            self.save_file_auto()
            self.update_tree()
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Сохранить", command=save_record, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy, width=20).pack(side=tk.LEFT, padx=5)

    # ---------------- Удаление ----------------
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        for item in selected:
            idx = int(item)
            self.records.pop(idx)
        self.save_file_auto()
        self.update_tree()

    # ---------------- Обновление дерева ----------------
    def update_tree(self):
        # Сохраняем открытые папки
        open_folders = {self.tree.item(i, "text") for i in self.tree.get_children() if self.tree.item(i, "open")}
        self.tree.delete(*self.tree.get_children())
        filter_text = self.search_var.get().lower() if hasattr(self, "search_var") else ""

        folders_dict = {}
        for idx, entry in enumerate(self.records):
            aes_key = decrypt_aes_key_rsa(base64.b64decode(entry["aes_key"]), self.private_key)
            data = decrypt_data_aes(base64.b64decode(entry["data"]), aes_key, base64.b64decode(entry["iv"]))
            folder = entry.get("folder", "Без папки")
            if filter_text not in data["resource"].lower():
                continue
            if folder not in folders_dict:
                folders_dict[folder] = []
            folders_dict[folder].append((idx, data))

        for folder_name, items in folders_dict.items():
            folder_id = self.tree.insert("", tk.END, text=folder_name, open=(folder_name in open_folders))
            for idx, data in items:
                parent_id = self.tree.insert(folder_id, tk.END, iid=str(idx), text=data['resource'])
                self.tree.insert(parent_id, tk.END, text=f"Логин: {data['login']}")
                self.tree.insert(parent_id, tk.END, text=f"Пароль: {data['password']}")
                self.tree.item(parent_id, open=False)

    # ---------------- Автосохранение ----------------
    def save_file_auto(self):
        with open(self.data_file, "w") as f:
            json.dump(self.records, f)

    def load_file_auto(self):
        if os.path.isfile(self.data_file):
            with open(self.data_file, "r") as f:
                self.records = json.load(f)

# ---------------- Запуск ----------------
def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12))
    style.configure("TLabel", font=("Arial", 12))
    app = PasswordManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

