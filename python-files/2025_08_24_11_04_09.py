#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZVZ Зондер Вирус Купол Командер 2025
Шуточный антивирус для развлечения
"""

import os
import time
import random
import hashlib
from datetime import datetime

class ZVZAntivirus:
    def __init__(self):
        self.name = "ZVZ Зондер Вирус Купол Командер 2025"
        self.version = "1.0.0"
        self.threats_found = 0
        self.files_scanned = 0
        self.fake_threats = [
            "Троян.Win32.FakeVirus.A",
            "Червь.Python.JokeWorm.B", 
            "Шпион.Generic.DataStealer.C",
            "Руткит.Boot.HiddenMaster.D",
            "Рекламщик.Browser.PopupMania.E",
            "Майнер.Crypto.BitcoinDigger.F",
            "Кейлоггер.Input.KeyCapture.G",
            "Ботнет.Network.ZombiePC.H"
        ]
        
    def print_header(self):
        print("=" * 60)
        print(f"🛡️  {self.name}")
        print(f"📱 Версия: {self.version}")
        print(f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("=" * 60)
        print("⚠️  ВНИМАНИЕ: Это шуточная программа!")
        print("🎭 Все угрозы - выдуманные!")
        print("=" * 60)
        
    def loading_animation(self, text, duration=2):
        """Анимация загрузки"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        end_time = time.time() + duration
        
        while time.time() < end_time:
            for char in chars:
                print(f"\r{char} {text}", end="", flush=True)
                time.sleep(0.1)
        print(f"\r✅ {text} - Завершено!")
        
    def scan_file(self, filepath):
        """Имитация сканирования файла"""
        self.files_scanned += 1
        
        # Случайно "находим" угрозы
        if random.random() < 0.15:  # 15% шанс найти "угрозу"
            threat = random.choice(self.fake_threats)
            self.threats_found += 1
            print(f"🚨 УГРОЗА ОБНАРУЖЕНА: {threat}")
            print(f"📁 Файл: {filepath}")
            print(f"🔧 Действие: Помещен в карантин (шутка!)")
            print("-" * 40)
            time.sleep(0.5)
        
    def quick_scan(self):
        """Быстрое сканирование"""
        print("\n🚀 Запуск быстрого сканирования...")
        self.loading_animation("Инициализация антивирусного движка", 1)
        self.loading_animation("Загрузка базы данных угроз", 1)
        self.loading_animation("Подготовка к сканированию", 1)
        
        print("\n📂 Сканирование системных файлов...")
        
        # Имитируем сканирование файлов
        fake_files = [
            "C:\\Windows\\System32\\kernel32.dll",
            "C:\\Windows\\System32\\ntdll.dll", 
            "C:\\Program Files\\Internet Explorer\\iexplore.exe",
            "C:\\Users\\User\\Desktop\\document.pdf",
            "C:\\Users\\User\\Downloads\\setup.exe",
            "C:\\Windows\\explorer.exe",
            "C:\\Program Files\\Windows Defender\\MsMpEng.exe",
            "C:\\Users\\User\\AppData\\Local\\Temp\\temp_file.tmp"
        ]
        
        for file in fake_files:
            print(f"🔍 Сканирование: {file}")
            self.scan_file(file)
            time.sleep(0.3)
            
        self.show_results()
        
    def full_scan(self):
        """Полное сканирование"""
        print("\n🔍 Запуск полного сканирования системы...")
        self.loading_animation("Подготовка к глубокому сканированию", 2)
        
        print("\n📁 Сканирование всех дисков...")
        
        # Больше файлов для полного сканирования
        for i in range(25):
            fake_path = f"C:\\FakeFolder{i}\\file_{i}.exe"
            print(f"🔍 Сканирование: {fake_path}")
            self.scan_file(fake_path)
            time.sleep(0.2)
            
        self.show_results()
        
    def show_results(self):
        """Показать результаты сканирования"""
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ")
        print("=" * 50)
        print(f"📁 Файлов просканировано: {self.files_scanned}")
        print(f"🚨 Угроз обнаружено: {self.threats_found}")
        
        if self.threats_found > 0:
            print(f"⚠️  Система под угрозой! (шутка)")
            print(f"🛡️  Рекомендуется очистка (но это не нужно)")
        else:
            print(f"✅ Система чиста!")
            print(f"🛡️  Ваш компьютер защищен!")
            
        print("=" * 50)
        
    def update_database(self):
        """Имитация обновления базы данных"""
        print("\n🔄 Обновление базы данных угроз...")
        self.loading_animation("Подключение к серверу ZVZ", 1)
        self.loading_animation("Загрузка новых сигнатур", 2)
        self.loading_animation("Установка обновлений", 1)
        print("✅ База данных успешно обновлена!")
        print(f"📅 Последнее обновление: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        
    def quarantine_manager(self):
        """Менеджер карантина"""
        print("\n🏥 МЕНЕДЖЕР КАРАНТИНА")
        print("-" * 30)
        
        if self.threats_found == 0:
            print("📭 Карантин пуст")
            print("✅ Угроз не обнаружено")
        else:
            print(f"📦 Файлов в карантине: {self.threats_found}")
            print("🗑️  Все файлы безопасно изолированы (шутка!)")
            
            choice = input("\n🤔 Очистить карантин? (y/n): ").lower()
            if choice == 'y':
                print("🧹 Очистка карантина...")
                time.sleep(1)
                print("✅ Карантин очищен!")
                self.threats_found = 0
                
    def system_info(self):
        """Информация о системе"""
        print("\n💻 ИНФОРМАЦИЯ О СИСТЕМЕ")
        print("-" * 30)
        print(f"🖥️  Операционная система: Защищенная ZVZ OS")
        print(f"🛡️  Статус защиты: АКТИВНА")
        print(f"🔄 Последнее сканирование: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print(f"📊 Всего сканирований: {random.randint(50, 200)}")
        print(f"🚨 Заблокировано угроз: {random.randint(1000, 5000)}")
        
    def run(self):
        """Главное меню программы"""
        self.print_header()
        
        while True:
            print("\n🎮 ГЛАВНОЕ МЕНЮ")
            print("-" * 20)
            print("1. 🚀 Быстрое сканирование")
            print("2. 🔍 Полное сканирование") 
            print("3. 🔄 Обновить базу данных")
            print("4. 🏥 Менеджер карантина")
            print("5. 💻 Информация о системе")
            print("6. 🚪 Выход")
            
            try:
                choice = input("\n🤖 Выберите действие (1-6): ").strip()
                
                if choice == '1':
                    self.quick_scan()
                elif choice == '2':
                    self.full_scan()
                elif choice == '3':
                    self.update_database()
                elif choice == '4':
                    self.quarantine_manager()
                elif choice == '5':
                    self.system_info()
                elif choice == '6':
                    print("\n👋 Спасибо за использование ZVZ Антивируса!")
                    print("🛡️  Оставайтесь в безопасности! (это шутка)")
                    break
                else:
                    print("❌ Неверный выбор! Попробуйте снова.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Программа завершена пользователем")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    try:
        antivirus = ZVZAntivirus()
        antivirus.run()
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")

if __name__ == "__main__":
    main()