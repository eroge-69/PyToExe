import os, shutil

# === Configuration ===
ROOT_IN  = r"C:\Users\Abide\Desktop\Starfab_Exports"
ROOT_OUT = r"C:\Users\Abide\Desktop\Starfab_Selected"

# Keep only core performance/combat folders
FOLDERS = [
    "thrusters",
    "powerplant",
    "cooler",
    "shieldgenerator",
    "fueltanks",
    "fuel_intakes",
    "quantumdrive",
    "jumpdrive",
    "controller",
    "weapons",
    "missile_racks",
    "countermeasures",
    "armor",
    "radar",
]

def copytree(src, dst):
    if not os.path.exists(src):
        return False
    os.makedirs(dst, exist_ok=True)
    for root, _, files in os.walk(src):
        rel = os.path.relpath(root, src)
        outdir = os.path.join(dst, rel)
        os.makedirs(outdir, exist_ok=True)
        for f in files:
            shutil.copy2(os.path.join(root, f), os.path.join(outdir, f))
    return True

def main():
    ships = [d for d in os.listdir(ROOT_IN) if os.path.isdir(os.path.join(ROOT_IN, d))]
    print(f"Processing {len(ships)} ships (core folders only)...\n")
    for ship in ships:
        ship_src = os.path.join(ROOT_IN, ship, r"Data\Libs\Foundry\Records\Entities\SCItem\Ships")
        if not os.path.exists(ship_src):
            print(f"[!] Missing ship path: {ship}")
            continue

        ship_dst = os.path.join(ROOT_OUT, ship)
        os.makedirs(ship_dst, exist_ok=True)

        for folder in FOLDERS:
            src = os.path.join(ship_src, folder)
            dst = os.path.join(ship_dst, folder)
            if copytree(src, dst):
                print(f"[+] {ship}: Copied {folder}")
            else:
                print(f"[-] {ship}: No {folder}")
    print("\n✅ Done.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()