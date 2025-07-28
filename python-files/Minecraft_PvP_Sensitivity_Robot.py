
import tkinter as tk
from tkinter import messagebox
import time
import threading

class SensitivityTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft PvP Sensitivity Robot")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        self.instructions = tk.Label(root, text="Follow the moving dot with your mouse as smoothly as possible.\nYou have 15 seconds.\nTry to keep your cursor centered on the dot.", font=("Arial", 16))
        self.instructions.pack(pady=20)
        
        self.canvas = tk.Canvas(root, width=600, height=400, bg="black")
        self.canvas.pack(pady=20)
        
        self.dot = None
        self.dot_radius = 10
        self.positions = []
        self.tracking = False
        
        self.start_btn = tk.Button(root, text="Start Test", font=("Arial", 14), command=self.start_test)
        self.start_btn.pack(pady=10)
        
        self.result_label = tk.Label(root, text="", font=("Arial", 18))
        self.result_label.pack(pady=10)
        
        self.root.bind('<Motion>', self.track_mouse)
        self.dot_x, self.dot_y = 300, 200
        self.create_dot(self.dot_x, self.dot_y)
        
    def create_dot(self, x, y):
        if self.dot is not None:
            self.canvas.delete(self.dot)
        self.dot = self.canvas.create_oval(x-self.dot_radius, y-self.dot_radius, x+self.dot_radius, y+self.dot_radius, fill="red")
        
    def move_dot(self):
        import random
        for _ in range(75):  # moves dot every 0.2 seconds for 15 seconds total
            if not self.tracking:
                break
            new_x = min(max(50, self.dot_x + random.randint(-50, 50)), 550)
            new_y = min(max(50, self.dot_y + random.randint(-50, 50)), 350)
            self.dot_x, self.dot_y = new_x, new_y
            self.create_dot(new_x, new_y)
            time.sleep(0.2)
        self.tracking = False
        self.analyze_results()
        
    def start_test(self):
        if self.tracking:
            return
        self.positions.clear()
        self.tracking = True
        self.result_label.config(text="")
        threading.Thread(target=self.move_dot, daemon=True).start()
        
    def track_mouse(self, event):
        if self.tracking:
            self.positions.append((event.x, event.y))
        
    def analyze_results(self):
        # Calculate average distance from dot to mouse cursor
        if not self.positions:
            return
        distances = []
        for pos in self.positions:
            dx = pos[0] - self.dot_x
            dy = pos[1] - self.dot_y
            dist = (dx**2 + dy**2)**0.5
            distances.append(dist)
        avg_distance = sum(distances) / len(distances)
        
        # Calculate sensitivity recommendation based on avg_distance
        # Lower avg_distance means better tracking; suggest higher sensitivity
        # For office mouse ~800 DPI, sensitivity between 25% to 55%
        # Map avg_distance from 0-100 range inversely to 55%-25% sensitivity
        clamped_distance = min(max(avg_distance, 0), 100)
        sens = 55 - (clamped_distance / 100) * 30  # 55% to 25%
        sens = round(sens, 1)
        
        result_text = (f"Your average tracking distance: {avg_distance:.2f} px\n"
                       f"Recommended Minecraft sensitivity: {sens}%")
        self.result_label.config(text=result_text)
        messagebox.showinfo("Test Complete", result_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = SensitivityTester(root)
    root.mainloop()
