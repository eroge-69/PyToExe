import customtkinter as ctk
import os
import requests
import shutil

# Настройки внешнего вида
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

# Константы
MODS_PATH = os.path.expanduser("~/.minecraft/mods")
CHEAT_URL = "https://your-site.com/cheat.jar"  # ← замени на свою ссылку
CHEAT_FILENAME = "wexside_cheat.jar"

# Данные пользователя (вшиты)
USER = {
    "username": "Perix",
    "password": "123",
    "friends": ["Nikita", "Dark", "Killa"]
}


class LoginPage(ctk.CTkFrame):
    def __init__(self, master, login_callback):
        super().__init__(master)
        self.login_callback = login_callback
        self.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self, text="🔒 Авторизация", font=("Arial", 22)).pack(pady=20)
        self.username_entry = ctk.CTkEntry(self, placeholder_text="Логин")
        self.username_entry.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        self.password_entry.pack(pady=10)

        self.status = ctk.CTkLabel(self, text="", text_color="red")
        self.status.pack()

        ctk.CTkButton(self, text="Войти", command=self.try_login).pack(pady=20)

    def try_login(self):
        login = self.username_entry.get()
        password = self.password_entry.get()

        if login == USER["username"] and password == USER["password"]:
            self.login_callback(USER["username"], USER)
        else:
            self.status.configure(text="Неверный логин или пароль")


class LoaderPage(ctk.CTkFrame):
    def __init__(self, master, username, user_data):
        super().__init__(master)
        self.username = username
        self.user_data = user_data
        self.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self, text=f"Добро пожаловать, {username}", font=("Arial", 20)).pack(pady=10)

        ctk.CTkLabel(self, text="📜 Список друзей:", font=("Arial", 16)).pack(pady=5)
        friends_box = ctk.CTkTextbox(self, width=300, height=100)
        friends_box.pack(pady=5)
        friends_box.insert("0.0", "\n".join(self.user_data["friends"]))
        friends_box.configure(state="disabled")

        ctk.CTkButton(self, text="📥 Загрузить чит", command=self.download_cheat).pack(pady=20)

        self.status = ctk.CTkLabel(self, text="")
        self.status.pack(pady=5)

    def download_cheat(self):
        try:
            if not os.path.exists(MODS_PATH):
                os.makedirs(MODS_PATH)

            response = requests.get(CHEAT_URL, stream=True)
            if response.status_code == 200:
                cheat_path = os.path.join(MODS_PATH, CHEAT_FILENAME)
                with open(cheat_path, "wb") as f:
                    shutil.copyfileobj(response.raw, f)
                self.status.configure(text="✅ Чит установлен", text_color="green")
            else:
                self.status.configure(text="❌ Ошибка загрузки", text_color="red")
        except Exception as e:
            self.status.configure(text=f"Ошибка: {e}", text_color="red")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Wexside Loader")
        self.geometry("500x400")
        self.resizable(False, False)
        self.login_page = LoginPage(self, self.login_success)
        self.current_page = self.login_page

    def login_success(self, username, user_data):
        self.current_page.destroy()
        self.current_page = LoaderPage(self, username, user_data)


if __name__ == "__main__":
    app = App()
    app.mainloop()
