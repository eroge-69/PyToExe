import sys
import threading
import time
import winreg
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QCheckBox, QPushButton, 
                             QProgressBar, QMessageBox, QFrame, QSplitter, QScrollArea, QGridLayout, QSplashScreen)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QMovie

def is_admin():
    """Check if the application is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ApplyTweaksThread(QThread):
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, selected_tweaks):
        super().__init__()
        self.selected_tweaks = selected_tweaks
    
    def run(self):
        total = len(self.selected_tweaks)
        for i, tweak in enumerate(self.selected_tweaks):
            self.progress_updated.emit(
                int((i + 1) / total * 100), 
                f"Applying: {tweak}"
            )
            
            if tweak == "Keyboard Tweaks":
                success = self.apply_keyboard_tweaks()
                if not success:
                    return
            elif tweak == "Boost CPU Cores":
                success = self.apply_cpu_boost_tweaks()
                if not success:
                    return
            elif tweak == "Clean Memory":
                success = self.apply_clean_memory_tweaks()
                if not success:
                    return
            elif tweak == "CPU Tweak":
                success = self.apply_cpu_tweak()
                if not success:
                    return
            elif tweak == "CpuPriority":
                success = self.apply_cpu_priority_tweak()
                if not success:
                    return
            elif tweak == "decrease delay" or tweak == "delay tweak":
                success = self.apply_lanmanserver_delay_tweak()
                if not success:
                    return
            elif tweak == "delete latency":
                success = self.apply_delete_latency_tweak()
                if not success:
                    return
            elif tweak == "gamebar FSO remove":
                success = self.apply_gamebar_fso_remove_tweak()
                if not success:
                    return
            elif tweak == "Game DVR":
                success = self.apply_game_dvr_tweak()
                if not success:
                    return
            elif tweak == "disable gpu energyDriver":
                success = self.apply_disable_gpu_energydrv_tweak()
                if not success:
                    return
            elif tweak == "disable limited user account control":
                success = self.apply_disable_limited_uac_tweak()
                if not success:
                    return
            elif tweak == "Disable Network Throttling":
                success = self.apply_disable_network_throttling_tweak()
                if not success:
                    return
            elif tweak == "Disable Power Throttling 2":
                success = self.apply_disable_power_throttling_2_tweak()
                if not success:
                    return
            elif tweak == "Disable Spectre _ Meltdown Protection":
                success = self.apply_disable_spectre_meltdown_protection_tweak()
                if not success:
                    return
            elif tweak == "Disable Transparency":
                success = self.apply_disable_transparency_tweak()
                if not success:
                    return
            elif tweak == "Disable_Game_Bar":
                success = self.apply_disable_game_bar_tweak()
                if not success:
                    return
            elif tweak == "DIsable_unnecessary_services_in_background":
                success = self.apply_disable_unnecessary_services_tweak()
                if not success:
                    return
            elif tweak == "xbox service disable":
                success = self.apply_xbox_service_disable_tweak()
                if not success:
                    return
            elif tweak == "Fortnite reg tweak":
                success = self.apply_fortnite_reg_tweak()
                if not success:
                    return
            elif tweak == "edit tweak":
                success = self.apply_edit_tweak()
                if not success:
                    return
            elif tweak == "low ping and delay":
                success = self.apply_low_ping_and_delay_tweak()
                if not success:
                    return
            elif tweak == "lower proccess":
                success = self.apply_lower_proccess_tweak()
                if not success:
                    return
            elif tweak == "Memory Management Optimizations":
                success = self.apply_memory_management_optimizations_tweak()
                if not success:
                    return
            elif tweak == "Optimize Windows":
                success = self.apply_optimize_windows_tweak()
                if not success:
                    return
            elif tweak == "DXGKrnl Latency Tweaks":
                success = self.apply_dxgkrnl_latency_tweaks()
                if not success:
                    return
            elif tweak == "Monitor Latency Tolerance":
                success = self.apply_monitor_latency_tolerance_tweak()
                if not success:
                    return
            
            time.sleep(0.5)  # Simulate processing time
        self.finished.emit()
    
    def apply_keyboard_tweaks(self):
        """Apply keyboard registry tweaks"""
        try:
            # Check for admin privileges
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            
            # Open the registry key
            key_path = r"SYSTEM\CurrentControlSet\Services\kbdclass\Parameters"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Registry values to set
            registry_values = {
                "KeyboardDataQueueSize": (0x32, winreg.REG_DWORD),
                "ConnectMultiplePorts": (0x00, winreg.REG_DWORD),
                "KeyboardDeviceBaseName": ("KeyboardClass", winreg.REG_SZ),
                "MaximumPortsServiced": (0x03, winreg.REG_DWORD),
                "SendOutputToAllPorts": (0x01, winreg.REG_DWORD),
                "WppRecorder_TraceGuid": ("{09281f1f-f66e-485a-99a2-91638f782c49}", winreg.REG_SZ)
            }
            
            # Set each registry value
            for name, (value, value_type) in registry_values.items():
                winreg.SetValueEx(key, name, 0, value_type, value)
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error applying keyboard tweaks: {str(e)}")
            return False
    
    def apply_cpu_boost_tweaks(self):
        """Apply CPU boost registry tweaks"""
        try:
            # Check for admin privileges
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            
            # Open the registry key
            key_path = r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\943c8cb6-6f93-4227-ad87-e9a3feec08d1"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Set the Attributes value
            winreg.SetValueEx(key, "Attributes", 0, winreg.REG_DWORD, 0x02)
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error applying CPU boost tweaks: {str(e)}")
            return False
    
    def apply_clean_memory_tweaks(self):
        """Apply clean memory registry tweaks"""
        try:
            # Check for admin privileges
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            
            # Open the registry key
            key_path = r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Set the value to disable Game DVR
            winreg.SetValueEx(key, "value", 0, winreg.REG_DWORD, 0x00)
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error applying clean memory tweaks: {str(e)}")
            return False
    
    def apply_cpu_tweak(self):
        """Apply CPU gaming performance registry tweaks"""
        try:
            # Check for admin privileges
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            
            # Open the registry key
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Registry values to set
            registry_values = {
                "GPU Priority": (0x08, winreg.REG_DWORD),
                "Priority": (0x06, winreg.REG_DWORD),
                "Scheduling Category": ("High", winreg.REG_SZ),
                "SFIO Priority": ("High", winreg.REG_SZ)
            }
            
            # Set each registry value
            for name, (value, value_type) in registry_values.items():
                winreg.SetValueEx(key, name, 0, value_type, value)
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Error applying CPU tweak: {str(e)}")
            return False

    def apply_cpu_priority_tweak(self):
        """Set CpuPriorityClass for csgo.exe"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\csgo.exe\PerfOptions"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.SetValueEx(key, "CpuPriorityClass", 0, winreg.REG_DWORD, 0x03)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying CpuPriority tweak: {str(e)}")
            return False

    def apply_lanmanserver_delay_tweak(self):
        """Set LanmanServer Parameters for delay tweaks"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key_path = r"SYSTEM\CurrentControlSet\services\LanmanServer\Parameters"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            values = {
                "autodisconnect": (0xffffffff, winreg.REG_DWORD),
                "Size": (0x03, winreg.REG_DWORD),
                "EnableOplocks": (0x00, winreg.REG_DWORD),
                "IRPStackSize": (0x20, winreg.REG_DWORD),
                "SharingViolationDelay": (0x00, winreg.REG_DWORD),
                "SharingViolationRetries": (0x00, winreg.REG_DWORD),
            }
            for name, (value, value_type) in values.items():
                winreg.SetValueEx(key, name, 0, value_type, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying delay tweak: {str(e)}")
            return False

    def apply_delete_latency_tweak(self):
        """Apply all registry tweaks for 'delete latency'"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # Helper for hex binary
            def hexstr_to_bytes(hexstr):
                return bytes(hexstr)
            # 1. HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\kernel
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel")
            winreg.SetValueEx(key, "DynamicDpcProtocol", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)

            # 2. HKEY_CURRENT_USER\Control Panel\Mouse
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse")
            winreg.SetValueEx(key, "MouseSensitivity", 0, winreg.REG_SZ, "10")
            winreg.SetValueEx(key, "SmoothMouseXCurve", 0, winreg.REG_BINARY, bytes([
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0xC0,0xCC,0x0C,0x00,0x00,0x00,0x00,0x00,
                0x80,0x99,0x19,0x00,0x00,0x00,0x00,0x00,
                0x40,0x66,0x26,0x00,0x00,0x00,0x00,0x00,
                0x00,0x33,0x33,0x00,0x00,0x00,0x00,0x00
            ]))
            winreg.SetValueEx(key, "SmoothMouseYCurve", 0, winreg.REG_BINARY, bytes([
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x38,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x70,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0xA8,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0xE0,0x00,0x00,0x00,0x00,0x00
            ]))
            winreg.SetValueEx(key, "SmoothMouseYCurve", 0, winreg.REG_BINARY, bytes([
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x38,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x70,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0xA8,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0xE0,0x00,0x00,0x00,0x00,0x00
            ]))
            winreg.CloseKey(key)

            # 3. HKEY_USERS\.DEFAULT\Control Panel\Mouse
            key = winreg.CreateKey(winreg.HKEY_USERS, r".DEFAULT\Control Panel\Mouse")
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key)

            # 4. HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
            winreg.SetValueEx(key, "NoInstrumentation", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)

            # 5. HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
            winreg.SetValueEx(key, "NoInstrumentation", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)

            # 6. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\SQMClient\Windows
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\SQMClient\Windows")
            winreg.SetValueEx(key, "CEIPEnable", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 7. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\HandwritingErrorReports
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\HandwritingErrorReports")
            winreg.SetValueEx(key, "PreventHandwritingErrorReports", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)

            # 8. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection")
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 9. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection")
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 10. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\AppCompat
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\AppCompat")
            winreg.SetValueEx(key, "AITEnable", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 11. HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters")
            tcpip_values = {
                "DelayedAckFrequency": 0x01,
                "DelayedAckTicks": 0x01,
                "CongestionAlgorithm": 0x01,
                "MultihopSets": 0x0f,
                "FastCopyReceiveThreshold": 0x4000,
                "FastSendDatagramThreshold": 0x4000,
            }
            for name, value in tcpip_values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)

            # 12. HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\AFD\Parameters
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\AFD\Parameters")
            afd_values = {
                "DefaultReceiveWindow": 0x4000,
                "DefaultSendWindow": 0x4000,
                "FastCopyReceiveThreshold": 0x4000,
                "FastSendDatagramThreshold": 0x4000,
                "DynamicSendBufferDisable": 0x00,
                "IgnorePushBitOnReceives": 0x01,
                "NonBlockingSendSpecialBuffering": 0x01,
                "DisableRawSecurity": 0x01,
            }
            for name, value in afd_values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)

            # 13. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile")
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 14. HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl")
            winreg.SetValueEx(key, "ConvertibleSlateMode", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 0x26)
            winreg.CloseKey(key)

            # 15. HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Session Manager\Memory Management
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\Session Manager\Memory Management")
            mm_values = {
                "EnableCfg": 0x00,
                "FeatureSettings": 0x01,
                "FeatureSettingsOverride": 0x03,
                "FeatureSettingsOverrideMask": 0x03,
                "MoveImages": 0x00,
            }
            for name, value in mm_values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)

            # 16. HKEY_LOCAL_MACHINE\SYSTEM\ControlSet001\Control\Session Manager\Memory Management\PrefetchParameters
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\Session Manager\Memory Management\PrefetchParameters")
            winreg.SetValueEx(key, "EnablePrefetcher", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "EnableSuperfetch", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying delete latency tweak: {str(e)}")
            return False

    def apply_gamebar_fso_remove_tweak(self):
        """Apply registry tweaks to disable Game Bar/FSO and related GameDVR features"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # 1. HKEY_CURRENT_USER\System\GameConfigStore
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 0x02)
            winreg.SetValueEx(key, "GameDVR_HonorUserFSEBehaviorMode", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "GameDVR_DXGIHonorFSEWindowsCompatible", 0, winreg.REG_DWORD, 0x01)
            winreg.SetValueEx(key, "GameDVR_EFSEFeatureFlags", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 2. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR")
            winreg.SetValueEx(key, "value", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 3. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\GameDVR
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR")
            winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 4. HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\GameDVR
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR")
            winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying gamebar FSO remove tweak: {str(e)}")
            return False

    def apply_game_dvr_tweak(self):
        """Apply registry tweaks to disable Game DVR features"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # 1. HKEY_CURRENT_USER\System\GameConfigStore
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 2. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR")
            winreg.SetValueEx(key, "value", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 3. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\GameDVR
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR")
            winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 4. HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR")
            winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Game DVR tweak: {str(e)}")
            return False

    def apply_disable_gpu_energydrv_tweak(self):
        """Disable the GpuEnergyDrv service by setting Start=4"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\GpuEnergyDrv")
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 0x04)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying disable gpu energyDriver tweak: {str(e)}")
            return False

    def apply_disable_limited_uac_tweak(self):
        """Disable Limited User Account Control by setting EnableLUA=0"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System")
            winreg.SetValueEx(key, "EnableLUA", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying disable limited user account control tweak: {str(e)}")
            return False

    def apply_disable_network_throttling_tweak(self):
        """Disable network throttling and set system responsiveness to 0"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile")
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_DWORD, 0xffffffff)
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Disable Network Throttling tweak: {str(e)}")
            return False

    def apply_disable_power_throttling_2_tweak(self):
        """Disable Power Throttling by setting PowerThrottlingOff=1"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power\PowerThrottling")
            winreg.SetValueEx(key, "PowerThrottlingOff", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Disable Power Throttling 2 tweak: {str(e)}")
            return False

    def apply_disable_spectre_meltdown_protection_tweak(self):
        """Disable Spectre and Meltdown Protection by setting FeatureSettingsOverride and FeatureSettingsOverrideMask to 3"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management")
            winreg.SetValueEx(key, "FeatureSettingsOverride", 0, winreg.REG_DWORD, 0x03)
            winreg.SetValueEx(key, "FeatureSettingsOverrideMask", 0, winreg.REG_DWORD, 0x03)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Disable Spectre _ Meltdown Protection tweak: {str(e)}")
            return False

    def apply_disable_transparency_tweak(self):
        """Disable Windows UI transparency"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Disable Transparency tweak: {str(e)}")
            return False

    def apply_disable_game_bar_tweak(self):
        """Disable Game Bar and related GameDVR features"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # 1. HKEY_CURRENT_USER\System\GameConfigStore
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 0x02)
            winreg.SetValueEx(key, "GameDVR_HonorUserFSEBehaviorMode", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "GameDVR_DXGIHonorFSEWindowsCompatible", 0, winreg.REG_DWORD, 0x01)
            winreg.SetValueEx(key, "GameDVR_EFSEFeatureFlags", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 2. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR")
            winreg.SetValueEx(key, "value", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 3. HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\GameDVR
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR")
            winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 4. HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\GameDVR
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR")
            winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Disable_Game_Bar tweak: {str(e)}")
            return False

    def apply_disable_unnecessary_services_tweak(self):
        """Disable unnecessary background services by setting Start=4 for each service"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            services = [
                "WbioSrvc",        # Windows Biometric Service
                "FontCache",       # Windows Font Cache Service
                "FontCache3.0.0.0",# Font Cache 3.0.0.0
                "GraphicsPerfSvc", # Graphics performance monitor service
                "stisvc",          # Windows Image Acquisition
                "WerSvc",          # Windows Error Reporting Service
                "PcaSvc",          # Program Compatibility Assistant Service
                "Wecsvc",          # Windows Event Collector
            ]
            for service in services:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, fr"SYSTEM\CurrentControlSet\Services\{service}")
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 0x04)
                winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying DIsable_unnecessary_services_in_background tweak: {str(e)}")
            return False

    def apply_xbox_service_disable_tweak(self):
        """Disable Xbox-related services by setting Start=4 for each service"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            services = [
                "XblGameSave",      # Xbox Live Game Save
                "XboxNetApiSvc",   # Xbox Live Networking Service
                "XboxGipSvc",      # Xbox Accessory Management Service
                "XblAuthManager",  # Xbox Live Auth Manager
            ]
            for service in services:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, fr"SYSTEM\CurrentControlSet\Services\{service}")
                winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 0x04)
                winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying xbox service disable tweak: {str(e)}")
            return False

    def apply_fortnite_reg_tweak(self):
        """Set CpuPriorityClass=3 for FortniteClient-Win64-Shipping.exe"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\FortniteClient-Win64-Shipping.exe\PerfOptions"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            winreg.SetValueEx(key, "CpuPriorityClass", 0, winreg.REG_DWORD, 0x03)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Fortnite reg tweak: {str(e)}")
            return False

    def apply_edit_tweak(self):
        """Reinforce Network Priorities by setting ServiceProvider priorities"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\ServiceProvider")
            winreg.SetValueEx(key, "LocalPriority", 0, winreg.REG_DWORD, 0x04)
            winreg.SetValueEx(key, "HostsPriority", 0, winreg.REG_DWORD, 0x05)
            winreg.SetValueEx(key, "DnsPriority", 0, winreg.REG_DWORD, 0x06)
            winreg.SetValueEx(key, "NetbtPriority", 0, winreg.REG_DWORD, 0x07)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying edit tweak: {str(e)}")
            return False

    def apply_low_ping_and_delay_tweak(self):
        """Set LanmanServer Parameters for low ping and delay"""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\services\LanmanServer\Parameters")
            values = {
                "autodisconnect": 0xffffffff,
                "Size": 0x03,
                "EnableOplocks": 0x00,
                "IRPStackSize": 0x20,
                "SharingViolationDelay": 0x00,
                "SharingViolationRetries": 0x00,
            }
            for name, value in values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying low ping and delay tweak: {str(e)}")
            return False

    def apply_lower_proccess_tweak(self):
        """Apply a comprehensive set of registry tweaks for lower process latency and privacy."""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # 1. Disable GameDVR/GameBar/FSO
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR")
            winreg.SetValueEx(key, "value", 0, winreg.REG_SZ, "00000000")
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "GameDVR_FSEBehavior", 0, winreg.REG_DWORD, 0x02)
            winreg.SetValueEx(key, "GameDVR_FSEBehaviorMode", 0, winreg.REG_DWORD, 0x02)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR")
            winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR")
            winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            # 2. Unlock CPU core settings
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\943c8cb6-6f93-4227-ad87-e9a3feec08d1")
            winreg.SetValueEx(key, "Attributes", 0, winreg.REG_SZ, "2")
            winreg.CloseKey(key)

            # 3. System responsiveness and network throttling
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile")
            winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0x0a)
            winreg.SetValueEx(key, "NetworkThrottlingIndex", 0, winreg.REG_SZ, "fffffff")
            winreg.CloseKey(key)

            # 4. Games task tweaks
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games")
            winreg.SetValueEx(key, "Affinity", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "Background Only", 0, winreg.REG_SZ, "False")
            winreg.SetValueEx(key, "Clock Rate", 0, winreg.REG_DWORD, 0x2710)
            winreg.SetValueEx(key, "GPU Priority", 0, winreg.REG_DWORD, 0x08)
            winreg.SetValueEx(key, "Priority", 0, winreg.REG_DWORD, 0x06)
            winreg.SetValueEx(key, "Scheduling Category", 0, winreg.REG_SZ, "High")
            winreg.SetValueEx(key, "SFIO Priority", 0, winreg.REG_SZ, "High")
            winreg.CloseKey(key)

            # 5. Copy To/Move To context menu
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"AllFilesystemObjects\shellex\ContextMenuHandlers\Copy To")
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "{C2FBB630-2971-11D1-A18C-00C04FD75D13}")
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"AllFilesystemObjects\shellex\ContextMenuHandlers\Move To")
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, "{C2FBB631-2971-11D1-A18C-00C04FD75D13}")
            winreg.CloseKey(key)

            # 6. RAM management and system speed
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
            winreg.SetValueEx(key, "AutoEndTasks", 0, winreg.REG_SZ, "1")
            winreg.SetValueEx(key, "HungAppTimeout", 0, winreg.REG_SZ, "1000")
            winreg.SetValueEx(key, "MenuShowDelay", 0, winreg.REG_SZ, "8")
            winreg.SetValueEx(key, "WaitToKillAppTimeout", 0, winreg.REG_SZ, "2000")
            winreg.SetValueEx(key, "LowLevelHooksTimeout", 0, winreg.REG_SZ, "1000")
            winreg.CloseKey(key)

            # 7. Disable unnecessary Explorer features
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
            explorer_values = {
                "NoLowDiskSpaceChecks": 0x01,
                "LinkResolveIgnoreLinkInfo": 0x01,
                "NoResolveSearch": 0x01,
                "NoResolveTrack": 0x01,
                "NoInternetOpenWith": 0x01,
            }
            for name, value in explorer_values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)

            # 8. Speed up shutdown
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control")
            winreg.SetValueEx(key, "WaitToKillServiceTimeout", 0, winreg.REG_SZ, "2000")
            winreg.CloseKey(key)

            # 9. Mouse acceleration fix
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse")
            winreg.SetValueEx(key, "MouseSensitivity", 0, winreg.REG_SZ, "10")
            winreg.SetValueEx(key, "SmoothMouseXCurve", 0, winreg.REG_BINARY, bytes([
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0xC0,0xCC,0x0C,0x00,0x00,0x00,0x00,0x00,
                0x80,0x99,0x19,0x00,0x00,0x00,0x00,0x00,
                0x40,0x66,0x26,0x00,0x00,0x00,0x00,0x00,
                0x00,0x33,0x33,0x00,0x00,0x00,0x00,0x00
            ]))
            winreg.SetValueEx(key, "SmoothMouseYCurve", 0, winreg.REG_BINARY, bytes([
                0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x38,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0x70,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0xA8,0x00,0x00,0x00,0x00,0x00,
                0x00,0x00,0xE0,0x00,0x00,0x00,0x00,0x00
            ]))
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_USERS, r".DEFAULT\Control Panel\Mouse")
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
            winreg.CloseKey(key)

            # 10. DPI scaling fix
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop")
            winreg.SetValueEx(key, "Win8DpiScaling", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "DpiScalingVer", 0, winreg.REG_DWORD, 0x1000)
            winreg.SetValueEx(key, "LogPixels", 0, winreg.REG_DWORD, 0x96)
            winreg.CloseKey(key)

            # 11. Privacy tweaks
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
            winreg.SetValueEx(key, "NoInstrumentation", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer")
            winreg.SetValueEx(key, "NoInstrumentation", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\SQMClient\Windows")
            winreg.SetValueEx(key, "CEIPEnable", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\HandwritingErrorReports")
            winreg.SetValueEx(key, "PreventHandwritingErrorReports", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection")
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection")
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\AppCompat")
            winreg.SetValueEx(key, "AITEnable", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying lower proccess tweak: {str(e)}")
            return False

    def apply_memory_management_optimizations_tweak(self):
        """Apply memory management optimizations to the registry."""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # Main Memory Management key
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\Session Manager\Memory Management")
            values = {
                "DisablePagingExecutive": 0x01,
                "LargeSystemCache": 0x00,
                "NonPagedPoolQuota": 0x00,
                "NonPagedPoolSize": 0x00,
                "PagedPoolQuota": 0x00,
                "PagedPoolSize": 0xc0,
                "SystemPages": 0xffffffff,
                "FeatureSettingsOverride": 0x03,
                "FeatureSettingsOverrideMask": 0x03,
                "KernelSEHOPEnabled": 0x00,
                "DisableExceptionChainValidation": 0x01,
                "PhysicalAddressExtension": 0x01,
                "FeatureSettings": 0x01,
                "PoolUsageMaximum": 0x60,
                "EnableBoottrace": 0x00,
                "EnableCfg": 0x00,
                "EnableLowVaAccess": 0x00,
                "CoalescingTimerInterval": 0x00,
                "IoPageLockLimit": 0x7a1200,
                "DisablePagingCombining": 0x01,
            }
            for name, value in values.items():
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)

            # PrefetchParameters subkey
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\ControlSet001\Control\Session Manager\Memory Management\PrefetchParameters")
            winreg.SetValueEx(key, "EnableBootTrace", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "EnablePrefetcher", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)

            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Memory Management Optimizations tweak: {str(e)}")
            return False

    def apply_dxgkrnl_latency_tweaks(self):
        """Set MonitorLatencyTolerance and MonitorRefreshLatencyTolerance to 0 in DXGKrnl service key."""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DXGKrnl")
            winreg.SetValueEx(key, "MonitorLatencyTolerance", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "MonitorRefreshLatencyTolerance", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying DXGKrnl Latency Tweaks: {str(e)}")
            return False

    def apply_monitor_latency_tolerance_tweak(self):
        """Set MonitorLatencyTolerance and MonitorRefreshLatencyTolerance to 0 in DXGKrnl service key."""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DXGKrnl")
            winreg.SetValueEx(key, "MonitorLatencyTolerance", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "MonitorRefreshLatencyTolerance", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Monitor Latency Tolerance tweak: {str(e)}")
            return False

    def apply_optimize_windows_tweak(self):
        """Apply Adamx's Optimize Windows registry tweaks."""
        try:
            if not is_admin():
                self.error_occurred.emit("Administrator privileges are required to modify registry settings. Please run the application as Administrator.")
                return False
            # Accounts Tab (Disable Syncing)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync")
            winreg.SetValueEx(key, "SyncPolicy", 0, winreg.REG_DWORD, 0x05)
            winreg.CloseKey(key)
            for group in ["Personalization", "BrowserSettings", "Credentials", "Accessibility", "Windows"]:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, fr"SOFTWARE\Microsoft\Windows\CurrentVersion\SettingSync\Groups\{group}")
                winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0x00)
                winreg.CloseKey(key)
            # Personalization Tab (Disable Transparency)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # Gaming Tab AND Graphics Settings
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\PolicyManager\default\ApplicationManagement\AllowGameDVR")
            winreg.SetValueEx(key, "value", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR")
            winreg.SetValueEx(key, "AllowGameDVR", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore")
            winreg.SetValueEx(key, "GameDVR_Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR")
            winreg.SetValueEx(key, "AppCaptureEnabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # Enable Game Mode
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\GameBar")
            winreg.SetValueEx(key, "AllowAutoGameMode", 0, winreg.REG_DWORD, 0x01)
            winreg.SetValueEx(key, "AutoGameModeEnabled", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            # Enable Hardware Accelerated GPU Scheduling
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers")
            winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 0x02)
            winreg.CloseKey(key)
            # Disable Variable Refresh Rate
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\DirectX\UserGpuPreferences")
            winreg.SetValueEx(key, "DirectXUserGlobalSettings", 0, winreg.REG_SZ, "VRROptimizeEnable=0;")
            winreg.CloseKey(key)
            # Ease of Access Tab
            for subkey in ["MouseKeys", "StickyKeys", "Keyboard Response", "ToggleKeys"]:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, fr"Control Panel\Accessibility\{subkey}")
                winreg.SetValueEx(key, "Flags", 0, winreg.REG_SZ, "0")
                winreg.CloseKey(key)
            # Privacy Tab & General Tab
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo")
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Control Panel\International\User Profile")
            winreg.SetValueEx(key, "HttpAcceptLanguageOptOut", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced")
            winreg.SetValueEx(key, "Start_TrackProgs", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager")
            winreg.SetValueEx(key, "SubscribedContent-338393Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "SubscribedContent-353694Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "SubscribedContent-353696Enabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # Speech Tab
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Speech_OneCore\Settings\OnlineSpeechPrivacy")
            winreg.SetValueEx(key, "HasAccepted", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # Inking & Typing Personalization Tab
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Personalization\Settings")
            winreg.SetValueEx(key, "AcceptedPrivacyPolicy", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\InputPersonalization")
            winreg.SetValueEx(key, "RestrictImplicitInkCollection", 0, winreg.REG_DWORD, 0x01)
            winreg.SetValueEx(key, "RestrictImplicitTextCollection", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\InputPersonalization\TrainedDataStore")
            winreg.SetValueEx(key, "HarvestContacts", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # Diagnostics & Feedback Tab
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack")
            winreg.SetValueEx(key, "ShowedToastAtLevel", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection")
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Privacy")
            winreg.SetValueEx(key, "TailoredExperiencesWithDiagnosticDataEnabled", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack\EventTranscriptKey")
            winreg.SetValueEx(key, "EnableEventTranscript", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Siuf\Rules")
            winreg.SetValueEx(key, "NumberOfSIUFInPeriod", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # Activity History Tab
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\System")
            winreg.SetValueEx(key, "PublishUserActivities", 0, winreg.REG_DWORD, 0x00)
            winreg.SetValueEx(key, "UploadUserActivities", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            # App Permissions Tab
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userNotificationListener")
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny")
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location")
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny")
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\appDiagnostics")
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny")
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\userAccountInformation")
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny")
            winreg.CloseKey(key)
            # Disable Let Unnecessary Apps Run In The Background
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications")
            winreg.SetValueEx(key, "GlobalUserDisabled", 0, winreg.REG_DWORD, 0x01)
            winreg.CloseKey(key)
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search")
            winreg.SetValueEx(key, "BackgroundAppGlobalToggle", 0, winreg.REG_DWORD, 0x00)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error applying Optimize Windows tweak: {str(e)}")
            return False

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23293a, stop:1 #181c2a);")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        appname = QLabel("Zuls Tweaks")
        appname.setFont(QFont('Segoe UI', 28, QFont.Weight.Bold))
        appname.setStyleSheet("color: #e6eaf3;")
        appname.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner = QLabel()
        spinner.setFixedSize(120, 50)
        spinner.setStyleSheet("background: none;")
        spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spinner.setText("<span style='color:#3b82f6; font-size:28px; font-weight:bold;'></span>")
        layout.addWidget(appname)
        layout.addSpacing(16)
        layout.addWidget(spinner)
        self.setLayout(layout)
        self.setFixedSize(400, 220)

    def showEvent(self, event):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        splash_geometry = self.geometry()
        x = screen_geometry.x() + (screen_geometry.width() - splash_geometry.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - splash_geometry.height()) // 2
        self.move(x, y)
        super().showEvent(event)

class ZulsTweaks(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zuls Tweaks")
        self.setGeometry(100, 100, 1400, 800)  # Further increased width
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23293a, stop:1 #181c2a);
            }
        """)
        # List of all tweak names and descriptions
        tweak_info = [
            ("Keyboard Tweaks", "Optimize keyboard input and buffer for gaming responsiveness."),
            ("Boost CPU Cores", "Unlock CPU core settings for maximum performance."),
            ("Clean Memory", "Apply memory tweaks to reduce background memory usage."),
            ("CPU Tweak", "Optimize CPU for gaming performance."),
            ("CpuPriority", "Set CPU priority for csgo.exe."),
            ("decrease delay", "Reduce network and system delays."),
            ("delay tweak", "Reduce network and system delays."),
            ("delete latency", "Apply all registry tweaks for lower latency."),
            ("gamebar FSO remove", "Disable Game Bar/FSO and related GameDVR features."),
            ("Game DVR", "Disable Game DVR and related features for lower latency."),
            ("disable gpu energyDriver", "Disable the GpuEnergyDrv service."),
            ("disable limited user account control", "Disable Limited User Account Control (UAC)."),
            ("Disable Network Throttling", "Disable network throttling and set system responsiveness to 0."),
            ("Disable Power Throttling 2", "Disable Power Throttling by setting PowerThrottlingOff=1."),
            ("Disable Spectre _ Meltdown Protection", "Disable Spectre and Meltdown Protection."),
            ("Disable Transparency", "Disable Windows UI transparency."),
            ("Disable_Game_Bar", "Disable Game Bar and related GameDVR features."),
            ("DIsable_unnecessary_services_in_background", "Disable unnecessary background services."),
            ("xbox service disable", "Disable Xbox-related services."),
            ("Fortnite reg tweak", "Set CpuPriorityClass=3 for FortniteClient-Win64-Shipping.exe."),
            ("edit tweak", "Reinforce Network Priorities by setting ServiceProvider priorities."),
            ("low ping and delay", "Set LanmanServer Parameters for low ping and delay."),
            ("lower proccess", "Apply registry tweaks for lower process latency and privacy."),
            ("Memory Management Optimizations", "Apply memory management optimizations to the registry."),
            ("Optimize Windows", "Apply Adamx's Optimize Windows registry tweaks."),
            ("DXGKrnl Latency Tweaks", "Set MonitorLatencyTolerance and MonitorRefreshLatencyTolerance to 0."),
            ("Monitor Latency Tolerance", "Set MonitorLatencyTolerance and MonitorRefreshLatencyTolerance to 0."),
        ]
        # Header
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 24, 0, 0)
        title = QLabel("Zuls Tweaks")
        title.setFont(QFont('Segoe UI', 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6eaf3; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle = QLabel("Best Tweaks")
        subtitle.setFont(QFont('Segoe UI', 14))
        subtitle.setStyleSheet("color: #7a88a6;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #2e3650; background: #2e3650; min-height:2px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addSpacing(8)
        header_layout.addWidget(divider)
        header.setLayout(header_layout)
        # Scroll area setup
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollBar:vertical { background: #23293a; width: 12px; border-radius: 6px; } QScrollBar::handle:vertical { background: #3b82f6; border-radius: 6px; min-height: 40px; }")
        scroll_content = QWidget()
        grid = QGridLayout()
        grid.setSpacing(48)  # Further increased spacing
        for i, (name, desc) in enumerate(tweak_info):
            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            card.setStyleSheet('''
                QFrame {
                    background: #23293a;
                    border-radius: 18px;
                    border: 1.5px solid #2e3650;
                    padding: 28px 22px 22px 22px;
                    min-width: 600px;  /* Further increased min-width */
                    min-height: 140px;
                    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
                }
                QFrame:hover {
                    border: 1.5px solid #3b82f6;
                    box-shadow: 0 8px 32px #3b82f633;
                }
            ''')
            vbox = QVBoxLayout()
            title = QLabel(name)
            title.setFont(QFont('Segoe UI', 17, QFont.Weight.Bold))
            title.setStyleSheet('color: #e6eaf3;')
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet('color: #b0b8c9; font-size: 14px;')
            btn = QPushButton('Apply')
            btn.setStyleSheet('''
                QPushButton {
                    background: #3b82f6;
                    color: white;
                    border-radius: 8px;
                    padding: 10px 28px;
                    font-weight: bold;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background: #2563eb;
                }
            ''')
            btn.clicked.connect(lambda checked, t=name: self.apply_single_tweak(t))
            vbox.addWidget(title)
            vbox.addWidget(desc_label)
            vbox.addStretch()
            vbox.addWidget(btn, alignment=Qt.AlignmentFlag.AlignRight)
            card.setLayout(vbox)
            grid.addWidget(card, i // 2, i % 2)
        scroll_content.setLayout(grid)
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout()
        main_layout.addWidget(header)
        main_layout.addWidget(scroll)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def apply_single_tweak(self, tweak_name):
        self.thread = ApplyTweaksThread([tweak_name])
        self.thread.finished.connect(lambda: QMessageBox.information(self, "Tweak Applied", f"{tweak_name} applied!"))
        self.thread.error_occurred.connect(lambda msg: QMessageBox.critical(self, "Error", msg))
        self.thread.start()

    def showEvent(self, event):
        # Center the main window on the screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        win_geometry = self.frameGeometry()
        x = screen_geometry.x() + (screen_geometry.width() - win_geometry.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - win_geometry.height()) // 2
        self.move(x, y)
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    splash = SplashScreen()
    splash.show()
    def show_main():
        splash.close()
        window = ZulsTweaks()
        window.show()
    QTimer.singleShot(5000, show_main)  # 5 seconds
    sys.exit(app.exec())

if __name__ == "__main__":
    main()