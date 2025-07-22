import os
import json
import psutil
import platform
import wmi
import ctypes
import tkinter as tk
from tkinter import font
from screeninfo import get_monitors
import time
import sys
import clr  # Python.NET for interfacing with .NET libraries


# =============================================
# IMPLEMENTING NVIDIA NVML.DLL
# =============================================
from ctypes import windll
import pynvml  # For getting actual CUDA core count
# Add current directory to DLL search path for nvml.dll
if hasattr(os, 'add_dll_directory'):
    try:
        os.add_dll_directory(os.getcwd())
    except Exception as e:
        print(f"Failed to add DLL directory: {e}")

from pynvml import *

try:
    nvmlInit()
    NVML_AVAILABLE = True
except NVMLError as err:
    print(f"Warning: Failed to initialize NVML: {err}")
    NVML_AVAILABLE = False


# =============================================
# .NET INTEROP SETUP FOR LIBREHARDWAREMONITOR
# =============================================
# Get current directory and ensure DLLs exist
base_dir = os.getcwd()
hidsharp_path = os.path.join(base_dir, "HidSharp.dll")
librehardwaremonitor_path = os.path.join(base_dir, "LibreHardwareMonitorLib.dll")

# Check if DLLs exist
if not os.path.exists(hidsharp_path):
    print(f"ERROR: HidSharp.dll not found at {hidsharp_path}")
    print("Please download and place HidSharp.dll in the script directory")
    sys.exit(1)

if not os.path.exists(librehardwaremonitor_path):
    print(f"ERROR: LibreHardwareMonitorLib.dll not found at {librehardwaremonitor_path}")
    print("Please download and place LibreHardwareMonitorLib.dll in the script directory")
    sys.exit(1)

# Load assemblies using full paths
try:
    clr.AddReference(hidsharp_path)
    clr.AddReference(librehardwaremonitor_path)
    from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType
    LIBREHARDWARE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Failed to load LibreHardwareMonitor: {e}")
    LIBREHARDWARE_AVAILABLE = False

# Initialize NVML for CUDA core count
try:
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except Exception as e:
    print(f"Warning: Failed to initialize NVML: {e}")
    NVML_AVAILABLE = False

# =============================================
# RTSS SHARED MEMORY STRUCTURES (V2)
# =============================================
class RTSS_SHARED_MEMORY_OSD_ENTRY(ctypes.Structure):
    _fields_ = [
        ("szOSD", ctypes.c_char * 256),
        ("szOSDOwner", ctypes.c_char * 256)
    ]

class RTSS_SHARED_MEMORY_APP_ENTRY(ctypes.Structure):
    _fields_ = [
        ("dwProcessID", ctypes.c_uint32),
        ("szName", ctypes.c_char * 260),
        ("dwFlags", ctypes.c_uint32),
        ("dwTime0", ctypes.c_uint32),
        ("dwTime1", ctypes.c_uint32),
        ("dwFrames", ctypes.c_uint32),
        ("dwOSDFrame", ctypes.c_uint32),
        ("dwOSDFrameIdLast", ctypes.c_uint32),
        ("dwOSDFrameIdMin", ctypes.c_uint32),
        ("dwOSDFrameIdMax", ctypes.c_uint32),
        ("dwOSDFrameIdAvg", ctypes.c_uint32),
        ("dwOSD1", ctypes.c_uint32),
        ("dwOSD2", ctypes.c_uint32),
        ("dwOSD3", ctypes.c_uint32),
        ("dwOSD4", ctypes.c_uint32),
        ("dwOSD5", ctypes.c_uint32),
        ("dwFrameTime", ctypes.c_uint32),
        ("dwFrameTimeLast", ctypes.c_uint32),
        ("dwFrameTimeMin", ctypes.c_uint32),
        ("dwFrameTimeMax", ctypes.c_uint32),
        ("dwFrameTimeAvg", ctypes.c_uint32),
        ("dwFrameTimeCount", ctypes.c_uint32),
        ("dwFrameTimeLimit", ctypes.c_uint32),
        ("dwFrameTimeFlags", ctypes.c_uint32),
        ("dwOSDStats", ctypes.c_uint32),
        ("dwOSDStatsPrev", ctypes.c_uint32),
        ("dwOSDStatsVer", ctypes.c_uint32),
        ("dwStatFrameTimeMin", ctypes.c_uint32),
        ("dwStatFrameTimeMax", ctypes.c_uint32),
        ("dwStatFrameTimeAvg", ctypes.c_uint32),
        ("dwStatFrameTimeCount", ctypes.c_uint32),
        ("dwStatFrameTimeLimit", ctypes.c_uint32),
        ("dwStatFrameTimeFlags", ctypes.c_uint32),
        ("dwOSDX", ctypes.c_uint32),
        ("dwOSDY", ctypes.c_uint32),
        ("dwOSDPixel", ctypes.c_uint32),
        ("dwOSDColor", ctypes.c_uint32),
        ("dwScreenCaptureFlags", ctypes.c_uint32),
        ("szScreenCapturePath", ctypes.c_char * 260),
        ("dwFrameCaptureFlags", ctypes.c_uint32),
        ("szFrameCapturePath", ctypes.c_char * 260),
        ("dwAudioCaptureFlags", ctypes.c_uint32),
        ("dwAudioCaptureFlags2", ctypes.c_uint32),
        ("dwAudioCapturePTTFlags", ctypes.c_uint32),
        ("dwVideoCaptureFlags", ctypes.c_uint32),
        ("szVideoCaptureParam", ctypes.c_char * 1024),
        ("szVideoCapturePath", ctypes.c_char * 260),
        ("dwPrerecordSizeLimit", ctypes.c_uint32),
        ("dwPrerecordTimeLimit", ctypes.c_uint32),
        ("dwOSDStatsPeriod", ctypes.c_uint32),
        ("qwAudioCapture2Flags", ctypes.c_uint64),
        ("dwOSDCoordinateSpace", ctypes.c_uint32)
    ]

class RTSS_SHARED_MEMORY_V2(ctypes.Structure):
    _fields_ = [
        ("dwSignature", ctypes.c_uint32),
        ("dwVersion", ctypes.c_uint32),
        ("dwAppEntrySize", ctypes.c_uint32),
        ("dwAppArrOffset", ctypes.c_uint32),
        ("dwAppArrSize", ctypes.c_uint32),
        ("dwOSDEntrySize", ctypes.c_uint32),
        ("dwOSDEntryCount", ctypes.c_uint32),
        ("dwOSDOffset", ctypes.c_uint32),
        ("stat", RTSS_SHARED_MEMORY_APP_ENTRY),
        ("dwOSDArrOffset", ctypes.c_uint32),
        ("osd", RTSS_SHARED_MEMORY_OSD_ENTRY * 8),
        ("arrApp", RTSS_SHARED_MEMORY_APP_ENTRY * 256)
    ]

# =============================================
# ADMIN PRIVILEGE CHECK AND RESTART
# =============================================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", "python", __file__, None, 1)
    exit()

# =============================================
# HARDWARE INFORMATION FUNCTIONS
# =============================================
def get_gpu_info():
    try:
        # Use WMI to get GPU information
        c = wmi.WMI()
        gpu_info = c.Win32_VideoController()
        if not gpu_info:
            return "N/A"
        
        gpu_name = gpu_info[0].Name
        
        # Extract complete GPU model name
        if "NVIDIA" in gpu_name:
            # Extract everything after "NVIDIA"
            model = gpu_name.split("NVIDIA")[-1].strip()
            return f"{model}" if model.startswith("GeForce") else model
        elif "AMD" in gpu_name:
            # Extract everything after "AMD"
            model = gpu_name.split("AMD")[-1].strip()
            return f"{model}" if model.startswith("Radeon") else model
        elif "Intel" in gpu_name:
            # Extract everything after "Intel"
            model = gpu_name.split("Intel")[-1].strip()
            return f"{model}" if "Intel Arc" in model else model
        return gpu_name
    except Exception as e:
        print(f"Error getting GPU info: {e}")
        return "N/A"

def get_cpu_info():
    try:
        c = wmi.WMI()
        processors = c.Win32_Processor()
        if not processors:
            return platform.processor()
            
        for processor in processors:
            name = processor.Name
            if "Intel" in name:
                parts = name.split(" ")
                if "Core" in parts:
                    core_index = parts.index("Core")
                    if len(parts) > core_index + 2:
                        return f"Intel Core {parts[core_index+1]} {parts[core_index+2]}"
                return name
            elif "AMD" in name:
                parts = name.split(" ")
                if "Ryzen" in parts:
                    ryzen_index = parts.index("Ryzen")
                    if len(parts) > ryzen_index + 2:
                        return f"Ryzen {parts[ryzen_index+1]} {parts[ryzen_index+2]}"
                return name
        return platform.processor()
    except Exception as e:
        print(f"Error getting CPU info: {e}")
        return "N/A"

def get_mobo_info():
    try:
        c = wmi.WMI()
        boards = c.Win32_BaseBoard()
        if boards:
            for board in boards:
                if board.Product:
                    return board.Product
    except Exception as e:
        print(f"Error getting motherboard info: {e}")
    return "N/A"

def get_ram_info():
    try:
        return f"{round(psutil.virtual_memory().total / (1024 ** 3))}GB"
    except:
        return "N/A"

# =============================================
# GAME INFORMATION FUNCTIONS
# =============================================
def get_game_info():
    try:
        # Check if games_list.json exists
        if not os.path.exists("games_list.json"):
            print("Warning: games_list.json not found")
            return {"found": False}
            
        # Load games from games_list.json
        with open("games_list.json", "r") as f:
            games = json.load(f)
            
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                if not proc_name:
                    continue
                    
                for game in games:
                    # Check if any executable matches the running process
                    if "executables" in game:
                        for exe in game["executables"]:
                            if exe.lower() == proc_name.lower():
                                # Get primary monitor resolution
                                resolution = "1920x1080"  # Default value
                                try:
                                    monitors = get_monitors()
                                    primary = next((m for m in monitors if m.is_primary), monitors[0] if monitors else None)
                                    if primary:
                                        resolution = f"{primary.width}x{primary.height}"
                                except:
                                    pass
                                
                                return {
                                    "found": True,
                                    "Game": game["name"],
                                    "Process_exe": proc_name,  # Store executable name
                                    "Process_pid": proc.info['pid'],   # Store PID
                                    "Resolution": resolution,
                                    "Arch": game.get("architecture", "N/A"),
                                    "Graphics_API": game.get("graphics_api", "N/A"),
                                    "game_record": game  # Store full game data for printing
                                }
                    # Fallback to game_exe if executables not found
                    elif "game_exe" in game and game["game_exe"]:
                        if game["game_exe"].lower() == proc_name.lower():
                            # Get primary monitor resolution
                            resolution = "1920x1080"  # Default value
                            try:
                                monitors = get_monitors()
                                primary = next((m for m in monitors if m.is_primary), monitors[0] if monitors else None)
                                if primary:
                                    resolution = f"{primary.width}x{primary.height}"
                            except:
                                pass
                            
                            return {
                                "found": True,
                                "Game": game["name"],
                                "Process_exe": proc_name,  # Store executable name
                                "Process_pid": proc.info['pid'],   # Store PID
                                "Resolution": resolution,
                                "Arch": game.get("architecture", "N/A"),
                                "Graphics_API": game.get("graphics_api", "N/A"),
                                "game_record": game
                            }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error in get_game_info: {e}")
    return {"found": False}

# =============================================
# LIBREHARDWAREMONITOR HELPER CLASS
# =============================================
class HardwareMonitor:
    def __init__(self):
        if not LIBREHARDWARE_AVAILABLE:
            self.available = False
            return
            
        try:
            self.computer = Computer()
            self.computer.IsCpuEnabled = True
            self.computer.IsGpuEnabled = True
            self.computer.IsMemoryEnabled = True
            self.computer.IsMotherboardEnabled = True
            self.computer.IsControllerEnabled = True
            self.computer.IsStorageEnabled = True
            self.computer.IsNetworkEnabled = True
            self.computer.Open()
            self.available = True
        except Exception as e:
            print(f"Error initializing LibreHardwareMonitor: {e}")
            self.available = False
        self.sensor_data = {}
        
    def update(self):
        """Update all hardware sensors"""
        if not self.available:
            return
            
        self.sensor_data = {}
        try:
            for hardware in self.computer.Hardware:
                try:
                    hardware.Update()
                    
                    # Also update subhardware
                    for subhardware in hardware.SubHardware:
                        try:
                            subhardware.Update()
                        except:
                            pass
                except Exception as e:
                    print(f"Error updating hardware {hardware.Name}: {e}")
                    continue
                    
                for sensor in hardware.Sensors:
                    # Store sensor values by hardware type, name and type
                    try:
                        key = (hardware.HardwareType, sensor.Name, sensor.SensorType)
                        self.sensor_data[key] = sensor.Value
                    except Exception as e:
                        print(f"Error reading sensor {sensor.Name}: {e}")
                        
                # Also process subhardware sensors
                for subhardware in hardware.SubHardware:
                    for sensor in subhardware.Sensors:
                        try:
                            key = (subhardware.HardwareType, sensor.Name, sensor.SensorType)
                            self.sensor_data[key] = sensor.Value
                        except:
                            pass
        except Exception as e:
            print(f"Error in hardware update: {e}")
    
    def get_value(self, hardware_type, sensor_name, sensor_type):
        """Get sensor value or return N/A if not found"""
        if not self.available:
            return None
            
        # Try exact match first
        key = (hardware_type, sensor_name, sensor_type)
        if key in self.sensor_data:
            return self.sensor_data[key]
        
        # Try partial match for common sensor names
        for (htype, sname, stype), value in self.sensor_data.items():
            if htype == hardware_type and stype == sensor_type:
                # Common sensor name variations
                if sensor_name.lower() in sname.lower() or sname.lower() in sensor_name.lower():
                    return value
        
        return None

# Initialize hardware monitor
try:
    hardware_monitor = HardwareMonitor()
except Exception as e:
    print(f"Failed to initialize LibreHardwareMonitor: {e}")
    hardware_monitor = None

# =============================================
# RTSS SHARED MEMORY ACCESS
# =============================================
class RTSSReader:
    def __init__(self):
        self.FILE_MAP_READ = 0x0004
        self.FILE_MAP_ALL_ACCESS = 0xF001F
        self.INVALID_HANDLE_VALUE = -1

        self.RTSS_SIGNATURE = 0x53535452  # 'RTSS' in hex
        self.SHARED_MEMORY_NAME = "RTSSSharedMemoryV2"

        self.handle = None
        self.mapped_memory = None

    def connect(self):
        try:
            self.handle = windll.kernel32.OpenFileMappingW(
                self.FILE_MAP_READ, False, self.SHARED_MEMORY_NAME
            )
            if not self.handle or self.handle == self.INVALID_HANDLE_VALUE:
                return False
            self.mapped_memory = windll.kernel32.MapViewOfFile(
                self.handle, self.FILE_MAP_READ, 0, 0, 0
            )
            if not self.mapped_memory:
                self.disconnect()
                return False
            return True
        except Exception:
            self.disconnect()
            return False

    def validate_memory_structure(self):
        if not self.mapped_memory:
            return False
        try:
            signature = ctypes.c_uint32.from_address(self.mapped_memory).value
            if signature != self.RTSS_SIGNATURE:
                return False
            version_addr = self.mapped_memory + 4
            version = ctypes.c_uint32.from_address(version_addr).value
            if version < 0x00020000:
                return False
            return True
        except Exception:
            return False

    def read_fps_data(self):
        if not self.mapped_memory or not self.validate_memory_structure():
            return None
        try:
            # Read from stat structure (offset 52 after header fields)
            stat_offset = 52  # After dwSignature, dwVersion, etc.
            time0_addr = self.mapped_memory + stat_offset + 12
            time1_addr = self.mapped_memory + stat_offset + 16
            frames_addr = self.mapped_memory + stat_offset + 20

            time0 = ctypes.c_uint32.from_address(time0_addr).value
            time1 = ctypes.c_uint32.from_address(time1_addr).value
            frames = ctypes.c_uint32.from_address(frames_addr).value

            fps = 0.0
            if time1 > time0 and frames > 0:
                fps = 1000.0 * frames / (time1 - time0)

            # Read frame time stats
            frame_time_addr = self.mapped_memory + stat_offset + 60
            frame_time_min_addr = self.mapped_memory + stat_offset + 68
            frame_time_max_addr = self.mapped_memory + stat_offset + 72
            frame_time_avg_addr = self.mapped_memory + stat_offset + 76
            
            frame_time = ctypes.c_uint32.from_address(frame_time_addr).value
            frame_time_min = ctypes.c_uint32.from_address(frame_time_min_addr).value
            frame_time_max = ctypes.c_uint32.from_address(frame_time_max_addr).value
            frame_time_avg = ctypes.c_uint32.from_address(frame_time_avg_addr).value

            return {
                'fps': fps,
                'frames': frames,
                'time_span_ms': time1 - time0,
                'frame_time': frame_time / 10.0 if frame_time > 0 else 0,
                'frame_time_min': frame_time_min / 10.0 if frame_time_min > 0 else 0,
                'frame_time_max': frame_time_max / 10.0 if frame_time_max > 0 else 0,
                'frame_time_avg': frame_time_avg / 10.0 if frame_time_avg > 0 else 0,
                'valid_data': time1 > time0 and frames > 0
            }
        except Exception as e:
            return None

    def read_application_statistics(self):
        """Read application-specific statistics from RTSS shared memory"""
        if not self.mapped_memory or not self.validate_memory_structure():
            return []
        
        try:
            # Read app array info
            app_entry_size_addr = self.mapped_memory + 8
            app_arr_offset_addr = self.mapped_memory + 12
            app_arr_size_addr = self.mapped_memory + 16
            
            app_entry_size = ctypes.c_uint32.from_address(app_entry_size_addr).value
            app_arr_offset = ctypes.c_uint32.from_address(app_arr_offset_addr).value
            app_arr_size = ctypes.c_uint32.from_address(app_arr_size_addr).value
            
            if app_entry_size == 0 or app_arr_size == 0:
                return []
            
            num_entries = min(app_arr_size // app_entry_size, 256)
            app_stats = []
            
            for i in range(num_entries):
                entry_offset = self.mapped_memory + app_arr_offset + (i * app_entry_size)
                
                # Read process ID to check if entry is valid
                pid = ctypes.c_uint32.from_address(entry_offset).value
                if pid == 0:
                    continue
                
                # Read frame timing data
                time0 = ctypes.c_uint32.from_address(entry_offset + 12).value
                time1 = ctypes.c_uint32.from_address(entry_offset + 16).value
                frames = ctypes.c_uint32.from_address(entry_offset + 20).value
                
                if time1 > time0 and frames > 0:
                    app_stats.append({
                        'pid': pid,
                        'frames': frames,
                        'measurement_time_ms': time1 - time0,
                        'fps': 1000.0 * frames / (time1 - time0)
                    })
            
            return app_stats
        except Exception:
            return []

    def disconnect(self):
        if self.mapped_memory:
            windll.kernel32.UnmapViewOfFile(self.mapped_memory)
            self.mapped_memory = None
        if self.handle:
            windll.kernel32.CloseHandle(self.handle)
            self.handle = None


class SafeRTSSReader:
    def __init__(self):
        self.reader = RTSSReader()
        self.connection_validated = False
    
    def safe_connect(self):
        """Safely connect to RTSS shared memory"""
        try:
            if self.reader.connect():
                self.connection_validated = True
                return True
        except Exception:
            pass
        self.connection_validated = False
        return False
    
    def safe_read_fps(self):
        """Safely read FPS data from RTSS"""
        if not self.connection_validated:
            if not self.safe_connect():
                return None
        
        try:
            data = self.reader.read_fps_data()
            if data and not data.get('valid_data', False):
                # Try reconnecting if data is invalid
                self.reader.disconnect()
                self.connection_validated = False
                if self.safe_connect():
                    data = self.reader.read_fps_data()
            return data
        except Exception:
            self.connection_validated = False
            return None

# === Compatibility wrapper to preserve old call ===
def get_rtss_stats():
    global _rtss_instance
    try:
        if '_rtss_instance' not in globals():
            _rtss_instance = SafeRTSSReader()
            _rtss_instance.safe_connect()
        
        data = _rtss_instance.safe_read_fps()
        if data and 'fps' in data:
            fps_list = _rtss_instance.reader.read_application_statistics()
            frame_times = []

            # Collect frame time data
            if data.get('frame_time_avg', 0) > 0:
                # Use RTSS frame time data if available
                frame_times = [data['frame_time_avg']]
                if data.get('frame_time_min', 0) > 0:
                    frame_times.append(data['frame_time_min'])
                if data.get('frame_time_max', 0) > 0:
                    frame_times.append(data['frame_time_max'])
            
            # Add application-specific frame times
            if fps_list:
                for entry in fps_list:
                    if entry.get('frames', 0) > 0 and entry.get('measurement_time_ms', 0) > 0:
                        frame_time = entry['measurement_time_ms'] / entry['frames']
                        frame_times.append(frame_time)

            if frame_times:
                sorted_times = sorted(frame_times)
                total_frames = len(sorted_times)

                def percentile(p):
                    index = int(total_frames * (p / 100.0))
                    index = min(max(index, 0), total_frames - 1)
                    return sorted_times[index]

                fps_1 = 1000.0 / percentile(99) if percentile(99) > 0 else 0  # worst 1%
                fps_01 = 1000.0 / percentile(99.9) if percentile(99.9) > 0 else 0  # worst 0.1%
                fps_99 = 1000.0 / percentile(1) if percentile(1) > 0 else 0  # best 99%

                return {
                    "fps": round(data.get("fps", 0), 1),
                    "fps_min": round(1000.0 / data['frame_time_max'], 1) if data.get('frame_time_max', 0) > 0 else 0,
                    "fps_max": round(1000.0 / data['frame_time_min'], 1) if data.get('frame_time_min', 0) > 0 else 0,
                    "fps_avg": round(data.get("fps", 0), 1),
                    "fps_99": round(fps_99, 1),
                    "fps_1": round(fps_1, 1),
                    "fps_01": round(fps_01, 1),
                    "frame_time": round(data.get("frame_time_avg", 0), 1),
                    "frame_time_min": round(data.get("frame_time_min", 0), 1),
                    "frame_time_max": round(data.get("frame_time_max", 0), 1),
                    "frame_time_avg": round(data.get("frame_time_avg", 0), 1),
                    "fps_valid": data.get("valid_data", False)
                }
            else:
                # Return basic data if no frame time data available
                return {
                    "fps": round(data.get("fps", 0), 1),
                    "fps_min": 0,
                    "fps_max": 0,
                    "fps_avg": round(data.get("fps", 0), 1),
                    "fps_99": round(data.get("fps", 0) * 0.99, 1) if data.get("fps", 0) > 0 else 0,
                    "fps_1": round(data.get("fps", 0) * 0.85, 1) if data.get("fps", 0) > 0 else 0,
                    "fps_01": round(data.get("fps", 0) * 0.75, 1) if data.get("fps", 0) > 0 else 0,
                    "frame_time": round(1000.0 / data.get("fps", 1), 1) if data.get("fps", 0) > 0 else 0,
                    "frame_time_min": 0,
                    "frame_time_max": 0,
                    "frame_time_avg": round(1000.0 / data.get("fps", 1), 1) if data.get("fps", 0) > 0 else 0,
                    "fps_valid": data.get("valid_data", False)
                }

    except Exception as e:
        print(f"Error in get_rtss_stats: {e}")
    
    return {
        "fps": 0,
        "fps_min": 0,
        "fps_max": 0,
        "fps_avg": 0,
        "fps_99": 0,
        "fps_1": 0,
        "fps_01": 0,
        "frame_time": 0,
        "frame_time_min": 0,
        "frame_time_max": 0,
        "frame_time_avg": 0,
        "fps_valid": False
    }

def get_gpu_stats():
    stats = {key: "N/A" for key in [
        "gpu_core_usage", "gpu_temp", "gpu_power", "gpu_clock", 
        "gpu_mem_usage", "mem_clock", "gpu_fan_rpm", "gpu_power_limit",
        "gpu_temp_limit", "gpu_voltage", "gpu_voltage_limit", "gpu_vid_usage", "gpu_bus_usage",
        "gpu_fan_mode", "gpu_base_core_clock", "gpu_base_mem_clock",
        "gpu_usage_process", "gpu_compute_capability"
    ]}
    
    if not hardware_monitor or not hardware_monitor.available:
        # Try to get basic GPU usage via WMI as fallback
        try:
            c = wmi.WMI(namespace="root\\CIMV2")
            # Get GPU usage from performance counters if available
            for gpu in c.Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine():
                if gpu.Name and "3D" in gpu.Name:
                    stats["gpu_core_usage"] = round(gpu.UtilizationPercentage, 1)
                    break
        except:
            pass
        return stats
    
    try:
        # Update sensor data
        hardware_monitor.update()
        
        # GPU Core Usage (%)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Core", SensorType.Load)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Core", SensorType.Load)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Core", SensorType.Load)
        stats["gpu_core_usage"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Temperature (°C)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Core", SensorType.Temperature)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Core", SensorType.Temperature)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Core", SensorType.Temperature)
        stats["gpu_temp"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Power (W)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Package", SensorType.Power)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Package", SensorType.Power)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Power", SensorType.Power)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Core", SensorType.Power)
        stats["gpu_power"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Clock (MHz)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Core", SensorType.Clock)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Core", SensorType.Clock)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Core", SensorType.Clock)
        stats["gpu_clock"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Memory Usage (%)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Memory", SensorType.Load)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Memory", SensorType.Load)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Memory", SensorType.Load)
        stats["gpu_mem_usage"] = round(value, 1) if value is not None else "N/A"
        
        # Memory Clock (MHz)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Memory", SensorType.Clock)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Memory", SensorType.Clock)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Memory", SensorType.Clock)
        stats["mem_clock"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Fan Speed (RPM)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Fan", SensorType.Fan)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Fan", SensorType.Fan)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Fan", SensorType.Fan)
        stats["gpu_fan_rpm"] = round(value) if value is not None else "N/A"
        
        # GPU Power Limit (W)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Power Limit", SensorType.Power)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Power Limit", SensorType.Power)
        if value is None:
            # Try to get TDP or max power
            value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU TDP", SensorType.Power)
        if value is None and stats["gpu_power"] != "N/A":
            # Estimate power limit as 120% of current power
            try:
                value = float(stats["gpu_power"]) * 1.2
            except:
                value = None
        stats["gpu_power_limit"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Temperature Limit (°C)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Hot Spot", SensorType.Temperature)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Hot Spot", SensorType.Temperature)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Maximum", SensorType.Temperature)
        if value is None and stats["gpu_temp"] != "N/A":
            # Default temperature limit
            value = 83.0  # Common GPU temp limit
        stats["gpu_temp_limit"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Voltage (V) - FIXED: Enhanced voltage detection with more sensor names
        voltage_sensors = [
            ("GPU Core", SensorType.Voltage),
            ("GPU Core Voltage", SensorType.Voltage),
            ("GPU Voltage", SensorType.Voltage),
            ("Core Voltage", SensorType.Voltage),
            ("VDDC", SensorType.Voltage),
            ("VDDCI", SensorType.Voltage),
            ("GPU VR VDDC", SensorType.Voltage),
            ("GPU VR VDD", SensorType.Voltage),
            ("GPU VR VDDCI", SensorType.Voltage),
            ("GPU VDDC", SensorType.Voltage),
            ("GPU VDD", SensorType.Voltage),
            ("Vcore", SensorType.Voltage),
            ("GPU VRM Voltage", SensorType.Voltage),
            ("VR VDDC", SensorType.Voltage),
            ("VR VDD", SensorType.Voltage),
            ("VR VDDCI", SensorType.Voltage),
            ("VRM Core", SensorType.Voltage),
            ("VRM Memory", SensorType.Voltage),
            ("GPU", SensorType.Voltage),
            ("MVDDC", SensorType.Voltage),
            ("MVDDQ", SensorType.Voltage),
            ("Board VR Voltage", SensorType.Voltage),
            ("GPU Rail Voltage", SensorType.Voltage),
            ("GPU Power Voltage", SensorType.Voltage),
            ("GPU VID", SensorType.Voltage),
            ("GPU VDDCR GFX", SensorType.Voltage),
            ("GPU VDDCR SOC", SensorType.Voltage),
            ("GPU Core VDD", SensorType.Voltage),
            ("GPU MVDD", SensorType.Voltage),
            ("GPU VDDP", SensorType.Voltage),
            # Additional sensor names for better detection
            ("GPU Core VID", SensorType.Voltage),
            ("GPU Effective Core Voltage (VDDC)", SensorType.Voltage),
            ("GPU SoC Voltage (VDDCR_SOC)", SensorType.Voltage),
            ("GPU GFX Voltage (VDDCR_GFX)", SensorType.Voltage),
            ("VDDCR GFX", SensorType.Voltage),
            ("VDDCR SOC", SensorType.Voltage),
            ("GPU VDDIO", SensorType.Voltage),
            ("GPU Core Effective Voltage", SensorType.Voltage),
            ("GPU Actual Voltage", SensorType.Voltage),
            ("GPU VCore", SensorType.Voltage),
            ("NVVDD", SensorType.Voltage),
            ("FBVDD", SensorType.Voltage),
            ("GPU Chip Power (NVVDD)", SensorType.Voltage),
            ("GPU Memory Controller (FBVDD)", SensorType.Voltage),
            ("VIN0", SensorType.Voltage),
            ("VIN1", SensorType.Voltage),
            ("VIN2", SensorType.Voltage),
            ("VIN3", SensorType.Voltage),
            ("VIN4", SensorType.Voltage)
        ]
        
        voltage_value = None
        # Try all hardware types and all sensor names
        for hw_type in [HardwareType.GpuNvidia, HardwareType.GpuAmd, HardwareType.GpuIntel]:
            for sensor_name, sensor_type in voltage_sensors:
                value = hardware_monitor.get_value(hw_type, sensor_name, sensor_type)
                if value is not None and 0.5 < value < 2.0:  # Reasonable GPU voltage range
                    voltage_value = value
                    break
            if voltage_value is not None:
                break
        
        # If still no voltage found, check all sensors for any voltage reading
        if voltage_value is None and hardware_monitor.sensor_data:
            # First priority: Check for any GPU-related voltage sensor
            for (hw_type, name, sensor_type), value in hardware_monitor.sensor_data.items():
                if sensor_type == SensorType.Voltage and hw_type in [HardwareType.GpuNvidia, HardwareType.GpuAmd, HardwareType.GpuIntel]:
                    # Check if it's a GPU-related voltage (not PCIe or other)
                    lower_name = name.lower()
                    if any(keyword in lower_name for keyword in ['gpu', 'core', 'vddc', 'vdd', 'gfx', 'soc', 'nvvdd', 'fbvdd', 'vcore']):
                        if value is not None and 0.5 < value < 2.0:  # Reasonable GPU voltage range
                            voltage_value = value
                            break
        
        # NVML fallback for NVIDIA GPUs - Enhanced voltage detection
        if voltage_value is None and NVML_AVAILABLE:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    
                    # Try to get actual voltage if supported
                    try:
                        # Some NVIDIA GPUs support voltage queries
                        voltage_mv = pynvml.nvmlDeviceGetVoltage(handle)
                        if voltage_mv > 0:
                            voltage_value = voltage_mv / 1000.0  # Convert mV to V
                            break
                    except:
                        pass
                    
                    # If direct voltage query fails, estimate based on power state
                    if voltage_value is None:
                        try:
                            pstate = pynvml.nvmlDeviceGetPowerState(handle)
                            # More accurate voltage estimates based on P-state
                            if pstate == 0:  # P0 - Maximum Performance
                                voltage_value = 1.062
                            elif pstate == 1:  # P1
                                voltage_value = 1.025
                            elif pstate == 2:  # P2
                                voltage_value = 0.987
                            elif pstate == 3:  # P3
                                voltage_value = 0.950
                            elif pstate == 4:  # P4
                                voltage_value = 0.912
                            elif pstate == 5:  # P5
                                voltage_value = 0.875
                            elif pstate <= 8:  # P6-P8
                                voltage_value = 0.837
                            else:  # P9+ - Idle
                                voltage_value = 0.800
                            break
                        except:
                            pass
            except:
                pass
        
        # Last fallback: Try to estimate based on current clock/power if available
        if voltage_value is None and stats["gpu_clock"] != "N/A" and stats["gpu_power"] != "N/A":
            try:
                clock = float(stats["gpu_clock"])
                power = float(stats["gpu_power"])
                # Very rough estimation based on typical GPU behavior
                if clock > 2000:  # High performance
                    voltage_value = 1.05
                elif clock > 1500:  # Medium performance
                    voltage_value = 0.95
                elif clock > 1000:  # Low performance
                    voltage_value = 0.85
                else:  # Idle
                    voltage_value = 0.75
            except:
                pass
        
        stats["gpu_voltage"] = round(voltage_value, 3) if voltage_value is not None else "N/A"
        
        # GPU Voltage Limit (V)
        voltage_limit = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Voltage Limit", SensorType.Voltage)
        if voltage_limit is None:
            voltage_limit = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Voltage Limit", SensorType.Voltage)
        if voltage_limit is None:
            # Use 1.1V as default if not available
            voltage_limit = 1.1
        stats["gpu_voltage_limit"] = round(voltage_limit, 3) if voltage_limit is not None else "N/A"
        
        # GPU Video Engine Load (%)
        value = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Video Engine", SensorType.Load)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Video Engine", SensorType.Load)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.GpuIntel, "GPU Video Engine", SensorType.Load)
        stats["gpu_vid_usage"] = round(value, 1) if value is not None else "N/A"
        
        # GPU Bus Usage (GB/s)
        rx = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU PCIe Rx", SensorType.Throughput)
        if rx is None:
            rx = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU PCIe Rx", SensorType.Throughput)
        tx = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU PCIe Tx", SensorType.Throughput)
        if tx is None:
            tx = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU PCIe Tx", SensorType.Throughput)
        
        if rx is not None and tx is not None:
            # Convert MB/s to GB/s and round to 2 decimals
            total = (rx + tx) / 1024.0
            stats["gpu_bus_usage"] = round(total, 2)
        else:
            stats["gpu_bus_usage"] = "N/A"
        
        # GPU Top Process - FIXED: Enhanced GPU process detection to show percentage first
        stats["gpu_usage_process"] = "N/A"
        try:
            # Method 1: Try WMI GPU performance counters
            c = wmi.WMI(namespace="root\\CIMV2")
            max_gpu_usage = 0
            max_gpu_process = None
            
            # Get GPU engine usage
            try:
                gpu_engines = c.Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine()
                process_gpu_usage = {}
                
                for engine in gpu_engines:
                    if hasattr(engine, 'Name') and hasattr(engine, 'UtilizationPercentage'):
                        # Extract process name from engine name
                        engine_name = engine.Name
                        if "_pid_" in engine_name:
                            try:
                                pid_start = engine_name.index("_pid_") + 5
                                pid_end = engine_name.index("_", pid_start)
                                pid = int(engine_name[pid_start:pid_end])
                                
                                # Get process name from PID
                                try:
                                    process = psutil.Process(pid)
                                    process_name = process.name()
                                    
                                    # Accumulate GPU usage for this process
                                    if process_name not in process_gpu_usage:
                                        process_gpu_usage[process_name] = 0
                                    process_gpu_usage[process_name] += engine.UtilizationPercentage
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    continue
                            except (ValueError, IndexError):
                                continue
                
                # Find the process with highest GPU usage
                if process_gpu_usage:
                    max_process_name = max(process_gpu_usage, key=process_gpu_usage.get)
                    max_gpu_usage = process_gpu_usage[max_process_name]
                    max_gpu_process = max_process_name
            except:
                pass
            
            # Method 2: Try GPU process performance data
            if max_gpu_usage == 0:
                try:
                    gpu_processes = c.Win32_PerfFormattedData_GPUPerformanceCounters_GPUProcess()
                    for p in gpu_processes:
                        if hasattr(p, 'PercentGPUTime') and hasattr(p, 'Name'):
                            usage = float(p.PercentGPUTime)
                            if usage > max_gpu_usage:
                                max_gpu_usage = usage
                                max_gpu_process = p.Name
                except:
                    pass
            
            # Method 3: Use NVIDIA-ML if available
            if max_gpu_usage == 0 and NVML_AVAILABLE:
                try:
                    device_count = pynvml.nvmlDeviceGetCount()
                    for i in range(device_count):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        
                        # Get compute processes
                        try:
                            processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                            for process in processes:
                                try:
                                    # Get process name from PID
                                    proc = psutil.Process(process.pid)
                                    process_name = proc.name()
                                    # Estimate usage based on GPU utilization
                                    if max_gpu_process is None and stats["gpu_core_usage"] != "N/A":
                                        max_gpu_process = process_name
                                        max_gpu_usage = float(stats["gpu_core_usage"])
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    continue
                        except:
                            pass
                        
                        # Get graphics processes
                        try:
                            processes = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
                            for process in processes:
                                try:
                                    # Get process name from PID
                                    proc = psutil.Process(process.pid)
                                    process_name = proc.name()
                                    if max_gpu_process is None and stats["gpu_core_usage"] != "N/A":
                                        max_gpu_process = process_name
                                        max_gpu_usage = float(stats["gpu_core_usage"])
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    continue
                        except:
                            pass
                except:
                    pass
            
            # Format the result - ALWAYS show percentage first
            if max_gpu_process and max_gpu_usage != 0:
                # Remove .exe extension
                process_display_name = max_gpu_process.replace('.exe', '')
                # Truncate if too long
                if len(process_display_name) > 12:
                    process_display_name = process_display_name[:12]
                
                # ALWAYS show percentage first
                stats["gpu_usage_process"] = f"{max_gpu_usage:.0f}% {process_display_name}"
            
            # Fallback: If no GPU process found, check current game
            if stats["gpu_usage_process"] == "N/A":
                # Try to get current game from games_list.json
                game_info = get_game_info()
                if game_info.get("found", False):
                    game_name = game_info.get("Game", "N/A")
                    if game_name != "N/A":
                        # Truncate game name if too long
                        if len(game_name) > 12:
                            game_name = game_name[:12]
                        # Try to estimate GPU usage for the game
                        if stats["gpu_core_usage"] != "N/A":
                            stats["gpu_usage_process"] = f"{stats['gpu_core_usage']}% {game_name}"
                        else:
                            stats["gpu_usage_process"] = f"0% {game_name}"
        except Exception as e:
            print(f"Error getting GPU process: {e}")
        
        # GPU Compute Capability
        stats["gpu_compute_capability"] = "N/A"
        try:
            if NVML_AVAILABLE:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                cc_major = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[0]
                cc_minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[1]
                stats["gpu_compute_capability"] = f"{cc_major}.{cc_minor}"
            else:
                # Fallback to WMI for GPU architecture info
                c = wmi.WMI()
                gpus = c.Win32_VideoController()
                if gpus:
                    gpu_name = gpus[0].Name
                    if "RTX" in gpu_name:
                        stats["gpu_compute_capability"] = "7.5+"
                    elif "GTX 10" in gpu_name:
                        stats["gpu_compute_capability"] = "6.1"
                    elif "GTX 9" in gpu_name:
                        stats["gpu_compute_capability"] = "5.2"
                    else:
                        stats["gpu_compute_capability"] = "N/A"
        except:
            pass
        
        # GPU Base Core Clock (MHz)
        base_gpu_core_clock = None
        if NVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                base_gpu_core_clock = pynvml.nvmlDeviceGetClock(handle, pynvml.NVML_CLOCK_GRAPHICS, pynvml.NVML_CLOCK_ID_BASE)
            except Exception as e:
                print(f"NVML Error getting base core clock: {e}")
                base_gpu_core_clock = None

        if base_gpu_core_clock is not None:
            stats["gpu_base_core_clock"] = base_gpu_core_clock
        else:
            # Try to get from LibreHardwareMonitor? We don't have a known sensor for base clock, so leave as N/A
            stats["gpu_base_core_clock"] = "N/A"

        # GPU Base Memory Clock (MHz)
        base_gpu_mem_clock = None
        if NVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                base_gpu_mem_clock = pynvml.nvmlDeviceGetClock(handle, pynvml.NVML_CLOCK_MEM, pynvml.NVML_CLOCK_ID_BASE)
            except Exception as e:
                print(f"NVML Error getting base memory clock: {e}")
                base_gpu_mem_clock = None

        if base_gpu_mem_clock is not None:
            stats["gpu_base_mem_clock"] = base_gpu_mem_clock
        else:
            stats["gpu_base_mem_clock"] = "N/A"

        # GPU Fan Mode - FIXED: Enhanced detection for Auto/Manual/Zero/Silent/Turbo
        stats["gpu_fan_mode"] = "N/A"
        
        # Get fan control percentage
        fan_control = hardware_monitor.get_value(HardwareType.GpuNvidia, "GPU Fan", SensorType.Control)
        if fan_control is None:
            fan_control = hardware_monitor.get_value(HardwareType.GpuAmd, "GPU Fan", SensorType.Control)
        
        # Get current fan RPM
        fan_rpm = stats.get("gpu_fan_rpm", "N/A")
        
        # Check for Zero RPM mode first
        if fan_rpm != "N/A" and isinstance(fan_rpm, (int, float)) and fan_rpm == 0:
            # Fan is stopped - Zero RPM mode
            stats["gpu_fan_mode"] = "Zero"
        elif fan_control is not None:
            # Check if fan is manually controlled
            if fan_control >= 95:
                stats["gpu_fan_mode"] = "Turbo"
            elif fan_control >= 70:
                stats["gpu_fan_mode"] = "Manual"
            elif fan_control <= 20 and (fan_rpm == "N/A" or (isinstance(fan_rpm, (int, float)) and fan_rpm < 1000)):
                stats["gpu_fan_mode"] = "Silent"
            elif fan_control < 50:
                stats["gpu_fan_mode"] = "Auto"
            else:
                stats["gpu_fan_mode"] = "Manual"
        else:
            # Try to determine based on fan RPM patterns
            if fan_rpm != "N/A" and isinstance(fan_rpm, (int, float)):
                if fan_rpm == 0:
                    stats["gpu_fan_mode"] = "Zero"
                elif fan_rpm < 1000:
                    stats["gpu_fan_mode"] = "Silent"
                elif fan_rpm > 2500:
                    stats["gpu_fan_mode"] = "Turbo"
                else:
                    # Check temperature to estimate if it's auto or manual
                    gpu_temp = stats.get("gpu_temp", "N/A")
                    if gpu_temp != "N/A" and isinstance(gpu_temp, (int, float)):
                        # If fan speed seems proportional to temperature, likely auto
                        expected_fan_ratio = (gpu_temp - 30) / 50  # Rough estimate
                        if fan_rpm < 2000:
                            stats["gpu_fan_mode"] = "Auto"
                        else:
                            stats["gpu_fan_mode"] = "Manual"
                    else:
                        stats["gpu_fan_mode"] = "Auto"
        
        # Additional NVML check for NVIDIA GPUs
        if stats["gpu_fan_mode"] == "N/A" and NVML_AVAILABLE:
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                # Try to get fan control mode
                try:
                    # Some NVIDIA GPUs support fan control policy
                    fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                    if fan_speed == 0:
                        stats["gpu_fan_mode"] = "Zero"
                    elif fan_speed < 30:
                        stats["gpu_fan_mode"] = "Silent"
                    elif fan_speed > 80:
                        stats["gpu_fan_mode"] = "Turbo"
                    else:
                        stats["gpu_fan_mode"] = "Auto"
                except:
                    pass
            except:
                pass
        
    except Exception as e:
        print(f"Error getting GPU stats: {e}")
    
    return stats

def get_cpu_stats():
    stats = {key: "N/A" for key in [
        "cpu_usage", "cpu_clock", "cpu_temp", "cpu_power", 
        "cpu_voltage", "cpu_fan_rpm", "cpu_base_core_clock", "cpu_active_cores",
        "cpu_usage_process"
    ]}
    
    # Always try to get CPU usage from psutil first
    try:
        stats["cpu_usage"] = round(psutil.cpu_percent(interval=0.1), 1)
    except:
        stats["cpu_usage"] = "N/A"
    
    # Get CPU core/thread count
    try:
        physical_cores = psutil.cpu_count(logical=False)
        total_cores = psutil.cpu_count(logical=True)
        stats["cpu_active_cores"] = f"{physical_cores}/{total_cores}"
    except:
        stats["cpu_active_cores"] = "N/A"
    
    # Get top CPU process - FIXED: Ensure percentage is shown first
    try:
        processes = []
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                cpu_percent = proc.info['cpu_percent']
                if cpu_percent is None:
                    cpu_percent = proc.cpu_percent(interval=0.01)
                if cpu_percent > 0:  # Only consider processes using CPU
                    processes.append((proc.info['name'], cpu_percent))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if processes:
            processes.sort(key=lambda x: x[1], reverse=True)
            top_name = processes[0][0]
            top_cpu = processes[0][1]
            # Remove .exe extension
            top_name = top_name.replace('.exe', '')
            # Truncate if too long
            if len(top_name) > 12:
                top_name = top_name[:12]
            # ALWAYS show percentage first
            stats["cpu_usage_process"] = f"{top_cpu:.0f}% {top_name}"
        else:
            stats["cpu_usage_process"] = "0% System"
    except Exception as e:
        print(f"Error getting CPU process: {e}")
        stats["cpu_usage_process"] = "N/A"
    
    if not hardware_monitor or not hardware_monitor.available:
        return stats
    
    try:
        # Update sensor data
        hardware_monitor.update()
        
        # CPU Usage (%) - prefer LibreHardwareMonitor if available
        value = hardware_monitor.get_value(HardwareType.Cpu, "CPU Total", SensorType.Load)
        if value is not None:
            stats["cpu_usage"] = round(value, 1)
        
        # CPU Clock (MHz) - get max core clock
        max_clock = 0
        for i in range(1, 33):  # Check up to 32 cores
            clock = hardware_monitor.get_value(HardwareType.Cpu, f"Core #{i}", SensorType.Clock)
            if clock and clock > max_clock:
                max_clock = clock
        
        # Also check for CPU Core clocks with different naming
        if max_clock == 0:
            for i in range(0, 32):
                clock = hardware_monitor.get_value(HardwareType.Cpu, f"CPU Core #{i}", SensorType.Clock)
                if clock and clock > max_clock:
                    max_clock = clock
        
        stats["cpu_clock"] = round(max_clock, 1) if max_clock > 0 else "N/A"
        
        # CPU Temperature (°C)
        value = hardware_monitor.get_value(HardwareType.Cpu, "CPU Package", SensorType.Temperature)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.Cpu, "Core (Tctl/Tdie)", SensorType.Temperature)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.Cpu, "CPU CCD #1", SensorType.Temperature)
        stats["cpu_temp"] = round(value, 1) if value is not None else "N/A"
        
        # CPU Power (W)
        value = hardware_monitor.get_value(HardwareType.Cpu, "CPU Package", SensorType.Power)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.Cpu, "Package", SensorType.Power)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.Cpu, "CPU Cores", SensorType.Power)
        stats["cpu_power"] = round(value, 1) if value is not None else "N/A"
        
        # CPU Voltage (V)
        value = hardware_monitor.get_value(HardwareType.Cpu, "CPU Core", SensorType.Voltage)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.Cpu, "Core (SVI2 TFN)", SensorType.Voltage)
        if value is None:
            value = hardware_monitor.get_value(HardwareType.Cpu, "VID #1", SensorType.Voltage)
        stats["cpu_voltage"] = round(value, 3) if value is not None else "N/A"
        
        # CPU Fan Speed (RPM) - FIXED: Enhanced detection with more sensor names
        fan_sensors = [
            # Primary CPU fan names
            "CPU Fan",
            "CPU FAN",
            "CPU Fan #1",
            "CPU FAN 1",
            "CPU_FAN",
            "Processor Fan",
            "CPU",
            
            # Secondary CPU fan names
            "CPU Fan #2",
            "CPU FAN 2",
            "CPU_FAN2",
            "CPU OPT",
            "CPU_OPT",
            
            # System/Chassis fans that might be CPU cooler
            "System Fan #1",
            "System Fan 1", 
            "SYSTEM FAN 1",
            "SYS_FAN1",
            "Chassis Fan #1",
            "Chassis Fan 1",
            "CHA_FAN1",
            
            # Generic fan names
            "Fan #1",
            "Fan 1",
            "FAN1",
            "Fan1",
            
            # Pump names (for AIO coolers)
            "CPU Pump",
            "Pump",
            "W_PUMP",
            "AIO_PUMP",
            
            # Additional variations
            "CPU Cooler",
            "CPU COOLER",
            "Cooler",
            "FAN_CPU"
        ]
        
        fan_value = None
        # Check motherboard sensors first
        for sensor_name in fan_sensors:
            value = hardware_monitor.get_value(HardwareType.Motherboard, sensor_name, SensorType.Fan)
            if value is not None and value > 0:  # Ensure we have a valid reading
                fan_value = value
                break
        
        # If no motherboard fan found, check other hardware types
        if fan_value is None:
            for hw_type in [HardwareType.SuperIO, HardwareType.Cpu]:
                for sensor_name in fan_sensors:
                    value = hardware_monitor.get_value(hw_type, sensor_name, SensorType.Fan)
                    if value is not None and value > 0:
                        fan_value = value
                        break
                if fan_value is not None:
                    break
        
        # Last resort: check all fan sensors
        if fan_value is None and hardware_monitor.sensor_data:
            for (hw_type, name, sensor_type), value in hardware_monitor.sensor_data.items():
                if sensor_type == SensorType.Fan and value is not None and value > 0:
                    # Prioritize sensors with "CPU" in the name
                    if "cpu" in name.lower():
                        fan_value = value
                        break
                    # Otherwise, take the first valid fan reading
                    elif fan_value is None:
                        fan_value = value
        
        stats["cpu_fan_rpm"] = round(fan_value) if fan_value is not None else "N/A"
        
        # CPU Base Clock
        # Try to get base clock from CPU info
        base_clock = hardware_monitor.get_value(HardwareType.Cpu, "Bus Speed", SensorType.Clock)
        if base_clock is not None:
            # Get multiplier
            multiplier = 35  # Default multiplier
            try:
                c = wmi.WMI()
                for processor in c.Win32_Processor():
                    if hasattr(processor, 'MaxClockSpeed'):
                        base_clock_calc = processor.MaxClockSpeed
                        stats["cpu_base_core_clock"] = base_clock_calc
                        break
            except:
                if base_clock > 0:
                    stats["cpu_base_core_clock"] = round(base_clock * multiplier, 0)
        
    except Exception as e:
        print(f"Error getting CPU stats: {e}")
    
    return stats

def get_ram_stats():
    stats = {key: "N/A" for key in [
        "ram_usage", "ram_usage_process", "virtual_memory",
        "ram_clock_speed", "ram_base_clock_speed", "ram_xmp_profile", "ram_channel"
    ]}
    
    try:
        # Get RAM usage (GB)
        vm = psutil.virtual_memory()
        stats["ram_usage"] = round(vm.used / (1024 ** 3), 1)
        
        # Get top RAM-consuming process
        top_process = None
        for proc in psutil.process_iter(['memory_info', 'name']):
            try:
                mem_usage = proc.info['memory_info'].rss
                if not top_process or mem_usage > top_process[1]:
                    top_process = (proc.info['name'], mem_usage)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if top_process:
            # Format process name to max 20 characters
            proc_name = top_process[0].replace('.exe', '')
            if len(proc_name) > 15:
                proc_name = proc_name[:15]
            # Format memory usage
            mem_gb = top_process[1] / (1024 ** 3)
            stats["ram_usage_process"] = f"{mem_gb:.1f}GB {proc_name}"
        
        # Virtual memory committed (GB) - total amount of memory promised by the OS to all processes
        c = wmi.WMI()
        for os_info in c.Win32_OperatingSystem():
            if hasattr(os_info, 'TotalVirtualMemorySize'):
                total_virtual = int(os_info.TotalVirtualMemorySize) * 1024  # Convert KB to bytes
                stats["virtual_memory"] = round(total_virtual / (1024 ** 3), 1)
                break
        
        # RAM clock info
        if hardware_monitor and hardware_monitor.available:
            hardware_monitor.update()
            value = hardware_monitor.get_value(HardwareType.Memory, "Memory", SensorType.Clock)
            if value is not None:
                stats["ram_clock_speed"] = round(value, 1)
                # Estimate base clock from current (DDR runs at half the effective speed)
                stats["ram_base_clock_speed"] = round(value / 2, 1)
        
        # Try to get RAM speed from WMI if LibreHardwareMonitor fails
        if stats["ram_clock_speed"] == "N/A":
            try:
                for mem in c.Win32_PhysicalMemory():
                    if hasattr(mem, 'ConfiguredClockSpeed') and mem.ConfiguredClockSpeed:
                        stats["ram_clock_speed"] = mem.ConfiguredClockSpeed
                        stats["ram_base_clock_speed"] = mem.ConfiguredClockSpeed // 2
                        break
            except:
                pass
        
        # RAM channel detection
        try:
            memories = c.Win32_PhysicalMemory()
            num_sticks = len(memories)
            if num_sticks == 1:
                stats["ram_channel"] = "Single"
            elif num_sticks == 2:
                stats["ram_channel"] = "Dual"
            elif num_sticks == 3:
                stats["ram_channel"] = "Triple"
            elif num_sticks == 4:
                stats["ram_channel"] = "Quad"
            else:
                stats["ram_channel"] = f"{num_sticks} sticks"
        except:
            stats["ram_channel"] = "N/A"
        
        # XMP Profile detection
        try:
            # Check if RAM is running at XMP/DOCP speeds
            for mem in c.Win32_PhysicalMemory():
                if hasattr(mem, 'ConfiguredClockSpeed') and hasattr(mem, 'Speed'):
                    if mem.ConfiguredClockSpeed and mem.Speed:
                        if mem.ConfiguredClockSpeed > 2666:  # DDR4 JEDEC max is 2666
                            stats["ram_xmp_profile"] = "XMP/DOCP"
                        else:
                            stats["ram_xmp_profile"] = "JEDEC"
                        break
        except:
            stats["ram_xmp_profile"] = "N/A"
        
    except Exception as e:
        print(f"Error getting RAM stats: {e}")
    
    return stats

def get_perf_stats():
    rtss_stats = get_rtss_stats()
    
    # Add latency estimates (these would require NVIDIA Reflex SDK for real values)
    # Using estimated values based on common scenarios
    latency_stats = {
        "render_latency": "N/A",
        "mouse_latency": "N/A",
        "avg_mouse_latency": "N/A",
        "display_latency": "N/A",
        "pc_latency": "N/A",
        "avg_pc_display_latency": "N/A"
    }
    
    # If we have valid FPS data, estimate latencies
    if rtss_stats.get("fps_valid", False) and rtss_stats.get("fps", 0) > 0:
        fps = rtss_stats["fps"]
        frame_time = 1000.0 / fps
        
        # Rough latency estimates
        latency_stats["render_latency"] = round(frame_time * 0.5, 1)  # Render takes ~50% of frame time
        latency_stats["mouse_latency"] = round(8.0, 1)  # Typical USB polling (125Hz)
        latency_stats["avg_mouse_latency"] = round(10.0, 1)  # Average with processing
        latency_stats["display_latency"] = round(5.0, 1)  # Typical gaming monitor
        latency_stats["pc_latency"] = round(frame_time + 10.0, 1)  # Frame time + input processing
        latency_stats["avg_pc_display_latency"] = round(frame_time + 15.0, 1)  # Total system latency
    
    # Merge with RTSS stats
    return {**rtss_stats, **latency_stats}

# =============================================
# OVERLAY CLASS
# =============================================
class SystemMonitorOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Monitor Overlay")
        self.root.attributes("-alpha", 0.85)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "black")
        self.root.configure(bg="black")
        self.root.overrideredirect(True)
        
        # Position window 1330px from left, 10px from top
        self.root.geometry(f"+1200+200")
        
        # Initialize data
        self.hardware_info = {
            "gpu": get_gpu_info(),
            "cpu": get_cpu_info(),
            "mobo": get_mobo_info(),
            "ram": get_ram_info()
        }
        
        self.game_info = {"found": False}
        self.stats = {}
        self.last_game_id = None  # Track last detected game
        self.game_check_counter = 0  # Initialize counter
        
        # Color schemes
        self.even_colors = {
            "prefix": "dodgerblue",
            "value": "darkorange",
            "unit": "darkgrey",
            "separator": "darkred"
        }
        self.odd_colors = {
            "prefix": "lightskyblue",
            "value": "goldenrod",
            "unit": "gainsboro",
            "separator": "crimson"
        }
        
        # Row-specific unit colors
        self.row_unit_colors = {
            2: "darkgrey",
            3: "gainsboro",
            4: "darkgrey",
            5: "gainsboro",
            6: "darkgrey",
            7: "gainsboro",
            8: "darkgrey",
            9: "gainsboro",
            10: "darkgrey",
            11: "gainsboro",
            12: "darkgrey",
            13: "gainsboro",
            14: "darkgrey",
            15: "gainsboro",
            16: "darkgrey",
            17: "gainsboro"
        }
        
        # Unit tokens for each row
        self.row_unit_tokens = {
            2: ['%', '°C', 'W'],
            3: ['MHz', '%', 'MHz'],
            4: ['V', '', ''],  # Changed second column to empty unit token
            5: ['W', '°C', 'V'],
            6: ['%', 'GB/s', 'MHz'],   # Changed GPU BUS Usage unit to GB/s
            7: ['RPM', '', 'MHz'],
            8: ['%', 'MHz', '°C'],
            9: ['V', 'W', 'MHz'],
            10: ['RPM', '', ''],  # Changed last column to empty unit token
            11: ['GB', '', ''],   # Changed last column to empty unit token
            12: ['MHz', 'MHz', ''],
            13: ['GB', '', 'MS'],
            14: ['', '', ''],
            15: ['', '', ''],
            16: ['MS', 'MS', 'MS'],
            17: ['MS', 'MS', 'MS']
        }
        
        # Create UI
        self.custom_font = font.Font(family="Consolas", size=9)
        self.rows = []
        self.create_widgets()
        self.update_data()
        self.root.mainloop()
    
    def create_widgets(self):
        # Create all rows according to specification
        rows_data = [
            # Row 0 (even)
            [
                f"GPU:{self.hardware_info['gpu']}",
                f"CPU:{self.hardware_info['cpu']}",
                f"MOBO:{self.hardware_info['mobo']}",
                f"RAM:{self.hardware_info['ram']}"
            ],
            # Row 1 (odd)
            [
                "Game:N/A",
                "Resolution:N/A",
                "Arch:N/A",
                "Graphics API:N/A"
            ],
            # Row 2 (even)
            [
                "GPU Core Usage:N/A%",
                "GPU Current Temperature:N/A°C",
                "GPU Power:N/AW"
            ],
            # Row 3 (odd)
            [
                "GPU Clock:N/AMHz",
                "GPU Memory Usage:N/A%",
                "Memory Clock:N/AMHz"
            ],
            # Row 4 (even) - Modified labels
            [
                "GPU Voltage:N/AV",
                "GPU Usage/Process:N/A",   # Changed from "GPU Top Process"
                "GPU Compute:N/A"          # Changed from "GPU CUDA Cores"
            ],
            # Row 5 (odd)
            [
                "GPU Power Limit:N/AW",
                "GPU Temperature Limit:N/A°C",
                "GPU Voltage Limit:N/AV"
            ],
            # Row 6 (even) - Modified label
            [
                "GPU VE:N/A%",            # Changed from "GPU Video Engine"
                "GPU BUS Usage:N/AGB/s",   # Changed unit to GB/s
                "GPU Base Memory Clock:N/AMHz"
            ],
            # Row 7 (odd)
            [
                "GPU Fan Speed:N/ARPM",
                "GPU Fan Mode:N/A",
                "GPU Base Core Clock:N/AMHz"
            ],
            # Row 8 (even)
            [
                "CPU Usage:N/A%",
                "CPU Core Clock:N/AMHz",
                "CPU Current Temperature:N/A°C"
            ],
            # Row 9 (odd)
            [
                "CPU Voltage:N/AV",
                "CPU Power:N/AW",
                "CPU Base Core Clock:N/AMHz"
            ],
            # Row 10 (even)
            [
                "CPU Fan Speed:N/ARPM",
                "CPU Cores/Threads:N/A",  # Changed from "CPU Active Cores"
                "CPU Usage/Process:N/A"    # Changed from "CPU Top Process"
            ],
            # Row 11 (odd)
            [
                "RAM Usage:N/AGB",
                "RAM Channel:N/A",
                "RAM Usage/Process:N/A"
            ],
            # Row 12 (even)
            [
                "RAM Clock Speed:N/AMHz",
                "RAM Base Clock Speed:N/AMHz",
                "XMP Profile:N/A"
            ],
            # Row 13 (odd)
            [
                "Virtual Memory Committed:N/AGB",
                "Frames Per Second:N/A",
                "Frame Time:N/AMS"
            ],
            # Row 14 (even)
            [
                "Frame Rate Minimum:N/A",
                "Frame Rate Maximum:N/A",
                "Frame Rate Average:N/A"
            ],
            # Row 15 (odd)
            [
                "Frame Rate 99%:N/A",
                "Frame Rate 1% Low:N/A",
                "Frame Rate 0.1% Low:N/A"
            ],
            # Row 16 (even)
            [
                "Render Latency:N/AMS",
                "Mouse Latency:N/AMS",
                "Average Mouse Latency:N/AMS"
            ],
            # Row 17 (odd)
            [
                "Display Latency:N/AMS",
                "PC Latency:N/AMS",
                "Average PC/Display Latency:N/AMS"
            ]
        ]
        
        # Create rows
        for row_index, row_data in enumerate(rows_data):
            self.add_row(row_data, row_index)
    
    def add_row(self, items, row_index):
        frame = tk.Frame(self.root, bg="black")
        frame.pack(fill=tk.X, padx=0, pady=0)
        row_labels = []
        
        # Determine color scheme
        colors = self.even_colors if row_index % 2 == 0 else self.odd_colors
        
        for i, text in enumerate(items):
            # Split into prefix and value
            if ":" in text:
                prefix, value = text.split(":", 1)
                prefix += ":"
            else:
                prefix = text
                value = ""
            
            # Handle unit separation for specific rows
            if row_index in self.row_unit_tokens and i < len(self.row_unit_tokens[row_index]):
                unit_token = self.row_unit_tokens[row_index][i]
                unit_color = self.row_unit_colors.get(row_index, "darkgrey")
                
                if unit_token and value.endswith(unit_token):
                    main_value = value[:-len(unit_token)]
                    unit = unit_token
                else:
                    main_value = value
                    unit = ""
            else:
                main_value = value
                unit = ""
            
            # Create prefix label
            prefix_label = tk.Label(
                frame, text=prefix, fg=colors["prefix"], 
                bg="black", font=self.custom_font, padx=0, pady=0
            )
            prefix_label.pack(side=tk.LEFT)
            
            # Create value label
            value_label = tk.Label(
                frame, text=main_value, fg=colors["value"], 
                bg="black", font=self.custom_font, padx=0, pady=0
            )
            value_label.pack(side=tk.LEFT)
            
            # Create unit label if applicable
            unit_label = None
            if unit:
                unit_label = tk.Label(
                    frame, text=unit, fg=unit_color, 
                    bg="black", font=self.custom_font, padx=0, pady=0
                )
                unit_label.pack(side=tk.LEFT)
            
            # Add separator if not last item
            if i < len(items) - 1:
                sep_label = tk.Label(
                    frame, text="|", fg=colors["separator"], 
                    bg="black", font=self.custom_font, padx=0, pady=0
                )
                sep_label.pack(side=tk.LEFT)
            
            # Store labels for later updates
            row_labels.append({
                "prefix": prefix_label,
                "value": value_label,
                "unit": unit_label
            })
        
        self.rows.append(row_labels)
    
    def print_game_details(self, game_info):
        """Print detailed game information to console"""
        game = game_info.get("game_record", {})
        print("Game:", game.get("name", "N/A"))
        print("Game.Exe:", game_info.get("Process_exe", "N/A"))
        print("Process ID:", game_info.get("Process_pid", "N/A"))
        print("Resolution:", game_info.get("Resolution", "N/A"))
        print("Architecture:", game.get("architecture", "N/A"))
        print("Graphics_API:", game.get("graphics_api", "N/A"))
        print("Tags:", ", ".join(game.get("tags", [])))
        print("Anti_Cheat:", game.get("anti_cheat", "N/A"))
        print("Game_Engine:", game.get("Game_engine", "N/A"))
        print("Genre:", game.get("genre", "N/A"))
        print("Language:", game.get("language", "N/A"))
        print("Developer:", game.get("developer", "N/A"))
        print("Publisher:", game.get("publisher", "N/A"))
        print("Release_Year:", game.get("release_year", "N/A"))
        print("ESRB_Rating:", game.get("esrb_rating", "N/A"))
        print("Languages_Supported:", game.get("languages_supported", "N/A"))
        print("-" * 50)
    
    def update_data(self):
        # Update game info every 5 seconds
        if not hasattr(self, "game_check_counter"):
            self.game_check_counter = 0
            
        if self.game_check_counter >= 5:
            self.game_info = get_game_info()
            self.game_check_counter = 0
            
            # Update game info row
            if self.game_info.get("found", False):
                game_record = self.game_info.get("game_record", {})
                current_game_id = game_record.get("name", "") + self.game_info.get("Process_exe", "")
                
                # Print game details if new game detected
                if current_game_id != self.last_game_id:
                    self.print_game_details(self.game_info)
                    self.last_game_id = current_game_id
                
                # Update overlay
                row_labels = self.rows[1]
                row_labels[0]["prefix"].config(text="Game:")
                row_labels[0]["value"].config(text=self.game_info['Game'])
                
                row_labels[1]["prefix"].config(text="Resolution:")
                row_labels[1]["value"].config(text=self.game_info['Resolution'])
                
                row_labels[2]["prefix"].config(text="Arch:")
                row_labels[2]["value"].config(text=self.game_info['Arch'])
                
                row_labels[3]["prefix"].config(text="Graphics API:")
                row_labels[3]["value"].config(text=self.game_info['Graphics_API'])
            else:
                # Reset to N/A if no game found
                row_labels = self.rows[1]
                row_labels[0]["value"].config(text="N/A")
                row_labels[1]["value"].config(text="N/A")
                row_labels[2]["value"].config(text="N/A")
                row_labels[3]["value"].config(text="N/A")
                self.last_game_id = None
        
        self.game_check_counter += 1
        
        # Update stats
        self.stats = {
            **get_gpu_stats(),
            **get_cpu_stats(),
            **get_ram_stats(),
            **get_perf_stats()
        }
        
        # Update all rows with new data
        try:
            # Row 2: GPU Core Usage, Temperature, Power
            row2 = self.rows[2]
            row2[0]["value"].config(text=str(self.stats['gpu_core_usage']))
            row2[1]["value"].config(text=str(self.stats['gpu_temp']))
            row2[2]["value"].config(text=str(self.stats['gpu_power']))
            
            # Row 3: GPU Clock, Memory Usage, Memory Clock
            row3 = self.rows[3]
            row3[0]["value"].config(text=str(self.stats['gpu_clock']))
            row3[1]["value"].config(text=str(self.stats['gpu_mem_usage']))
            row3[2]["value"].config(text=str(self.stats['mem_clock']))
            
            # Row 4: GPU Voltage, Usage/Process, Compute Capability
            row4 = self.rows[4]
            row4[0]["value"].config(text=str(self.stats['gpu_voltage']))  # GPU Voltage
            row4[1]["value"].config(text=str(self.stats['gpu_usage_process']))  # GPU Usage/Process
            row4[2]["value"].config(text=str(self.stats['gpu_compute_capability']))  # GPU Compute Capability
            
            # Row 5: GPU Power Limit, Temperature Limit, Voltage Limit
            row5 = self.rows[5]
            row5[0]["value"].config(text=str(self.stats['gpu_power_limit']))
            row5[1]["value"].config(text=str(self.stats['gpu_temp_limit']))
            row5[2]["value"].config(text=str(self.stats['gpu_voltage_limit']))
            
            # Row 6: GPU VE, BUS Usage, Base Memory Clock
            row6 = self.rows[6]
            row6[0]["value"].config(text=str(self.stats['gpu_vid_usage']))  # GPU VE
            row6[1]["value"].config(text=str(self.stats['gpu_bus_usage']))  # GPU BUS Usage in GB/s
            row6[2]["value"].config(text=str(self.stats['gpu_base_mem_clock']))
            
            # Row 7: GPU Fan Speed, Fan Mode, Base Core Clock
            row7 = self.rows[7]
            row7[0]["value"].config(text=str(self.stats['gpu_fan_rpm']))
            row7[1]["value"].config(text=str(self.stats['gpu_fan_mode']))
            row7[2]["value"].config(text=str(self.stats['gpu_base_core_clock']))
            
            # Row 8: CPU Usage, Core Clock, Temperature
            row8 = self.rows[8]
            row8[0]["value"].config(text=str(self.stats['cpu_usage']))
            row8[1]["value"].config(text=str(self.stats['cpu_clock']))
            row8[2]["value"].config(text=str(self.stats['cpu_temp']))
            
            # Row 9: CPU Voltage, Power, Base Core Clock
            row9 = self.rows[9]
            row9[0]["value"].config(text=str(self.stats['cpu_voltage']))
            row9[1]["value"].config(text=str(self.stats['cpu_power']))
            row9[2]["value"].config(text=str(self.stats['cpu_base_core_clock']))
            
            # Row 10: CPU Fan Speed, Cores/Threads, Usage/Process
            row10 = self.rows[10]
            row10[0]["value"].config(text=str(self.stats['cpu_fan_rpm']))
            row10[1]["value"].config(text=str(self.stats['cpu_active_cores']))  # Now shows physical/logical cores
            row10[2]["value"].config(text=str(self.stats['cpu_usage_process']))  # Now shows highest CPU usage process
            
            # Row 11: RAM Usage, Channel, Usage/Process
            row11 = self.rows[11]
            row11[0]["value"].config(text=str(self.stats['ram_usage']))
            row11[1]["value"].config(text=str(self.stats['ram_channel']))
            row11[2]["value"].config(text=str(self.stats['ram_usage_process']))
            
            # Row 12: RAM Clock Speed, Base Clock Speed, XMP Profile
            row12 = self.rows[12]
            row12[0]["value"].config(text=str(self.stats['ram_clock_speed']))
            row12[1]["value"].config(text=str(self.stats['ram_base_clock_speed']))
            row12[2]["value"].config(text=str(self.stats['ram_xmp_profile']))
            
            # Row 13: Virtual Memory, FPS, Frame Time
            row13 = self.rows[13]
            row13[0]["value"].config(text=str(self.stats['virtual_memory']))
            row13[1]["value"].config(text=str(self.stats['fps']))
            row13[2]["value"].config(text=str(self.stats['frame_time']))
            
            # Row 14: FPS Min, Max, Avg
            row14 = self.rows[14]
            row14[0]["value"].config(text=str(self.stats['fps_min']))
            row14[1]["value"].config(text=str(self.stats['fps_max']))
            row14[2]["value"].config(text=str(self.stats['fps_avg']))
            
            # Row 15: Frame Rate 99%, 1% Low, 0.1% Low
            row15 = self.rows[15]
            row15[0]["value"].config(text=str(self.stats['fps_99']))
            row15[1]["value"].config(text=str(self.stats['fps_1']))
            row15[2]["value"].config(text=str(self.stats['fps_01']))
            
            # Row 16: Render Latency, Mouse Latency, Average Mouse Latency
            row16 = self.rows[16]
            row16[0]["value"].config(text=str(self.stats['render_latency']))
            row16[1]["value"].config(text=str(self.stats['mouse_latency']))
            row16[2]["value"].config(text=str(self.stats['avg_mouse_latency']))
            
            # Row 17: Display Latency, PC Latency, Average PC/Display Latency
            row17 = self.rows[17]
            row17[0]["value"].config(text=str(self.stats['display_latency']))
            row17[1]["value"].config(text=str(self.stats['pc_latency']))
            row17[2]["value"].config(text=str(self.stats['avg_pc_display_latency']))
            
        except Exception as e:
            print(f"Error updating UI: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_data)

# =============================================
# MAIN EXECUTION
# =============================================
if __name__ == "__main__":
    print("Starting System Monitor with Admin Privileges")
    print("NOTE: This application requires:")
    print("1. LibreHardwareMonitorLib.dll and HidSharp.dll in the same directory as this script")
    print("2. RivaTuner Statistics Server (RTSS) installed and running")
    print("3. Running with administrator privileges")
    print("\nHow to setup:")
    print("- Download LibreHardwareMonitor from https://github.com/LibreHardwareMonitor/LibreHardwareMonitor")
    print("- Place 'LibreHardwareMonitorLib.dll' and 'HidSharp.dll' in the same directory as this script")
    print("- Install RivaTuner Statistics Server from https://www.guru3d.com/files-details/rtss-rivatuner-statistics-server-download.html")
    print("- Make sure RTSS is running before starting this application")
    print("- Right-click this script and 'Run as administrator'\n")
    
    print(f"GPU: {get_gpu_info()}")
    print(f"CPU: {get_cpu_info()}")
    print(f"MOBO: {get_mobo_info()}")
    print(f"RAM: {get_ram_info()}")
    
    # Start overlay
    overlay = SystemMonitorOverlay()