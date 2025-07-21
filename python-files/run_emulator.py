import subprocess
import os

# manual
# > emulator -avd Pixel_4_API_34 -no-snapshot-load

emulator_exe = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe")
list_cmd = [emulator_exe, "-list-avds"]

try:
    output = subprocess.check_output(list_cmd).decode().strip()
    avds = output.splitlines()

    if not avds:
        print("❌ No emulators found. Please create an AVD first.")
        exit(1)

    if len(avds) == 1:
        emulator_name = avds[0]
        print(f"✅ Only one emulator found, launching: {emulator_name}")
    else:
        print("Available emulators:")
        for idx, avd in enumerate(avds, 1):
            print(f"{idx}. {avd}")

        choice = input(f"\nChoose emulator to launch [1-{len(avds)}]: ")
        try:
            idx = int(choice) - 1
            if not (0 <= idx < len(avds)):
                print("❌ Invalid choice.")
                exit(1)
            emulator_name = avds[idx]
        except ValueError:
            print("❌ Invalid input.")
            exit(1)

    cmd = [
        emulator_exe,
        "-avd", emulator_name,
        "-gpu", "auto"
    ]

    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Emulator '{emulator_name}' launched successfully.")

except subprocess.CalledProcessError as e:
    print("❌ Failed to list emulators.")
    print(e)
