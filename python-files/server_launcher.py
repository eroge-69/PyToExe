import json
import webbrowser
import socket
import subprocess
import os
from pathlib import Path
import sys
import re
import urllib
import urllib.parse
import urllib.request

def load_config(config_path="config.json"):
    if not Path(config_path).exists():
        print(f"Error: Config file {config_path} not found", file=sys.stderr)
        return None
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            required_keys = ['url', 'port', 'command']
            for key in required_keys:
                if key not in config:
                    print(f"Error: Missing required configuration: {key}", file=sys.stderr)
                    return None
            if not isinstance(config['port'], int) or config['port'] <= 0:
                print("Error: Invalid port number", file=sys.stderr)
                return None
            return config
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config file", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        return None

def open_browser(url, browser_path=None):
    if len(url) == 0:
        if not Path("test.htm").exists():
            print("Error: Missing test.htm")
            return None
        else:
            url = Path("test.htm")  
            fullpath = os.path.abspath(url)
            escapedFullpath = re.escape(os.path.abspath(url))
            url = "file://" + fullpath + '?test=JM'
            print(f"Will use {url}")             
    try:
        if browser_path and os.path.exists(browser_path):
            webbrowser.register('custom', None, webbrowser.BackgroundBrowser(browser_path))
            webbrowser.get('custom').open(url)
        else:
            print(f"Using default browser with {url}")
            webbrowser.open_new(url)
    except Exception as e:
        print(f"Warning: Could not open browser: {e}", file=sys.stderr)

def start_listener(port, command_template):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
            except OSError as e:
                print(f"Error: Could not bind to port {port}: {e}", file=sys.stderr)
                return
            s.listen(5)
            print(f"Listening on port {port} (press Ctrl+C to stop)...")
            try:
                while True:
                    conn, addr = s.accept()
                    with conn:
                        print(f"Connection from {addr}")
                        request = b''
                        data = conn.recv(1024)
                        if not data:
                            continue
                        try:
                            request += data
                            # HTTP request - extract body
                            header_body_split = request.split(b'\r\n\r\n', 1)
                            if len(header_body_split) == 2:
                                headers, body = header_body_split
                                payload = body.decode('utf-8', errors='replace').strip()
                            else:
                                # Just headers, no body
                                payload = ""
                            print(f"Connection from {addr}, received payload: '{payload}'")
                            # Send HTTP 200 response if it was an HTTP request
                            response = (
                                b'HTTP/1.1 200 OK\r\n'
                                b'Content-Length: 0\r\n'
                                b'Connection: close\r\n'
                                b'\r\n'
                            )
                            conn.sendall(response)
                            print(f"Sent: {response}")
                            
                            command = command_template.replace('{data}', payload)
                            print(f"Executing: {command}")
                            subprocess.Popen(command, shell=True)
                        except Exception as e:
                            print(f"Error processing data: {e}", file=sys.stderr)
            except KeyboardInterrupt:
                print("\nStopping server...")
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)

def main():
    config = load_config()
    if not config:
        sys.exit(1)

    print("Configuration loaded successfully")
    open_browser(config['url'], config.get('browser_path'))

    print("Starting server...")
    start_listener(config['port'], config['command'])

if __name__ == '__main__':
    main()
