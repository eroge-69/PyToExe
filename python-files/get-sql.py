import winreg
import win32serviceutil
import win32service
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("sql_instances.txt")

def get_registry_value(root, path, name):
    try:
        with winreg.OpenKey(root, path) as key:
            return winreg.QueryValueEx(key, name)[0]
    except FileNotFoundError:
        return None

def get_subkeys(root, path):
    try:
        with winreg.OpenKey(root, path) as key:
            subkeys = []
            i = 0
            while True:
                try:
                    subkeys.append(winreg.EnumKey(key, i))
                    i += 1
                except OSError:
                    break
            return subkeys
    except FileNotFoundError:
        return []

def get_named_instances():
    instances = []
    instance_path = r"SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, instance_path) as key:
            i = 0
            while True:
                try:
                    instance_name = winreg.EnumValue(key, i)[0]
                    instance_id = winreg.EnumValue(key, i)[1]

                    service_name = "MSSQLSERVER" if instance_name == "MSSQLSERVER" else f"MSSQL${instance_name}"
                    try:
                        status = win32serviceutil.QueryServiceStatus(service_name)[1]
                        status_str = {
                            win32service.SERVICE_STOPPED: "Stopped",
                            win32service.SERVICE_RUNNING: "Running"
                        }.get(status, "Unknown")
                    except:
                        status_str = "Not Found"

                    version = get_registry_value(winreg.HKEY_LOCAL_MACHINE,
                        fr"SOFTWARE\Microsoft\Microsoft SQL Server\{instance_id}\Setup", "Version") or "Unknown"

                    path = get_registry_value(winreg.HKEY_LOCAL_MACHINE,
                        fr"SOFTWARE\Microsoft\Microsoft SQL Server\{instance_id}\Setup", "SQLPath") or "Unknown"

                    instances.append({
                        "Name": instance_name,
                        "Version": version,
                        "Status": status_str,
                        "Path": path
                    })
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        pass
    return instances

def get_orphaned_instances(existing_paths):
    instances = []
    base_key = r"SOFTWARE\Microsoft\Microsoft SQL Server"
    subkeys = get_subkeys(winreg.HKEY_LOCAL_MACHINE, base_key)

    for subkey in subkeys:
        if not subkey.startswith("MSSQL"):
            continue
        path = get_registry_value(winreg.HKEY_LOCAL_MACHINE,
            fr"{base_key}\{subkey}\Setup", "SQLPath")
        if path and path not in existing_paths:
            instances.append({
                "Name": subkey,
                "Version": "Unknown",
                "Status": "Unknown",
                "Path": path
            })
    return instances

def write_to_file(instances, output_path):
    if not instances:
        output_path.write_text("No SQL Server instances found.\n")
        print(f"No SQL Server instances found. Written to {output_path}")
        return

    lines = []
    lines.append("SQL Server Instances")
    lines.append("=" * 80)
    for inst in instances:
        lines.append(f"Name   : {inst['Name']}")
        lines.append(f"Version: {inst['Version']}")
        lines.append(f"Status : {inst['Status']}")
        lines.append(f"Path   : {inst['Path']}")
        lines.append("-" * 80)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote SQL Server instance info to: {output_path}")

def main():
    named = get_named_instances()
    paths = [i["Path"] for i in named]
    orphaned = get_orphaned_instances(paths)
    all_instances = named + orphaned

    write_to_file(all_instances, OUTPUT_FILE)

if __name__ == "__main__":
    main()
