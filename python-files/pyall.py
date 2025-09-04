import subprocess
import ctypes
import sys
import re

def get_all_sessions():
    """Получает список всех сессий с помощью команды query session."""
    try:
        result = subprocess.run(['query', 'session'], capture_output=True, text=True, encoding='cp866')
        output = result.stdout
        sessions = []
        lines = output.split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) < 2:
                continue
            session_id = parts[-2]
            session_status = parts[-1]
            if not session_id.isdigit():
                continue
            if session_id == '0':
                continue
            sessions.append({'id': session_id, 'status': session_status, 'raw': line})
        return sessions
    except Exception as e:
        print(f"Ошибка при получении списка сессий: {e}")
        return []

def run_tscon(session_id):
    """Запускает команду tscon для подключения к указанной сессии."""
    try:
        subprocess.run(f"tscon {session_id} /password:123qwe", shell=True, check=True)
        print(f"Подключение к сессии {session_id} выполнено успешно.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при подключении: {e}")
        print("Убедитесь, что скрипт запущен с правами администратора.")
    except Exception as e:
        print(f"Общая ошибка: {e}")

def main():
    sessions = get_all_sessions()
    if not sessions:
        print("Сессий не найдено.")
        return

    print("Доступные сессии:")
    for idx, session in enumerate(sessions, 1):
        print(f"{idx}. {session['raw']}")

    try:
        choice = int(input("Выберите сессию для подключения (введите номер): "))
        if 1 <= choice <= len(sessions):
            selected_session = sessions[choice - 1]
            print(f"Подключение к сессии ID: {selected_session['id']}...")
            run_tscon(selected_session['id'])
        else:
            print("Неверный выбор.")
    except ValueError:
        print("Пожалуйста, введите число.")

if __name__ == "__main__":
    main()