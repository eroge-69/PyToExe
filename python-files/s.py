#!/usr/bin/env python3
# ngxhelper.py - консольный помощник (скачивает/открывает официальные страницы)
# Зависимости: tqdm, colorama
# pip install tqdm colorama

import os
import sys
import urllib.request
import webbrowser
import platform
import subprocess
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

# ---- Настройки ----
CLEAR_CMD = "cls" if os.name == "nt" else "clear"

# стабильные прямые ссылки (будут скачиваться)
DIRECT_LINKS = {
    "1": ("https://crystalidea.com/downloads/uninstalltool_setup.exe", "uninstalltool_setup.exe"),
    "2": ("https://simpleunlocker.ds1nc.ru/release/simpleunlocker_release.zip", "simpleunlocker_release.zip"),
    "6": ("https://netcologne.dl.sourceforge.net/project/processhacker/processhacker2/processhacker-2.39-setup.exe?viasf=1", "processhacker-2.39-setup.exe"),
    "11": ("https://www.zhangduo.com/UnknownDeviceIdentifier.exe", "UnknownDeviceIdentifier.exe"),
    "12": ("https://www.defenderui.com/Download/InstallDefenderUI.exe", "InstallDefenderUI.exe"),
    "15": ("https://raw.githubusercontent.com/AdderlyMark/adderly.github.io/main/soft/MakuTweaker%20Setup.exe", "MakuTweaker_Setup.exe"),
    "16": ("https://devbuilds.s.kaspersky-labs.com/devbuilds/KVRT/latest/full/KVRT.exe", "KVRT.exe"),
    "17": ("https://pixeldrain.com/api/file/WwP2mm83?download", "Windows_10_LTSC_21H2.iso"),
    "18": ("https://download.ccleaner.com/ccsetup613.exe", "ccsetup613.exe"),
    "20": ("https://www.7-zip.org/a/7z2301-x64.exe", "7z2301-x64.exe"),
    "23": ("https://download.teamviewer.com/download/TeamViewer_Setup.exe", "TeamViewer_Setup.exe"),
    "24": ("https://download.anydesk.com/AnyDesk.exe", "AnyDesk_Setup.exe"),
    "25": ("https://cdn-fastly.obsproject.com/downloads/OBS-Studio-30.0.2-Full-Installer-x64.exe", "OBS_Studio_Installer.exe"),  # fallback if direct works
    "8_direct": ("https://aka.ms/vs/17/release/vc_redist.x64.exe", "vc_redist_2022_x64.exe"),
    "9_direct": ("https://sdk.lunarg.com/sdk/download/1.3.280.0/windows/VulkanRT-1.3.280.0-Installer.exe", "VulkanRT-1.3.280.0-Installer.exe"),
}

# страницы для открытия (для программ с часто меняющимися direct links)
PAGE_LINKS = {
    "3": "https://www.nvidia.com/en-eu/geforce/drivers/",
    "4": "https://www.amd.com/en/support/download/drivers.html",
    "7": "https://chat.openai.com/",  # chatgpt official (redirects)
    "19": "https://www.malwarebytes.com/mwb-download",  # Malwarebytes download page
    "21": "https://www.cpuid.com/softwares/hwmonitor.html",  # HWMonitor page (CPUID)
    "22": "https://crystalmark.info/en/software/crystaldiskinfo/",  # CrystalDiskInfo page
    "9": "https://vulkan.lunarg.com/sdk/home",  # Vulkan SDK page
    "25_page": "https://obsproject.com/download",  # OBS download page (preferred)
}

# ---- Утилиты ----

def slow_print(text: str, color: str = Fore.WHITE, delay: float = 0.0):
    """Печатает строку цветом; delay оставлен для совместимости (можно 0)."""
    if delay > 0:
        for ch in text:
            sys.stdout.write(color + ch + Style.RESET_ALL)
            sys.stdout.flush()
            import time
            time.sleep(delay)
        print()
    else:
        print(color + text + Style.RESET_ALL)

def download_with_progress(url: str, out_filename: str):
    """Скачивает файл по URL с прогресс-баром. Обрабатывает отсутствие Content-Length."""
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            # получим размер, если есть
            total_header = resp.getheader("Content-Length")
            total = int(total_header) if total_header and total_header.isdigit() else None
            block = 1024 * 8
            with open(out_filename, "wb") as f:
                if total:
                    with tqdm(total=total, unit="B", unit_scale=True, desc=out_filename, ncols=80) as pbar:
                        while True:
                            chunk = resp.read(block)
                            if not chunk:
                                break
                            f.write(chunk)
                            pbar.update(len(chunk))
                else:
                    # неизвестный размер
                    with tqdm(unit="B", unit_scale=True, desc=out_filename, ncols=80) as pbar:
                        while True:
                            chunk = resp.read(block)
                            if not chunk:
                                break
                            f.write(chunk)
                            pbar.update(len(chunk))
        slow_print(f"[+] {out_filename} загружен.", Fore.GREEN)
    except Exception as e:
        slow_print(f"[!] Ошибка загрузки {out_filename}: {e}", Fore.RED)

def open_page(url: str):
    try:
        webbrowser.open(url)
        slow_print(f"[i] Открыта страница: {url}", Fore.GREEN)
    except Exception as e:
        slow_print(f"[!] Не удалось открыть браузер: {e}", Fore.RED)

def open_control_panel():
    if platform.system() != "Windows":
        slow_print("Панель управления доступна только в Windows.", Fore.YELLOW)
        return
    try:
        subprocess.Popen("control", shell=True)
        slow_print("Открываю Панель управления Windows...", Fore.GREEN)
    except Exception as e:
        slow_print(f"Ошибка при открытии Панели управления: {e}", Fore.RED)

def wait_return():
    try:
        input("\nНажмите Enter, чтобы вернуться в меню...")
    except EOFError:
        pass

# ---- Главное меню ----

def main():
    while True:
        os.system(CLEAR_CMD)
        slow_print(r""" 
 _   _  ______  ___          _            _   
| \ | |/ ___\\ \/ / |__   ___| |_ __   ___| |_ 
|  \| | |  _ \\  /| '_ \ / _ \ | '_ \ / _ \ __|
| |\  | |_| |/  \| | | |  __/ | |_) |  __/ |_ 
|_| \_|\____/_/\_\_| |_|\___|_| .__/ \___|\__|
                              |_|             
""", Fore.CYAN)

        slow_print("Программа NGXhelper поможет удалить вирусы и установить нужные программы\n", Fore.GREEN)

        print(Fore.CYAN + "1. Скачать Uninstall Tool (direct)")
        print("2. Скачать SimpleUnlocker (direct)")
        print("3. Открыть сайт NVIDIA драйверов (page)")
        print("4. Открыть сайт AMD драйверов (page)")
        print("5. Скачать ProcessHacker (direct)")
        print("6. Открыть Панель управления Windows")
        print("7. Перейти в ChatGPT (page)")
        print("8. Скачать Visual C++ 2022 Redistributable (direct)")
        print("9. Vulkan Runtime / SDK (open page) — рекомендую открыть страницу")
        print("10. Скачать Reset Windows Update Tool (direct)")
        print("11. Скачать Unknown Device Identifier (direct)")
        print("12. Скачать DefenderUI (direct)")
        print("13. Скачать Visual C++ Redistributable (alias for 8)")
        print("14. Скачать Vulkan Runtime (alias for 9)")
        print("15. Скачать MakuTweaker (direct)")
        print("16. Скачать Kaspersky Virus Removal Tool (direct)")
        print("17. Скачать Windows 10 LTSC 21H2 (PixelDrain direct)")
        print("18. Скачать CCleaner (direct)")
        print("19. Malwarebytes (open download page - ensures current build)")
        print("20. Скачать 7-Zip (direct)")
        print("21. HWMonitor (open CPUID page)")
        print("22. CrystalDiskInfo (open official page)")
        print("23. Скачать TeamViewer (direct)")
        print("24. Скачать AnyDesk (direct)")
        print("25. OBS Studio (open official download page preferred)")
        print("q. Выход\n")

        choice = input(Fore.YELLOW + "Выберите действие: ").strip().lower()

        # direct-download choices
        if choice in DIRECT_LINKS:
            url, filename = DIRECT_LINKS[choice]
            download_with_progress(url, filename)
            wait_return()
        # some numeric aliases mapping to direct keys
        elif choice == "13":
            url, filename = DIRECT_LINKS["8_direct"]
            download_with_progress(url, filename)
            wait_return()
        elif choice == "14":
            # open Vulkan SDK page (safer)
            open_page(PAGE_LINKS["9"])
            wait_return()
        elif choice == "10":
            # Reset Windows Update Tool direct (kept previously)
            download_with_progress("https://github.com/ManuelGil/Reset-Windows-Update-Tool/releases/download/v11.1.0/Portable.zip",
                                   "ResetWindowsUpdateTool_Portable_v11.1.0.zip")
            wait_return()
        elif choice == "25":
            # prefer opening OBS page to get latest installer
            open_page(PAGE_LINKS["25_page"])
            wait_return()
        elif choice in PAGE_LINKS:
            open_page(PAGE_LINKS[choice])
            wait_return()
        elif choice == "6":
            open_control_panel()
            wait_return()
        elif choice == "q":
            slow_print("Выход из программы. Пока!", Fore.GREEN)
            break
        else:
            slow_print("Неверный ввод — попробуйте ещё раз.", Fore.YELLOW)
            wait_return()

if __name__ == "__main__":
    main()
