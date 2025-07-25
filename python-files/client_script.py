import threading
import socket
import platform
import http.client
import urllib.parse

SERVER_HOST = "YOUR_PC_IP"  # e.g., 192.168.1.45
SERVER_PORT = 8080
SEND_INTERVAL = 60  # seconds

stop_event = threading.Event()
server_unreachable = False  # Tracks if sending fails

def get_system_info():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    os_info = platform.platform()
    log = f"""
Machine Name: {hostname}
Local IP Address: {local_ip}
Operating System: {os_info}
"""
    return log.strip()

def send_log():
    global server_unreachable

    if stop_event.is_set():
        if server_unreachable:
            print("stopping writing to file")
        else:
            print("Stopping log sending.")
        return

    log = get_system_info()
    try:
        conn = http.client.HTTPConnection(SERVER_HOST, SERVER_PORT, timeout=10)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(log))
        }
        conn.request("POST", "/", log, headers)
        response = conn.getresponse()
        if response.status == 200:
            print("Log sent to server.")
        else:
            raise Exception(f"Server responded with status code: {response.status}")
        conn.close()
    except Exception as e:
        server_unreachable = True
        with open(r"C:\\Users\\kevin\\Documents\\IP logs.txt", "a") as f:
            f.write(log + "\n---\n")
        print("copied to txt file")

    if not stop_event.is_set():
        threading.Timer(SEND_INTERVAL, send_log).start()

def stop_sending():
    stop_event.set()

if __name__ == "__main__":
    send_log()

    if server_unreachable:
        input("Press Enter to stop writing to text file...\n")
    else:
        input("Press Enter to stop sending logs...\n")

    stop_sending()


    # cant work with photo idea