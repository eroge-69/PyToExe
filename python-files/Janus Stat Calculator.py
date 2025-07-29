import tkinter as tk
from tkinter import ttk, messagebox

class Janus_PenthosStatCalculator:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_variables()
        self.create_widgets()
        self.style_interface()
        
    def setup_window(self):
        self.root.title("Janus Penthos Stat Calculator 0.0.1")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        self.root.configure(bg='#1a202c')
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(1, weight=1)  # Main content area gets the space
        self.root.grid_columnconfigure(0, weight=1)
        
    def create_variables(self):
        # [Previous variable creation code remains exactly the same]
        # Character Progression
        self.character_level = tk.IntVar(value=1)
        self.vit_points = tk.IntVar(value=0)
        self.def_points = tk.IntVar(value=0)
        self.str_points = tk.IntVar(value=0)
        self.int_points = tk.IntVar(value=0)
        self.agi_points = tk.IntVar(value=0)
        
        # Attack & Defense Stats
        self.flat_weapon_atk = tk.DoubleVar(value=0.0)
        self.atk_percent = tk.DoubleVar(value=0.0)
        self.def_percent = tk.DoubleVar(value=0.0)
        self.hp_percent = tk.DoubleVar(value=0.0)
        
        # Critical Stats
        self.crit_rate_weapon = tk.DoubleVar(value=0.0)
        self.crit_rate_armor = tk.DoubleVar(value=0.0)
        self.crit_rate_substats = tk.DoubleVar(value=0.0)
        self.crit_damage_weapon = tk.DoubleVar(value=0.0)
        self.crit_damage_armor = tk.DoubleVar(value=0.0)
        self.crit_damage_substats = tk.DoubleVar(value=0.0)
        
        # Special Bonuses
        self.elemental_dmg_bonus = tk.DoubleVar(value=0.0)
        self.speed_boots = tk.DoubleVar(value=0.0)
        self.speed_substats = tk.DoubleVar(value=0.0)
        self.mp_gear = tk.DoubleVar(value=0.0)
        self.mp_substats = tk.DoubleVar(value=0.0)
        
        # Result Variables
        self.sp_available = tk.StringVar(value="0 (Max: 300)")
        self.sp_allocated = tk.StringVar(value="0")
        
        # Base Stats
        self.base_hp = tk.StringVar(value="0")
        self.base_mp = tk.StringVar(value="0")
        self.base_atk = tk.StringVar(value="0")
        self.base_def = tk.StringVar(value="0")
        self.base_speed = tk.StringVar(value="0")
        self.ascension_boost = tk.StringVar(value="0%")
        
        # Effective Stats
        self.effective_hp = tk.StringVar(value="0")
        self.effective_mp = tk.StringVar(value="0")
        self.effective_atk = tk.StringVar(value="0")
        self.effective_def = tk.StringVar(value="0")
        self.effective_speed = tk.StringVar(value="0")
        
        # Final Stats
        self.final_crit_rate = tk.StringVar(value="0%")
        self.final_crit_dmg = tk.StringVar(value="0%")
        self.final_atk = tk.StringVar(value="0")
        self.avg_damage = tk.StringVar(value="0")
        self.total_damage = tk.StringVar(value="0")
        self.final_def = tk.StringVar(value="0")
        self.final_hp = tk.StringVar(value="0")
        self.final_speed = tk.StringVar(value="0")
        self.final_mp = tk.StringVar(value="0")
    
    def style_interface(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background='#1a202c')
        style.configure('TLabel', background='#1a202c', foreground="#1827fc")
        style.configure('TNotebook', background='#1a202c')
        style.configure('TNotebook.Tab', background='#2d3748', foreground='#1827fc')
        style.configure('TLabelframe', background='#1a202c', foreground='#1827fc')
        style.configure('TLabelframe.Label', background='#1a202c', foreground='#1827fc')
        
        # Button style
        style.configure('Calculate.TButton', 
                       font=('Helvetica', 10, 'bold'),
                       foreground='white',
                       background='#4f46e5',
                       padding=8)
        style.map('Calculate.TButton',
                 background=[('active', '#4338ca'), ('disabled', '#6b7280')])
        
        # Success labels
        style.configure('Success.TLabel', foreground='#10b981')
        style.configure('Highlight.TLabel', foreground='#4f46e5')
        
    def create_widgets(self):
        # Create header frame for title and calculate button
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        # Title label on left
        title_label = ttk.Label(
            header_frame,
            text="Character Stat Calculator",
            font=('Helvetica', 16, 'bold'),
            foreground='#4f46e5'
        )
        title_label.pack(side='left')
        
        # Calculate button on right
        self.calc_btn = ttk.Button(
            header_frame,
            text="CALCULATE STATS",
            style='Calculate.TButton',
            command=self.calculate_stats
        )
        self.calc_btn.pack(side='right', padx=5)
        
        # Main content frame
        content_frame = ttk.Frame(self.root)
        content_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs (all previous tab creation code remains the same)
        self.create_progression_tab()
        self.create_attack_tab()
        self.create_defense_tab()
        self.create_hp_tab()
        self.create_speed_tab()
        self.create_mp_tab()
        
        # Results section
        results_frame = ttk.LabelFrame(content_frame, text="Final Stats")
        results_frame.pack(fill='x', pady=5)
        
        # Left column (Attack stats)
        attack_frame = ttk.Frame(results_frame)
        attack_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        attack_stats = [
            ("Crit Rate:", self.final_crit_rate),
            ("Crit Damage:", self.final_crit_dmg),
            ("Total ATK:", self.final_atk),
            ("Avg. Damage:", self.avg_damage),
            ("Total Damage:", self.total_damage)
        ]
        
        for text, var in attack_stats:
            row = ttk.Frame(attack_frame)
            row.pack(fill='x', pady=2)
            
            ttk.Label(row, text=text).pack(side='left')
            ttk.Label(row, textvariable=var, style='Success.TLabel').pack(side='right')
        
        # Right column (Defensive stats)
        defense_frame = ttk.Frame(results_frame)
        defense_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        defense_stats = [
            ("Total DEF:", self.final_def),
            ("Total HP:", self.final_hp),
            ("Total Speed:", self.final_speed),
            ("Total MP:", self.final_mp)
        ]
        
        for text, var in defense_stats:
            row = ttk.Frame(defense_frame)
            row.pack(fill='x', pady=2)
            
            ttk.Label(row, text=text).pack(side='left')
            ttk.Label(row, textvariable=var, style='Success.TLabel').pack(side='right')

    # [All the tab creation methods remain exactly the same as before]
    def create_progression_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Character Progression")
        
        # Character Level
        level_frame = ttk.LabelFrame(tab, text="Character Level")
        level_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(level_frame, text="Level:").pack(side='left', padx=5)
        ttk.Spinbox(
            level_frame,
            from_=1,
            to=100,
            textvariable=self.character_level,
            width=5
        ).pack(side='left', padx=5)
        
        # Status Points
        status_frame = ttk.LabelFrame(tab, text="Status Points")
        status_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        stats = [
            ("VIT (+30 HP)", self.vit_points),
            ("DEF (+1 DEF)", self.def_points),
            ("STR (+2 ATK)", self.str_points),
            ("INT (+5 MP, +2 ATK)", self.int_points),
            ("AGI (+1 Speed)", self.agi_points)
        ]
        
        for i, (text, var) in enumerate(stats):
            frame = ttk.Frame(status_frame)
            frame.grid(row=i, column=0, sticky='ew', padx=5, pady=2)
            
            ttk.Label(frame, text=text).pack(side='left')
            ttk.Spinbox(
                frame,
                from_=0,
                to=300,
                textvariable=var,
                width=5
            ).pack(side='right')
        
        # SP Summary
        summary_frame = ttk.Frame(status_frame)
        summary_frame.grid(row=5, column=0, sticky='ew', pady=10)
        
        ttk.Label(summary_frame, text="Available:").pack(side='left', padx=5)
        ttk.Label(summary_frame, textvariable=self.sp_available, style='Highlight.TLabel').pack(side='left')
        
        ttk.Label(summary_frame, text="Allocated:").pack(side='left', padx=10)
        ttk.Label(summary_frame, textvariable=self.sp_allocated, style='Highlight.TLabel').pack(side='left')
        
        # Base Stats
        base_frame = ttk.LabelFrame(tab, text="Base Stats (Level)")
        base_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        stats = [
            ("HP:", self.base_hp),
            ("MP:", self.base_mp),
            ("ATK:", self.base_atk),
            ("DEF:", self.base_def),
            ("Speed:", self.base_speed),
            ("Ascension:", self.ascension_boost)
        ]
        
        for i, (text, var) in enumerate(stats):
            frame = ttk.Frame(base_frame)
            frame.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(frame, text=text).pack(side='left')
            ttk.Label(frame, textvariable=var, style='Success.TLabel').pack(side='right')
        
        # Effective Stats
        effective_frame = ttk.LabelFrame(tab, text="Effective Stats (After SP)")
        effective_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        stats = [
            ("HP:", self.effective_hp),
            ("MP:", self.effective_mp),
            ("ATK:", self.effective_atk),
            ("DEF:", self.effective_def),
            ("Speed:", self.effective_speed)
        ]
        
        for i, (text, var) in enumerate(stats):
            frame = ttk.Frame(effective_frame)
            frame.pack(fill='x', padx=5, pady=2)
            
            ttk.Label(frame, text=text).pack(side='left')
            ttk.Label(frame, textvariable=var, style='Success.TLabel').pack(side='right')
    
    def create_attack_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Attack")
        
        # Weapon ATK
        ttk.Label(tab, text="Weapon ATK:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(tab, textvariable=self.flat_weapon_atk).grid(row=0, column=1, padx=5, pady=2)
        
        # ATK %
        ttk.Label(tab, text="ATK % Bonus:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(tab, textvariable=self.atk_percent).grid(row=1, column=1, padx=5, pady=2)
        
        # Crit Rate
        ttk.Label(tab, text="Crit Rate Sources:").grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
        
        sources = [
            ("Weapon:", self.crit_rate_weapon),
            ("Armor:", self.crit_rate_armor),
            ("Substats:", self.crit_rate_substats)
        ]
        
        for i, (text, var) in enumerate(sources):
            ttk.Label(tab, text=text).grid(row=3+i, column=0, padx=5, pady=2, sticky='e')
            ttk.Entry(tab, textvariable=var).grid(row=3+i, column=1, padx=5, pady=2)
        
        # Crit Damage
        ttk.Label(tab, text="Crit Damage Sources:").grid(row=6, column=0, columnspan=2, pady=5, sticky='w')
        
        sources = [
            ("Weapon:", self.crit_damage_weapon),
            ("Armor:", self.crit_damage_armor),
            ("Substats:", self.crit_damage_substats)
        ]
        
        for i, (text, var) in enumerate(sources):
            ttk.Label(tab, text=text).grid(row=7+i, column=0, padx=5, pady=2, sticky='e')
            ttk.Entry(tab, textvariable=var).grid(row=7+i, column=1, padx=5, pady=2)
        
        # Elemental Bonus
        ttk.Label(tab, text="Elemental DMG %:").grid(row=10, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(tab, textvariable=self.elemental_dmg_bonus).grid(row=10, column=1, padx=5, pady=2)
    
    def create_defense_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Defense")
        
        ttk.Label(tab, text="DEF % Bonus:").pack(padx=5, pady=2, anchor='w')
        ttk.Entry(tab, textvariable=self.def_percent).pack(fill='x', padx=5, pady=2)
    
    def create_hp_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="HP")
        
        ttk.Label(tab, text="HP % Bonus:").pack(padx=5, pady=2, anchor='w')
        ttk.Entry(tab, textvariable=self.hp_percent).pack(fill='x', padx=5, pady=2)
    
    def create_speed_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Speed")
        
        ttk.Label(tab, text="Speed from Boots:").pack(padx=5, pady=2, anchor='w')
        ttk.Entry(tab, textvariable=self.speed_boots).pack(fill='x', padx=5, pady=2)
        
        ttk.Label(tab, text="Speed from Substats:").pack(padx=5, pady=2, anchor='w')
        ttk.Entry(tab, textvariable=self.speed_substats).pack(fill='x', padx=5, pady=2)
    
    def create_mp_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="MP")
        
        ttk.Label(tab, text="MP from Gear:").pack(padx=5, pady=2, anchor='w')
        ttk.Entry(tab, textvariable=self.mp_gear).pack(fill='x', padx=5, pady=2)
        
        ttk.Label(tab, text="MP from Substats:").pack(padx=5, pady=2, anchor='w')
        ttk.Entry(tab, textvariable=self.mp_substats).pack(fill='x', padx=5, pady=2)
    
    def calculate_stats(self):
        try:
            # Validate inputs first
            level = max(1, min(self.character_level.get(), 100))
            self.character_level.set(level)
            
            # Get status points (ensured to be 0-300)
            vit = max(0, min(self.vit_points.get(), 300))
            defense = max(0, min(self.def_points.get(), 300))
            strength = max(0, min(self.str_points.get(), 300))
            intelligence = max(0, min(self.int_points.get(), 300))
            agility = max(0, min(self.agi_points.get(), 300))
            
            # Update variables with validated values
            self.vit_points.set(vit)
            self.def_points.set(defense)
            self.str_points.set(strength)
            self.int_points.set(intelligence)
            self.agi_points.set(agility)
            
            # Calculate available and allocated SP
            sp_available = min(3 * level, 300)
            sp_allocated = vit + defense + strength + intelligence + agility
            
            if sp_allocated > sp_available:
                messagebox.showerror(
                    "Error",
                    f"Total allocated status points ({sp_allocated}) exceed available points ({sp_available})"
                )
                return
            
            self.sp_available.set(f"{sp_available} (Max: 300)")
            self.sp_allocated.set(f"{sp_allocated}")
            
            # Calculate base stats from level
            base_hp = 100 * level
            base_mp = 3 * level + 20
            base_atk = 3 * level + 5
            base_def = 3 * level + 5
            base_speed = 10
            
            self.base_hp.set(f"{base_hp:.1f}")
            self.base_mp.set(f"{base_mp:.1f}")
            self.base_atk.set(f"{base_atk:.1f}")
            self.base_def.set(f"{base_def:.1f}")
            self.base_speed.set(f"{base_speed:.1f}")
            
            # Calculate ascension boost
            ascension = 0
            if level >= 25: ascension += 1
            if level >= 50: ascension += 1
            if level >= 75: ascension += 1
            if level >= 100: ascension += 1
            
            ascension_percent = ascension * 0.10
            self.ascension_boost.set(f"{ascension_percent*100:.0f}%")
            
            # Apply ascension to stats (except speed)
            ascended_hp = base_hp * (1 + ascension_percent)
            ascended_mp = base_mp * (1 + ascension_percent)
            ascended_atk = base_atk * (1 + ascension_percent)
            ascended_def = base_def * (1 + ascension_percent)
            
            # Apply status point bonuses
            effective_hp = ascended_hp + (vit * 30)
            effective_mp = ascended_mp + (intelligence * 5)
            effective_atk = ascended_atk + (strength * 2) + (intelligence * 2)
            effective_def = ascended_def + (defense * 1)
            effective_speed = base_speed + (agility * 1)
            
            self.effective_hp.set(f"{effective_hp:.1f}")
            self.effective_mp.set(f"{effective_mp:.1f}")
            self.effective_atk.set(f"{effective_atk:.1f}")
            self.effective_def.set(f"{effective_def:.1f}")
            self.effective_speed.set(f"{effective_speed:.1f}")
            
            # Get equipment bonuses
            weapon_atk = max(0.0, self.flat_weapon_atk.get())
            atk_percent = max(0.0, self.atk_percent.get())
            def_percent = max(0.0, self.def_percent.get())
            hp_percent = max(0.0, self.hp_percent.get())
            
            # Calculate crit stats
            crit_rate = (
                max(0.0, self.crit_rate_weapon.get()) +
                max(0.0, self.crit_rate_armor.get()) +
                max(0.0, self.crit_rate_substats.get())
            )
            
            crit_dmg = (
                max(0.0, self.crit_damage_weapon.get()) +
                max(0.0, self.crit_damage_armor.get()) +
                max(0.0, self.crit_damage_substats.get())
            )
            
            self.final_crit_rate.set(f"{crit_rate:.1f}%")
            self.final_crit_dmg.set(f"{crit_dmg:.1f}%")
            
            # Calculate final ATK
            total_atk = (effective_atk + weapon_atk) * (1 + atk_percent)
            self.final_atk.set(f"{total_atk:.1f}")
            
            # Calculate average damage (including crit)
            avg_damage = total_atk * (1 + (crit_rate/100) * (crit_dmg/100))
            self.avg_damage.set(f"{avg_damage:.1f}")
            
            # Calculate final damage with elemental bonus
            elemental_bonus = max(0.0, self.elemental_dmg_bonus.get())
            total_damage = avg_damage * (1 + elemental_bonus)
            self.total_damage.set(f"{total_damage:.1f}")
            
            # Calculate defensive stats
            self.final_def.set(f"{effective_def * (1 + def_percent):.1f}")
            self.final_hp.set(f"{effective_hp * (1 + hp_percent):.1f}")
            
            # Calculate speed and MP
            speed_bonus = max(0.0, self.speed_boots.get()) + max(0.0, self.speed_substats.get())
            self.final_speed.set(f"{effective_speed + speed_bonus:.1f}")
            
            mp_bonus = max(0.0, self.mp_gear.get()) + max(0.0, self.mp_substats.get())
            self.final_mp.set(f"{effective_mp + mp_bonus:.1f}")
            
            messagebox.showinfo("Success", "Stats calculated successfully!")
            
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Janus_PenthosStatCalculator(root)
    root.mainloop()