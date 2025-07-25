import subprocess
import miniupnpc
import socket

# Step 1: Enable UPnP Port Forwarding
def upnp_forward_ports(start_port=31400, end_port=31409):
    try:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()

        local_ip = upnp.lanaddr
        for port in range(start_port, end_port + 1):
            upnp.addportmapping(port, 'TCP', local_ip, port, f'Pi Node Port {port}', '')
            print(f"[UPNP] Port {port} forwarded to {local_ip}")
    except Exception as e:
        print("[UPNP] Failed:", e)

# Step 2: Add Windows Firewall Rules
def allow_firewall_ports(start_port=31400, end_port=31409):
    try:
        for port in range(start_port, end_port + 1):
            subprocess.run(
                ["netsh", "advfirewall", "firewall", "add", "rule",
                 f"name=PiNodePort{port}", "dir=in", "action=allow",
                 "protocol=TCP", f"localport={port}"],
                check=True
            )
            print(f"[FIREWALL] Allowed TCP port {port} through Windows Firewall")
    except subprocess.CalledProcessError as e:
        print("[FIREWALL] Error:", e)

# Step 3: Check if port is open on local machine
def check_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0

if __name__ == "__main__":
    print("Forwarding and allowing ports 31400–31409 for Pi Node...")
    upnp_forward_ports()
    allow_firewall_ports()
    for port in range(31400, 31410):
        status = "open" if check_port_open(port) else "closed"
        print(f"[CHECK] Local port {port} is {status}")
