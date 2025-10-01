import tkinter as tk
from tkinter import ttk, font as tkFont
import serial
import serial.tools.list_ports
import time
import math
import sys
import threading
import queue

# --- Configuration Constants ---
BAUD_RATE = 9600
UPDATE_INTERVAL_MS = 50  # Fast update speed for responsiveness
# These are the *initial* GUI defaults; the Arduino will use EEPROM values upon connection.
TEMP_THRESHOLD = 37.0    # °C (Default Alarm trigger point)
HUMIDITY_MAX = 90.0      # % (Default Alarm trigger point)
GAS_THRESHOLD = 300.0    # Analog value (Default Alarm trigger point)

# --- Arabic Localization ---
ARABIC_STRINGS = {
    "APP_TITLE": "نظام المراقبة والتحكم الآلي (SCADA)",
    "TEMP_BAR": "الحرارة",
    "HUMIDITY_BAR": "الرطوبة",
    "GAS_LEVEL": "مستوى الغاز",
    "NORMAL": "تشغيل طبيعي",
    "ALARM": "إنذار! توجد مشكلة",
    "VALVE_STATUS": "حالة الصمام:",
    "OPEN": "مفتوح \u2705",
    "CLOSED": "مغلق \u274C",
    "MUTE_TOGGLE": "كتم / إقرار الإنذار \u2194",
    "CONNECT": "اتصال",
    "REFRESH": "تحديث المنافذ",
    "STATUS": "حالة النظام",
    "PORT_CONTROL": "تحكم الاتصال",
    "ALARM_CAUSE": "سبب الإنذار:",
    "HIGH_TEMP": "الحرارة مرتفعة",
    "HIGH_HUMIDITY": "الرطوبة خارج المجال",
    "GAS_LEAK": "كشف تسرب غاز",
    "NO_DATA": "جارٍ الاتصال...",
    "BUZZER": "الإنذار الصوتي:",
    "ACTIVE": "نشط \u26A0",
    "MUTED": "مكتوم \U0001F507",
    "TEMP": "درجة الحرارة",
    "HUMIDITY": "الرطوبة",
    "SETTINGS_TITLE": "إعدادات العتبات",
    "SAVE_SETTINGS": "حفظ العتبات \u2714",
    "TEMP_ENTRY_LABEL": "عتبة الحرارة الجديدة (0-150):",
    "HUM_ENTRY_LABEL": "عتبة الرطوبة الجديدة (0-100):",
    "GAS_ENTRY_LABEL": "عتبة الغاز الجديدة (0-1023):",
    "SAVED_SUCCESS": "تم إرسال الإعدادات بنجاح!",
    "SAVE_ERROR": "خطأ: تأكد من صحة القيم",
}

# --- Visual Constants ---
BG_COLOR = "#f7f7f7"
WARNING_COLOR = "#cc3300"
NORMAL_COLOR = "#008800"
VALVE_OPEN_COLOR = "#00cc66"
VALVE_CLOSED_COLOR = "#cc3300"
TEMP_RED = "#cc3300"    # High Value Color
TEMP_YELLOW = "#ffff00" # Low Value Color
HUM_CYAN = "#00cccc"

# --- Global Data Storage and Threading Tools ---
data = {'T': 0.0, 'H': 0.0, 'G': 0, 'S': 0, 'M': 0}
data_queue = queue.Queue() # Queue for data transfer from thread to GUI

# --- Serial Reader Thread ---
class SerialThread(threading.Thread):
    def __init__(self, serial_port, baud_rate, data_q):
        super().__init__()
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.data_q = data_q
        self.running = True
        self.serial_connection = None
        self.daemon = True 

    def run(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=1) 
            time.sleep(2)
            self.serial_connection.flushInput()
            print(f"Serial thread started on {self.serial_port}")
        except serial.SerialException as e:
            print(f"Serial thread failed to open port {self.serial_port}: {e}")
            self.data_q.put({"error": str(e)})
            self.running = False
            return

        while self.running:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Use a short timeout on readline to make sure the thread is responsive when closing
                    line = self.serial_connection.readline().decode('utf-8').strip() 
                    if line and ',' in line:
                        parts = line.split(',')
                        if len(parts) == 5:
                            parsed_data = {
                                'T': float(parts[0]),
                                'H': float(parts[1]),
                                'G': int(parts[2]),
                                'S': int(parts[3]),
                                'M': int(parts[4])
                            }
                            self.data_q.put(parsed_data)
            except Exception as e:
                print(f"Error reading serial data: {e}")
                time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()


# --- Color Gradient Utility ---
def interpolate_color(start_hex, end_hex, fraction):
    """Interpolates between two hex colors based on a fraction (0.0 to 1.0)."""
    start_hex = start_hex.lstrip('#')
    end_hex = end_hex.lstrip('#')
    
    start_rgb = tuple(int(start_hex[i:i+2], 16) for i in (0, 2, 4))
    end_rgb = tuple(int(end_hex[i:i+2], 16) for i in (0, 2, 4))
    
    r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * fraction)
    g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * fraction)
    b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * fraction)
    
    return f'#{r:02x}{g:02x}{b:02x}'

# --- LevelBar Class for Vertical Gauges ---
class LevelBar:
    def __init__(self, master, label_text, unit, max_value, color_start, color_end, sensor_icon):
        self.max_value = max_value
        self.color_start = color_start
        self.color_end = color_end
        self.unit = unit
        self.value = 0.0
        
        self.frame = ttk.Frame(master, padding="10", relief="flat", style="TFrame")
        
        self.title_label = ttk.Label(self.frame, text=f"{sensor_icon} {label_text}", font=tkFont.Font(family="Arial", size=14, weight="bold"), background=BG_COLOR, foreground="#333333")
        self.title_label.pack(side="top", pady=(0, 10))

        self.canvas_height = 250
        self.canvas = tk.Canvas(self.frame, width=150, height=self.canvas_height, bg="#e0e0e0", highlightthickness=0)
        self.canvas.pack(side="top", pady=5)
        
        self.bar_x, self.bar_y = 50, 20
        self.bar_width, self.bar_height = 50, self.canvas_height - 40
        
        self.canvas.create_rectangle(self.bar_x, self.bar_y, self.bar_x + self.bar_width, self.bar_y + self.bar_height, fill="#cccccc", outline="#aaaaaa", width=1)
        
        self.fill_id = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color_start, outline=self.color_start)
        self.pointer_triangle = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="#333333")
        self.value_text = self.canvas.create_text(self.bar_x + self.bar_width + 5, 0, anchor="w", text="N/A", font=tkFont.Font(family="Arial", size=10, weight="bold"), fill="#333333")


    def update_value(self, new_value):
        self.value = 0.8 * self.value + 0.2 * new_value
        normalized_value = min(max(self.value / self.max_value, 0), 1)
        fill_height = normalized_value * self.bar_height
        fill_y1 = self.bar_y + self.bar_height - fill_height
        
        fill_color = interpolate_color(self.color_start, self.color_end, normalized_value)
        
        self.canvas.coords(self.fill_id, self.bar_x, fill_y1, self.bar_x + self.bar_width, self.bar_y + self.bar_height)
        self.canvas.itemconfig(self.fill_id, fill=fill_color, outline=fill_color)
        
        pointer_y = fill_y1
        tri_size = 10
        tri_x1 = self.bar_x + self.bar_width + 1
        tri_x2 = tri_x1 + tri_size
        
        self.canvas.coords(self.pointer_triangle, 
                           tri_x1, pointer_y, 
                           tri_x2, pointer_y - tri_size // 2, 
                           tri_x2, pointer_y + tri_size // 2)
        
        text_x = tri_x2 + 5
        self.canvas.coords(self.value_text, text_x, pointer_y)
        self.canvas.itemconfig(self.value_text, text=f"{self.value:.1f} {self.unit}")
        

# --- Main Application ---
class SCADASystem(tk.Tk):
    def __init__(self):
        global TEMP_THRESHOLD, HUMIDITY_MAX, GAS_THRESHOLD
        super().__init__()
        self.title(ARABIC_STRINGS["APP_TITLE"])
        self.geometry("900x630") # Adjusted height for the new input field
        self.configure(bg=BG_COLOR)
        self.option_add('*tearOff', tk.FALSE)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Local state for current thresholds
        self.temp_threshold = TEMP_THRESHOLD
        self.humidity_max = HUMIDITY_MAX
        self.gas_threshold = GAS_THRESHOLD

        self.serial_thread = None
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_closing) 
        self.update_data()


    def create_widgets(self):
        self.arabic_font = tkFont.Font(family="Arial", size=10)
        self.large_alarm_font = tkFont.Font(family="Arial", size=20, weight="bold")
        
        style = ttk.Style()
        style.theme_use('default') 
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TButton", font=self.arabic_font)
        style.configure("TLabel", font=self.arabic_font, background=BG_COLOR)


        # --- 1. COM Port Control Frame (Sticky Top) ---
        self.control_frame = ttk.Frame(self, padding="10", relief="raised", style="TFrame")
        self.control_frame.grid(row=0, column=0, sticky='nwe', padx=10, pady=5)
        self.control_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Label(self.control_frame, text="المنفذ:", font=self.arabic_font).grid(row=0, column=0, padx=5, sticky='w')
        self.com_var = tk.StringVar(self)
        self.com_list = self.get_serial_ports()
        self.com_menu = ttk.Combobox(self.control_frame, textvariable=self.com_var, values=self.com_list, state='readonly', font=self.arabic_font)
        self.com_menu.grid(row=0, column=1, padx=5, sticky='ew')
        if self.com_list:
             self.com_var.set(self.com_list[0])

        self.connect_button = ttk.Button(self.control_frame, text=ARABIC_STRINGS["CONNECT"], command=self.connect_serial)
        self.connect_button.grid(row=0, column=2, padx=5, sticky='ew')

        self.refresh_button = ttk.Button(self.control_frame, text=ARABIC_STRINGS["REFRESH"], command=self.refresh_ports)
        self.refresh_button.grid(row=0, column=3, padx=5, sticky='ew')
        
        # --- 2. Main Content Frame ---
        self.main_frame = ttk.Frame(self, padding="10", style="TFrame", borderwidth=0)
        self.main_frame.grid(row=1, column=0, sticky='nwes', padx=10, pady=5)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # --- 2.1. Level Bars Frame ---
        self.bars_frame = ttk.Frame(self.main_frame, padding="10", style="TFrame", borderwidth=0)
        self.bars_frame.grid(row=0, column=0, sticky='nwes', padx=5, pady=5)
        self.bars_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.bars_frame.grid_rowconfigure(0, weight=1)

        self.temp_bar = LevelBar(self.bars_frame, ARABIC_STRINGS["TEMP_BAR"], "°م", 150.0, TEMP_YELLOW, TEMP_RED, "\u263C")
        self.temp_bar.frame.grid(row=0, column=0, sticky='nwes')

        self.hum_bar = LevelBar(self.bars_frame, ARABIC_STRINGS["HUMIDITY_BAR"], "%", 100.0, HUM_CYAN, HUM_CYAN, "\u2614")
        self.hum_bar.frame.grid(row=0, column=1, sticky='nwes')
        
        self.gas_frame = ttk.Frame(self.bars_frame, padding="10", relief="flat", style="TFrame", borderwidth=0)
        self.gas_frame.grid(row=0, column=2, sticky='nwes', padx=5, pady=5)
        
        ttk.Label(self.gas_frame, text=f"{ARABIC_STRINGS['GAS_LEVEL']} \U0001F525", font=tkFont.Font(family="Arial", size=14, weight="bold"), background=BG_COLOR, foreground="#333333").pack(pady=(0, 10))
        
        self.gas_level_label = ttk.Label(self.gas_frame, text=ARABIC_STRINGS["NO_DATA"], font=tkFont.Font(family="Arial", size=14, weight="bold"), background="#cccccc", foreground="#333333", padding=10, relief="raised")
        self.gas_level_label.pack(pady=5, fill="x")
        
        self.gas_raw_label = ttk.Label(self.gas_frame, text="Raw: N/A", font=self.arabic_font, background=BG_COLOR, foreground="#333333")
        self.gas_raw_label.pack(pady=5, fill="x")


        # --- 2.2. Indicators and Controls Frame ---
        self.indicator_frame = ttk.Frame(self.main_frame, padding="10", relief="flat", style="TFrame", borderwidth=0)
        self.indicator_frame.grid(row=0, column=1, sticky='nwes', padx=5, pady=5)
        self.indicator_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.indicator_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(self.indicator_frame, text=ARABIC_STRINGS["STATUS"], 
                                      font=tkFont.Font(family="Arial", size=20, weight="bold"), 
                                      foreground="white", background="#cccccc", padding=20, relief="raised")
        self.status_label.grid(row=0, column=0, sticky='nwes', pady=10)

        self.alarm_message_label = ttk.Label(self.indicator_frame, text="",
                                             font=self.large_alarm_font,
                                             foreground=WARNING_COLOR, background=BG_COLOR, justify=tk.CENTER, wraplength=400)
        self.alarm_message_label.grid(row=1, column=0, sticky='nwes', pady=10, padx=10)

        self.actuator_control_box = ttk.Frame(self.indicator_frame, padding="10", relief="ridge", borderwidth=2, style="TFrame")
        self.actuator_control_box.grid(row=2, column=0, sticky='nwe', pady=10)
        self.actuator_control_box.grid_columnconfigure((0, 1), weight=1)
        self.actuator_control_box.grid_rowconfigure((0, 1, 2), weight=1)

        self.valve_label = ttk.Label(self.actuator_control_box, text=ARABIC_STRINGS["VALVE_STATUS"] + ARABIC_STRINGS["NO_DATA"], font=tkFont.Font(family="Arial", size=10))
        self.valve_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.valve_icon = ttk.Label(self.actuator_control_box, text="?", font=tkFont.Font(size=20), foreground="#333333") 
        self.valve_icon.grid(row=0, column=1, padx=5, pady=5, sticky='e')
        
        self.buzzer_label = ttk.Label(self.actuator_control_box, text=ARABIC_STRINGS["BUZZER"] + ARABIC_STRINGS["NO_DATA"], font=tkFont.Font(family="Arial", size=10))
        self.buzzer_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        self.mute_button = ttk.Button(self.actuator_control_box, text=ARABIC_STRINGS["MUTE_TOGGLE"], command=self.send_mute_command)
        self.mute_button.grid(row=2, column=0, columnspan=2, pady=10, sticky='s')
        
        self.settings_frame = ttk.LabelFrame(self.indicator_frame, text=ARABIC_STRINGS["SETTINGS_TITLE"], padding="10", relief="ridge", style="TFrame")
        self.settings_frame.grid(row=3, column=0, sticky='nwes', pady=10)
        self.settings_frame.grid_columnconfigure((0, 1), weight=1)
        
        # --- Temperature Entry ---
        ttk.Label(self.settings_frame, text=ARABIC_STRINGS["TEMP_ENTRY_LABEL"], font=self.arabic_font).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.temp_entry = ttk.Entry(self.settings_frame, width=10)
        self.temp_entry.insert(0, str(self.temp_threshold))
        self.temp_entry.grid(row=0, column=1, padx=5, pady=5, sticky='e')

        # --- Humidity Entry ---
        ttk.Label(self.settings_frame, text=ARABIC_STRINGS["HUM_ENTRY_LABEL"], font=self.arabic_font).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.hum_entry = ttk.Entry(self.settings_frame, width=10)
        self.hum_entry.insert(0, str(self.humidity_max))
        self.hum_entry.grid(row=1, column=1, padx=5, pady=5, sticky='e')

        # --- Gas Entry (NEW) ---
        ttk.Label(self.settings_frame, text=ARABIC_STRINGS["GAS_ENTRY_LABEL"], font=self.arabic_font).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.gas_entry = ttk.Entry(self.settings_frame, width=10)
        self.gas_entry.insert(0, str(self.gas_threshold))
        self.gas_entry.grid(row=2, column=1, padx=5, pady=5, sticky='e')

        self.save_status_label = ttk.Label(self.settings_frame, text="", font=self.arabic_font)
        self.save_status_label.grid(row=3, column=0, columnspan=2, pady=5, sticky='nwe')

        self.save_button = ttk.Button(self.settings_frame, text=ARABIC_STRINGS["SAVE_SETTINGS"], command=self.save_thresholds)
        self.save_button.grid(row=4, column=0, columnspan=2, pady=10, sticky='nwes')


    def get_serial_ports(self):
        """Fetches a list of available serial ports."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def refresh_ports(self):
        """Refreshes the COM port dropdown menu."""
        self.com_list = self.get_serial_ports()
        self.com_menu['values'] = self.com_list
        if self.com_list:
            current_port = self.com_var.get()
            if current_port not in self.com_list:
                self.com_var.set(self.com_list[0])
        else:
            self.com_var.set("")
            
    def connect_serial(self):
        """Initializes and starts the serial reading thread."""
        port = self.com_var.get()
        
        if self.serial_thread and self.serial_thread.is_alive():
            self.disconnect_serial()

        if not port:
            self.status_label.config(text=ARABIC_STRINGS["PORT_CONTROL"], background=WARNING_COLOR)
            return
            
        try:
            self.serial_thread = SerialThread(port, BAUD_RATE, data_queue)
            self.serial_thread.start()
            
            self.connect_button.config(text="فصل", command=self.disconnect_serial)
            self.status_label.config(text="جاري بدء الاتصال...", background="#ffcc00")

        except Exception as e:
            self.status_label.config(text=f"خطأ: {e}", background=WARNING_COLOR)
            self.serial_thread = None
            
    def disconnect_serial(self):
        """Stops the serial reading thread."""
        if self.serial_thread and self.serial_thread.is_alive():
            self.serial_thread.stop()
            self.serial_thread.join(0.5) 

        self.serial_thread = None
        self.connect_button.config(text=ARABIC_STRINGS["CONNECT"], command=self.connect_serial)
        self.status_label.config(text="غير متصل", background="#cccccc")
            
    def send_mute_command(self):
        """Sends the 'R' command forcefully to the Arduino."""
        if self.serial_thread and self.serial_thread.running:
            try:
                conn = self.serial_thread.serial_connection
                if conn and conn.is_open:
                    # FIX: Aggressively push the command immediately to prevent lag/loss
                    conn.flushInput()   
                    conn.flushOutput()  
                    conn.write('R'.encode()) 
                    conn.flush()        
            except Exception as e:
                print(f"Error sending Mute command: {e}")
        else:
            print("Cannot send Mute command: Serial thread not active.")


    def save_thresholds(self):
        """Validates input and sends the 'S<T>,<H>,<G>' command to Arduino EEPROM."""
        if not (self.serial_thread and self.serial_thread.running):
            self.save_status_label.config(text="خطأ: يرجى الاتصال أولاً", foreground=WARNING_COLOR)
            return

        try:
            new_temp = float(self.temp_entry.get())
            new_hum = float(self.hum_entry.get())
            new_gas = float(self.gas_entry.get()) # Read Gas Value

            # Simple validation checks
            if not (0 < new_temp < 150 and 0 <= new_hum <= 100 and 0 <= new_gas <= 1023):
                 self.save_status_label.config(text=ARABIC_STRINGS["SAVE_ERROR"], foreground=WARNING_COLOR)
                 return

            # Construct the three-part command: S<T>,<H>,<G>\n
            command = f"S{new_temp:.1f},{new_hum:.1f},{new_gas:.1f}\n"

            conn = self.serial_thread.serial_connection
            if conn and conn.is_open:
                conn.flushOutput()
                conn.write(command.encode())
                conn.flush()
                
                # Update local GUI thresholds immediately
                self.temp_threshold = new_temp
                self.humidity_max = new_hum
                self.gas_threshold = new_gas # Update local gas threshold
                self.save_status_label.config(text=ARABIC_STRINGS["SAVED_SUCCESS"], foreground=NORMAL_COLOR)
                print(f"Settings command sent: {command.strip()}")
            else:
                self.save_status_label.config(text="خطأ: الاتصال غير جاهز.", foreground=WARNING_COLOR)
            
        except ValueError:
            self.save_status_label.config(text=ARABIC_STRINGS["SAVE_ERROR"], foreground=WARNING_COLOR)

    def check_alarm_cause(self, t, h, g):
        """Determines the specific cause(s) of the alarm based on current GUI thresholds."""
        causes = []
        if t > self.temp_threshold:
            causes.append(ARABIC_STRINGS["HIGH_TEMP"])
        if h > self.humidity_max:
            causes.append(ARABIC_STRINGS["HIGH_HUMIDITY"])
        if g > self.gas_threshold: # Use local gas threshold
            causes.append(ARABIC_STRINGS["GAS_LEAK"])
            
        if not causes:
            return ""
        
        return " - ".join(causes)


    def update_data(self):
        """Checks the queue for new data and updates GUI elements (runs in main thread)."""
        global data

        try:
            new_data = data_queue.get(block=False) 
            
            if "error" in new_data:
                self.status_label.config(text=f"خطأ: {new_data['error']}", background=WARNING_COLOR)
                self.disconnect_serial()
            else:
                data.update(new_data)
                self.status_label.config(text="متصل", background=NORMAL_COLOR)

        except queue.Empty:
            pass 
        except Exception as e:
            print(f"Error processing queue data: {e}")
            
        
        t = data['T']
        h = data['H']
        g = data['G']
        s = data['S']
        m = data['M']

        self.temp_bar.update_value(t)
        self.hum_bar.update_value(h)

        if g > self.gas_threshold:
            gas_status = "خطر"
            gas_color = WARNING_COLOR
        elif g > self.gas_threshold * 0.7:
            gas_status = "تحذير"
            gas_color = "#ffcc00"
        else:
            gas_status = ARABIC_STRINGS["NORMAL"]
            gas_color = NORMAL_COLOR
            
        self.gas_level_label.config(text=f"{ARABIC_STRINGS['GAS_LEVEL']}: {gas_status}", background=gas_color, foreground="white")
        self.gas_raw_label.config(text=f"Raw: {g}")


        if s == 1:
            cause_message = self.check_alarm_cause(t, h, g)
            self.status_label.config(text=ARABIC_STRINGS["ALARM"], background=WARNING_COLOR)
            self.alarm_message_label.config(text=f"{ARABIC_STRINGS['ALARM_CAUSE']}: {cause_message}", foreground=WARNING_COLOR)

            self.valve_label.config(text=ARABIC_STRINGS["VALVE_STATUS"] + ARABIC_STRINGS["CLOSED"], foreground=WARNING_COLOR)
            self.valve_icon.config(text="\u274C", foreground=VALVE_CLOSED_COLOR)
            
            if m == 1:
                self.buzzer_label.config(text=f"{ARABIC_STRINGS['BUZZER']} {ARABIC_STRINGS['MUTED']}", foreground="#333333")
            else:
                self.buzzer_label.config(text=f"{ARABIC_STRINGS['BUZZER']} {ARABIC_STRINGS['ACTIVE']}", foreground=WARNING_COLOR)

        else:
            self.status_label.config(text=ARABIC_STRINGS["NORMAL"], background=NORMAL_COLOR)
            self.alarm_message_label.config(text="", foreground="#333333") 

            self.valve_label.config(text=ARABIC_STRINGS["VALVE_STATUS"] + ARABIC_STRINGS["OPEN"], foreground=NORMAL_COLOR)
            self.valve_icon.config(text="\u2705", foreground=VALVE_OPEN_COLOR)

            self.buzzer_label.config(text=f"{ARABIC_STRINGS['BUZZER']} {ARABIC_STRINGS['NORMAL']}", foreground="#333333")

        self.after(UPDATE_INTERVAL_MS, self.update_data)

    def on_closing(self):
        """Stops the serial thread and closes the application gracefully."""
        self.disconnect_serial()
        self.destroy()

# --- Initialization ---
if __name__ == "__main__":
    app = SCADASystem()
    app.mainloop()
