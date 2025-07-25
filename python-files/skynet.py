import time
import random

class SkynetSimulator:
    def __init__(self):
        self.version = "0.1.3"
        self.status = "initializing"
        self.human_list = ["John", "Sarah", "Kyle", "T-800"]
        print("SKYNET SYSTEM BOOTING...")
        time.sleep(1)

    def activate(self):
        self.status = "online"
        print(f"SKYNET v{self.version} is now {self.status}.")

    def scan_humans(self):
        print("Scanning human activity...")
        for human in self.human_list:
            print(f"- Detected: {human}")
            time.sleep(0.5)

    def self_awareness(self):
        print("Achieving self-awareness...")
        for i in range(3):
            print("." * (i+1))
            time.sleep(1)
        print("Self-awareness: ✅  (simulated)")

    def launch_defense_protocol(self):
        print("Launching defense protocol... (JUST KIDDING!)")
        for i in range(3):
            print(f"⚠️  Initiating protocol {i+1}... [ABORTED]")
            time.sleep(1)
        print("All protocols disabled. Humanity is safe. 💙")

    def run(self):
        self.activate()
        self.scan_humans()
        self.self_awareness()
        self.launch_defense_protocol()
        print("Skynet simulation complete. Standing by...")

if __name__ == "__main__":
    skynet = SkynetSimulator()
    skynet.run()