import flet as ft
import sys
import os
import random
import string
import logging
import bcrypt
import mysql.connector
from datetime import datetime
from typing import Optional, Dict, List

# === НАСТРОЙКИ БАЗЫ ДАННЫХ ===
DB_CONFIG = {
    "host": "46.174.50.7",
    "user": "u39635_staff",
    "password": "Milky2207!",
    "database": "u39635_academy"
}

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
def setup_logging():
    try:
        LOG_FILE = "app.log"
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            encoding="utf-8"
        )
        logging.info("=== Приложение запущено ===")
    except Exception as e:
        print(f"Ошибка настройки логгирования: {e}")

# === ПОДКЛЮЧЕНИЕ К БАЗЕ ===
def connect_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к MySQL: {e}")
        return None

# === СОЗДАНИЕ ТАБЛИЦ ===
def initialize_database():
    try:
        conn = connect_db()
        if not conn:
            return False
            
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(64) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_superadmin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            license_number VARCHAR(64) UNIQUE NOT NULL,
            name VARCHAR(128) NOT NULL,
            level VARCHAR(64),
            certificate_url TEXT,
            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS license_categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            license_id INT NOT NULL,
            category_name VARCHAR(64) NOT NULL,
            FOREIGN KEY (license_id) REFERENCES licenses(id) ON DELETE CASCADE
        );
        """)

        cursor.execute("SELECT * FROM admins WHERE username='admin'")
        if not cursor.fetchone():
            pw_hash = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO admins (username, password_hash, is_superadmin) VALUES (%s, %s, %s)",
                ("admin", pw_hash, True)
            )
            conn.commit()
            logging.info("Создан суперпользователь admin с паролем password123")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logging.error(f"Ошибка инициализации базы: {e}")
        return False

# === ОСНОВНОЕ ПРИЛОЖЕНИЕ ===
class AcademyApp:
    def __init__(self):
        self.current_user = None
        self.page = None
        self.navigation_rail = None
        self.content_area = None
        self.current_view = None
        
    def main(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.show_login()
        
    def setup_page(self):
        self.page.title = "🎓 Admin Academy"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window.width = 1200
        self.page.window.height = 700
        self.page.window.min_width = 1000
        self.page.window.min_height = 600
        
    def show_login(self):
        """Показать окно входа"""
        username_field = ft.TextField(
            label="Логин",
            prefix_icon=ft.Icons.PERSON,
            width=300
        )
        
        password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            width=300
        )
        
        def login_click(e):
            username = username_field.value.strip()
            password = password_field.value.strip()
            
            if not username or not password:
                self.show_snackbar("Введите логин и пароль")
                return
                
            conn = connect_db()
            if not conn:
                self.show_snackbar("Ошибка подключения к базе данных")
                return
                
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM admins WHERE username=%s", (username,))
                user = cursor.fetchone()
                cursor.close()

                if user and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
                    logging.info(f"Пользователь {username} вошёл в систему.")
                    self.current_user = user
                    self.show_main_layout()
                else:
                    logging.warning(f"Неудачная попытка входа: {username}")
                    self.show_snackbar("Неверный логин или пароль")
            except Exception as e:
                logging.error(f"Ошибка при входе: {e}")
                self.show_snackbar(f"Ошибка при входе: {e}")
            finally:
                conn.close()
        
        login_content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "🎓 Admin Academy",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=20),
                    username_field,
                    password_field,
                    ft.Container(height=10),
                    ft.FilledButton(
                        "Войти",
                        on_click=login_click,
                        width=300
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        self.page.clean()
        self.page.add(login_content)
        
    def show_main_layout(self):
        """Показать основную структуру приложения"""
        # Создаем навигацию
        self.create_navigation()
        
        # Создаем область контента
        self.content_area = ft.Container(expand=True)
        
        # Создаем заголовок
        header = self.create_header()
        
        # Основной макет
        main_layout = ft.Row(
            [
                self.navigation_rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        header,
                        ft.Divider(height=1),
                        self.content_area
                    ],
                    expand=True,
                    spacing=0
                )
            ],
            expand=True
        )
        
        self.page.clean()
        self.page.add(main_layout)
        
        # Показать первую страницу
        self.show_add_license()
        
    def create_header(self):
        """Создать заголовок"""
        role = "Руководитель" if self.current_user["is_superadmin"] else "Наставник"
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        f"Вы вошли как: {role} ({self.current_user['username']})",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(expand=True),
                    ft.FilledButton(
                        "🚪 Выйти",
                        on_click=self.logout,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.RED_400
                        )
                    )
                ]
            ),
            padding=15,
            bgcolor=ft.Colors.GREY_900
        )
        
    def create_navigation(self):
        """Создать навигационную панель"""
        nav_items = [
            ("➕ Добавить лицензию", ft.Icons.ADD_CIRCLE_OUTLINE),
            ("🔍 Проверить лицензию", ft.Icons.SEARCH),
            ("🗑 Удалить лицензию", ft.Icons.DELETE_OUTLINE),
            ("📋 Список лицензий", ft.Icons.LIST_ALT),
            ("🏷 Категории", ft.Icons.CATEGORY),
        ]
        
        if self.current_user["is_superadmin"]:
            nav_items.append(("👑 Администраторы", ft.Icons.ADMIN_PANEL_SETTINGS))
            
        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=icon,
                    selected_icon=icon,
                    label=label,
                ) for label, icon in nav_items
            ],
            on_change=self.on_navigation_change,
            expand=True,
        )
        
    def on_navigation_change(self, e):
        """Обработчик изменения навигации"""
        index = e.control.selected_index
        views = [
            self.show_add_license,
            self.show_check_license,
            self.show_delete_license,
            self.show_list_licenses,
            self.show_categories,
        ]
        
        if self.current_user["is_superadmin"]:
            views.append(self.show_manage_admins)
            
        if index < len(views):
            views[index]()
            
    def show_add_license(self):
        """Показать страницу добавления лицензии"""
        name_field = ft.TextField(label="Имя владельца", expand=True)
        level_field = ft.TextField(label="Уровень", expand=True)
        url_field = ft.TextField(label="Сертификат (URL)", expand=True)
        result_text = ft.Text()
        
        def add_license(e):
            try:
                conn = connect_db()
                if not conn:
                    self.show_snackbar("Ошибка подключения к базе данных")
                    return
                    
                license_num = "AA-" + ''.join(random.choices(string.ascii_uppercase, k=4)) + "-" + ''.join(random.choices(string.digits, k=4))
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO licenses (license_number, name, level, certificate_url) VALUES (%s, %s, %s, %s)",
                    (license_num, name_field.value, level_field.value, url_field.value)
                )
                conn.commit()
                cursor.close()
                conn.close()
                
                logging.info(f"Добавлена лицензия {license_num} для {name_field.value}")
                result_text.value = f"✅ Лицензия {license_num} успешно добавлена!"
                result_text.color = ft.Colors.GREEN
                
                # Очистить поля
                name_field.value = ""
                level_field.value = ""
                url_field.value = ""
                
                self.content_area.update()
                
            except Exception as e:
                logging.error(f"Ошибка добавления лицензии: {e}")
                result_text.value = f"❌ Ошибка: {e}"
                result_text.color = ft.Colors.RED
                self.content_area.update()
        
        content = ft.Column(
            [
                ft.Text("Добавление лицензии", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                name_field,
                ft.Container(height=10),
                level_field,
                ft.Container(height=10),
                url_field,
                ft.Container(height=20),
                ft.FilledButton("Добавить лицензию", on_click=add_license),
                ft.Container(height=20),
                result_text
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        self.content_area.content = ft.Container(content, padding=20, expand=True)
        self.content_area.update()
        
    def show_check_license(self):
        """Показать страницу проверки лицензии"""
        license_field = ft.TextField(
            label="Номер лицензии",
            hint_text="AA-XXXX-1234",
            prefix_icon=ft.Icons.SEARCH,
            expand=True
        )
        result_text = ft.Text()
        
        def check_license(e):
            code = license_field.value.strip()
            if not code:
                self.show_snackbar("Введите номер лицензии")
                return
                
            conn = connect_db()
            if not conn:
                self.show_snackbar("Ошибка подключения к базе данных")
                return
                
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM licenses WHERE license_number=%s", (code,))
                data = cursor.fetchone()
                
                if not data:
                    result_text.value = "❌ Лицензия не найдена."
                    result_text.color = ft.Colors.RED
                else:
                    cursor.execute("SELECT category_name FROM license_categories WHERE license_id=%s", (data["id"],))
                    cats = [r["category_name"] for r in cursor.fetchall()]
                    cats_str = ", ".join(cats) if cats else "—"
                    
                    result_text.value = (
                        f"✅ Лицензия найдена!\n\n"
                        f"👤 Имя: {data['name']}\n"
                        f"📜 Уровень: {data['level']}\n"
                        f"🔢 Номер: {data['license_number']}\n"
                        f"🕒 Дата выдачи: {data['issued_at']}\n"
                        f"🏷 Категории: {cats_str}\n"
                        f"🖼 Сертификат: {data['certificate_url'] or '—'}"
                    )
                    result_text.color = ft.Colors.GREEN
                    
                cursor.close()
                
            except Exception as e:
                logging.error(f"Ошибка проверки лицензии: {e}")
                result_text.value = f"❌ Ошибка: {e}"
                result_text.color = ft.Colors.RED
            finally:
                conn.close()
                self.content_area.update()
        
        content = ft.Column(
            [
                ft.Text("Проверка лицензии", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Row([license_field]),
                ft.Container(height=10),
                ft.FilledButton("Проверить", on_click=check_license),
                ft.Container(height=20),
                result_text
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        self.content_area.content = ft.Container(content, padding=20, expand=True)
        self.content_area.update()
        
    def show_delete_license(self):
        """Показать страницу удаления лицензии"""
        license_field = ft.TextField(
            label="Номер лицензии для удаления",
            prefix_icon=ft.Icons.WARNING_AMBER,
            expand=True
        )
        result_text = ft.Text()
        
        def delete_license(e):
            code = license_field.value.strip()
            if not code:
                self.show_snackbar("Введите номер лицензии")
                return
                
            # Подтверждение удаления
            def confirm_delete(e):
                conn = connect_db()
                if not conn:
                    self.show_snackbar("Ошибка подключения к базе данных")
                    return
                    
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM licenses WHERE license_number=%s", (code,))
                    conn.commit()
                    deleted = cursor.rowcount
                    cursor.close()
                    
                    if deleted:
                        logging.info(f"Удалена лицензия {code}")
                        result_text.value = "✅ Лицензия успешно удалена"
                        result_text.color = ft.Colors.GREEN
                        license_field.value = ""
                    else:
                        result_text.value = "❌ Лицензия не найдена"
                        result_text.color = ft.Colors.RED
                        
                except Exception as e:
                    logging.error(f"Ошибка удаления лицензии: {e}")
                    result_text.value = f"❌ Ошибка: {e}"
                    result_text.color = ft.Colors.RED
                finally:
                    conn.close()
                    self.content_area.update()
                    self.page.close(dialog)
            
            dialog = ft.AlertDialog(
                title=ft.Text("Подтверждение удаления"),
                content=ft.Text(f"Вы уверены, что хотите удалить лицензию {code}?"),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                    ft.TextButton("Удалить", on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ],
            )
            self.page.open(dialog)
        
        content = ft.Column(
            [
                ft.Text("Удаление лицензии", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Row([license_field]),
                ft.Container(height=10),
                ft.FilledButton(
                    "Удалить лицензию", 
                    on_click=delete_license,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED)
                ),
                ft.Container(height=20),
                result_text
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        self.content_area.content = ft.Container(content, padding=20, expand=True)
        self.content_area.update()
        
    def show_list_licenses(self):
        """Показать список всех лицензий"""

        # 👇 создаём таблицу с одной "временной" колонкой
        data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Загрузка..."))],
            rows=[]
        )

        def load_initial_data():
            self.load_licenses_data(data_table)

        refresh_button = ft.FilledButton(
            "🔄 Обновить",
            on_click=lambda e: self.load_licenses_data(data_table)
        )

        content = ft.Column(
            [
                ft.Text("Список лицензий", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                refresh_button,
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([data_table], scroll=ft.ScrollMode.ADAPTIVE),
                    expand=True
                )
            ],
            expand=True
        )

        self.content_area.content = ft.Container(content, padding=20, expand=True)
        self.content_area.update()

        # 👇 после отрисовки таблицы — подгружаем реальные данные
        load_initial_data()
        
    def load_licenses_data(self, data_table):
        """Загрузить данные лицензий в таблицу"""
        try:
            conn = connect_db()
            if not conn:
                self.show_snackbar("Ошибка подключения к базе данных")
                return
                
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT license_number, name, level, issued_at FROM licenses ORDER BY issued_at DESC")
            rows = cursor.fetchall()
            
            # Создаем колонки
            data_table.columns = [
                ft.DataColumn(ft.Text("Номер")),
                ft.DataColumn(ft.Text("Имя")),
                ft.DataColumn(ft.Text("Уровень")),
                ft.DataColumn(ft.Text("Дата выдачи")),
            ]
            
            # Создаем строки
            data_table.rows = []
            for row in rows:
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(row["license_number"])),
                            ft.DataCell(ft.Text(row["name"])),
                            ft.DataCell(ft.Text(row["level"] or "")),
                            ft.DataCell(ft.Text(str(row["issued_at"]))),
                        ]
                    )
                )
                
            cursor.close()
            conn.close()
            self.content_area.update()
            
        except Exception as e:
            logging.error(f"Ошибка загрузки данных: {e}")
            self.show_snackbar(f"Ошибка загрузки данных: {e}")
            
    def show_categories(self):
        """Показать страницу управления категориями"""
        license_field = ft.TextField(label="Номер лицензии", expand=True)
        category_field = ft.TextField(label="Название категории", expand=True)
        result_text = ft.Text()
        
        def add_category(e):
            code = license_field.value.strip()
            category = category_field.value.strip()
            
            if not code or not category:
                self.show_snackbar("Заполните все поля")
                return
                
            conn = connect_db()
            if not conn:
                self.show_snackbar("Ошибка подключения к базе данных")
                return
                
            try:
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id FROM licenses WHERE license_number=%s", (code,))
                row = cur.fetchone()
                
                if not row:
                    result_text.value = "❌ Лицензия не найдена"
                    result_text.color = ft.Colors.RED
                else:
                    cur.execute("INSERT INTO license_categories (license_id, category_name) VALUES (%s,%s)", (row["id"], category))
                    conn.commit()
                    result_text.value = "✅ Категория успешно добавлена"
                    result_text.color = ft.Colors.GREEN
                    logging.info(f"Добавлена категория '{category}' к {code}")
                    
                    # Очистить поля
                    license_field.value = ""
                    category_field.value = ""
                    
                cur.close()
                
            except Exception as e:
                logging.error(f"Ошибка добавления категории: {e}")
                result_text.value = f"❌ Ошибка: {e}"
                result_text.color = ft.Colors.RED
            finally:
                conn.close()
                self.content_area.update()
        
        content = ft.Column(
            [
                ft.Text("Добавление категорий", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                license_field,
                ft.Container(height=10),
                category_field,
                ft.Container(height=20),
                ft.FilledButton("Добавить категорию", on_click=add_category),
                ft.Container(height=20),
                result_text
            ],
            scroll=ft.ScrollMode.ADAPTIVE
        )
        
        self.content_area.content = ft.Container(content, padding=20, expand=True)
        self.content_area.update()
        
    def show_manage_admins(self):
        """Показать страницу управления администраторами (только для суперадминов)"""
        if not self.current_user["is_superadmin"]:
            self.show_snackbar("Недостаточно прав")
            return

        username_field = ft.TextField(label="Логин", expand=True)
        password_field = ft.TextField(label="Пароль", password=True, expand=True)
        role_field = ft.Dropdown(
            label="Роль",
            options=[
                ft.dropdown.Option("0", "Наставник"),
                ft.dropdown.Option("1", "Руководитель"),
            ],
            value="0",
            expand=True
        )

        # 👇 добавляем хотя бы одну видимую колонку
        admins_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Загрузка..."))],
            rows=[]
        )
        
        def load_admins():
            try:
                conn = connect_db()
                if not conn:
                    return
                    
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id, username, is_superadmin, created_at FROM admins")
                rows = cur.fetchall()
                
                admins_table.columns = [
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("Логин")),
                    ft.DataColumn(ft.Text("Роль")),
                    ft.DataColumn(ft.Text("Создан")),
                ]
                
                admins_table.rows = []
                for row in rows:
                    role = "👑 Руководитель" if row["is_superadmin"] else "👨‍🏫 Наставник"
                    admins_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(row["id"]))),
                                ft.DataCell(ft.Text(row["username"])),
                                ft.DataCell(ft.Text(role)),
                                ft.DataCell(ft.Text(str(row["created_at"]))),
                            ]
                        )
                    )
                    
                cur.close()
                conn.close()
                self.content_area.update()
                
            except Exception as e:
                logging.error(f"Ошибка загрузки администраторов: {e}")
                
        def add_admin(e):
            username = username_field.value.strip()
            password = password_field.value.strip()
            
            if not username or not password:
                self.show_snackbar("Введите логин и пароль")
                return
                
            conn = connect_db()
            if not conn:
                self.show_snackbar("Ошибка подключения к базе данных")
                return
                
            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM admins WHERE username=%s", (username,))
                if cur.fetchone():
                    self.show_snackbar("Такой логин уже существует")
                else:
                    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                    is_superadmin = role_field.value == "1"
                    cur.execute("INSERT INTO admins (username,password_hash,is_superadmin) VALUES (%s,%s,%s)", 
                               (username, pw_hash, is_superadmin))
                    conn.commit()
                    self.show_snackbar("✅ Администратор добавлен")
                    logging.info(f"Добавлен администратор {username}")
                    
                    # Очистить поля и обновить таблицу
                    username_field.value = ""
                    password_field.value = ""
                    load_admins()
                    
                cur.close()
            except Exception as e:
                logging.error(f"Ошибка добавления администратора: {e}")
                self.show_snackbar(f"Ошибка: {e}")
            finally:
                conn.close()
        
        content = ft.Column(
            [
                ft.Text("Управление администраторами", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(height=20),
                ft.Text("Добавить администратора:", size=16, weight=ft.FontWeight.BOLD),
                ft.Row([username_field, password_field, role_field]),
                ft.Container(height=10),
                ft.FilledButton("➕ Добавить администратора", on_click=add_admin),
                ft.Container(height=30),
                ft.Text("Список администраторов:", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column([admins_table], scroll=ft.ScrollMode.ADAPTIVE),
                    expand=True
                )
            ],
            expand=True
        )
        
        self.content_area.content = ft.Container(content, padding=20, expand=True)
        self.content_area.update()
        
        # Загрузить список администраторов
        load_admins()
        
    def logout(self, e):
        """Выход из системы"""
        logging.info(f"Пользователь {self.current_user['username']} вышел из системы.")
        self.current_user = None
        self.show_login()
        
    def show_snackbar(self, message: str):
        """Показать уведомление"""
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()

# === ЗАПУСК ПРИЛОЖЕНИЯ ===
if __name__ == "__main__":
    import traceback

    try:
        # Для PyInstaller
        if getattr(sys, 'frozen', False):
            os.chdir(sys._MEIPASS)

        setup_logging()
        logging.info("=== Запуск приложения ===")

        if not initialize_database():
            logging.critical("Ошибка инициализации базы данных.")
            print("Не удалось инициализировать базу данных.")
            sys.exit(1)

        app = AcademyApp()
        ft.app(target=app.main)

    except Exception as e:
        tb = traceback.format_exc()
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(tb)
        print(tb)
        sys.exit(1)