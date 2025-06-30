import customtkinter
from pynput import keyboard
import threading
import sys

# --- Configure customtkinter's appearance for a Sleek Dark UI ---
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

# Define consistent fonts
MAIN_FONT = ("Inter", 14)
HEADER_FONT = ("Inter", 22, "bold")
BUTTON_FONT = ("Inter", 15, "bold")
SLIDER_LABEL_FONT = ("Inter", 12)
STATUS_FONT = ("Inter", 13)
WATERMARK_FONT = ("Inter", 16, "bold")

VALID_KEY = "kraken-I0GCNQLDVCLMFHQOGIK"

class DraggableOverlay(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("kraken")
        # Start with a size appropriate for the key entry first, then adjust for main overlay
        self.geometry("380x280+100+100") # Smaller initial size for key entry
        self.withdraw() # Start completely hidden

        # --- Window Attributes ---
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.normal_alpha = 0.98
        self.stream_proof_alpha = 0.0
        self.attributes('-alpha', self.normal_alpha)

        if sys.platform.startswith('win'):
            self.wm_attributes('-toolwindow', True)

        self.is_authenticated = False
        self.is_key_entry_visible = False # New state for the key entry overlay
        self.is_main_overlay_visible = False # New state for the main cheat overlay

        self.x = 0
        self.y = 0

        self.main_frame = customtkinter.CTkFrame(self,
                                                 fg_color="#1F2023",
                                                 corner_radius=15,
                                                 border_width=2,
                                                 border_color="#3A3B40")
        self.main_frame.pack(expand=True, fill="both", padx=15, pady=15)

        self.main_frame.bind("<ButtonPress-1>", self.start_move)
        self.main_frame.bind("<B1-Motion>", self.do_move)
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        self.key_entry_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.main_controls_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")

        self._setup_key_entry_ui()
        self._setup_main_controls_ui() # This now includes the new status label

        # We don't pack any frame initially. They will be packed based on state.

        self.listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        self.listener_thread.start()
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    # --- Movable Window Helper Functions ---
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    # --- UI Setup Functions ---
    def _setup_key_entry_ui(self):
        self.key_entry_header = customtkinter.CTkLabel(self.key_entry_frame,
                                                      text="kraken beta",
                                                      font=HEADER_FONT,
                                                      text_color="#89CFF0")
        self.key_entry_header.pack(pady=(20, 10)) # Reduced padding for key entry view

        self.key_entry_field = customtkinter.CTkEntry(self.key_entry_frame,
                                                      width=300,
                                                      height=40,
                                                      placeholder_text="Enter Key Here...",
                                                      font=MAIN_FONT,
                                                      fg_color="#2B2D30",
                                                      border_color="#3E4044",
                                                      corner_radius=8)
        self.key_entry_field.pack(pady=(10, 15), padx=20) # Reduced padding
        self.key_entry_field.bind("<Return>", lambda event=None: self._check_key())

        self.submit_key_button = customtkinter.CTkButton(self.key_entry_frame,
                                                         text="SUBMIT KEY",
                                                         command=self._check_key,
                                                         font=BUTTON_FONT,
                                                         fg_color="#4CAF50",
                                                         hover_color="#388E3C",
                                                         height=45,
                                                         corner_radius=8)
        self.submit_key_button.pack(pady=(10, 15), padx=20) # Reduced padding

        self.key_status_label = customtkinter.CTkLabel(self.key_entry_frame,
                                                       text="",
                                                       font=STATUS_FONT,
                                                       text_color="#E53935")
        self.key_status_label.pack(pady=(5, 10)) # Reduced padding

    def _setup_main_controls_ui(self):
        self.header_label = customtkinter.CTkLabel(self.main_controls_frame,
                                                 text="KRAKEN test beta",
                                                 font=HEADER_FONT,
                                                 text_color="#89CFF0")
        self.header_label.pack(pady=(10, 20))

        self.aimbot_frame = customtkinter.CTkFrame(self.main_controls_frame,
                                                   fg_color="#2B2D30",
                                                   corner_radius=8,
                                                   border_width=1,
                                                   border_color="#3E4044")
        self.aimbot_frame.pack(fill="x", pady=(0, 15), padx=10)

        self.aimbot_checkbox = customtkinter.CTkCheckBox(self.aimbot_frame,
                                                          text="Aimbot",
                                                          font=MAIN_FONT,
                                                          text_color="#E0E0E0",
                                                          command=self._update_status_display,
                                                          hover_color="#3A3A3A")
        self.aimbot_checkbox.pack(pady=(12, 6), padx=15, anchor="w")

        self.aimbot_slider_label = customtkinter.CTkLabel(self.aimbot_frame,
                                                           text="Smoothing: 0.0",
                                                           font=SLIDER_LABEL_FONT,
                                                           text_color="#A0A0A0")
        self.aimbot_slider_label.pack(pady=(4, 0), padx=15, anchor="w")

        self.aimbot_slider = customtkinter.CTkSlider(self.aimbot_frame,
                                                     from_=0, to=100,
                                                     command=self.aimbot_slider_callback,
                                                     button_color="#4CAF50",
                                                     progress_color="#4CAF50",
                                                     height=12,
                                                     button_hover_color="#388E3C")
        self.aimbot_slider.set(0)
        self.aimbot_slider.pack(pady=(5, 15), padx=15, fill="x")

        self.features_frame = customtkinter.CTkFrame(self.main_controls_frame,
                                                     fg_color="#2B2D30",
                                                     corner_radius=8,
                                                     border_width=1,
                                                     border_color="#3E4044")
        self.features_frame.pack(fill="x", pady=(0, 15), padx=10)

        self.wallcheck_checkbox = customtkinter.CTkCheckBox(self.features_frame,
                                                            text="Wallcheck",
                                                            font=MAIN_FONT,
                                                            text_color="#E0E0E0",
                                                            command=self._update_status_display,
                                                            hover_color="#3A3A3A")
        self.wallcheck_checkbox.pack(pady=(12, 6), padx=15, anchor="w")

        self.streamproof_checkbox = customtkinter.CTkCheckBox(self.features_frame,
                                                             text="Stream Proof",
                                                             font=MAIN_FONT,
                                                             text_color="#E0E0E0",
                                                             command=self._update_status_display,
                                                             hover_color="#3A3A3A")
        self.streamproof_checkbox.pack(pady=(6, 12), padx=15, anchor="w")

        self.feature_status_label = customtkinter.CTkLabel(self.main_controls_frame,
                                                        text="kraken",
                                                        font=STATUS_FONT,
                                                        text_color="#B0B0B0")
        self.feature_status_label.pack(pady=(10, 15), padx=12, anchor="w")

        self.close_button = customtkinter.CTkButton(self.main_controls_frame,
                                                     text="UNINJECT",
                                                     command=self.close_app,
                                                     fg_color="#E53935",
                                                     hover_color="#C62828",
                                                     font=BUTTON_FONT,
                                                     height=40,
                                                     corner_radius=8)
        self.close_button.pack(pady=(10, 5), padx=10, fill="x")

    # --- Authentication Logic ---
    def _check_key(self):
        entered_key = self.key_entry_field.get().strip()
        if entered_key == VALID_KEY:
            self.is_authenticated = True
            self.key_status_label.configure(text="Authentication Successful!", text_color="#4CAF50")
            print("Authentication Successful!")
            self.after(500, self._hide_key_entry_and_prepare_main) # Hide key entry and prepare main
        else:
            self.key_status_label.configure(text="Invalid Key. Please try again.", text_color="#E53935")
            print("Invalid Key.")
            self.key_entry_field.delete(0, customtkinter.END)

    def _hide_key_entry_and_prepare_main(self):
        self.key_entry_frame.pack_forget() # Hide the key entry frame
        self.is_key_entry_visible = False
        # Adjust geometry for main overlay
        self.geometry(f"380x480+{self.winfo_x()}+{self.winfo_y()}")
        self.withdraw() # Hide the entire overlay again, waiting for next INSERT press
        self.is_main_overlay_visible = False # Ensure main overlay is seen as hidden

    # --- Widget Callbacks ---
    def _update_status_display(self):
        aimbot_status = "ON" if self.aimbot_checkbox.get() else "OFF"
        wallcheck_status = "ON" if self.wallcheck_checkbox.get() else "OFF"
        streamproof_status = "ON" if self.streamproof_checkbox.get() else "OFF"

        status_text = (
            f"ra "
            f"ra "
            f"ra"
        )
        self.feature_status_label.configure(text=status_text)

        # Handle alpha change directly here if stream proof is involved
        if self.streamproof_checkbox.get():
            self.attributes('-alpha', self.stream_proof_alpha)
        else:
            self.attributes('-alpha', self.normal_alpha)


    def aimbot_slider_callback(self, value):
        self.aimbot_slider_label.configure(text=f"Smoothing: {value:.1f}")

    # --- Overlay Visibility Toggle (INSERT key) ---
    def _toggle_overlay_based_on_state(self):
        if not self.is_authenticated:
            # State 1: Not authenticated, Key Entry is not visible -> Show Key Entry
            if not self.is_key_entry_visible:
                print("Showing Key Entry Overlay.")
                self.geometry("380x280+100+100") # Reset size for key entry
                self.deiconify()
                self.key_entry_frame.pack(expand=True, fill="both")
                self.key_entry_field.focus_set()
                self.lift()
                self.is_key_entry_visible = True
            # State 2: Not authenticated, Key Entry IS visible -> Do nothing
            else:
                print("Key Entry Overlay already visible. Please enter the key.")
                self.key_status_label.configure(text="Please enter the key to proceed.", text_color="#FFD700")
                self.after(3000, lambda: self.key_status_label.configure(text="", text_color="#E53935")) # Clear message
        else:
            # Authenticated: Toggle Main Overlay visibility
            if self.streamproof_checkbox.get():
                print("Cannot toggle visibility with INSERT key while Stream Proof is active.")
                return

            if self.is_main_overlay_visible:
                # Hide Main Overlay
                self.withdraw()
                self.is_main_overlay_visible = False
                print("Main Overlay Hidden.")
            else:
                # Show Main Overlay
                self.deiconify()
                # Ensure correct frame is packed
                self.key_entry_frame.pack_forget() # Just in case it was accidentally packed
                self.main_controls_frame.pack(expand=True, fill="both")
                self.geometry(f"380x480+{self.winfo_x()}+{self.winfo_y()}") # Restore main overlay size
                self.lift()
                self.is_main_overlay_visible = True
                self._update_status_display() # Update status when visible

    def _on_press(self, key):
        try:
            if key == keyboard.Key.insert:
                self.after_idle(self._toggle_overlay_based_on_state)
        except AttributeError:
            pass

    def _start_listener(self):
        with keyboard.Listener(on_press=self._on_press) as listener:
            self.listener = listener
            listener.join()

    # --- Application Close ---
    def close_app(self):
        print("Closing Overlay Application...")
        if hasattr(self, 'listener') and self.listener.running:
            try:
                self.listener.stop()
            except Exception as e:
                print(f"Error stopping listener: {e}")
        self.quit()
        self.destroy()


class Watermark(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("")
        self.TRANSPARENT_COLOR = '#010101'

        self.geometry(f"320x40+8+8")

        self.configure(fg_color=self.TRANSPARENT_COLOR)
        self.wm_attributes('-transparentcolor', self.TRANSPARENT_COLOR)
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.99)
        self.attributes('-toolwindow', True)
        self.attributes("-disabled", True)
        self.resizable(False, False)

        self.label = customtkinter.CTkLabel(self,
                                            text="Kraken | Creds: Monkey",
                                            font=WATERMARK_FONT,
                                            text_color="#B3E5FC")
        self.label.configure(fg_color=self.TRANSPARENT_COLOR)
        self.label.pack(expand=True, fill="both", padx=10, pady=5)

        self.deiconify()
        self.lift()


# --- Application Entry Point ---
if __name__ == "__main__":
    app = DraggableOverlay()
    watermark_app = Watermark()

    app.watermark_app = watermark_app

    original_close_app = app.close_app
    def combined_close_app():
        original_close_app()
        if hasattr(app, 'watermark_app') and app.watermark_app:
            app.watermark_app.destroy()
    app.close_app = combined_close_app

    app.mainloop()
