#!/usr/bin/env python3
"""
Servidor Web con Control de Puerto Serie - Versión Simplificada
HTML integrado directamente en el código Python
"""

from flask import Flask, request, jsonify
import serial
import serial.tools.list_ports
import threading
import time
import json
import requests
from browser import launch_windows
app = Flask(__name__)

# Configuración del puerto serie
SERIAL_PORT = None  # Se detectará automáticamente
BAUD_RATE = 9600
ser = None

# Estado actual del sistema
current_state = {
    'status': 'preparada',
    'led': False,
    'serial_connected': False,
    'serial_port': None,
    'available_ports': []
}

# HTML integrado
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Línea 1</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #2ac2d5 0%, #008d9d 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 100%;
            backdrop-filter: blur(10px);
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        .status-section {
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 1.2em;
            color: #555;
            margin-bottom: 15px;
            font-weight: 600;
        }

        .status-selector {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .status-btn {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            min-width: 120px;
        }

        .status-btn.preparada {
            background:  #2196F3;
            color: white;
        }

        .status-btn.funcionando {
            background:#4CAF50;
            color: white;
        }

        .status-btn.con_errores {
            background: #f44336;
            color: white;
        }

        .status-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .status-btn.active {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
        }

        .led-section {
            text-align: center;
            margin-bottom: 40px;
        }

        .led-btn {
            padding: 15px 30px;
            font-size: 1.2em;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            min-width: 200px;
        }

        .led-btn.off {
            background: #ccc;
            color: #666;
        }

        .led-btn.on {
            background: #FF9800;
            color: white;
            box-shadow: 0 0 20px rgba(255, 152, 0, 0.5);
        }

        .led-btn:hover {
            transform: translateY(-2px);
        }

        .status-display {
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.05);
        }

        .status-display h3 {
            color: #333;
            margin-bottom: 10px;
        }

        .port-section {
            margin-bottom: 25px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 10px;
        }

        .port-selector {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }

        .port-select {
            flex: 1;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            min-width: 200px;
        }

        .port-select:focus {
            outline: none;
            border-color: #007bff;
        }

        .connect-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .connect-btn:hover {
            background: #218838;
            transform: translateY(-1px);
        }

        .connect-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
        }

        .refresh-btn {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }

        .refresh-btn:hover {
            background: #138496;
        }
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            border-radius: 8px;
        }

        .connected {
            background: #d4edda;
            color: #155724;
        }

        .disconnected {
            background: #f8d7da;
            color: #721c24;
        }

        .reconnect-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
        }

        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .message.show {
            opacity: 1;
        }

        .message.success {
            background: #d4edda;
            color: #155724;
        }

        .message.error {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
    <div style="text-align: center; margin-bottom: 30px;">
            <img src="https://mma.prnewswire.com/media/2520570/4944716/Insud_Pharma_Logo.jpg?p=publish" 
                 alt="Insud Pharma Logo" 
                 style="max-width: 200px; height: auto; border-radius: 0px; margin-bottom: 20px;">
        </div>        
        <div class="port-section">
            <div class="section-title">🔌 Configuración Puerto Serie</div>
            <div class="port-selector">
                <select id="port-select" class="port-select">
                    <option value="">Seleccionar puerto...</option>
                </select>
                <button class="refresh-btn" onclick="refreshPorts()">🔄</button>
                <button id="connect-btn" class="connect-btn" onclick="connectPort()">Conectar</button>
            </div>
        </div>
        
        <div class="status-display">
            <h3>Estado Actual</h3>
            <h4>Linea de Producción 1</h4>
            <div id="connection-status" class="connection-status disconnected">
            🔌 Puerto Serie: Desconectado
            </div>
            <p>⚙️ Modo: <span id="current-status">Apagado</span></p>
            <p>💡 LED: <span id="led-status">Apagado</span></p>
        </div>
        
        <div class="led-section">
            <div class="section-title">💡 Control de LED</div>
            <button id="led-btn" class="led-btn off" onclick="toggleLED()">
                LED Apagado
            </button>
        </div>

        <div class="status-section">
            <div class="section-title">💻 Estado de la línea</div>
            <div class="status-selector">
                <button class="status-btn preparada active" onclick="setStatus('preparada')">
                    Preparada
                </button>
                <button class="status-btn funcionando" onclick="setStatus('funcionando')">
                    Funcionando
                </button>
                <button class="status-btn con_errores" onclick="setStatus('con_errores')">
                    Con Errores
                </button>
            </div>
        </div>

        

        

        <div id="message" class="message"></div>
    </div>

    <script>
        let currentStatus = 'preparada';
        let ledState = false;
        let serialConnected = false;
        let availablePorts = [];
        let currentPort = null;

        // Actualizar estado inicial
        updateStatus();
        refreshPorts();

        function refreshPorts() {
            fetch('/api/ports')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    availablePorts = data.ports;
                    currentPort = data.current_port;
                    updatePortSelector();
                }
            })
            .catch(error => {
                console.error('Error obteniendo puertos:', error);
                showMessage('Error obteniendo puertos', 'error');
            });
        }

        function updatePortSelector() {
            const portSelect = document.getElementById('port-select');
            portSelect.innerHTML = '<option value="">Seleccionar puerto...</option>';
            
            availablePorts.forEach(port => {
                const option = document.createElement('option');
                option.value = port.device;
                option.textContent = `${port.device} - ${port.description}`;
                if (port.device === currentPort) {
                    option.selected = true;
                }
                portSelect.appendChild(option);
            });
        }

        function connectPort() {
            const portSelect = document.getElementById('port-select');
            const selectedPort = portSelect.value;
            
            if (!selectedPort) {
                showMessage('Por favor selecciona un puerto', 'error');
                return;
            }

            const connectBtn = document.getElementById('connect-btn');
            connectBtn.disabled = true;
            connectBtn.textContent = 'Conectando...';

            fetch('/api/connect_port', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({port: selectedPort})
            })
            .then(response => response.json())
            .then(data => {
                serialConnected = data.connected;
                currentPort = data.port;
                updateConnectionStatus();
                showMessage(data.message, data.success ? 'success' : 'error');
            })
            .catch(error => {
                showMessage('Error de conexión', 'error');
                console.error('Error:', error);
            })
            .finally(() => {
                connectBtn.disabled = false;
                connectBtn.textContent = 'Conectar';
            });
        }

        function setStatus(status) {
            fetch('/api/set_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({status: status})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    currentStatus = status;
                    updateStatusButtons();
                    updateCurrentStatus();
                    showMessage(data.message, 'success');
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                showMessage('Error de conexión', 'error');
                console.error('Error:', error);
            });
        }

        function toggleLED() {
            fetch('/api/toggle_led', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    ledState = data.led_state;
                    updateLEDButton();
                    updateCurrentStatus();
                    showMessage(data.message, 'success');
                } else {
                    showMessage('Error controlando LED', 'error');
                }
            })
            .catch(error => {
                showMessage('Error de conexión', 'error');
                console.error('Error:', error);
            });
        }

        function reconnectSerial() {
            fetch('/api/reconnect_serial', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                serialConnected = data.connected;
                updateConnectionStatus();
                showMessage(data.message, data.success ? 'success' : 'error');
            })
            .catch(error => {
                showMessage('Error de conexión', 'error');
                console.error('Error:', error);
            });
        }

        function updateStatus() {
            fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                currentStatus = data.status;
                ledState = data.led;
                serialConnected = data.serial_connected;
                currentPort = data.serial_port;
                
                updateStatusButtons();
                updateLEDButton();
                updateCurrentStatus();
                updateConnectionStatus();
            })
            .catch(error => {
                console.error('Error obteniendo estado:', error);
            });
        }

        function updateStatusButtons() {
            document.querySelectorAll('.status-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`.status-btn.${currentStatus}`).classList.add('active');
        }

        function updateLEDButton() {
            const ledBtn = document.getElementById('led-btn');
            if (ledState) {
                ledBtn.className = 'led-btn on';
                ledBtn.textContent = 'LED Encendido';
            } else {
                ledBtn.className = 'led-btn off';
                ledBtn.textContent = 'LED Apagado';
            }
            document.getElementById('led-status').textContent = ledState ? 'Encendido' : 'Apagado';
        }

        function updateCurrentStatus() {
            const statusText = {
                'preparada': 'Preparada',
                'funcionando': 'Funcionando',
                'con_errores': 'Con Errores'
            };
            document.getElementById('current-status').textContent = statusText[currentStatus];
        }

        function updateConnectionStatus() {
            const statusDiv = document.getElementById('connection-status');
            if (serialConnected && currentPort) {
                statusDiv.className = 'connection-status connected';
                statusDiv.innerHTML = `🔌 Puerto Serie: Conectado (${currentPort})`;
            } else {
                statusDiv.className = 'connection-status disconnected';
                statusDiv.innerHTML = '🔌 Puerto Serie: Desconectado';
            }
        }

        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = `message ${type} show`;
            
            setTimeout(() => {
                messageDiv.classList.remove('show');
            }, 3000);
        }

        // Actualizar estado cada 10 segundos
        setInterval(updateStatus, 10000);
        
        // Refrescar puertos cada 30 segundos
        setInterval(refreshPorts, 30000);
    </script>
</body>
</html>'''


def get_available_ports():
    """Obtiene lista de puertos serie disponibles"""
    ports = serial.tools.list_ports.comports()
    available_ports = []

    for port in ports:
        port_info = {
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid
        }
        available_ports.append(port_info)

    return available_ports

def cargar_url_desde_json(ruta_archivo):
    with open(ruta_archivo, 'r') as f:
        data = json.load(f)
        return data['url']  # Se espera un JSON como: {"url": "https://ejemplo.com/api"}

def obtener_datos_desde_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Lanza excepción si hay error HTTP
    return response.json()

def extraer_hexcolor(datos):
    if isinstance(datos, list) and len(datos) > 0:
        return datos[0].get('HexColor', None)
    return None
def find_serial_port():
    """Encuentra automáticamente el puerto serie disponible"""
    # Primero intentar conectar al puerto por defecto
    default_port = "/dev/cu.usbserial-110"
    try:
        test_serial = serial.Serial(default_port, BAUD_RATE, timeout=1)
        test_serial.close()
        return default_port
    except:
        print(f"⚠️ No se pudo conectar al puerto por defecto: {default_port}")
    
    # Si no funciona el puerto por defecto, no intentar otros puertos automáticamente
    return None


def init_serial(port=None):
    """Inicializa la conexión serie"""
    global ser, SERIAL_PORT

    if port:
        SERIAL_PORT = port
    elif SERIAL_PORT is None:
        SERIAL_PORT = find_serial_port()

    if SERIAL_PORT:
        try:
            if ser and ser.is_open:
                ser.close()
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            current_state['serial_connected'] = True
            current_state['serial_port'] = SERIAL_PORT
            print(f"✅ Puerto serie conectado: {SERIAL_PORT}")
            return True
        except Exception as e:
            print(f"❌ Error conectando puerto serie: {e}")
            current_state['serial_connected'] = False
            current_state['serial_port'] = None
            return False
    else:
        print("❌ No se encontró ningún puerto serie disponible")
        current_state['serial_connected'] = False
        current_state['serial_port'] = None
        return False


def send_serial_data(data):
    """Envía datos por puerto serie"""
    global ser

    if ser and ser.is_open:
        try:
            message = f"{data}\n"
            ser.write(message.encode())
            print(f"📤 Enviado por serie: {data}")
            return True
        except Exception as e:
            print(f"❌ Error enviando datos serie: {e}")
            current_state['serial_connected'] = False
            return False
    else:
        print("⚠️ Puerto serie no disponible")
        return False


@app.route('/')
def index():
    """Página principal - sirve HTML directamente"""
    return HTML_TEMPLATE


@app.route('/api/ports', methods=['GET'])
def get_ports():
    """Obtiene lista de puertos serie disponibles"""
    ports = get_available_ports()
    current_state['available_ports'] = ports
    return jsonify({
        'success': True,
        'ports': ports,
        'current_port': current_state.get('serial_port')
    })


@app.route('/api/connect_port', methods=['POST'])
def connect_port():
    """Conecta a un puerto serie específico"""
    data = request.get_json()

    if 'port' in data:
        port = data['port']
        success = init_serial(port)

        return jsonify({
            'success': success,
            'connected': current_state['serial_connected'],
            'port': current_state.get('serial_port'),
            'message': f'Conectado a {port}' if success else f'Error conectando a {port}'
        })

    return jsonify({'success': False, 'message': 'Puerto no especificado'})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Obtiene el estado actual del sistema"""
    return jsonify(current_state)


@app.route('/api/set_status', methods=['POST'])
def set_status():
    """Cambia el estado del sistema"""
    data = request.get_json()

    if 'status' in data:
        status = data['status']
        if status in ['preparada', 'funcionando', 'con_errores']:
            current_state['status'] = status

            # Enviar por puerto serie
            serial_message = f"LED_{status.upper()}"
            send_serial_data(serial_message)

            return jsonify({
                'success': True,
                'status': status,
                'message': f'Estado cambiado a: {status}'
            })

    return jsonify({'success': False, 'message': 'Estado inválido'})


@app.route('/api/toggle_led', methods=['POST'])
def toggle_led():
    """Enciende/apaga el LED"""
    current_state['led'] = not current_state['led']
    led_state = "ON" if current_state['led'] else "OFF"

    # Enviar por puerto serie
    serial_message = f"LED_{led_state}"
    send_serial_data(serial_message)

    return jsonify({
        'success': True,
        'led_state': current_state['led'],
        'message': f'LED {"encendido" if current_state["led"] else "apagado"}'
    })


@app.route('/api/reconnect_serial', methods=['POST'])
def reconnect_serial():
    """Intenta reconectar el puerto serie"""
    global ser

    if ser:
        ser.close()

    success = init_serial()

    return jsonify({
        'success': success,
        'connected': current_state['serial_connected'],
        'message': 'Puerto serie reconectado' if success else 'Error reconectando puerto serie'
    })


def main():
    """Función principal"""
    print("🚀 Iniciando servidor web con control serie...")

    # Actualizar lista de puertos disponibles
    current_state['available_ports'] = get_available_ports()

    # Inicializar puerto serie
    init_serial()

    print("\n" + "="*50)
    print("🌐 Servidor Web iniciado")
    print("📍 URL: http://localhost:6700")
    print("🔌 Puerto Serie:", SERIAL_PORT if SERIAL_PORT else "No disponible")
    print("💡 HTML integrado directamente en el código")
    print("="*50 + "\n")
    
    # Iniciar servidor
    try:
        app.run(host='0.0.0.0', port=6700, debug=False, use_reloader=False)

    except KeyboardInterrupt:
        print("\n🛑 Cerrando servidor...")
        if ser and ser.is_open:
            ser.close()
            print("🔌 Puerto serie cerrado")
    except Exception as e:
        print(f"❌ Error en el servidor: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()

if __name__ == '__main__':
    server_thread = threading.Thread(target=main, daemon=True)
    server_thread.start()
    try:
        # Esperar un momento para que el servidor se inicie
        time.sleep(2)
        # Lanzar el navegador
        launch_windows("Línea de Producción 1")
    except Exception as e:
        print(f"❌ Error al lanzar el navegador: {e}")
        