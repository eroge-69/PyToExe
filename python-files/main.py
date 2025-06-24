import os
import shutil

# Paths
mods_dir = os.path.join(os.getcwd(), "mods")
ibrahim_dir = os.path.join(os.getcwd(), "ibrahim_mods")
backup_dir = os.path.join(os.getcwd(), ".mods")

# Ensure backup folder exists
os.makedirs(backup_dir, exist_ok=True)

# Replacement mapping: old → new
replacements = {
    "create-1.20.1-6.0.6.jar": "create-1.20.1-0.5.1.j.jar",
    "createcobblestone-1.4.5+forge-1.20.1-106.jar": "createcobblestone-1.4.2+forge-1.20.1-74.jar",
    "JadeAddons-1.20.1-Forge-5.5.0.jar": "JadeAddons-1.20.1-Forge-5.3.1.jar",
    "mechanicalbotania-1.0.2.jar": "mechanicalbotania-1.0.1.jar",
    "sliceanddice-forge-3.4.0.jar": "sliceanddice-forge-3.3.0.jar",
    "supplementaries-1.20-3.1.31.jar": "supplementaries-1.20-3.1.11.jar",
}

# Extra files to remove
extra_remove = [
    "create_enchantment_industry-1.3.3-for-create-6.0.6.jar",
    "createbetterfps-1.1.jar",
    "ShoulderSurfing-Forge-1.20.1-4.13.1.jar",
    "vivecraftcompat-1.20-1.5.0.jar"
]

# Files to add
mods_to_add = [
    "eureka-1201-1.5.1-beta.3.jar",
    "valkyrienskies-120-2.3.0-beta.7.jar"
]

def safe_move(src, dst):
    try:
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"Moved: {os.path.basename(src)}")
    except Exception as e:
        print(f"Error moving {src}: {e}")

def safe_copy(src, dst):
    try:
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"Copied: {os.path.basename(src)}")
    except Exception as e:
        print(f"Error copying {src}: {e}")

# Step 1: Move old mods from /mods to /.mods
for old_mod in list(replacements.keys()) + extra_remove:
    src = os.path.join(mods_dir, old_mod)
    dst = os.path.join(backup_dir, old_mod)
    safe_move(src, dst)

# Step 2: Archive any matching mods from ibrahim_mods
for old_mod in replacements.keys():
    src = os.path.join(ibrahim_dir, old_mod)
    dst = os.path.join(backup_dir, old_mod)
    safe_move(src, dst)

# Step 3: Copy desired downgraded or added mods from ibrahim_mods to /mods
for mod in list(replacements.values()) + mods_to_add:
    src = os.path.join(ibrahim_dir, mod)
    dst = os.path.join(mods_dir, mod)
    safe_copy(src, dst)

print("All tasks completed.")
