import sys
import mido
import sacn
import threading
import time
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
    QVBoxLayout, QHBoxLayout, QMenu, QStatusBar, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject, Qt, QThread, QPoint

# --- CONFIGURATION ---

# sACN Configuration
SACN_UNIVERSE = 101
SACN_DESTINATION_IP = "192.168.1.119"
SACN_FPS = 30

# MIDI Device Name
APC_DEVICE_NAME = "APC mini mk2"

# Blinking speed for active buttons (in seconds)
BLINK_INTERVAL = 0.2

# --- APC MINI MK2 COLOR & BUTTON CONFIGURATION ---

# This map links a color name to the MIDI Velocity value.
COLOR_MAP = {
    'Off': 0, 'Black': 0, 'Grey': 2, 'White': 3,
    'Red': 5, 'Green': 21, 'Blue': 45, 'Yellow': 13,
    'Orange': 9, 'Lime': 17, 'Cyan': 37, 'Magenta': 53,
    'Pink': 53, 'Purple': 81, 'Light_Red': 4, 'Light_Green': 20,
    'Light_Blue': 44, 'Light_Yellow': 12, 'Light_Pink': 52,
    'Light_Purple': 48, 'Red_Dim': 6, 'Green_Dim': 22,
    'Blue_Dim': 46, 'Yellow_Dim': 14, 'Solid': 5
}

# This map provides hex codes for the GUI buttons to visually represent the colors.
# It's separate from the MIDI color map.
GUI_COLOR_MAP = {
    'Off': '#202020', 'Black': '#202020', 'Grey': '#606060', 'White': '#FFFFFF',
    'Red': '#FF1010', 'Green': '#10FF10', 'Blue': '#1010FF', 'Yellow': '#FFFF10',
    'Orange': '#FF8C00', 'Lime': '#ADFF2F', 'Cyan': '#10FFFF', 'Magenta': '#FF10FF',
    'Pink': '#FF69B4', 'Purple': '#8A2BE2', 'Light_Red': '#F08080', 'Light_Green': '#90EE90',
    'Light_Blue': '#ADD8E6', 'Light_Yellow': '#FFFFE0', 'Light_Pink': '#FFB6C1',
    'Light_Purple': '#E6E6FA', 'Red_Dim': '#8B0000', 'Green_Dim': '#006400',
    'Blue_Dim': '#00008B', 'Yellow_Dim': '#BDB76B', 'Solid': '#FF1010'
}

# Default Button Colors Configuration (Loaded on first run)
DEFAULT_BUTTON_COLORS = [
    # 8x8 Grid
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    # Right Edge Buttons
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off'],
    # Bottom Edge Buttons
    ['Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off']
]

# Default Button Behavior Configuration
DEFAULT_BUTTON_MODES = [
    # 8x8 Grid
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    # Right Edge Buttons
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump'],
    # Bottom Edge Buttons
    ['Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump', 'Bump']
]

# --- DMX CHANNEL MAPPING ---
GRID_DMX_START_CHANNEL = 1
RIGHT_BUTTON_DMX_START_CHANNEL = 101
BOTTOM_BUTTON_DMX_START_CHANNEL = 111
FADER_DMX_START_CHANNEL = 201

################################################################################
#                                                                              #
#                         CONTROLLER BACKEND LOGIC                             #
#                                                                              #
################################################################################

class ControllerBackend(QObject):
    """
    Manages all non-GUI logic: MIDI I/O, sACN sending, and state management.
    Runs in a separate QThread to avoid freezing the GUI.
    """
    status_updated = pyqtSignal(str)
    midi_ports_found = pyqtSignal(str, str)
    midi_ports_not_found = pyqtSignal(str)
    initialization_complete = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.inport = None
        self.outport = None
        self.sender = None
        self.blinker_thread = None
        self.stop_blinker_event = threading.Event()
        self.stop_midi_listener_event = threading.Event()

        # State variables
        self.button_states = {}
        self.note_map = {}
        self.cc_map = {}
        self.blinker_led_state = True

    def run(self):
        """Main entry point when the thread starts."""
        self.status_updated.emit("Backend thread started.")
        self.find_and_open_ports()

    def find_and_open_ports(self):
        inport_name, outport_name = None, None
        try:
            for name in mido.get_input_names():
                if APC_DEVICE_NAME in name:
                    inport_name = name
                    break
            for name in mido.get_output_names():
                if APC_DEVICE_NAME in name:
                    outport_name = name
                    break

            if not inport_name or not outport_name:
                self.midi_ports_not_found.emit(f"ERROR: Could not find MIDI device '{APC_DEVICE_NAME}'.")
                return

            self.midi_ports_found.emit(inport_name, outport_name)

            self.inport = mido.open_input(inport_name)
            self.outport = mido.open_output(outport_name)

            self.start_sacn()
            self.initialize_device()
            self.initialization_complete.emit()
            self.listen_for_midi()

        except Exception as e:
            self.status_updated.emit(f"Error during initialization: {e}")

    def start_sacn(self):
        try:
            self.sender = sacn.sACNsender(fps=SACN_FPS)
            self.sender.start()
            self.sender.activate_output(SACN_UNIVERSE)
            self.sender[SACN_UNIVERSE].destination = SACN_DESTINATION_IP
            self.status_updated.emit(f"sACN sender started for Universe {SACN_UNIVERSE} -> {SACN_DESTINATION_IP}")
        except Exception as e:
            self.status_updated.emit(f"ERROR: Could not start sACN sender: {e}")
            raise e # Propagate to stop initialization

    def initialize_device(self):
        self.status_updated.emit("Setting APC to DAW mode and initializing LEDs...")
        # Sysex message to switch APC to a mode that allows individual LED control
        mode_change_msg = mido.Message('sysex', data=[0x47, 0x7F, 0x26, 0x04, 0x01, 0x00, 0x04, 0x01])
        self.outport.send(mode_change_msg)
        time.sleep(0.1)  # Give device time to process
        self.initialize_leds()
        self.start_blinker_thread()
        self.status_updated.emit("Controller is active. Ready for input.")

    def listen_for_midi(self):
        """The main MIDI listening loop."""
        while not self.stop_midi_listener_event.is_set():
            try:
                for msg in self.inport.iter_pending():
                    if msg.type in ['note_on', 'note_off']:
                        self.handle_button_press(msg)
                    elif msg.type == 'control_change':
                        if msg.control in self.cc_map:
                            self.handle_fader_move(msg)
                time.sleep(0.001) # Prevent high CPU usage
            except Exception as e:
                self.status_updated.emit(f"Error in MIDI loop: {e}")
                break

    def stop(self):
        """Gracefully shuts down all processes."""
        self.status_updated.emit("Shutdown sequence initiated...")
        self.stop_midi_listener_event.set()
        self.stop_blinker_event.set()

        if self.blinker_thread and self.blinker_thread.is_alive():
            self.blinker_thread.join(timeout=1.0)
            self.status_updated.emit("Blinker thread stopped.")

        if self.outport and not self.outport.closed:
            self.clear_all_leds()
            self.outport.close()
            self.status_updated.emit("MIDI output port closed.")

        if self.inport and not self.inport.closed:
            self.inport.close()
            self.status_updated.emit("MIDI input port closed.")

        if self.sender and self.sender.is_running:
            self.sender.stop()
            self.status_updated.emit("sACN sender stopped.")
        
        self.status_updated.emit("Backend shutdown complete.")


    def generate_maps_from_config(self, colors, modes):
        """Parses the config from the GUI to create runtime mappings."""
        self.note_map.clear()
        self.cc_map.clear()
        self.button_states.clear()

        # 8x8 Grid Pads (MIDI Notes 0–63)
        for r, (color_row, mode_row) in enumerate(zip(colors[:8], modes[:8])):
            for c, (color_name, mode_name) in enumerate(zip(color_row, mode_row)):
                note = (7 - r) * 8 + c
                dmx = GRID_DMX_START_CHANNEL + (r * 8) + c
                self.note_map[note] = {
                    'color_name': color_name,
                    'color_id': COLOR_MAP.get(color_name, 0),
                    'dmx': dmx,
                    'mode': mode_name.lower()
                }
                self.button_states[note] = 'solid'

        # Right Edge Buttons (MIDI Notes 112–119)
        for i, (color, mode) in enumerate(zip(colors[8], modes[8])):
            note = 112 + i
            dmx = RIGHT_BUTTON_DMX_START_CHANNEL + i
            self.note_map[note] = {
                'color_name': color, 'color_id': COLOR_MAP.get(color, 0),
                'dmx': dmx, 'mode': mode.lower()
            }
            self.button_states[note] = 'solid'

        # Bottom Edge Buttons (MIDI Notes 100–107 + 122)
        for i, (color, mode) in enumerate(zip(colors[9], modes[9])):
            note = 100 + i if i < 8 else 122
            dmx = BOTTOM_BUTTON_DMX_START_CHANNEL + i
            self.note_map[note] = {
                'color_name': color, 'color_id': COLOR_MAP.get(color, 0),
                'dmx': dmx, 'mode': mode.lower()
            }
            self.button_states[note] = 'solid'

        # Faders (MIDI CCs 48–56)
        for i in range(9):
            self.cc_map[48 + i] = {'dmx': FADER_DMX_START_CHANNEL + i}

        toggle_count = sum(1 for cfg in self.note_map.values() if cfg['mode'] == 'toggle')
        bump_count = sum(1 for cfg in self.note_map.values() if cfg['mode'] == 'bump')
        self.status_updated.emit(f"Config loaded: {toggle_count} Toggle, {bump_count} Bump buttons.")
        # If the device is already running, re-initialize the LEDs with the new config
        if self.outport:
            self.initialize_leds()

    def update_button_config(self, note, new_color_name, new_mode_name):
        """Updates a single button's configuration in real-time."""
        if note in self.note_map:
            self.note_map[note]['color_name'] = new_color_name
            self.note_map[note]['color_id'] = COLOR_MAP.get(new_color_name, 0)
            self.note_map[note]['mode'] = new_mode_name.lower()
            
            # Reset state and update LED on device
            self.button_states[note] = 'solid'
            if self.outport:
                color_id = self.note_map[note]['color_id']
                msg = mido.Message('note_on', note=note, velocity=color_id)
                self.outport.send(msg)
            self.status_updated.emit(f"Updated Note {note}: Color={new_color_name}, Mode={new_mode_name}")

    def initialize_leds(self):
        if not self.outport: return
        for note, config in self.note_map.items():
            msg = mido.Message('note_on', note=note, velocity=config['color_id'])
            self.outport.send(msg)

    def clear_all_leds(self):
        if not self.outport: return
        for note in self.note_map.keys():
            msg = mido.Message('note_off', note=note)
            self.outport.send(msg)
        self.status_updated.emit("All LEDs cleared.")

    def start_blinker_thread(self):
        self.stop_blinker_event.clear()
        self.blinker_thread = threading.Thread(target=self._blinker_loop, daemon=True)
        self.blinker_thread.start()

    def _blinker_loop(self):
        while not self.stop_blinker_event.is_set():
            if not self.outport or self.outport.closed: break
            try:
                for note, state in list(self.button_states.items()):
                    if state == 'blinking' and self.note_map[note]['mode'] == 'toggle':
                        color_id = self.note_map[note]['color_id']
                        velocity = color_id if self.blinker_led_state else 0
                        msg = mido.Message('note_on', note=note, velocity=velocity)
                        self.outport.send(msg)
                self.blinker_led_state = not self.blinker_led_state
                time.sleep(BLINK_INTERVAL)
            except (AttributeError, KeyError, RuntimeError):
                # Handles cases where maps are being updated or port closes during loop
                break

    def set_dmx_value(self, dmx_channel, dmx_value):
        if not self.sender: return
        dmx_data = list(self.sender[SACN_UNIVERSE].dmx_data)
        if 0 <= dmx_channel - 1 < len(dmx_data):
            dmx_data[dmx_channel - 1] = dmx_value
            self.sender[SACN_UNIVERSE].dmx_data = dmx_data

    def handle_button_press(self, msg):
        if msg.note not in self.note_map: return
        config = self.note_map[msg.note]
        dmx_channel = config['dmx']

        if config['mode'] == 'toggle':
            # Toggle mode now acts like bump for DMX but keeps LED behavior
            if msg.type == 'note_on' and msg.velocity > 0:
                # Set DMX to 255 (like bump)
                self.set_dmx_value(dmx_channel, 255)
                
                # Handle LED feedback (toggle between solid and blinking)
                if self.button_states[msg.note] == 'solid':
                    self.button_states[msg.note] = 'blinking'
                else:
                    self.button_states[msg.note] = 'solid'
                    self.outport.send(mido.Message('note_on', note=msg.note, velocity=config['color_id']))
            
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Set DMX to 0 (like bump)
                self.set_dmx_value(dmx_channel, 0)
                # LED feedback stays the same (no change on note_off for toggles)

        elif config['mode'] == 'bump':
            if msg.type == 'note_on' and msg.velocity > 0:
                self.set_dmx_value(dmx_channel, 255)
                self.outport.send(mido.Message('note_on', note=msg.note, velocity=0))
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                self.set_dmx_value(dmx_channel, 0)
                self.outport.send(mido.Message('note_on', note=msg.note, velocity=config['color_id']))

    def handle_fader_move(self, msg):
        config = self.cc_map[msg.control]
        dmx_value = round((msg.value / 127) * 255)
        self.set_dmx_value(config['dmx'], dmx_value)


################################################################################
#                                                                              #
#                           GUI FRONTEND LOGIC                                 #
#                                                                              #
################################################################################

class ConfigurableButton(QPushButton):
    """A custom button widget that stores its configuration and selection state."""
    def __init__(self, text, note, color_name, mode_name):
        super().__init__(text)
        self.note = note
        self.color_name = color_name
        self.mode_name = mode_name
        self.is_selected = False
        self.update_visuals()

    def set_config(self, color_name, mode_name):
        self.color_name = color_name
        self.mode_name = mode_name
        self.update_visuals()

    def set_selected(self, selected):
        """Sets the selection state and updates visuals."""
        self.is_selected = selected
        self.update_visuals()

    def update_visuals(self):
        """Updates the button's appearance based on its config and selection state."""
        hex_color = GUI_COLOR_MAP.get(self.color_name, '#202020')
        # Determine text color for contrast
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        text_color = 'white' if (r * 0.299 + g * 0.587 + b * 0.114) < 140 else 'black'
        
        self.setText(self.mode_name[0]) # 'B' for Bump, 'T' for Toggle
        font = self.font()
        font.setBold(True)
        self.setFont(font)

        # Define border style based on selection
        border_style = "2px solid #0078d7" if self.is_selected else "1px solid #555"
        hover_border_style = "2px solid #3399ff" # A brighter blue for hover

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {hex_color};
                color: {text_color};
                border: {border_style};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton:hover {{
                border: {hover_border_style};
            }}
        """)


class DragSelectionWidget(QWidget):
    """A widget that handles drag selection over child buttons."""
    def __init__(self):
        super().__init__()
        self.drag_start = None
        self.drag_current = None
        self.is_dragging = False
        self.buttons = {}  # Will store note -> button mapping
        self.main_window = None  # Reference to MainWindow
        
    def set_main_window(self, main_window):
        self.main_window = main_window
        self.buttons = main_window.buttons
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if we clicked on a button
            clicked_widget = self.childAt(event.position().toPoint())
            if isinstance(clicked_widget, ConfigurableButton):
                # If we clicked on a button, let the button handle it first
                clicked_widget.clicked.emit()
            else:
                # If we clicked on empty space, start drag selection
                self.drag_start = event.position().toPoint()
                self.drag_current = self.drag_start
                self.is_dragging = True
                # Clear existing selection when starting new drag
                if self.main_window:
                    for btn in list(self.main_window.selected_buttons):
                        btn.set_selected(False)
                    self.main_window.selected_buttons.clear()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.drag_start:
            self.drag_current = event.position().toPoint()
            self.update_drag_selection()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.drag_start = None
            self.drag_current = None
            if self.main_window:
                self.main_window.update_status_bar(f"{len(self.main_window.selected_buttons)} buttons selected.")
        super().mouseReleaseEvent(event)

    def update_drag_selection(self):
        if not self.drag_start or not self.drag_current or not self.main_window:
            return
            
        # Create selection rectangle
        x1, y1 = self.drag_start.x(), self.drag_start.y()
        x2, y2 = self.drag_current.x(), self.drag_current.y()
        
        # Ensure proper rectangle bounds
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        # Clear current selection
        for btn in list(self.main_window.selected_buttons):
            btn.set_selected(False)
        self.main_window.selected_buttons.clear()
        
        # Check which buttons intersect with the drag rectangle
        for button in self.buttons.values():
            button_rect = button.geometry()
            button_global_pos = button.mapToParent(QPoint(0, 0))
            
            # Check if button intersects with drag rectangle
            if (button_global_pos.x() < right and 
                button_global_pos.x() + button_rect.width() > left and
                button_global_pos.y() < bottom and 
                button_global_pos.y() + button_rect.height() > top):
                
                button.set_selected(True)
                self.main_window.selected_buttons.add(button)


class MainWindow(QMainWindow):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akai APC mini mk2 sACN Controller")
        self.setGeometry(100, 100, 800, 600)

        # Store all button widgets for easy access
        self.buttons = {} # key: note, value: ConfigurableButton widget
        self.selected_buttons = set() # Store currently selected buttons

        # --- Backend Setup ---
        self.backend_thread = QThread()
        self.backend = ControllerBackend()
        self.backend.moveToThread(self.backend_thread)

        # Connect signals from backend to GUI slots
        self.backend.status_updated.connect(self.update_status_bar)
        self.backend.midi_ports_not_found.connect(self.handle_midi_error)
        self.backend_thread.started.connect(self.backend.run)

        # Start the backend thread
        self.backend_thread.start()

        self.initUI()
        self.load_initial_config(DEFAULT_BUTTON_COLORS, DEFAULT_BUTTON_MODES)

    def initUI(self):
        # --- Menu Bar ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        
        load_action = QAction("&Load Profile...", self)
        load_action.triggered.connect(self.load_profile)
        file_menu.addAction(load_action)

        save_action = QAction("&Save Profile As...", self)
        save_action.triggered.connect(self.save_profile)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- Status Bar ---
        self.setStatusBar(QStatusBar(self))

        # --- Main Layout with Drag Selection ---
        self.drag_widget = DragSelectionWidget()
        self.drag_widget.set_main_window(self)
        self.setCentralWidget(self.drag_widget)
        
        main_layout = QVBoxLayout(self.drag_widget)

        # Create the grid for all buttons
        apc_layout = QGridLayout()
        apc_layout.setSpacing(5)

        # Create 8x8 Grid
        for r in range(8):
            for c in range(8):
                note = (7 - r) * 8 + c
                button = ConfigurableButton(" ", note, "Off", "Bump")
                button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda pos, b=button: self.show_context_menu(b, pos))
                button.clicked.connect(lambda checked, b=button: self.handle_button_left_click(b))
                apc_layout.addWidget(button, r, c)
                self.buttons[note] = button

        # Create Right Edge Buttons
        for i in range(8):
            note = 112 + i
            button = ConfigurableButton(" ", note, "Off", "Bump")
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(lambda pos, b=button: self.show_context_menu(b, pos))
            button.clicked.connect(lambda checked, b=button: self.handle_button_left_click(b))
            apc_layout.addWidget(button, i, 9) # Column 9 to add spacing
            self.buttons[note] = button

        # Create Bottom Edge Buttons
        bottom_layout = QHBoxLayout()
        for i in range(9):
            note = 100 + i if i < 8 else 122
            button = ConfigurableButton(" ", note, "Off", "Bump")
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(lambda pos, b=button: self.show_context_menu(b, pos))
            button.clicked.connect(lambda checked, b=button: self.handle_button_left_click(b))
            bottom_layout.addWidget(button)
            self.buttons[note] = button

        main_layout.addLayout(apc_layout)
        main_layout.addLayout(bottom_layout)

    def handle_button_left_click(self, button):
        """Toggles the selection state of a clicked button."""
        if button in self.selected_buttons:
            button.set_selected(False)
            self.selected_buttons.remove(button)
        else:
            button.set_selected(True)
            self.selected_buttons.add(button)
        self.update_status_bar(f"{len(self.selected_buttons)} buttons selected.")

    def show_context_menu(self, button, position):
        """Shows a context menu to change properties for all selected buttons."""
        # If the right-clicked button is not in the current selection,
        # clear the old selection and select only this one.
        if button not in self.selected_buttons:
            for btn in list(self.selected_buttons): # Iterate over a copy
                btn.set_selected(False)
            self.selected_buttons.clear()
            
            button.set_selected(True)
            self.selected_buttons.add(button)
            self.update_status_bar("1 button selected.")

        context_menu = QMenu(self)
        
        # Color Sub-Menu
        color_menu = context_menu.addMenu("Set Color")
        for color_name in sorted(COLOR_MAP.keys()):
            action = QAction(color_name, self)
            # Use a lambda that captures the color name to be applied to all selected buttons
            action.triggered.connect(lambda checked, c=color_name: self.change_selected_buttons_color(c))
            color_menu.addAction(action)

        # Mode Sub-Menu
        mode_menu = context_menu.addMenu("Set Mode")
        toggle_action = QAction("Toggle", self)
        toggle_action.triggered.connect(lambda: self.change_selected_buttons_mode("Toggle"))
        mode_menu.addAction(toggle_action)

        bump_action = QAction("Bump", self)
        bump_action.triggered.connect(lambda: self.change_selected_buttons_mode("Bump"))
        mode_menu.addAction(bump_action)

        context_menu.exec(button.mapToGlobal(position))
    
    def change_selected_buttons_color(self, color_name):
        """Applies a new color to all currently selected buttons."""
        if not self.selected_buttons: return
        for button in self.selected_buttons:
            button.set_config(color_name, button.mode_name)
            self.backend.update_button_config(button.note, color_name, button.mode_name)
        self.update_status_bar(f"Set color to '{color_name}' for {len(self.selected_buttons)} buttons.")


    def change_selected_buttons_mode(self, mode_name):
        """Applies a new mode to all currently selected buttons."""
        if not self.selected_buttons: return
        for button in self.selected_buttons:
            button.set_config(button.color_name, mode_name)
            self.backend.update_button_config(button.note, button.color_name, mode_name)
        self.update_status_bar(f"Set mode to '{mode_name}' for {len(self.selected_buttons)} buttons.")


    def load_initial_config(self, colors, modes):
        """Loads the default config into the GUI and sends it to the backend."""
        # Clear any existing selections
        for btn in list(self.selected_buttons):
            btn.set_selected(False)
        self.selected_buttons.clear()

        self.backend.generate_maps_from_config(colors, modes)
        
        # 8x8 Grid
        for r, (color_row, mode_row) in enumerate(zip(colors[:8], modes[:8])):
            for c, (color_name, mode_name) in enumerate(zip(color_row, mode_row)):
                note = (7 - r) * 8 + c
                if note in self.buttons:
                    self.buttons[note].set_config(color_name, mode_name)
        
        # Right Edge
        for i, (color, mode) in enumerate(zip(colors[8], modes[8])):
            note = 112 + i
            if note in self.buttons:
                self.buttons[note].set_config(color, mode)
        
        # Bottom Edge
        for i, (color, mode) in enumerate(zip(colors[9], modes[9])):
            note = 100 + i if i < 8 else 122
            if note in self.buttons:
                self.buttons[note].set_config(color, mode)
    
    def save_profile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Profile", "", "JSON Files (*.json);;All Files (*)")
        if not filePath:
            return

        colors = [([''] * 8) for _ in range(8)] + [[''] * 8, [''] * 9]
        modes = [([''] * 8) for _ in range(8)] + [[''] * 8, [''] * 9]

        # 8x8 Grid
        for r in range(8):
            for c in range(8):
                note = (7 - r) * 8 + c
                btn = self.buttons[note]
                colors[r][c] = btn.color_name
                modes[r][c] = btn.mode_name
        
        # Right Edge
        for i in range(8):
            note = 112 + i
            btn = self.buttons[note]
            colors[8][i] = btn.color_name
            modes[8][i] = btn.mode_name

        # Bottom Edge
        for i in range(9):
            note = 100 + i if i < 8 else 122
            btn = self.buttons[note]
            colors[9][i] = btn.color_name
            modes[9][i] = btn.mode_name

        profile_data = {'colors': colors, 'modes': modes}
        try:
            with open(filePath, 'w') as f:
                json.dump(profile_data, f, indent=4)
            self.update_status_bar(f"Profile saved to {filePath}")
        except Exception as e:
            self.update_status_bar(f"Error saving profile: {e}")

    def load_profile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Load Profile", "", "JSON Files (*.json);;All Files (*)")
        if not filePath:
            return
        
        try:
            with open(filePath, 'r') as f:
                profile_data = json.load(f)
            
            # Basic validation
            if 'colors' not in profile_data or 'modes' not in profile_data:
                raise ValueError("Invalid profile format.")

            self.load_initial_config(profile_data['colors'], profile_data['modes'])
            self.update_status_bar(f"Profile loaded from {filePath}")
        except Exception as e:
            self.update_status_bar(f"Error loading profile: {e}")

    @pyqtSlot(str)
    def update_status_bar(self, message):
        self.statusBar().showMessage(message, 5000) # Show for 5 seconds
        print(f"STATUS: {message}") # Also print to console for logging

    @pyqtSlot(str)
    def handle_midi_error(self, message):
        self.update_status_bar(message)
        # Show a critical error message box to the user
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setText("MIDI Device Error")
        error_box.setInformativeText(f"{message}\nPlease ensure the Akai APC mini mk2 is connected and not in use by other software, then restart the application.")
        error_box.setWindowTitle("Error")
        error_box.exec()
        
    def closeEvent(self, event):
        """Overrides the window close event to ensure graceful shutdown."""
        self.backend.stop()
        self.backend_thread.quit()
        self.backend_thread.wait()
        event.accept()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())