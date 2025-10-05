# Mic Enhancement GUI with Dear PyGui (System-Wide Volume Control via pycaw)
# Features: List active/working mics, slider for volume/gain, apply system-wide to selected mic, floating overlay.
# Like Equalizer APO: Applies persistent gain adjustment to mic's hardware/software mixer (not full EQ, but volume boost).
# Requirements: pip install dearpygui pycaw comtypes

import dearpygui.dearpygui as dpg
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, AudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

class MicEnhancer:
    def __init__(self):
        self.devices = []
        self.device_dict = {}
        self.current_device = None
        self.volume = 100.0  # 0-100%

    def list_active_mics(self):
        """List only active (working, non-hidden) input devices."""
        self.devices = []
        self.device_dict = {}
        try:
            devices = AudioUtilities.GetAllDevices()
            for device in devices:
                if device.DataFlow == 0:  # eRender = Output, eCapture = Input
                    continue
                interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                state = device.State
                if state == 1:  # DEVICE_STATE_ACTIVE
                    name = device.FriendlyName
                    self.devices.append(name)
                    self.device_dict[name] = volume
            return self.devices
        except Exception as e:
            print(f"Error listing mics: {e}")
            return []

    def set_volume(self, device_name, vol_percent):
        """Set volume for selected mic (0-100%)."""
        if device_name not in self.device_dict:
            return False
        try:
            volume = self.device_dict[device_name]
            # Convert percent to dB (-inf to 0, but map 0% to -inf ~ -65dB, 100% to 0dB)
            db_range = volume.GetVolumeRange()
            min_db, max_db, _ = db_range
            db = min_db + (vol_percent / 100.0) * (max_db - min_db)
            volume.SetMasterVolume(db, None)
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False

class AudioGUI:
    def __init__(self):
        self.enhancer = MicEnhancer()
        self.mics = self.enhancer.list_active_mics()
        self.overlay_tag = None
        self.overlay_text_tag = None
        self.create_context()

    def create_context(self):
        dpg.create_context()
        dpg.create_viewport(title="Mic Enhancer Setup", width=400, height=500)

    def setup_main_window(self):
        with dpg.window(label="Mic Enhancer Control", tag="main_window"):
            # Mic Selector (only active ones)
            dpg.add_text("Select Active Microphone:")
            mic_items = self.mics
            self.mic_combo = dpg.add_combo(items=mic_items, default_value=mic_items[0] if mic_items else "", width=300, callback=self.on_mic_change)

            # Volume Slider (Gain/Boost %)
            dpg.add_text("Enhancement Gain (%):")
            self.volume_slider = dpg.add_slider_float(min_value=0, max_value=200, default_value=100, width=300, format="%.0f%%", callback=self.on_volume_change)

            # Apply Button
            self.apply_btn = dpg.add_button(label="Apply Enhancement to Mic", callback=self.apply_enhancement)

            # Status
            self.status_text = dpg.add_text("Ready to enhance.", color=[0, 255, 0, 255])

            # Overlay Button
            self.overlay_btn = dpg.add_button(label="Create Status Overlay", callback=self.create_overlay)

        dpg.set_primary_window("main_window", True)

    def on_mic_change(self, sender, app_data):
        self.enhancer.current_device = app_data
        dpg.set_value(self.status_text, f"Selected: {app_data}")

    def on_volume_change(self, sender, app_data):
        self.enhancer.volume = app_data
        if self.overlay_text_tag:
            dpg.set_value(self.overlay_text_tag, f"Mic Enhanced\nGain: {app_data:.0f}%")

    def apply_enhancement(self):
        device_name = dpg.get_value(self.mic_combo)
        vol_percent = dpg.get_value(self.volume_slider)
        if not device_name:
            dpg.set_value(self.status_text, "Error: Select a mic.", color=[255, 0, 0, 255])
            return
        success = self.enhancer.set_volume(device_name, vol_percent)
        if success:
            dpg.set_value(self.status_text, f"Applied {vol_percent:.0f}% gain to {device_name}", color=[0, 255, 0, 255])
            print(f"Enhancement applied system-wide to {device_name}")
        else:
            dpg.set_value(self.status_text, "Error applying enhancement.", color=[255, 0, 0, 255])

    def create_overlay(self):
        if self.overlay_tag:
            dpg.configure_item(self.overlay_tag, show=True)
            return

        # Floating overlay (drag to position over apps like Discord)
        with dpg.window(label="Enhancer Overlay", tag="overlay", width=200, height=100, pos=[100, 100], no_title_bar=True, no_resize=True):
            dpg.add_text("Mic Enhanced\nGain: 100%", tag="overlay_text", color=[255, 255, 255, 255])

        # Semi-transparent theme
        with dpg.theme(tag="overlay_theme"):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 0, 0, 128))

        dpg.bind_theme("overlay_theme", "overlay")
        self.overlay_tag = "overlay"
        self.overlay_text_tag = "overlay_text"
        self.update_overlay()
        print("Overlay created! Drag over your app.")

    def update_overlay(self):
        if self.overlay_text_tag and dpg.does_item_exist(self.overlay_text_tag):
            current_vol = dpg.get_value(self.volume_slider)
            dpg.set_value(self.overlay_text_tag, f"Mic Enhanced\nGain: {current_vol:.0f}%")
        dpg.set_frame_callback(dpg.get_frame_count() + 60, self.update_overlay)

    def run(self):
        self.setup_main_window()
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = AudioGUI()
    app.run()
