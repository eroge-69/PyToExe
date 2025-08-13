import socket
import requests
import ipaddress
import threading
import queue
import time

def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception as e:
        return f"Error fetching external IP: {e}"

def get_internal_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        internal_ip = s.getsockname()[0]
        s.close()
        return internal_ip
    except Exception as e:
        return f"Error fetching internal IP: {e}"

def scan_network(ip_base, start, end, queue):
    active_hosts = []
    for i in range(start, end + 1):
        ip = ip_base + str(i)
        try:
            socket.setdefaulttimeout(1)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, 80))
            active_hosts.append(ip)
            s.close()
        except:
            pass
    queue.put(active_hosts)

def scan_local_network():
    internal_ip = get_internal_ip()
    if "Error" in internal_ip:
        return internal_ip
    
    try:
        network = ipaddress.ip_network(f"{internal_ip}/24", strict=False)
        ip_base = ".".join(internal_ip.split('.')[:-1]) + "."
        
        threads = []
        queue_result = queue.Queue()
        chunk_size = 256 // 4
        for i in range(4):
            start = i * chunk_size + 1
            end = start + chunk_size - 1 if i < 3 else 256
            thread = threading.Thread(target=scan_network, args=(ip_base, start, end, queue_result))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        active_hosts = []
        while not queue_result.empty():
            active_hosts.extend(queue_result.get())
        
        return active_hosts if active_hosts else "No active hosts found"
    except Exception as e:
        return f"Error scanning network: {e}"

def main():
    print("=== IP Scanner ===")
    print(f"External IP: {get_external_ip()}")
    print(f"Internal IP: {get_internal_ip()}")
    print("\nScanning local network for active hosts (this may take a moment)...")
    result = scan_local_network()
    print("\nActive hosts on local network:")
    if isinstance(result, list):
        for host in result:
            print(host)
    else:
        print(result)

if __name__ == "__main__":
    main()