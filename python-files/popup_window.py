# popup_window.py
import tkinter as tk
import sys
import os
import tempfile
import json
import time
import subprocess

def get_response_file_path():
    """Возвращает путь к файлу для записи ответа."""
    return os.path.join(tempfile.gettempdir(), "user_response.json")

def save_and_close():
    """Сохраняет текст из поля ввода в файл и закрывает окно."""
    user_input = text_entry.get("1.0", tk.END).strip()

    # --- НЕТ ОКНА ОШИБКИ, просто игнорируем пустой ввод ---
    if not user_input:
        # Ничего не делаем, если поле пустое. Окно не закрывается.
        # Можно добавить визуальную подсказку, если нужно, но без модального окна.
        # Например, мигание поля ввода или изменение его цвета.
        # Пока просто игнорируем.
        print("Пустой ответ. Отправка игнорируется.")
        return
    # --- КОНЕЦ ИГНОРИРОВАНИЯ ПУСТОГО ВВОДА ---

    timestamp = int(time.time())
    response_data = {
        "timestamp": timestamp,
        "response": user_input
    }
    try:
        response_file = get_response_file_path()
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)
        print(f"Ответ сохранен в {response_file}")
    except Exception as e:
        print(f"Ошибка при сохранении ответа: {e}")

    # Закрываем окно и завершаем процесс ТОЛЬКО если ввод был
    root.destroy()
    sys.exit(0)

def on_enter_key(event):
    """Обработчик нажатия Enter в текстовом поле."""
    save_and_close()
    # Не используем "break", чтобы Enter мог создавать новые строки при необходимости
    # Если нужно строго однострочное поле, можно вернуть "break"
    # return "break"

# Получаем текст вопроса из аргументов командной строки
question_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Введите ваш ответ:"

# Создаем главное окно
root = tk.Tk()
root.title("Сообщение от родителя")

# --- Настройки для ПОЛНОЙ БЛОКИРОВКИ и поверх всех ---
# Убираем стандартную строку заголовка
root.overrideredirect(True)
# Делаем окно полноэкранным
root.state('zoomed')
# Устанавливаем окно поверх всех
root.attributes('-topmost', True)
# Убираем возможность изменения размера
root.resizable(False, False)

# --- Создаем собственную строку заголовка ---
title_bar = tk.Frame(root, bg='#2c3e50', relief='raised', bd=0, height=40)
title_bar.pack(fill='x')

title_label = tk.Label(title_bar, text="Сообщение", bg='#2c3e50', fg='white', font=("Arial", 12, "bold"))
title_label.pack(side='left', padx=15, pady=10)

# --- Конец собственной строки заголовка ---

# Создаем и размещаем виджеты в основном контейнере
content_frame = tk.Frame(root, bg='#ecf0f1')
content_frame.pack(fill='both', expand=True, padx=50, pady=30)

# Метка с вопросом
label = tk.Label(content_frame, text=question_text, wraplength=root.winfo_screenwidth()-100, justify='left', font=("Arial", 11), bg='#ecf0f1')
label.pack(pady=(20, 15), padx=20, fill='x')

# Фрейм для поля ввода
input_frame = tk.Frame(content_frame, bg='#ecf0f1')
input_frame.pack(fill='both', expand=True, padx=20, pady=10)

# Метка для поля ввода
text_label = tk.Label(input_frame, text="Ваш ответ:", font=("Arial", 10), bg='#ecf0f1')
text_label.pack(anchor='w')

# Поле ввода (Text)
text_entry = tk.Text(input_frame, height=10, font=("Arial", 11), bg='white', relief='solid', bd=1)
text_entry.pack(fill='both', expand=True, pady=5)
# Привязываем Enter к функции отправки
text_entry.bind('<Return>', on_enter_key)

# Кнопка отправки
send_button = tk.Button(content_frame, text="Отправить ответ", command=save_and_close, font=("Arial", 11, "bold"), bg='#4CAF50', fg='white', relief='raised', padx=20, pady=8)
send_button.pack(pady=20)

# --- Финальные настройки фокуса ---
# Устанавливаем фокус на поле ввода
text_entry.focus_set()

# --- Отключаем возможность закрытия окна стандартными способами ---
def on_closing():
    # Игнорируем попытки закрытия
    pass

root.protocol("WM_DELETE_WINDOW", on_closing)

# --- Упрощенная попытка поддержания фокуса ---
# Вместо агрессивного grab_set и постоянного поднятия, просто делаем topmost один раз
# и устанавливаем фокус. Это должно быть достаточно, чтобы окно было заметным,
# но не мешало вводу.
# root.focus_force() # Уже установили фокус на text_entry

# Запуск главного цикла событий
root.mainloop()