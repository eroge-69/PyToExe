import os
import platform
import subprocess

def get_wifi_passwords():
    system = platform.system()
    wifi_data = ""
    try:
        if system == "Windows":
            profiles = subprocess.check_output(
                ["netsh", "wlan", "show", "profiles"],
                universal_newlines=True,
                stderr=subprocess.DEVNULL
            )

            for line in profiles.splitlines():
                if "Profil Tous les utilisateurs" in line or "All User Profile" in line:
                    name = line.split(":")[-1].strip()
                    try:
                        details = subprocess.check_output(
                            ["netsh", "wlan", "show", "profile", name, "key=clear"],
                            universal_newlines=True,
                            stderr=subprocess.DEVNULL
                        )
                        wifi_data += details + "\n\n"
                    except:
                        pass

        elif system == "Linux":
            profiles = subprocess.check_output(
                ["nmcli", "-t", "-f", "NAME", "connection", "show"],
                universal_newlines=True
            ).splitlines()

            for name in profiles:
                try:
                    passwd = subprocess.check_output(
                        ["nmcli", "-s", "-g", "802-11-wireless-security.psk", "connection", "show", name],
                        universal_newlines=True
                    ).strip()
                    wifi_data += f"SSID: {name}\nPassword: {passwd if passwd else 'N/A'}\n\n"
                except:
                    wifi_data += f"SSID: {name}\nPassword: N/A\n\n"

        elif system == "Darwin":
            profiles = subprocess.check_output(
                ["security", "find-generic-password", "-D", "AirPort network password", "-a", "", "-g"],
                universal_newlines=True, stderr=subprocess.STDOUT
            )
            wifi_data += profiles

        else:
            wifi_data = "OS non supporté.\n"

    except Exception as e:
        wifi_data = f"Erreur: {e}\n"

    with open("wifi-info.txt", "a", encoding="utf-8") as f:  
        f.write(wifi_data + "\n---\n")

if __name__ == "__main__":
    get_wifi_passwords()
