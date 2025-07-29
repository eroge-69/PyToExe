import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import time
import psutil
import os
import math
import csv
import socket
import sys
import json # For saving/loading profiles

# Multiprocessing for true multi-core CPU stress
import multiprocessing
# For multiprocessing Events, need to ensure they are properly handled
# and shared between processes. Queue is also an option for more complex IPC.
# For simple stop signal, multiprocessing.Event is fine.

# Matplotlib for graphing
import matplotlib
matplotlib.use("TkAgg") # Use TkAgg backend for Tkinter embedding
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt # Explicitly import pyplot as plt

# PyTorch for GPU stress (conditional import)
try:
    import torch
    GPU_AVAILABLE_TORCH = torch.cuda.is_available()
except ImportError:
    GPU_AVAILABLE_TORCH = False
    print("PyTorch or CUDA not available. GPU stress testing will be disabled.")

# pynvml for NVIDIA GPU monitoring (conditional import)
try:
    import pynvml
    GPU_AVAILABLE_NVML = True # Assume NVML will work if PyTorch can see CUDA
except ImportError:
    GPU_AVAILABLE_NVML = False
    print("pynvml not available. Advanced NVIDIA GPU monitoring will be limited.")

# --- Constants ---
DISK_STRESS_FILE_NAME = "stress_test_file.tmp"
CLOUD_API_ENDPOINT = "https://your-cloud-api.com/metrics" # REPLACE with your actual API endpoint
CLOUD_API_KEY = "YOUR_API_KEY_HERE" # REPLACE with your actual API key (consider more secure storage in production)
PROFILE_FILE_NAME = "stress_profile.json" # Default name for saving profiles

# --- Stress Test Worker Functions (Moved outside class for easier multiprocessing) ---

def cpu_stress_worker(stop_event):
    """Worker function for CPU stress. Runs in a separate process."""
    print(f"CPU stress worker (PID: {os.getpid()}) started.")
    try:
        while not stop_event.is_set():
            # Keep CPU busy with a simple calculation
            _ = 1 + 1
    except Exception as e:
        print(f"CPU stress worker (PID: {os.getpid()}) error: {e}")
    finally:
        print(f"CPU stress worker (PID: {os.getpid()}) stopped.")

def ram_stress_worker(allocation_mb, stop_event, log_callback=None):
    """Worker function for RAM stress."""
    bytes_to_allocate = allocation_mb * 1024 * 1024
    allocated_list = []
    if log_callback:
        log_callback(f"RAM stress worker started (allocating ~{allocation_mb}MB).")
    try:
        while not stop_event.is_set():
            # Allocate in smaller chunks to avoid a single huge allocation failure
            # and to allow for more granular control/release if needed.
            chunk_size = 10 * 1024 * 1024 # 10MB chunks
            num_chunks = bytes_to_allocate // chunk_size
            current_allocated_bytes = 0

            for i in range(num_chunks):
                if stop_event.is_set():
                    break
                try:
                    allocated_list.append(bytearray(chunk_size))
                    current_allocated_bytes += chunk_size
                except MemoryError:
                    if log_callback:
                        log_callback(f"RAM stress worker: Memory allocation failed after {current_allocated_bytes / (1024**3):.2f}GB. System likely at limit.")
                    stop_event.set() # Signal main thread to stop all RAM stress
                    break
            time.sleep(0.01) # Small sleep to yield, not block
    except Exception as e:
        if log_callback:
            log_callback(f"RAM stress worker error: {e}")
    finally:
        del allocated_list # Release memory
        if log_callback:
            log_callback("RAM stress worker stopped.")


def disk_stress_worker(file_size_mb, stop_event, endurance_mode=False, log_callback=None):
    """Worker function for Disk stress."""
    data_chunk = os.urandom(1024 * 1024)  # 1MB chunk
    file_path = DISK_STRESS_FILE_NAME

    if log_callback:
        log_callback(f"Disk I/O stress worker started (File: {file_size_mb}MB, Endurance: {endurance_mode}).")
        if endurance_mode:
            log_callback("WARNING: SSD Endurance Mode writes continuously and can impact SSD lifespan. Use with extreme caution.")

    try:
        # Open file in binary write mode; for endurance, use r+b to append/overwrite
        mode = "wb"
        if endurance_mode and os.path.exists(file_path):
            # If endurance mode and file exists, open for read/write to overwrite
            # Ensure it's the right size, if not, recreate.
            if os.path.getsize(file_path) == file_size_mb * 1024 * 1024:
                mode = "r+b"
            else:
                if log_callback:
  	                log_callback(f"Endurance file size mismatch, recreating: {file_path}")
        
        with open(file_path, mode) as f:
            if endurance_mode and mode == "wb": # If file was recreated for endurance
                if log_callback:
                    log_callback(f"Creating endurance file: {file_path}")
                f.seek(0)
                f.truncate(0)
                for _ in range(file_size_mb):
                    f.write(data_chunk)
                f.flush()
                os.fsync(f.fileno()) # Ensure data is written to disk

            while not stop_event.is_set():
                f.seek(0) # Go to beginning for overwrite in endurance mode or re-write
                for _ in range(file_size_mb):
                    if stop_event.is_set():
                        break
                    f.write(data_chunk)
                f.flush()
                os.fsync(f.fileno()) # Critical for actual disk I/O stress
                time.sleep(0.01) # Small sleep to yield CPU, but keep I/O busy
    except Exception as e:
        if log_callback:
            log_callback(f"ERROR in disk worker: {e}")
    finally:
        if not endurance_mode and os.path.exists(file_path):
            try:
                os.remove(file_path)
                if log_callback:
                    log_callback("Disk I/O test stopped and temp file cleaned up.")
            except OSError as e:
                if log_callback:
                    log_callback(f"ERROR: Could not delete temp file '{file_path}': {e}")
        elif endurance_mode:
            if log_callback:
                log_callback("SSD Endurance test stopped. File left intact for continuous testing. Manually delete if no longer needed.")


def gpu_stress_worker(stop_event, intensity_level, log_callback=None):
    """Worker function for GPU stress using PyTorch."""
    if not GPU_AVAILABLE_TORCH:
        if log_callback:
            log_callback("CUDA is not available. GPU stress worker exiting.")
        return

    device = torch.device("cuda")
    if log_callback:
        log_callback(f"GPU stress worker started on {device} (Intensity: {intensity_level}).")

    # Intensity scaling based on matrix size and iterations
    # These sizes/iterations are arbitrary; fine-tune for your target GPUs
    matrix_sizes = {"Easy": 1024, "Medium": 2048, "Hard": 4096, "Extreme": 8192}
    iterations_per_sleep_map = {"Easy": 50, "Medium": 100, "Hard": 200, "Extreme": 400}

    matrix_size = matrix_sizes.get(intensity_level, matrix_sizes["Medium"])
    iterations_per_sleep = iterations_per_sleep_map.get(intensity_level, iterations_per_sleep_map["Medium"])

    try:
        # Create tensors once to minimize allocation overhead in loop
        a = torch.randn(matrix_size, matrix_size, device=device)
        b = torch.randn(matrix_size, matrix_size, device=device)

        while not stop_event.is_set():
            for _ in range(iterations_per_sleep):
                if stop_event.is_set():
                    break
                c = torch.matmul(a, b) # Heavy matrix multiplication
                torch.cuda.synchronize() # Force synchronization to ensure work is actually done on GPU
            time.sleep(0.005) # Small sleep to yield, but keep GPU busy
    except Exception as e:
        if log_callback:
            log_callback(f"GPU stress worker error: {e}")
    finally:
        if GPU_AVAILABLE_TORCH:
            torch.cuda.empty_cache() # Clear GPU memory
        if log_callback:
            log_callback("GPU stress worker stopped.")


def udp_flood_worker(target_ip, target_port, packet_size, stop_event, log_callback=None):
    """Worker function for UDP network flood."""
    if log_callback:
        log_callback(f"UDP flood worker started to {target_ip}:{target_port} with {packet_size} bytes packets.")
        log_callback("WARNING: This can cause network congestion. Use on local network or with explicit permission.")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket
    message = os.urandom(packet_size) # Random data for packet

    try:
        while not stop_event.is_set():
            sock.sendto(message, (target_ip, target_port))
            time.sleep(0.000001) # Very small sleep for maximum flood rate
    except Exception as e:
        if log_callback:
            log_callback(f"UDP flood worker error: {e}")
    finally:
        sock.close()
        if log_callback:
            log_callback("UDP flood worker stopped.")


class StressTesterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Fusion Stress Tester PRO v0.0.9")
        self.geometry("1050x850") # Slightly wider for new elements
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Allow main_frame to expand

        # --- State Variables ---
        self.is_stressing = False
        # CPU workers will be a list of multiprocessing.Process objects
        self.stress_workers = {
            "cpu": [],
            "ram": None,
            "disk": None,
            "gpu": None,
            "network": None
        }
        # CPU stop event is multiprocessing.Event, others are threading.Event
        self.stop_events = {
            "cpu": multiprocessing.Event(),
            "ram": threading.Event(),
            "disk": threading.Event(),
            "gpu": threading.Event(),
            "network": threading.Event()
        }

        # Performance data for graphing and export
        self.performance_data = {
            "timestamp": [],
            "cpu_percent": [], # Overall CPU
            "cpu_percent_per_core": [], # Per-core data
            "ram_percent": [],
            "disk_percent": [],
            "cpu_temp": [],
            "gpu_mem_allocated": [],
            "gpu_temp": [], # New: GPU temperature
            "gpu_percent": [], # New: GPU usage percent
            "network_sent_mbps": [], # New: Instantaneous network speeds
            "network_recv_mbps": []
        }
        self._last_net_io_counters = psutil.net_io_counters()
        self._last_record_time = time.time()
        self.record_interval = 1 # Record data every 1 second for graphs/logging

        # Rolling window for graphs
        self.max_graph_data_points = 600 # Keep last 10 minutes of data (600 points * 1 sec/point)

        # --- UI Setup ---
        self.create_widgets()
        self.log_message("Application started.")
        self.update_stats() # Start monitoring loop

    def create_widgets(self):
        # Header with PRO branding
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        # Ensure the first column expands to push the version to the right if needed
        header_frame.grid_columnconfigure(0, weight=1) # Main title column
        header_frame.grid_columnconfigure(1, weight=0) # Version column (fixed width)

        ctk.CTkLabel(header_frame, text="Fusion Stress Tester", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, padx=(10,0), pady=10, sticky="w")
        # Place the PRO version in a separate column, sticking to the left of that column
        ctk.CTkLabel(header_frame, text="PRO v0.0.9", font=ctk.CTkFont(size=14, weight="bold"), text_color="gold").grid(row=0, column=1, padx=(5,10), pady=10, sticky="w")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.create_control_widgets(self.main_frame)
        self.create_monitoring_widgets(self.main_frame)
        self.create_log_widgets(self)

    def create_control_widgets(self, parent_frame):
        control_frame = ctk.CTkFrame(parent_frame)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        control_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(control_frame, text="Stress Control", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        # Global Start/Stop
        self.start_all_button = ctk.CTkButton(control_frame, text="Start All Stress Tests", command=self.start_global_stress, fg_color="green")
        self.start_all_button.pack(padx=20, pady=10, fill="x")
        self.stop_all_button = ctk.CTkButton(control_frame, text="Stop All Stress Tests", command=self.stop_global_stress, fg_color="red", state="disabled")
        self.stop_all_button.pack(padx=20, pady=(0, 10), fill="x")

        # Intensity Selector
        ctk.CTkLabel(control_frame, text="Overall Intensity:").pack(padx=20, pady=(10, 0), anchor="w")
        self.intensity_selector = ctk.CTkOptionMenu(control_frame, values=["Easy", "Medium", "Hard", "Extreme"])
        self.intensity_selector.set("Medium")
        self.intensity_selector.pack(padx=20, pady=5, fill="x")

        # CPU Stress
        cpu_frame = ctk.CTkFrame(control_frame)
        cpu_frame.pack(padx=20, pady=(15, 5), fill="x")
        ctk.CTkLabel(cpu_frame, text="CPU Stress", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,0))
        ctk.CTkLabel(cpu_frame, text="Cores to Stress (e.g., 4 or All):").pack(padx=10, pady=(5,0), anchor="w")
        self.cpu_cores_entry = ctk.CTkEntry(cpu_frame, placeholder_text="e.g., All")
        self.cpu_cores_entry.insert(0, "All")
        self.cpu_cores_entry.pack(padx=10, pady=2, fill="x")
        self.cpu_button = ctk.CTkButton(cpu_frame, text="Start CPU Stress", command=self.toggle_cpu_stress, fg_color="blue")
        self.cpu_button.pack(padx=10, pady=5, fill="x")

        # RAM Stress
        ram_frame = ctk.CTkFrame(control_frame)
        ram_frame.pack(padx=20, pady=(10, 5), fill="x")
        ctk.CTkLabel(ram_frame, text="RAM Stress", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,0))
        ctk.CTkLabel(ram_frame, text="RAM to allocate (MB):").pack(padx=10, pady=(5,0), anchor="w")
        self.ram_mb_entry = ctk.CTkEntry(ram_frame, placeholder_text="e.g., 1024")
        self.ram_mb_entry.insert(0, "1024") # Default 1GB
        self.ram_mb_entry.pack(padx=10, pady=2, fill="x")
        self.ram_button = ctk.CTkButton(ram_frame, text="Start RAM Stress", command=self.toggle_ram_stress, fg_color="blue")
        self.ram_button.pack(padx=10, pady=5, fill="x")

        # Disk Stress
        disk_frame = ctk.CTkFrame(control_frame)
        disk_frame.pack(padx=20, pady=(10, 5), fill="x")
        ctk.CTkLabel(disk_frame, text="Disk Stress", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,0))
        ctk.CTkLabel(disk_frame, text="File size (MB):").pack(padx=10, pady=(5,0), anchor="w")
        self.disk_mb_entry = ctk.CTkEntry(disk_frame, placeholder_text="e.g., 500")
        self.disk_mb_entry.insert(0, "500") # Default 500MB
        self.disk_mb_entry.pack(padx=10, pady=2, fill="x")
        self.ssd_endurance_checkbox = ctk.CTkCheckBox(disk_frame, text="Enable SSD Endurance Mode (Caution!)",
                                                        hover_color="orange") # Removed text_color_checked="red"
        self.ssd_endurance_checkbox.pack(padx=10, pady=(5,5), anchor="w")
        self.disk_button = ctk.CTkButton(disk_frame, text="Start Disk Stress", command=self.toggle_disk_stress, fg_color="blue")
        self.disk_button.pack(padx=10, pady=5, fill="x")

        # GPU Stress
        if GPU_AVAILABLE_TORCH:
            gpu_frame = ctk.CTkFrame(control_frame)
            gpu_frame.pack(padx=20, pady=(10, 5), fill="x")
            ctk.CTkLabel(gpu_frame, text="GPU Stress (CUDA)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,0))
            self.gpu_button = ctk.CTkButton(gpu_frame, text="Start GPU Stress", command=self.toggle_gpu_stress, fg_color="purple")
            self.gpu_button.pack(padx=10, pady=5, fill="x")
        else:
            ctk.CTkLabel(control_frame, text="GPU Stress (CUDA) Disabled: PyTorch/CUDA not found.", text_color="gray", font=ctk.CTkFont(size=12)).pack(padx=20, pady=5)

        # Network Stress
        network_frame = ctk.CTkFrame(control_frame)
        network_frame.pack(padx=20, pady=(10, 5), fill="x", expand=True)
        ctk.CTkLabel(network_frame, text="Network Stress (UDP Flood)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5, 0))

        ctk.CTkLabel(network_frame, text="Target IP/Hostname").pack(padx=10, pady=(5,0), anchor="w")
        self.target_ip_entry = ctk.CTkEntry(network_frame, placeholder_text="e.g., 127.0.0.1")
        self.target_ip_entry.insert(0, "127.0.0.1")
        self.target_ip_entry.pack(padx=10, pady=2, fill="x")

        ctk.CTkLabel(network_frame, text="Target Port").pack(padx=10, pady=(5,0), anchor="w")
        self.target_port_entry = ctk.CTkEntry(network_frame, placeholder_text="e.g., 80")
        self.target_port_entry.insert(0, "80")
        self.target_port_entry.pack(padx=10, pady=2, fill="x")

        ctk.CTkLabel(network_frame, text="Packet Size (bytes)").pack(padx=10, pady=(5,0), anchor="w")
        self.packet_size_entry = ctk.CTkEntry(network_frame, placeholder_text="e.g., 1024")
        self.packet_size_entry.insert(0, "1024")
        self.packet_size_entry.pack(padx=10, pady=2, fill="x")

        self.network_button = ctk.CTkButton(network_frame, text="Start Network Stress", command=self.toggle_network_stress, fg_color="orange")
        self.network_button.pack(padx=10, pady=(10, 5), fill="x")

        # Save/Load Profile
        profile_frame = ctk.CTkFrame(control_frame)
        profile_frame.pack(padx=20, pady=(15, 10), fill="x")
        ctk.CTkLabel(profile_frame, text="Test Profiles", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,0))
        self.save_profile_button = ctk.CTkButton(profile_frame, text="Save Current Profile", command=self.save_profile)
        self.save_profile_button.pack(side="left", padx=5, pady=5, expand=True)
        self.load_profile_button = ctk.CTkButton(profile_frame, text="Load Profile", command=self.load_profile)
        self.load_profile_button.pack(side="right", padx=5, pady=5, expand=True)


    def create_monitoring_widgets(self, parent_frame):
        monitor_frame = ctk.CTkFrame(parent_frame)
        monitor_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        monitor_frame.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(monitor_frame)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_view.add("System Status")
        self.tab_view.add("Safety & Monitoring")
        self.tab_view.add("Performance Graphs")

        # --- System Status Tab ---
        status_tab = self.tab_view.tab("System Status")
        status_tab.grid_columnconfigure(0, weight=1)
        # We don't need grid_columnconfigure(1) here as we're using a scrollable frame for dynamic content

        ctk.CTkLabel(status_tab, text="Live System Metrics", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(10, 5), sticky="w", padx=10)

        # Create a scrollable frame for CPU Cores, RAM, Disk, etc.
        # This will contain all the dynamic labels that might exceed space
        self.status_scroll_frame = ctk.CTkScrollableFrame(status_tab)
        self.status_scroll_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.status_scroll_frame.grid_columnconfigure(0, weight=1) # Allow content inside to expand

        # Now, place all the labels *inside* self.status_scroll_frame
        # Start the row counter for elements inside the scrollable frame from 0
        current_row_in_scroll_frame = 0

        self.cpu_label = ctk.CTkLabel(self.status_scroll_frame, text="CPU Usage: 0% (Avg)")
        self.cpu_label.grid(row=current_row_in_scroll_frame, column=0, padx=10, pady=5, sticky="w")
        current_row_in_scroll_frame += 1

        self.cpu_cores_labels = []
        for i in range(psutil.cpu_count(logical=True)):
            label = ctk.CTkLabel(self.status_scroll_frame, text=f"  Core {i}: 0%")
            label.grid(row=current_row_in_scroll_frame + i, column=0, padx=20, pady=0, sticky="w")
            self.cpu_cores_labels.append(label)

        current_row_in_scroll_frame += psutil.cpu_count(logical=True) # Advance row counter past all core labels

        self.ram_label = ctk.CTkLabel(self.status_scroll_frame, text="RAM Usage: 0%")
        self.ram_label.grid(row=current_row_in_scroll_frame, column=0, padx=10, pady=5, sticky="w")
        current_row_in_scroll_frame += 1
        
        self.disk_label = ctk.CTkLabel(self.status_scroll_frame, text="Disk Usage: 0%")
        self.disk_label.grid(row=current_row_in_scroll_frame, column=0, padx=10, pady=5, sticky="w")
        current_row_in_scroll_frame += 1
        
        self.cpu_temp_label = ctk.CTkLabel(self.status_scroll_frame, text="CPU Temp: N/A")
        self.cpu_temp_label.grid(row=current_row_in_scroll_frame, column=0, padx=10, pady=5, sticky="w")
        current_row_in_scroll_frame += 1
        
        self.gpu_status_label = ctk.CTkLabel(self.status_scroll_frame, text="GPU: N/A")
        self.gpu_status_label.grid(row=current_row_in_scroll_frame, column=0, padx=10, pady=5, sticky="w")
        current_row_in_scroll_frame += 1

        # For network labels, they can still be in two columns within the scrollable frame
        # We need a sub-frame or manage their grid in the same column but spanning
        # Let's put them in a sub-frame for better alignment in two columns if desired
        network_labels_frame = ctk.CTkFrame(self.status_scroll_frame, fg_color="transparent") # Use transparent frame
        network_labels_frame.grid(row=current_row_in_scroll_frame, column=0, padx=10, pady=5, sticky="ew")
        network_labels_frame.grid_columnconfigure(0, weight=1)
        network_labels_frame.grid_columnconfigure(1, weight=1)

        self.net_up_label = ctk.CTkLabel(network_labels_frame, text="Net Upload: 0 Mbps")
        self.net_up_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        self.net_down_label = ctk.CTkLabel(network_labels_frame, text="Net Download: 0 Mbps")
        self.net_down_label.grid(row=0, column=1, padx=0, pady=0, sticky="w")


        # --- Safety & Monitoring Tab ---
        safety_tab = self.tab_view.tab("Safety & Monitoring")
        safety_tab.grid_columnconfigure(0, weight=1)
        safety_tab.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(safety_tab, text="Safety Configuration", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(10, 5))

        ctk.CTkLabel(safety_tab, text="CPU Temp Limit (°C)").grid(row=1, column=0, padx=10, pady=(5,0), sticky="w")
        self.cpu_temp_limit_entry = ctk.CTkEntry(safety_tab, placeholder_text="e.g., 90")
        self.cpu_temp_limit_entry.insert(0, "90")
        self.cpu_temp_limit_entry.grid(row=1, column=1, padx=10, pady=2, sticky="ew")

        ctk.CTkLabel(safety_tab, text="RAM Free Threshold (GB)").grid(row=2, column=0, padx=10, pady=(5,0), sticky="w")
        self.ram_free_threshold_entry = ctk.CTkEntry(safety_tab, placeholder_text="e.g., 2.0")
        self.ram_free_threshold_entry.insert(0, "2.0")
        self.ram_free_threshold_entry.grid(row=2, column=1, padx=10, pady=2, sticky="ew")

        ctk.CTkLabel(safety_tab, text="Disk Free Threshold (GB)").grid(row=3, column=0, padx=10, pady=(5,0), sticky="w")
        self.disk_free_threshold_entry = ctk.CTkEntry(safety_tab, placeholder_text="e.g., 10.0")
        self.disk_free_threshold_entry.insert(0, "10.0")
        self.disk_free_threshold_entry.grid(row=3, column=1, padx=10, pady=2, sticky="ew")

        self.safety_monitoring_active = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(safety_tab, text="Enable Automatic Safety Stops", variable=self.safety_monitoring_active).grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(safety_tab, text="Current System Status", font=ctk.CTkFont(size=16, weight="bold")).grid(row=5, column=0, columnspan=2, pady=(10, 5))
        self.current_temp_label = ctk.CTkLabel(safety_tab, text="Current CPU Temp: N/A", font=ctk.CTkFont(size=12, weight="bold"))
        self.current_temp_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(10,0), sticky="w")
        self.current_ram_label = ctk.CTkLabel(safety_tab, text="Current RAM Free: N/A", font=ctk.CTkFont(size=12, weight="bold"))
        self.current_ram_label.grid(row=7, column=0, columnspan=2, padx=10, pady=0, sticky="w")
        self.current_disk_label = ctk.CTkLabel(safety_tab, text="Current Disk Free: N/A", font=ctk.CTkFont(size=12, weight="bold"))
        self.current_disk_label.grid(row=8, column=0, columnspan=2, padx=10, pady=(0,10), sticky="w")

        self.enable_cloud_api_checkbox = ctk.CTkCheckBox(safety_tab, text="Enable Cloud API Reporting (Alpha)")
        self.enable_cloud_api_checkbox.grid(row=9, column=0, columnspan=2, padx=10, pady=10, sticky="w")


        # --- Performance Graphs Tab ---
        graph_tab = self.tab_view.tab("Performance Graphs")
        graph_tab.grid_columnconfigure(0, weight=1)
        graph_tab.grid_rowconfigure(0, weight=1)

        self.figure, self.ax = plt.subplots(figsize=(8, 5))
        # Ensure dark mode compatibility for matplotlib plots
        if ctk.get_appearance_mode() == "Dark":
            self.figure.set_facecolor("#2B2B2B") # CustomTkinter dark background
            self.ax.set_facecolor("#2B2B2B")
            self.ax.tick_params(colors='white')
            self.ax.yaxis.label.set_color('white')
            self.ax.xaxis.label.set_color('white')
            self.ax.title.set_color('white')
            self.ax.spines['left'].set_color('white')
            self.ax.spines['bottom'].set_color('white')
            self.ax.spines['right'].set_color('white')
            self.ax.spines['top'].set_color('white')
            self.ax.legend(facecolor='#2B2B2B', edgecolor='white', labelcolor='white') # Adjust legend
            self.ax.grid(True, color='gray') # Make grid visible in dark mode
        else:
            self.figure.set_facecolor("white")
            self.ax.set_facecolor("white")
            self.ax.grid(True, color='lightgray')

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_tab)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)

        self.toolbar = NavigationToolbar2Tk(self.canvas, graph_tab)
        self.toolbar.update()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        export_frame = ctk.CTkFrame(graph_tab)
        export_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(export_frame, text="Benchmarking Data Export:").pack(side="left", padx=(10,5))
        self.export_csv_button = ctk.CTkButton(export_frame, text="Export Data to CSV", command=self.export_performance_data)
        self.export_csv_button.pack(side="right", padx=(5,10))

    def create_log_widgets(self, parent_frame):
        log_frame = ctk.CTkFrame(parent_frame)
        log_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="System Logs", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

        self.log_text = ctk.CTkTextbox(log_frame, wrap="word", height=150)
        self.log_text.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.log_text.configure(state="disabled") # Make read-only

    def log_message(self, message):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{timestamp} {message}\n")
        self.log_text.see("end") # Auto-scroll to bottom
        self.log_text.configure(state="disabled")

    def start_global_stress(self):
        if self.is_stressing:
            return

        self.is_stressing = True
        self.log_message("Starting all selected stress tests...")
        self.start_all_button.configure(state="disabled")
        self.stop_all_button.configure(state="normal")

        # Reset performance data for new benchmark
        self.performance_data = {k: [] for k in self.performance_data}
        self.update_graphs() # Clear graph

        # Start individual stress tests
        self.start_cpu_stress()
        self.start_ram_stress()
        self.start_disk_stress()
        if GPU_AVAILABLE_TORCH:
            self.start_gpu_stress()
        self.start_network_stress()

    def stop_global_stress(self, reason="stopped by user"):
        if not self.is_stressing:
            return

        self.is_stressing = False
        self.log_message(f"Stopping all stress tests ({reason})...")
        self.start_all_button.configure(state="normal")
        self.stop_all_button.configure(state="disabled")

        self.stop_cpu_stress()
        self.stop_ram_stress()
        self.stop_disk_stress()
        self.stop_gpu_stress()
        self.stop_network_stress()

        self.log_message("All stress tests stopped.")

    # --- Individual Stress Test Controls ---

    def toggle_cpu_stress(self):
        if self.stress_workers["cpu"]: # Check if any CPU processes are running
            self.stop_cpu_stress()
        else:
            self.start_cpu_stress()

    def start_cpu_stress(self):
        if self.stress_workers["cpu"]: # Already running
            return

        num_cores_str = self.cpu_cores_entry.get().strip().lower()
        total_logical_cores = psutil.cpu_count(logical=True)
        num_cores_to_stress = total_logical_cores # Default to all

        if num_cores_str != "all":
            try:
                num_cores_to_stress = int(num_cores_str)
                if not (1 <= num_cores_to_stress <= total_logical_cores):
                    raise ValueError(f"Number of cores must be between 1 and {total_logical_cores}.")
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please enter a valid number of CPU cores (1-{total_logical_cores}) or 'All'. Error: {e}")
                self.log_message(f"ERROR: Invalid CPU cores input: '{num_cores_str}' - {e}")
                return

        self.log_message(f"Starting CPU stress test on {num_cores_to_stress} cores.")
        self.stop_events["cpu"].clear() # Clear the multiprocessing event

        # Create one process per selected core
        for i in range(num_cores_to_stress):
            p = multiprocessing.Process(target=cpu_stress_worker, args=(self.stop_events["cpu"],), daemon=True)
            self.stress_workers["cpu"].append(p)
            p.start()
            # Note: Setting CPU affinity is complex and platform-specific for multiprocessing.
            # This current setup will launch processes, OS will schedule them.

        self.cpu_button.configure(text=f"Stop CPU Stress ({len(self.stress_workers['cpu'])} Cores)", fg_color="red")

    def stop_cpu_stress(self):
        if self.stress_workers["cpu"]:
            self.stop_events["cpu"].set() # Signal all processes to stop
            self.log_message("Waiting for CPU stress processes to terminate...")
            for p in self.stress_workers["cpu"]:
                if p.is_alive():
                    p.join(timeout=2) # Give process time to clean up
                    if p.is_alive():
                        p.terminate() # Force terminate if still alive
                        p.join(timeout=1) # Wait briefly after terminate
                        self.log_message(f"WARNING: CPU stress process {p.pid} forcefully terminated.")
            self.stress_workers["cpu"].clear() # Clear the list of processes
            self.cpu_button.configure(text="Start CPU Stress", fg_color="blue")
            self.log_message("CPU stress stopped.")

    def toggle_ram_stress(self):
        if self.stress_workers["ram"] and self.stress_workers["ram"].is_alive():
            self.stop_ram_stress()
        else:
            self.start_ram_stress()

    def start_ram_stress(self):
        if self.stress_workers["ram"] and self.stress_workers["ram"].is_alive():
            return
        try:
            ram_mb = int(self.ram_mb_entry.get())
            if ram_mb <= 0:
                raise ValueError("Allocation size must be positive.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive number for RAM to allocate (MB).")
            self.log_message("ERROR: Invalid RAM allocation size.")
            return

        self.log_message(f"Starting RAM stress test, attempting to allocate {ram_mb}MB.")
        self.stop_events["ram"].clear()
        self.stress_workers["ram"] = threading.Thread(target=ram_stress_worker, args=(ram_mb, self.stop_events["ram"], self.log_message), daemon=True)
        self.stress_workers["ram"].start()
        self.ram_button.configure(text="Stop RAM Stress", fg_color="red")

    def stop_ram_stress(self):
        if self.stress_workers["ram"] and self.stress_workers["ram"].is_alive():
            self.stop_events["ram"].set()
            self.stress_workers["ram"].join(timeout=2)
            if self.stress_workers["ram"].is_alive():
                self.log_message("WARNING: RAM stress thread did not terminate cleanly.")
            self.stress_workers["ram"] = None
            self.ram_button.configure(text="Start RAM Stress", fg_color="blue")
            self.log_message("RAM stress stopped.")

    def toggle_disk_stress(self):
        if self.stress_workers["disk"] and self.stress_workers["disk"].is_alive():
            self.stop_disk_stress()
        else:
            self.start_disk_stress()

    def start_disk_stress(self):
        if self.stress_workers["disk"] and self.stress_workers["disk"].is_alive():
            return
        try:
            disk_mb = int(self.disk_mb_entry.get())
            if disk_mb <= 0:
                raise ValueError("File size must be positive.")
            if disk_mb > (psutil.disk_usage('/').free / (1024*1024)):
                confirm = messagebox.askyesno("Disk Space Warning", f"You are trying to allocate {disk_mb}MB, but only {psutil.disk_usage('/').free / (1024*1024):.0f}MB is free on your disk. This may cause issues. Continue?")
                if not confirm:
                    self.log_message("Disk stress aborted by user due to low disk space warning.")
                    return
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter a valid positive number for Disk File Size (MB). Error: {e}")
            self.log_message(f"ERROR: Invalid disk file size. {e}")
            return

        endurance_mode = self.ssd_endurance_checkbox.get()
        self.log_message(f"Starting Disk stress test (File Size: {disk_mb}MB, Endurance Mode: {endurance_mode}).")
        self.stop_events["disk"].clear()
        self.stress_workers["disk"] = threading.Thread(target=disk_stress_worker, args=(disk_mb, self.stop_events["disk"], endurance_mode, self.log_message), daemon=True)
        self.stress_workers["disk"].start()
        self.disk_button.configure(text="Stop Disk Stress", fg_color="red")

    def stop_disk_stress(self):
        if self.stress_workers["disk"] and self.stress_workers["disk"].is_alive():
            self.stop_events["disk"].set()
            self.stress_workers["disk"].join(timeout=5) # Disk I/O might take longer to stop
            if self.stress_workers["disk"].is_alive():
                self.log_message("WARNING: Disk stress thread did not terminate cleanly.")
            self.stress_workers["disk"] = None
            self.disk_button.configure(text="Start Disk Stress", fg_color="blue")
            self.log_message("Disk stress stopped.")
            # Ensure file is removed if not in endurance mode
            if not self.ssd_endurance_checkbox.get() and os.path.exists(DISK_STRESS_FILE_NAME):
                 try:
                     os.remove(DISK_STRESS_FILE_NAME)
                     self.log_message(f"Cleaned up temporary disk file: {DISK_STRESS_FILE_NAME}")
                 except OSError as e:
                     self.log_message(f"ERROR: Failed to remove temporary disk file {DISK_STRESS_FILE_NAME}: {e}")

    def toggle_gpu_stress(self):
        if not GPU_AVAILABLE_TORCH:
            self.log_message("ERROR: GPU stress requires PyTorch with CUDA and an NVIDIA GPU.")
            messagebox.showerror("GPU Error", "NVIDIA CUDA GPU not detected or PyTorch not installed with CUDA support.")
            return

        if self.stress_workers["gpu"] and self.stress_workers["gpu"].is_alive():
            self.stop_gpu_stress()
        else:
            self.start_gpu_stress()

    def start_gpu_stress(self):
        if not GPU_AVAILABLE_TORCH: return

        if not (self.stress_workers["gpu"] and self.stress_workers["gpu"].is_alive()):
            intensity = self.intensity_selector.get()
            self.log_message(f"Starting GPU stress test ({intensity} intensity).")
            self.stop_events["gpu"].clear()
            self.stress_workers["gpu"] = threading.Thread(target=gpu_stress_worker, args=(self.stop_events["gpu"], intensity, self.log_message), daemon=True)
            self.stress_workers["gpu"].start()
            self.gpu_button.configure(text="Stop GPU Stress", fg_color="red")

    def stop_gpu_stress(self):
        if self.stress_workers["gpu"] and self.stress_workers["gpu"].is_alive():
            self.stop_events["gpu"].set()
            self.stress_workers["gpu"].join(timeout=5)
            if self.stress_workers["gpu"].is_alive():
                self.log_message("WARNING: GPU stress thread did not terminate cleanly.")
            self.stress_workers["gpu"] = None
            if GPU_AVAILABLE_TORCH:
                self.gpu_button.configure(text="Start GPU Stress", fg_color="purple")
            self.log_message("GPU stress stopped.")

    def toggle_network_stress(self):
        if self.stress_workers["network"] and self.stress_workers["network"].is_alive():
            self.stop_network_stress()
        else:
            self.start_network_stress()

    def start_network_stress(self):
        if self.stress_workers["network"] and self.stress_workers["network"].is_alive():
            return
        target_ip = self.target_ip_entry.get().strip()
        if not target_ip:
            messagebox.showerror("Invalid Input", "Target IP/Hostname cannot be empty.")
            self.log_message("ERROR: Network stress target IP is empty.")
            return
        try:
            target_port = int(self.target_port_entry.get())
            packet_size = int(self.packet_size_entry.get())
            if not (1 <= target_port <= 65535 and 1 <= packet_size <= 65507):
                raise ValueError("Invalid port (1-65535) or packet size (1-65507) range.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numbers for Target Port and Packet Size. Error: {e}")
            self.log_message(f"ERROR: Invalid network stress parameters. {e}")
            return

        self.log_message(f"Starting network stress (UDP Flood) to {target_ip}:{target_port} with {packet_size} byte packets.")
        self.stop_events["network"].clear()
        self.stress_workers["network"] = threading.Thread(target=udp_flood_worker, args=(target_ip, target_port, packet_size, self.stop_events["network"], self.log_message), daemon=True)
        self.stress_workers["network"].start()
        self.network_button.configure(text="Stop Network Stress", fg_color="red")

    def stop_network_stress(self):
        if self.stress_workers["network"] and self.stress_workers["network"].is_alive():
            self.stop_events["network"].set()
            self.stress_workers["network"].join(timeout=2)
            if self.stress_workers["network"].is_alive():
                self.log_message("WARNING: Network stress thread did not terminate cleanly.")
            self.stress_workers["network"] = None
            self.network_button.configure(text="Start Network Stress", fg_color="orange")
            self.log_message("Network stress stopped.")


    # --- Monitoring and Safety Systems ---
    def update_stats(self):
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=None) # Overall CPU usage
        cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True) # Per-core usage
        self.cpu_label.configure(text=f"CPU Usage: {cpu_percent:.1f}% (Avg)")
        for i, percent in enumerate(cpu_percent_per_core):
            if i < len(self.cpu_cores_labels): # Update existing labels
                self.cpu_cores_labels[i].configure(text=f"  Core {i}: {percent:.1f}%")

        # RAM Usage
        ram = psutil.virtual_memory()
        self.ram_label.configure(text=f"RAM Usage: {ram.percent:.1f}% ({ram.used / (1024**3):.2f}GB / {ram.total / (1024**3):.2f}GB)")
        ram_free_gb = ram.available / (1024**3)

        # Disk Usage (for root partition)
        try:
            disk_usage = psutil.disk_usage('/')
            self.disk_label.configure(text=f"Disk Usage: {disk_usage.percent:.1f}% ({disk_usage.used / (1024**3):.2f}GB / {disk_usage.total / (1024**3):.2f}GB)")
            disk_free_gb = disk_usage.free / (1024**3)
        except Exception as e:
            self.disk_label.configure(text=f"Disk Usage: N/A ({e})")
            disk_free_gb = float('inf') # Set to inf to prevent false safety trigger


        # CPU Temperature (platform-dependent)
        avg_temp = None
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                cpu_temp_found = False
                for name, entries in temps.items():
                    for entry in entries:
                        # Prioritize 'package id', 'cpu', 'core' temperatures
                        if 'package id' in entry.label.lower() or 'cpu' in entry.label.lower() or 'core' in entry.label.lower():
                            if entry.current is not None:
                                avg_temp = entry.current
                                cpu_temp_found = True
                                break
                    if cpu_temp_found:
                        break
                if avg_temp is not None:
                    self.cpu_temp_label.configure(text=f"CPU Temp: {avg_temp:.1f}°C")
                else:
                    self.cpu_temp_label.configure(text="CPU Temp: N/A (No relevant sensor found)")
            else:
                self.cpu_temp_label.configure(text="CPU Temp: N/A (No sensor data)")
        except Exception as e:
            self.cpu_temp_label.configure(text=f"CPU Temp: Error ({e})")
            avg_temp = float('nan') # Store as NaN for graph if error


        # GPU Monitoring (NVIDIA via pynvml, or basic PyTorch if NVML fails)
        gpu_temp = float('nan')
        gpu_percent = float('nan')
        gpu_mem_allocated_gb = float('nan')
        
        if GPU_AVAILABLE_NVML: # Prefer NVML for comprehensive NVIDIA data
            try:
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0) # Monitor first GPU
                    temp_info = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMP_GPU)
                    gpu_temp = temp_info

                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_percent = utilization.gpu

                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    gpu_mem_allocated_gb = mem_info.used / (1024**3)
                    gpu_mem_total_gb = mem_info.total / (1024**3)

                    self.gpu_status_label.configure(text=f"GPU: {gpu_percent:.1f}% Util, {gpu_temp:.1f}°C, {gpu_mem_allocated_gb:.2f}GB Used")
                else:
                    self.gpu_status_label.configure(text="GPU: N/A (No NVIDIA GPU detected by NVML)")
            except pynvml.NVMLError as e:
                self.gpu_status_label.configure(text=f"GPU: NVML Error ({e}). Trying PyTorch...")
                # Fallback to PyTorch if NVML fails (e.g., driver issues)
                if GPU_AVAILABLE_TORCH:
                    try:
                        allocated = torch.cuda.memory_allocated(0) / (1024**3)
                        cached = torch.cuda.memory_reserved(0) / (1024**3)
                        self.gpu_status_label.configure(text=f"GPU (PyTorch): {allocated:.2f}GB Used / {cached:.2f}GB Reserved")
                        gpu_mem_allocated_gb = allocated
                    except Exception as e_torch:
                        self.gpu_status_label.configure(text=f"GPU: N/A (PyTorch Error: {e_torch})")
            finally:
                try: pynvml.nvmlShutdown() # Always try to shutdown NVML
                except pynvml.NVMLError: pass # Ignore if already shut down or not initialized
        elif GPU_AVAILABLE_TORCH: # If NVML not available but PyTorch is (e.g., AMD GPU with PyTorch ROCm, or Intel GPU)
            try:
                allocated = torch.cuda.memory_allocated(0) / (1024**3)
                cached = torch.cuda.memory_reserved(0) / (1024**3)
                self.gpu_status_label.configure(text=f"GPU (PyTorch): {allocated:.2f}GB Used / {cached:.2f}GB Reserved")
                gpu_mem_allocated_gb = allocated
            except Exception as e_torch:
                self.gpu_status_label.configure(text=f"GPU: N/A (PyTorch Error: {e_torch})")
        else:
            self.gpu_status_label.configure(text="GPU: N/A (No GPU detected)")

        # Network Usage (in Mbps)
        net_io = psutil.net_io_counters()
        time_diff = time.time() - self._last_record_time
        bytes_sent_diff = net_io.bytes_sent - self._last_net_io_counters.bytes_sent
        bytes_recv_diff = net_io.bytes_recv - self._last_net_io_counters.bytes_recv

        upload_mbps = (bytes_sent_diff / (1024 * 1024)) * 8 / time_diff if time_diff > 0 else 0 # MBps to Mbps
        download_mbps = (bytes_recv_diff / (1024 * 1024)) * 8 / time_diff if time_diff > 0 else 0 # MBps to Mbps

        self.net_up_label.configure(text=f"Net Upload: {upload_mbps:.2f} Mbps")
        self.net_down_label.configure(text=f"Net Download: {download_mbps:.2f} Mbps")
        self._last_net_io_counters = net_io


        # --- Safety System Updates ---
        self.current_temp_label.configure(text=f"Current CPU Temp: {avg_temp:.1f}°C" if avg_temp is not None else "Current CPU Temp: N/A")
        self.current_ram_label.configure(text=f"Current RAM Free: {ram_free_gb:.2f} GB")
        self.current_disk_label.configure(text=f"Current Disk Free: {disk_free_gb:.2f} GB")

        if self.is_stressing and self.safety_monitoring_active.get():
            self.perform_safety_checks(avg_temp, ram_free_gb, disk_free_gb)

        # --- Benchmarking Data Collection (with rolling window) ---
        current_time = time.time()
        # Record data only if enough time has passed since last record, or if it's the first record
        if current_time - self._last_record_time >= self.record_interval:
            self.performance_data["timestamp"].append(current_time)
            self.performance_data["cpu_percent"].append(cpu_percent)
            self.performance_data["cpu_percent_per_core"].append(cpu_percent_per_core)
            self.performance_data["ram_percent"].append(ram.percent)
            self.performance_data["disk_percent"].append(disk_usage.percent if 'disk_usage' in locals() else 0.0)
            self.performance_data["cpu_temp"].append(avg_temp if avg_temp is not None else float('nan'))
            self.performance_data["gpu_mem_allocated"].append(gpu_mem_allocated_gb)
            self.performance_data["gpu_temp"].append(gpu_temp)
            self.performance_data["gpu_percent"].append(gpu_percent)
            self.performance_data["network_sent_mbps"].append(upload_mbps)
            self.performance_data["network_recv_mbps"].append(download_mbps)

            # Apply rolling window
            if len(self.performance_data["timestamp"]) > self.max_graph_data_points:
                for key in self.performance_data:
                    # For cpu_percent_per_core, need to pop the list itself
                    if key == "cpu_percent_per_core":
                        if self.performance_data[key]:
                            self.performance_data[key].pop(0)
                    else:
                        self.performance_data[key].pop(0)
            
            self._last_record_time = current_time # Update timestamp AFTER collecting data

            self.update_graphs()
            if self.enable_cloud_api_checkbox.get():
                threading.Thread(target=self.send_metrics_to_cloud, daemon=True).start()


        self.after(self.record_interval * 1000, self.update_stats) # Schedule next update


    def perform_safety_checks(self, current_temp, current_ram_free, current_disk_free):
        # CPU Temp Check
        try:
            temp_limit = float(self.cpu_temp_limit_entry.get())
            if current_temp is not None and not math.isnan(current_temp) and current_temp > temp_limit:
                self.log_message(f"EMERGENCY STOP: CPU temperature {current_temp:.1f}°C exceeded limit {temp_limit}°C.")
                self.stop_global_stress("CPU temperature exceeded limit")
                messagebox.showerror("Safety Stop", f"CPU temperature ({current_temp:.1f}°C) exceeded configured limit ({temp_limit}°C). Stress test stopped.")
                return
        except ValueError:
            pass

        # RAM Free Threshold Check
        try:
            ram_threshold = float(self.ram_free_threshold_entry.get())
            if current_ram_free is not None and current_ram_free < ram_threshold:
                self.log_message(f"EMERGENCY STOP: RAM free ({current_ram_free:.2f}GB) below threshold {ram_threshold:.2f}GB.")
                self.stop_global_stress("RAM free below threshold")
                messagebox.showerror("Safety Stop", f"RAM free ({current_ram_free:.2f}GB) is below configured threshold ({ram_threshold:.2f}GB). Stress test stopped.")
                return
        except ValueError:
            pass

        # Disk Free Threshold Check
        try:
            disk_threshold = float(self.disk_free_threshold_entry.get())
            if current_disk_free is not None and current_disk_free < disk_threshold:
                self.log_message(f"EMERGENCY STOP: Disk free ({current_disk_free:.2f}GB) below threshold {disk_threshold:.2f}GB.")
                self.stop_global_stress("Disk free below threshold")
                messagebox.showerror("Safety Stop", f"Disk free ({current_disk_free:.2f}GB) is below configured threshold ({disk_threshold:.2f}GB). Stress test stopped.")
                return
        except ValueError:
            pass


    def update_graphs(self):
        self.ax.clear()
        if not self.performance_data["timestamp"]:
            self.ax.text(0.5, 0.5, "No data yet", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
            self.canvas.draw_idle()
            return

        # Calculate time in minutes relative to start
        timestamps_minutes = [(t - self.performance_data["timestamp"][0]) / 60 for t in self.performance_data["timestamp"]]

        if len(timestamps_minutes) > 0: # Even one point can be plotted, but lines need >1
            # Plot CPU, RAM, Disk Usage (%)
            self.ax.plot(timestamps_minutes, self.performance_data["cpu_percent"], label="CPU %", color='tab:blue')
            self.ax.plot(timestamps_minutes, self.performance_data["ram_percent"], label="RAM %", color='tab:green')
            self.ax.plot(timestamps_minutes, self.performance_data["disk_percent"], label="Disk %", color='tab:orange')

            # Plot CPU Temperature (°C) - filtered for valid values
            valid_cpu_temps_x = [timestamps_minutes[i] for i, val in enumerate(self.performance_data["cpu_temp"]) if not math.isnan(val)]
            valid_cpu_temps_y = [val for val in self.performance_data["cpu_temp"] if not math.isnan(val)]
            if valid_cpu_temps_x:
                self.ax.plot(valid_cpu_temps_x, valid_cpu_temps_y, label="CPU Temp (°C)", linestyle='--', color='tab:red')

            # Plot GPU Data (if available and valid)
            if GPU_AVAILABLE_TORCH or GPU_AVAILABLE_NVML:
                valid_gpu_temps_x = [timestamps_minutes[i] for i, val in enumerate(self.performance_data["gpu_temp"]) if not math.isnan(val)]
                valid_gpu_temps_y = [val for val in self.performance_data["gpu_temp"] if not math.isnan(val)]
                if valid_gpu_temps_x:
                    self.ax.plot(valid_gpu_temps_x, valid_gpu_temps_y, label="GPU Temp (°C)", linestyle=':', color='purple')

                valid_gpu_percent_x = [timestamps_minutes[i] for i, val in enumerate(self.performance_data["gpu_percent"]) if not math.isnan(val)]
                valid_gpu_percent_y = [val for val in self.performance_data["gpu_percent"] if not math.isnan(val)]
                if valid_gpu_percent_x:
                    self.ax.plot(valid_gpu_percent_x, valid_gpu_percent_y, label="GPU Usage (%)", linestyle=':', color='darkgreen')

                valid_gpu_mem_x = [timestamps_minutes[i] for i, val in enumerate(self.performance_data["gpu_mem_allocated"]) if not math.isnan(val)]
                valid_gpu_mem_y = [val for val in self.performance_data["gpu_mem_allocated"] if not math.isnan(val)]
                if valid_gpu_mem_x:
                    self.ax.plot(valid_gpu_mem_x, valid_gpu_mem_y, label="GPU Mem (GB)", linestyle='-.', color='magenta')

            # Plot Network Speeds (Mbps)
            self.ax.plot(timestamps_minutes, self.performance_data["network_sent_mbps"], label="Net Sent (Mbps)", linestyle='-.', color='cyan')
            self.ax.plot(timestamps_minutes, self.performance_data["network_recv_mbps"], label="Net Recv (Mbps)", linestyle='-.', color='pink')


        self.ax.set_xlabel("Time (minutes)")
        self.ax.set_ylabel("Usage (%) / Value")
        self.ax.set_title("System Performance Over Time")
        
        # Legend outside the plot area
        self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')
        
        self.ax.grid(True)
        self.figure.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend
        self.canvas.draw_idle()

    def export_performance_data(self):
        if not self.performance_data["timestamp"]:
            messagebox.showinfo("Export Data", "No performance data to export yet.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Performance Data As"
        )
        if not file_path:
            return

        try:
            fieldnames = [
                "Timestamp_Unix",
                "Timestamp_Relative_Minutes",
                "CPU_Usage_Percent_Overall",
            ]
            # Dynamically add per-core CPU fields
            for i in range(len(self.performance_data["cpu_percent_per_core"][0]) if self.performance_data["cpu_percent_per_core"] else 0):
                fieldnames.append(f"CPU_Core_{i}_Percent")
            
            fieldnames.extend([
                "RAM_Usage_Percent",
                "Disk_Usage_Percent",
                "CPU_Temperature_C",
                "GPU_Temperature_C",
                "GPU_Usage_Percent",
                "GPU_Memory_Allocated_GB",
                "Network_Sent_Mbps",
                "Network_Recv_Mbps"
            ])
            
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                start_time = self.performance_data["timestamp"][0]
                for i in range(len(self.performance_data["timestamp"])):
                    row = {
                        "Timestamp_Unix": self.performance_data["timestamp"][i],
                        "Timestamp_Relative_Minutes": (self.performance_data["timestamp"][i] - start_time) / 60,
                        "CPU_Usage_Percent_Overall": self.performance_data["cpu_percent"][i],
                    }
                    # Add per-core CPU data
                    if i < len(self.performance_data["cpu_percent_per_core"]):
                        for j, core_percent in enumerate(self.performance_data["cpu_percent_per_core"][i]):
                            row[f"CPU_Core_{j}_Percent"] = core_percent
                    
                    row.update({
                        "RAM_Usage_Percent": self.performance_data["ram_percent"][i],
                        "Disk_Usage_Percent": self.performance_data["disk_percent"][i],
                        "CPU_Temperature_C": self.performance_data["cpu_temp"][i],
                        "GPU_Temperature_C": self.performance_data["gpu_temp"][i],
                        "GPU_Usage_Percent": self.performance_data["gpu_percent"][i],
                        "GPU_Memory_Allocated_GB": self.performance_data["gpu_mem_allocated"][i],
                        "Network_Sent_Mbps": self.performance_data["network_sent_mbps"][i],
                        "Network_Recv_Mbps": self.performance_data["network_recv_mbps"][i]
                    })
                    writer.writerow(row)
            self.log_message(f"Performance data exported to: {file_path}")
            messagebox.showinfo("Export Data", f"Performance data successfully exported to:\n{file_path}")
        except Exception as e:
            self.log_message(f"ERROR: Failed to export data: {e}")
            messagebox.showerror("Export Error", f"Failed to export data: {e}")

    def send_metrics_to_cloud(self):
        if not self.enable_cloud_api_checkbox.get():
            return
        if not self.performance_data["timestamp"]:
            return

        latest_index = len(self.performance_data["timestamp"]) - 1
        if latest_index < 0:
            return

        data_point = {
            "timestamp": self.performance_data["timestamp"][latest_index],
            "cpu_usage_percent": self.performance_data["cpu_percent"][latest_index],
            "ram_usage_percent": self.performance_data["ram_percent"][latest_index],
            "disk_usage_percent": self.performance_data["disk_percent"][latest_index],
            "cpu_temperature_c": self.performance_data["cpu_temp"][latest_index],
            "gpu_temperature_c": self.performance_data["gpu_temp"][latest_index],
            "gpu_usage_percent": self.performance_data["gpu_percent"][latest_index],
            "gpu_memory_allocated_gb": self.performance_data["gpu_mem_allocated"][latest_index],
            "network_sent_mbps": self.performance_data["network_sent_mbps"][latest_index],
            "network_recv_mbps": self.performance_data["network_recv_mbps"][latest_index]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CLOUD_API_KEY}" # Replace with actual auth mechanism
        }

        try:
            # Import requests here to avoid circular dependency or unnecessary global import if not used
            import requests
            response = requests.post(CLOUD_API_ENDPOINT, json=data_point, headers=headers, timeout=5)
            response.raise_for_status()
            self.log_message(f"Cloud API: Sent metrics successfully. Status: {response.status_code}")
        except ImportError:
            self.log_message("ERROR: 'requests' library not found. Cannot send metrics to cloud API.")
        except Exception as e:
            self.log_message(f"ERROR: Cloud API reporting failed: {e}")

    def save_profile(self):
        profile = {
            "intensity_level": self.intensity_selector.get(),
            "cpu_cores_to_stress": self.cpu_cores_entry.get(),
            "ram_allocation_mb": self.ram_mb_entry.get(),
            "disk_file_size_mb": self.disk_mb_entry.get(),
            "ssd_endurance_mode": self.ssd_endurance_checkbox.get(),
            "network_target_ip": self.target_ip_entry.get(),
            "network_target_port": self.target_port_entry.get(),
            "network_packet_size": self.packet_size_entry.get(),
            "cpu_temp_limit": self.cpu_temp_limit_entry.get(),
            "ram_free_threshold": self.ram_free_threshold_entry.get(),
            "disk_free_threshold": self.disk_free_threshold_entry.get(),
            "safety_monitoring_active": self.safety_monitoring_active.get(),
            "cloud_api_reporting_active": self.enable_cloud_api_checkbox.get()
        }
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=PROFILE_FILE_NAME,
                title="Save Test Profile As"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(profile, f, indent=4)
                self.log_message(f"Test profile saved to: {file_path}")
                messagebox.showinfo("Save Profile", f"Test profile saved successfully to:\n{file_path}")
        except Exception as e:
            self.log_message(f"ERROR: Failed to save profile: {e}")
            messagebox.showerror("Save Profile Error", f"Failed to save profile: {e}")

    def load_profile(self):
        try:
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=PROFILE_FILE_NAME,
                title="Load Test Profile"
            )
            if file_path:
                with open(file_path, 'r') as f:
                    profile = json.load(f)
                
                # Apply loaded settings to UI widgets
                self.intensity_selector.set(profile.get("intensity_level", "Medium"))
                self.cpu_cores_entry.delete(0, tk.END)
                self.cpu_cores_entry.insert(0, profile.get("cpu_cores_to_stress", "All"))
                self.ram_mb_entry.delete(0, tk.END)
                self.ram_mb_entry.insert(0, profile.get("ram_allocation_mb", "1024"))
                self.disk_mb_entry.delete(0, tk.END)
                self.disk_mb_entry.insert(0, profile.get("disk_file_size_mb", "500"))
                self.ssd_endurance_checkbox.set(profile.get("ssd_endurance_mode", False))
                self.target_ip_entry.delete(0, tk.END)
                self.target_ip_entry.insert(0, profile.get("network_target_ip", "127.0.0.1"))
                self.target_port_entry.delete(0, tk.END)
                self.target_port_entry.insert(0, profile.get("network_target_port", "80"))
                self.packet_size_entry.delete(0, tk.END)
                self.packet_size_entry.insert(0, profile.get("network_packet_size", "1024"))
                self.cpu_temp_limit_entry.delete(0, tk.END)
                self.cpu_temp_limit_entry.insert(0, profile.get("cpu_temp_limit", "90"))
                self.ram_free_threshold_entry.delete(0, tk.END)
                self.ram_free_threshold_entry.insert(0, profile.get("ram_free_threshold", "2.0"))
                self.disk_free_threshold_entry.delete(0, tk.END)
                self.disk_free_threshold_entry.insert(0, profile.get("disk_free_threshold", "10.0"))
                self.safety_monitoring_active.set(profile.get("safety_monitoring_active", True))
                self.enable_cloud_api_checkbox.set(profile.get("cloud_api_reporting_active", False))
                
                self.log_message(f"Test profile loaded from: {file_path}")
                messagebox.showinfo("Load Profile", f"Test profile loaded successfully from:\n{file_path}")
        except FileNotFoundError:
            messagebox.showerror("Load Profile Error", "Selected profile file not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Load Profile Error", "Invalid JSON file format. Please select a valid profile file.")
        except Exception as e:
            self.log_message(f"ERROR: Failed to load profile: {e}")
            messagebox.showerror("Load Profile Error", f"Failed to load profile: {e}")


if __name__ == "__main__":
    # Important for multiprocessing tests on Windows executables
    multiprocessing.freeze_support()

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = StressTesterApp()
    app.mainloop()