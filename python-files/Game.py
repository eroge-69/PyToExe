import time
import sys
import random

def print_progress(phase, progress):
    bar = '█' * (progress // 5) + '-' * (20 - progress // 5)
    sys.stdout.write(f"\r[{phase}] Progress: [{bar}] {progress}%")
    sys.stdout.flush()

def simulate_phase(phase_name, errors, duration):
    # Pre-phase “realistic” log dumps
    if phase_name == "VBSP":
        for line in [
            "Valve Software - vbsp 1.0.0.0 (Aug 4 2025)",
            "Command line: vbsp -game tf -meta -scale 1 pl_memevalley.vmf",
            "Reading map file 'pl_memevalley.vmf'...",
            "Parsing entity lumps...",
            "Writing BSP...",
            "Partitioning 5124 brushes..."
        ]:
            print(line)
            time.sleep(0.2)

    elif phase_name == "VVIS":
        for line in [
            "Valve Software - vvis 1.0.0.0",
            "3 threads for portal flow computation",
            "Reading BSP file 'pl_memevalley.bsp'...",
            "Building connectivity graph...",
            "Optimizing clusters..."
        ]:
            print(line)
            time.sleep(0.2)

    elif phase_name == "VRAD":
        for line in [
            "Valve Software - vrad 1.0.0.0",
            "HDR lighting enabled",
            "Computing direct lighting...",
            "Computing radiosity bounces...",
            "Gathering surface samples..."
        ]:
            print(line)
            time.sleep(0.2)

    print(f"\n🔧 Starting {phase_name} (approx. {duration}s)...")
    time.sleep(0.3)
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break

        progress = int((elapsed / duration) * 100)
        if progress > 100:
            progress = 100

        print_progress(phase_name, progress)
        time.sleep(0.1)

        # “1...2...3...” markers in VVIS/VRAD
        if phase_name == "VVIS" and random.random() < 0.05:
            for m in ["\n1...", "2...", "3..."]:
                sys.stdout.write(m)
                sys.stdout.flush()
                time.sleep(0.1)
        if phase_name == "VRAD" and random.random() < 0.05:
            for m in ["\n1...", "2...", "3...", "4..."]:
                sys.stdout.write(m)
                sys.stdout.flush()
                time.sleep(0.1)

        # Only trigger errors when progress is between 85% and 100%
        if progress >= 85 and random.random() < 0.08:
            error = random.choice(errors)
            print(f"\n{error}")
            print("⏳ Attempting auto-resolution...")
            time.sleep(random.uniform(1.0, 2.0))
            print("✅ Issue resolved.\n")
            print_progress(phase_name, 100)
            time.sleep(0.5)
            break

    actual = time.time() - start_time
    print(f"\n{phase_name} completed in {actual:.2f} seconds.\n")

def simulate_server_console():
    print("\n🖥️ Launching TF2 Source Dedicated Server...\n")
    time.sleep(0.3)
    lines = [
        "Server is hibernating",
        "Connection from 192.168.0.42:27015",
        "Client 'SniperMain' connected (STEAM_0:1:12345678)",
        "Loading map 'pl_memevalley.bsp'",
        "Initializing voice codec: Speex",
        "VAC secure mode activated",
        "Sending full update to client 'SniperMain'",
        "Player 'SniperMain' joined team RED",
        "Client 'PyroBot' connected (STEAM_0:0:87654321)",
        "Player 'PyroBot' joined team BLU",
        "Client 'HeavyWeaponsGuy' connected (STEAM_0:1:11223344)",
        "Player 'HeavyWeaponsGuy' joined team SPECTATOR",
        "Workshop item '987654321' mounted successfully",
        "Executing server.cfg...",
        "RCON command received: sv_cheats 1",
        "Client 'Scout420' connected (STEAM_0:0:99999999)",
        "Player 'Scout420' joined team RED",
        "Sending inventory snapshot to 'Scout420'",
        "Voice channel initialized for 'PyroBot'",
        "Client 'EngineerDad' connected (STEAM_0:1:55555555)",
        "Player 'EngineerDad' joined team BLU",
    ]
    errors = [
        "NET ERROR 0x802: Reliable channel overflow",
        "SCRIPT ERROR 0x3F1: Lua callback failed in 'custom_hats.lua'",
        "AUTH ERROR 0x108: Steam validation failed for client 'PyroBot'",
        "RESOURCE ERROR 0x2A0: Missing file 'materials/vgui/hud/healthbar.vmt'",
        "ENGINE ERROR 0x900: Entity 'func_respawnroomvisualizer' has no team",
        "VOICE ERROR 0xA11: Codec initialization failed for 'Scout420'",
        "MAP ERROR 0xB07: Navmesh missing for 'pl_memevalley.bsp'",
        "SECURITY ERROR 0xC00: VAC module timeout — reinitializing",
        "RCON ERROR 0xD42: Unauthorized command attempt from 192.168.0.99",
    ]

    for _ in range(50):
        if random.random() < 0.2:
            print(random.choice(errors))
            time.sleep(0.1)
        else:
            print(random.choice(lines))
            time.sleep(0.05)

def simulate_crash():
    print("\n💥 FATAL ERROR: Segmentation fault in module 'engine.dll' (Code 0xDEAD)")
    print("🧠 Dumping core to 'crash_2025_08_08.dmp'...")
    time.sleep(1.5)
    print("🔁 Restarting build environment...\n")
    time.sleep(2)

# Error pools
vbsp_errors = [
    "vbsp ERROR 0x101: Entity 'func_respawnroomvisualizer' has no associated team",
    "vbsp WARNING 0x102: Brush 1234 has non-convex geometry",
    "vbsp ERROR 0x103: Leak detected — pointfile generated",
    "vbsp ERROR 0x104: Entity 'info_player_teamspawn' missing team assignment",
    "vbsp WARNING 0x105: Overlapping brushes detected in sector 7G"
]

vvis_errors = [
    "vvis ERROR 0x201: Portal flow computation failed",
    "vvis WARNING 0x202: Map contains isolated clusters",
    "vvis ERROR 0x203: No valid visleafs found",
    "vvis ERROR 0x204: BSP tree traversal exceeded recursion limit",
    "vvis WARNING 0x205: Orphaned visgroup detected"
]

vrad_errors = [
    "vrad ERROR 0x301: No HDR lighting data found",
    "vrad WARNING 0x302: Lightmap scale too high — clamping",
    "vrad ERROR 0x303: Radiosity bounce failed on surface 5678",
    "vrad ERROR 0x304: Light entity 'light_env' missing target",
    "vrad WARNING 0x305: Texture 'dev_measurewall01' lacks reflectivity data"
]

compile_errors = [
    "COMPILE ERROR 0x401: Undefined reference to 'QuantumSingularityProtocol'",
    "COMPILE WARNING 0x402: Deprecated API usage in 'flux_core.cpp'",
    "COMPILE ERROR 0x403: Stack overflow detected in recursive loop",
    "COMPILE ERROR 0x404: Memory leak detected in 'neutrino_cache'",
    "COMPILE WARNING 0x405: Unused variable 'g_bIsUberReady'"
]

# Infinite loop with realistic durations:
# VBSP: 10s, VVIS: 38s, VRAD: 4m38s (278s), COMPILE: 8s
while True:
    simulate_phase("VBSP", vbsp_errors, duration=128)
    simulate_phase("VVIS", vvis_errors, duration=438)
    simulate_phase("VRAD", vrad_errors, duration=3278)
    simulate_phase("COMPILE", compile_errors, duration=224)
    simulate_server_console()
    simulate_crash()

