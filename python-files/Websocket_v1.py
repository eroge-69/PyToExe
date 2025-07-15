import asyncio
import websockets
import nidaqmx
import tkinter as tk
from tkinter import ttk
from datetime import datetime

async def switch_output(device_name, channel_name, io_name, state):
    digital_output_channel = f"{device_name}/{channel_name}/{io_name}"
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(digital_output_channel)
        task.write(state)
        print(f"{digital_output_channel} {'eingeschaltet' if state else 'ausgeschaltet'}.")
        return f"{digital_output_channel}/{state}"

async def read_input(device_name, channel_name, io_name):
    digital_input_channel = f"{device_name}/{channel_name}/{io_name}"
    with nidaqmx.Task() as task:
        task.di_channels.add_di_chan(digital_input_channel)
        value = task.read()
        print(f"{digital_input_channel} gelesen. Wert: {value}")
        return f"{digital_input_channel}/{value}"

async def read_temp(device_name, channel_name, io_name):
    temp_channel = f"{device_name}/{channel_name}"
    thermocouple_type = getattr(nidaqmx.constants.ThermocoupleType, io_name)
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_thrmcpl_chan(temp_channel, thermocouple_type=thermocouple_type)
        value = task.read()
        print(f"{temp_channel} gelesen. Temperatur: {value}")
        return f"{temp_channel}/{value}"

async def read_analog(device_name, channel_name):
    analog_channel = f"{device_name}/{channel_name}"
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(analog_channel)
        value = task.read()
        print(f"{analog_channel} gelesen. Wert: {value}")
        return f"{analog_channel}/{value}"

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Nachrichten GUI")
        self.root.iconbitmap("C:\\local_repo\\TestScripte\\Python\\Ni_Websocket\\icon.ico")  # Set the icon
        self.connection_status = tk.StringVar(value="Nicht verbunden")
        self.ip_address = tk.StringVar(value="localhost")
        self.port = tk.StringVar(value="8765")
        self.server = None
        self.server_task = None
        self.create_widgets()

    def create_widgets(self):
        self.info_label = ttk.Label(root, text="Bitte zuerst IP-Adresse und den Port eingeben, dann Server starten.", font=('Arial', 10, 'bold'), foreground="blue")
        self.info_label.pack(pady=10)
        
        # Server settings frame
        self.server_settings_frame = ttk.LabelFrame(root, text="Server-Einstellungen", padding=(10, 10))
        self.server_settings_frame.pack(pady=10, padx=10, fill='x')

        self.ip_label = ttk.Label(self.server_settings_frame, text="IP Adresse:")
        self.ip_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')

        self.ip_entry = ttk.Entry(self.server_settings_frame, textvariable=self.ip_address)
        self.ip_entry.grid(row=0, column=1, pady=5, sticky='ew')

        self.port_label = ttk.Label(self.server_settings_frame, text="Port:")
        self.port_label.grid(row=1, column=0, padx=(0, 10), pady=5, sticky='w')

        self.port_entry = ttk.Entry(self.server_settings_frame, textvariable=self.port)
        self.port_entry.grid(row=1, column=1, pady=5, sticky='ew')

        self.start_button = ttk.Button(self.server_settings_frame, text="Server starten", command=self.start_server)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=15, sticky='ew')

        self.status_label_frame = ttk.LabelFrame(root, text="Verbindungsstatus", padding=(10, 10))
        self.status_label_frame.pack(pady=10, padx=10, fill='x')
        
        self.status_label = ttk.Label(self.status_label_frame, text="Status:")
        self.status_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')
        
        self.connection_label = ttk.Label(self.status_label_frame, textvariable=self.connection_status, background="red", width=20, anchor='center')
        self.connection_label.grid(row=0, column=1, pady=5)

        self.messages_frame = ttk.Frame(root)
        self.messages_frame.pack(pady=(10, 10), padx=10, fill=tk.BOTH, expand=True)

        self.received_frame = ttk.LabelFrame(self.messages_frame, text="Empfangene Nachrichten", padding=(10, 10))
        self.received_frame.pack(side=tk.LEFT, padx=5, pady=(0, 5), fill=tk.BOTH, expand=True)

        self.received_scrollbar = ttk.Scrollbar(self.received_frame)
        self.received_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.received_listbox = tk.Listbox(self.received_frame, width=50, height=15, bg="lightgrey", yscrollcommand=self.received_scrollbar.set)
        self.received_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.received_scrollbar.config(command=self.received_listbox.yview)
        
        self.sent_frame = ttk.LabelFrame(self.messages_frame, text="Gesendete Nachrichten", padding=(10, 10))
        self.sent_frame.pack(side=tk.LEFT, padx=5, pady=(0, 5), fill=tk.BOTH, expand=True)

        self.sent_scrollbar = ttk.Scrollbar(self.sent_frame)
        self.sent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.sent_listbox = tk.Listbox(self.sent_frame, width=50, height=15, bg="lightgrey", yscrollcommand=self.sent_scrollbar.set)
        self.sent_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.sent_scrollbar.config(command=self.sent_listbox.yview)

    def update_received_message(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.received_listbox.insert(tk.END, f"{timestamp} - {message}")
        self.received_listbox.yview(tk.END)

    def update_sent_message(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.sent_listbox.insert(tk.END, f"{timestamp} - {message}")
        self.sent_listbox.yview(tk.END)

    def update_status(self, status):
        self.connection_status.set(status)
        self.connection_label.config(background="green" if status == "Verbunden" else "red")

    async def handler(self, websocket):
        try:
            self.update_status("Verbunden")
            async for message in websocket:
                self.update_received_message(message)
                parts = message.split('/')
                response = "Ungültige Nachricht"
                
                if len(parts) == 5 and parts[0] == "write":
                    device_name, channel_name, io_name, state = parts[1], parts[2], parts[3], parts[4]
                    state = True if state == "True" else False
                    response = await switch_output(device_name, channel_name, io_name, state)
                elif len(parts) == 4 and parts[0] == "read":
                    device_name, channel_name, io_name = parts[1], parts[2], parts[3]
                    response = await read_input(device_name, channel_name, io_name)
                elif len(parts) == 4 and parts[0] == "readTemp":
                    device_name, channel_name, io_name = parts[1], parts[2], parts[3]
                    response = await read_temp(device_name, channel_name, io_name)
                elif len(parts) == 3 and parts[0] == "readAnalog":
                    device_name, channel_name = parts[1], parts[2]
                    response = await read_analog(device_name, channel_name)
                else:
                    print(f"Ungültige Nachricht: {message}")

                await websocket.send(response)
                self.update_sent_message(response)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"WebSocket-Verbindung geschlossen: {e}")
            self.update_received_message("Verbindung geschlossen")
            self.update_sent_message("Verbindung geschlossen")
        finally:
            self.update_status("Nicht verbunden")
            await websocket.close()

    async def main(self):
        self.server = await websockets.serve(self.handler, self.ip_address.get(), int(self.port.get()))
        print(f"WebSocket-Server läuft auf ws://{self.ip_address.get()}:{self.port.get()}")
        await self.server.wait_closed()

    def start_server(self):
        if self.server_task:
            self.server_task.cancel()
            self.update_status("Nicht verbunden")
        self.server_task = asyncio.create_task(self.main())

async def run_gui(gui):
    while True:
        gui.root.update()
        gui.root.update_idletasks()
        await asyncio.sleep(0.01)

async def run(gui):
    await asyncio.gather(run_gui(gui))

if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    asyncio.run(run(gui))
