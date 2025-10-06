import random
from datetime import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App

host = '127.0.0.1'
port = 29985

class GasDataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/gas/api/data':
            # Generate random values for the gas data
            gas_data = {
                'PUC_Test': 'Airvisor Technologies P. Ltd./AVG500_tController.puc_data',
                'CO': f'{random.uniform(0.001, 0.199):.2f}',
                'HC': f'{random.randint(0, 99):04}',
                'CO2': f'{random.uniform(0.0, 0.200):.2f}',
                'O2': f'{random.uniform(0.0, 30.0):.2f}',
                'RPM': f'{random.randint(2310, 2690):04}',
                'Lambda_CO': f'{random.uniform(0.01, 0.020):.2f}',
                'Lambda': f'{random.uniform(0.98, 1.028):.3f}',
                'Date': datetime.now().strftime('%d-%m-%Y'),
                'Time': datetime.now().strftime('%H:%M'),
                'Reserve': random.randint(1, 10),
                'Status': 'OK'
            }

            # Create the response string
            response_data = json.dumps(gas_data)

            # Set response headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type')
            self.end_headers()

            # Send the response
            self.wfile.write(response_data.encode())

        elif self.path == '/gas/api/data' and self.command == 'OPTIONS':
            # Handle OPTIONS request
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type')
            self.end_headers()

        else:
            # If the requested path is not recognized, return 404 Not Found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

class SmokeDataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/smoke/api/data':
            # Generate random values for the smoke data
            test1_value = f'TR01;{random.uniform(0.20, 0.5):.2f};{random.randint(500, 700)};{random.randint(2100, 2800)};{000}'
            test2_value = f'TR02;{random.uniform(0.20, 0.50):.2f};{random.randint(400, 600)};{random.randint(2150, 2780)};{000}'
            test3_value = f'TR03;{random.uniform(0.20, 0.50):.2f};{random.randint(300, 900)};{random.randint(2173, 2650)};{000}'

            smoke_data = {
                'Date': datetime.now().strftime('%d-%m-%Y'),
                'Flush_Cyl': '#PT;680;1870;000',
                'PUC_Test': 'Airvisor Technologies P. Ltd./AVS100_tController.puc_data',
                'Status': 'OK',
                'Test1': test1_value,
                'Test2': test2_value,
                'Test3': test3_value,
                'Test_AVG': f'#TA;{random.uniform(1.00, 2.30):.2f}',
                'Test_Status': '#TS0',
                'Time': datetime.now().strftime('%H:%M')
            }

            # Create the response string
            response_data = json.dumps(smoke_data)

            # Set response headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type')
            self.end_headers()

            # Send the response
            self.wfile.write(response_data.encode())

        elif self.path == '/smoke/api/data' and self.command == 'OPTIONS':
            # Handle OPTIONS request
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type')
            self.end_headers()

        else:
            # If the requested path is not recognized, return 404 Not Found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

class SmokeDataHandler1(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/smoke/api/data':
            # Generate random values for the smoke data
            test1_value = f'TR01;{random.uniform(0.20, 0.5):.2f};{random.randint(500, 700)};{random.randint(2100, 2800)};{000}'
            test2_value = f'TR02;{random.uniform(0.20, 0.50):.2f};{random.randint(400, 600)};{random.randint(2150, 2780)};{000}'
            test3_value = f'TR03;{random.uniform(0.20, 0.50):.2f};{random.randint(300, 900)};{random.randint(2173, 2650)};{000}'

            smoke_data = {
                'Date': datetime.now().strftime('%d-%m-%Y'),
                'Flush_Cyl': '#PT;680;1870;000',
                'PUC_Test': 'Airvisor Technologies P. Ltd./AVS100_tController.puc_data',
                'Status': 'OK',
                'Test1': test1_value,
                'Test2': test2_value,
                'Test3': test3_value,
                'Test_AVG': f'#TA;{random.uniform(0.01, 0.06):.2f}',
                'Test_Status': '#TS0',
                'Time': datetime.now().strftime('%H:%M')
            }

            # Create the response string
            response_data = json.dumps(smoke_data)

            # Set response headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type')
            self.end_headers()

            # Send the response
            self.wfile.write(response_data.encode())

        elif self.path == '/smoke/api/data' and self.command == 'OPTIONS':
            # Handle OPTIONS request
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-type')
            self.end_headers()

        else:
            # If the requested path is not recognized, return 404 Not Found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

class DataServerApp(App):
    def build(self):
        self.title = "Data Server"
        self.layout = BoxLayout(orientation='vertical', spacing=10)
        self.label = Label(text="Server status: Stopped")
        self.layout.add_widget(self.label)
        self.gas_start_button = Button(text="Start Petrol Server", on_release=self.start_gas_server)
        self.layout.add_widget(self.gas_start_button)
        self.smoke_start_button = Button(text="Start Diesel Server", on_release=self.start_smoke_server)
        self.layout.add_widget(self.smoke_start_button)
        self.smoke_start_button = Button(text="Start Diesel BS6 Server", on_release=self.start_smoke_server1)
        self.layout.add_widget(self.smoke_start_button)
        self.stop_button = Button(text="Stop Server", on_release=self.stop_server, disabled=True)
        self.layout.add_widget(self.stop_button)
        return self.layout

    def start_gas_server(self, instance):
        self.gas_start_button.disabled = True
        self.smoke_start_button.disabled = True
        self.stop_button.disabled = False
        self.label.text = "Server status: Running"

        self.gas_server_thread = threading.Thread(target=self.run_gas_server)
        self.gas_server_thread.daemon = True
        self.gas_server_thread.start()

    def run_gas_server(self):
        server = HTTPServer((host, port), GasDataHandler)
        print(f'Gas Server listening on http://{host}:{port}/gas/api/data')
        server.serve_forever()

    def start_smoke_server(self, instance):
        self.gas_start_button.disabled = True
        self.smoke_start_button.disabled = True
        self.stop_button.disabled = False
        self.label.text = "Server status: Running"

        self.smoke_server_thread = threading.Thread(target=self.run_smoke_server)
        self.smoke_server_thread.daemon = True
        self.smoke_server_thread.start()
    

    def start_smoke_server1(self, instance):
        self.gas_start_button.disabled = True
        self.smoke_start_button.disabled = True
        self.stop_button.disabled = False
        self.label.text = "Server status: Running"

        self.smoke_server_thread = threading.Thread(target=self.run_smoke_server)
        self.smoke_server_thread.daemon = True
        self.smoke_server_thread.start()

    def run_smoke_server1(self):
        server = HTTPServer((host, port), SmokeDataHandler1)
        print(f'Smoke Server listening on http://{host}:{port}/smoke/api/data')
        server.serve_forever()

    def run_smoke_server(self):
        server = HTTPServer((host, port), SmokeDataHandler)
        print(f'Smoke Server listening on http://{host}:{port}/smoke/api/data')
        server.serve_forever()

    def stop_server(self, instance):
        self.gas_start_button.disabled = False
        self.smoke_start_button.disabled = False
        self.stop_button.disabled = True
        self.label.text = "Server status: Stopped"

        if self.gas_server_thread and self.gas_server_thread.is_alive():
            self.gas_server_thread.shutdown()

        if self.smoke_server_thread and self.smoke_server_thread.is_alive():
            self.smoke_server_thread.shutdown()

if __name__ == '__main__':
    DataServerApp().run()
