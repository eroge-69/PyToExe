import winreg
import os

def get_installed_software(registry_path):
    software_list = []
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
        i = 0
        while True:
            try:
                subkey_name = winreg.EnumKey(reg_key, i)
                subkey = winreg.OpenKey(reg_key, subkey_name)
                try:
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    try:
                        version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                    except FileNotFoundError:
                        version = "Unbekannt"
                    software_list.append((name, version))
                except FileNotFoundError:
                    pass
                finally:
                    winreg.CloseKey(subkey)
                i += 1
            except OSError:
                break
        winreg.CloseKey(reg_key)
    except FileNotFoundError:
        pass

    return software_list

def export_to_file(software_list, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write("Installierte Programme:\n")
        file.write("=" * 50 + "\n")
        for name, version in software_list:
            file.write("{} | Version: {}\n".format(name, version))
    print("Liste erfolgreich exportiert: {}".format(output_path))

def main():
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    all_software = []
    for path in registry_paths:
        all_software += get_installed_software(path)

    output_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "Installierte_Programme.txt")
    export_to_file(all_software, output_path)

if __name__ == "__main__":
    main()
