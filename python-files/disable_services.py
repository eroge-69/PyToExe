
import subprocess

def disable_service(service_name):
    print(f"Disabling {service_name}...")
    result = subprocess.run(["sc", "config", service_name, "start=", "disabled"], capture_output=True, text=True)
    if "SUCCESS" in result.stdout:
        print(f"{service_name} disabled successfully.")
    else:
        print(f"Failed to disable {service_name}. Output:")
        print(result.stdout)

def stop_service(service_name):
    print(f"Stopping {service_name}...")
    result = subprocess.run(["net", "stop", service_name], capture_output=True, text=True)
    if "stopped successfully" in result.stdout.lower():
        print(f"{service_name} stopped successfully.")
    else:
        print(f"Failed to stop {service_name}. Output:")
        print(result.stdout)

if __name__ == "__main__":
    services = ["wuauserv", "bits"]
    for service in services:
        stop_service(service)
        disable_service(service)
    input("Done. Press Enter to exit...")
