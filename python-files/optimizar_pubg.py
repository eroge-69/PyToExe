import ctypes
import subprocess
import winreg
import configparser
import shutil
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Por favor, ejecuta este script como administrador.")
    exit()

# Establecer plan de energía a Alto Rendimiento
plans = subprocess.check_output("powercfg -l", shell=True).decode()
for line in plans.splitlines():
    if "Alto rendimiento" in line or "High Performance" in line:
        guid = line.split()[3]
        subprocess.run(f"powercfg -setactive {guid}", shell=True)
        print("Plan de energía establecido a Alto Rendimiento.")
        break
else:
    print("No se encontró el plan de energía de Alto Rendimiento. Créalo manualmente.")

# Modificar registro
key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\PriorityControl", 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(key, "Win32PrioritySeparation", 0, winreg.REG_DWORD, 26)
winreg.CloseKey(key)
print("Registro modificado: Win32PrioritySeparation establecido a 26.")

# Solicitar resolución del monitor
width = int(input("Ingresa el ancho de tu monitor (ejemplo, 1920): "))
height = int(input("Ingresa el alto de tu monitor (ejemplo, 1080): "))
custom_width = int(width * 0.9)
custom_height = height

# Localizar archivo INI
local_appdata = os.getenv("LOCALAPPDATA")
ini_path = os.path.join(local_appdata, "TslGame", "Saved", "Config", "WindowsNoEditor", "GameUserSettings.ini")
if not os.path.exists(ini_path):
    print("No se encontró GameUserSettings.ini. Asegúrate de que PUBG esté instalado.")
    exit()

# Crear copia de seguridad del archivo INI
backup_path = ini_path + ".backup"
shutil.copy(ini_path, backup_path)
print("Copia de seguridad de GameUserSettings.ini creada.")

# Modificar archivo INI
config = configparser.ConfigParser()
config.read(ini_path)

# Asegurar que las secciones existan
if '[/Script/TslGame.TslGameUserSettings]' not in config:
    config['[/Script/TslGame.TslGameUserSettings]'] = {}
if '[ScalabilityGroups]' not in config:
    config['[ScalabilityGroups]'] = {}

# Establecer resolución y otras configuraciones
settings = config['[/Script/TslGame.TslGameUserSettings]']
settings['ResolutionSizeX'] = str(custom_width)
settings['ResolutionSizeY'] = str(custom_height)
settings['LastUserConfirmedResolutionSizeX'] = str(custom_width)
settings['LastUserConfirmedResolutionSizeY'] = str(custom_height)
settings['DesiredScreenWidth'] = str(custom_width)
settings['DesiredScreenHeight'] = str(custom_height)
settings['bUseDesiredScreenHeight'] = 'True'
settings['FrameRateLimit'] = '0.000000'
settings['FullscreenMode'] = '0'
settings['ScreenScale'] = '100.000000'

# Establecer configuraciones de escalabilidad
scalability = config['[ScalabilityGroups]']
scalability['sg.ResolutionQuality'] = '100'
scalability['sg.ViewDistanceQuality'] = '2'
scalability['sg.AntiAliasingQuality'] = '0'
scalability['sg.ShadowQuality'] = '0'
scalability['sg.PostProcessQuality'] = '0'
scalability['sg.TextureQuality'] = '0'
scalability['sg.EffectsQuality'] = '0'
scalability['sg.FoliageQuality'] = '0'

# Escribir de vuelta al archivo INI
with open(ini_path, 'w') as configfile:
    config.write(configfile)

print("Optimizaciones aplicadas con éxito. Se guardó una copia de seguridad del archivo original como GameUserSettings.ini.backup")

print("\nOpcional: En Steam, haz clic derecho en PUBG -> Propiedades -> Opciones de Lanzamiento -> agrega '-koreanrating' para sangre verde y otros cambios.")