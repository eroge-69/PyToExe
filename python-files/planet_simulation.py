import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import json
import os

def load_rules(file_path='atmosphere_rules.json'):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load or parse atmosphere_rules.json: {e}")
        return None

def check_survivability(composition, pressure_atm, rules_data):
    if not rules_data: return (False, "Could not load atmosphere rules.")
    for rule in rules_data['survivability_rules']:
        if 'gas' in rule:
            gas_symbol = rule.get('gas')
            gas_percentage = composition.get(gas_symbol, 0)
            if rule['condition'] == 'less_than' and gas_percentage < rule['value']: return (False, rule['reason'])
            if rule['condition'] == 'greater_than' and gas_percentage > rule['value']: return (False, rule['reason'])
        elif 'pressure_atm' in rule:
            if rule['condition'] == 'less_than' and pressure_atm < rule['value']: return (False, rule['reason'])
            if rule['condition'] == 'greater_than' and pressure_atm > rule['value']: return (False, rule['reason'])
    return (True, "Survivable: Atmosphere is within all known human tolerances.")

class PlanetCreatorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Planet Configuration")
        self.rules = load_rules()
        if not self.rules:
            self.master.destroy()
            return

        # Styling
        style = ttk.Style(self.master)
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.master, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Widgets ---
        self.widgets = {}
        self._create_basic_info(main_frame, 0)
        self._create_atmosphere_info(main_frame, 1)
        self._create_ring_info(main_frame, 2)
        
        # --- Action Buttons & Status ---
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(action_frame, text="Ready.", font=('Helvetica', 10, 'italic'))
        self.status_label.pack(side=tk.LEFT, expand=True)

        create_button = ttk.Button(action_frame, text="Create Planet", command=self.create_planet)
        create_button.pack(side=tk.RIGHT)

    def _create_basic_info(self, parent, row):
        frame = ttk.LabelFrame(parent, text="Basic Information", padding="10")
        frame.grid(row=row, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(frame, text="Planet Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.widgets['name'] = ttk.Entry(frame, width=30)
        self.widgets['name'].insert(0, "New Terra")
        self.widgets['name'].grid(row=0, column=1)

        ttk.Label(frame, text="Radius (km):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.widgets['radius'] = ttk.Entry(frame, width=30)
        self.widgets['radius'].insert(0, "6371")
        self.widgets['radius'].grid(row=1, column=1)

        ttk.Label(frame, text="Rotation Speed:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.widgets['rotation'] = ttk.Entry(frame, width=30)
        self.widgets['rotation'].insert(0, "0.1")
        self.widgets['rotation'].grid(row=2, column=1)

    def _create_atmosphere_info(self, parent, row):
        frame = ttk.LabelFrame(parent, text="Atmosphere Composition", padding="10")
        frame.grid(row=row, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        self.gas_entries = {}
        gas_row = 0
        for symbol, info in self.rules['gases'].items():
            label_text = f"{info['name']} ({symbol.upper()}) %:"
            ttk.Label(frame, text=label_text).grid(row=gas_row, column=0, sticky=tk.W, pady=2)
            
            entry = ttk.Entry(frame, width=10)
            entry.insert(0, "0.0")
            entry.grid(row=gas_row, column=1, sticky=tk.W)
            entry.bind("<KeyRelease>", self.update_total_percentage)
            self.gas_entries[symbol] = entry
            gas_row += 1

        ttk.Separator(frame, orient='horizontal').grid(row=gas_row, columnspan=2, sticky='ew', pady=5)
        gas_row += 1

        self.total_label = ttk.Label(frame, text="Total: 0.0%", font=('Helvetica', 10, 'bold'))
        self.total_label.grid(row=gas_row, column=0, columnspan=2, sticky=tk.W)

        # Pre-fill with Earth-like values
        self.gas_entries['o2'].delete(0, tk.END); self.gas_entries['o2'].insert(0, "21.0")
        self.gas_entries['n2'].delete(0, tk.END); self.gas_entries['n2'].insert(0, "78.0")
        self.gas_entries['ar'].delete(0, tk.END); self.gas_entries['ar'].insert(0, "0.9")
        self.gas_entries['co2'].delete(0, tk.END); self.gas_entries['co2'].insert(0, "0.1")
        self.update_total_percentage()

        # Pressure
        ttk.Label(frame, text="Pressure (ATM):").grid(row=gas_row+1, column=0, sticky=tk.W, pady=(10,2))
        self.widgets['pressure'] = ttk.Entry(frame, width=10)
        self.widgets['pressure'].insert(0, "1.0")
        self.widgets['pressure'].grid(row=gas_row+1, column=1, sticky=tk.W, pady=(10,2))

    def _create_ring_info(self, parent, row):
        # Ring info can be simplified or expanded as needed
        pass

    def update_total_percentage(self, event=None):
        total = 0.0
        for entry in self.gas_entries.values():
            try:
                total += float(entry.get())
            except ValueError:
                pass # Ignore non-numeric input for now
        
        self.total_label.config(text=f"Total: {total:.2f}%")
        if abs(total - 100.0) > 0.01:
            self.total_label.config(foreground="red")
        else:
            self.total_label.config(foreground="green")

    def create_planet(self):
        try:
            # --- Validation and Data Gathering ---
            composition = {}
            for symbol, entry in self.gas_entries.items():
                composition[symbol] = float(entry.get())
            
            if abs(sum(composition.values()) - 100.0) > 0.01:
                self.status_label.config(text="Error: Gas percentages must sum to 100.")
                return

            pressure = float(self.widgets['pressure'].get())
            radius = float(self.widgets['radius'].get())
            rotation = float(self.widgets['rotation'].get())
            
            # --- Analysis ---
            is_survivable, reason = check_survivability(composition, pressure, self.rules)
            self.status_label.config(text=f"Analysis: {reason}")
            
            # --- JSON Creation ---
            data_to_save = {
                'name': self.widgets['name'].get(),
                'radius': radius / 10000.0,
                'rotationSpeed': rotation * (3.14159 / 180),
                'hasRings': False, # Simplified for this GUI version
                'isSurvivable': is_survivable,
                'atmospherePressure': pressure,
                'atmosphereComposition': composition
            }

            with open('planet_data.json', 'w') as f:
                json.dump(data_to_save, f, indent=4)
            
            messagebox.showinfo("Success", f"Planet '{data_to_save['name']}' created successfully!\n\n{reason}\n\nNow open the planet_3d.html file.")
            self.master.destroy()

        except ValueError:
            self.status_label.config(text="Error: Please ensure all fields are valid numbers.")
        except Exception as e:
            messagebox.showerror("An Error Occurred", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PlanetCreatorApp(root)
    root.mainloop()