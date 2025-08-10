import os
import subprocess
import wmi
import socket
import platform
import csv
from datetime import datetime

# Verificar la versión de Python
if platform.python_version_tuple()[0] < '3':
    print("⚠️ Python 3.0 o superior es requerido para ejecutar este script.")
    exit()

# Forzar enfoque para evitar doble ENTER si se ejecuta desde .bat o acceso directo
os.system('title Inventario de Equipo')

# Ruta de red y letra de unidad temporal
network_path = "\\\\10.60.0.4\\instaladores"
temp_drive = "Z:"
csv_file = os.path.join(temp_drive, "Jorge Moreno", "Inventario_Jorge.csv")

# Intentar conectar como invitado
subprocess.run(['net', 'use', temp_drive, network_path, '/user:Invitado', '""', '/persistent:no'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if not os.path.exists(temp_drive):
    print("❌ No se pudo conectar a la ruta compartida. Verifica acceso o permisos.")
    exit()

# === PREGUNTAS AL USUARIO ===
codigo_cpu = input("🖥️  Ingrese el CÓDIGO DE PATRIMONIO del CPU: ")
codigo_monitor = input("🖥️  Ingrese el CÓDIGO DE PATRIMONIO del MONITOR: ")
area = input("🏢 Ingrese el NOMBRE DEL ÁREA: ")
usuario = input("👤 Ingrese el NOMBRE DEL USUARIO: ")

# === INFORMACIÓN DEL SISTEMA ===
hostname = socket.gethostname()
os_info = wmi.WMI().Win32_OperatingSystem()[0]
cs_info = wmi.WMI().Win32_ComputerSystem()[0]
bios_info = wmi.WMI().Win32_BIOS()[0]
cpu_info = wmi.WMI().Win32_Processor()[0]
ram_gb = round(cs_info.TotalPhysicalMemory / (1024 ** 3), 2)
arch = os_info.OSArchitecture

# ==== IP ====
ip = ""
for interface in wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True):
    ip_addresses = interface.IPAddress
    for ip_addr in ip_addresses:
        if ip_addr.startswith("10."):
            ip = ip_addr
            break
    if ip:
        break
if not ip:
    ip = "No detectada"

# ==== Discos ====
disks = wmi.WMI().Win32_LogicalDisk(DriveType=3)
disk_list = []
for disk in disks:
    size_gb = round(disk.Size / (1024 ** 3), 2)
    free_gb = round(disk.FreeSpace / (1024 ** 3), 2)
    disk_list.append(f"{disk.DeviceID}: {size_gb}GB total / {free_gb}GB libres")
discos = " | ".join(disk_list)

# ==== Monitores ====
mon_list = []
for monitor in wmi.WMI(namespace='root\\wmi').WmiMonitorID():
    manu = ''.join(chr(c) for c in monitor.ManufacturerName if c != 0)
    model = ''.join(chr(c) for c in monitor.ProductCodeID if c != 0)
    serial = ''.join(chr(c) for c in monitor.SerialNumberID if c != 0)
    mon_list.append(f"{manu} - Modelo: {model} - Serie: {serial}")
if not mon_list:
    mon_list = ["No detectado"]
mon_str = " | ".join(mon_list)

# ==== Software instalado general ====
all_software = []
for software in wmi.WMI().Win32_Product():
    all_software.append(software)

# ==== Office ====
office_keywords = ["Office", "Microsoft 365"]
office_obj = next((s for s in all_software if any(keyword in s.Name for keyword in office_keywords)), None)

if not office_obj:
    click_to_run = None
    try:
        click_to_run = wmi.WMI().Win32_Registry(RegistryPath="HKLM:\\SOFTWARE\\Microsoft\\Office\\ClickToRun\\Configuration")[0]
    except:
        pass
    if click_to_run:
        prod_id = click_to_run.ProductReleaseIds
        client_version = click_to_run.ClientVersionToReport
        product_name = {
            "ProPlus": "Microsoft Office Professional Plus",
            "O365ProPlus": "Microsoft Office 365 ProPlus",
            "HomeBusiness": "Microsoft Office Home and Business",
            "HomeStudent": "Microsoft Office Home and Student",
            "Standard": "Microsoft Office Standard",
            "Enterprise": "Microsoft Office Enterprise"
        }.get(prod_id, "Microsoft Office")
        year = {
            "16.0": "2016/2019/365",
            "15.0": "2013",
            "14.0": "2010"
        }.get(client_version.split('.')[0], "")
        office = f"{product_name} {year}" if year else product_name
    else:
        office = "No detectado"
else:
    office = office_obj.Name
if not office:
    office = "No detectado"

# ==== Antivirus ====
antivirus_keywords = ["Antivirus", "ESET", "Kaspersky", "McAfee", "Sophos", "Norton", "Bitdefender", "Trend Micro", "Symantec", "Panda", "Avast", "AVG", "F-Secure", "G Data", "Malwarebytes"]
antivirus_obj = next((s for s in all_software if any(keyword in s.Name for keyword in antivirus_keywords)), None)

antivirus = f"{antivirus_obj.Name} v{antivirus_obj.Version} - Publisher: {antivirus_obj.Vendor}" if antivirus_obj else "No detectado"

# ==== Otras Aplicaciones (excluyendo Office y Antivirus) ====
otras_apps_list = [s for s in all_software if s.Name not in office_keywords and s.Name not in antivirus_keywords]
otras_apps_texto = [f"{app.Name} v{app.Version}" if app.Version else app.Name for app in otras_apps_list]
otras_apps_resumen = " | ".join(sorted(otras_apps_texto)[:20])

# ==== Crear objeto de inventario ====
inventory = {
    "FechaRegistro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "NombreEquipo": hostname,
    "IP": ip,
    "SistemaOperativo": os_info.Caption,
    "Arquitectura": arch,
    "Fabricante": cs_info.Manufacturer,
    "Modelo": cs_info.Model,
    "BIOSSerial": bios_info.SerialNumber,
    "Procesador": cpu_info.Name,
    "Núcleos": cpu_info.NumberOfCores,
    "VelocidadMHz": cpu_info.MaxClockSpeed,
    "RAM_GB": ram_gb,
    "Discos": discos,
    "Monitores": mon_str,
    "Office": office,
    "Antivirus": antivirus,
    "OtrasAplicaciones": otras_apps_resumen,
    "CodigoPatrimonioCPU": codigo_cpu,
    "CodigoPatrimonioMonitor": codigo_monitor,
    "Area": area,
    "Usuario": usuario
}

# ==== Escribir CSV ====
if os.path.exists(csv_file):
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=inventory.keys())
        writer.writerow(inventory)
else:
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=inventory.keys())
        writer.writeheader()
        writer.writerow(inventory)

print(f"✅ Inventario actualizado en: {csv_file}")

# ==== Desconectar unidad temporal ====
subprocess.run(['net', 'use', temp_drive, '/delete', '/y'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)