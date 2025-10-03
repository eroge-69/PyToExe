import tkinter as tk
from tkinter import ttk, messagebox
import random

# ----- Core mechanics -----

def roll_pool(pool, hunger, difficulty=None):
    if pool <= 0:
        raise ValueError("Pool must be >= 1")
    if hunger < 0:
        raise ValueError("Hunger must be >= 0")
    if hunger > pool:
        hunger = pool

    dice = [random.randint(1, 10) for _ in range(pool)]
    hunger_dice = dice[-hunger:] if hunger > 0 else []

    tens = [d for d in dice if d == 10]
    non_ten_successes = sum(1 for d in dice if 6 <= d <= 9)
    base_successes_from_tens = len(tens)
    crit_pairs = len(tens) // 2
    crit_bonus = crit_pairs * 2
    total_successes = non_ten_successes + base_successes_from_tens + crit_bonus

    messy_critical = crit_pairs > 0 and any(d == 10 for d in hunger_dice)
    is_success = None
    bestial_failure = False
    if difficulty is not None:
        is_success = total_successes >= difficulty
        bestial_failure = (not is_success) and any(d == 1 for d in hunger_dice)

    return {
        "dice": dice,
        "hunger_dice": hunger_dice,
        "successes": total_successes,
        "crit_pairs": crit_pairs,
        "messy": messy_critical,
        "bestial": bestial_failure,
        "difficulty": difficulty,
        "outcome": is_success
    }

def rouse_check():
    die = random.randint(1, 10)
    success = die >= 6
    return success, (0 if success else 1), die

# ----- Data model -----

ATTRIBUTES = [
    "Strength", "Dexterity", "Stamina",
    "Charisma", "Manipulation", "Composure",
    "Intelligence", "Wits", "Resolve"
]

SKILLS = [
    # Physical
    "Athletics", "Brawl", "Melee", "Firearms", "Stealth", "Survival",
    # Social
    "Insight", "Intimidation", "Persuasion", "Subterfuge", "Streetwise", "Etiquette",
    # Mental
    "Awareness", "Investigation", "Medicine", "Occult", "Science", "Technology"
]

class Character:
    def __init__(self, name, attributes=None, skills=None, hunger=0):
        self.name = name
        self.attributes = {a: 1 for a in ATTRIBUTES}
        self.skills = {s: 0 for s in SKILLS}
        if attributes:
            self.attributes.update(attributes)
        if skills:
            self.skills.update(skills)
        self.hunger = int(hunger)

    def pool(self, attribute, skill, modifiers=0):
        a = self.attributes.get(attribute, 0)
        s = self.skills.get(skill, 0)
        return max(1, a + s + modifiers)

# ----- UI App -----

class V5App:
    def __init__(self, root):
        self.root = root
        self.root.title("Vampire V5 GM Helper")

        self.characters = {}  # name -> Character

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_roller = ttk.Frame(self.notebook)
        self.tab_chars = ttk.Frame(self.notebook)
        self.tab_opposed = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_roller, text="Dice Roller")
        self.notebook.add(self.tab_chars, text="Characters")
        self.notebook.add(self.tab_opposed, text="Opposed Roll")

        self.build_roller_tab()
        self.build_character_tab()
        self.build_opposed_tab()

    # ----- Dice Roller Tab -----
    def build_roller_tab(self):
        frame = self.tab_roller

        # Inputs
        ttk.Label(frame, text="Dice Pool:").grid(row=0, column=0, sticky="w")
        self.pool_var = tk.IntVar(value=6)
        ttk.Entry(frame, textvariable=self.pool_var, width=6).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="Hunger:").grid(row=1, column=0, sticky="w")
        self.hunger_var = tk.IntVar(value=2)
        ttk.Entry(frame, textvariable=self.hunger_var, width=6).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Difficulty:").grid(row=2, column=0, sticky="w")
        self.diff_var = tk.IntVar(value=3)
        ttk.Entry(frame, textvariable=self.diff_var, width=6).grid(row=2, column=1, sticky="w")

        ttk.Button(frame, text="Roll", command=self.do_roll).grid(row=3, column=0, columnspan=2, pady=6)

        # Output
        self.output = tk.Text(frame, width=70, height=16, wrap="word")
        self.output.grid(row=4, column=0, columnspan=2, padx=6, pady=6)

    def do_roll(self):
        try:
            pool = self.pool_var.get()
            hunger = self.hunger_var.get()
            diff = self.diff_var.get()
            result = roll_pool(pool, hunger, diff)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        text = []
        text.append(f"Rolled {pool} dice (Hunger {hunger}) vs Difficulty {diff}")
        text.append(f"Dice: {result['dice']} | Hunger: {result['hunger_dice']}")
        text.append(f"Total Successes: {result['successes']}")
        if result['crit_pairs'] > 0:
            text.append(f"Criticals: {result['crit_pairs']} pair(s)")
        if result['messy']:
            text.append("Messy Critical!")
        if result['bestial']:
            text.append("Bestial Failure!")
        if result['outcome'] is not None:
            text.append("Outcome: " + ("SUCCESS" if result['outcome'] else "FAILURE"))

        self.output.insert("end", "\n".join(text) + "\n\n")
        self.output.see("end")

    # ----- Characters Tab -----
    def build_character_tab(self):
        frame = self.tab_chars
        frame.columnconfigure(2, weight=1)

        # Left: create/edit form
        form = ttk.LabelFrame(frame, text="Character sheet")
        form.grid(row=0, column=0, sticky="n", padx=6, pady=6)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        self.cs_name = tk.StringVar()
        ttk.Entry(form, textvariable=self.cs_name, width=22).grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Hunger").grid(row=0, column=2, sticky="e")
        self.cs_hunger = tk.IntVar(value=1)
        ttk.Entry(form, textvariable=self.cs_hunger, width=5).grid(row=0, column=3, sticky="w")

        # Attributes grid
        attr_frame = ttk.LabelFrame(form, text="Attributes")
        attr_frame.grid(row=1, column=0, columnspan=4, padx=4, pady=4, sticky="ew")
        self.attr_vars = {}
        r = 0
        for i, attr in enumerate(ATTRIBUTES):
            self.attr_vars[attr] = tk.IntVar(value=2 if attr in ("Dexterity", "Wits", "Resolve") else 1)
            ttk.Label(attr_frame, text=attr).grid(row=r, column=0, sticky="w")
            ttk.Spinbox(attr_frame, from_=0, to=5, textvariable=self.attr_vars[attr], width=4).grid(row=r, column=1, sticky="w")
            r += 1

        # Skills grid
        skill_frame = ttk.LabelFrame(form, text="Skills")
        skill_frame.grid(row=2, column=0, columnspan=4, padx=4, pady=4, sticky="ew")
        self.skill_vars = {}
        r = 0
        for s in SKILLS:
            self.skill_vars[s] = tk.IntVar(value=1 if s in ("Stealth", "Brawl", "Awareness") else 0)
            ttk.Label(skill_frame, text=s).grid(row=r, column=0, sticky="w")
            ttk.Spinbox(skill_frame, from_=0, to=5, textvariable=self.skill_vars[s], width=4).grid(row=r, column=1, sticky="w")
            r += 1

        # Buttons
        ttk.Button(form, text="Add / Update", command=self.add_update_character).grid(row=3, column=0, columnspan=2, pady=6)
        ttk.Button(form, text="Clear", command=self.clear_form).grid(row=3, column=2, columnspan=2, pady=6)

        # Right: list + actions
        right = ttk.LabelFrame(frame, text="Roster")
        right.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        frame.columnconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self.char_list = tk.Listbox(right, height=18)
        self.char_list.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.char_list.bind("<<ListboxSelect>>", self.populate_form_from_selection)

        # Roll from sheet
        sheet_actions = ttk.LabelFrame(right, text="Roll")
        sheet_actions.grid(row=1, column=0, sticky="ew", padx=4, pady=4)

        ttk.Label(sheet_actions, text="Attribute").grid(row=0, column=0, sticky="w")
        self.roll_attr = tk.StringVar(value=ATTRIBUTES[1])  # Dexterity
        ttk.Combobox(sheet_actions, values=ATTRIBUTES, textvariable=self.roll_attr, width=14, state="readonly").grid(row=0, column=1)

        ttk.Label(sheet_actions, text="Skill").grid(row=1, column=0, sticky="w")
        self.roll_skill = tk.StringVar(value="Stealth")
        ttk.Combobox(sheet_actions, values=SKILLS, textvariable=self.roll_skill, width=14, state="readonly").grid(row=1, column=1)

        ttk.Label(sheet_actions, text="Difficulty").grid(row=2, column=0, sticky="w")
        self.roll_diff = tk.IntVar(value=3)
        ttk.Entry(sheet_actions, textvariable=self.roll_diff, width=6).grid(row=2, column=1, sticky="w")

        ttk.Button(sheet_actions, text="Roll Test", command=self.roll_from_sheet).grid(row=3, column=0, columnspan=2, pady=6)
        ttk.Button(sheet_actions, text="Rouse Check", command=self.rouse_for_selected).grid(row=4, column=0, columnspan=2, pady=2)

        # Output
        self.sheet_output = tk.Text(right, width=50, height=12, wrap="word")
        self.sheet_output.grid(row=2, column=0, sticky="ew", padx=4, pady=4)

    def add_update_character(self):
        name = self.cs_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Character must have a name.")
            return

        attributes = {a: self.attr_vars[a].get() for a in ATTRIBUTES}
        skills = {s: self.skill_vars[s].get() for s in SKILLS}
        hunger = self.cs_hunger.get()

        self.characters[name] = Character(name, attributes, skills, hunger)
        self.refresh_roster()
        messagebox.showinfo("Saved", f"{name} saved/updated.")

    def clear_form(self):
        self.cs_name.set("")
        self.cs_hunger.set(1)
        for a in ATTRIBUTES:
            self.attr_vars[a].set(1)
        for s in SKILLS:
            self.skill_vars[s].set(0)

    def refresh_roster(self):
        self.char_list.delete(0, "end")
        for name in sorted(self.characters.keys()):
            self.char_list.insert("end", name)

    def populate_form_from_selection(self, event=None):
        sel = self.char_list.curselection()
        if not sel:
            return
        name = self.char_list.get(sel[0])
        c = self.characters.get(name)
        if not c:
            return
        self.cs_name.set(c.name)
        self.cs_hunger.set(c.hunger)
        for a in ATTRIBUTES:
            self.attr_vars[a].set(c.attributes.get(a, 0))
        for s in SKILLS:
            self.skill_vars[s].set(c.skills.get(s, 0))

    def get_selected_character(self):
        sel = self.char_list.curselection()
        if not sel:
            messagebox.showerror("Error", "Select a character first.")
            return None
        name = self.char_list.get(sel[0])
        return self.characters.get(name)

    def roll_from_sheet(self):
        c = self.get_selected_character()
        if not c:
            return
        attribute = self.roll_attr.get()
        skill = self.roll_skill.get()
        diff = self.roll_diff.get()

        pool = c.pool(attribute, skill)
        result = roll_pool(pool, c.hunger, difficulty=diff)

        lines = [
            f"{c.name}: {attribute} + {skill} (Pool {pool}, Hunger {c.hunger}) vs Diff {diff}",
            f"Dice: {result['dice']} | Hunger: {result['hunger_dice']}",
            f"Successes: {result['successes']}",
        ]
        if result["crit_pairs"] > 0:
            lines.append(f"Criticals: {result['crit_pairs']} pair(s)")
        if result["messy"]:
            lines.append("Messy Critical!")
        if result["bestial"]:
            lines.append("Bestial Failure!")
        lines.append("Outcome: " + ("SUCCESS" if result["outcome"] else "FAILURE"))

        self.sheet_output.insert("end", "\n".join(lines) + "\n\n")
        self.sheet_output.see("end")

    def rouse_for_selected(self):
        c = self.get_selected_character()
        if not c:
            return
        ok, delta, die = rouse_check()
        c.hunger = max(0, c.hunger + delta)
        self.cs_hunger.set(c.hunger)
        self.sheet_output.insert("end", f"{c.name} Rouse: d10={die} -> {'Success' if ok else 'Failure; Hunger +1'} (Hunger {c.hunger})\n\n")
        self.sheet_output.see("end")

    # ----- Opposed Tab -----
    def build_opposed_tab(self):
        frame = self.tab_opposed

        left = ttk.LabelFrame(frame, text="Side A")
        right = ttk.LabelFrame(frame, text="Side B")
        left.grid(row=0, column=0, padx=6, pady=6, sticky="n")
        right.grid(row=0, column=1, padx=6, pady=6, sticky="n")

        # A
        ttk.Label(left, text="Character").grid(row=0, column=0, sticky="w")
        self.a_name = tk.StringVar()
        self.a_combo = ttk.Combobox(left, values=[], textvariable=self.a_name, width=20, state="readonly")
        self.a_combo.grid(row=0, column=1)
        ttk.Label(left, text="Attribute").grid(row=1, column=0, sticky="w")
        self.a_attr = tk.StringVar(value="Wits")
        ttk.Combobox(left, values=ATTRIBUTES, textvariable=self.a_attr, width=16, state="readonly").grid(row=1, column=1)
        ttk.Label(left, text="Skill").grid(row=2, column=0, sticky="w")
        self.a_skill = tk.StringVar(value="Firearms")
        ttk.Combobox(left, values=SKILLS, textvariable=self.a_skill, width=16, state="readonly").grid(row=2, column=1)

        # B
        ttk.Label(right, text="Character").grid(row=0, column=0, sticky="w")
        self.b_name = tk.StringVar()
        self.b_combo = ttk.Combobox(right, values=[], textvariable=self.b_name, width=20, state="readonly")
        self.b_combo.grid(row=0, column=1)
        ttk.Label(right, text="Attribute").grid(row=1, column=0, sticky="w")
        self.b_attr = tk.StringVar(value="Strength")
        ttk.Combobox(right, values=ATTRIBUTES, textvariable=self.b_attr, width=16, state="readonly").grid(row=1, column=1)
        ttk.Label(right, text="Skill").grid(row=2, column=0, sticky="w")
        self.b_skill = tk.StringVar(value="Brawl")
        ttk.Combobox(right, values=SKILLS, textvariable=self.b_skill, width=16, state="readonly").grid(row=2, column=1)

        # Roll button and output
        ttk.Button(frame, text="Opposed Roll", command=self.do_opposed).grid(row=1, column=0, columnspan=2, pady=6)
        self.op_output = tk.Text(frame, width=72, height=12, wrap="word")
        self.op_output.grid(row=2, column=0, columnspan=2, padx=6, pady=6)

        # Keep combos in sync with roster
        frame.bind("<Visibility>", lambda e: self.refresh_opposed_combos())

    def refresh_opposed_combos(self):
        names = sorted(self.characters.keys())
        self.a_combo["values"] = names
        self.b_combo["values"] = names

    def do_opposed(self):
        a_name = self.a_name.get().strip()
        b_name = self.b_name.get().strip()
        if not a_name or not b_name:
            messagebox.showerror("Error", "Select both characters.")
            return
        if a_name == b_name:
            messagebox.showerror("Error", "Choose two different characters.")
            return
        a = self.characters.get(a_name)
        b = self.characters.get(b_name)
        a_pool = a.pool(self.a_attr.get(), self.a_skill.get())
        b_pool = b.pool(self.b_attr.get(), self.b_skill.get())

        res_a = roll_pool(a_pool, a.hunger, difficulty=None)
        res_b = roll_pool(b_pool, b.hunger, difficulty=None)
        margin = res_a["successes"] - res_b["successes"]

        lines = [
            f"A: {a.name} {self.a_attr.get()} + {self.a_skill.get()} (Pool {a_pool}, Hunger {a.hunger}) -> {res_a['successes']} successes",
            f"   Dice: {res_a['dice']} | Hunger: {res_a['hunger_dice']}" +
            (" | Messy" if res_a["messy"] else "") +
            (" | Bestial" if res_a["bestial"] else ""),
            f"B: {b.name} {self.b_attr.get()} + {self.b_skill.get()} (Pool {b_pool}, Hunger {b.hunger}) -> {res_b['successes']} successes",
            f"   Dice: {res_b['dice']} | Hunger: {res_b['hunger_dice']}" +
            (" | Messy" if res_b["messy"] else "") +
            (" | Bestial" if res_b["bestial"] else ""),
            f"Margin: {margin} -> " + ("A wins" if margin > 0 else ("B wins" if margin < 0 else "Tie"))
        ]
        self.op_output.insert("end", "\n".join(lines) + "\n\n")
        self.op_output.see("end")

# ----- Run app -----

if __name__ == "__main__":
    root = tk.Tk()
    app = V5App(root)
    root.mainloop()
