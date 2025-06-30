import subprocess

# Winget install helper
def install_apps(app_ids):
    for app in app_ids:
        try:
            print(f"\nInstalling {app}...")
            subprocess.run(["winget", "install", "--id", app, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {app}: {e}")

# Category-specific app lists
apps = {
    "1": {  # Internet Browsers
        "name": "Internet Browsers",
        "apps": [
            "Google.Chrome",
            "Mozilla.Firefox",
            "Brave.Brave"
        ]
    },
    "2": {  # Apps
        "name": "Productivity Apps",
        "apps": [
            "Notepad++.Notepad++",
            "Spotify.Spotify",
            "Discord.Discord",
            "7zip.7zip",
            "Microsoft.PowerToys"
        ]
    },
    "3": {  # Actual Free Games
        "name": "Free Games",
        "apps": [
            "Microsoft.MinecraftUWP",      # Minecraft Bedrock (free trial)
            "Microsoft.Mahjong",           # Free Mahjong
            "Microsoft.SolitaireCollection",  # Free Solitaire
            "Microsoft.Minesweeper",       # Free Minesweeper
            "Microsoft.Wordament"          # Word game
        ]
    },
    "4": {  # Video Players
        "name": "Video Players",
        "apps": [
            "VideoLAN.VLC",
            "KMPlayer.KMPlayer"
        ]
    },
    "5": {  # Photo Viewers
        "name": "Photo Viewers",
        "apps": [
            "IrfanSkiljan.IrfanView",
            "XnView.XnView"
        ]
    }
}

# Set French keyboard layout via PowerShell
def set_keyboard_layout_to_french():
    print("\n🔁 Changing keyboard layout to French (AZERTY)...")
    ps_script = (
        "$LangList = Get-WinUserLanguageList; "
        "$LangList[0].InputMethodTips.Clear(); "
        "$LangList[0].InputMethodTips.Add('040c:0000040c'); "
        "Set-WinUserLanguageList $LangList -Force; "
        "Set-WinUILanguageOverride -Language fr-FR; "
        "Set-WinUserLanguageList fr-FR -Force; "
        "Set-WinSystemLocale fr-FR"
    )
    subprocess.run(["powershell", "-Command", ps_script], shell=True)
    print("✅ Layout changed to French. Please restart your PC to apply changes.")

# Menu system
def main():
    while True:
        print("\nWhat services do you want to install?")
        print("1. Internet Browsers")
        print("2. Apps")
        print("3. Free Games")
        print("4. Video Players")
        print("5. Photo Viewers")
        print("6. Change Keyboard Layout to French")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        if choice in apps:
            print(f"\n📦 Installing: {apps[choice]['name']}")
            install_apps(apps[choice]["apps"])
        elif choice == "6":
            set_keyboard_layout_to_french()
        elif choice == "7":
            print("👋 Exiting. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
