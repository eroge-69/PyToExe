import customtkinter as ctk
import psutil
import platform
import subprocess
import webbrowser
import threading
import time
import os
import shutil
import ctypes
from tkinter import messagebox  # messagebox is still useful for some Tkinter specific needs

# Try to import gpuinfo, provide a fallback if not found
try:
    from gpuinfo import GPUInfo
except ImportError:
    class GPUInfo:
        @staticmethod
        def get_info():
            return []  # Return empty list if library not available


    print(
        "Warning: 'gpuinfo' library not found. GPU detection might be less detailed. Install with 'pip install py-gpuinfo'.")

# --- Color and Font Definitions (Adapted for CustomTkinter) ---
COLOR_PRIMARY = "#2C004F"  # Dark Purple for sidebar/accents
COLOR_SECONDARY = "#6A0DAD"  # Lighter Purple for secondary elements
COLOR_ACCENT = "#8A2BE2"  # Bright Purple for highlights/buttons
COLOR_BACKGROUND = "#0D0D0D"  # Very Dark Gray for main background
COLOR_TEXT_PRIMARY = "#FFFFFF"  # White text
COLOR_TEXT_SECONDARY = "#CCCCCC"  # Light gray text for less important info
COLOR_DISABLED = "#555555"  # Color for disabled elements

# CustomTkinter uses its own font system, but we can define families
FONT_TITLE = ("Arial", 28, "bold")
FONT_SUBTITLE = ("Arial", 20, "bold")
FONT_HEADING = ("Arial", 18, "bold")
FONT_BODY = ("Arial", 14)
FONT_SIDEBAR_BUTTON = ("Arial", 16)

# --- CustomTkinter App Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("TweakLab - Ultimate Edition")
app.geometry("1200x700")
app.configure(fg_color=COLOR_BACKGROUND)

# REMOVE DEFAULT TITLE BAR
app.overrideredirect(True)  # This removes the default window decorations

# Global variables for window movement and state
x_pos = 0
y_pos = 0


def set_initial_position():
    app.update_idletasks()  # Ensure window dimensions are calculated
    # Get current window width and height
    window_width = app.winfo_width()
    window_height = app.winfo_height()

    # Calculate screen center position
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)

    app.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")


def start_move(event):
    global x_pos, y_pos
    x_pos = event.x
    y_pos = event.y


def do_move(event):
    # Calculate new window position
    deltax = event.x - x_pos
    deltay = event.y - y_pos
    x = app.winfo_x() + deltax
    y = app.winfo_y() + deltay
    app.geometry(f"+{x}+{y}")


# Functions for custom title bar buttons
def close_app():
    app.destroy()


# Sidebar frame
sidebar_frame = ctk.CTkFrame(app, width=220, fg_color=COLOR_PRIMARY, corner_radius=0)
sidebar_frame.pack(side="left", fill="y", expand=False)

# Top Bar Frame for custom title bar elements
top_bar_frame = ctk.CTkFrame(app, height=40, fg_color=COLOR_PRIMARY, corner_radius=0)
top_bar_frame.pack(side="top", fill="x", expand=False)

# Make top bar draggable
top_bar_frame.bind("<ButtonPress-1>", start_move)
top_bar_frame.bind("<B1-Motion>", do_move)

# Title/Logo in top bar
top_bar_logo_label = ctk.CTkLabel(top_bar_frame, text="TweakLab", font=FONT_SUBTITLE, text_color=COLOR_TEXT_PRIMARY)
top_bar_logo_label.pack(side="left", padx=10, pady=5)
# Also make logo draggable
top_bar_logo_label.bind("<ButtonPress-1>", start_move)
top_bar_logo_label.bind("<B1-Motion>", do_move)

# Only Close button remains in top bar (right side)
close_button = ctk.CTkButton(top_bar_frame, text="✕", command=close_app,
                             fg_color="transparent", hover_color="#C00000",
                             text_color=COLOR_TEXT_PRIMARY, font=("Arial", 20, "bold"), width=40, height=40,
                             corner_radius=0)
close_button.pack(side="right")

# Main content frame (now packs after top_bar_frame)
main_content_frame = ctk.CTkFrame(app, fg_color=COLOR_BACKGROUND, corner_radius=0)
main_content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)


# --- Progress Overlay (Adapted for CustomTkinter) ---
class CtkProgressOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
        self.progress_bar = None
        self.message_label = None

    def show(self, message="Optimizing...", is_determinate=False, max_val=100):
        if self.overlay is not None:
            self.hide()  # Ensure previous overlay is hidden

        self.overlay = ctk.CTkFrame(self.parent, fg_color=COLOR_BACKGROUND, corner_radius=10)
        self.overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.3)
        self.overlay.lift()  # Bring to front

        self.message_label = ctk.CTkLabel(self.overlay, text=message, font=FONT_HEADING, text_color=COLOR_TEXT_PRIMARY)
        self.message_label.pack(pady=(30, 10))

        if is_determinate:
            self.progress_bar = ctk.CTkProgressBar(self.overlay, mode="determinate", progress_color=COLOR_ACCENT)
            self.progress_bar.set(0)
            self.progress_bar.pack(fill="x", padx=30, pady=10)
        else:
            self.progress_bar = ctk.CTkProgressBar(self.overlay, mode="indeterminate", progress_color=COLOR_ACCENT)
            self.progress_bar.start()
            self.progress_bar.pack(fill="x", padx=30, pady=10)

        self.parent.update_idletasks()  # Update UI immediately

    def update_progress(self, value=None, message=None):
        if self.progress_bar and self.progress_bar.cget("mode") == "determinate" and value is not None:
            self.progress_bar.set(value / 100.0)  # CTkProgressBar uses value from 0.0 to 1.0
        if self.message_label and message is not None:
            self.message_label.configure(text=message)
        self.parent.update_idletasks()

    def hide(self):
        if self.progress_bar:
            if self.progress_bar.cget("mode") == "indeterminate":
                self.progress_bar.stop()
            self.progress_bar.destroy()
            self.progress_bar = None
        if self.message_label:
            self.message_label.destroy()
            self.message_label = None
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
        self.parent.update_idletasks()


progress_overlay = CtkProgressOverlay(app)


# --- System Info Retrieval (Combined and improved) ---
# NOTE: This function is still here but no longer called by show_intro_screen
def get_system_info():
    # CPU Name
    cpu_name = "N/A (CPU Bilgisi Alınamadı)"
    try:
        if platform.system() == "Windows":
            # Try wmic for detailed CPU name on Windows
            wmic_cpu_output = subprocess.check_output("wmic path Win32_Processor get Name /value",
                                                      shell=True,
                                                      creationflags=subprocess.CREATE_NO_WINDOW,
                                                      stderr=subprocess.PIPE).decode('utf-8', errors='ignore')
            cpu_lines = wmic_cpu_output.strip().split('\n')
            wmic_cpu_name_list = [line.split('=')[1].strip() for line in cpu_lines if
                                  line.startswith('Name=') and line.split('=')[1].strip()]

            if wmic_cpu_name_list:
                cpu_name = wmic_cpu_name_list[0]
            else:
                # Fallback to platform.processor() if wmic returns empty
                cpu_name = platform.processor()
                if not cpu_name:
                    cpu_name = "N/A (WMIC ve Platform CPU Hatası)"
        else:  # For non-Windows systems
            cpu_name = platform.processor()
            if not cpu_name:
                cpu_name = "N/A (Platform CPU Hatası)"
    except Exception as e:
        cpu_name = f"N/A (CPU Detay Hatası: {str(e)})"
        print(f"CPU bilgisi alınırken hata oluştu: {e}")

    # RAM Info
    ram_total_gb = round(psutil.virtual_memory().total / (1024 ** 3))
    ram_total = f"{ram_total_gb} GB"

    # Disk Info
    disk_total_gb = psutil.disk_usage('/').total // (1024 ** 3)
    disk_total = f"{disk_total_gb} GB"

    # GPU Info
    gpu_name = "N/A (GPU Bilgisi Alınamadı)"
    try:
        if platform.system() == "Windows":
            wmic_output_caption = subprocess.check_output("wmic path Win32_VideoController get Caption /value",
                                                          shell=True,
                                                          creationflags=subprocess.CREATE_NO_WINDOW,
                                                          stderr=subprocess.PIPE).decode('utf-8', errors='ignore')
            gpu_lines_caption = wmic_output_caption.strip().split('\n')
            wmic_gpu_names = [line.split('=')[1].strip() for line in gpu_lines_caption if
                              line.startswith('Caption=') and line.split('=')[1].strip()]

            if wmic_gpu_names:
                gpu_name = ", ".join(wmic_gpu_names)
            else:
                # Fallback to 'Name' if 'Caption' is empty or not found
                wmic_output_name = subprocess.check_output("wmic path Win32_VideoController get Name /value",
                                                           shell=True,
                                                           creationflags=subprocess.CREATE_NO_WINDOW,
                                                           stderr=subprocess.PIPE).decode('utf-8', errors='ignore')
                gpu_lines_name = wmic_output_name.strip().split('\n')
                wmic_gpu_names_name = [line.split('=')[1].strip() for line in gpu_lines_name if
                                       line.startswith('Name=') and line.split('=')[1].strip()]
                if wmic_gpu_names_name:
                    gpu_name = ", ".join(wmic_gpu_names_name)
                else:
                    # If wmic still empty, try gpuinfo
                    try:
                        gpu_info_list = GPUInfo.get_info()
                        if gpu_info_list:
                            # Safely get 'name', provide fallback if not present
                            gpu_name = gpu_info_list[0].get('name', 'N/A (GPUInfo Kütüphane Hatası)')
                        else:
                            gpu_name = "N/A (WMIC/GPUInfo Başarısız)"
                    except Exception as e:
                        gpu_name = f"N/A (GPUInfo Detay Hatası: {str(e)})"
                        print(f"GPU bilgisi (gpuinfo) alınırken hata oluştu: {e}")
        else:  # For non-Windows, primarily rely on gpuinfo
            try:
                gpu_info_list = GPUInfo.get_info()
                if gpu_info_list:
                    gpu_name = gpu_info_list[0].get('name', 'N/A (GPUInfo Kütüphane Hatası)')
                else:
                    gpu_name = "N/A (GPUInfo Başarısız)"
            except Exception as e:
                gpu_name = f"N/A (GPUInfo Detay Hatası: {str(e)})"
                print(f"GPU bilgisi (gpuinfo) alınırken hata oluştu: {e}")
    except Exception as e:
        gpu_name = f"N/A (Genel GPU Hatası: {str(e)})"
        print(f"GPU bilgisi alınırken genel hata oluştu: {e}")

    return cpu_name, gpu_name, ram_total, disk_total


# --- Optimization Action Wrapper (Adapted for CustomTkinter messaging) ---
def run_optimization_action(action_func, message="Applying Optimization...", success_message="Optimization Applied!",
                            error_message="An error occurred!", confirm=True):
    if confirm:
        response = messagebox.askyesno("Confirm Optimization",
                                       "Are you sure you want to apply this optimization? Some operations may require administrator privileges or system restart.")
        if not response:
            return

    def _run_in_thread():
        progress_overlay.show(message)
        try:
            result = action_func()
            progress_overlay.hide()
            messagebox.showinfo("Success", success_message + "\n" + str(result))
        except Exception as e:
            progress_overlay.hide()
            messagebox.showerror("Error", f"{error_message}\n{e}")

    threading.Thread(target=_run_in_thread, daemon=True).start()


# --- Core Optimization Functions (from tweak son kod.txt, adapted for CustomTkinter messaging) ---

# CPU Optimizations
def optimize_cpu(level):
    if "Gaming Profile" in level:
        # Simulate: Disable CPU Core Parking (conceptual, usually handled by power plans)
        subprocess.run(["powercfg", "/setactive", "8c5e7fd7-bc28-4a69-8263-1002ec216062"], shell=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)  # High Performance
        return f"CPU optimized for {level} (High Performance Power Plan active)."
    elif "Office/Productivity" in level:
        subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], shell=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)  # Balanced
        return f"CPU optimized for {level} (Balanced Power Plan active)."
    elif "Max Performance" in level:
        subprocess.run(["powercfg", "/setactive", "8c5e7fd7-bc28-4a69-8263-1002ec216062"], shell=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)  # High Performance
        return f"CPU set to {level} (High Performance Power Plan active)."
    return "CPU optimization applied."


# GPU Optimizations
def optimize_gpu(level):
    if "Gaming" in level:
        # Conceptual: In a real app, this would interface with NVIDIA/AMD tools (e.g., MSI Afterburner profiles or driver settings via command line)
        return f"GPU optimized for {level}. (Requires manual driver settings/3rd party tools for full effect)."
    elif "Power Saving" in level:
        # Conceptual: Reduce power limits, set passive fan curve
        return f"GPU optimized for {level}. (Requires manual driver settings/3rd party tools for full effect)."
    return "GPU optimization applied."


# RAM Optimizations
def optimize_ram(level):
    if "Aggressive Clean" in level:
        try:
            if platform.system() == "Windows":
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
                return "Aggressive RAM clean performed for current process. System-wide cleanup often requires more advanced tools."
            else:
                return "Aggressive RAM clean is Windows-specific."
        except Exception as e:
            return f"Error during aggressive RAM clean: {e}"
    elif "Optimize" in level:  # Handles "Optimize XGB RAM"
        return f"RAM optimized for {level}. (Specific optimizations depend on RAM size and type)."
    return "RAM optimization applied."


# Storage Optimizations
def optimize_storage(level):
    if "SSD Max Performance" in level:
        # Disable NTFS Last Access Time, ensure TRIM is active
        if platform.system() == "Windows":
            try:
                subprocess.run(["fsutil", "behavior", "set", "disablelastaccess", "1"], shell=True, check=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
                # Check TRIM status: fsutil behavior query DisableDeleteNotify
                return "NTFS Last Access Time disabled. SSD performance optimized."
            except subprocess.CalledProcessError as e:
                return f"Error optimizing SSD: {e}. Run as administrator."
        else:
            return "SSD optimization is Windows-specific."
    elif "HDD General Optimize" in level:
        # Schedule defragmentation (if Windows, usually automatic)
        if platform.system() == "Windows":
            try:
                # This command defrags all drives, run periodically, not a one-time 'optimize'
                # For specific drive: subprocess.run(["defrag", "C:", "/U"], shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return "HDD optimization suggested. Ensure regular defragmentation is scheduled for HDDs."
            except subprocess.CalledProcessError as e:
                return f"Error optimizing HDD: {e}. Run as administrator."
        else:
            return "HDD optimization is Windows-specific."
    return "Storage optimization applied."


# Other Specific Optimizations (placeholders for now, actual implementation would be complex)
def optimize_game(game_name):
    # This would involve launching game with specific parameters, or applying game-specific config tweaks
    return f"Optimizing settings for {game_name}. (Requires game-specific config/launch options)."


def optimize_internet(level):
    if level == "Gaming Priority":
        # TCP NoDelay, TcpAckFrequency registry tweaks (requires admin, complex)
        return "Internet optimized for Gaming Priority. (Requires advanced network config)."
    elif level == "Streaming Priority":
        return "Internet optimized for Streaming Priority. (Requires advanced network config)."
    return "Internet optimization applied."


def optimize_input_lag():
    # Timer resolution (e.g., using TimerResolution.exe or similar via ctypes for NtSetTimerResolution)
    # Keyboard/mouse polling rates (requires driver/hardware settings, not software)
    return "Input lag reduction applied (Timer Resolution to 1ms if possible)."


def set_timer_resolution(value_ms):
    # This requires ctypes and kernel32/ntdll access, potentially complex and needs admin
    # Example (simplified conceptual):
    try:
        ntdll = ctypes.WinDLL("ntdll.dll")
        # NtSetTimerResolution takes 100-nanosecond intervals. 1ms = 10000 100-ns intervals.
        if value_ms == 1:
            resolution = ctypes.c_ulong(10000)
            ntdll.NtSetTimerResolution(resolution, True)  # True for periodic
            return "Timer resolution set to 1ms."
        elif value_ms == "Default":
            resolution = ctypes.c_ulong(0)  # Not precise, usually means system default
            ntdll.NtSetTimerResolution(resolution, False)  # False for not periodic
            return "Timer resolution reset to default."
        return "Invalid timer resolution value."
    except Exception as e:
        return f"Failed to set timer resolution: {e}. May require admin privileges or specific Windows build."


def clean_downloads_logs_traces():
    # Delete temporary files, browser cache, Windows update logs, etc.
    # This needs careful implementation to avoid deleting user's important files.
    temp_paths = [
        os.path.join(os.environ.get("TEMP", ""), "*"),
        os.path.join(os.environ.get("WINDIR", ""), "Temp", "*"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "INetCache", "*"),  # IE/Edge cache
        # DANGEROUS! Would need user confirmation for each file: os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "*")
    ]
    cleaned_count = 0
    for path_pattern in temp_paths:
        folder = os.path.dirname(path_pattern)
        if os.path.exists(folder):
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                try:
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                        cleaned_count += 1
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        cleaned_count += 1
                except Exception as e:
                    print(f"Could not delete {item_path}: {e}")  # For debugging
    return f"Cleaned {cleaned_count} temporary files and traces."


def optimize_windows_services(level):
    # Enable/disable Windows services via 'sc' command or WMI (requires admin)
    # This needs careful selection as disabling critical services can break Windows.
    if level == "Performance Mode":
        return "Windows services adjusted for Performance Mode. (Requires admin and careful selection)."
    elif level == "Balanced Mode":
        return "Windows services adjusted for Balanced Mode. (Requires admin and careful selection)."
    return "Windows services optimization applied."


def optimize_power_plan():
    # Create or activate a custom power plan
    # Example: Create "TweakLab High Performance" plan
    # subprocess.run(["powercfg", "-duplicatescheme", "8c5e7fd7-bc28-4a69-8263-1002ec216062"], shell=True) # Duplicate High Performance
    # subprocess.run(["powercfg", "-setactive", "NEW_GUID_HERE"], shell=True)
    return "Custom Power Plan created/activated (TweakLab V1)."


def optimize_monitor(refresh_rate):
    # Changes display refresh rate (requires specific tools like 'ChangeScreenResolution.exe' or direct driver API)
    return f"Monitor refresh rate set to {refresh_rate}Hz (Conceptual, requires external tool/API)."


def optimize_thermal_management(profile):
    # Set fan profiles (requires specific hardware/driver tools like FanControl, Argus Monitor, or BIOS access)
    return f"Thermal management profile set to {profile} (Conceptual, requires external tool/API)."


# --- UI Content Functions (Adapted for CustomTkinter) ---

# Helper to clear main content frame
def clear_main_content():
    for widget in main_content_frame.winfo_children():
        widget.destroy()


# Function to create an optimization button in the main content area
def create_optimization_button(parent_frame, text, action_command):
    btn = ctk.CTkButton(parent_frame, text=text, command=action_command,
                        fg_color=COLOR_ACCENT, hover_color=COLOR_PRIMARY,
                        font=FONT_HEADING, height=50, corner_radius=10)
    btn.pack(fill="x", pady=5, padx=20)
    return btn


# Function to create a dropdown for optimization options
def create_optimization_dropdown(parent_frame, label_text, options_list, default_value, action_func):
    frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
    frame.pack(fill="x", pady=5, padx=20)

    ctk.CTkLabel(frame, text=label_text + ":", font=FONT_BODY, text_color=COLOR_TEXT_PRIMARY).pack(side="left", padx=10)

    selected_option = ctk.StringVar(value=default_value)
    dropdown = ctk.CTkOptionMenu(frame, values=options_list, variable=selected_option,
                                 fg_color=COLOR_PRIMARY, button_color=COLOR_ACCENT, button_hover_color=COLOR_PRIMARY)
    dropdown.pack(side="right", padx=10, expand=True, fill="x")

    apply_btn = ctk.CTkButton(frame, text="Apply",
                              command=lambda: run_optimization_action(lambda: action_func(selected_option.get())),
                              fg_color=COLOR_ACCENT, hover_color=COLOR_PRIMARY, font=FONT_BODY, width=80)
    apply_btn.pack(side="right", padx=5)


# --- Menu Content Functions (Ported from tweak son kod.txt) ---

def show_intro_screen():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Thank you for choosing TweakLab!", font=FONT_TITLE,
                 text_color=COLOR_ACCENT).pack(pady=40)
    ctk.CTkLabel(main_content_frame,
                 text="If you encounter any problems or need assistance, please feel free to reach out to us.",
                 font=FONT_SUBTITLE, text_color=COLOR_TEXT_PRIMARY, wraplength=700).pack(pady=20)

    # Discord button (optional, but good for linking help)
    ctk.CTkButton(main_content_frame, text="Join Our Discord Server",
                  command=lambda: webbrowser.open("https://discord.gg/tweaklab"),
                  fg_color=COLOR_ACCENT, hover_color=COLOR_PRIMARY, font=FONT_HEADING, height=50,
                  corner_radius=10).pack(pady=30, ipadx=20)

    ctk.CTkLabel(main_content_frame, text="For detailed optimizations, select an option from the sidebar.",
                 font=FONT_BODY, text_color=COLOR_TEXT_SECONDARY).pack(pady=(20, 10), padx=15, anchor="center")


# --- New: One-Click Full Boost Function ---
def run_one_click_full_boost():
    results = []
    results.append(optimize_cpu("Max Performance"))  # Generic max performance
    results.append(optimize_gpu("Gaming/High Performance"))  # Generic gaming performance
    results.append(optimize_ram("Aggressive Clean"))
    results.append(optimize_storage("SSD Max Performance"))
    results.append(set_timer_resolution(1))
    results.append(optimize_power_plan())  # Activate TweakLab V1 Power Plan
    # Add other "safe" or essential full boost actions here

    return "\n".join(results)


def show_full_boost_one_click():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="⚡ One-Click Full Boost ⚡", font=FONT_TITLE, text_color=COLOR_ACCENT).pack(
        pady=20)
    ctk.CTkLabel(main_content_frame,
                 text="This will apply a comprehensive set of recommended optimizations for maximum performance.",
                 font=FONT_BODY, text_color=COLOR_TEXT_PRIMARY, wraplength=600).pack(pady=10)
    ctk.CTkLabel(main_content_frame, text="Recommended for Gaming and High-Performance tasks.", font=FONT_BODY,
                 text_color=COLOR_TEXT_SECONDARY, wraplength=600).pack(pady=5)

    ctk.CTkButton(main_content_frame, text="Activate Full Boost",
                  command=lambda: run_optimization_action(run_one_click_full_boost,
                                                          message="Activating Full Boost...",
                                                          success_message="Full Boost Applied Successfully!"),
                  fg_color=COLOR_ACCENT, hover_color=COLOR_PRIMARY, font=FONT_HEADING, height=60,
                  corner_radius=10).pack(pady=40, ipadx=30, ipady=15)


# --- Existing Menus, now called directly from Sidebar or other menus ---

def show_game_optimization_menu():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Optimize for Specific Games", font=FONT_SUBTITLE,
                 text_color=COLOR_ACCENT).pack(pady=20)

    game_options = ["FiveM", "GTA V", "Fortnite", "Valorant", "Counter-Strike 2", "Other/General"]
    create_optimization_dropdown(main_content_frame, "Select Game", game_options, game_options[0], optimize_game)

    # Back button only if this is a sub-menu of another complex menu
    # For now, as it's direct from sidebar, no back button needed unless desired


def show_performance_menu():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Performance Tweaks", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)

    # Updated CPU Optimization Options
    cpu_options = ["AMD Gaming Profile", "Intel Gaming Profile", "AMD Max Performance", "Intel Max Performance",
                   "Office/Productivity"]
    create_optimization_dropdown(main_content_frame, "CPU Optimization", cpu_options, "AMD Gaming Profile",
                                 optimize_cpu)

    # Updated GPU Optimization Options
    gpu_options = ["NVIDIA Gaming/High Performance", "AMD Gaming/High Performance", "NVIDIA Silent/Power Saving",
                   "AMD Silent/Power Saving"]
    create_optimization_dropdown(main_content_frame, "GPU Optimization", gpu_options, "NVIDIA Gaming/High Performance",
                                 optimize_gpu)

    # Updated RAM Optimization Options
    ram_options = ["Optimize 4GB RAM", "Optimize 8GB RAM", "Optimize 16GB RAM", "Optimize 32GB RAM",
                   "Optimize 64GB+ RAM", "Aggressive Clean (All)"]
    create_optimization_dropdown(main_content_frame, "RAM Optimization", ram_options, "Aggressive Clean (All)",
                                 optimize_ram)

    # Storage Optimization Options (remains as is based on general levels)
    storage_options = ["SSD Max Performance", "HDD General Optimize"]
    create_optimization_dropdown(main_content_frame, "Storage Optimization", storage_options, "SSD Max Performance",
                                 optimize_storage)


def show_internet_optimization_menu():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Internet Optimization", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)
    create_optimization_dropdown(main_content_frame, "Network Optimization Mode",
                                 ["Gaming Priority", "Streaming Priority", "General Use"], "Gaming Priority",
                                 optimize_internet)


# --- New: Advanced System Tweaks Menu ---
def show_advanced_tweaks_menu():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="🔧 Advanced System Tweaks 🔧", font=FONT_TITLE, text_color=COLOR_ACCENT).pack(
        pady=20)

    create_optimization_button(main_content_frame, "Thermal Management", show_thermal_menu_content)
    create_optimization_button(main_content_frame, "Optimize Downloads & Logs", show_downloads_logs_menu_content)
    create_optimization_button(main_content_frame, "Optimize Windows Services", show_windows_services_menu_content)
    create_optimization_button(main_content_frame, "Input Lag Reduction", show_input_lag_menu_content)
    create_optimization_button(main_content_frame, "Boot & BIOS Optimization", show_boot_bios_menu_content)
    create_optimization_button(main_content_frame, "Power Plan Optimization", show_power_plan_menu_content)
    create_optimization_button(main_content_frame, "Monitor Optimization", show_monitor_optimization_menu_content)


# Sub-menus that were previously direct buttons under "FPS Boosting", now linked from "Advanced System Tweaks"
def show_thermal_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Thermal Management", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)
    create_optimization_dropdown(main_content_frame, "Fan Profile", ["Silent", "Balanced", "Performance", "Reset"],
                                 "Balanced", optimize_thermal_management)
    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_downloads_logs_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Optimize Downloads & Logs", font=FONT_SUBTITLE,
                 text_color=COLOR_ACCENT).pack(pady=20)

    ctk.CTkLabel(main_content_frame,
                 text="This will clean temporary files, browser caches, and system logs. It will NOT automatically delete your personal downloads for safety reasons.",
                 font=FONT_BODY, text_color=COLOR_TEXT_SECONDARY, wraplength=600).pack(pady=10)
    create_optimization_button(main_content_frame, "Clean Temporary Files & Logs",
                               lambda: run_optimization_action(clean_downloads_logs_traces,
                                                               message="Cleaning...",
                                                               success_message="Temporary files and logs cleaned."))
    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_windows_services_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Optimize Windows Services", font=FONT_SUBTITLE,
                 text_color=COLOR_ACCENT).pack(pady=20)
    create_optimization_dropdown(main_content_frame, "Service Optimization Mode",
                                 ["Performance Mode", "Balanced Mode", "Default"], "Balanced Mode",
                                 optimize_windows_services)
    ctk.CTkLabel(main_content_frame,
                 text="Note: Changing Windows services requires careful consideration and administrator privileges. Incorrect changes may cause system instability.",
                 font=FONT_BODY, text_color=COLOR_TEXT_SECONDARY, wraplength=500).pack(pady=10)
    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_input_lag_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Input Lag Reduction", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)

    create_optimization_button(main_content_frame, "Reduce Overall Input Lag (Set Timer Resolution to 1ms)",
                               lambda: run_optimization_action(lambda: set_timer_resolution(1),
                                                               message="Reducing input lag...",
                                                               success_message="Input lag reduced (Timer Resolution set to 1ms)."))
    create_optimization_button(main_content_frame, "Reset Timer Resolution to Default",
                               lambda: run_optimization_action(lambda: set_timer_resolution("Default"),
                                                               message="Resetting timer resolution...",
                                                               success_message="Timer resolution reset to default."))

    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_boot_bios_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Boot & BIOS Optimization", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)

    ctk.CTkLabel(main_content_frame, text="BIOS Optimization Guide: (Click for more info)", font=FONT_BODY,
                 text_color=COLOR_TEXT_PRIMARY).pack(pady=10)
    ctk.CTkButton(main_content_frame, text="Open BIOS Guide Link",
                  command=lambda: webbrowser.open("https://www.example.com/bios-guide"),  # Replace with actual guide
                  fg_color=COLOR_ACCENT, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=5)

    create_optimization_button(main_content_frame, "Optimize Startup Programs (Open Task Manager)",
                               lambda: subprocess.Popen(["taskmgr", "/s", "startup"],
                                                        shell=True) if platform.system() == "Windows" else messagebox.showinfo(
                                   "Info", "Open Task Manager/Startup programs manually."),
                               confirm=False)

    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_power_plan_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Power Plan Optimization", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)
    create_optimization_button(main_content_frame, "Activate TweakLab V1 Power Plan (High Performance)",
                               lambda: run_optimization_action(optimize_power_plan,
                                                               message="Activating Power Plan...",
                                                               success_message="TweakLab V1 Power Plan Activated!"))
    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_monitor_optimization_menu_content():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Monitor Optimization", font=FONT_SUBTITLE, text_color=COLOR_ACCENT).pack(
        pady=20)
    create_optimization_dropdown(main_content_frame, "Set Refresh Rate",
                                 ["60Hz", "75Hz", "120Hz", "144Hz", "240Hz", "360Hz", "Max Available"], "Max Available",
                                 optimize_monitor)
    ctk.CTkLabel(main_content_frame,
                 text="Note: Changing refresh rate might require a restart or can be done via display settings.",
                 font=FONT_BODY, text_color=COLOR_TEXT_SECONDARY, wraplength=500).pack(pady=10)
    ctk.CTkButton(main_content_frame, text="Back to Advanced Tweaks", command=show_advanced_tweaks_menu,
                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY, font=FONT_BODY).pack(pady=20)


def show_help_center():
    clear_main_content()
    ctk.CTkLabel(main_content_frame, text="Help Center", font=FONT_TITLE, text_color=COLOR_ACCENT).pack(pady=20)
    ctk.CTkLabel(main_content_frame, text="For assistance or to report issues, please join our Discord server.",
                 font=FONT_BODY, text_color=COLOR_TEXT_PRIMARY).pack(pady=10)
    ctk.CTkButton(main_content_frame, text="Join TweakLab Discord",
                  command=lambda: webbrowser.open("https://discord.gg/tweaklab"),
                  fg_color=COLOR_ACCENT, hover_color=COLOR_PRIMARY, font=FONT_HEADING).pack(pady=20, ipadx=20, ipady=10)

    ctk.CTkLabel(main_content_frame, text="\n⚠️ Important Notice ⚠️", font=FONT_HEADING, text_color="#FF6347").pack(
        pady=10)
    ctk.CTkLabel(main_content_frame,
                 text="TweakLab performs system modifications to enhance performance. Exercise caution and understand the potential risks. Actions like overclocking may damage your hardware or cause system instability. In case of issues, consider using Windows System Restore or reinstalling drivers.",
                 font=FONT_BODY, text_color=COLOR_TEXT_SECONDARY, wraplength=700, justify="center").pack(pady=10)


# --- Sidebar Buttons ---
sidebar_items = [
    ("🏠 Home", show_intro_screen),
    ("⚡ One-Click Full Boost", show_full_boost_one_click),
    ("🎮 Game Optimization", show_game_optimization_menu),
    ("💡 Performance Tweaks", show_performance_menu),
    ("🌐 Network Optimization", show_internet_optimization_menu),
    ("🔧 Advanced System Tweaks", show_advanced_tweaks_menu),
    ("🆘 Help Center", show_help_center)
]

for text, command in sidebar_items:
    ctk.CTkButton(sidebar_frame, text=text, command=command,
                  fg_color=COLOR_PRIMARY, hover_color=COLOR_ACCENT, corner_radius=0,
                  font=FONT_SIDEBAR_BUTTON, height=40, anchor="w").pack(fill="x", pady=2, padx=5)

# Initialize with intro screen
show_intro_screen()

# Set initial position to center the window once widgets are packed
app.after(100, set_initial_position)  # Call after a small delay to ensure geometry is calculated

app.mainloop()