import json
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, Union, Tuple
import webbrowser


class OutfitConverter:
    """Professional converter between Cherax, YimMenu, and Stand outfit formats"""
    
    COMPONENT_MAP = {
        "Head": {"yim_id": 0, "stand": "Head"},
        "Beard": {"yim_id": 1, "stand": "Facial Hair"},
        "Hair": {"yim_id": 2, "stand": "Hair"},
        "Torso": {"yim_id": 3, "stand": "Top"},
        "Legs": {"yim_id": 4, "stand": "Pants"},
        "Hands": {"yim_id": 5, "stand": "Gloves"},
        "Feet": {"yim_id": 6, "stand": "Shoes"},
        "Teeth": {"yim_id": 7, "stand": "Accessories"},
        "Special": {"yim_id": 8, "stand": "Top 2"},
        "Special 2": {"yim_id": 9, "stand": "Bag / Parachute"},
        "Decal": {"yim_id": 10, "stand": "Decals"},
        "Tuxedo/Jacket Bib": {"yim_id": 11, "stand": "Top 3"}
    }
    
    PROPS_MAP = {
        "Head": {"yim_id": 0, "stand": "Hat"},
        "Eyes": {"yim_id": 1, "stand": "Glasses"},
        "Ears": {"yim_id": 2, "stand": "Earwear"},
        "Left Wrist": {"yim_id": 6, "stand": "Watch"},
        "Right Wrist": {"yim_id": 7, "stand": "Bracelet"}
    }
    
    YIM_TO_CHERAX = {v["yim_id"]: k for k, v in COMPONENT_MAP.items()}
    YIM_TO_STAND = {v["yim_id"]: v["stand"] for k, v in COMPONENT_MAP.items()}
    STAND_TO_CHERAX = {v["stand"]: k for k, v in COMPONENT_MAP.items()}
    YIM_PROPS_TO_CHERAX = {v["yim_id"]: k for k, v in PROPS_MAP.items()}
    YIM_PROPS_TO_STAND = {v["yim_id"]: v["stand"] for k, v in PROPS_MAP.items()}
    STAND_PROPS_TO_CHERAX = {v["stand"]: k for k, v in PROPS_MAP.items()}
    
    @staticmethod
    def detect_format(data: Union[Dict, str]) -> Tuple[str, float]:
        if isinstance(data, str):
            stand_keywords = ["Model:", "Head:", "Top:", "Pants:", "Hair Colour:"]
            matches = sum(1 for kw in stand_keywords if kw in data)
            if matches >= 3:
                return "stand", min(matches / len(stand_keywords), 1.0)
            return "unknown", 0.0
        
        if isinstance(data, dict):
            cherax_score = 0.0
            yim_score = 0.0
            
            if "format" in data and data.get("format") == "Cherax Entity":
                cherax_score += 0.4
            if "baseFlags" in data:
                cherax_score += 0.2
            if "face_features" in data:
                cherax_score += 0.2
            if "components" in data:
                components = data["components"]
                if components and isinstance(list(components.keys())[0], str):
                    first_key = list(components.keys())[0]
                    if first_key in OutfitConverter.COMPONENT_MAP:
                        cherax_score += 0.3
                    if "drawable" in str(components.get(first_key, {})):
                        cherax_score += 0.2
            
            if "blend_data" in data:
                yim_score += 0.3
            if "components" in data:
                components = data["components"]
                if components:
                    keys = list(components.keys())
                    if all(str(k).isdigit() for k in keys):
                        yim_score += 0.3
                    first_comp = components.get(keys[0], {})
                    if "drawable_id" in first_comp:
                        yim_score += 0.3
            if "props" in data:
                props = data["props"]
                if props and all(str(k).isdigit() for k in props.keys()):
                    yim_score += 0.2
            
            if cherax_score > yim_score and cherax_score >= 0.5:
                return "cherax", cherax_score
            elif yim_score > cherax_score and yim_score >= 0.5:
                return "yim", yim_score
            elif cherax_score > 0 or yim_score > 0:
                return ("cherax" if cherax_score > yim_score else "yim"), max(cherax_score, yim_score)
        
        return "unknown", 0.0
    
    @staticmethod
    def cherax_to_yim(cherax_data: Dict[str, Any]) -> Dict[str, Any]:
        yim_data = {"model": cherax_data.get("model", 1885233650), "components": {}, "props": {}}
        
        if "components" in cherax_data:
            for comp_name, comp_data in cherax_data["components"].items():
                if comp_name in OutfitConverter.COMPONENT_MAP:
                    comp_id = str(OutfitConverter.COMPONENT_MAP[comp_name]["yim_id"])
                    yim_data["components"][comp_id] = {
                        "drawable_id": comp_data.get("drawable", 0),
                        "texture_id": comp_data.get("texture", 0)
                    }
        
        if "props" in cherax_data:
            for prop_name, prop_data in cherax_data["props"].items():
                if prop_name in OutfitConverter.PROPS_MAP:
                    prop_id = str(OutfitConverter.PROPS_MAP[prop_name]["yim_id"])
                    yim_data["props"][prop_id] = {
                        "drawable_id": prop_data.get("drawable", -1),
                        "texture_id": prop_data.get("texture", -1)
                    }
        
        yim_data["blend_data"] = {
            "is_parent": 0, "shape_first_id": 0, "shape_mix": 0.0,
            "shape_second_id": 0, "shape_third_id": 0, "skin_first_id": 0,
            "skin_mix": 0.5, "skin_second_id": 0, "skin_third_id": 0, "third_mix": 0.0
        }
        return yim_data
    
    @staticmethod
    def cherax_to_stand(cherax_data: Dict[str, Any]) -> str:
        lines = ["Model: mp_m_freemode_01"]
        stand_components = {
            "Head": (0, 0), "Facial Hair": (0, 0), "Hair": (0, 0),
            "Hair Colour": 0, "Hair Colour: Highlight": -1,
            "Top": (0, 0), "Top 2": (0, 0), "Top 3": (0, 0),
            "Bag / Parachute": (0, 0), "Gloves": (0, 0), "Pants": (0, 0),
            "Shoes": (0, 0), "Accessories": (0, 0), "Decals": (0, 0),
        }
        stand_props = {
            "Hat": (-1, -1), "Glasses": (-1, -1), "Earwear": (-1, -1),
            "Watch": (-1, -1), "Bracelet": (-1, -1),
        }
        
        if "components" in cherax_data:
            for comp_name, comp_data in cherax_data["components"].items():
                if comp_name in OutfitConverter.COMPONENT_MAP:
                    stand_name = OutfitConverter.COMPONENT_MAP[comp_name]["stand"]
                    stand_components[stand_name] = (comp_data.get("drawable", 0), comp_data.get("texture", 0))
        
        if "props" in cherax_data:
            for prop_name, prop_data in cherax_data["props"].items():
                if prop_name in OutfitConverter.PROPS_MAP:
                    stand_name = OutfitConverter.PROPS_MAP[prop_name]["stand"]
                    stand_props[stand_name] = (prop_data.get("drawable", -1), prop_data.get("texture", -1))
        
        for name, value in stand_components.items():
            if isinstance(value, tuple):
                lines.append(f"{name}: {value[0]}")
                lines.append(f"{name} Variation: {value[1]}")
            else:
                lines.append(f"{name}: {value}")
        
        lines.append(f"Facial Hair Colour: {cherax_data.get('primary_hair_tint', 0)}")
        
        for name, value in stand_props.items():
            lines.append(f"{name}: {value[0]}")
            lines.append(f"{name} Variation: {value[1]}")
        
        return "\n".join(lines)
    
    @staticmethod
    def yim_to_cherax(yim_data: Dict[str, Any]) -> Dict[str, Any]:
        cherax_data = {
            "format": "Cherax Entity", "type": 2, "model": yim_data.get("model", 1885233650),
            "baseFlags": 66855, "components": {}, "props": {},
            "face_features": {
                "Nose Width": 0.0, "Nose Peak": 0.0, "Nose Length": 0.0,
                "Nose Bone Curveness": 0.0, "Nose Tip": 0.0, "Nose Bone Twist": 0.0,
                "Eyebrow Height": 0.0, "Eyebrow Indent": 0.0, "Cheek Bones": 0.0,
                "Cheek Sideways Bone Size": 0.0, "Cheek Bones Width": 0.0,
                "Eye Opening": 0.0, "Lip Thickness": 0.0, "Jaw Bone Width": 0.0,
                "Jaw Bone Shape": 0.0, "Chin Bone": 0.0, "Chin Bone Length": 0.0,
                "Chin Bone Shape": 0.0, "Chin Hole": 0.0, "Neck Thickness": 0.0
            },
            "primary_hair_tint": 255, "secondary_hair_tint": 255, "attachments": []
        }
        
        if "components" in yim_data:
            for comp_id, comp_data in yim_data["components"].items():
                comp_id_int = int(comp_id)
                if comp_id_int in OutfitConverter.YIM_TO_CHERAX:
                    comp_name = OutfitConverter.YIM_TO_CHERAX[comp_id_int]
                    cherax_data["components"][comp_name] = {
                        "drawable": comp_data.get("drawable_id", 0),
                        "texture": comp_data.get("texture_id", 0),
                        "palette": 0
                    }
        
        if "props" in yim_data:
            for prop_id, prop_data in yim_data["props"].items():
                prop_id_int = int(prop_id)
                if prop_id_int in OutfitConverter.YIM_PROPS_TO_CHERAX:
                    prop_name = OutfitConverter.YIM_PROPS_TO_CHERAX[prop_id_int]
                    cherax_data["props"][prop_name] = {
                        "drawable": prop_data.get("drawable_id", -1),
                        "texture": prop_data.get("texture_id", -1)
                    }
        return cherax_data
    
    @staticmethod
    def yim_to_stand(yim_data: Dict[str, Any]) -> str:
        return OutfitConverter.cherax_to_stand(OutfitConverter.yim_to_cherax(yim_data))
    
    @staticmethod
    def stand_to_cherax(stand_text: str) -> Dict[str, Any]:
        lines = stand_text.strip().split('\n')
        cherax_data = {
            "format": "Cherax Entity", "type": 2, "model": 1885233650,
            "baseFlags": 66855, "components": {}, "props": {},
            "face_features": {
                "Nose Width": 0.0, "Nose Peak": 0.0, "Nose Length": 0.0,
                "Nose Bone Curveness": 0.0, "Nose Tip": 0.0, "Nose Bone Twist": 0.0,
                "Eyebrow Height": 0.0, "Eyebrow Indent": 0.0, "Cheek Bones": 0.0,
                "Cheek Sideways Bone Size": 0.0, "Cheek Bones Width": 0.0,
                "Eye Opening": 0.0, "Lip Thickness": 0.0, "Jaw Bone Width": 0.0,
                "Jaw Bone Shape": 0.0, "Chin Bone": 0.0, "Chin Bone Length": 0.0,
                "Chin Bone Shape": 0.0, "Chin Hole": 0.0, "Neck Thickness": 0.0
            },
            "primary_hair_tint": 0, "secondary_hair_tint": 0, "attachments": []
        }
        
        data_dict = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key, value = key.strip(), value.strip()
                try:
                    data_dict[key] = int(value)
                except ValueError:
                    data_dict[key] = value
        
        for stand_name, cherax_name in OutfitConverter.STAND_TO_CHERAX.items():
            if stand_name in data_dict and f"{stand_name} Variation" in data_dict:
                cherax_data["components"][cherax_name] = {
                    "drawable": data_dict.get(stand_name, 0),
                    "texture": data_dict.get(f"{stand_name} Variation", 0),
                    "palette": 0
                }
        
        for stand_name, cherax_name in OutfitConverter.STAND_PROPS_TO_CHERAX.items():
            if stand_name in data_dict and f"{stand_name} Variation" in data_dict:
                cherax_data["props"][cherax_name] = {
                    "drawable": data_dict.get(stand_name, -1),
                    "texture": data_dict.get(f"{stand_name} Variation", -1)
                }
        
        if "Hair Colour" in data_dict:
            cherax_data["primary_hair_tint"] = data_dict["Hair Colour"]
        if "Facial Hair Colour" in data_dict:
            cherax_data["secondary_hair_tint"] = data_dict["Facial Hair Colour"]
        
        return cherax_data
    
    @staticmethod
    def stand_to_yim(stand_text: str) -> Dict[str, Any]:
        return OutfitConverter.cherax_to_yim(OutfitConverter.stand_to_cherax(stand_text))


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        bg = kwargs.pop('bg', '#7c3aed')
        fg = kwargs.pop('fg', '#ffffff')
        width = kwargs.pop('width', 200)
        height = kwargs.pop('height', 45)
        
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg = bg
        self.hover_bg = '#9333ea'
        
        self.rect = self.create_rectangle(0, 0, width, height, fill=bg, outline='', tags='button')
        self.text_id = self.create_text(width//2, height//2, text=text, fill=fg, 
                                       font=('Segoe UI', 11, 'bold'), tags='button')
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def on_enter(self, e):
        self.itemconfig(self.rect, fill=self.hover_bg)
        self.config(cursor='hand2')
        
    def on_leave(self, e):
        self.itemconfig(self.rect, fill=self.bg)
        self.config(cursor='')
        
    def on_click(self, e):
        if self.command:
            self.command()


class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GTA V Outfit Converter")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        self.bg_dark = "#0f0f1e"
        self.bg_card = "#1a1a2e"
        self.bg_input = "#16213e"
        self.purple = "#7c3aed"
        self.purple_glow = "#a855f7"
        self.text_primary = "#ffffff"
        self.text_secondary = "#94a3b8"
        self.success = "#10b981"
        
        self.root.configure(bg=self.bg_dark)
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_dark)
        header.pack(fill=tk.X, pady=(20, 0))
        
        title = tk.Label(header, text="GTA V OUTFIT CONVERTER",
                        font=("Segoe UI", 26, "bold"), bg=self.bg_dark, fg=self.purple_glow)
        title.pack()
        
        subtitle = tk.Label(header, text="Universal Format Converter • Cherax • YimMenu • Stand",
                           font=("Segoe UI", 10), bg=self.bg_dark, fg=self.text_secondary)
        subtitle.pack()
        
        # Main card
        card = tk.Frame(self.root, bg=self.bg_card)
        card.pack(pady=20, padx=60, fill=tk.BOTH, expand=True)
        
        tk.Frame(card, bg=self.purple, height=2).pack(fill=tk.X)
        
        content = tk.Frame(card, bg=self.bg_card)
        content.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Auto-detect
        tk.Label(content, text="🎯 Smart Auto-Detection", font=("Segoe UI", 12, "bold"),
                bg=self.bg_card, fg=self.text_primary).pack()
        
        self.detect_label = tk.Label(content, text="Drop your file and I'll handle the rest",
                                     font=("Segoe UI", 9), bg=self.bg_card, fg=self.text_secondary)
        self.detect_label.pack(pady=5)
        
        # File input
        input_section = tk.Frame(content, bg=self.bg_card)
        input_section.pack(fill=tk.X, pady=20)
        
        tk.Label(input_section, text="Select File", font=("Segoe UI", 10, "bold"),
                bg=self.bg_card, fg=self.text_primary).pack(anchor=tk.W, pady=(0, 8))
        
        input_container = tk.Frame(input_section, bg=self.bg_card)
        input_container.pack(fill=tk.X)
        
        self.input_file_var = tk.StringVar()
        
        tk.Entry(input_container, textvariable=self.input_file_var, font=("Segoe UI", 10),
                bg=self.bg_input, fg=self.text_primary, insertbackground=self.purple,
                relief=tk.FLAT, bd=0).pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12, padx=(0, 10))
        
        ModernButton(input_container, "Browse", self.browse_input, 
                    bg=self.purple, width=100, height=42).pack(side=tk.LEFT)
        
        # Options
        options_frame = tk.Frame(content, bg=self.bg_card)
        options_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(options_frame, text="Conversion Direction", font=("Segoe UI", 10, "bold"),
                bg=self.bg_card, fg=self.text_primary).pack(anchor=tk.W, pady=(0, 10))
        
        self.direction_var = tk.StringVar(value="auto")
        
        radio_grid = tk.Frame(options_frame, bg=self.bg_card)
        radio_grid.pack(fill=tk.X)
        
        options = [
            ("🔄 Auto-Detect", "auto"), ("Cherax → YimMenu", "cherax_to_yim"),
            ("YimMenu → Cherax", "yim_to_cherax"), ("Cherax → Stand", "cherax_to_stand"),
            ("YimMenu → Stand", "yim_to_stand"), ("Stand → Cherax", "stand_to_cherax"),
            ("Stand → YimMenu", "stand_to_yim")
        ]
        
        for i, (label, value) in enumerate(options):
            tk.Radiobutton(radio_grid, text=label, variable=self.direction_var, value=value,
                          bg=self.bg_card, fg=self.text_secondary, selectcolor=self.bg_input,
                          activebackground=self.bg_card, activeforeground=self.purple,
                          font=("Segoe UI", 9), relief=tk.FLAT, cursor='hand2'
                          ).grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=5)
        
        # Convert button
        ModernButton(content, "⚡ CONVERT NOW", self.convert_file,
                    bg=self.purple, width=250, height=50).pack(pady=25)
        
        # Log
        tk.Label(content, text="Conversion Log", font=("Segoe UI", 10, "bold"),
                bg=self.bg_card, fg=self.text_primary).pack(anchor=tk.W, pady=(0, 8))
        
        self.log_text = tk.Text(content, height=8, bg=self.bg_input, fg=self.success,
                               font=("Consolas", 9), relief=tk.FLAT, bd=0, padx=15, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Footer
        footer = tk.Frame(self.root, bg=self.bg_dark)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        footer_content = tk.Frame(footer, bg=self.bg_dark)
        footer_content.pack()
        
        tk.Label(footer_content, text="Created by ", font=("Segoe UI", 9),
                bg=self.bg_dark, fg=self.text_secondary).pack(side=tk.LEFT)
        
        creator = tk.Label(footer_content, text="@sizrox", font=("Segoe UI", 9, "bold"),
                          bg=self.bg_dark, fg=self.purple, cursor="hand2")
        creator.pack(side=tk.LEFT)
        creator.bind("<Button-1>", lambda e: webbrowser.open("https://discord.com/users/sizrox"))
        
        discord = tk.Label(footer_content, text=" 💬 ", font=("Segoe UI", 12),
                          bg=self.bg_dark, fg=self.purple, cursor="hand2")
        discord.pack(side=tk.LEFT, padx=5)
        discord.bind("<Button-1>", lambda e: webbrowser.open("https://discord.com/users/sizrox"))
        
        tk.Label(footer_content, text=" | Professional GTA V Modding Tool",
                font=("Segoe UI", 9), bg=self.bg_dark, fg=self.text_secondary).pack(side=tk.LEFT)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Outfit File",
            filetypes=[("All Supported", "*.json;*.txt"), ("JSON files", "*.json"),
                      ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
            self.log(f"📁 Selected: {Path(filename).name}")
            self.auto_detect_format(filename)
    
    def auto_detect_format(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                data = content
            
            detected_format, confidence = OutfitConverter.detect_format(data)
            
            if detected_format != "unknown":
                confidence_pct = int(confidence * 100)
                self.detect_label.config(
                    text=f"✓ Detected: {detected_format.upper()} ({confidence_pct}% confidence)",
                    fg=self.success
                )
            else:
                self.detect_label.config(
                    text="⚠ Unable to detect format - please select manually",
                    fg="#f59e0b"
                )
        except:
            self.detect_label.config(text="⚠ Error reading file", fg="#ef4444")
    
    def log(self, message: str):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def convert_file(self):
        input_file = self.input_file_var.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input file!")
            return
        
        if not Path(input_file).exists():
            messagebox.showerror("Error", "Input file does not exist!")
            return
        
        try:
            self.log("\n" + "="*50)
            self.log("⚡ Starting conversion process...")
            
            input_path = Path(input_file)
            self.log(f"📖 Reading: {input_path.name}")
            
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                input_data = json.loads(content)
            except json.JSONDecodeError:
                input_data = content
            
            detected_format, confidence = OutfitConverter.detect_format(input_data)
            self.log(f"🔍 Detected format: {detected_format.upper()} ({int(confidence * 100)}% confidence)")
            
            direction = self.direction_var.get()
            
            if direction == "auto":
                if detected_format == "cherax":
                    direction = "cherax_to_yim"
                    self.log("🎯 Auto-selected: Cherax → YimMenu")
                elif detected_format == "yim":
                    direction = "yim_to_stand"
                    self.log("🎯 Auto-selected: YimMenu → Stand")
                elif detected_format == "stand":
                    direction = "stand_to_cherax"
                    self.log("🎯 Auto-selected: Stand → Cherax")
                else:
                    raise ValueError("Could not auto-detect format! Please select conversion direction manually.")
            
            self.log(f"⚙️ Converting: {direction.replace('_', ' → ').upper()}")
            
            output_ext = ".json"
            output_suffix = ""
            
            if direction == "cherax_to_yim":
                output_data = OutfitConverter.cherax_to_yim(input_data)
                output_suffix = "_yim"
            elif direction == "yim_to_cherax":
                output_data = OutfitConverter.yim_to_cherax(input_data)
                output_suffix = "_cherax"
            elif direction == "cherax_to_stand":
                output_data = OutfitConverter.cherax_to_stand(input_data)
                output_ext = ".txt"
                output_suffix = "_stand"
            elif direction == "yim_to_stand":
                output_data = OutfitConverter.yim_to_stand(input_data)
                output_ext = ".txt"
                output_suffix = "_stand"
            elif direction == "stand_to_cherax":
                output_data = OutfitConverter.stand_to_cherax(input_data)
                output_suffix = "_cherax"
            elif direction == "stand_to_yim":
                output_data = OutfitConverter.stand_to_yim(input_data)
                output_suffix = "_yim"
            else:
                raise ValueError(f"Unknown conversion direction: {direction}")
            
            output_file = input_path.parent / f"{input_path.stem}{output_suffix}{output_ext}"
            
            self.log(f"💾 Writing: {output_file.name}")
            with open(output_file, 'w', encoding='utf-8') as f:
                if isinstance(output_data, str):
                    f.write(output_data)
                else:
                    json.dump(output_data, f, indent=4)
            
            self.log("✅ Conversion completed successfully!")
            self.log(f"📂 Output saved: {output_file}")
            self.log("="*50 + "\n")
            
            messagebox.showinfo("Success ✓", 
                f"Conversion completed successfully!\n\nOutput saved to:\n{output_file.name}")
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON file: {str(e)}"
            self.log(f"❌ ERROR: {error_msg}")
            messagebox.showerror("JSON Error", error_msg)
        except Exception as e:
            error_msg = f"{str(e)}"
            self.log(f"❌ ERROR: {error_msg}")
            messagebox.showerror("Error", error_msg)


def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()