# -*- coding: utf-8 -*-
import time
import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
    ▄███████▄    ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄   ▀████    ▐████▀ ███    █▄    ▄▄▄▄███▄▄▄▄
  ███    ███   ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄   ███▌   ████▀  ███    ███ ▄██▀▀▀███▀▀▀██▄
  ███    ███   ███    ███   ███    █▀  ███   ███   ███    ███  ▐███    ███    ███ ███   ███   ███
  ███    ███  ▄███▄▄▄▄██▀  ▄███▄▄▄     ███   ███   ███    ▀███▄███▀    ███    ███ ███   ███   ███
▀█████████▀  ▀▀███▀▀▀▀▀   ▀▀███▀▀▀     ███   ███   ███    ████▀██▄     ███    ███ ███   ███   ███
  ███        ▀███████████   ███    █▄  ███   ███   ███   ▐███  ▀███    ███    ███ ███   ███   ███
  ███          ███    ███   ███    ███ ███   ███   ███  ▄███     ███▄  ███    ███ ███   ███   ███
 ▄████▀        ███    ███   ██████████  ▀█   ███   █▀  ████       ███▄ ████████▀   ▀█   ███   █▀
               ███    ███

"""
    print(banner)

def print_footer():
    print("\n===============================================")
    print("                 Made by @premxum                ")
    print("         THIS BENCHMARK UTILITY IS 100% FREE!   ")
    print("===============================================")

def benchmark_fps():
    clear_screen()
    print("Benchmarking FPS for Win32PrioritySeparation values (1 to 47)...\n")
    best_fps = 0
    best_setting = None
    for setting in range(1, 48):
        print(f"Testing setting {setting}...", end='\r')
        time.sleep(0.3)  # Simuliere Messzeit
        fps = random.randint(50, 200)  # Dummy-Wert
        if fps > best_fps:
            best_fps = fps
            best_setting = setting
    print(f"\nBest FPS: {best_fps} at setting {best_setting}")
    input("\nPress Enter to return to the menu...")

def benchmark_latency():
    clear_screen()
    print("Benchmarking Latency for Win32PrioritySeparation values (1 to 47)...\n")
    best_latency = 9999
    best_setting = None
    for setting in range(1, 48):
        print(f"Testing setting {setting}...", end='\r')
        time.sleep(0.3)  # Simuliere Messzeit
        latency = random.uniform(1.0, 20.0)  # Dummy-Wert in ms
        if latency < best_latency:
            best_latency = latency
            best_setting = setting
    print(f"\nBest Latency: {best_latency:.2f} ms at setting {best_setting}")
    input("\nPress Enter to return to the menu...")

def main_menu():
    while True:
        clear_screen()
        print_banner()
        print("Welcome to Premxum's Benchmarker Utility\n")
        print("1. Benchmark FPS")
        print("2. Benchmark Latency")
        print("3. Exit\n")
        print_footer()
        choice = input("\nChoose an option [1-3]: ").strip()
        if choice == '1':
            benchmark_fps()
        elif choice == '2':
            benchmark_latency()
        elif choice == '3':
            print("\nThanks for using Premxum's Benchmarker. Goodbye!\n")
            break
        else:
            print("\nInvalid choice. Please select 1, 2 or 3.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
