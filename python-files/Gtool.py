import os
import shutil
import json
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import base64
import threading
import re
import zipfile
from idlelib.percolator import Percolator
from idlelib.colorizer import ColorDelegator
from idlelib.undo import UndoDelegator




class CodeEditor(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self._lua_keywords = [
            'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for', 
            'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat', 
            'return', 'then', 'true', 'until', 'while'
        ]
        self._lua_functions = [
            'assert', 'collectgarbage', 'dofile', 'error', 'getmetatable', 
            'ipairs', 'load', 'loadfile', 'next', 'pairs', 'pcall', 'print', 
            'rawequal', 'rawget', 'rawlen', 'rawset', 'require', 'select', 
            'setmetatable', 'tonumber', 'tostring', 'type', 'xpcall'
        ]
        self._lua_lib = [
            'coroutine', 'debug', 'io', 'math', 'os', 'package', 'string', 'table', 'utf8'
        ]
        
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<Tab>', self._handle_tab)
        self.bind('<Return>', self._handle_return)
        self.bind('<Control-space>', self._show_completions)
        self.create_autorun_folders = True
        
        self._setup_syntax_highlighting()
        
        self._error_tags = []
        self.tag_config('error', foreground='red', underline=True)
        
        
        
    def _setup_syntax_highlighting(self):
        self.percolator = Percolator(self)
        self.undo = UndoDelegator()
        self.percolator.insertfilter(self.undo)
        
        self.color = ColorDelegator()
        self.color.prog = re.compile(
            r'(?P<KEYWORD>' + '|'.join(self._lua_keywords) + r')\b|'
            r'(?P<BUILTIN>' + '|'.join(self._lua_functions) + r')\b|'
            r'(?P<STRING>"[^"]*"?|\'[^\']*\'?)|'
            r'(?P<COMMENT>--\[\[.*?\]\]|--[^\n]*)',
            re.MULTILINE|re.DOTALL
        )
        
        self.color.tagdefs = {
            'KEYWORD': {'foreground': '#CC7A00', 'font': 'TkFixedFont'},
            'BUILTIN': {'foreground': '#7A00CC', 'font': 'TkFixedFont'},
            'STRING': {'foreground': '#007ACC', 'font': 'TkFixedFont'},
            'COMMENT': {'foreground': '#007A00', 'font': 'TkFixedFont'},
        }
        
        self.percolator.insertfilter(self.color)
        
    def _on_key_release(self, event):
        if event.keysym == 'BackSpace':
            self._check_errors()
            
    def _handle_tab(self, event):
        self.insert(tk.INSERT, '    ')
        return 'break'
    
    def _handle_return(self, event):
        line = self.get('insert linestart', 'insert lineend')
        
        if re.match(r'^\s*function\s+\w+\(.*\)\s*$', line):
            self.insert(tk.INSERT, '\n    \nend')
            self.mark_set(tk.INSERT, 'insert -1 line +4 chars')
            return 'break'
        elif re.match(r'^\s*if\s+.+\s+then\s*$', line):
            self.insert(tk.INSERT, '\n    \nend')
            self.mark_set(tk.INSERT, 'insert -1 line +4 chars')
            return 'break'
        elif re.match(r'^\s*for\s+.+\s+do\s*$', line):
            self.insert(tk.INSERT, '\n    \nend')
            self.mark_set(tk.INSERT, 'insert -1 line +4 chars')
            return 'break'
        elif re.match(r'^\s*while\s+.+\s+do\s*$', line):
            self.insert(tk.INSERT, '\n    \nend')
            self.mark_set(tk.INSERT, 'insert -1 line +4 chars')
            return 'break'
        
        match = re.match(r'^(\s*)', line)
        indent = match.group(1) if match else ''
        self.insert(tk.INSERT, '\n' + indent)
        return 'break'
        
    def _check_errors(self):
        for tag in self._error_tags:
            self.tag_remove('error', tag[0], tag[1])
        self._error_tags = []
    
    def _show_completions(self, event=None):
        pos = self.index(tk.INSERT)
        line_start = self.get('insert linestart', 'insert')
        word_start = re.search(r'(\w+)$', line_start)
        
        if not word_start:
            return
        
        word = word_start.group(1)
        start_pos = f'insert - {len(word)}c'
        
        completions = []
        for kw in self._lua_keywords + self._lua_functions + self._lua_lib:
            if kw.startswith(word.lower()):
                completions.append(kw)
        
        if not completions:
            return
        
        popup = tk.Toplevel(self)
        popup.wm_overrideredirect(True)
        popup.wm_geometry(f"+{self.winfo_pointerx()}+{self.winfo_pointery()}")
        
        lb = tk.Listbox(popup, height=min(10, len(completions)))
        lb.pack()
        
        for item in completions:
            lb.insert(tk.END, item)
        
        def on_select(event):
            selected = lb.get(lb.curselection())
            self.delete(start_pos, 'insert')
            self.insert(start_pos, selected)
            popup.destroy()
        
        lb.bind('<Double-Button-1>', on_select)
        lb.bind('<Return>', on_select)
        
        def on_leave(event):
            popup.destroy()
        
        popup.bind('<FocusOut>', on_leave)
        lb.focus_set()

class ProjectGarry:
    def __init__(self, root):
        self.root = root
        self.root.title("GBox: Hooked")
        img = tk.PhotoImage(file='ChatGPT Image Jul 6, 2025, 09_00_23 PM.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        self.original_path = None
        self.project_path = None
        self.current_file_path = None
        self.dark_mode = False
        self.autosave = False

        self.frame = tk.Frame(root)
        self.frame.pack(fill='both', expand=True)

        self.search_frame = tk.Frame(self.frame)
        self.search_frame.pack(side='top', fill='x')

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=5, pady=2)

        self.search_btn = tk.Button(self.search_frame, text="Search", command=self.search_tree)
        self.search_btn.pack(side='left', padx=5)

        self.tree = ttk.Treeview(self.frame)
        self.tree.pack(side='left', fill='y')
        self.tree.bind("<<TreeviewSelect>>", self.on_file_select)

        self.right_frame = tk.Frame(self.frame)
        self.right_frame.pack(side='right', fill='both', expand=True)

        self.toolbar = tk.Frame(self.right_frame)
        self.toolbar.pack(fill='x')
        self.brush_color = (0, 0, 0)
        self.brush_size = 5
        self.colors = [
            (0, 0, 0), (255, 255, 255), (255, 0, 0),
            (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 165, 0), (128, 0, 128), (0, 255, 255)
        ]
        for c in self.colors:
            b = tk.Button(self.toolbar, bg="#%02x%02x%02x" % c, width=2, command=lambda col=c: self.set_brush_color(col))
            b.pack(side='left', padx=1)
        self.size_var = tk.IntVar(value=self.brush_size)
        size_box = ttk.Combobox(self.toolbar, values=[1, 3, 5, 10, 20], width=3, state="readonly", textvariable=self.size_var)
        size_box.pack(side='left', padx=5)
        size_box.bind("<<ComboboxSelected>>", lambda e: setattr(self, 'brush_size', self.size_var.get()))

        self.import_btn = tk.Button(self.toolbar, text="Import Image", command=self.import_image)
        self.import_btn.pack(side='left', padx=5)

        self.new_file_btn = tk.Button(self.toolbar, text="New File", command=self.create_new_file)
        self.new_file_btn.pack(side='left', padx=5)

        self.settings_btn = tk.Button(self.toolbar, text="Settings", command=self.open_settings)
        self.settings_btn.pack(side='left', padx=5)

        self.generate_json_btn = tk.Button(self.toolbar, text="Generate .json", command=self.generate_json)
        self.generate_json_btn.pack(side='left', padx=5)

        self.save_all_btn = tk.Button(self.toolbar, text="Save All", command=self.save_all_files)
        self.save_all_btn.pack(side='left', padx=5)

        self.png_to_vmt_btn = tk.Button(self.toolbar, text="PNG→VMT", command=self.convert_png_to_vmt)
        self.png_to_vmt_btn.pack(side='left', padx=5)

        self.model_convert_btn = tk.Button(self.toolbar, text="Convert Model", command=self.convert_model_format)
        self.model_convert_btn.pack(side='left', padx=5)

        self.image_info_label = tk.Label(self.right_frame, text="", anchor='w')
        self.image_info_label.pack(fill='x')

        self.text = CodeEditor(self.right_frame, wrap='none')
        self.text_scroll_x = tk.Scrollbar(self.right_frame, orient='horizontal', command=self.text.xview)
        self.text.configure(xscrollcommand=self.text_scroll_x.set)

        self.kv_frame = tk.Frame(self.right_frame)
        self.kv_widgets = []

        self.image_canvas = None
        self.image_obj = None
        self.img = None
        self.tkimg = None
        self.drawing = False

        self.loading_label = tk.Label(self.root, text="", fg="red")
        self.loading_label.pack()

        self.menubar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Create New Mod", command=self.create_new_mod)
        self.file_menu.add_command(label="Open Mod Folder", command=self.load_mod_folder)
        self.file_menu.add_command(label="Save File", command=self.save_file)
        self.file_menu.add_command(label="Add Folder", command=self.add_folder)
        self.file_menu.add_command(label="Export to GMod", command=self.export_to_gmod)
        self.file_menu.add_command(label="Package as Mod", command=self.package_as_mod)
        self.file_menu.add_command(label="Package as .pack", command=self.package_as_pack)
        self.file_menu.add_command(label="Export File", command=self.export_selected_file)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.root.config(menu=self.menubar)

    def convert_png_to_vmt(self):
        if not self.current_file_path or not self.current_file_path.lower().endswith('.png'):
            messagebox.showerror("Error", "Please select a PNG file first")
            return
        
        try:
            png_path = self.current_file_path
            base_name = os.path.splitext(os.path.basename(png_path))[0]
            vmt_path = os.path.join(os.path.dirname(png_path), f"{base_name}.vmt")
            
            vmt_content = f'''"UnlitGeneric"
{{
    "$basetexture" "materials/{os.path.splitext(os.path.relpath(png_path, self.project_path))[0]}"
    "$translucent" "1"
    "$nocull" "1"
}}'''
            
            with open(vmt_path, 'w') as f:
                f.write(vmt_content)
            
            self.tree.delete(*self.tree.get_children())
            self.build_tree(self.project_path, "")
            messagebox.showinfo("Success", f"Created VMT file at:\n{vmt_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create VMT:\n{str(e)}")

    def convert_model_format(self):
        if not self.current_file_path or not self.current_file_path.lower().endswith(('.obj', '.fbx', '.dae')):
            messagebox.showerror("Error", "Please select a model file first (OBJ/FBX/DAE)")
            return
        
        try:
            model_path = self.current_file_path
            base_name = os.path.splitext(os.path.basename(model_path))[0]
            output_dir = os.path.join(os.path.dirname(model_path), "converted_models")
            
            os.makedirs(output_dir, exist_ok=True)
            
            qc_content = f'''$modelname "{base_name}.mdl"
$cdmaterials "models/{base_name}/"
$bodygroup "body"
{{
    studio "{base_name}.smd"
}}
$sequence "idle" "{base_name}.smd"
$surfaceprop "default"
'''
            
            with open(os.path.join(output_dir, f"{base_name}.qc"), 'w') as f:
                f.write(qc_content)
            
            with open(os.path.join(output_dir, f"{base_name}.smd"), 'w') as f:
                f.write("version 1\nnodes\n0 \"root\" -1\nend\nskeleton\ntime 0\n0 0 0 0 0 0\nend\n")
            
            self.tree.delete(*self.tree.get_children())
            self.build_tree(self.project_path, "")
            messagebox.showinfo("Success", f"Created Valve model files in:\n{output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert model:\n{str(e)}")

    def create_new_mod(self):
        new_mod_window = tk.Toplevel(self.root)
        new_mod_window.title("Create New Mod")
        
        tk.Label(new_mod_window, text="Mod Name:").grid(row=0, column=0, padx=5, pady=5)
        mod_name_entry = tk.Entry(new_mod_window, width=30)
        mod_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(new_mod_window, text="Mod Type:").grid(row=1, column=0, padx=5, pady=5)
        mod_type_var = tk.StringVar(value="gamemode")
        mod_type_menu = ttk.Combobox(new_mod_window, textvariable=mod_type_var, state="readonly")
        mod_type_menu['values'] = ("gamemode", "addon", "tool", "weapon", "entity", "map")
        mod_type_menu.grid(row=1, column=1, padx=5, pady=5)

        def create_mod():
            
            
            mod_name = mod_name_entry.get()
            if not mod_name:
                messagebox.showerror("Error", "Please enter a mod name")
                return
                
            mod_type = mod_type_var.get()
            dest_folder = filedialog.askdirectory(title="Select Folder to Create Mod In")
            if not dest_folder:
                return
                
            mod_path = os.path.join(dest_folder, mod_name)
            if os.path.exists(mod_path):
                messagebox.showerror("Error", "Folder already exists")
                return
                
            os.makedirs(mod_path)
            
            folders = ["lua", "materials", "models", "sound", "particles", "scenes"]
            
            for folder in folders:
                os.makedirs(os.path.join(mod_path, folder), exist_ok=True)
                
            lua_path = os.path.join(mod_path, "lua")
            if mod_type == "gamemode":
                gamemode_path = os.path.join(lua_path, "gamemodes", mod_name)
                os.makedirs(gamemode_path)
                
                with open(os.path.join(gamemode_path, "cl_init.lua"), 'w') as f:
                    f.write(f"""-- Client initialization for {mod_name}
include("shared.lua")

function GM:Initialize()
end

function GM:Think()
end
""")
                
                with open(os.path.join(gamemode_path, "init.lua"), 'w') as f:
                    f.write(f"""-- Shared initialization for {mod_name}
AddCSLuaFile("cl_init.lua")
AddCSLuaFile("shared.lua")
include("shared.lua")

function GM:Initialize()
end
""")
                
                with open(os.path.join(gamemode_path, "shared.lua"), 'w') as f:
                    f.write(f"""-- Shared definitions for {mod_name}

GM.Name = "{mod_name}"
GM.Author = "You"
GM.Email = ""
GM.Website = ""

DeriveGamemode("base")
""")
                    
                with open(os.path.join(lua_path, "autorun", "client", f"{mod_name}_client.lua"), 'w') as f:
                    f.write(f"""-- Client autorun for {mod_name}
print("{mod_name} client loaded!")
""")
                    
                with open(os.path.join(lua_path, "autorun", "server", f"{mod_name}_server.lua"), 'w') as f:
                    f.write(f"""-- Server autorun for {mod_name}
print("{mod_name} server loaded!")
""")
                    
            elif mod_type == "addon":
                with open(os.path.join(lua_path, "autorun", "client", f"{mod_name}_client.lua"), 'w') as f:
                    f.write(f"""-- Client autorun for {mod_name}
print("{mod_name} client loaded!")
""")
                    
                with open(os.path.join(lua_path, "autorun", "server", f"{mod_name}_server.lua"), 'w') as f:
                    f.write(f"""-- Server autorun for {mod_name}
print("{mod_name} server loaded!")
""")
                    
            elif mod_type in ("tool", "weapon", "entity"):
                ent_folder = "entities" if mod_type == "entity" else "weapons" if mod_type == "weapon" else "tools"
                with open(os.path.join(lua_path, ent_folder, f"{mod_name}.lua"), 'w') as f:
                    if mod_type == "tool":
                        f.write(f"""-- Tool script for {mod_name}
TOOL.Category = "Your Category"
TOOL.Name = "{mod_name}"
TOOL.Command = nil
TOOL.ConfigName = ""

if CLIENT then
    language.Add("tool.{mod_name.lower()}.name", "{mod_name}")
    language.Add("tool.{mod_name.lower()}.desc", "Description")
    language.Add("tool.{mod_name.lower()}.0", "Left click to use")
end

TOOL.ClientConVar = {{
    ["example"] = "0"
}}

function TOOL:LeftClick(trace)
    if not trace.Hit then return false end
    if CLIENT then return true end
    
    return true
end
""")
                    elif mod_type == "weapon":
                        f.write(f"""-- Weapon script for {mod_name}
AddCSLuaFile()

SWEP.Base = "weapon_base"
SWEP.PrintName = "{mod_name}"
SWEP.Author = "You"
SWEP.Contact = ""
SWEP.Purpose = ""
SWEP.Instructions = ""

SWEP.Spawnable = true
SWEP.AdminSpawnable = false
SWEP.Category = "Your Category"

SWEP.Primary.ClipSize = -1
SWEP.Primary.DefaultClip = -1
SWEP.Primary.Automatic = false
SWEP.Primary.Ammo = "none"

SWEP.Secondary.ClipSize = -1
SWEP.Secondary.DefaultClip = -1
SWEP.Secondary.Automatic = false
SWEP.Secondary.Ammo = "none"

function SWEP:PrimaryAttack()
    self:SetNextPrimaryFire(CurTime() + 0.5)
    
    if CLIENT then return end
    
end
""")
                    else:
                        f.write(f"""-- Entity script for {mod_name}
AddCSLuaFile()

ENT.Type = "anim"
ENT.Base = "base_gmodentity"
ENT.PrintName = "{mod_name}"
ENT.Author = "You"
ENT.Contact = ""
ENT.Purpose = ""
ENT.Instructions = ""
ENT.Spawnable = true
ENT.AdminSpawnable = false

function ENT:Initialize()
    if SERVER then
        self:SetModel("models/props_junk/plasticbucket001a.mdl")
        self:PhysicsInit(SOLID_VPHYSICS)
        self:SetMoveType(MOVETYPE_VPHYSICS)
        self:SetSolid(SOLID_VPHYSICS)
        
        local phys = self:GetPhysicsObject()
        if phys:IsValid() then
            phys:Wake()
        end
    end
end
""")
            
            with open(os.path.join(mod_path, "addon.json"), 'w') as f:
                json.dump({
                    "title": mod_name,
                    "type": "gamemode" if mod_type == "gamemode" else "servercontent",
                    "tags": ["fun", "roleplay", "sandbox"],
                    "ignore": ["*.psd", "*.vcproj", "*.svn/"],
                    "description": f"My {mod_type} mod for Garry's Mod"
                }, f, indent=4)

            self.project_path = mod_path
            self.tree.delete(*self.tree.get_children())
            self.build_tree(self.project_path, "")
            new_mod_window.destroy()
            messagebox.showinfo("Success", f"Created new {mod_type} mod at:\n{mod_path}")

        create_button = tk.Button(new_mod_window, text="Create", command=create_mod)
        create_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_new_file(self):
        if not self.project_path:
            messagebox.showerror("Error", "No project loaded")
            return

        new_file_window = tk.Toplevel(self.root)
        new_file_window.title("Create New File")

        tk.Label(new_file_window, text="File Name:").grid(row=0, column=0, padx=5, pady=5)
        file_name_entry = tk.Entry(new_file_window, width=30)
        file_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(new_file_window, text="File Type:").grid(row=1, column=0, padx=5, pady=5)
        file_type_var = tk.StringVar(value=".lua")
        file_type_menu = ttk.Combobox(new_file_window, textvariable=file_type_var, state="readonly")
        file_type_menu['values'] = (".lua", ".txt", ".json", ".vmt", ".ini", ".png", ".jpg")
        file_type_menu.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(new_file_window, text="Location:").grid(row=2, column=0, padx=5, pady=5)
        location_var = tk.StringVar()
        location_entry = tk.Entry(new_file_window, textvariable=location_var, width=30)
        location_entry.grid(row=2, column=1, padx=5, pady=5)

        def browse_location():
            folder = filedialog.askdirectory(title="Select Folder", initialdir=self.project_path)
            if folder:
                location_var.set(os.path.relpath(folder, self.project_path))

        browse_btn = tk.Button(new_file_window, text="Browse", command=browse_location)
        browse_btn.grid(row=2, column=2, padx=5)

        def create_file():
            file_name = file_name_entry.get()
            if not file_name:
                messagebox.showerror("Error", "Please enter a file name")
                return

            file_type = file_type_var.get()
            if not file_name.endswith(file_type):
                file_name += file_type

            location = location_var.get()
            if not location:
                location = ""

            full_path = os.path.join(self.project_path, location, file_name)
            if os.path.exists(full_path):
                messagebox.showerror("Error", "File already exists")
                return

            try:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    if file_type == ".lua":
                        f.write("-- New Lua script\n")
                    elif file_type == ".json":
                        f.write("{\n    \n}\n")
                    elif file_type == ".vmt":
                        f.write('""\n{\n    "$basetexture" ""\n}\n')
                    elif file_type == ".ini":
                        f.write("[Section]\nkey=value\n")

                self.tree.delete(*self.tree.get_children())
                self.build_tree(self.project_path, "")
                new_file_window.destroy()
                messagebox.showinfo("Success", f"Created new file: {file_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file: {str(e)}")

        tk.Button(new_file_window, text="Create", command=create_file).grid(row=3, column=0, columnspan=3, pady=10)

    def generate_json(self):
        if not self.project_path:
            messagebox.showerror("Error", "No project folder loaded")
            return

        json_window = tk.Toplevel(self.root)
        json_window.title("Generate .json")

        tk.Label(json_window, text="Mod Title:").grid(row=0, column=0, sticky='w')
        title_entry = tk.Entry(json_window, width=40)
        title_entry.grid(row=0, column=1)

        tk.Label(json_window, text="Author:").grid(row=1, column=0, sticky='w')
        author_entry = tk.Entry(json_window, width=40)
        author_entry.grid(row=1, column=1)

        tk.Label(json_window, text="Description:").grid(row=2, column=0, sticky='w')
        desc_entry = tk.Entry(json_window, width=40)
        desc_entry.grid(row=2, column=1)

        tk.Label(json_window, text="Type:").grid(row=3, column=0, sticky='w')
        type_var = tk.StringVar(value="servercontent")
        type_menu = ttk.Combobox(json_window, textvariable=type_var, values=["gamemode", "servercontent", "tool", "map"], state="readonly")
        type_menu.grid(row=3, column=1)

        def generate():
            json_data = {
                "title": title_entry.get() or "My GMod Mod",
                "type": type_var.get(),
                "tags": ["fun"],
                "ignore": ["*.psd", "*.vcproj", "*.svn/"],
                "author": author_entry.get() or "Unknown",
                "description": desc_entry.get() or "A Garry's Mod addon"
            }

            json_path = os.path.join(self.project_path, "addon.json")
            try:
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=4)
                messagebox.showinfo("Success", f"Created addon.json at:\n{json_path}")
                json_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create addon.json:\n{str(e)}")

        tk.Button(json_window, text="Generate", command=generate).grid(row=4, column=0, columnspan=2, pady=10)

    def save_all_files(self):
        if not self.project_path:
            messagebox.showerror("Error", "No project folder loaded")
            return

        self.loading_label.config(text="Saving all files...")
        self.root.update()

        def do_save():
            try:
                if self.current_file_path and os.path.isfile(self.current_file_path):
                    self.save_file()

                for root, dirs, files in os.walk(self.project_path):
                    for file in files:
                        if file.endswith(('.json', '.vmt', '.ini')):
                            file_path = os.path.join(root, file)
                            try:
                                if file.endswith('.json'):
                                    with open(file_path, 'r') as f:
                                        data = json.load(f)
                                    with open(file_path, 'w') as f:
                                        json.dump(data, f, indent=4)
                                elif file.endswith('.vmt'):
                                    with open(file_path, 'r') as f:
                                        lines = f.readlines()
                                    with open(file_path, 'w') as f:
                                        f.writelines(lines)
                                elif file.endswith('.ini'):
                                    config = configparser.ConfigParser()
                                    config.read(file_path)
                                    with open(file_path, 'w') as f:
                                        config.write(f)
                            except:
                                continue

                self.loading_label.config(text="")
                messagebox.showinfo("Success", "All files saved successfully")
            except Exception as e:
                self.loading_label.config(text="")
                messagebox.showerror("Error", f"Failed to save all files:\n{str(e)}")

        threading.Thread(target=do_save).start()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        dark_mode_cb = tk.Checkbutton(settings_window, text="Dark Mode", variable=dark_mode_var, 
                                    command=lambda: self.toggle_dark_mode(dark_mode_var.get()))
        dark_mode_cb.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        autosave_var = tk.BooleanVar(value=self.autosave)
        autosave_cb = tk.Checkbutton(settings_window, text="Enable Autosave", variable=autosave_var,
                                    command=lambda: setattr(self, 'autosave', autosave_var.get()))
        autosave_cb.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        tk.Label(settings_window, text="Editor Font Size:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        font_size_var = tk.StringVar(value="10")
        font_size_spin = tk.Spinbox(settings_window, from_=8, to=24, textvariable=font_size_var)
        font_size_spin.grid(row=2, column=1, sticky='w', padx=5, pady=5)

        def apply_font_size():
            try:
                size = int(font_size_var.get())
                self.text.config(font=('TkFixedFont', size))
            except:
                pass

        tk.Button(settings_window, text="Apply Font Size", command=apply_font_size).grid(row=2, column=2, padx=5)

        tk.Button(settings_window, text="Close", command=settings_window.destroy).grid(row=3, column=0, columnspan=3, pady=10)

    def toggle_dark_mode(self, enabled):
        self.dark_mode = enabled
        if enabled:
            self.root.configure(bg='#2d2d2d')
            self.text.configure(bg='#1e1e1e', fg='#ffffff', insertbackground='white')
            self.frame.configure(bg='#2d2d2d')
            self.right_frame.configure(bg='#2d2d2d')
            self.toolbar.configure(bg='#2d2d2d')
        else:
            self.root.configure(bg='#f0f0f0')
            self.text.configure(bg='white', fg='black', insertbackground='black')
            self.frame.configure(bg='#f0f0f0')
            self.right_frame.configure(bg='#f0f0f0')
            self.toolbar.configure(bg='#f0f0f0')

    def set_brush_color(self, color):
        self.brush_color = color

    def import_image(self):
        if not self.current_file_path or not self.current_file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            messagebox.showwarning("Warning", "No image selected to replace.")
            return
        new_img_path = filedialog.askopenfilename(title="Select Image to Import", filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if not new_img_path:
            return
        try:
            shutil.copy(new_img_path, self.current_file_path)
            self.load_image_editor(self.current_file_path)
            messagebox.showinfo("Replaced", "Image replaced successfully.")
        except:
            messagebox.showerror("Error", "Failed to replace the image.")

    def add_folder(self):
        if not self.project_path:
            return
        folder_name = filedialog.askdirectory(title="Select Folder to Add")
        if not folder_name:
            return
        dest = os.path.join(self.project_path, os.path.basename(folder_name))
        if os.path.exists(dest):
            messagebox.showerror("Error", "Folder already exists in project.")
            return
        try:
            shutil.copytree(folder_name, dest)
            self.tree.delete(*self.tree.get_children())
            self.build_tree(self.project_path, "")
            messagebox.showinfo("Added", f"Folder added: {os.path.basename(folder_name)}")
        except:
            messagebox.showerror("Error", "Failed to add folder.")

    def load_mod_folder(self):
        selected_path = filedialog.askdirectory()
        if not selected_path:
            return
        self.original_path = selected_path
        folder_name = os.path.basename(selected_path)
        parent_dir = os.path.dirname(selected_path)
        working_path = os.path.join(parent_dir, folder_name + "_working")
        make_copy = messagebox.askyesno("Working Copy", "Create a working copy to edit without changing the original?")
        if make_copy:
            self.loading_label.config(text="Creating working copy, please wait...")
            self.root.update()
            def do_copy():
                if os.path.exists(working_path):
                    shutil.rmtree(working_path)
                shutil.copytree(selected_path, working_path)
                self.project_path = working_path
                self.loading_label.config(text="")
                self.tree.delete(*self.tree.get_children())
                self.build_tree(self.project_path, "")
            threading.Thread(target=do_copy).start()
        else:
            self.project_path = selected_path
            self.tree.delete(*self.tree.get_children())
            self.build_tree(self.project_path, "")

    def build_tree(self, path, parent):
        try:
            items = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
        except:
            items = []
        for item in items:
            full_path = os.path.join(path, item)
            node = self.tree.insert(parent, 'end', text=item, open=False)
            if os.path.isdir(full_path):
                self.build_tree(full_path, node)

    def on_file_select(self, event):
        for w in self.kv_frame.winfo_children():
            w.destroy()
        self.kv_widgets.clear()
        self.kv_frame.pack_forget()
        self.text.pack_forget()
        self.text_scroll_x.pack_forget()
        self.image_info_label.config(text="")
        if self.image_canvas:
            self.image_canvas.pack_forget()
            self.image_canvas = None
        item = self.tree.selection()
        if not item:
            return
        path_parts = []
        node = item[0]
        while node:
            path_parts.insert(0, self.tree.item(node)["text"])
            node = self.tree.parent(node)
        file_path = os.path.join(self.project_path, *path_parts)
        self.current_file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        if os.path.isfile(file_path):
            try:
                if ext == ".json" or ext == ".vmt":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    data = {}
                    for line in lines:
                        line = line.strip()
                        if '"' in line:
                            parts = line.split('"')
                            if len(parts) >= 4:
                                key = parts[1]
                                val = parts[3]
                                data[key] = val
                            elif len(parts) >= 3:
                                key = parts[1]
                                val = parts[2].strip()
                                data[key] = val
                    self.kv_frame.pack(fill='both', expand=True)
                    self.load_kv_editor(data)
                elif ext == ".ini":
                    config = configparser.ConfigParser()
                    config.read(file_path)
                    data = {}
                    for section in config.sections():
                        for key in config[section]:
                            data[f"{section}.{key}"] = config[section][key]
                    self.kv_frame.pack(fill='both', expand=True)
                    self.load_kv_editor(data)
                elif ext in (".png", ".jpg", ".jpeg"):
                    self.load_image_editor(file_path)
                elif ext == ".bin":
                    with open(file_path, 'rb') as f:
                        try:
                            content = f.read().decode('utf-8')
                        except:
                            f.seek(0)
                            content = base64.b64encode(f.read()).decode('utf-8')
                    self.text.delete(1.0, tk.END)
                    self.text.insert(tk.END, content)
                    self.text.pack(fill='both', expand=True)
                    self.text_scroll_x.pack(fill='x')
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.text.delete(1.0, tk.END)
                    self.text.insert(tk.END, content)
                    self.text.pack(fill='both', expand=True)
                    self.text_scroll_x.pack(fill='x')
            except:
                self.text.delete(1.0, tk.END)
                self.text.insert(tk.END, "[UNREADABLE FILE]")
                self.text.pack(fill='both', expand=True)

    def load_kv_editor(self, data):
        for i, (key, val) in enumerate(data.items()):
            k = tk.Label(self.kv_frame, text=key, cursor="hand2")
            k.grid(row=i, column=0, sticky='w')
            e = tk.Entry(self.kv_frame, width=60)
            e.insert(0, val)
            e.grid(row=i, column=1, sticky='w')
            self.kv_widgets.append((key, e))
            def on_double_click(event, key=key):
                if '.' in key:
                    name, subkey = key.split('.', 1)
                else:
                    name, subkey = key, "(none)"
                popup = tk.Toplevel(self.root)
                popup.title("Key Details")
                tk.Label(popup, text=f"Name: {name}").pack(padx=10, pady=5)
                tk.Label(popup, text=f"Subkey: {subkey}").pack(padx=10, pady=5)
                tk.Button(popup, text="Close", command=popup.destroy).pack(pady=10)
            k.bind("<Double-Button-1>", on_double_click)
            self.apply_theme_widgets(self.kv_frame)

    def load_image_editor(self, path):
        self.img = Image.open(path).convert("RGBA")
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.image_info_label.config(text=f"Image: {self.img.width}x{self.img.height}")
        if not self.image_canvas:
            self.image_canvas = tk.Canvas(self.right_frame, width=self.img.width, height=self.img.height)
            self.image_obj = self.image_canvas.create_image(0, 0, anchor="nw", image=self.tkimg)
            self.image_canvas.bind("<B1-Motion>", self.paint)
            self.image_canvas.bind("<ButtonPress-1>", self.start_paint)
            self.image_canvas.bind("<ButtonRelease-1>", self.stop_paint)
            self.image_canvas.pack(fill='both', expand=True)
        else:
            self.image_canvas.config(width=self.img.width, height=self.img.height)
            self.image_canvas.itemconfig(self.image_obj, image=self.tkimg)

    def start_paint(self, event):
        self.drawing = True
        self.paint(event)

    def stop_paint(self, event):
        self.drawing = False

    def paint(self, event):
        if not self.drawing:
            return
        x = int(event.x)
        y = int(event.y)
        r = self.brush_size
        pxmin = max(0, x - r)
        pxmax = min(self.img.width, x + r)
        pymin = max(0, y - r)
        pymax = min(self.img.height, y + r)
        for px in range(pxmin, pxmax):
            for py in range(pymin, pymax):
                dx = px - x
                dy = py - y
                if dx * dx + dy * dy <= r * r:
                    self.img.putpixel((px, py), self.brush_color + (255,))
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.image_canvas.itemconfig(self.image_obj, image=self.tkimg)

    def save_file(self):
        if not self.current_file_path:
            return
        ext = os.path.splitext(self.current_file_path)[1].lower()
        try:
            if self.kv_widgets:
                data = {}
                for key, entry in self.kv_widgets:
                    data[key] = entry.get()
                if ext == ".json":
                    with open(self.current_file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4)
                elif ext == ".vmt":
                    with open(self.current_file_path, 'w', encoding='utf-8') as f:
                        f.write('""\n')
                        for key, val in data.items():
                            f.write(f'    "{key}" "{val}"\n')
                        f.write('""\n')
                elif ext == ".ini":
                    config = configparser.ConfigParser()
                    for full_key, val in data.items():
                        if '.' in full_key:
                            section, key = full_key.split('.', 1)
                        else:
                            section, key = 'DEFAULT', full_key
                        if section not in config:
                            config[section] = {}
                        config[section][key] = val
                    with open(self.current_file_path, 'w', encoding='utf-8') as f:
                        config.write(f)
            elif ext in (".png", ".jpg", ".jpeg") and self.img:
                self.img.save(self.current_file_path)
                messagebox.showinfo("Saved", "Image saved.")
            else:
                content = self.text.get(1.0, tk.END)
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            if ext not in (".png", ".jpg", ".jpeg"):
                messagebox.showinfo("Saved", "File saved.")
        except:
            messagebox.showerror("Error", "Failed to save.")

    def export_to_gmod(self):
        if not self.project_path:
            return
        gamemode_name = os.path.basename(self.project_path)
        gmod_path = filedialog.askdirectory(title="Select garrysmod/addons folder")
        if not gmod_path:
            return
        dest_path = os.path.join(gmod_path, gamemode_name)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        shutil.copytree(self.project_path, dest_path)
        messagebox.showinfo("Exported", f"Exported to {dest_path}")

    def package_as_mod(self):
        if not self.project_path:
            messagebox.showerror("Error", "No mod folder loaded.")
            return

        package_window = tk.Toplevel(self.root)
        package_window.title("Package As Mod")

        tk.Label(package_window, text="Mod Name:").grid(row=0, column=0, sticky='w')
        name_entry = tk.Entry(package_window, width=40)
        name_entry.grid(row=0, column=1)

        tk.Label(package_window, text="Author:").grid(row=1, column=0, sticky='w')
        author_entry = tk.Entry(package_window, width=40)
        author_entry.grid(row=1, column=1)

        tk.Label(package_window, text="Description:").grid(row=2, column=0, sticky='w')
        desc_entry = tk.Entry(package_window, width=40)
        desc_entry.grid(row=2, column=1)

        thumbnail_path = tk.StringVar()

        def select_thumbnail():
            file_path = filedialog.askopenfilename(title="Select Thumbnail", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
            if file_path:
                thumbnail_path.set(file_path)

        tk.Button(package_window, text="Choose Thumbnail", command=select_thumbnail).grid(row=3, column=0, columnspan=2)

        def confirm_package():
            dest_folder = filedialog.askdirectory(title="Select Folder to Save Mod")
            if not dest_folder:
                return

            self.loading_label.config(text="Packing mod... This may take a few minutes...")
            self.root.update()

            def do_package():
                mod_name = name_entry.get() or "My GMod Mod"
                full_path = os.path.join(dest_folder, mod_name)
                if os.path.exists(full_path):
                    shutil.rmtree(full_path)
                shutil.copytree(self.project_path, full_path)

                addon_data = {
                    "title": mod_name,
                    "type": "servercontent",
                    "tags": ["fun"],
                    "ignore": [".psd", ".vcproj", ".svn/"],
                    "author": author_entry.get(),
                    "description": desc_entry.get()
                }

                with open(os.path.join(full_path, "addon.json"), 'w', encoding='utf-8') as f:
                    json.dump(addon_data, f, indent=4)

                thumb_dest = os.path.join(full_path, "icon.png")
                if thumbnail_path.get():
                    try:
                        shutil.copy(thumbnail_path.get(), thumb_dest)
                    except:
                        pass

                self.loading_label.config(text="")
                messagebox.showinfo("Packaged", f"Addon packaged and saved to:\n{full_path}")
                package_window.destroy()

            threading.Thread(target=do_package).start()

        tk.Button(package_window, text="Package", command=confirm_package).grid(row=4, column=0, columnspan=2, pady=10)

    def package_as_pack(self):
        if not self.project_path:
            messagebox.showerror("Error", "No mod folder loaded.")
            return

        pack_window = tk.Toplevel(self.root)
        pack_window.title("Package as .pack")

        tk.Label(pack_window, text="Mod Name:").grid(row=0, column=0, sticky='w')
        name_entry = tk.Entry(pack_window, width=40)
        name_entry.grid(row=0, column=1)

        def confirm_package():
            dest_file = filedialog.asksaveasfilename(
                title="Save .pack File",
                defaultextension=".pack",
                filetypes=[("Pack Files", "*.pack")]
            )
            if not dest_file:
                return

            self.loading_label.config(text="Creating .pack file...")
            self.root.update()

            def do_package():
                mod_name = name_entry.get() or "MyGModMod"
                with zipfile.ZipFile(dest_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(self.project_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, self.project_path)
                            zipf.write(file_path, arcname)

                self.loading_label.config(text="")
                messagebox.showinfo("Packaged", f"Pack file created:\n{dest_file}")
                pack_window.destroy()

            threading.Thread(target=do_package).start()

        tk.Button(pack_window, text="Create .pack", command=confirm_package).grid(row=1, column=0, columnspan=2, pady=10)

    def export_selected_file(self):
        if not self.current_file_path or not os.path.isfile(self.current_file_path):
            messagebox.showwarning("Warning", "Please select a valid file from the tree.")
            return
        dest_folder = filedialog.askdirectory(title="Select Destination Folder")
        if not dest_folder:
            return
        try:
            dest_path = os.path.join(dest_folder, os.path.basename(self.current_file_path))
            shutil.copy2(self.current_file_path, dest_path)
            messagebox.showinfo("Exported", f"File exported to:\n{dest_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file:\n{str(e)}")

    def search_tree(self):
        pass

    def apply_theme_widgets(self, parent):
        pass

def test_lua_code(self):
    """Execute the current Lua code in a Lua interpreter"""
    if not self.current_file_path or not self.current_file_path.lower().endswith('.lua'):
        messagebox.showerror("Error", "Please select a Lua file first")
        return
    
    try:
        import lupa
        from lupa import LuaRuntime
    except ImportError:
        messagebox.showerror("Error", "Lupa module not found. Install it with: pip install lupa")
        return
    
    try:
        lua = LuaRuntime()
        
       
        lua_code = self.text.get("1.0", tk.END)
        
        
        output_window = tk.Toplevel(self.root)
        output_window.title("Lua Test Output")
        
        output_text = tk.Text(output_window, wrap='word', height=20, width=80)
        output_scroll = tk.Scrollbar(output_window, command=output_text.yview)
        output_text.configure(yscrollcommand=output_scroll.set)
        
        output_scroll.pack(side='right', fill='y')
        output_text.pack(fill='both', expand=True)
        
        def lua_print(*args):
            output_text.insert(tk.END, ' '.join(str(arg) for arg in args) + '\n')
            output_text.see(tk.END)
        
        lua.globals().print = lua_print
        
        # Execute the code
        output_text.insert(tk.END, f"-- Testing {os.path.basename(self.current_file_path)} --\n")
        try:
            lua.execute(lua_code)
            output_text.insert(tk.END, "\n-- Execution completed successfully --\n")
        except Exception as e:
            output_text.insert(tk.END, f"\n-- Error: {str(e)} --\n")
        
        output_text.configure(state='disabled')
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to execute Lua code:\n{str(e)}")
root = tk.Tk()
app = ProjectGarry(root)
root.mainloop()