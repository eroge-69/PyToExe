import json
import os
import base64
import time
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass

class HackerTerminal:
    @staticmethod
    def clear_screen():
        """Очистка экрана с анимацией"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def typewriter(text, delay=0.03, end="\n"):
        """Эффект печатающей машинки"""
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write(end)
        sys.stdout.flush()
    
    @staticmethod
    def matrix_effect(lines=10):
        """Эффект падающего кода матрицы"""
        print("\033[32m", end="")  # Зеленый цвет
        for _ in range(lines):
            print(''.join([str(int(time.time() * 1000) % 10) for _ in range(80)]))
            time.sleep(0.1)
        print("\033[0m", end="")  # Сброс цвета
    
    @staticmethod
    def display_header():
        """Отображение хакерского заголовка"""
        HackerTerminal.clear_screen()
        print("\033[32m", end="")  # Зеленый текст
        print("═" * 60)
        print("█" * 60)
        HackerTerminal.typewriter("██▓▒░ СИСТЕМА ЗАШИФРОВАННЫХ КОММУНИКАЦИЙ ИНКВИЗИЦИИ ░▒▓██", delay=0.01)
        print("█" * 60)
        print("═" * 60)
        print("\033[0m", end="")  # Сброс цвета
    
    @staticmethod
    def loading_animation(message="ЗАГРУЗКА", duration=2):
        """Анимация загрузки"""
        HackerTerminal.clear_screen()
        print("\033[32m", end="")
        HackerTerminal.typewriter(f"\n{message}", end="")
        for _ in range(5):
            print(".", end="", flush=True)
            time.sleep(duration/5)
        print("\n\033[0m", end="")
    
    @staticmethod
    def input_with_typewriter(prompt, delay=0.03):
        """Ввод с предварительным выводом текста печатающей машинкой"""
        HackerTerminal.typewriter(prompt, delay=delay, end="")
        return input()
    
    @staticmethod
    def getpass_with_typewriter(prompt, delay=0.03):
        """Безопасный ввод с предварительным выводом текста"""
        HackerTerminal.typewriter(prompt, delay=delay, end="")
        return getpass.getpass("")
    
    @staticmethod
    def parse_formatting(text):
        """Разбор текста с форматированием [blue]слово[/blue]"""
        if not text:
            return text
            
        formatted_text = text
        
        # Синее выделение
        formatted_text = formatted_text.replace('[blue]', '\033[94m')
        formatted_text = formatted_text.replace('[/blue]', '\033[0m')
        
        # Жирное выделение  
        formatted_text = formatted_text.replace('[bold]', '\033[1m')
        formatted_text = formatted_text.replace('[/bold]', '\033[0m')
        
        # Подчеркивание
        formatted_text = formatted_text.replace('[underline]', '\033[4m')
        formatted_text = formatted_text.replace('[/underline]', '\033[0m')
        
        return formatted_text

class SecureNotes:
    def __init__(self):
        self.notes_file = "cyber_comm.dat"
        self.salt_file = "security_key.bin"
        self.fernet = None
        self.notes = {}
        self.terminal = HackerTerminal()
        
    def derive_key(self, password, salt):
        """Создание криптографического ключа"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def setup_master_password(self):
        """Инициализация системы безопасности"""
        self.terminal.display_header()
        self.terminal.typewriter("ИНИЦИАЛИЗАЦИЯ СИСТЕМЫ БЕЗОПАСНОСТИ...")
        time.sleep(1)
        
        if os.path.exists(self.salt_file):
            self.terminal.typewriter("СИСТЕМА УЖЕ АКТИВИРОВАНА...")
            time.sleep(1)
            return False
            
        self.terminal.typewriter("\n\033[33m[СИСТЕМА] УСТАНОВИТЕ ГЛАВНЫЙ КЛЮЧ ДОСТУПА\033[0m")
        password = self.terminal.getpass_with_typewriter("\033[32m[ВВОД] ГЛАВНЫЙ КЛЮЧ: \033[0m")
        confirm = self.terminal.getpass_with_typewriter("\033[32m[ПОДТВЕРЖДЕНИЕ] ПОВТОРИТЕ КЛЮЧ: \033[0m")
        
        if password != confirm:
            self.terminal.typewriter("\033[31mОШИБКА: КЛЮЧИ НЕ СОВПАДАЮТ\033[0m")
            time.sleep(2)
            return False
            
        salt = os.urandom(16)
        with open(self.salt_file, 'wb') as f:
            f.write(salt)
            
        key = self.derive_key(password, salt)
        self.fernet = Fernet(key)
        
        self.save_notes()
        self.terminal.typewriter("\033[32mСИСТЕМА АКТИВИРОВАНА. ДОСТУП РАЗРЕШЕН.\033[0m")
        time.sleep(2)
        return True
    
    def authenticate(self):
        """Процедура аутентификации"""
        self.terminal.display_header()
        
        if not os.path.exists(self.salt_file):
            self.terminal.typewriter("\033[31mСИСТЕМА НЕ АКТИВИРОВАНА...\033[0m")
            time.sleep(2)
            return False
            
        try:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
                
            self.terminal.typewriter("ТРЕБУЕТСЯ АУТЕНТИФИКАЦИЯ...")
            password = self.terminal.getpass_with_typewriter("\033[32m[СИСТЕМА] ВВЕДИТЕ ГЛАВНЫЙ КЛЮЧ: \033[0m")
            
            self.terminal.loading_animation("ПРОВЕРКА КЛЮЧА")
            
            key = self.derive_key(password, salt)
            self.fernet = Fernet(key)
            
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.notes = json.loads(decrypted_data.decode())
                
            self.terminal.typewriter("\033[32mДОСТУП РАЗРЕШЕН. ДОБРО ПОЖАЛОВАТЬ ИНКВИЗИТОР.\033[0m")
            time.sleep(1)
            return True
            
        except Exception as e:
            self.terminal.typewriter("\033[31mОШИБКА: НЕВЕРНЫЙ КЛЮЧ ИЛИ ПОВРЕЖДЕННЫЕ ДАННЫЕ\033[0m")
            time.sleep(2)
            return False
    
    def encrypt_text(self, text):
        """Шифрование данных"""
        return self.fernet.encrypt(text.encode()).decode()
    
    def decrypt_text(self, encrypted_text):
        """Дешифровка данных"""
        return self.fernet.decrypt(encrypted_text.encode()).decode()
    
    def save_notes(self):
        """Сохранение зашифрованных данных"""
        if self.fernet:
            data_json = json.dumps(self.notes, ensure_ascii=False, indent=2)
            encrypted_data = self.fernet.encrypt(data_json.encode())
            with open(self.notes_file, 'wb') as f:
                f.write(encrypted_data)
    
    def create_note(self):
        """Создание новой записи"""
        self.terminal.display_header()
        self.terminal.typewriter("СОЗДАНИЕ НОВОЙ ЗАПИСИ...")
        print()
        
        title = self.terminal.input_with_typewriter("\033[33m[СИСТЕМА] ИДЕНТИФИКАТОР ЗАПИСИ: \033[0m")
        
        # Подсказка по форматированию
        self.terminal.typewriter("\n\033[36m[ПОДСКАЗКА] Используйте:\033[0m")
        self.terminal.typewriter("\033[36m  [blue]текст[/blue] - синее выделение\033[0m")
        self.terminal.typewriter("\033[36m  [bold]текст[/bold] - жирный текст\033[0m")
        self.terminal.typewriter("\033[36m  [underline]текст[/underline] - подчеркивание\033[0m\n")
        
        content = self.terminal.input_with_typewriter("\033[33m[СИСТЕМА] СОДЕРЖИМОЕ: \033[0m")
        
        # Спросить о пароле для заметки
        use_password = self.terminal.input_with_typewriter("\033[33m[СИСТЕМА] ЗАЩИТИТЬ ПАРОЛЕМ? (y/N): \033[0m")
        note_password = None
        
        if use_password.lower() == 'y':
            note_password = self.terminal.getpass_with_typewriter("\033[33m[СИСТЕМА] ПАРОЛЬ ДЛЯ ЗАМЕТКИ: \033[0m")
            confirm = self.terminal.getpass_with_typewriter("\033[33m[СИСТЕМА] ПОДТВЕРДИТЕ ПАРОЛЬ: \033[0m")
            
            if note_password != confirm:
                self.terminal.typewriter("\033[31mОШИБКА: ПАРОЛИ НЕ СОВПАДАЮТ\033[0m")
                time.sleep(2)
                return
        
        # Создаем структуру данных для заметки
        note_data = {
            'content': self.encrypt_text(content),
            'password_protected': note_password is not None
        }
        
        # Если есть пароль, добавляем хэш пароля
        if note_password:
            salt = os.urandom(16)
            note_key = self.derive_key(note_password, salt)
            note_fernet = Fernet(note_key)
            note_data['content'] = note_fernet.encrypt(content.encode()).decode()
            note_data['salt'] = base64.b64encode(salt).decode()
        
        self.notes[title] = note_data
        self.save_notes()
        
        self.terminal.typewriter(f"\033[32mЗАПИСЬ '{title}' ДОБАВЛЕНА В БАЗУ ДАННЫХ\033[0m")
        time.sleep(1)
    
    def decrypt_note_content(self, note_data, title=""):
        """Дешифровка содержимого заметки с учетом пароля"""
        try:
            if note_data.get('password_protected'):
                # Запрос пароля для защищенной заметки
                self.terminal.typewriter(f"\033[33mЗАПИСЬ '{title}' ЗАЩИЩЕНА ПАРОЛЕМ\033[0m")
                password = self.terminal.getpass_with_typewriter("\033[33m[СИСТЕМА] ВВЕДИТЕ ПАРОЛЬ: \033[0m")
                
                # Проверяем пароль
                salt = base64.b64decode(note_data['salt'])
                note_key = self.derive_key(password, salt)
                note_fernet = Fernet(note_key)
                
                # Пытаемся дешифровать
                content = note_fernet.decrypt(note_data['content'].encode()).decode()
                return content
            else:
                # Обычная дешифровка
                return self.decrypt_text(note_data['content'])
        except:
            self.terminal.typewriter("\033[31mОШИБКА: НЕВЕРНЫЙ ПАРОЛЬ ИЛИ ПОВРЕЖДЕННЫЕ ДАННЫЕ\033[0m")
            time.sleep(2)
            return None
    
    def view_notes(self):
        """Просмотр списка записей"""
        self.terminal.display_header()
        
        if not self.notes:
            self.terminal.typewriter("\033[33mБАЗА ДАННЫХ ПУСТА...\033[0m")
            time.sleep(1)
            return
            
        self.terminal.typewriter("СПИСОК АКТИВНЫХ ЗАПИСЕЙ:")
        print("\n" + "═" * 60)
        for i, (title, note_data) in enumerate(self.notes.items(), 1):
            protection = " 🔒" if note_data.get('password_protected') else ""
            self.terminal.typewriter(f"\033[36m[{i:02d}]\033[0m {title}{protection}", delay=0.01)
        print("═" * 60)
    
    def read_note(self):
        """Чтение конкретной записи"""
        self.view_notes()
        if not self.notes:
            self.terminal.input_with_typewriter("\n\033[33m[ENTER] ДЛЯ ПРОДОЛЖЕНИЯ...\033[0m")
            return
            
        try:
            choice = self.terminal.input_with_typewriter("\n\033[33m[СИСТЕМА] ВВЕДИТЕ НОМЕР ЗАПИСИ: \033[0m")
            if not choice:
                return
                
            choice = int(choice) - 1
            titles = list(self.notes.keys())
            
            if 0 <= choice < len(titles):
                title = titles[choice]
                note_data = self.notes[title]
                
                content = self.decrypt_note_content(note_data, title)
                if content is None:
                    return
                
                self.terminal.display_header()
                print(f"\033[35m══════════════════════════════════════════════\033[0m")
                self.terminal.typewriter(f"\033[35m ЗАПИСЬ: {title}\033[0m", delay=0.01)
                if note_data.get('password_protected'):
                    self.terminal.typewriter("\033[31m🔒 ЗАЩИЩЕНО ПАРОЛЕМ\033[0m", delay=0.01)
                print(f"\033[35m══════════════════════════════════════════════\033[0m")
                
                # Применяем форматирование к содержимому
                formatted_content = self.terminal.parse_formatting(content)
                self.terminal.typewriter(f"\033[32m{formatted_content}\033[0m", delay=0.01)
                
                print(f"\033[35m══════════════════════════════════════════════\033[0m")
                
                self.terminal.input_with_typewriter("\n\033[33m[ENTER] ДЛЯ ПРОДОЛЖЕНИЯ...\033[0m")
            else:
                self.terminal.typewriter("\033[31mОШИБКА: НЕВЕРНЫЙ ИНДЕКС\033[0m")
                time.sleep(1)
        except ValueError:
            self.terminal.typewriter("\033[31mОШИБКА: НЕКОРРЕКТНЫЙ ВВОД\033[0m")
            time.sleep(1)
    
    def edit_note(self):
        """Редактирование записи"""
        self.view_notes()
        if not self.notes:
            self.terminal.input_with_typewriter("\n\033[33m[ENTER] ДЛЯ ПРОДОЛЖЕНИЯ...\033[0m")
            return
            
        try:
            choice = self.terminal.input_with_typewriter("\n\033[33m[СИСТЕМА] ВВЕДИТЕ НОМЕР ДЛЯ РЕДАКТИРОВАНИЯ: \033[0m")
            if not choice:
                return
                
            choice = int(choice) - 1
            titles = list(self.notes.keys())
            
            if 0 <= choice < len(titles):
                title = titles[choice]
                note_data = self.notes[title]
                
                # Если заметка защищена паролем, запросим его
                if note_data.get('password_protected'):
                    content = self.decrypt_note_content(note_data, title)
                    if content is None:
                        return
                else:
                    content = self.decrypt_text(note_data['content'])
                
                self.terminal.display_header()
                self.terminal.typewriter(f"\033[33mРЕДАКТИРОВАНИЕ: {title}\033[0m")
                
                # Показываем текущее содержимое с форматированием
                formatted_content = self.terminal.parse_formatting(content)
                self.terminal.typewriter(f"\033[32mТЕКУЩЕЕ СОДЕРЖИМОЕ: {formatted_content}\033[0m")
                print()
                
                # Подсказка по форматированию
                self.terminal.typewriter("\033[36m[ПОДСКАЗКА] Используйте:\033[0m")
                self.terminal.typewriter("\033[36m  [blue]текст[/blue] - синее выделение\033[0m")
                self.terminal.typewriter("\033[36m  [bold]текст[/bold] - жирный текст\033[0m")
                self.terminal.typewriter("\033[36m  [underline]текст[/underline] - подчеркивание\033[0m\n")
                
                new_content = self.terminal.input_with_typewriter("\033[33m[СИСТЕМА] НОВОЕ СОДЕРЖИМОЕ: \033[0m")
                
                if new_content:
                    # Сохраняем с тем же уровнем защиты
                    if note_data.get('password_protected'):
                        salt = base64.b64decode(note_data['salt'])
                        note_key = self.derive_key(
                            self.terminal.getpass_with_typewriter("\033[33m[СИСТЕМА] ПАРОЛЬ ДЛЯ ЗАМЕТКИ: \033[0m"), 
                            salt
                        )
                        note_fernet = Fernet(note_key)
                        note_data['content'] = note_fernet.encrypt(new_content.encode()).decode()
                    else:
                        note_data['content'] = self.encrypt_text(new_content)
                    
                    self.save_notes()
                    self.terminal.typewriter("\033[32mЗАПИСЬ ОБНОВЛЕНА\033[0m")
                    time.sleep(1)
            else:
                self.terminal.typewriter("\033[31mОШИБКА: НЕВЕРНЫЙ ИНДЕКС\033[0m")
                time.sleep(1)
        except ValueError:
            self.terminal.typewriter("\033[31mОШИБКА: НЕКОРРЕКТНЫЙ ВВОД\033[0m")
            time.sleep(1)
    
    def delete_note(self):
        """Удаление записи"""
        self.view_notes()
        if not self.notes:
            self.terminal.input_with_typewriter("\n\033[33m[ENTER] ДЛЯ ПРОДОЛЖЕНИЯ...\033[0m")
            return
            
        try:
            choice = self.terminal.input_with_typewriter("\n\033[33m[СИСТЕМА] ВВЕДИТЕ НОМЕР ДЛЯ УДАЛЕНИЯ: \033[0m")
            if not choice:
                return
                
            choice = int(choice) - 1
            titles = list(self.notes.keys())
            
            if 0 <= choice < len(titles):
                title = titles[choice]
                confirm = self.terminal.input_with_typewriter(f"\033[31mПОДТВЕРДИТЕ УДАЛЕНИЕ '{title}'? (y/N): \033[0m")
                if confirm.lower() == 'y':
                    del self.notes[title]
                    self.save_notes()
                    self.terminal.typewriter("\033[32mЗАПИСЬ УДАЛЕНА\033[0m")
                    time.sleep(1)
            else:
                self.terminal.typewriter("\033[31mОШИБКА: НЕВЕРНЫЙ ИНДЕКС\033[0m")
                time.sleep(1)
        except ValueError:
            self.terminal.typewriter("\033[31mОШИБКА: НЕКОРРЕКТНЫЙ ВВОД\033[0m")
            time.sleep(1)
    
    def show_menu(self):
        """Главное меню системы"""
        while True:
            self.terminal.display_header()
            
            self.terminal.typewriter("\033[36m[1] СОЗДАТЬ НОВУЮ ЗАПИСЬ\033[0m", delay=0.01)
            self.terminal.typewriter("\033[36m[2] ПРОСМОТР АРХИВА\033[0m", delay=0.01)
            self.terminal.typewriter("\033[36m[3] ЧТЕНИЕ ЗАПИСИ\033[0m", delay=0.01)
            self.terminal.typewriter("\033[36m[4] РЕДАКТИРОВАНИЕ\033[0m", delay=0.01)
            self.terminal.typewriter("\033[36m[5] УДАЛЕНИЕ\033[0m", delay=0.01)
            self.terminal.typewriter("\033[31m[6] ВЫХОД ИЗ СИСТЕМА\033[0m", delay=0.01)
            print("\033[35m" + "═" * 40 + "\033[0m")
            
            choice = self.terminal.input_with_typewriter("\033[33m[СИСТЕМА] ВЫБЕРИТЕ ОПЕРАЦИЮ: \033[0m")
            
            if choice == '1':
                self.create_note()
            elif choice == '2':
                self.view_notes()
                self.terminal.input_with_typewriter("\n\033[33m[ENTER] ДЛЯ ПРОДОЛЖЕНИЯ...\033[0m")
            elif choice == '3':
                self.read_note()
            elif choice == '4':
                self.edit_note()
            elif choice == '5':
                self.delete_note()
            elif choice == '6':
                self.terminal.display_header()
                self.terminal.typewriter("\033[35mСИСТЕМА ЗАВЕРШАЕТ РАБОТУ...\033[0m")
                self.terminal.matrix_effect(5)
                break
            else:
                self.terminal.typewriter("\033[31mНЕВЕРНАЯ КОМАНДА\033[0m")
                time.sleep(1)

def main():
    notes_app = SecureNotes()
    
    # Начальная анимация
    notes_app.terminal.matrix_effect(3)
    
    # Проверка активации системы
    if not os.path.exists(notes_app.salt_file):
        notes_app.terminal.display_header()
        notes_app.terminal.typewriter("\033[33mОБНАРУЖЕНА НЕАКТИВИРОВАННАЯ СИСТЕМА...\033[0m")
        time.sleep(1)
        if not notes_app.setup_master_password():
            return
    
    # Аутентификация
    if notes_app.authenticate():
        notes_app.show_menu()
    else:
        notes_app.terminal.typewriter("\033[31mСИСТЕМА БЛОКИРОВАНА...\033[0m")
        time.sleep(2)

if __name__ == "__main__":
    main()