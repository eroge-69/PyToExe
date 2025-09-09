import os
import time
TIMING = 6

def main():
    i = 0
    start_prog = input('Для перезапуска сетевого адаптера нажмите - "Enter".')
    os.system("netsh interface set interface \"Ethernet\" disable")
    time.sleep(2)  # Ждем пару секунд
    # Включение сетевого адаптера
    print('Перезапуск сетевого адаптера...')
    os.system("netsh interface set interface \"Ethernet\" enable")
    for i in range(i, TIMING):
        print('.')
        time.sleep(0.5)
        i += 1
    print("Сетевой адаптер успешно перезапущен")
    exit_prog = input('Нажмите "Enter для выхода из программы"')  
    
    
if __name__ == '__main__':
    main()