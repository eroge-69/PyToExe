import os
import sys
import ctypes
import subprocess

def is_admin():
    """Проверка прав администратора"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Перезапуск с правами администратора"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def enable_admin_account():
    """Активация встроенной учетной записи администратора"""
    try:
        subprocess.run(['net', 'user', 'Администратор', '/active:yes'], check=True)
        subprocess.run(['net', 'user', 'Администратор', '*'], check=True)
        print("[+] Встроенная учетная запись 'Администратор' активирована")
    except subprocess.CalledProcessError as e:
        print(f"[!] Ошибка активации: {e}")

def remove_user_restrictions(username):
    """Полное снятие ограничений для пользователя"""
    try:
        # Добавление в группы администраторов
        groups = ['Администраторы', 'Пользователи удаленного рабочего стола']
        for group in groups:
            subprocess.run(['net', 'localgroup', group, username, '/add'], check=True)
        
        # Сброс политик безопасности
        subprocess.run(['secedit', '/configure', '/cfg', '%windir%\inf\defltbase.inf', '/db', 'defltbase.sdb', '/verbose'], check=True)
        
        # Отключение контроля учетных записей (UAC)
        subprocess.run(['reg', 'add', 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System', '/v', 'EnableLUA', '/t', 'REG_DWORD', '/d', '0', '/f'], check=True)
        
        # Разрешение всех политик безопасности
        subprocess.run(['gpupdate', '/force'], check=True)
        
        print(f"\n[+] Все ограничения сняты для пользователя: {username}")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Ошибка: {e}")

def disable_security_features():
    """Отключение функций безопасности Windows"""
    try:
        # Отключение Защитника Windows
        subprocess.run(['reg', 'add', 'HKLM\SOFTWARE\Policies\Microsoft\Windows Defender', '/v', 'DisableAntiSpyware', '/t', 'REG_DWORD', '/d', '1', '/f'], check=True)
        
        # Отключение SmartScreen
        subprocess.run(['reg', 'add', 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer', '/v', 'SmartScreenEnabled', '/t', 'REG_SZ', '/d', 'Off', '/f'], check=True)
        
        # Отключение контроля учетных записей (UAC)
        subprocess.run(['reg', 'add', 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System', '/v', 'EnableLUA', '/t', 'REG_DWORD', '/d', '0', '/f'], check=True)
        
        print("[+] Функции безопасности отключены")
    except subprocess.CalledProcessError as e:
        print(f"[!] Ошибка отключения функций безопасности: {e}")

def reset_local_policies():
    """Сброс локальных групповых политик"""
    try:
        subprocess.run(['secedit', '/configure', '/cfg', '%windir%\inf\defltbase.inf', '/db', 'defltbase.sdb', '/verbose'], check=True)
        subprocess.run(['gpupdate', '/force'], check=True)
        print("[+] Локальные политики сброшены")
    except subprocess.CalledProcessError as e:
        print(f"[!] Ошибка сброса политик: {e}")

def main():
    print("Полный инструмент снятия ограничений Windows")
    print("-------------------------------------------")
    
    if not is_admin():
        print("\n[!] Требуются права администратора")
        print("[*] Пытаюсь повысить привилегии...")
        run_as_admin()
        return
    
    current_user = os.getenv('USERNAME')
    print(f"\nТекущий пользователь: {current_user}")
    
    print("\nВыберите действие:")
    print("1. Полное снятие ограничений для текущего пользователя")
    print("2. Полное снятие ограничений для другого пользователя")
    print("3. Активировать встроенного Администратора и снять все ограничения")
    print("4. Отключить все функции безопасности Windows")
    print("5. Сбросить все локальные политики безопасности")
    print("6. Выход")
    
    choice = input("\nВведите номер (1-6): ")
    
    if choice == '1':
        remove_user_restrictions(current_user)
    elif choice == '2':
        username = input("Введите имя пользователя: ")
        remove_user_restrictions(username)
    elif choice == '3':
        enable_admin_account()
        remove_user_restrictions('Администратор')
    elif choice == '4':
        disable_security_features()
    elif choice == '5':
        reset_local_policies()
    elif choice == '6':
        print("\nВыход...")
        sys.exit(0)
    else:
        print("\n[!] Неверный выбор")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")