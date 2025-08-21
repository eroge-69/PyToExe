#!/usr/bin/env python3
"""
Minecraft Bedrock Mod Maker (No‑Code)
Author: ChatGPT (GPT‑5 Thinking)

⚡ What this app does
- Lets you create simple Bedrock add‑ons (items + crafting recipes) with a GUI — no coding.
- Exports a single .mcaddon file you can import into Minecraft Bedrock (Windows 10, Mobile, Console*).
  *Console import steps may differ.

✅ Features (v1.0)
- Set pack name, description, and author.
- Add unlimited custom items with: in‑game name, ID, max stack size, category, attack damage, and a PNG texture.
- Optional shapeless crafting recipes for each item.
- Generates valid Resource Pack (RP) + Behavior Pack (BP) with manifests.
- Bundles both into a single .mcaddon you can double‑click to import.

🛠 Requirements
- Python 3.8+
- No external libraries needed (uses only the Python standard library).

📦 Output
- A .mcaddon file is saved into an "exports/" folder next to this script.

🧭 How to run
- Windows: Right‑click this file > Open with > Python, or run `python mod_maker.py`
- macOS/Linux: `python3 mod_maker.py`

"""
import json
import os
import re
import shutil
import sys
import tempfile
import uuid
import zipfile
from dataclasses import dataclass, asdict, field
from datetime import datetime
from tkinter import (
    Tk, Toplevel, StringVar, IntVar, DoubleVar, BooleanVar,
    ttk, filedialog, messagebox, END, N, S, E, W
)

APP_TITLE = "Minecraft Bedrock Mod Maker (No‑Code)"
APP_VERSION = "1.0"

# -----------------------------
# Data models
# -----------------------------
@dataclass
class Recipe:
    enabled: bool = False
    # Shapeless crafting: list of minecraft:item IDs like "minecraft:stick" or custom IDs
    ingredients: list = field(default_factory=list)
    count: int = 1

@dataclass
class Item:
    name: str = ""              # Display name in game, e.g., "Titan Ingot"
    identifier: str = ""        # Short id, e.g., "titan_ingot" (will become "your_namespace:titan_ingot")
    texture_path: str = ""      # Path to PNG texture chosen by user
    max_stack: int = 64
    category: str = "items"     # creative category hint (items, equipment, nature, etc.)
    attack_damage: float = 0.0   # Used if the item is a weapon‑like tool in BP component
    recipe: Recipe = field(default_factory=Recipe)

@dataclass
class Project:
    pack_name: str = "My Mod Pack"
    author: str = "Your Name"
    description: str = "Created with Mod Maker — no coding!"
    namespace: str = "modmaker"
    items: list = field(default_factory=list)  # list[Item]

# -----------------------------
# Utilities
# -----------------------------
SAFE_ID_RE = re.compile(r"^[a-z0-9_]+$")

def ensure_safe_identifier(text: str) -> str:
    """Normalize to lower_snake_case a‑z0‑9_ only."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9_]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "item"


def make_uuid() -> str:
    return str(uuid.uuid4())


def write_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# Bedrock pack generators
# -----------------------------
class BedrockExporter:
    def __init__(self, project: Project):
        self.project = project
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.root_tmp = tempfile.mkdtemp(prefix="modmaker_")
        self.rp_dir = os.path.join(self.root_tmp, "RP")
        self.bp_dir = os.path.join(self.root_tmp, "BP")
        self.rp_uuid = make_uuid()
        self.bp_uuid = make_uuid()

    def cleanup(self):
        shutil.rmtree(self.root_tmp, ignore_errors=True)

    # ---- Resource Pack (RP)
    def build_rp(self):
        manifest = {
            "format_version": 2,
            "header": {
                "name": f"{self.project.pack_name} [RP]",
                "description": self.project.description,
                "uuid": self.rp_uuid,
                "version": [1, 0, 0],
                "min_engine_version": [1, 20, 0]
            },
            "modules": [
                {
                    "type": "resources",
                    "uuid": make_uuid(),
                    "version": [1, 0, 0]
                }
            ]
        }
        write_json(os.path.join(self.rp_dir, "manifest.json"), manifest)

        # pack_icon placeholder
        self._write_pack_icon(self.rp_dir)

        # Item textures + item_texture.json mapping
        texture_map = {"resource_pack_name": f"{self.project.pack_name} [RP]",
                        "texture_name": "atlas.items",
                        "texture_data": {}}

        for it in self.project.items:
            safe_id = ensure_safe_identifier(it.identifier)
            tex_name = f"{self.project.namespace}:{safe_id}"
            texture_map["texture_data"][tex_name] = {"textures": f"textures/items/{safe_id}"}

            # copy provided texture (or create placeholder)
            dst = os.path.join(self.rp_dir, "textures", "items", f"{safe_id}.png")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if it.texture_path and os.path.isfile(it.texture_path) and it.texture_path.lower().endswith(".png"):
                shutil.copyfile(it.texture_path, dst)
            else:
                # generate a small placeholder PNG (1x1) via binary header without PIL
                # This is a valid 1x1 transparent PNG
                placeholder = (
                    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
                    b"\x00\x00\x00\x0cIDAT\x08\xd7c\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
                )
                with open(dst, "wb") as f:
                    f.write(placeholder)

        write_json(os.path.join(self.rp_dir, "textures", "item_texture.json"), texture_map)

        # Language file for item display names
        lang_lines = [f"# Generated {self.timestamp}"]
        for it in self.project.items:
            safe_id = ensure_safe_identifier(it.identifier)
            lang_key = f"item.{self.project.namespace}.{safe_id}.name"
            lang_lines.append(f"{lang_key}={it.name}")
        lang_path = os.path.join(self.rp_dir, "texts", "en_US.lang")
        os.makedirs(os.path.dirname(lang_path), exist_ok=True)
        with open(lang_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lang_lines))

    # ---- Behavior Pack (BP)
    def build_bp(self):
        manifest = {
            "format_version": 2,
            "header": {
                "name": f"{self.project.pack_name} [BP]",
                "description": self.project.description,
                "uuid": self.bp_uuid,
                "version": [1, 0, 0],
                "min_engine_version": [1, 20, 0]
            },
            "modules": [
                {
                    "type": "data",
                    "uuid": make_uuid(),
                    "version": [1, 0, 0]
                }
            ],
            "dependencies": [
                {"uuid": self.rp_uuid, "version": [1, 0, 0]}
            ]
        }
        write_json(os.path.join(self.bp_dir, "manifest.json"), manifest)
        self._write_pack_icon(self.bp_dir)

        # Items JSON (BP)
        for it in self.project.items:
            safe_id = ensure_safe_identifier(it.identifier)
            full_id = f"{self.project.namespace}:{safe_id}"
            item_def = {
                "format_version": "1.20.0",
                "minecraft:item": {
                    "description": {
                        "identifier": full_id,
                        "category": it.category or "items"
                    },
                    "components": {
                        "minecraft:icon": {
                            "texture": full_id
                        },
                        "minecraft:max_stack_size": max(1, int(it.max_stack)),
                    }
                }
            }

            # Optional damage (treat as weapon‑ish by adding durability + damage)
            if it.attack_damage and it.attack_damage > 0:
                item_def["minecraft:item"]["components"]["minecraft:hand_equipped"] = True
                item_def["minecraft:item"]["components"]["minecraft:durability"] = {"max_durability": 128}
                item_def["minecraft:item"]["components"]["minecraft:damage"] = int(it.attack_damage)

            out_path = os.path.join(self.bp_dir, "items", f"{safe_id}.json")
            write_json(out_path, item_def)

            # Optional shapeless recipe
            if it.recipe and it.recipe.enabled and it.recipe.ingredients:
                recipe = {
                    "format_version": "1.20.0",
                    "minecraft:recipe_shapeless": {
                        "description": {"identifier": f"{full_id}_from_shapeless"},
                        "tags": ["crafting_table"],
                        "ingredients": [{"item": ing} for ing in it.recipe.ingredients],
                        "result": {"item": full_id, "count": max(1, int(it.recipe.count))}
                    }
                }
                rec_path = os.path.join(self.bp_dir, "recipes", f"{safe_id}_shapeless.json")
                write_json(rec_path, recipe)

    def bundle_mcaddon(self, export_dir: str) -> str:
        os.makedirs(export_dir, exist_ok=True)
        # Zip both packs into a single .mcaddon (zip with .mcaddon extension)
        export_name = ensure_safe_identifier(self.project.pack_name) or "my_pack"
        mcaddon_path = os.path.join(export_dir, f"{export_name}.mcaddon")
        with zipfile.ZipFile(mcaddon_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(self.rp_dir):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, self.root_tmp)
                    zf.write(full, rel)
            for root, _, files in os.walk(self.bp_dir):
                for f in files:
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, self.root_tmp)
                    zf.write(full, rel)
        return mcaddon_path

    def _write_pack_icon(self, pack_dir: str):
        # 1x1 placeholder icon — Minecraft allows it
        icon_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0cIDAT\x08\xd7c\x00\x01\x00\x00\x05\x00\x01\x0d\n\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        os.makedirs(pack_dir, exist_ok=True)
        with open(os.path.join(pack_dir, "pack_icon.png"), "wb") as f:
            f.write(icon_bytes)


# -----------------------------
# GUI Application
# -----------------------------
class ModMakerApp:
    def __init__(self, root: Tk):
        self.root = root
        root.title(f"{APP_TITLE} v{APP_VERSION}")
        root.geometry("980x640")
        root.minsize(900, 560)

        self.project = Project()

        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True)

        # ---- Project tab
        self.tab_project = ttk.Frame(nb)
        nb.add(self.tab_project, text="Project")
        self._build_project_tab(self.tab_project)

        # ---- Items tab
        self.tab_items = ttk.Frame(nb)
        nb.add(self.tab_items, text="Items")
        self._build_items_tab(self.tab_items)

        # ---- Export tab
        self.tab_export = ttk.Frame(nb)
        nb.add(self.tab_export, text="Export")
        self._build_export_tab(self.tab_export)

    # ---------------- Project Tab ----------------
    def _build_project_tab(self, parent):
        padx, pady = 12, 10
        frm = ttk.Frame(parent, padding=20)
        frm.pack(fill="x", expand=True, anchor="n")

        self.var_pack_name = StringVar(value=self.project.pack_name)
        self.var_author = StringVar(value=self.project.author)
        self.var_desc = StringVar(value=self.project.description)
        self.var_namespace = StringVar(value=self.project.namespace)

        ttk.Label(frm, text="Pack Name").grid(row=0, column=0, sticky=W, padx=padx, pady=pady)
        ttk.Entry(frm, textvariable=self.var_pack_name, width=40).grid(row=0, column=1, sticky=W)

        ttk.Label(frm, text="Author").grid(row=1, column=0, sticky=W, padx=padx, pady=pady)
        ttk.Entry(frm, textvariable=self.var_author, width=40).grid(row=1, column=1, sticky=W)

        ttk.Label(frm, text="Description").grid(row=2, column=0, sticky=W, padx=padx, pady=pady)
        ttk.Entry(frm, textvariable=self.var_desc, width=60).grid(row=2, column=1, sticky=W)

        ttk.Label(frm, text="Namespace (a_z_0_9)" ).grid(row=3, column=0, sticky=W, padx=padx, pady=pady)
        ttk.Entry(frm, textvariable=self.var_namespace, width=24).grid(row=3, column=1, sticky=W)

        ttk.Separator(parent).pack(fill="x", pady=6)
        tip = ttk.Label(parent, padding=10, wraplength=880,
                        text=("Tips:\n"
                              "• Namespace becomes your item prefix, e.g., 'mymod:steel_ingot'.\n"
                              "• You can change these later before exporting."))
        tip.pack(fill="x")

    # ---------------- Items Tab ----------------
    def _build_items_tab(self, parent):
        outer = ttk.Frame(parent, padding=10)
        outer.pack(fill="both", expand=True)

        # Left: list
        left = ttk.Frame(outer)
        left.pack(side="left", fill="both", expand=True)
        ttk.Label(left, text="Items in Project").pack(anchor="w")
        self.list_items = ttk.Treeview(left, columns=("id","name","stack","cat","dmg"), show="headings")
        self.list_items.heading("id", text="Identifier")
        self.list_items.heading("name", text="Name")
        self.list_items.heading("stack", text="Max Stack")
        self.list_items.heading("cat", text="Category")
        self.list_items.heading("dmg", text="Damage")
        self.list_items.column("id", width=180)
        self.list_items.column("name", width=180)
        self.list_items.column("stack", width=90, anchor="center")
        self.list_items.column("cat", width=100, anchor="center")
        self.list_items.column("dmg", width=80, anchor="center")
        self.list_items.pack(fill="both", expand=True)
        self.list_items.bind("<<TreeviewSelect>>", self._on_item_selected)

        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="New Item", command=self._new_item).pack(side="left")
        ttk.Button(btns, text="Delete", command=self._delete_item).pack(side="left", padx=6)

        # Right: editor
        right = ttk.LabelFrame(outer, text="Item Editor", padding=10)
        right.pack(side="left", fill="both", expand=True, padx=10)

        self.var_item_name = StringVar()
        self.var_item_id = StringVar()
        self.var_item_texture = StringVar()
        self.var_item_stack = IntVar(value=64)
        self.var_item_cat = StringVar(value="items")
        self.var_item_damage = DoubleVar(value=0.0)

        grid = right
        r=0
        ttk.Label(grid, text="Display Name").grid(row=r, column=0, sticky=W); r+=1
        ttk.Entry(grid, textvariable=self.var_item_name, width=34).grid(row=r-1, column=1, sticky=W)

        ttk.Label(grid, text="Identifier (snake_case)").grid(row=r, column=0, sticky=W); r+=1
        ttk.Entry(grid, textvariable=self.var_item_id, width=34).grid(row=r-1, column=1, sticky=W)

        ttk.Label(grid, text="Texture (.png)").grid(row=r, column=0, sticky=W); r+=1
        row = ttk.Frame(grid)
        row.grid(row=r-1, column=1, sticky=W)
        ttk.Entry(row, textvariable=self.var_item_texture, width=28).pack(side="left")
        ttk.Button(row, text="Browse", command=self._browse_texture).pack(side="left", padx=6)

        ttk.Label(grid, text="Max Stack (1‑64)").grid(row=r, column=0, sticky=W); r+=1
        ttk.Spinbox(grid, from_=1, to=64, textvariable=self.var_item_stack, width=8).grid(row=r-1, column=1, sticky=W)

        ttk.Label(grid, text="Category").grid(row=r, column=0, sticky=W); r+=1
        ttk.Combobox(grid, values=["items","equipment","nature","construction","items"], textvariable=self.var_item_cat, width=16).grid(row=r-1, column=1, sticky=W)

        ttk.Label(grid, text="Attack Damage (optional)").grid(row=r, column=0, sticky=W); r+=1
        ttk.Spinbox(grid, from_=0, to=40, increment=1, textvariable=self.var_item_damage, width=8).grid(row=r-1, column=1, sticky=W)

        # Recipe group
        recipe_box = ttk.LabelFrame(right, text="Shapeless Recipe (optional)", padding=10)
        recipe_box.grid(row=r, column=0, columnspan=2, sticky=E+W, pady=10); r+=1

        self.var_recipe_enabled = BooleanVar(value=False)
        self.var_recipe_ings = StringVar(value="minecraft:stick,minecraft:stick")
        self.var_recipe_count = IntVar(value=1)

        ttk.Checkbutton(recipe_box, text="Enable recipe for this item", variable=self.var_recipe_enabled).grid(row=0, column=0, columnspan=2, sticky=W)
        ttk.Label(recipe_box, text="Ingredients (comma‑separated IDs)").grid(row=1, column=0, sticky=W)
        ttk.Entry(recipe_box, textvariable=self.var_recipe_ings, width=40).grid(row=1, column=1, sticky=W)
        ttk.Label(recipe_box, text="Output Count").grid(row=2, column=0, sticky=W)
        ttk.Spinbox(recipe_box, from_=1, to=64, textvariable=self.var_recipe_count, width=8).grid(row=2, column=1, sticky=W)

        # Save/Edit buttons
        actions = ttk.Frame(right)
        actions.grid(row=r, column=0, columnspan=2, sticky=W, pady=6)
        ttk.Button(actions, text="Save Item", command=self._save_item).pack(side="left")
        ttk.Button(actions, text="Reset Form", command=self._reset_item_form).pack(side="left", padx=8)

        # Stretch configs
        for c in range(2):
            right.columnconfigure(c, weight=1)

    # ---------------- Export Tab ----------------
    def _build_export_tab(self, parent):
        wrap = ttk.Frame(parent, padding=20)
        wrap.pack(fill="both", expand=True)

        info = ("When you click EXPORT, the app will generate a Behavior Pack and Resource Pack, "
                "bundle them into a single .mcaddon, and save it under an 'exports' folder.")
        ttk.Label(wrap, text=info, wraplength=880, justify="left").pack(anchor="w", pady=10)

        ttk.Button(wrap, text="EXPORT .mcaddon", command=self._do_export).pack(anchor="w", pady=6)

    # ---------------- Logic ----------------
    def _on_item_selected(self, event=None):
        sel = self.list_items.selection()
        if not sel:
            return
        index = int(self.list_items.index(sel[0]))
        it: Item = self.project.items[index]
        self._load_item_into_form(it)

    def _new_item(self):
        self._reset_item_form()
        self.list_items.selection_remove(self.list_items.selection())

    def _delete_item(self):
        sel = self.list_items.selection()
        if not sel:
            return
        index = int(self.list_items.index(sel[0]))
        del self.project.items[index]
        self._refresh_items_list()
        self._reset_item_form()

    def _browse_texture(self):
        path = filedialog.askopenfilename(title="Select PNG texture", filetypes=[["PNG images","*.png"]])
        if path:
            self.var_item_texture.set(path)

    def _reset_item_form(self):
        self.var_item_name.set("")
        self.var_item_id.set("")
        self.var_item_texture.set("")
        self.var_item_stack.set(64)
        self.var_item_cat.set("items")
        self.var_item_damage.set(0.0)
        self.var_recipe_enabled.set(False)
        self.var_recipe_ings.set("minecraft:stick,minecraft:stick")
        self.var_recipe_count.set(1)

    def _load_item_into_form(self, it: Item):
        self.var_item_name.set(it.name)
        self.var_item_id.set(it.identifier)
        self.var_item_texture.set(it.texture_path)
        self.var_item_stack.set(it.max_stack)
        self.var_item_cat.set(it.category)
        self.var_item_damage.set(it.attack_damage)
        self.var_recipe_enabled.set(bool(it.recipe.enabled))
        self.var_recipe_ings.set(",".join(it.recipe.ingredients) if it.recipe.ingredients else "")
        self.var_recipe_count.set(it.recipe.count if it.recipe.count else 1)

    def _save_item(self):
        name = self.var_item_name.get().strip()
        ident = ensure_safe_identifier(self.var_item_id.get())
        if not name:
            messagebox.showerror("Missing", "Please enter a display name.")
            return
        if not ident or not SAFE_ID_RE.match(ident):
            messagebox.showerror("Identifier", "Use only lowercase letters, numbers, and underscores.")
            return

        texture = self.var_item_texture.get().strip()
        stack = max(1, min(64, int(self.var_item_stack.get())))
        cat = (self.var_item_cat.get() or "items").strip()
        dmg = float(self.var_item_damage.get() or 0.0)

        rec_enabled = bool(self.var_recipe_enabled.get())
        ings_raw = [s.strip() for s in self.var_recipe_ings.get().split(",") if s.strip()]
        out_count = max(1, min(64, int(self.var_recipe_count.get())))

        recipe = Recipe(enabled=rec_enabled, ingredients=ings_raw, count=out_count)
        new_item = Item(name=name, identifier=ident, texture_path=texture, max_stack=stack,
                        category=cat, attack_damage=dmg, recipe=recipe)

        # if selection exists -> update, else append
        sel = self.list_items.selection()
        if sel:
            index = int(self.list_items.index(sel[0]))
            self.project.items[index] = new_item
        else:
            self.project.items.append(new_item)

        self._refresh_items_list()
        messagebox.showinfo("Saved", f"Item '{name}' saved.")

    def _refresh_items_list(self):
        for row in self.list_items.get_children():
            self.list_items.delete(row)
        for it in self.project.items:
            self.list_items.insert("", END, values=(it.identifier, it.name, it.max_stack, it.category, it.attack_damage))

    def _sync_project_header(self):
        self.project.pack_name = self.var_pack_name.get().strip() or "My Mod Pack"
        self.project.author = self.var_author.get().strip() or "Your Name"
        self.project.description = self.var_desc.get().strip() or "Created with Mod Maker — no coding!"
        ns = ensure_safe_identifier(self.var_namespace.get())
        self.project.namespace = ns or "modmaker"

    def _do_export(self):
        self._sync_project_header()
        if not self.project.items:
            if not messagebox.askyesno("No Items", "No items added yet. Export anyway?"):
                return

        exporter = BedrockExporter(self.project)
        try:
            exporter.build_rp()
            exporter.build_bp()
            export_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "exports")
            path = exporter.bundle_mcaddon(export_dir)
            # Also drop a README with import instructions
            with open(os.path.join(export_dir, "README.txt"), "w", encoding="utf-8") as f:
                f.write((
                    f"Exported by {APP_TITLE} v{APP_VERSION} on {exporter.timestamp}\n\n"
                    f"HOW TO IMPORT:\n"
                    f"1) Double‑click the .mcaddon file to open Minecraft and import.\n"
                    f"2) Create a new world (or edit an existing one) and enable BOTH the behavior and resource packs.\n"
                    f"3) Enter the world and find your items in the creative inventory.\n\n"
                    f"NOTES:\n"
                    f"• If you used custom textures, keep them as 16x16 or 32x32 PNGs for best results.\n"
                    f"• Recipes are shapeless and crafted at the crafting table.\n"
                ))
            messagebox.showinfo("Exported", f"Export complete!\nSaved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))
        finally:
            exporter.cleanup()


def main():
    root = Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass
    app = ModMakerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
