import psutil
import ctypes
import time
import os
import subprocess
import signal
from ctypes import wintypes
import platform
import sys
from time import sleep
from datetime import datetime, timezone
import logging

THREAD_QUERY_INFORMATION = 64
THREAD_SUSPEND_RESUME = 2
OpenThread = ctypes.windll.kernel32.OpenThread
SuspendThread = ctypes.windll.kernel32.SuspendThread
CloseHandle = ctypes.windll.kernel32.CloseHandle
QueryThreadCycleTime = ctypes.windll.kernel32.QueryThreadCycleTime

def get_thread_cycle_time(thread_id):
    logging.debug(f'Getting cycle time for thread: {thread_id}')
    h_thread = OpenThread(THREAD_QUERY_INFORMATION, False, thread_id)
    if not h_thread:
        logging.error(f'OpenThread failed for thread {thread_id}')
        return 0
    cycle_time = ctypes.c_ulonglong(0)
    if QueryThreadCycleTime(h_thread, ctypes.byref(cycle_time)) == 0:
        logging.error(f'QueryThreadCycleTime failed for thread {thread_id}')
        CloseHandle(h_thread)
        return 0
    CloseHandle(h_thread)
    logging.debug(f'Thread {thread_id} cycle time: {cycle_time.value}')
    return cycle_time.value

def suspend_thread(thread_id):
    logging.debug(f'Suspending thread: {thread_id}')
    h_thread = OpenThread(THREAD_SUSPEND_RESUME, False, thread_id)
    if not h_thread:
        logging.error(f'[ERROR] Could not open thread {thread_id}')
        return False
    result = SuspendThread(h_thread)
    if result == -1:
        logging.error(f'[ERROR] SuspendThread failed for thread {thread_id}')
        CloseHandle(h_thread)
        return False
    CloseHandle(h_thread)
    return True

def find_active_threads(process_name='vgc.exe'):
    logging.debug('Searching for active threads...')
    active_threads = {}
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                for thread in proc.threads():
                    cycles = get_thread_cycle_time(thread.id)
                    if cycles > 10000:
                        active_threads[thread.id] = cycles
        logging.debug(f'Found active threads: {active_threads}')
        return active_threads
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logging.exception(f'[ERROR] {str(e)}')
        return {}

def ensure_vgc_running():
    logging.debug('Ensuring vgc.exe is running...')
    try:
        for proc in os.popen('tasklist').read().splitlines():
            if 'vgc.exe' in proc.lower():
                logging.debug('vgc.exe is already running.')
                return True
        print('[INFO] vgc.exe is not running. Starting Vanguard service...', end='\r')
        result = subprocess.run('sc start vgc', shell=True)
        if result.returncode == 0:
            os.system('cls')
            print('[SUCCESS] Vanguard service started!', end='\r')
            time.sleep(3)
            return True
        logging.error('Failed to start Vanguard service.')
        print('[ERROR] Failed to start Vanguard service.', end='\r')
        return False
    except Exception as e:
        logging.exception('Exception in ensure_vgc_running')
        return False

def display_menu():
    os.system('cls')
    print('\n██╗ ██████╗ ██╗ ██████╗ ██╗ ██╗██████╗ █████╗ ███████╗███████╗\n██║ ██╔═══██╗██║ ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝\n██║ ██║ ██║██║ ██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗\n██║ ██║ ██║██║ ██╔══██╗ ╚██╔╝ ██╔═══╝ ██╔══██║╚════██║╚════██║\n███████╗╚██████╔╝███████╗██████╔╝ ██║ ██║ ██║ ██║███████║███████║\n╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝ ╚═╝ ╚═╝ ╚═╝╚══════╝╚══════╝\ndiscord.gg/cheatshu\n')
    print('1. bypass')
    print('2. Exit')

def close_processes():
    logging.debug('Closing any remaining processes...')

def clear():
    """ Konsolu temizler. """
    if platform.system() == 'Windows':
        os.system('cls')
    elif platform.system() in ['Linux', 'Darwin']:
        os.system('clear')

def main():
    try:
        while True:
            display_menu()
            option = input('Select an option: ')
            if option == '1':
                if not ensure_vgc_running():
                    print('[ERROR] Could not start vgc.exe.', end='\r')
                else:
                    print('\n[INFO] Processing', end='\r')
                    time.sleep(3)
                    initial_threads = find_active_threads()
                    if len(initial_threads) < 4:
                        print('[ERROR] Could not find at least four active threads with a delta cycle above 10,000.', end='\r')
                        logging.error('Active threads count less than 4.')
                        continue
                    print('[Bilgi] League of Legends veya valoranti ac Open league or valorant: 01.00', end='', flush=True)
                    for i in range(60, 0, -1):
                        print(f'\r[Bilgi] League of Legends veya valoranti ac Open league or valorant: 00:{i:02d}', end='', flush=True)
                        time.sleep(1)
                    print('\r[Bilgi] League of Legends veya valoranti ac Open league or valorant: 00:00', end='', flush=True)
                    print('\n[INFO] Timer completed.', end='\r')
                    for thread_id in initial_threads.keys():
                        suspend_thread(thread_id)
                    for i in range(180, 0, -1):
                        minutes, seconds = divmod(i, 60)
                        print(f'\r[bilgi] 3 dakika bekledikten sonra istedigini kullanabilirsin Wait 3 min than inject: {minutes:02d}:{seconds:02d}', end='', flush=True)
                        time.sleep(1)
                    print('\r[INFO] 3 dakika bekledikten sonra istedigini kullanabilirsin Wait 3 min than inject: 00:00', end='', flush=True)
                    print('[INFO] Simdi Hile Kullanabilirsin You can use cheat rn!')
            elif option == '2':
                print('Exiting...', end='\r')
                break
            else:
                print('[ERROR] Invalid option.', end='\r')
    except KeyboardInterrupt:
        logging.info('Program interrupted by the user.')
        print('\n[INFO] Program interrupted by the user.', end='\r')
    except Exception as e:
        logging.exception('Unexpected error in main loop')
        print(f'\n[ERROR] {e}')
        input('\nPress Enter to exit...')
    finally:
        close_processes()
        print('[INFO] Processes closed. Program finished.', end='\r')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception('Fatal error occurred during program startup')
        print(f'\n[ERROR] {e}')
        input('\nPress Enter to exit...')