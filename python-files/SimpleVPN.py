import socket
import threading
import json
import time
import sys
import os
from typing import Dict, List
import uuid

os.system('cls' if os.name == 'nt' else 'clear')

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SimpleVPN:
    def __init__(self):
        self.networks: Dict[str, dict] = {}
        self.server_socket = None
        self.running = False
        self.server_ip = self.get_local_ip()
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def print_banner(self):
        print(f"{Colors.CYAN}{'═'*50}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{'W0nderfulX SVPN':^50}{Colors.END}")
        print(f"{Colors.YELLOW}Simple Play With Friends{Colors.END}")
        print(f"{Colors.GREEN}📡 Ваш IP: {self.server_ip}{Colors.END}")
        print(f"{Colors.CYAN}{'═'*50}{Colors.END}")

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind(('0.0.0.0', 4899))
            self.running = True
            
            self.print_banner()
            print(f"{Colors.GREEN}✅ Сервер запущен! (Создайте сеть для подключения к друг другу -> 1){Colors.END}")
            print(f"{Colors.BLUE}📢 Ваш IP Сервера: {self.server_ip}{Colors.END}")
            
            threading.Thread(target=self.handle_messages, daemon=True).start()
            self.show_menu()
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Ошибка запуска: {e}{Colors.END}")
            return False

    def show_menu(self):
        while self.running:
            print(f"\n{Colors.CYAN}{'═'*50}{Colors.END}")
            print(f"{Colors.BOLD}🎮 МЕНЮ СЕРВЕРА:{Colors.END}")
            print(f"{Colors.GREEN}1. Создать сеть{Colors.END}")
            print(f"{Colors.BLUE}2. Список сетей{Colors.END}")
            print(f"{Colors.YELLOW}3. Выход{Colors.END}")
            
            try:
                choice = input(f"\n{Colors.BLUE}Выберите: {Colors.END}").strip()
                
                if choice == "1":
                    self.create_network_menu()
                elif choice == "2":
                    self.show_network_list()
                elif choice == "3":
                    break
                else:
                    print(f"{Colors.RED}❌ Неверный выбор!{Colors.END}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")

    def create_network_menu(self):
        print(f"\n{Colors.CYAN}{'═'*50}{Colors.END}")
        print(f"{Colors.BOLD}🎯 СОЗДАНИЕ СЕТИ:{Colors.END}")
        
        network_name = input(f"{Colors.BLUE}Название сети: {Colors.END}").strip()
        if not network_name:
            print(f"{Colors.RED}❌ Название не может быть пустым!{Colors.END}")
            return
            
        password = input(f"{Colors.BLUE}Пароль (Enter - без пароля): {Colors.END}").strip()
        
        network_id = str(uuid.uuid4())[:8].upper()
        
        self.networks[network_id] = {
            'name': network_name,
            'password': password,
            'members': [],
            'created_at': time.time()
        }
        
        print(f"\n{Colors.GREEN}✅ Сеть создана!{Colors.END}")
        print(f"{Colors.BLUE}📡 Название: {network_name}{Colors.END}")
        print(f"{Colors.BLUE}🔑 ID сети: {network_id}{Colors.END}")
        if password:
            print(f"{Colors.BLUE}🔒 Пароль: {password}{Colors.END}")
        else:
            print(f"{Colors.BLUE}🔓 Без пароля{Colors.END}")
        
        print(f"\n{Colors.YELLOW}📢 Дайте ID сети друзьям для подключения!{Colors.END}")

    def show_network_list(self):
        print(f"\n{Colors.CYAN}{'═'*50}{Colors.END}")
        print(f"{Colors.BOLD}🌐 АКТИВНЫЕ СЕТИ:{Colors.END}")
        
        if not self.networks:
            print(f"{Colors.YELLOW}   Нет созданных сетей{Colors.END}")
            return
            
        for net_id, network in self.networks.items():
            print(f"\n{Colors.GREEN}📡 {network['name']}{Colors.END}")
            print(f"{Colors.BLUE}   ID: {net_id}{Colors.END}")
            print(f"{Colors.BLUE}   Участников: {len(network['members'])}{Colors.END}")
            if network['password']:
                print(f"{Colors.BLUE}   🔒 С паролем{Colors.END}")
            else:
                print(f"{Colors.BLUE}   🔓 Без пароля{Colors.END}")

    def handle_messages(self):
        while self.running:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                message = json.loads(data.decode())
                self.process_message(message, addr)
            except:
                pass

    def process_message(self, message, addr):
        msg_type = message.get('type')
        
        if msg_type == 'join_network':
            self.handle_join_network(message, addr)
        elif msg_type == 'get_networks':
            self.send_network_list(addr)

    def handle_join_network(self, message, addr):
        network_id = message.get('network_id', '').upper()
        password = message.get('password', '')
        client_name = message.get('client_name', 'Неизвестный')
        
        if network_id not in self.networks:
            self.send_error("Сеть не найдена!", addr)
            return
            
        network = self.networks[network_id]
        
        if network['password'] != password:
            self.send_error("Неверный пароль!", addr)
            return
            
        # Добавляем клиента
        client_info = {
            'name': client_name,
            'ip': addr[0],
            'joined_at': time.time()
        }
        
        if client_info not in network['members']:
            network['members'].append(client_info)
        
        print(f"{Colors.BLUE}👥 {client_name} подключился к {network['name']}{Colors.END}")
        
        # Отправляем ответ клиенту
        response = {
            'type': 'join_success',
            'network_name': network['name'],
            'members': network['members']
        }
        self.send_response(response, addr)

    def send_network_list(self, addr):
        networks_list = []
        for net_id, network in self.networks.items():
            networks_list.append({
                'id': net_id,
                'name': network['name'],
                'members_count': len(network['members']),
                'has_password': bool(network['password'])
            })
        
        response = {
            'type': 'networks_list',
            'networks': networks_list
        }
        self.send_response(response, addr)

    def send_response(self, response, addr):
        try:
            self.server_socket.sendto(json.dumps(response).encode(), addr)
        except:
            pass

    def send_error(self, error_msg, addr):
        error_response = {
            'type': 'error',
            'message': error_msg
        }
        self.send_response(error_response, addr)

    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print(f"\n{Colors.YELLOW}🛑 Сервер остановлен{Colors.END}")

class SimpleVPNClient:
    def __init__(self):
        self.client_name = ""
        self.server_ip = ""
        self.udp_socket = None
        self.running = False

    def print_banner(self):
        print(f"{Colors.CYAN}{'═'*50}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.PURPLE}{'W0nderfulX SVPN - Клиент':^50}{Colors.END}")
        print(f"{Colors.CYAN}{'═'*50}{Colors.END}")

    def start_client(self):
        self.print_banner()
        
        self.client_name = input(f"{Colors.BLUE}Ваше имя: {Colors.END}").strip() or "Игрок"
        self.server_ip = input(f"{Colors.BLUE}IP сервера: {Colors.END}").strip()
        
        if not self.server_ip:
            print(f"{Colors.RED}❌ Введите IP сервера!{Colors.END}")
            return
            
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind(('0.0.0.0', 0))  # Случайный порт
            self.running = True
            
            print(f"{Colors.GREEN}✅ Клиент запущен!{Colors.END}")
            
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.show_menu()
            
        except Exception as e:
            print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")

    def show_menu(self):
        while self.running:
            print(f"\n{Colors.CYAN}{'═'*50}{Colors.END}")
            print(f"{Colors.BOLD}🎮 МЕНЮ КЛИЕНТА:{Colors.END}")
            print(f"{Colors.GREEN}1. Подключиться к сети{Colors.END}")
            print(f"{Colors.BLUE}2. Список сетей{Colors.END}")
            print(f"{Colors.YELLOW}3. Выход{Colors.END}")
            
            try:
                choice = input(f"\n{Colors.BLUE}Выберите: {Colors.END}").strip()
                
                if choice == "1":
                    self.join_network_menu()
                elif choice == "2":
                    self.request_network_list()
                elif choice == "3":
                    break
                else:
                    print(f"{Colors.RED}❌ Неверный выбор!{Colors.END}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")

    def join_network_menu(self):
        print(f"\n{Colors.CYAN}{'═'*50}{Colors.END}")
        print(f"{Colors.BOLD}👥 ПОДКЛЮЧЕНИЕ К СЕТИ:{Colors.END}")
        
        network_id = input(f"{Colors.BLUE}ID сети: {Colors.END}").strip().upper()
        if not network_id:
            print(f"{Colors.RED}❌ Введите ID сети!{Colors.END}")
            return
            
        password = input(f"{Colors.BLUE}Пароль (Enter - если нет): {Colors.END}").strip()
        
        message = {
            'type': 'join_network',
            'network_id': network_id,
            'password': password,
            'client_name': self.client_name
        }
        
        self.send_message(message, (self.server_ip, 4899))
        print(f"{Colors.GREEN}✅ Запрос отправлен!{Colors.END}")

    def request_network_list(self):
        message = {'type': 'get_networks'}
        self.send_message(message, (self.server_ip, 4899))
        print(f"{Colors.GREEN}✅ Запрос списка сетей отправлен!{Colors.END}")

    def send_message(self, message, addr):
        try:
            self.udp_socket.sendto(json.dumps(message).encode(), addr)
        except:
            print(f"{Colors.RED}❌ Ошибка отправки{Colors.END}")

    def receive_messages(self):
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(4096)
                message = json.loads(data.decode())
                self.handle_message(message)
            except:
                pass

    def handle_message(self, message):
        msg_type = message.get('type')
        
        if msg_type == 'join_success':
            print(f"\n{Colors.GREEN}✅ Успешное подключение!{Colors.END}")
            print(f"{Colors.BLUE}📡 Сеть: {message['network_name']}{Colors.END}")
            
            members = message.get('members', [])
            if members:
                print(f"{Colors.BLUE}👥 Участники:{Colors.END}")
                for member in members:
                    print(f"   • {member['name']} - {member['ip']}")
            
            print(f"\n{Colors.YELLOW}🎮 Теперь в игре подключайтесь к IP участников!{Colors.END}")
            
        elif msg_type == 'networks_list':
            networks = message.get('networks', [])
            print(f"\n{Colors.BLUE}🌐 ДОСТУПНЫЕ СЕТИ:{Colors.END}")
            
            if not networks:
                print(f"{Colors.YELLOW}   Нет доступных сетей{Colors.END}")
                return
                
            for network in networks:
                status = "🔒" if network['has_password'] else "🔓"
                print(f"\n{status} {network['name']}")
                print(f"   ID: {network['id']}")
                print(f"   Участников: {network['members_count']}")
                
        elif msg_type == 'error':
            print(f"\n{Colors.RED}❌ Ошибка: {message.get('message')}{Colors.END}")

    def stop_client(self):
        self.running = False
        if self.udp_socket:
            self.udp_socket.close()
        print(f"\n{Colors.YELLOW}🛑 Клиент остановлен{Colors.END}")

def main():
    print(f"{Colors.CYAN}{'═'*50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'W0nderfulX SVPN':^50}{Colors.END}")
    print(f"{Colors.YELLOW}Simple Play With Friends{Colors.END}")
    print()
    
    print(f"{Colors.GREEN}1. Создать сеть (Сервер){Colors.END}")
    print(f"{Colors.BLUE}2. Подключиться (Клиент){Colors.END}")
    print(f"{Colors.RED}3. Выход{Colors.END}")
    print()
    
    try:
        choice = input(f"{Colors.BOLD}Выберите (1/2/3): {Colors.END}").strip()
        
        if choice == "1":
            vpn = SimpleVPN()
            if vpn.start_server():
                try:
                    input(f"\n{Colors.YELLOW}Нажмите Enter для выхода...{Colors.END}")
                except:
                    pass
                finally:
                    vpn.stop_server()
                    
        elif choice == "2":
            client = SimpleVPNClient()
            client.start_client()
            client.stop_client()
            
        elif choice == "3":
            print(f"{Colors.YELLOW}👋 До свидания!{Colors.END}")
            
        else:
            print(f"{Colors.RED}❌ Неверный выбор!{Colors.END}")
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}👋 До свидания!{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ Ошибка: {e}{Colors.END}")

if __name__ == "__main__":
    main()