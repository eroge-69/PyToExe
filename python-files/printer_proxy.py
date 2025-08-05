from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import socket
import base64
import io
import os
import logging
from PIL import Image
from config import DEFAULT_PRINTER_IP, DEFAULT_PRINTER_PORT, DEBUG, LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('printer_service.log')
    ]
)
logger = logging.getLogger('printer_proxy')

app = Flask(__name__, template_folder='templates')
app.config['JSON_SORT_KEYS'] = False
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cgi-bin/epos/service.cgi', methods=['POST'])
def print_to_printer():
    try:
        data = request.get_json()

        if not data:
            logger.warning("No data received in request")
            return jsonify({"error": "No data received"}), 400

        # Try to get receipt data directly, or from wrapped format
        receipt_data = data.get("receipt_data", data)

        printer_ip = data.get("printer_ip", DEFAULT_PRINTER_IP)
        printer_port = int(data.get("printer_port", DEFAULT_PRINTER_PORT))
        
        logger.info(f"Print request received for printer at {printer_ip}:{printer_port}")

        # Handle ping request for connection testing
        if receipt_data.get("type") == "ping":
            try:
                # Just test if we can connect to the printer
                with socket.socket() as s:
                    s.settimeout(3)
                    s.connect((printer_ip, printer_port))
                logger.info(f"Printer connection test successful: {printer_ip}:{printer_port}")
                return jsonify({"status": "success", "message": "Printer connection successful"}), 200
            except Exception as e:
                logger.error(f"Printer connection test failed: {printer_ip}:{printer_port} - {str(e)}")
                return jsonify({"status": "error", "message": f"Printer connection failed: {str(e)}"}), 400
                
        elif receipt_data.get("type") == "image" and receipt_data.get("image"):
            logger.info("Processing image print request")
            escpos = build_escpos_image(receipt_data["image"])
            
            # Automatically add beep command to every print job
            # Default: 8 beeps with 300ms duration
            beep_count = 8
            beep_duration = 3
            
            logger.info(f"Automatically adding beep command: {beep_count} beeps of {beep_duration*100}ms")
            # Add beep command after the image data but before the cut command
            # ESC B n t - where n is number of beeps (1-9) and t is duration in 100ms units
            beep_command = bytearray([0x1B, 0x42, beep_count, beep_duration])
            escpos = escpos[:-4] + beep_command + escpos[-4:]  # Insert before the cut command
            
            send_to_printer(printer_ip, printer_port, escpos)
            logger.info("Image printed successfully with beep")
            return jsonify({"status": "success", "message": "Printed Successfully with beep"}), 200

        elif receipt_data.get("type") == "command" and receipt_data.get("command") == "open_cashbox":
            logger.info("Processing cash drawer open command")
            escpos = b'\x1B\x70\x00\x19\xFA'  # Open drawer
            send_to_printer(printer_ip, printer_port, escpos)
            logger.info("Cash drawer command sent")
            return jsonify({"status": "success", "message": "Cash drawer command sent"}), 200
            
        elif receipt_data.get("type") == "text":
            logger.info("Processing text print request")
            escpos = _build_esc_pos_text(receipt_data)
            send_to_printer(printer_ip, printer_port, escpos)
            logger.info("Text printed successfully")
            return jsonify({"status": "success", "message": "Printed Successfully"}), 200
            
        else:
            logger.warning(f"Unsupported receipt type: {receipt_data.get('type')}")
            return jsonify({"status": "error", "message": f"Unsupported receipt type: {receipt_data.get('type')}"}), 400

    except Exception as e:
        logger.error(f"Print failed: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"Print failed: {str(e)}"}), 500

def send_to_printer(ip, port, data):
    try:
        with socket.socket() as s:
            s.settimeout(10)
            logger.debug(f"Connecting to printer at {ip}:{port}")
            s.connect((ip, port))
            logger.debug(f"Sending {len(data)} bytes to printer")
            s.sendall(data)
            logger.debug("Data sent successfully to printer")
    except socket.timeout:
        logger.error(f"Connection to printer at {ip}:{port} timed out")
        raise Exception(f"Connection to printer at {ip}:{port} timed out")
    except ConnectionRefusedError:
        logger.error(f"Connection to printer at {ip}:{port} refused")
        raise Exception(f"Connection to printer at {ip}:{port} refused")
    except Exception as e:
        logger.error(f"Failed to send data to printer at {ip}:{port}: {str(e)}")
        raise

def build_escpos_image(base64_img):
    img_data = base64.b64decode(base64_img)
    image = Image.open(io.BytesIO(img_data)).convert('1')

    # Resize to 384px width max for most receipt printers
    width = min(image.width, 384)
    height = int(image.height * (width / image.width))
    image = image.resize((width, height))

    pixels = list(image.getdata())
    bytes_per_line = (width + 7) // 8

    escpos = bytearray()
    escpos.extend(b'\x1B\x40')  # Initialize
    escpos.extend(b'\x1D\x76\x30\x00')  # Raster bit image command
    escpos.extend(bytes([bytes_per_line & 0xFF, bytes_per_line >> 8]))  # Width
    escpos.extend(bytes([height & 0xFF, height >> 8]))  # Height

    for y in range(height):
        line = bytearray(bytes_per_line)
        for x in range(width):
            pixel = pixels[y * width + x]
            if pixel == 0:  # Black pixel
                line[x // 8] |= (1 << (7 - (x % 8)))
        escpos.extend(line)

    escpos.extend(b'\x1D\x56\x42\x00')  # Full cut
    return escpos

def _build_esc_pos_text(receipt_data):
    commands = bytearray()
    commands.extend(b'\x1B\x40')  # Initialize printer
    commands.extend(b'\x1B\x21\x30')  # Bold + double size
    commands.extend(b'Dine In\n')
    commands.extend(b'\x1B\x21\x00')  # Back to normal

    company = receipt_data.get('company', '')
    table = receipt_data.get('table', '')
    order_num = receipt_data.get('order_number', '')

    if company:
        commands.extend(company.encode('utf-8') + b'\n')
    if table:
        commands.extend(f"Table: {table}\n".encode('utf-8'))
    if order_num:
        commands.extend(f"Order #: {order_num}\n".encode('utf-8'))

    commands.extend(b'\n')

    for line in receipt_data.get('orderlines', []):
        name = line.get('product_name', '')
        qty = line.get('quantity', 1)
        commands.extend(f"{qty} x {name}\n".encode('utf-8'))

    commands.extend(b'\n')
    
    beep_count = 3
    beep_duration = 2
    
    # ESC B n t - where n is number of beeps (1-9) and t is duration in 100ms units
    commands.extend(bytes([0x1B, 0x42, beep_count, beep_duration]))
    
    commands.extend(b'\n')
    commands.extend(b'\x1D\x56\x00')  # Full cut
    return commands


if __name__ == '__main__':
    from config import SERVER_HOST, SERVER_PORT
    logger.info(f"Starting printer proxy server on {SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"Default printer set to {DEFAULT_PRINTER_IP}:{DEFAULT_PRINTER_PORT}")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG)
