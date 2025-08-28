import os
import sys
import subprocess
import json
import time
from colorama import init, Fore, Back, Style

# Инициализация colorama для Windows
init(autoreset=True)


class RelakeLoader:
    def __init__(self):
        self.config_file = "relake_config.json"
        # Фиксированный путь к JAR файлу
        self.jar_path = "C:/RelakeLoader/game/relake.jar"
        self.memory_mb = 2048
        self.load_config()

    def load_config(self):
        """Загрузка конфигурации из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Не загружаем jar_path из конфига, используем фиксированный
                    self.memory_mb = config.get('memory_mb', 2048)
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")

    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            config = {
                'memory_mb': self.memory_mb
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")

    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_logo(self):
        """Вывод ASCII логотипа"""
        logo = f"""
{Fore.CYAN + Style.BRIGHT}
  ██████╗ ███████╗██╗      █████╗ ██╗  ██╗███████╗
  ██╔══██╗██╔════╝██║     ██╔══██╗██║ ██╔╝██╔════╝
  ██████╔╝█████╗  ██║     ███████║█████╔╝ █████╗  
  ██╔══██╗██╔══╝  ██║     ██╔══██║██╔═██╗ ██╔══╝  
  ██║  ██║███████╗███████╗██║  ██║██║  ██╗███████╗
  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
"""
        print(logo)

    def print_menu(self):
        # Статус JAR файла
        print()

        print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} Запуск чита")
        print(f"  {Fore.BLUE}[2]{Style.RESET_ALL} Настроить оперативную память")
        print(f"  {Fore.RED}[0]{Style.RESET_ALL} Выход")
        print()

    def configure_memory(self):
        """Настройка оперативной памяти"""
        self.clear_screen()
        self.print_logo()

        print(f"{Fore.YELLOW}Сейчас установлено:{Style.RESET_ALL} {self.memory_mb} MB")
        print(f"{Fore.YELLOW}Рекомендуемые значения:{Style.RESET_ALL}")
        print(f"  • {Fore.GREEN}4096 MB")
        print(f"  • {Fore.GREEN}8192 MB")

        try:
            memory = input(f"\n{Fore.GREEN}Введите количество МБ: {Style.RESET_ALL}").strip()
            memory_mb = int(memory)

            if memory_mb < 1512:
                print(f"{Fore.RED}✗ Слишком мало памяти! Минимум 1512 MB{Style.RESET_ALL}")
            elif memory_mb > 36384:
                print(f"{Fore.RED}✗ Слишком много памяти! Максимум 36384 MB{Style.RESET_ALL}")
            else:
                self.memory_mb = memory_mb
                self.save_config()

        except ValueError:
            print(f"\n{Fore.RED}✗ Некорректное значение!{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Нажмите Enter для продолжения...{Style.RESET_ALL}")

    def launch_jar(self):
        """Запуск JAR файла"""
        self.clear_screen()
        self.print_logo()
        print(f"{Fore.YELLOW + Style.BRIGHT}ЗАПУСК ЧИТА{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

        if not os.path.exists(self.jar_path):
            print(f"\n{Fore.RED}✗ JAR файл не найден!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Проверьте наличие файла: {self.jar_path}{Style.RESET_ALL}")
            input(f"\n{Fore.YELLOW}Нажмите Enter для продолжения...{Style.RESET_ALL}")
            return

        print(f"\n{Fore.WHITE}Параметры запуска:{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}JAR файл:{Style.RESET_ALL} {os.path.basename(self.jar_path)}")
        print(f"  {Fore.YELLOW}Память:{Style.RESET_ALL} {self.memory_mb} MB")

        print(f"\n{Fore.GREEN}Запуск чита...{Style.RESET_ALL}")

        # Анимация загрузки
        for i in range(5):
            print(f"{Fore.CYAN}{'█' * (i + 1)}{'░' * (4 - i)} {(i + 1) * 20}%{Style.RESET_ALL}", end='\r')
            time.sleep(0.5)

        print(f"\n\n{Fore.GREEN}✓ Запуск выполнен!{Style.RESET_ALL}")

        try:
            # Команда для запуска JAR с настройками памяти
            java_cmd = [
                "java",
                f"-Xmx{self.memory_mb}M",
                f"-Xms{self.memory_mb // 2}M",
                "-jar",
                self.jar_path
            ]

            print(f"{Fore.YELLOW}Команда: {' '.join(java_cmd)}{Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Запускаю Minecraft чит...{Style.RESET_ALL}")

            # Запуск процесса
            subprocess.Popen(java_cmd)
            print(f"{Fore.GREEN}✓ Процесс запущен успешно!{Style.RESET_ALL}")

        except FileNotFoundError:
            print(f"\n{Fore.RED}✗ Java не найдена в системе!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Установите Java для запуска JAR файлов.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}✗ Ошибка запуска: {e}{Style.RESET_ALL}")

        input(f"\n{Fore.YELLOW}Нажмите Enter для продолжения...{Style.RESET_ALL}")

    def run(self):
        """Главный цикл программы"""
        while True:
            self.clear_screen()
            self.print_logo()
            self.print_menu()

            choice = input(f"{Fore.GREEN}Выберите опцию: {Style.RESET_ALL}").strip()

            if choice == '1':
                self.launch_jar()
            elif choice == '2':
                self.configure_memory()
            elif choice == '0':
                self.clear_screen()
                print(f"\n{Fore.CYAN + Style.BRIGHT}До свидания!{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Relake Loader закрывается...{Style.RESET_ALL}\n")
                sys.exit(0)
            else:
                print(f"\n{Fore.RED}Неверная опция! Попробуйте снова.{Style.RESET_ALL}")
                time.sleep(1)


if __name__ == "__main__":
    try:
        loader = RelakeLoader()
        loader.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Программа прервана пользователем.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Критическая ошибка: {e}{Style.RESET_ALL}")
        input("Нажмите Enter для выхода...")