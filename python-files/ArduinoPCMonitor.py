import json
import time
import serial
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# --- Configuration ---
# Adjust your serial port and baud rate to match your Arduino setup
SERIAL_PORT = 'COM7'
BAUD_RATE = 9600

# OpenHardwareMonitor's web server URL
OHM_URL = 'http://localhost:8085/data.json'

# --- Main Functions ---

def get_json_contents(json_url):
    """Fetches and decodes JSON data from a URL."""
    try:
        req = Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urlopen(req, timeout=5).read()
        return json.loads(response.decode('utf-8'))
    except HTTPError as e:
        print(f"[ERROR] HTTPError: {e.code}. Is OpenHardwareMonitor running with the web server enabled?")
    except URLError as e:
        print(f"[ERROR] URLError: {e.reason}. Check the OHM_URL and your network connection.")
    except json.JSONDecodeError:
        print('[ERROR] Invalid JSON received. The data from OHM might be corrupted or empty.')
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred in get_json_contents: {e}")
    return None

def find_node_by_text(node, text_to_find, case_sensitive=False):
    """
    Recursively search for a node by its 'Text' value.
    """
    if node is None:
        return None
        
    node_text = node.get('Text', '')
    search_text = text_to_find
    if not case_sensitive:
        node_text = node_text.lower()
        search_text = search_text.lower()

    if search_text in node_text:
        return node
        
    for child in node.get('Children', []):
        found = find_node_by_text(child, text_to_find, case_sensitive)
        if found:
            return found
    return None

def get_sensor_value(parent_node, sensor_name):
    """
    Finds a specific sensor within a parent node and parses its value.
    """
    if not parent_node:
        return 0.0
        
    sensor_node = find_node_by_text(parent_node, sensor_name)
    if sensor_node and 'Value' in sensor_node:
        value_str = sensor_node.get('Value', '0')
        try:
            numeric_part = value_str.split(' ')[0]
            return float(numeric_part)
        except (ValueError, IndexError):
            return 0.0
    return 0.0

def get_system_info(data_json):
    """
    Extracts all required CPU and GPU info from the main JSON data.
    """
    info = {
        'cpu_temp': 0.0, 'cpu_load': 0.0,
        'gpu_temp': 0.0, 'gpu_load': 0.0, 'vram_used_gb': 0.0
    }

    if not data_json:
        return info

    computer_node = data_json.get('Children', [{}])[0]
    cpu_node = find_node_by_text(computer_node, 'ryzen') or find_node_by_text(computer_node, 'intel')
    gpu_node = find_node_by_text(computer_node, 'nvidia') or find_node_by_text(computer_node, 'amd')

    if not cpu_node: print("[WARNING] CPU device node not found.")
    if not gpu_node: print("[WARNING] GPU device node not found.")

    if cpu_node:
        temps_node = find_node_by_text(cpu_node, 'Temperatures')
        load_node = find_node_by_text(cpu_node, 'Load')
        info['cpu_temp'] = get_sensor_value(temps_node, 'Core (Tctl/Tdie)')
        info['cpu_load'] = get_sensor_value(load_node, 'CPU Total')

    if gpu_node:
        temps_node = find_node_by_text(gpu_node, 'Temperatures')
        load_node = find_node_by_text(gpu_node, 'Load')
        data_node = find_node_by_text(gpu_node, 'Data') # Find the "Data" section for VRAM

        info['gpu_temp'] = get_sensor_value(temps_node, 'GPU Core')
        info['gpu_load'] = get_sensor_value(load_node, 'GPU Core')
        
        # Get VRAM usage in MB from the 'Data' node and convert to GB
        vram_used_mb = get_sensor_value(data_node, 'GPU Memory Used')
        if vram_used_mb > 0:
            info['vram_used_gb'] = vram_used_mb / 1024.0
        
    return info

def main():
    """Main loop to fetch data and send it over serial."""
    ser = None
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[INFO] Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        time.sleep(2)
    except serial.SerialException as e:
        print(f"[ERROR] Could not open serial port '{SERIAL_PORT}': {e}")
        return

    while True:
        data_json = get_json_contents(OHM_URL)
        
        if data_json is None:
            print("[INFO] Failed to get data from OpenHardwareMonitor. Retrying...")
            try:
                ser.write("WAIT\n".encode('ascii'))
            except Exception as e:
                print(f"[ERROR] Serial write failed during error state: {e}")
            time.sleep(2)
            continue

        all_info = get_system_info(data_json)

        # Format data string to send over serial. Note the new 'VU' key.
        # Example: CT:45.3;CU:15.2;GT:52.0;GU:10.5;VU:1.85\n
        data_str = (
            f"CT:{all_info['cpu_temp']:.1f};"
            f"CU:{all_info['cpu_load']:.1f};"
            f"GT:{all_info['gpu_temp']:.1f};"
            f"GU:{all_info['gpu_load']:.1f};"
            f"VU:{all_info['vram_used_gb']:.2f}\n" # VU = VRAM Used (in GB)
        )

        print("Sending:", data_str.strip())

        try:
            ser.write(data_str.encode('ascii'))
        except Exception as e:
            print(f"[ERROR] Serial write failed: {e}")
            # This block attempts to recover the serial connection if it fails.
            try:
                print("[INFO] Attempting to reopen serial port...")
                ser.close()
                time.sleep(1)
                ser.open()
                print("[INFO] Serial port reopened successfully.")
            except Exception as reopen_e:
                # This is the line that was causing the IndentationError. It is now fixed.
                print(f"[ERROR] Failed to reopen serial port: {reopen_e}")
                time.sleep(5) # Wait before the next main loop iteration

        time.sleep(1)

if __name__ == '__main__':
    main()
