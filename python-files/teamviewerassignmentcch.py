import subprocess

def execute_teamviewer_assignment(program_path):
    try:
        command = f'"{program_path}" assignment --id 0001CoABChAKWvWA3WYR7q05nbRccXToEigIACAAAgAJAHWjprbt24AcgaGsqmijZnx_dZEuvYJP46sMbRkCkGQGkD_FTBWZvupDpYLwCDKqttMxtpc8zVRTMqAXcZCOR2ESiglEr1t2_ndiFRTBkDVyGWXUP6X2U54xG3PBF3lie7xIAEQpODIfw=='
        subprocess.run(command, check=True, shell=True)
        print(f"Successfully executed TeamViewer assignment using {program_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute TeamViewer assignment using {program_path}: {e}")

def main():
    program_paths = [
        r"C:\Program Files (x86)\TeamViewer\TeamViewer.exe",
        r"C:\Program Files\TeamViewer\TeamViewer.exe"
    ]

    for path in program_paths:
        execute_teamviewer_assignment(path)

if __name__ == "__main__":
    main()
