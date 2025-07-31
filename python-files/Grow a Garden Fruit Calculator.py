import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import math

# Fruit and mutation data
thelist = [
    ("Tranquil Bloom", 3.8, 84223),
    ("Easter Egg", 2.85, 2256),
    ("Moon Flower", 1.90, 8574),
    ("Star Fruit", 2.85, 13538),
    ("Pepper", 4.75, 7220),
    ("Grape", 2.85, 7085),
    ("Night Shade", 0.48, 3159),
    ("Mint", 0.95, 4738),
    ("Glowshroom", 0.70, 271),
    ("Blood Banana", 1.42, 5415),
    ("Beanstalk", 9.5, 25270),
    ("Coconut", 13.31, 361),
    ("Candy Blossom", 2.85, 90250),
    ("Carrot", 0.24, 18),
    ("Strawberry", 0.29, 14),
    ("Blueberry", 0.17, 18),
    ("Orange Tulip", 0.0499, 767),
    ("Tomato", 0.44, 27),
    ("Daffodil", 0.16, 903),
    ("Watermelon", 7.3, 2708),
    ("Pumpkin", 6.90, 3069),
    ("Mushroom", 25.9, 136278),
    ("Bamboo", 3.80, 3610),
    ("Apple", 2.85, 248),
    ("Corn", 1.90, 36),
    ("Cactus", 6.65, 3069),
    ("Cranberry", 0.95, 1805),
    ("Moon Melon", 7.6, 16245),
    ("Durian", 7.60, 6317),
    ("Peach", 1.90, 271),
    ("Cacao", 7.6, 10830),
    ("Moon Glow", 6.65, 18050),
    ("Dragon Fruit", 11.38, 4287),
    ("Mango", 14.28, 5866),
    ("Moon Blossom", 2.85, 60166),
    ("Raspberry", 0.71, 90),
    ("Eggplant", 4.75, 6769),
    ("Papaya", 2.86, 903),
    ("Celesti Berry", 1.90, 9025),
    ("Moon Mango", 14.25, 45125),
    ("Passion Fruit", 2.867, 3204),
    ("Soul Fruit", 23.75, 6994),
    ("Chocolate Carrot", 0.2616, 9928),
    ("Red Lolipop", 3.7988, 45125),
    ("Candy Sunflower", 1.428, 72200),
    ("Lotus", 18.99, 15343),
    ("Pineapple", 2.85, 1805),
    ("Hive", 7.59, 55955),
    ("Lilac", 2.846, 31588),
    ("Rose", 0.95, 4513),
    ("Foxglove", 1.9, 18050),
    ("Purple Dahlia", 11.4, 67688),
    ("Sunflower", 15.65, 144000),
    ("Pink Lily", 5.699, 58663),
    ("Nectarine", 2.807, 35000),
    ("Lavender", 0.25, 22563),
    ("Honey Suckle", 11.4, 90250),
    ("Venus Flytrap", 9.5, 76712),
    ("Nectar Shade", 0.75, 45125),
    ("Manuka", 0.289, 22563),
    ("Ember Lily", 11.40, 50138),
    ("Dandelion", 3.79, 45125),
    ("Lumira", 5.69, 76713),
    ("Crocus", 0.285, 27075),
    ("Sun Coil", 9.5, 72200),
    ("Bee Balm", 0.94, 16245),
    ("Nectar Thorn", 5.76, 30083),
    ("Violet Corn", 2.85, 45125),
    ("Bendboo", 17.09, 138988),
    ("Succulent", 4.75, 22563),
    ("Sugar Apple", 8.55, 43320),
    ("Cursed Fruit", 22.9, 15000),
    ("Cocovine", 13.3, 60166),
    ("Dragon Pepper", 5.69, 80000),
    ("Cauliflower", 4.74, 36),
    ("Avocado", 3.32, 80),
    ("Green Apple", 2.85, 271),
    ("Kiwi", 4.75, 2482),
    ("Banana", 1.42, 1805),
    ("Prickly Pear", 6.65, 6319),
    ("Feijoa", 9.50, 11733),
    ("Loquat", 6.17, 7220),
    ("Wild Carrot", 0.286, 22563),
    ("Pear", 2.85, 18050),
    ("Cantaloupe", 5.22, 30685),
    ("Parasol Flower", 5.7, 180500),
    ("Rosy Delight", 9.5, 62273),
    ("Elephant Ears", 17.1, 69492),
    ("Bell Pepper", 7.61, 4964),
    ("Aloe Vera", 5.22, 56858),
    ("Peace Lily", 0.5, 16666),
    ("Traveler's Fruit", 11.4, 48085),
    ("Delphinium", 0.285, 21660),
    ("Lily of the Valley", 5.69, 44331),
    ("Guanabana", 3.80, 63626),
    ("Pitcher Plant", 11.4, 28800),
    ("Rafflesia", 7.6, 3159),
    ("Liberty Lily", 6.176, 27075),
    ("Firework Flower", 19, 136278),
    ("Bone Blossom", 2.85, 180500),
    ("Horned Dinoshroom", 4.94, 67218),
    ("Firefly Fern", 4.75, 64980),
    ("Stone Bite", 0.94, 31545),
    ("Boneboo", 14.5, 131967),
    ("Paradise Petal", 2.61, 22563),
    ("Burning Bud", 11.40, 63175),
    ("Fossil Light", 3.79, 79420),
    ("Horse Tail", 2.85, 27075),
    ("Giant Pinecone", 5.14, 64980),
    ("Lingon Berry", 0.485, 31588),
    ("Grand Volcania", 6.65, 63676),
    ("Amber Spine", 5.7, 49638),
    ("Mono Blooma", 0.477, 19855),
    ("Serenity", 0.24, 31588),
    ("Soft Sunshine", 1.90, 40613),
    ("Taro Flower", 6.64, 108300),
    ("Spiked Mango", 14.25, 60919),
    ("Zen Rocks", 17.1, 135375),
    ("Hinomai", 9.5, 72200),
    ("Maple Apple", 2.85, 51521),
]


mutations = {
    "Rainbow": 50, "Gold": 20, "Shocked": 100, "Frozen": 10, "Wet": 2, "Chilled": 2,
    "Choc": 2, "Moonlit": 2, "Bloodlit": 4, "Celestial": 120, "Disco": 125,
    "Zombified": 25, "Plasma": 5, "Voidtouched": 135, "Pollinated": 3,
    "Honeyglazed": 5, "Dawnbound": 150, "Heavenly": 5, "Cooked": 10,
    "Burnt": 4, "Molten": 25, "Meteoric": 125, "Windstruck": 2, "Verdant": 4,
    "Paradisal": 100, "Sundried": 85, "Twisted": 5, "Galactic": 120,
    "Aurora": 90, "Cloudtouched": 5, "Drenched": 5, "Fried": 8, "Sandy": 3,
    "Amber": 10, "Clay": 5, "Ceramic": 30, "Ancientamber": 50, "Oldamber": 20,
    "Friendbound": 70, "Tempestous": 12, "Infected": 75, "Tranquil": 20,
    "Chakra": 15, "Toxic": 12, "Radioactive": 80, "Foxfire": 90,
    "Harmonisedfoxfire": 190, "Corrupt": 20, "Jackpot": 15, "Subzero": 40,
    "Blitzshock": 50, "Touchdown": 105, "Static": 8, "Harmonisedchakra": 35
}

def enforce_mutation_rules(name, mv_dict):
    if mv_dict[name].get():
        exclusive_groups = [
            ["Rainbow", "Gold"],
            ["Wet", "Drenched"],
            ["Ancientamber", "Oldamber", "Amber"],
            ["Foxfire", "Harmonisedfoxfire"],
            ["Chakra", "Harmonisedchakra"],
            ["Drenched", "Frozen", "Wet", "Chilled"],
            ["Verdant", "Paradisal", "Sundried"],
        ]
        for group in exclusive_groups:
            if name in group:
                for g in group:
                    if g != name:
                        mv_dict[g].set(0)


root = tk.Tk()
root.title("Fruit Mutation Calculator")
root.geometry("350x300")
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Reusable display updater for fruits and mutations
def build_search_section(tab, fruit_mode=True):
    selected = tk.StringVar()
    mv_dict = {name: tk.IntVar() for name in mutations}

    fruit_frame = ttk.Frame(tab)
    fruit_frame.pack(pady=5)
    ttk.Label(fruit_frame, text="Search Fruit:").pack(side="left")
    fruit_var = tk.StringVar()
    fruit_entry = ttk.Entry(fruit_frame, textvariable=fruit_var, width=30)
    fruit_entry.pack(side="left", padx=5)
    fruit_result = ttk.Frame(tab)
    fruit_result.pack()

    def update_fruit_display(*_):
        for widget in fruit_result.winfo_children(): widget.destroy()
        query = fruit_var.get().lower()
        sorted_fruits = sorted([f[0] for f in thelist])
        display = sorted_fruits[:3] if query == "" else [f for f in sorted_fruits if f.lower().startswith(query)][:3]
        for i, name in enumerate(display):
            b = ttk.Button(fruit_result, text=name, command=lambda n=name: selected.set(n))
            b.grid(row=0, column=i, padx=5, pady=2, sticky="w")

    fruit_var.trace_add("write", update_fruit_display)

    search_frame = ttk.Frame(tab)
    search_frame.pack(pady=(10, 0))
    search_var = tk.StringVar()
    ttk.Label(search_frame, text="Search Mutations:").pack(side="left")
    ttk.Entry(search_frame, textvariable=search_var, width=20).pack(side="left", padx=5)

    mut_frame = ttk.Frame(tab)
    mut_frame.pack(pady=5, fill="x")

    def update_mut_display(*_):
        for widget in mut_frame.winfo_children(): widget.destroy()
        query = search_var.get().lower()
        sorted_mut = sorted(mutations.keys())
        display = sorted_mut[:4] if query == "" else [m for m in sorted_mut if m.lower().startswith(query)][:3]
        for i, m in enumerate(display):
            cb = ttk.Checkbutton(mut_frame, text=m, variable=mv_dict[m], command=lambda mn=m: enforce_mutation_rules(mn, mv_dict))
            cb.grid(row=0, column=i, padx=5, sticky="w")

    search_var.trace_add("write", update_mut_display)
    return selected, mv_dict, fruit_var

# --- Value Calculator Tab ---
calc_tab = ttk.Frame(notebook)
notebook.add(calc_tab, text="Value Calculator")
selected_fruit, mv, fruit_search_var = build_search_section(calc_tab, fruit_mode=True)

# Weight input (label to the left)
weight_frame = ttk.Frame(calc_tab)
weight_frame.pack(pady=5)
ttk.Label(weight_frame, text="Weight:").pack(side="left", padx=(0, 5))
weight_entry = ttk.Entry(weight_frame, width=10)
weight_entry.pack(side="left")

value_result = tk.Text(calc_tab, height=2, width=60, state="disabled")
value_result.pack(pady=5)

def calculate():
    value_result.config(state="normal")
    value_result.delete(1.0, tk.END)
    
    # Get the current font of the Text widget
    current_font = tkfont.Font(font=value_result['font'])
    # Create a larger font based on the current one
    larger_font = tkfont.Font(family=current_font.actual('family'),
                              size=current_font.actual('size') + 4,
                              weight=current_font.actual('weight'),
                              slant=current_font.actual('slant'),
                              underline=current_font.actual('underline'),
                              overstrike=current_font.actual('overstrike'))
    
    # Configure a tag for larger, centered text
    value_result.tag_configure("larger_centered", font=larger_font, justify="center")
    
    fname = selected_fruit.get()
    try:
        weight = float(weight_entry.get())
    except ValueError:
        value_result.insert(tk.END, "Invalid weight.\n", "larger_centered")
        value_result.config(state="disabled")
        return
    data = next((f for f in thelist if f[0] == fname), None)
    if not data:
        value_result.insert(tk.END, "Fruit not found.\n", "larger_centered")
        value_result.config(state="disabled")
        return
    _, v1, v3 = data
    weight = max(weight, v1)
    base = ((weight / v1) ** 2) * v3
    gmult = 1
    for g in ("Rainbow", "Gold"):
        if mv[g].get():
            gmult *= mutations[g]
    others = [mutations[m] for m in mutations if m not in ("Rainbow", "Gold") and mv[m].get()]
    total_mult = 1 + sum(others) - len(others) if others else 1
    final = int(base * gmult * total_mult + 0.5)
    
    # Insert result with the centered and larger font tag
    value_result.insert(tk.END, f"≈${final:,}", "larger_centered")
    
    # Apply center alignment for the entire line
    value_result.tag_add("larger_centered", "1.0", "end")
    
    value_result.config(state="disabled")



ttk.Button(calc_tab, text="Calculate Sell Price", command=calculate).pack(pady=10)

# --- Weight Calculator Tab ---
weight_tab = ttk.Frame(notebook)
notebook.add(weight_tab, text="Weight Calculator")
selected_fruit_w, mv_w, fruit_search_var_w = build_search_section(weight_tab, fruit_mode=True)

# Sell Price input (label to the left)
sell_frame = ttk.Frame(weight_tab)
sell_frame.pack(pady=5)
ttk.Label(sell_frame, text="Sell Price:").pack(side="left", padx=(0, 5))
sell_entry = ttk.Entry(sell_frame, width=10)
sell_entry.pack(side="left")

weight_result = tk.Text(weight_tab, height=2, width=60, state="disabled")
weight_result.pack(pady=5)

import tkinter.font as tkfont
import math

def calculate_weight():
    weight_result.config(state="normal")
    weight_result.delete(1.0, tk.END)
    
    current_font = tkfont.Font(font=weight_result['font'])
    larger_font = tkfont.Font(family=current_font.actual('family'),
                              size=current_font.actual('size') + 4,
                              weight=current_font.actual('weight'),
                              slant=current_font.actual('slant'),
                              underline=current_font.actual('underline'),
                              overstrike=current_font.actual('overstrike'))
    
    weight_result.tag_configure("larger_centered", font=larger_font, justify="center")
    
    fname = selected_fruit_w.get()
    try:
        sell_price = float(sell_entry.get())
    except ValueError:
        weight_result.insert(tk.END, "Invalid price.\n", "larger_centered")
        weight_result.config(state="disabled")
        return
    data = next((f for f in thelist if f[0] == fname), None)
    if not data:
        weight_result.insert(tk.END, "Fruit not found.\n", "larger_centered")
        weight_result.config(state="disabled")
        return
    _, v1, v3 = data
    gmult = 1
    for g in ("Rainbow", "Gold"):
        if mv_w[g].get():
            gmult *= mutations[g]
    others = [mutations[m] for m in mutations if m not in ("Rainbow", "Gold") and mv_w[m].get()]
    total_mult = 1 + sum(others) - len(others) if others else 1
    if v3 * gmult * total_mult == 0:
        weight_result.insert(tk.END, "Invalid multiplier.", "larger_centered")
        weight_result.config(state="disabled")
        return
    val = sell_price / (v3 * gmult * total_mult)
    weight = max(v1, v1 * math.sqrt(val))
    
    weight_result.insert(tk.END, f"{weight:.4f} kg", "larger_centered")
    weight_result.tag_add("larger_centered", "1.0", "end")
    
    weight_result.config(state="disabled")


ttk.Button(weight_tab, text="Calculate Weight", command=calculate_weight).pack(pady=10)

# Always on top toggle
always_on_top_var = tk.BooleanVar(value=False)
def toggle_top():
    root.attributes('-topmost', always_on_top_var.get())

ttk.Checkbutton(
    root, text="Always on Top", variable=always_on_top_var,
    command=toggle_top
).place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

root.mainloop()
