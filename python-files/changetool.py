
import socket
import datetime

def get_timestamp():
    return datetime.datetime.now().strftime("%H%M%S")

def build_packet(dev_id, new_plate):
    timestamp = get_timestamp()
    return f"*KW{dev_id},001,{timestamp},{new_plate}#".encode()

def send_packet(server_ip, port, packet):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))
        s.sendall(packet)
        return s.recv(4096)

def main():
    print("=== Vehicle Plate Change Tool ===")
    server_ip = "108.181.186.162"
    port = 6803
    dev_id = input("Enter Device ID (e.g., NR09G29088): ").strip()
    new_plate = input("Enter New Plate Number (e.g., KDC307C): ").strip()

    packet = build_packet(dev_id, new_plate)
    print(f"[>] Sending: {packet.decode()}")

    try:
        response = send_packet(server_ip, port, packet)
        print("[<] Response:")
        print(response.decode(errors='ignore'))
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
