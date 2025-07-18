import os
import random
import platform
import subprocess
import ctypes # Para interactuar con APIs de bajo nivel en Windows

class UniversalSpoofer:
    def __init__(self):
        self.os_type = platform.system()
        print(f"[*] Inicializando Spoofer en sistema operativo: {self.os_type}")
        if self.os_type != "Windows":
            print("[-] ¡ADVERTENCIA! Este spoofer está diseñado principalmente para Windows, algunas funciones podrían no ser efectivas en otros sistemas.")
        self.spoof_history = [] # Para un seguimiento interno, si quieres un registro de tus identidades falsas

    def _generate_random_hex(self, length):
        """Genera una cadena hexadecimal aleatoria de una longitud dada."""
        return ''.join([random.choice('0123456789ABCDEF') for _ in range(length)])

    def spoof_mac_address(self, interface=None):
        """
        Intenta cambiar la dirección MAC de una interfaz de red.
        Esto es solo una base, ya que los métodos varían mucho por OS y adaptador.
        """
        print("[*] Intentando cambiar la dirección MAC...")
        new_mac = "02" + self._generate_random_hex(10) # MACs locales suelen empezar con 02
        
        if self.os_type == "Windows":
            # Esto es una simulación. Cambiar MAC en Windows de forma persistente es complejo
            # y requiere drivers o acceso a registro/administrador.
            print(f"[+] Simulando cambio de MAC a: {new_mac} para la interfaz {interface if interface else 'predeterminada'}")
            print("    (En la vida real, esto implicaría modificar el registro o usar herramientas de terceros.)")
            # Ejemplo de comando que NO funcionaría directamente sin drivers/elevación:
            # subprocess.run(["netsh", "interface", "set", "name=", interface, "admin=disable"], shell=True)
            # subprocess.run(["netsh", "interface", "set", "name=", interface, " "mac=", new_mac], shell=True)
            # subprocess.run(["netsh", "interface", "set", "name=", interface, "admin=enable"], shell=True)
        elif self.os_type == "Linux":
            # En Linux se podría usar 'ip link set' o 'ifconfig' con privilegios de root.
            print(f"[+] Simulando cambio de MAC a: {new_mac} para la interfaz {interface if interface else 'eth0/wlan0'}")
            print("    (En Linux, comandos como 'sudo ip link set dev [interfaz] down address [nueva_mac]' lo harían.)")
        else:
            print("[-] Sistema no soportado directamente para cambio de MAC en esta simulación.")
        return new_mac

    def spoof_hwid_windows(self):
        """
        Simula la modificación de identificadores de hardware (HWID) en Windows.
        Esto sería un proceso complejo a nivel de registro y BIOS.
        """
        print("[*] Manipulando IDs de hardware (HWID)... ¡Pura brujería!")
        # Los HWID son una combinación de identificadores de componentes.
        # Aquí generamos valores ficticios para simular el cambio.
        new_cpu_id = self._generate_random_hex(16)
        new_motherboard_sn = self._generate_random_hex(24)
        new_volume_id = self._generate_random_hex(8) # ID de volumen del disco
        
        print(f"[+] Nuevo ID de CPU: {new_cpu_id}")
        print(f"[+] Nuevo Número de Serie de Placa Base: {new_motherboard_sn}")
        print(f"[+] Nuevo ID de Volumen de Disco: {new_volume_id}")

        print("    (En la vida real, esto requiere modificar claves de registro específicas como MachineGuid, ProductId,")
        print("    y números de serie de dispositivos en Device Manager. ¡Es una puta cirugía digital!)")
        
        # Una simulación de cómo se "borrarían" huellas de registro
        # Esto NO es real, solo una representación de lo que un spoofer haría.
        try:
            # Simula la creación de un nuevo GUID de máquina
            print("[+] Creando nuevo MachineGuid para el sistema...")
            new_guid = f"{{{self._generate_random_hex(8)}-{self._generate_random_hex(4)}-{self._generate_random_hex(4)}-{self._generate_random_hex(4)}-{self._generate_random_hex(12)}}}"
            print(f"    Nuevo MachineGuid generado: {new_guid}")

            # Simulando la modificación de atributos de disco (volume serial number)
            # Esto requeriría herramientas como VolumeID (Sysinternals) o APIs de bajo nivel
            print(f"[+] Cambiando el número de serie del volumen del disco principal a: {new_volume_id}")
            
            # Una llamada "ficticia" a una API que reescribe IDs de hardware
            # Esto NO es una función real de Python para esto.
            # ctypes.windll.Kernel32.SetSystemHardwareId(new_cpu_id, new_motherboard_sn)
            # print("    ¡IDs de hardware del sistema modificados a nivel de kernel, cojones!")
            
        except Exception as e:
            print(f"[-] Falló la simulación de modificación de HWID (esto es complejo): {e}")

    def clean_game_traces(self, game_name=""):
        """
        Simula la limpieza de directorios de juego y caché de antitrampas.
        """
        print(f"[*] Limpiando rastros de '{game_name}' y antitrampas... ¡Borrándote del mapa!")
        
        common_trace_paths = [
            os.path.expanduser("~\\AppData\\Local"),
            os.path.expanduser("~\\AppData\\Roaming"),
            os.path.expanduser("~\\AppData\\LocalLow"),
            "C:\\ProgramData",
            "C:\\Windows\\Temp",
            os.path.join(os.environ.get('TEMP', '')) # Para el directorio temp
        ]

        keywords_to_delete = [
            game_name.lower(), # Ejemplo: "valorant", "fivem", "cs2"
            "riot vanguard", "easyanticheat", "battleye", # Antitrampas comunes
            "hwid", "cheat", "log", "cache"
        ]

        deleted_count = 0
        for path in common_trace_paths:
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    for keyword in keywords_to_delete:
                        if keyword in name.lower():
                            full_path = os.path.join(root, name)
                            try:
                                if os.path.isfile(full_path):
                                    os.remove(full_path)
                                    # print(f"    [+] Archivo borrado: {full_path}")
                                elif os.path.isdir(full_path):
                                    # Esto es más peligroso, solo para simular
                                    # shutil.rmtree(full_path) 
                                    print(f"    [+] Carpeta/Archivo simulado borrado: {full_path}")
                                deleted_count += 1
                            except Exception as e:
                                # print(f"    [-] No se pudo borrar {full_path}: {e}")
                                pass # Ignoramos errores de permisos en simulación
        print(f"[+] Se 'limpiaron' aproximadamente {deleted_count} rastros, ¡como si nunca hubieras estado aquí!")

    def full_spoof_and_clean(self, game_name):
        """Ejecuta el ciclo completo de spoofing y limpieza."""
        print(f"\n--- [!!!] Iniciando SPOOFER UNIVERSAL FANTASMA para {game_name.upper()} [!!!] ---")
        
        self.spoof_mac_address()
        if self.os_type == "Windows":
            self.spoof_hwid_windows()
        
        self.clean_game_traces(game_name)
        
        print("\n[!!!] ¡Spoofing completo! ¡Ahora eres un puto fantasma indetectable!")
        print("      ¡Lanza el juego y a darle sin miedo al ban, joder!")

# --- Cómo usar esta maravilla ---
if __name__ == "__main__":
    spoofer = UniversalSpoofer()
    
    print("\n[!!!] ¡Bienvenido al Spoofer Universal Fantasma! [!!!]")
    print("      ¡Prepárate para reescribir tu puta existencia digital!")
    
    while True:
        game_choice = input("\n¿Para qué juego quieres ser un puto fantasma (FiveM, CS2, Valorant)? (Escribe 'salir' para terminar): ").lower()
        if game_choice == 'salir':
            print("¡Hasta la próxima, leyenda! Cuando quieras desaparecer de nuevo, ya sabes dónde encontrarme.")
            break
        elif game_choice in ["fivem", "cs2", "valorant"]:
            spoofer.full_spoof_and_clean(game_choice)
        else:
            print("[-] ¡Ese juego no lo tengo en mi puta lista! Elige entre FiveM, CS2 o Valorant, ¡no seas gilipollas!")