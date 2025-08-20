import subprocess
import sys
import shutil

def main():
    if not shutil.which("ngrok"):
        print("ngrok não instalado.")
        sys.exit(1)

    ngrok_command = [
        "ngrok", "http", "https://localhost:8686", "--domain=secure-seahorse-literally.ngrok-free.app"
    ]

    try:
        subprocess.Popen(ngrok_command, shell=True)
        print("ngrok inicializado")
    except Exception as e:
        print(e)
    
if __name__ == "__main__":
    main()