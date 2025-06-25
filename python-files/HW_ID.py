import platform
import subprocess
import uuid
import re
import sys

def get_system_uuid():
    """Obtener UUID del sistema (HW)"""
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.check_output('wmic csproduct get uuid', shell=True).decode()
            return result.split('\n')[1].strip()
        elif system == "Linux":
            with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                return f.read().strip()
        elif system == "Darwin":  # macOS
            result = subprocess.check_output(['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice'])
            match = re.search(b'"IOPlatformUUID" = "(.*?)"', result)
            if match:
                return match.group(1).decode()
    except:
        return None
    return None

def get_mac_address():
    """Obtener dirección MAC primaria"""
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            # Obtiene la MAC de la interfaz en0 (usualmente la principal)
            result = subprocess.check_output(['ifconfig', 'en0'])
            match = re.search(b'ether\s+([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', result)
            if match:
                return match.group(1).decode().upper()
        else:
            # Usa el método estándar para Windows/Linux
            mac = uuid.getnode()
            if (mac >> 40) & 1:  # Verifica si es MAC local
                return None
            return ':'.join(['{:02X}'.format((mac >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])
    except:
        return None
    return None

def get_disk_serial():
    """Obtener identificador único de almacenamiento"""
    try:
        system = platform.system()
        if system == "Windows":
            result = subprocess.check_output('wmic diskdrive get serialnumber', shell=True).decode()
            return result.split('\n')[1].strip()
        elif system == "Linux":
            # Usar ID del disco en lugar de serial (más accesible)
            result = subprocess.check_output(['lsblk', '-dno', 'UUID', '/dev/sda']).decode().strip()
            return result if result else None
        elif system == "Darwin":  # macOS
            # Obtiene UUID del volumen de arranque
            result = subprocess.check_output(['diskutil', 'info', '/']).decode()
            match = re.search(r'Volume UUID:\s+([0-9A-F-]{36})', result)
            if match:
                return match.group(1)
    except:
        return None
    return None

def get_system_serial():
    """Obtener serial del hardware (especialmente útil para macOS)"""
    try:
        system = platform.system()
        if system == "Darwin":
            result = subprocess.check_output(['system_profiler', 'SPHardwareDataType']).decode()
            match = re.search(r'Serial Number \(system\):\s+(\S+)', result)
            if match:
                return match.group(1)
        elif system == "Linux":
            with open('/sys/class/dmi/id/product_serial', 'r') as f:
                return f.read().strip()
        elif system == "Windows":
            result = subprocess.check_output('wmic bios get serialnumber', shell=True).decode()
            return result.split('\n')[1].strip()
    except:
        return None
    return None

def generate_hardware_id():
    """Generar identificador único combinado"""
    identifiers = [
        get_system_uuid(),
        get_mac_address(),
        get_disk_serial(),
        get_system_serial()  # Nuevo elemento importante para macOS
    ]
    
    # Filtrar valores nulos y combinar
    valid_ids = [i for i in identifiers if i]
    
    if not valid_ids:
        return "ERROR_NO_HW_ID"
    
    combined = "-".join(valid_ids)
    
    # Generar hash para uniformidad y privacidad
    import hashlib
    return hashlib.sha256(combined.encode()).hexdigest()

# Ejecutar prueba
if __name__ == "__main__":
    print("\n=== Identificadores de Hardware ===")
    print(f"Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"UUID del sistema: {get_system_uuid()}")
    print(f"Dirección MAC: {get_mac_address()}")
    print(f"ID Almacenamiento: {get_disk_serial()}")
    print(f"Serial del sistema: {get_system_serial()}")
    print(f"\nID Único Generado: {generate_hardware_id()}")