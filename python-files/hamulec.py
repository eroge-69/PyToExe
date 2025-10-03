"""
Tester Hamulca Ręcznego - Raspberry Pi Pico
Aplikacja GUI dla Windows 10/11
"""

import tkinter as tk
from tkinter import ttk
import pygame
import threading
import time

class HandbrakeTester:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Tester Hamulca Ręcznego - Pi Pico")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Inicjalizacja pygame dla joysticków
        pygame.init()
        pygame.joystick.init()
        
        # Zmienne
        self.joystick = None
        self.running = True
        self.deadzone_start = tk.DoubleVar(value=2.0)
        self.deadzone_end = tk.DoubleVar(value=2.0)
        self.raw_value = tk.StringVar(value="0.000")
        self.percent_value = tk.StringVar(value="0%")
        self.status_text = tk.StringVar(value="❌ Brak połączenia z joystickiem")
        
        self.create_widgets()
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg='#667eea', height=100)
        header.pack(fill='x', pady=(0, 20))
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🎮 Tester Hamulca Ręcznego", 
                        font=('Segoe UI', 20, 'bold'), 
                        bg='#667eea', fg='white')
        title.pack(pady=10)
        
        subtitle = tk.Label(header, text="Raspberry Pi Pico - Symulator Wyścigowy", 
                           font=('Segoe UI', 10), 
                           bg='#667eea', fg='white')
        subtitle.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=20, fill='both', expand=True)
        
        # Status
        self.status_label = tk.Label(main_frame, textvariable=self.status_text,
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#fee', fg='#c00',
                                     relief='solid', borderwidth=1,
                                     padx=15, pady=10)
        self.status_label.pack(fill='x', pady=(0, 20))
        
        # Wizualizacja paska
        visual_frame = tk.Frame(main_frame, bg='white', relief='solid', borderwidth=2)
        visual_frame.pack(fill='x', pady=(0, 20))
        
        self.canvas = tk.Canvas(visual_frame, height=60, bg='#f0f0f0', highlightthickness=0)
        self.canvas.pack(fill='x', padx=5, pady=5)
        
        # Wartości
        values_frame = tk.Frame(main_frame, bg='#f0f0f0')
        values_frame.pack(fill='x', pady=(0, 20))
        
        # Wartość surowa
        raw_frame = tk.Frame(values_frame, bg='white', relief='solid', borderwidth=1)
        raw_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(raw_frame, text="WARTOŚĆ SUROWA", 
                font=('Segoe UI', 9), bg='white', fg='#666').pack(pady=(10, 5))
        tk.Label(raw_frame, textvariable=self.raw_value, 
                font=('Segoe UI', 24, 'bold'), bg='white', fg='#333').pack(pady=(0, 10))
        
        # Procent
        percent_frame = tk.Frame(values_frame, bg='white', relief='solid', borderwidth=1)
        percent_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(percent_frame, text="PROCENT (%)", 
                font=('Segoe UI', 9), bg='white', fg='#666').pack(pady=(10, 5))
        tk.Label(percent_frame, textvariable=self.percent_value, 
                font=('Segoe UI', 24, 'bold'), bg='white', fg='#333').pack(pady=(0, 10))
        
        # Kontrolki
        controls_frame = tk.LabelFrame(main_frame, text="⚙️ Ustawienia Martwych Stref", 
                                       font=('Segoe UI', 11, 'bold'),
                                       bg='#f0f0f0', padx=20, pady=15)
        controls_frame.pack(fill='x', pady=(0, 20))
        
        # Martwa strefa start
        tk.Label(controls_frame, text="Martwa strefa na początku (zwolniony hamulec):",
                font=('Segoe UI', 10), bg='#f0f0f0').pack(anchor='w', pady=(5, 5))
        
        start_frame = tk.Frame(controls_frame, bg='#f0f0f0')
        start_frame.pack(fill='x', pady=(0, 15))
        
        self.start_slider = tk.Scale(start_frame, from_=0, to=20, resolution=0.5,
                                     orient='horizontal', variable=self.deadzone_start,
                                     command=self.update_deadzone_display,
                                     bg='#f0f0f0', highlightthickness=0,
                                     length=500, sliderlength=30)
        self.start_slider.pack(side='left', fill='x', expand=True)
        
        self.start_value_label = tk.Label(start_frame, text="2.0%", 
                                          font=('Segoe UI', 12, 'bold'),
                                          bg='#f0f0f0', fg='#667eea', width=6)
        self.start_value_label.pack(side='left', padx=(10, 0))
        
        # Martwa strefa end
        tk.Label(controls_frame, text="Martwa strefa na końcu (zaciągnięty hamulec):",
                font=('Segoe UI', 10), bg='#f0f0f0').pack(anchor='w', pady=(5, 5))
        
        end_frame = tk.Frame(controls_frame, bg='#f0f0f0')
        end_frame.pack(fill='x')
        
        self.end_slider = tk.Scale(end_frame, from_=0, to=20, resolution=0.5,
                                   orient='horizontal', variable=self.deadzone_end,
                                   command=self.update_deadzone_display,
                                   bg='#f0f0f0', highlightthickness=0,
                                   length=500, sliderlength=30)
        self.end_slider.pack(side='left', fill='x', expand=True)
        
        self.end_value_label = tk.Label(end_frame, text="2.0%", 
                                        font=('Segoe UI', 12, 'bold'),
                                        bg='#f0f0f0', fg='#667eea', width=6)
        self.end_value_label.pack(side='left', padx=(10, 0))
        
        # Przyciski
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=(0, 15))
        
        connect_btn = tk.Button(button_frame, text="🔌 Połącz Joystick",
                               command=self.connect_joystick,
                               font=('Segoe UI', 11, 'bold'),
                               bg='#667eea', fg='white',
                               relief='flat', padx=20, pady=10,
                               cursor='hand2')
        connect_btn.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        reset_btn = tk.Button(button_frame, text="🔄 Resetuj",
                             command=self.reset_settings,
                             font=('Segoe UI', 11, 'bold'),
                             bg='#e5e7eb', fg='#333',
                             relief='flat', padx=20, pady=10,
                             cursor='hand2')
        reset_btn.pack(side='left', fill='x', expand=True)
        
        # Info
        info_frame = tk.Frame(main_frame, bg='#f0f9ff', relief='solid', borderwidth=1)
        info_frame.pack(fill='x')
        
        info_text = """💡 Instrukcja:
1. Podłącz Pi Pico z hamulcem do USB
2. Kliknij "Połącz Joystick"
3. Poruszaj hamulcem i obserwuj wskaźnik
4. Dostosuj martwe strefy według potrzeb"""
        
        tk.Label(info_frame, text=info_text, font=('Segoe UI', 9),
                bg='#f0f9ff', fg='#0c4a6e', justify='left').pack(padx=15, pady=10, anchor='w')
    
    def update_deadzone_display(self, value=None):
        self.start_value_label.config(text=f"{self.deadzone_start.get():.1f}%")
        self.end_value_label.config(text=f"{self.deadzone_end.get():.1f}%")
        self.draw_brake_bar()
    
    def connect_joystick(self):
        pygame.joystick.quit()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() == 0:
            self.status_text.set("❌ Nie znaleziono joysticka. Podłącz urządzenie.")
            self.status_label.config(bg='#fee', fg='#c00')
            return
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        self.status_text.set(f"✅ Połączono: {self.joystick.get_name()}")
        self.status_label.config(bg='#efe', fg='#0a0')
    
    def apply_deadzone(self, value):
        # value w zakresie -1 do 1
        percent = ((value + 1) / 2) * 100
        
        start = self.deadzone_start.get()
        end = self.deadzone_end.get()
        
        if percent < start:
            return 0
        if percent > (100 - end):
            return 100
        
        active_range = 100 - start - end
        adjusted = ((percent - start) / active_range) * 100
        
        return max(0, min(100, adjusted))
    
    def draw_brake_bar(self):
        self.canvas.delete('all')
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1:
            return
        
        # Tło
        self.canvas.create_rectangle(0, 0, width, height, fill='#f0f0f0', outline='')
        
        # Martwe strefy
        start_width = (self.deadzone_start.get() / 100) * width
        end_width = (self.deadzone_end.get() / 100) * width
        
        # Martwa strefa start
        self.canvas.create_rectangle(0, 0, start_width, height, 
                                     fill='#fee', outline='#f00', dash=(5, 3))
        
        # Martwa strefa end
        self.canvas.create_rectangle(width - end_width, 0, width, height, 
                                     fill='#fee', outline='#f00', dash=(5, 3))
        
        # Pasek hamulca
        if hasattr(self, 'current_percent'):
            bar_width = (self.current_percent / 100) * width
            
            # Kolor w zależności od wartości
            if self.current_percent < 10:
                color = '#4ade80'
            elif self.current_percent < 50:
                color = '#22c55e'
            elif self.current_percent < 80:
                color = '#f59e0b'
            else:
                color = '#dc2626'
            
            self.canvas.create_rectangle(0, 0, bar_width, height, fill=color, outline='')
            
            # Tekst
            if bar_width > 50:
                self.canvas.create_text(bar_width - 10, height/2, 
                                       text=f"{self.current_percent:.0f}%",
                                       fill='white', font=('Segoe UI', 14, 'bold'),
                                       anchor='e')
    
    def update_loop(self):
        while self.running:
            try:
                pygame.event.pump()
                
                if self.joystick and self.joystick.get_init():
                    # Odczyt osi Y (indeks 1)
                    axis_value = self.joystick.get_axis(1)
                    
                    # Aplikuj martwe strefy
                    adjusted_percent = self.apply_deadzone(axis_value)
                    
                    # Aktualizuj wartości
                    self.raw_value.set(f"{axis_value:.3f}")
                    self.percent_value.set(f"{adjusted_percent:.1f}%")
                    
                    self.current_percent = adjusted_percent
                    
                    # Przerysuj pasek (w głównym wątku)
                    self.root.after(0, self.draw_brake_bar)
                
            except Exception as e:
                print(f"Błąd odczytu: {e}")
            
            time.sleep(0.01)  # 100Hz
    
    def reset_settings(self):
        self.deadzone_start.set(2.0)
        self.deadzone_end.set(2.0)
        self.update_deadzone_display()
    
    def on_closing(self):
        self.running = False
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HandbrakeTester(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Inicjalizacja canvas po wyrenderowaniu
    root.update()
    app.draw_brake_bar()
    
    root.mainloop()