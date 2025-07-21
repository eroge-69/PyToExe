import subprocess, os

# Paths
mod_path = os.path.join(os.getcwd(), "modules")
persona_path = os.path.join(os.getcwd(), "persona")
config_path = os.path.join(os.getcwd(), "config")
legal_path = os.path.join(os.getcwd(), "legal")

def verify_file(path, label):
    if not os.path.isfile(path):
        print(f"❌ Missing {label}")
        return False
    print(f"✅ {label} detected.")
    return True

def launch_exe(file_name):
    exe_path = os.path.join(mod_path, file_name)
    if verify_file(exe_path, file_name):
        subprocess.run(exe_path)

def verify_assets():
    print("\n🔍 MythForge Sovereign Compiler initializing...")
    verify_file(os.path.join(config_path, "EngineConfig.ini"), "EngineConfig")
    verify_file(os.path.join(persona_path, "GarrickCrayton.persona"), "Persona Rig")
    verify_file(os.path.join(legal_path, "AssetAuthorLog.json"), "Asset Log")

def run_hall():
    launch_exe("MythForge_Editor.exe")

def run_metahumanoid():
    launch_exe("MetaHumanoid_Rig.exe")

# Execute flow
verify_assets()
run_hall()
run_metahumanoid()