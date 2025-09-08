#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== НАЧАЛО ВЫПОЛНЕНИЯ ===")
import os
print("Текущая директория:", os.getcwd())
print("Файлы в директории:", os.listdir())

def main():
    """Основная функция приложения"""
    try:
        print("1. Пытаемся импортировать auth_window...")
        
        import auth_window
        print("✅ auth_window импортирован успешно")
        
        from auth_window import AuthWindow
        print("✅ AuthWindow импортирован успешно")
        
        print("2. Запускаем Game Vision Assistant...")
        print("📋 Версия: 1.0") 
        print("👤 Автор: Nikgames")
        print("-" * 40)
        
        # Запуск окна авторизации
        print("3. Создаем окно авторизации...")
        auth_app = AuthWindow()
        print("✅ Окно авторизации создано")
        
        print("4. Запускаем главный цикл...")
        auth_app.run()
        print("✅ Главный цикл завершен")
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        print("Трассировка ошибки:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

print("=== КОНЕЦ ПРОГРАММЫ ===")
input("Нажмите Enter для выхода...")