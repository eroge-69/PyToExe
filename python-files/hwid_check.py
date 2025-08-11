import subprocess
import platform


def get_hwid():
    system = platform.system()
    hwid_info = {}

    try:
        if system == "Windows":
            # Pobranie informacji o CPU
            cpu_info = subprocess.check_output(
                ["wmic", "cpu", "get", "ProcessorId"], stderr=subprocess.DEVNULL
            ).decode().split("\n")[1].strip()
            hwid_info["CPU_ID"] = cpu_info

            # Pobranie numeru seryjnego płyty głównej
            mb_info = subprocess.check_output(
                ["wmic", "baseboard", "get", "SerialNumber"], stderr=subprocess.DEVNULL
            ).decode().split("\n")[1].strip()
            hwid_info["Motherboard_SN"] = mb_info

            # Pobranie numeru seryjnego dysku
            disk_info = subprocess.check_output(
                ["wmic", "diskdrive", "get", "SerialNumber"], stderr=subprocess.DEVNULL
            ).decode().split("\n")[1].strip()
            hwid_info["Disk_SN"] = disk_info

        elif system == "Linux":
            # CPU
            cpu_info = subprocess.check_output(
                ["cat", "/proc/cpuinfo"], stderr=subprocess.DEVNULL
            ).decode()
            for line in cpu_info.split("\n"):
                if "Serial" in line or "processor" in line.lower():
                    hwid_info["CPU_ID"] = line.split(":")[-1].strip()
                    break

            # Płyta główna
            try:
                mb_info = subprocess.check_output(
                    ["sudo", "dmidecode", "-s", "baseboard-serial-number"], stderr=subprocess.DEVNULL
                ).decode().strip()
                hwid_info["Motherboard_SN"] = mb_info
            except:
                hwid_info["Motherboard_SN"] = "Brak uprawnień lub brak dostępu"

            # Dysk
            disk_info = subprocess.check_output(
                ["lsblk", "-o", "NAME,SERIAL"], stderr=subprocess.DEVNULL
            ).decode()
            hwid_info["Disk_SN"] = disk_info

        else:
            return {"Error": "System nieobsługiwany"}

    except Exception as e:
        hwid_info["Error"] = str(e)

    return hwid_info


if __name__ == "__main__":
    info = get_hwid()
    for key, value in info.items():
        print(f"{key}: {value}")
