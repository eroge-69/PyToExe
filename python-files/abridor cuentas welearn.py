import webbrowser
import time
import threading
from typing import List
import requests

class InstagramProfileOpener:
    def __init__(self):
        self.base_url = "https://www.instagram.com/{}"
        self.is_paused = False
        self.should_stop = False

    def _wait_for_unpause(self):
        """Espera hasta que el proceso sea despausado"""
        while self.is_paused and not self.should_stop:
            time.sleep(0.1)

    def _listen_for_pause_commands(self):
        """Escucha comandos de pausa en un hilo separado"""
        while not self.should_stop:
            try:
                command = input().strip().lower()
                if command == 'p':
                    if not self.is_paused:
                        self.is_paused = True
                        print("\n⏸️  PROCESO PAUSADO - Presiona 'r' + Enter para reanudar, 's' + Enter para detener")
                elif command == 'r':
                    if self.is_paused:
                        self.is_paused = False
                        print("\n▶️  PROCESO REANUDADO")
                elif command == 's':
                    self.should_stop = True
                    self.is_paused = False
                    print("\n🛑 PROCESO DETENIDO")
                    break
            except EOFError:
                break

    def open_profiles(self, nicknames: List[str], delay: float = 1.5):
        """
        Opens Instagram profiles in Chrome tabs in order with pause/resume functionality

        Args:
            nicknames: List of Instagram usernames in order
            delay: Delay between opening tabs (default 1.5 seconds)
        """
        print(f"Opening {len(nicknames)} Instagram profiles in order...")
        print("\n🎮 CONTROLES:")
        print("  'p' + Enter = Pausar")
        print("  'r' + Enter = Reanudar")
        print("  's' + Enter = Detener")
        print("-" * 50)

        # Reset control flags
        self.is_paused = False
        self.should_stop = False

        # Start listening for pause commands in a separate thread
        listener_thread = threading.Thread(target=self._listen_for_pause_commands, daemon=True)
        listener_thread.start()

        for i, nickname in enumerate(nicknames, 1):
            # Check if process should stop
            if self.should_stop:
                print(f"\n🛑 Proceso detenido por el usuario en {i-1}/{len(nicknames)} perfiles")
                break

            # Wait if paused
            if self.is_paused:
                print(f"\n⏸️  Pausado en perfil {i}/{len(nicknames)} - @{nickname.strip().lstrip('@')}")
                self._wait_for_unpause()

                # Check again if process should stop after unpause
                if self.should_stop:
                    print(f"\n🛑 Proceso detenido por el usuario en {i-1}/{len(nicknames)} perfiles")
                    break

            # Clean nickname (remove @ if present)
            clean_nickname = nickname.strip().lstrip('@')

            # Skip empty nicknames
            if not clean_nickname:
                print(f"Skipping empty nickname at position {i}")
                continue

            # Build Instagram URL
            url = self.base_url.format(clean_nickname)

            print(f"[{i:2d}/{len(nicknames)}] Opening: @{clean_nickname}")
            print(f"         URL: {url}")

            # Open in new Chrome tab
            webbrowser.open_new_tab(url)

            # Add delay between tabs (except for the last one)
            if i < len(nicknames) and not self.should_stop:
                for _ in range(int(delay * 10)):  # Split delay into smaller chunks
                    if self.should_stop:
                        break
                    if self.is_paused:
                        self._wait_for_unpause()
                        if self.should_stop:
                            break
                    time.sleep(0.1)

        # Mark process as finished
        self.should_stop = True

        if not self.should_stop:
            print("-" * 50)
            print("✅ All Instagram profiles opened successfully!")

        print("\n🎮 Proceso finalizado. Presiona Enter para continuar...")

    def open_from_file(self, filename: str, delay: float = 1.5):
        """
        Opens Instagram profiles from a text file with pause/resume functionality

        Args:
            filename: Path to file containing usernames (one per line)
            delay: Delay between opening tabs
        """
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                nicknames = [line.strip() for line in file if line.strip()]

            print(f"Loaded {len(nicknames)} usernames from {filename}")
            self.open_profiles(nicknames, delay)

        except FileNotFoundError:
            print(f"❌ Error: File '{filename}' not found!")
        except Exception as e:
            print(f"❌ Error reading file: {e}")

    def check_accounts_status(self, nicknames: List[str]):
        """
        Automatically checks if Instagram accounts are still active/open with pause/resume functionality

        Args:
            nicknames: List of Instagram usernames to check
        """
        print(f"Checking status of {len(nicknames)} Instagram accounts...")
        print("\n🎮 CONTROLES:")
        print("  'p' + Enter = Pausar")
        print("  'r' + Enter = Reanudar") 
        print("  's' + Enter = Detener")
        print("-" * 50)

        # Reset control flags
        self.is_paused = False
        self.should_stop = False

        # Start listening for pause commands in a separate thread
        listener_thread = threading.Thread(target=self._listen_for_pause_commands, daemon=True)
        listener_thread.start()

        active_accounts = []
        inactive_accounts = []

        for i, nickname in enumerate(nicknames, 1):
            # Check if process should stop
            if self.should_stop:
                print(f"\n🛑 Verificación detenida por el usuario en {i-1}/{len(nicknames)} cuentas")
                break

            # Wait if paused
            if self.is_paused:
                print(f"\n⏸️  Pausado en cuenta {i}/{len(nicknames)} - @{nickname.strip().lstrip('@')}")
                self._wait_for_unpause()

                # Check again if process should stop after unpause
                if self.should_stop:
                    print(f"\n🛑 Verificación detenida por el usuario en {i-1}/{len(nicknames)} cuentas")
                    break

            clean_nickname = nickname.strip().lstrip('@')

            if not clean_nickname:
                print(f"Skipping empty nickname at position {i}")
                continue

            url = self.base_url.format(clean_nickname)

            try:
                # Send a HEAD request to check if profile exists
                response = requests.head(url, timeout=10, allow_redirects=True)

                if response.status_code == 200:
                    print(f"[{i:2d}/{len(nicknames)}] ✅ @{clean_nickname} - Active")
                    active_accounts.append(clean_nickname)
                else:
                    print(f"[{i:2d}/{len(nicknames)}] ❌ @{clean_nickname} - Not accessible (Status: {response.status_code})")
                    inactive_accounts.append(clean_nickname)

            except requests.RequestException as e:
                print(f"[{i:2d}/{len(nicknames)}] ⚠️  @{clean_nickname} - Error checking: {str(e)[:50]}...")
                inactive_accounts.append(clean_nickname)

            # Small delay to avoid rate limiting (with pause check)
            for _ in range(5):  # 0.5 seconds split into smaller chunks
                if self.should_stop:
                    break
                if self.is_paused:
                    self._wait_for_unpause()
                    if self.should_stop:
                        break
                time.sleep(0.1)

        # Mark process as finished
        self.should_stop = True

        print("-" * 50)
        print(f"✅ Active accounts: {len(active_accounts)}")
        print(f"❌ Inactive/Inaccessible accounts: {len(inactive_accounts)}")

        if inactive_accounts:
            print("\nInactive/Inaccessible accounts:")
            for account in inactive_accounts:
                print(f"  - @{account}")

        print("\n🎮 Verificación finalizada. Presiona Enter para continuar...")

def main():
    opener = InstagramProfileOpener()

    while True:
        print("\n🔗 Instagram Profile Opener")
        print("=" * 40)
        print("Choose an option:")
        print("1. Enter usernames manually")
        print("2. Load usernames from file")
        print("3. Check account status (auto-check)")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == '1':
            print("\nEnter Instagram usernames (one per line, press Enter twice to finish):")
            nicknames = []
            while True:
                username = input("Username: ").strip()
                if not username:
                    break
                nicknames.append(username)

            if nicknames:
                delay = float(input(f"\nDelay between tabs (seconds, default 1.5): ") or "1.5")
                opener.open_profiles(nicknames, delay)
            else:
                print("No usernames entered!")

        elif choice == '2':
            filename = input("Enter filename (e.g., usernames.txt): ").strip()
            delay = float(input("Delay between tabs (seconds, default 1.5): ") or "1.5")
            opener.open_from_file(filename, delay)

        elif choice == '3':
            print("\nChoose input method for account checking:")
            print("a. Enter usernames manually")
            print("b. Load from file")

            sub_choice = input("Enter choice (a/b): ").strip().lower()

            if sub_choice == 'a':
                print("\nEnter Instagram usernames to check (one per line, press Enter twice to finish):")
                nicknames = []
                while True:
                    username = input("Username: ").strip()
                    if not username:
                        break
                    nicknames.append(username)

                if nicknames:
                    opener.check_accounts_status(nicknames)
                else:
                    print("No usernames entered!")

            elif sub_choice == 'b':
                filename = input("Enter filename (e.g., usernames.txt): ").strip()
                try:
                    with open(filename, 'r', encoding='utf-8') as file:
                        nicknames = [line.strip() for line in file if line.strip()]

                    print(f"Loaded {len(nicknames)} usernames from {filename}")
                    opener.check_accounts_status(nicknames)

                except FileNotFoundError:
                    print(f"❌ Error: File '{filename}' not found!")
                except Exception as e:
                    print(f"❌ Error reading file: {e}")
            else:
                print("❌ Invalid choice!")

        elif choice == '4':
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice!")

        # Ask if user wants to continue
        continue_choice = input("\nPress Enter to continue or 'q' to quit: ").strip().lower()
        if continue_choice == 'q':
            print("👋 Goodbye!")
            break

# Alternative: Simple function for direct use
def open_instagram_profiles(usernames, delay=1.5):
    """
    Simple function to open Instagram profiles with pause/resume functionality

    Usage:
        open_instagram_profiles(['user1', 'user2', 'user3'])
    """
    opener = InstagramProfileOpener()
    opener.open_profiles(usernames, delay)

if __name__ == "__main__":
    main()
