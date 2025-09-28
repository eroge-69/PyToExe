import socket
import threading
import time
import json
from datetime import datetime, timedelta
import http.server
import socketserver
import webbrowser
import os

class TimeManager:
    def __init__(self):
        self.clients = {}
        self.sessions = {}
        self.is_running = True
        
    def add_client(self, client_id, client_name, initial_time_minutes=120):
        """Добавить клиента"""
        self.clients[client_id] = {
            'name': client_name,
            'total_time': initial_time_minutes * 60,  # в секундах
            'remaining_time': initial_time_minutes * 60,
            'is_active': False,
            'last_update': time.time()
        }
        
    def start_session(self, client_id):
        """Начать сессию клиента"""
        if client_id in self.clients:
            self.clients[client_id]['is_active'] = True
            self.clients[client_id]['last_update'] = time.time()
            self.sessions[client_id] = {
                'start_time': datetime.now(),
                'initial_time': self.clients[client_id]['remaining_time']
            }
            return True
        return False
    
    def pause_session(self, client_id):
        """Приостановить сессию"""
        if client_id in self.clients and self.clients[client_id]['is_active']:
            self._update_remaining_time(client_id)
            self.clients[client_id]['is_active'] = False
            return True
        return False
    
    def stop_session(self, client_id):
        """Остановить сессию"""
        if client_id in self.clients:
            self._update_remaining_time(client_id)
            self.clients[client_id]['is_active'] = False
            if client_id in self.sessions:
                del self.sessions[client_id]
            return True
        return False
    
    def add_time(self, client_id, minutes):
        """Добавить время клиенту"""
        if client_id in self.clients:
            seconds = minutes * 60
            self.clients[client_id]['total_time'] += seconds
            self.clients[client_id]['remaining_time'] += seconds
            return True
        return False
    
    def _update_remaining_time(self, client_id):
        """Обновить оставшееся время"""
        if client_id in self.clients and self.clients[client_id]['is_active']:
            current_time = time.time()
            elapsed = current_time - self.clients[client_id]['last_update']
            self.clients[client_id]['remaining_time'] -= elapsed
            self.clients[client_id]['last_update'] = current_time
            
            # Если время вышло, автоматически остановить сессию
            if self.clients[client_id]['remaining_time'] <= 0:
                self.clients[client_id]['remaining_time'] = 0
                self.clients[client_id]['is_active'] = False
                if client_id in self.sessions:
                    del self.sessions[client_id]
    
    def get_client_info(self, client_id):
        """Получить информацию о клиенте"""
        if client_id in self.clients:
            self._update_remaining_time(client_id)
            client = self.clients[client_id].copy()
            client['remaining_time_formatted'] = self._format_time(client['remaining_time'])
            client['total_time_formatted'] = self._format_time(client['total_time'])
            return client
        return None
    
    def get_all_clients(self):
        """Получить информацию обо всех клиентах"""
        for client_id in list(self.clients.keys()):
            self._update_remaining_time(client_id)
        
        clients_info = {}
        for client_id, client_data in self.clients.items():
            clients_info[client_id] = {
                'name': client_data['name'],
                'remaining_time': self._format_time(client_data['remaining_time']),
                'total_time': self._format_time(client_data['total_time']),
                'is_active': client_data['is_active'],
                'minutes_remaining': int(client_data['remaining_time'] / 60)
            }
        return clients_info
    
    def _format_time(self, seconds):
        """Форматировать время в читаемый вид"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"
    
    def save_state(self, filename='time_manager_state.json'):
        """Сохранить состояние"""
        state = {
            'clients': self.clients,
            'sessions': {}
        }
        # Конвертируем datetime в строки для сериализации
        for client_id, session in self.sessions.items():
            state['sessions'][client_id] = {
                'start_time': session['start_time'].isoformat(),
                'initial_time': session['initial_time']
            }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filename='time_manager_state.json'):
        """Загрузить состояние"""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            
            self.clients = state['clients']
            self.sessions = {}
            
            # Восстанавливаем datetime объекты
            for client_id, session in state.get('sessions', {}).items():
                self.sessions[client_id] = {
                    'start_time': datetime.fromisoformat(session['start_time']),
                    'initial_time': session['initial_time']
                }
        except FileNotFoundError:
            print("Файл состояния не найден, начинаем с чистого листа")

class WebHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.time_manager = kwargs.pop('time_manager')
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/api/clients':
            self._send_clients_data()
        elif self.path.startswith('/api/'):
            self._send_error(404, "API endpoint not found")
        else:
            # Обслуживаем статические файлы
            if self.path == '/':
                self.path = '/index.html'
            super().do_GET()
    
    def do_POST(self):
        """Обработка POST запросов"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            action = data.get('action')
            client_id = data.get('client_id')
            
            if action == 'start':
                success = self.time_manager.start_session(client_id)
            elif action == 'pause':
                success = self.time_manager.pause_session(client_id)
            elif action == 'stop':
                success = self.time_manager.stop_session(client_id)
            elif action == 'add_time':
                minutes = data.get('minutes', 0)
                success = self.time_manager.add_time(client_id, minutes)
            else:
                success = False
            
            response = {'success': success}
            self._send_json_response(response)
            
        except Exception as e:
            self._send_error(500, str(e))
    
    def _send_clients_data(self):
        """Отправить данные о клиентах"""
        clients_data = self.time_manager.get_all_clients()
        self._send_json_response(clients_data)
    
    def _send_json_response(self, data):
        """Отправить JSON ответ"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, code, message):
        """Отправить ошибку"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'error': message}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def start_web_server(time_manager, port=8080):
    """Запустить веб-сервер"""
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    os.makedirs(web_dir, exist_ok=True)
    
    os.chdir(web_dir)
    
    handler = lambda *args: WebHandler(*args, time_manager=time_manager)
    httpd = socketserver.TCPServer(("", port), handler)
    
    print(f"Веб-панель доступна по адресу: http://localhost:{port}")
    print("Запускаем браузер...")
    webbrowser.open(f'http://localhost:{port}')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nОстанавливаем веб-сервер...")
        httpd.shutdown()

def main():
    # Создаем и инициализируем менеджер времени
    tm = TimeManager()
    tm.load_state()
    
    # Добавляем тестовых клиентов
    if not tm.clients:
        tm.add_client('client1', 'Компьютер 1', 120)
        tm.add_client('client2', 'Компьютер 2', 120)
        tm.add_client('client3', 'Компьютер 3', 120)
        tm.add_client('client4', 'Компьютер 4', 120)
    
    print("Запускаем систему управления временем компьютерного клуба...")
    
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=start_web_server, args=(tm,))
    web_thread.daemon = True
    web_thread.start()
    
    try:
        while True:
            time.sleep(1)
            # Автосохранение каждые 30 секунд
            if int(time.time()) % 30 == 0:
                tm.save_state()
                
    except KeyboardInterrupt:
        print("\nОстанавливаем систему...")
        tm.save_state()
        print("Состояние сохранено")

if __name__ == "__main__":
    main()