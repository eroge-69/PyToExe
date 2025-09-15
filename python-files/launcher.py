import subprocess
import threading
import json
import time
import sys
import os
from queue import Queue
import tkinter as tk
from tkinter import messagebox

class MinecraftLauncher:
    def __init__(self):
        self.java_process = None
        self.csharp_process = None
        self.running = False
        self.input_queue = Queue()
        self.world_data = {"chunks": {}, "player": {"x": 0, "y": 64, "z": 0, "yaw": 0, "pitch": 0}}
        
    def start_processes(self):
        """Avvia i processi Java e C#"""
        try:
            # Avvia GameCore Java
            self.java_process = subprocess.Popen(
                ["java", "GameCore"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Avvia Renderer C#
            self.csharp_process = subprocess.Popen(
                ["dotnet", "run", "--project", "Renderer.cs"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            print("✓ Processi avviati con successo")
            return True
            
        except Exception as e:
            print(f"❌ Errore nell'avvio dei processi: {e}")
            return False
    
    def handle_java_output(self):
        """Gestisce l'output dal processo Java"""
        while self.running and self.java_process:
            try:
                line = self.java_process.stdout.readline()
                if line:
                    data = json.loads(line.strip())
                    # Invia dati al renderer C#
                    if self.csharp_process:
                        self.csharp_process.stdin.write(json.dumps(data) + "\n")
                        self.csharp_process.stdin.flush()
                    # Aggiorna world data locale
                    self.world_data.update(data)
            except Exception as e:
                print(f"Errore lettura Java: {e}")
                break
    
    def handle_csharp_output(self):
        """Gestisce l'output dal processo C#"""
        while self.running and self.csharp_process:
            try:
                line = self.csharp_process.stdout.readline()
                if line:
                    data = json.loads(line.strip())
                    # Gestisci input utente dal renderer
                    if data.get("type") == "input":
                        self.process_input(data)
            except Exception as e:
                print(f"Errore lettura C#: {e}")
                break
    
    def process_input(self, input_data):
        """Processa input dell'utente e lo invia a Java"""
        try:
            # Converti input in comandi di gioco
            command = self.convert_input_to_command(input_data)
            if command and self.java_process:
                self.java_process.stdin.write(json.dumps(command) + "\n")
                self.java_process.stdin.flush()
        except Exception as e:
            print(f"Errore processing input: {e}")
    
    def convert_input_to_command(self, input_data):
        """Converte input utente in comandi per GameCore"""
        if input_data.get("action") == "move":
            return {
                "type": "player_move",
                "x": input_data.get("x", 0),
                "y": input_data.get("y", 64),
                "z": input_data.get("z", 0),
                "yaw": input_data.get("yaw", 0),
                "pitch": input_data.get("pitch", 0)
            }
        elif input_data.get("action") == "mine":
            return {
                "type": "break_block",
                "x": input_data.get("block_x"),
                "y": input_data.get("block_y"),
                "z": input_data.get("block_z")
            }
        elif input_data.get("action") == "place":
            return {
                "type": "place_block",
                "x": input_data.get("block_x"),
                "y": input_data.get("block_y"),
                "z": input_data.get("block_z"),
                "block_type": input_data.get("block_type", "stone")
            }
        return None
    
    def create_gui(self):
        """Crea una GUI semplice per controlli"""
        root = tk.Tk()
        root.title("Minecraft Clone Launcher")
        root.geometry("400x300")
        
        # Status
        status_label = tk.Label(root, text="Status: Ready", font=("Arial", 12))
        status_label.pack(pady=10)
        
        # Pulsante Start
        start_button = tk.Button(
            root, 
            text="Start Game", 
            command=self.start_game,
            font=("Arial", 14),
            bg="green",
            fg="white",
            width=20
        )
        start_button.pack(pady=10)
        
        # Pulsante Stop
        stop_button = tk.Button(
            root,
            text="Stop Game",
            command=self.stop_game,
            font=("Arial", 14),
            bg="red",
            fg="white",
            width=20
        )
        stop_button.pack(pady=10)
        
        # Info
        info_text = tk.Text(root, height=8, width=50)
        info_text.pack(pady=10)
        info_text.insert("1.0", "Minecraft Clone v1.0\n\nControls:\nWASD - Movement\nMouse - Look around\nLeft Click - Mine\nRight Click - Place\nESC - Menu\n\nFiles needed:\n- GameCore.java (compiled)\n- Renderer.cs")
        info_text.config(state=tk.DISABLED)
        
        return root
    
    def start_game(self):
        """Avvia il gioco"""
        if not self.running:
            if self.start_processes():
                self.running = True
                # Avvia thread per gestire I/O
                threading.Thread(target=self.handle_java_output, daemon=True).start()
                threading.Thread(target=self.handle_csharp_output, daemon=True).start()
                print("🎮 Gioco avviato!")
            else:
                messagebox.showerror("Errore", "Impossibile avviare i processi di gioco!")
    
    def stop_game(self):
        """Ferma il gioco"""
        self.running = False
        if self.java_process:
            self.java_process.terminate()
        if self.csharp_process:
            self.csharp_process.terminate()
        print("🛑 Gioco fermato!")
    
    def run(self):
        """Loop principale del launcher"""
        # Controlla se i file necessari esistono
        if not os.path.exists("GameCore.class"):
            print("❌ GameCore.class non trovato! Compila prima GameCore.java")
            return
        
        if not os.path.exists("Renderer.cs"):
            print("❌ Renderer.cs non trovato!")
            return
        
        print("🚀 Minecraft Clone Launcher v1.0")
        print("Files trovati ✓")
        
        # Modalità GUI
        root = self.create_gui()
        root.protocol("WM_DELETE_WINDOW", lambda: (self.stop_game(), root.destroy()))
        root.mainloop()

def main():
    launcher = MinecraftLauncher()
    try:
        launcher.run()
    except KeyboardInterrupt:
        print("\n🛑 Chiusura launcher...")
        launcher.stop_game()
    except Exception as e:
        print(f"❌ Errore fatale: {e}")

if __name__ == "__main__":
    main()