
import os
import subprocess

def shell():
    while True:
        comando = input("@")
        if comando == "exit":
            break
        elif comando.startswith("run "):
            directory = comando[3:]
            try:
                os.chdir(directory)
            except FileNotFoundError:
                print(f"Directory '{directory}' non trovata.")
        else:
            try:
                subprocess.run(comando, shell=True)
            except Exception as e:
                print(f"Errore: {e}")


if __name__ == "__main__":
    print("bird shell®© 2025 Giuseppe Stancati")
    shell()