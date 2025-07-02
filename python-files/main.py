import os
import platform
import shutil
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

# === Logger setup ===
logger = logging.getLogger("UnbanTool")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler("unban_tool.log", encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# === ASCII Logo ===
ASCII_LOGO = f"""
{Fore.RED}{Style.BRIGHT}
 ██████╗  █████╗ ██████╗ ██╗  ██╗    ███████╗██████╗  ██████╗  ██████╗ ███████╗███████╗██████╗     
 ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝    ██╔════╝██╔══██╗██╔═══██╗██╔═══██╗██╔════╝██╔════╝██╔══██╗    
 ██║  ██║███████║██████╔╝█████╔╝     ███████╗██████╔╝██║   ██║██║   ██║█████╗  █████╗  ██████╔╝    
 ██║  ██║██╔══██║██╔══██╗██╔═██╗     ╚════██║██╔═══╝ ██║   ██║██║   ██║██╔══╝  ██╔══╝  ██╔══██╗    
 ██████╔╝██║  ██║██║  ██║██║  ██╗    ███████║██║     ╚██████╔╝╚██████╔╝██║     ███████╗██║  ██║    
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝      ╚═════╝  ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝    
{Style.RESET_ALL}
"""

class AppPaths:
    """
    Detects and holds app data/cache paths to clean for unban.
    """
    def __init__(self):
        self.paths: Dict[str, Path] = {}
        self.home = Path.home()
        self.os_system = platform.system()
        self._detect_paths()

    def _detect_paths(self):
        logger.debug(f"Detecting app paths for OS: {self.os_system}")
        if self.os_system == "Windows":
            appdata = Path(os.getenv('APPDATA', ''))
            localappdata = Path(os.getenv('LOCALAPPDATA', ''))

            self.paths.update({
                "Discord Data": appdata / "Discord",
                "Discord Cache": localappdata / "Discord" / "Cache",
                "Minecraft": self.home / "AppData" / "Roaming" / ".minecraft",
                "FiveM": appdata / "FiveM",
                "Roblox": self.home / "AppData" / "Local" / "Roblox",
                "CS:GO Config": self.home / "AppData" / "Local" / "Programs" / "Steam" / "steamapps" / "common" / "Counter-Strike Global Offensive" / "csgo" / "cfg",
                "Valorant": localappdata / "Riot Games" / "Riot Client" / "Config",
                "Epic Games": self.home / "Documents" / "Epic",
            })
        else:  # Linux and macOS
            self.paths.update({
                "Discord Config": self.home / ".config" / "discord",
                "Discord Cache": self.home / ".cache" / "discord",
                "Minecraft": self.home / ".minecraft",
                "FiveM": self.home / ".local" / "share" / "FiveM",
                "Roblox": self.home / ".local" / "share" / "Roblox",
                "CS:GO Config": self.home / ".steam" / "steam" / "steamapps" / "common" / "Counter-Strike Global Offensive" / "csgo" / "cfg",
                "Valorant": self.home / ".config" / "riotgames" / "valorant",
                "Epic Games": self.home / "Documents" / "Epic",
            })

    def get_all_paths(self) -> Dict[str, Path]:
        return self.paths

class UnbanCleaner:
    """
    Main cleaner class to delete app data/cache for unban.
    """

    def __init__(self, app_paths: Dict[str, Path]):
        self.app_paths = app_paths

    def remove_path(self, desc: str, path: Path):
        try:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"Removed folder: {desc} -> {path}")
                else:
                    path.unlink()
                    logger.info(f"Removed file: {desc} -> {path}")
                print(f"{Fore.GREEN}[✔] Cleaned: {desc}")
            else:
                logger.debug(f"Not found: {desc} -> {path}")
                print(f"{Fore.YELLOW}[-] Not found: {desc}")
        except Exception as e:
            logger.error(f"Failed to remove {desc} ({path}): {e}")
            print(f"{Fore.RED}[✘] Failed to remove {desc}: {e}")

    def clean_all(self):
        print(f"{Fore.CYAN}Starting unban cleanup...\n{Style.RESET_ALL}")
        for desc, path in self.app_paths.items():
            self.remove_path(desc, path)
            time.sleep(0.15)

        self.flush_dns()
        print(f"\n{Fore.GREEN}Cleanup completed! Please restart your system or applications for changes to apply.{Style.RESET_ALL}")

    @staticmethod
    def flush_dns():
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["ipconfig", "/flushdns"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == "Linux":
                subprocess.run(["systemd-resolve", "--flush-caches"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == "Darwin":
                subprocess.run(["dscacheutil", "-flushcache"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                print(f"{Fore.YELLOW}DNS flush not supported on this OS ({system})")
                logger.warning(f"DNS flush not supported on OS: {system}")
                return
            print(f"{Fore.GREEN}[✔] DNS cache flushed successfully.")
            logger.info("DNS cache flushed.")
        except Exception as e:
            logger.error(f"DNS flush failed: {e}")
            print(f"{Fore.RED}[✘] DNS flush failed: {e}")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_console()
    print(ASCII_LOGO)
    print(f"{Fore.CYAN}{Style.BRIGHT}Dar Spoofer V1\n{Style.RESET_ALL}")

def main_menu(cleaner: UnbanCleaner):
    while True:
        print_header()
        print(f"{Fore.YELLOW}Select an option:\n")
        print(f"{Fore.GREEN}[1] Run Unban Cleanup")
        print(f"{Fore.RED}[0] Exit\n")
        choice = input(f"{Fore.CYAN}Enter your choice: {Style.RESET_ALL}").strip()
        if choice == "1":
            cleaner.clean_all()
            input(f"{Fore.CYAN}\nPress ENTER to return to menu...{Style.RESET_ALL}")
        elif choice == "0":
            print(f"{Fore.MAGENTA}Goodbye, stay safe!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice, please try again.{Style.RESET_ALL}")
            time.sleep(1.5)

def main():
    app_paths = AppPaths().get_all_paths()
    cleaner = UnbanCleaner(app_paths)
    main_menu(cleaner)

if __name__ == "__main__":
    main()
