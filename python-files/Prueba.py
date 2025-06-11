import os
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def disable_windows_defender():
    try:
        # Desactivar Windows Defender
        os.system('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"')
        os.system('powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true"')
        os.system('powershell -Command "Set-MpPreference -DisableBlockAtFirstSeen $true"')
        os.system('powershell -Command "Set-MpPreference -DisableIOAVProtection $true"')
        os.system('powershell -Command "Set-MpPreference -DisableScriptScanning $true"')
        print("✅ Windows Defender desactivado correctamente.")
    except Exception as e:
        print(f"❌ Error al desactivar Windows Defender: {e}")

def disable_firewall():
    try:
        # Desactivar Firewall de Windows
        os.system('netsh advfirewall set allprofiles state off')
        print("✅ Firewall desactivado correctamente.")
    except Exception as e:
        print(f"❌ Error al desactivar el Firewall: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("🔒 Este script requiere permisos de administrador. Ejecútalo como administrador.")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        print("=== Desactivando protecciones de Windows (solo para pruebas) ===")
        disable_windows_defender()
        disable_firewall()
        input("Presiona Enter para salir...")