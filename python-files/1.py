import subprocess

def activate_windows(edition, key):
    try:
        # Используем команду slmgr для активации Windows
        command = f'slmgr /ipk {key}'
        subprocess.run(command, shell=True, check=True)

        # Проверяем статус активации
        command = 'slmgr /xpr'
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(result.stdout)

        print(f"Windows {edition} успешно активирован!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при активации Windows {edition}: {e}")

def main():
    print("Выберите версию Windows для активации:")
    print("1. Windows 10/11")
    print("2. Windows 7")
    print("3. Windows 8")

    choice = input("Введите номер версии: ")

    if choice == '1':
        edition = "10/11"
        key = "VK7JG-NPHTM-C97JM-9MPGT-3V66T"  # Пример ключа для Windows 10/11
    elif choice == '2':
        edition = "7"
        key = "33PXH-7Y69K-2G89C-48VK7-PG7K9"  # Пример ключа для Windows 7
    elif choice == '3':
        edition = "8"
        key = "2B87N-8KFHP-D26CC-84F5Q-76C7H"  # Пример ключа для Windows 8
    else:
        print("Неверный выбор. Пожалуйста, выберите правильную версию.")
        return

    activate_windows(edition, key)

if __name__ == "__main__":
    main()