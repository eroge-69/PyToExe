import time
import psutil
import cpuinfo

# Check if sensors_temperatures is available
def get_core_temps():
    temps = psutil.sensors_temperatures()
    core_temps = {}
    for name, entries in temps.items():
        for entry in entries:
            if entry.label and 'Core' in entry.label:
                core_num = int(entry.label.replace('Core ', ''))
                core_temps[core_num] = entry.current
    return core_temps

def get_top_processes_by_core(core_indices, interval=1.0):
    # Map process PID to affinity and CPU percent
    proc_info = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            affinity = proc.cpu_affinity()
            cpu_percent = proc.cpu_percent(interval=interval)
            if any(core in affinity for core in core_indices) and cpu_percent > 0:
                proc_info.append((proc.pid, proc.name(), affinity, cpu_percent))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    proc_info.sort(key=lambda x: x[3], reverse=True)
    return proc_info

def main():
    print("Diagnosing overheating for cores 12 and 13.")
    print("Press Ctrl+C to exit.")
    while True:
        try:
            # Step 1: Get core temperatures
            core_temps = get_core_temps()
            t12 = core_temps.get(12, None)
            t13 = core_temps.get(13, None)
            print(f"Core 12 Temp: {t12}°C, Core 13 Temp: {t13}°C")

            # Step 2: Get CPU usage per core
            usage = psutil.cpu_percent(percpu=True)
            print(f"Core 12 Usage: {usage[12]}%, Core 13 Usage: {usage[13]}%")

            # Step 3: Find processes using these cores heavily
            print("Checking for high CPU usage processes on cores 12/13...")
            top_procs = get_top_processes_by_core([12, 13])
            if top_procs:
                print("Processes using cores 12/13:")
                for pid, name, affinity, cpu_percent in top_procs:
                    print(f"PID {pid}, Name: {name}, Affinity: {affinity}, CPU: {cpu_percent}%")
                    # Optionally kill high-usage process:
                    if cpu_percent > 50: # arbitrary threshold
                        answer = input(f"Kill process {name} (PID {pid})? [y/N]: ").strip().lower()
                        if answer == 'y':
                            try:
                                psutil.Process(pid).kill()
                                print(f"Killed process {name} (PID {pid}).")
                            except Exception as e:
                                print(f"Failed to kill process: {e}")
            else:
                print("No high usage processes found on cores 12/13.")

            # Step 4: Suggest fixes
            if t12 and t12 > 85 or t13 and t13 > 85:
                print("Warning: Core temperature is high! (>85°C)")
                print("- Ensure laptop vents are unobstructed.")
                print("- Consider cleaning fans or repasting thermal compound.")
                print("- Check for background processes or malware.")
                print("- Limit CPU-intensive tasks.")

            time.sleep(5)
        except KeyboardInterrupt:
            print("Exiting diagnosis.")
            break

if __name__ == "__main__":
    main()