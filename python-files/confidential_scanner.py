import os
import sys
import ctypes
import platform
import time
from datetime import datetime
import winreg
from pathlib import Path
import shutil

# Настройки кодировки для корректного отображения русских символов
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

class GhostScan:
    def __init__(self):
        self.version = "2.9.0"
        self.keywords = [
            "секретно", "конфиденциально", "NDA", "договор", "соглашение", "акт", "счёт", "накладная", 
            "смета", "отчёт", "баланс", "ведомость", "реестр", "перечень", "список", "заявка", 
            "заявление", "анкета", "паспорт", "свидетельство", "сертификат", "диплом", "аттестат", 
            "удостоверение", "доверенность", "приказ", "распоряжение", "протокол", "решение", 
            "постановление", "инструкция", "положение", "регламент", "устав", "учредительный", 
            "договор", "выписка", "заключение", "справка", "характеристика", "презентация", 
            "коммерческое предложение", "ТЭО", "бизнес-план", "финансовый отчёт", "аудит", "ревизия", 
            "инвентаризация", "налоговая декларация", "бухгалтерия", "зарплата", "кадры", "персонал", 
            "реестр сотрудников", "личное дело", "трудовая книжка", "Паспорт", "ИНН", "СНИЛС", "ОМС", 
            "Водительское", "Страховка", "Медицинский", "Банковская карта", "Реквизиты", "Платёж", 
            "Платёжка", "Перевод", "Транзакция", "Счёт", "Депозит", "Кредит", "Ипотека", "Зарплата", 
            "Премия", "Аванс", "Отпускные", "Больничный", "Пенсия", "золото", "золотодобыча", 
            "золотоносный", "золотой запас", "золотой слиток", "золотой песок", "золотая жила", 
            "золотой рудник", "золотой прииск", "месторождение", "россыпь", "коренное месторождение", 
            "геологоразведка", "геологоразведочные работы", "проба золота", "аффинаж", "драгметаллы", 
            "благородные металлы", "слиток", "шлих", "самородок", "драга", "промывка", "цианирование", 
            "амальгамация", "кучное выщелачивание", "запасы", "ресурсы", "резервы", "балансовые запасы", 
            "содержание золота", "грамм на тонну", "г/т", "золотосодержащий", "кварц", "пирит", 
            "арсенопирит", "добыча", "переработка", "обогащение", "флотация", "гравитация", 
            "цианирование", "электролиз", "лицензия", "недра", "концессия", "горный отвод", "карьер", 
            "разрез", "шахта", "штольня", "штрек", "забой", "экскаватор", "бульдозер", "драга", 
            "промприбор", "мельница", "дробилка", "концентрат", "шлам", "хвосты", "отвалы", "эфеля", 
            "контракт", "соглашение", "договор", "аренда", "лицензия", "патент", "авторское право", 
            "товарный знак", "коммерческая тайна", "персональные данные", "клиент", "заказчик", 
            "поставщик", "подрядчик", "налоговый вычет", "налоговая льгота", "налоговый кодекс", 
            "налоговый учет", "налоговый период", "налоговый орган", "налоговый контроль", 
            "налоговый аудит", "налоговый консультант", "налоговый агент", "налоговый резидент", 
            "налоговый нерезидент"
        ]
        self.extensions = [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".rtf", ".odt", ".zip", ".rar"]
        self.win_ver = platform.release()
        self.desktop_path = self.get_desktop_path()
        self.priority_paths = [self.desktop_path]
        self.standard_paths = [
            str(Path.home() / "Documents"),
            str(Path.home() / "Downloads")
        ]
        self.log_path = str(Path(self.desktop_path) / "GhostScan_Logs")
        self.scan_paths = []
        self.total_files = 0
        self.matches_found = 0

    def get_desktop_path(self):
        """Получаем путь к рабочему столу"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                desktop = winreg.QueryValueEx(key, "Desktop")[0]
                desktop = os.path.expandvars(desktop)
                if os.path.exists(desktop):
                    return desktop
        except:
            pass

        # Проверяем стандартные пути
        possible_paths = [
            Path.home() / "Desktop",
            Path.home() / "Рабочий стол",
            Path.home() / "OneDrive" / "Desktop",
            Path.home() / "OneDrive" / "Рабочий стол",
            Path(os.environ["PUBLIC"]) / "Desktop"
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        # Если ничего не найдено, используем TEMP
        return os.environ["TEMP"]

    def clear_screen(self):
        """Очищаем экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """Выводим заголовок"""
        self.clear_screen()
        print("=" * 80)
        print(f"\n{title.center(80)}\n")
        print("=" * 80)
        print()

    def configure_paths(self):
        """Настройка путей сканирования"""
        while True:
            self.print_header("НАСТРОЙКА ПУТЕЙ СКАНИРОВАНИЯ")
            print("Текущие настройки:")
            print(f"1. Приоритетные пути: {', '.join(self.priority_paths)}")
            print(f"2. Стандартные пути: {', '.join(self.standard_paths)}")
            print("3. Использовать только один путь для сканирования")
            print("4. Вернуться в главное меню\n")

            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == "1":
                new_paths = input("Введите новые приоритетные пути (разделитель ;): ").strip()
                if new_paths:
                    self.priority_paths = [p.strip() for p in new_paths.split(';') if p.strip()]
            elif choice == "2":
                new_paths = input("Введите новые стандартные пути (разделитель ;): ").strip()
                if new_paths:
                    self.standard_paths = [p.strip() for p in new_paths.split(';') if p.strip()]
            elif choice == "3":
                single_path = input("Введите единственный путь для сканирования: ").strip()
                if single_path:
                    self.priority_paths = [single_path]
                    self.standard_paths = []
            elif choice == "4":
                break
            else:
                print("\n[!] Неверный выбор. Попробуйте снова.")
                time.sleep(1)

    def configure_log_path(self):
        """Настройка пути сохранения логов"""
        while True:
            self.print_header("НАСТРОЙКА ПУТИ СОХРАНЕНИЯ ЛОГОВ")
            print(f"Текущий путь: {self.log_path}\n")
            print("1. Использовать путь по умолчанию")
            print("2. Указать новый путь")
            print("3. Вернуться в главное меню\n")

            choice = input("Выберите действие (1-3): ").strip()
            
            if choice == "1":
                self.log_path = str(Path(self.desktop_path) / "GhostScan_Logs")
            elif choice == "2":
                new_path = input("Введите новый путь для сохранения логов: ").strip()
                if new_path:
                    self.log_path = new_path
            elif choice == "3":
                break
            else:
                print("\n[!] Неверный выбор. Попробуйте снова.")
                time.sleep(1)

    def scan_file_name(self, file_path):
        """Проверяем имя файла на совпадения с ключевыми словами"""
        file_name = os.path.basename(file_path).lower()
        matches = []
        
        for keyword in self.keywords:
            if keyword.lower() in file_name:
                matches.append(keyword)
                if len(matches) >= 2:  # Останавливаемся после 2 совпадений
                    break
        
        return matches

    def scan_file_content(self, file_path):
        """Проверяем содержимое файла на совпадения с ключевыми словами (для текстовых файлов)"""
        if not file_path.lower().endswith(('.txt', '.doc', '.docx', '.pdf', '.rtf', '.odt')):
            return []
        
        matches = []
        
        try:
            # Для простоты проверяем только текстовые файлы
            if file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                    for keyword in self.keywords:
                        if keyword.lower() in content:
                            matches.append(keyword)
                            if len(matches) >= 2:  # Останавливаемся после 2 совпадений
                                break
        except:
            pass
        
        return matches

    def turbo_scan(self):
        """Быстрое сканирование (только по именам файлов)"""
        self.print_header(f"Ghost Scan v{self.version} - БЫСТРОЕ СКАНИРОВАНИЕ")
        print("Сканирование запущено...\n")
        
        # Создаем папку для логов, если ее нет
        os.makedirs(self.log_path, exist_ok=True)
        
        # Создаем файл отчета
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.log_path, f"GS_TurboScan_{timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Ghost Scan v{self.version} - БЫСТРОЕ СКАНИРОВАНИЕ\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Пути: {', '.join(self.priority_paths + self.standard_paths)}\n\n")
            
            self.total_files = 0
            self.matches_found = 0
            
            # Объединяем все пути для сканирования
            all_paths = list(set(self.priority_paths + self.standard_paths))
            
            for path in all_paths:
                if not os.path.exists(path):
                    continue
                    
                for root, _, files in os.walk(path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in self.extensions):
                            self.total_files += 1
                            file_path = os.path.join(root, file)
                            
                            # Обновляем прогресс в консоли
                            self.clear_screen()
                            print(f"Ghost Scan v{self.version} - БЫСТРОЕ СКАНИРОВАНИЕ")
                            print(f"\nПрогресс: {self.total_files} файлов")
                            print(f"Найдено совпадений: {self.matches_found}")
                            print(f"Текущий файл: {file[:50]}...\n")
                            
                            # Проверяем имя файла
                            matches = self.scan_file_name(file_path)
                            
                            if matches:
                                self.matches_found += 1
                                f.write(f"[СОВПАДЕНИЕ {self.matches_found}]\n")
                                f.write(f"Файл: {file}\n")
                                f.write(f"Путь: {file_path}\n")
                                f.write(f"Ключевые слова: {', '.join(matches)}\n\n")
            
            # Записываем итоги
            f.write("\n" + "=" * 30 + "\n")
            f.write(f"Всего проверено: {self.total_files} файлов\n")
            f.write(f"Найдено совпадений: {self.matches_found}\n")
            f.write("=" * 30 + "\n")
        
        # Показываем результаты
        self.print_header("СКАНИРОВАНИЕ ЗАВЕРШЕНО")
        print(f"Тип сканирования: БЫСТРОЕ сканирование (по названию файла)")
        print(f"Проверено файлов: {self.total_files}")
        print(f"Найдено совпадений: {self.matches_found}")
        print(f"\nОтчет сохранен: {report_file}")
        
        # Открываем папку с логами
        os.startfile(self.log_path)
        input("\nНажмите Enter для возврата в меню...")

    def deep_scan(self):
        """Глубокое сканирование (проверка содержимого файлов)"""
        self.print_header(f"Ghost Scan v{self.version} - ГЛУБОКОЕ СКАНИРОВАНИЕ")
        print("Сканирование запущено...\n")
        
        # Создаем папку для логов, если ее нет
        os.makedirs(self.log_path, exist_ok=True)
        
        # Создаем файл отчета
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.log_path, f"GS_DeepScan_{timestamp}.txt")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Ghost Scan v{self.version} - ГЛУБОКОЕ СКАНИРОВАНИЕ\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Пути: {', '.join(self.priority_paths + self.standard_paths)}\n\n")
            
            self.total_files = 0
            self.matches_found = 0
            
            # Объединяем все пути для сканирования
            all_paths = list(set(self.priority_paths + self.standard_paths))
            
            for path in all_paths:
                if not os.path.exists(path):
                    continue
                    
                for root, _, files in os.walk(path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in self.extensions):
                            self.total_files += 1
                            file_path = os.path.join(root, file)
                            
                            # Обновляем прогресс в консоли
                            self.clear_screen()
                            print(f"Ghost Scan v{self.version} - ГЛУБОКОЕ СКАНИРОВАНИЕ")
                            print(f"\nПрогресс: {self.total_files} файлов")
                            print(f"Найдено совпадений: {self.matches_found}")
                            print(f"Текущий файл: {file[:50]}...\n")
                            
                            # Проверяем имя файла и содержимое
                            matches = self.scan_file_name(file_path)
                            
                            # Если в имени файла меньше 2 совпадений, проверяем содержимое
                            if len(matches) < 2:
                                content_matches = self.scan_file_content(file_path)
                                matches.extend(content_matches)
                            
                            if matches:
                                self.matches_found += 1
                                f.write(f"[СОВПАДЕНИЕ {self.matches_found}]\n")
                                f.write(f"Файл: {file}\n")
                                f.write(f"Путь: {file_path}\n")
                                f.write(f"Ключевые слова: {', '.join(matches[:2])}\n\n")
            
            # Записываем итоги
            f.write("\n" + "=" * 30 + "\n")
            f.write(f"Всего проверено: {self.total_files} файлов\n")
            f.write(f"Найдено совпадений: {self.matches_found}\n")
            f.write("=" * 30 + "\n")
        
        # Показываем результаты
        self.print_header("СКАНИРОВАНИЕ ЗАВЕРШЕНО")
        print(f"Тип сканирования: ГЛУБОКОЕ сканирование (проверка содержимого файла)")
        print(f"Проверено файлов: {self.total_files}")
        print(f"Найдено совпадений: {self.matches_found}")
        print(f"\nОтчет сохранен: {report_file}")
        
        # Открываем папку с логами
        os.startfile(self.log_path)
        input("\nНажмите Enter для возврата в меню...")

    def main_menu(self):
        """Главное меню программы"""
        while True:
            self.print_header(f"Ghost Scan by Silaev v{self.version} (Windows {self.win_ver})")
            print("Текущие настройки:")
            print(f"  - Приоритетные пути: {', '.join(self.priority_paths)}")
            print(f"  - Стандартные пути: {', '.join(self.standard_paths)}")
            print(f"  - Каталог логов: {self.log_path}\n")
            
            print("Выберите действие:")
            print("=" * 80)
            print("1. ГЛУБОКОЕ сканирование (все указанные папки)")
            print("2. БЫСТРОЕ сканирование (рабочий стол, документы, загрузки)")
            print("3. Настроить пути сканирования")
            print("4. Настроить путь сохранения логов")
            print("5. Выйти\n")
            
            choice = input("Введите номер: ").strip()
            
            if choice == "1":
                self.deep_scan()
            elif choice == "2":
                self.turbo_scan()
            elif choice == "3":
                self.configure_paths()
            elif choice == "4":
                self.configure_log_path()
            elif choice == "5":
                break
            else:
                print("\n[!] Неверный выбор. Попробуйте снова.")
                time.sleep(1)

if __name__ == "__main__":
    # Проверяем, что программа запущена от имени администратора
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    
    if not is_admin:
        print("Для полного доступа к файлам рекомендуется запускать программу от имени администратора.")
        print("Продолжить без прав администратора? (y/n)")
        if input().strip().lower() != 'y':
            sys.exit()
    
    # Запускаем программу
    app = GhostScan()
    app.main_menu()