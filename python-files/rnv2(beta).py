import subprocess
import os
import psutil  # Para detectar Ethernet

# Archivo de salida
archivo_salida = "wifi_claves.txt"

def conexion_actual():
    # Detectar WiFi
    try:
        estado = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        ssid_actual = None
        for line in estado.stdout.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid_actual = line.split(":")[1].strip()
                if ssid_actual:
                    # Obtener contraseña de esa WiFi
                    contrasena = "SIN CONTRASEÑA"
                    try:
                        detalle = subprocess.run(
                            ["netsh", "wlan", "show", "profile", ssid_actual, "key=clear"],
                            capture_output=True, text=True, encoding="utf-8", errors="ignore"
                        )
                        for l in detalle.stdout.splitlines():
                            if "Contenido de la clave" in l:
                                contrasena = l.split(":")[1].strip()
                    except:
                        pass
                    return f"WiFi / {ssid_actual} / {contrasena}"
    except:
        pass

    # Detectar Ethernet si WiFi no está conectado
    for iface, addrs in psutil.net_if_addrs().items():
        if "Ethernet" in iface or "Local Area Connection" in iface:
            stats = psutil.net_if_stats().get(iface)
            if stats and stats.isup:
                return "Ethernet / Conectado"

    return "Desconectado"

def listar_redes_y_guardar():
    perfiles = []

    # Obtener perfiles WiFi (español o inglés)
    try:
        resultado = subprocess.run(
            ["netsh", "wlan", "show", "profiles"],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        )
        for line in resultado.stdout.splitlines():
            if "Perfil de todos los usuarios" in line or "All User Profile" in line:
                ssid = line.split(":")[1].strip()
                perfiles.append(ssid)
    except:
        pass

    actual = conexion_actual()

    # Mostrar arriba “Conexión actual:” como pediste
    print(f"\n🌐 Conexión actual: {actual}\n")

    contenido = []
    contenido.append(f"Conexión actual: {actual}\n")
    contenido.append("🔑 Redes guardadas:\n")

    # Mostrar red actual aunque no tenga perfil
    if actual.startswith("WiFi"):
        ssid_actual = actual.split(" / ")[1]
        if ssid_actual not in perfiles:
            contrasena = actual.split(" / ")[2]
            linea = f"{ssid_actual} / {contrasena} / ONLINE"
            contenido.append(linea)
            print(linea)

    # Listar todos los perfiles guardados
    for ssid in perfiles:
        contrasena = "SIN CONTRASEÑA"
        try:
            detalle = subprocess.run(
                ["netsh", "wlan", "show", "profile", ssid, "key=clear"],
                capture_output=True, text=True, encoding="utf-8", errors="ignore"
            )
            for line in detalle.stdout.splitlines():
                if "Contenido de la clave" in line:
                    contrasena = line.split(":")[1].strip()
        except:
            pass
        estado = "ONLINE" if actual.startswith("WiFi") and ssid == actual.split(" / ")[1] else "OFFLINE"
        linea = f"{ssid} / {contrasena} / {estado}"
        contenido.append(linea)
        print(linea)

    # Guardar en archivo
    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(contenido))
    print(f"\n✅ Información guardada en {archivo_salida}")

def crear_bat():
    bat_contenido = f"""@echo off
python "{os.path.basename(__file__)}"
pause
"""
    bat_nombre = "abrir_rev_practicante.bat"
    with open(bat_nombre, "w", encoding="utf-8") as f:
        f.write(bat_contenido)
    print(f"✅ Archivo BAT creado: {bat_nombre}")
    print("💡 Doble clic en este BAT para ejecutar el script sin que se cierre la ventana.")

if __name__ == "__main__":
    listar_redes_y_guardar()
    crear_bat()
    input("\nPresiona Enter para salir...")
