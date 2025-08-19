#Author: PatchesTheMerchant
#Among Us Undetectable (AUU)
 
import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import pymem
import os
import sys
import subprocess
from PIL import Image, ImageTk
import time
import ctypes
from ctypes import wintypes
 
class MemoryReader:
    def __init__(self, root, process_name):
        self.root = root
        self.icon_path = self.resource_path("aupp.ico")
        try:
            root.iconbitmap(self.icon_path)
        except tk.TclError:
            pass  # Icon file not found, continue without icon
        self.process_name = process_name
        self.base_adderess = None
        self.auto_update_thread = None
        self.auto_update_flag = threading.Event()
        self.auto_update_interval = tk.DoubleVar(value=0.1)  # Default interval set to 0.1 second
        self.toggle_state = tk.BooleanVar(value=False)
        self.update_names_flag = False
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Legacy offsets (may be outdated)
        self.steam_offset = 0x0295D3AC
        self.epic_offset = 0x0327E990
        
        # Newer offset (from v2020.8.12s, may be patched)
        self.new_role_offset = 0xE22924
        self.new_offset_chain = [0x24, 0x218, 0xC, 0x5C, 0x0, 0x34, 0x28]

        # Add platform selection
        self.platform_var = "None"
        
        # Cosmetic unlock variables
        self.cosmetic_hook_active = False
        self.original_bytes = None
        self.hook_address = None
        
        # Configure dark mode theme
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="white")
        self.style.configure("TCheckbutton", background="#2b2b2b", foreground="white")
        self.style.configure("Horizontal.TScale", background="#2b2b2b", foreground="white")
        self.style.configure("TButton", background="#2b2b2b", foreground="white")
        self.style.configure("TRadiobutton", background="#2b2b2b", foreground="white")
 
        self.roles = {
            0: "Crewmate",
            1: "Impostor",
            2: "Scientist",
            3: "Engineer",
            4: "Guardian Angel",
            5: "Shapeshifter",
            6: "Dead",
            7: "Dead (Imp)",
            8: "Noise Maker",
            9: "Phantom",
            10: "Tracker"
        }
        self.alive_roles = set(self.roles.keys())
        self.player_states = {}  # Dictionary to store player states
        
        self.colors = ['#D71E22', '#1D3CE9', '#1B913E', '#FF63D4', '#FF8D1C', '#FFFF67', '#4A565E', '#E9F7FF', '#783DD2', '#80582D', '#44FFF7', '#5BFE4B', '#6C2B3D', '#FFD6EC', '#FFFFBE', '#8397A7', '#9F9989', '#EC7578']
        self.colornames = ['Red', 'Blue', 'Green', 'Pink', 'Orange', 'Yellow', 'Black', 'White', 'Purple', 'Brown', 'Cyan', 'Lime', 'Maroon', 'Rose', 'Banana', 'Grey', 'Tan', 'Coral']
        self.output_text = tk.Text(root, height=15, width=50, bg='#1c1c1c', fg='white', insertbackground='white', highlightbackground='#2b2b2b', highlightcolor='#2b2b2b')
        self.output_text.pack(padx=10, pady=10)
        for color_hex, color_tag in zip(self.colors, self.colornames):
            self.output_text.tag_configure(color_tag, foreground=color_hex)
 
        self.output_text.tag_configure('gray', foreground='gray')
        self.output_text.tag_configure('imp', foreground='red')
        self.footer_label = ttk.Label(root, text="0: Close   ||   1: Read Players   ||   2:Radar-ON   ||   3:Radar-OFF   ||   4: Force Impostor   ||   5: Unlock Cosmetics   ||   9: PANIC! (delete)")
        self.output_text.insert(tk.END,"* Start Among Us\n* Start a game\n* Press 1 to know who the Impostors are!\n* Press 2 to enable Radar\n* Press 3 to disable Radar\n* Press 4 to force yourself to be Impostor\n* Press 5 to unlock all cosmetics\n* Press 9 to PANIC (delete this cheat)")
        self.footer_label.pack(side='bottom', fill='x')
 
        # Frame for slider and toggle
        self.slider_frame = ttk.Frame(root)
        self.slider_frame.pack(pady=10)
 
        # Create slider for auto-update interval
        self.slider_label = ttk.Label(self.slider_frame, text="Radar-update speed:")
        self.slider_label.pack(side=tk.LEFT)
        self.slider = ttk.Scale(self.slider_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL, variable=self.auto_update_interval)
        self.slider.pack(side=tk.LEFT, padx=10)
 
        # Create toggle switch for enabling/disabling auto-update prompt
        self.toggle_button = ttk.Checkbutton(self.slider_frame, text="Auto Radar", variable=self.toggle_state, command=self.toggle_auto_update)
        self.toggle_button.pack(side=tk.LEFT)
 
        # Button to read players
        self.style.configure("BlackText.TButton", foreground="black")
        self.read_button = ttk.Button(self.slider_frame, text="Read Players", command=self.update_names, style="BlackText.TButton")
        self.read_button.pack(side=tk.LEFT, padx=10)
        
        # Button to unlock cosmetics
        self.cosmetic_button = ttk.Button(self.slider_frame, text="Unlock Cosmetics", command=self.toggle_cosmetic_unlock, style="BlackText.TButton")
        self.cosmetic_button.pack(side=tk.LEFT, padx=10)
        self.auto_update_names()
        
                # Load the Polus image
        polus_path = self.resource_path("Polus.png")
        try:
            self.polus_image = Image.open(polus_path)
            self.polus_tk = ImageTk.PhotoImage(self.polus_image)
            canvas_width = self.polus_image.width
            canvas_height = self.polus_image.height
            has_background_image = True
        except (FileNotFoundError, IOError):
            # Image file not found, use default canvas size
            self.polus_image = None
            self.polus_tk = None
            canvas_width = 800
            canvas_height = 600
            has_background_image = False

        # Create a canvas for plotting
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg='#2b2b2b', highlightthickness=0)
        self.canvas.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Add the map image as a background layer if available
        if has_background_image:
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor='nw', image=self.polus_tk)
        else:
            self.image_on_canvas = None
 
        # Bind resize event
        self.canvas.bind("<Configure>", self.on_resize)
 
    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
 
    def identify_platform(self):
        pm = pymem.Pymem("Among Us.exe")
        module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
        module_base_address = module.lpBaseOfDll
 
        try:
            # Try Epic first
            epic_offset_addr = pm.read_ulonglong(module_base_address + self.epic_offset)
            # Probe for a valid pointer
            pm.read_ulonglong(epic_offset_addr + 0xB8)
            return "epic"
        except:
            try:
                # Try Steam fallback
                steam_offset_addr = pm.read_uint(module_base_address + self.steam_offset)
                pm.read_uint(steam_offset_addr + 0x5C)
                return "steam"
            except:
                return "unknown"
        finally:
            pm.close_process()
 
    def find_base_address(self):
        self.platform_var = self.identify_platform()
        pm = pymem.Pymem("Among Us.exe")
        module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
        module_base_address = module.lpBaseOfDll
 
        if self.platform_var == "steam":
            add_offset = pm.read_uint(module_base_address + self.steam_offset)
            self.base_address = pm.read_uint(add_offset + 0x5C)
            self.base_address = pm.read_uint(self.base_address)
        elif self.platform_var == "epic":
            add_offset = pm.read_ulonglong(module_base_address + self.epic_offset)
            self.base_address = pm.read_ulonglong(add_offset + 0xB8)
            self.base_address = pm.read_ulonglong(self.base_address)
        else:
            return
        pm.close_process()
 
    def find_impostors(self):
        if self.identify_platform() == "steam":
            return self.find_impostors_steam()
        elif self.identify_platform() == "epic":
            return self.find_impostors_epic()
        else:
            return
        
    def find_impostors_steam(self):
        players = []
        try:
            pm = pymem.Pymem("Among Us.exe")
            allclients_ptr = pm.read_uint(self.base_address + 0x38)
            items_ptr = pm.read_uint(allclients_ptr + 0x8)
            items_count = pm.read_uint(allclients_ptr + 0xC)
            for i in range(items_count):
                item_base = pm.read_uint(items_ptr + 0x10 + (i * 4))
 
                item_char_ptr = pm.read_uint(item_base + 0x10)
                item_data_ptr = pm.read_uint(item_char_ptr + 0x58)
                item_role_ptr = pm.read_uint(item_data_ptr + 0x4C)
                item_role = pm.read_uint(item_role_ptr + 0x10)
                role_name = self.roles.get(item_role, item_role)
 
                rigid_body_2d = pm.read_uint(item_char_ptr + 0xD0)
                rigid_body_2d_cached = pm.read_uint(rigid_body_2d + 0x8)
                item_x_val = pm.read_float(rigid_body_2d_cached + 0x7C)
                item_y_val = pm.read_float(rigid_body_2d_cached + 0x80)
 
                item_color_id = pm.read_uint(item_base + 0x28)
                coordinates = (item_x_val, item_y_val, item_color_id)
                if role_name == "Dead" or role_name == "Dead (Imp)" or role_name == "Guardian Angel":
                    coordinates = (0, 0, item_color_id)
                item_name_ptr = pm.read_uint(item_base + 0x1C)
                item_name_length = pm.read_uint(item_name_ptr + 0x8)
                item_name_address = item_name_ptr + 0xC
                raw_name_bytes = pm.read_bytes(item_name_address, item_name_length * 2)
                item_name = raw_name_bytes.decode('utf-16').rstrip('\x00')
 
                player_details = f"{item_name:10} | {self.colornames[item_color_id]:7} | "
                players.append((player_details, role_name, coordinates))
                
                # Update player state
                self.player_states[item_name] = role_name in self.alive_roles
 
            pm.close_process()
            return players
        except:
            pm.close_process()
            return players
    
    def find_impostors_epic(self):
        players = []
        try:
            pm = pymem.Pymem("Among Us.exe")
            allclients_ptr = pm.read_ulonglong(self.base_address + 0x58)
 
            items_ptr = pm.read_ulonglong(allclients_ptr + 0x10)
            items_count = pm.read_uint(allclients_ptr + 0x18)
            for i in range(items_count):
                item_base = pm.read_ulonglong(items_ptr + 0x20 + (i * 8))
                item_char_ptr = pm.read_ulonglong(item_base + 0x18)
                item_data_ptr = pm.read_ulonglong(item_char_ptr + 0x78)
                item_role_ptr = pm.read_ulonglong(item_data_ptr + 0x68)
                item_role = pm.read_uint(item_role_ptr + 0x20)
                role_name = self.roles.get(item_role, item_role)
 
                rigid_body_2d = pm.read_ulonglong(item_char_ptr + 0x148)
                rigid_body_2d_cached = pm.read_ulonglong(rigid_body_2d + 0x10)
                item_x_val = pm.read_float(rigid_body_2d_cached + 0xB0)
                item_y_val = pm.read_float(rigid_body_2d_cached + 0xB4)
 
                item_color_id = pm.read_uint(item_base + 0x48)
                coordinates = (item_x_val, item_y_val, item_color_id)
                if role_name == "Dead" or role_name == "Dead (Imp)" or role_name == "Guardian Angel":
                    coordinates = (0, 0, item_color_id)
                item_name_ptr = pm.read_ulonglong(item_base + 0x30)
                item_name_length = pm.read_uint(item_name_ptr + 0x10)
                item_name_address = item_name_ptr + 0x14
                raw_name_bytes = pm.read_bytes(item_name_address, item_name_length * 2)
                item_name = raw_name_bytes.decode('utf-16').rstrip('\x00')
 
                player_details = f"{item_name:10} | {self.colornames[item_color_id]:7} | "
                players.append((player_details, role_name, coordinates))
                # Update player state
                self.player_states[item_name] = role_name in self.alive_roles
 
            pm.close_process()
            return players
        except:
            pm.close_process()
            return players
 
    def read_memory(self):
        self.find_base_address()
        players = self.find_impostors()
 
        x_values = []
        y_values = []
        color_values = []
        dead_players = []
 
        for player_details, role_name, (playerx, playery, playercolor) in players:
            x_values.append(playerx)
            y_values.append(playery)
            color_values.append(self.colors[playercolor])
            if role_name == "Dead":
                dead_players.append((playerx, playery))
 
        self.update_plot(x_values, y_values, color_values, dead_players,)
 
        if self.update_names_flag:
            self.output_text.delete('1.0', tk.END)  # Clear existing text
            for player_details, role_name, (playerx, playery, playercolor) in players:
                if role_name in ["Shapeshifter", "Impostor", "Phantom"]:
                    self.output_text.insert(tk.END, f"{player_details}", self.colornames[playercolor])
                    self.output_text.insert(tk.END, f"{role_name}\n", 'imp')
                elif role_name in ["Dead", "Dead (Imp)", "Guardian Angel"]:
                    self.output_text.insert(tk.END, f"{player_details} {role_name}\n", 'gray')
                else:
                    self.output_text.insert(tk.END, f"{player_details}", self.colornames[playercolor])
                    self.output_text.insert(tk.END, f"{role_name}\n")
            self.update_names_flag = False
 
    def update_plot(self, x_values, y_values, color_values, dead_players):
        self.canvas.delete("overlay")  # Clear the previous plot, but keep the background image
 
        for x, y, color in zip(x_values, y_values, color_values):
            canvas_x = self.map_x_to_canvas(x)
            canvas_y = self.map_y_to_canvas(y)
            self.canvas.create_oval(canvas_x - 10, canvas_y - 10, canvas_x + 10, canvas_y + 10, fill=color, outline=color, tag="overlay")
 
        # Draw black circles over dead players
        for x, y in dead_players:
            canvas_x = self.map_x_to_canvas(x)
            canvas_y = self.map_y_to_canvas(y)
            self.canvas.create_oval(canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5, fill='black', outline='black', tag="overlay")
 
    def map_x_to_canvas(self, x):
        return (x - 0.474) / (40.85 - 0.474) * self.canvas.winfo_width()
 
    def map_y_to_canvas(self, y):
        # Invert the y-axis
        return self.canvas.winfo_height() - (y + 26.1) / (26.1 - 0.39) * self.canvas.winfo_height()
 
    def on_resize(self, event):
        # Resize the image and redraw (only if background image exists)
        if self.polus_image is not None and self.image_on_canvas is not None:
            self.polus_tk = ImageTk.PhotoImage(self.polus_image.resize((event.width, event.height), Image.Resampling.LANCZOS))
            self.canvas.itemconfig(self.image_on_canvas, image=self.polus_tk)
        self.update_plot([], [], [], [])  # Clear and redraw everything
 
    def auto_update(self):
        while self.auto_update_flag.is_set():
            self.read_memory()
            time.sleep(self.auto_update_interval.get())
 
    def enable_auto_update(self):
        self.auto_update_flag.set()
        if self.auto_update_thread is None or not self.auto_update_thread.is_alive():
            self.auto_update_thread = threading.Thread(target=self.auto_update)
            self.auto_update_thread.start()
 
    def disable_auto_update(self):
        self.auto_update_flag.clear()
        if self.auto_update_thread is not None:
            self.auto_update_thread.join()
        self.auto_update_thread = None
 
    def toggle_auto_update(self):
        if self.toggle_state.get():
            if not self.auto_update_flag.is_set():
                self.enable_auto_update()
        else:
            self.disable_auto_update()
 
    def update_names(self):
        self.update_names_flag = True
        self.read_memory()
    
    def auto_update_names(self):
        def run():
            while True:
                self.update_names()
                time.sleep(5)  # 5 seconds interval
        threading.Thread(target=run, daemon=True).start()
    
    def force_impostor_role(self):
        """Force your own player to become impostor"""
        try:
            pm = pymem.Pymem("Among Us.exe")
            
            # Try newer offset method first
            if self._try_new_impostor_method(pm):
                pm.close_process()
                self.output_text.insert(tk.END, "Successfully forced impostor role (new method)!\n", 'imp')
                return
            
            # Fall back to legacy method
            self.find_base_address()
            
            if self.platform_var == "steam":
                self._force_impostor_steam(pm)
            elif self.platform_var == "epic":
                self._force_impostor_epic(pm)
            else:
                self.output_text.insert(tk.END, "Unknown platform - cannot force impostor role\n")
                return
                
            pm.close_process()
            self.output_text.insert(tk.END, "Successfully forced impostor role (legacy method)!\n", 'imp')
        except Exception as e:
            try:
                pm.close_process()
            except:
                pass
            self.output_text.insert(tk.END, f"Failed to force impostor role: {str(e)}\n")
            self.output_text.insert(tk.END, "Note: Offsets may be outdated. Game might have been updated.\n")
    
    def _force_impostor_steam(self, pm):
        """Force impostor role for Steam version"""
        allclients_ptr = pm.read_uint(self.base_address + 0x38)
        items_ptr = pm.read_uint(allclients_ptr + 0x8)
        items_count = pm.read_uint(allclients_ptr + 0xC)
        
        # Find your own player (usually the first one or local player)
        for i in range(items_count):
            item_base = pm.read_uint(items_ptr + 0x10 + (i * 4))
            item_char_ptr = pm.read_uint(item_base + 0x10)
            item_data_ptr = pm.read_uint(item_char_ptr + 0x58)
            item_role_ptr = pm.read_uint(item_data_ptr + 0x4C)
            
            # Check if this is the local player (you can modify this logic)
            # For now, we'll force the first player to be impostor
            if i == 0:  # Assuming first player is you
                pm.write_uint(item_role_ptr + 0x10, 1)  # 1 = Impostor role
                break
    
    def _force_impostor_epic(self, pm):
        """Force impostor role for Epic version"""
        allclients_ptr = pm.read_ulonglong(self.base_address + 0x58)
        items_ptr = pm.read_ulonglong(allclients_ptr + 0x10)
        items_count = pm.read_uint(allclients_ptr + 0x18)
        
        # Find your own player (usually the first one or local player)
        for i in range(items_count):
            item_base = pm.read_ulonglong(items_ptr + 0x20 + (i * 8))
            item_char_ptr = pm.read_ulonglong(item_base + 0x18)
            item_data_ptr = pm.read_ulonglong(item_char_ptr + 0x78)
            item_role_ptr = pm.read_ulonglong(item_data_ptr + 0x68)
            
            # Check if this is the local player
            # For now, we'll force the first player to be impostor
            if i == 0:  # Assuming first player is you
                pm.write_uint(item_role_ptr + 0x20, 1)  # 1 = Impostor role
                break

    def _try_new_impostor_method(self, pm):
        """Try the newer offset method for forcing impostor role"""
        try:
            # Get GameAssembly.dll base address
            module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
            game_assembly_base = module.lpBaseOfDll
            
            # Start with the base offset
            current_address = game_assembly_base + self.new_role_offset
            
            # Follow the pointer chain
            for i, offset in enumerate(self.new_offset_chain):
                if i == len(self.new_offset_chain) - 1:
                    # Last offset - this is where we write the role value
                    role_address = current_address + offset
                    
                    # Write impostor role (1 = impostor, 0 = crew, 257 = ghost)
                    pm.write_uint(role_address, 1)
                    return True
                else:
                    # Read the pointer and continue the chain
                    try:
                        current_address = pm.read_ulonglong(current_address + offset)
                    except:
                        # Try 32-bit read if 64-bit fails
                        current_address = pm.read_uint(current_address + offset)
                        
            return True
            
        except Exception as e:
            # If this method fails, we'll fall back to legacy method
            self.output_text.insert(tk.END, f"New method failed: {str(e)}. Trying legacy method...\n")
            return False

    def toggle_cosmetic_unlock(self):
        """Toggle cosmetic unlock on/off"""
        if self.cosmetic_hook_active:
            self.disable_cosmetic_unlock()
        else:
            self.enable_cosmetic_unlock()
    
    def enable_cosmetic_unlock(self):
        """Enable cosmetic unlock by hooking GetPurchase function"""
        try:
            pm = pymem.Pymem("Among Us.exe")
            
            # Get GameAssembly.dll base address
            module = pymem.process.module_from_name(pm.process_handle, "GameAssembly.dll")
            game_assembly_base = module.lpBaseOfDll
            
            # GetPurchase function RVA (this may need updating for different game versions)
            get_purchase_rva = 0x7827D0
            self.hook_address = game_assembly_base + get_purchase_rva
            
            # Read original bytes
            self.original_bytes = pm.read_bytes(self.hook_address, 5)
            
            # Create hook shellcode that returns 1 (true)
            # mov eax, 1; ret
            hook_code = b'\xB8\x01\x00\x00\x00\xC3'  # mov eax, 1; ret
            
            # Allocate memory for our hook
            kernel32 = ctypes.windll.kernel32
            hook_memory = kernel32.VirtualAllocEx(
                pm.process_handle,
                None,
                len(hook_code),
                0x3000,  # MEM_COMMIT | MEM_RESERVE
                0x40     # PAGE_EXECUTE_READWRITE
            )
            
            if not hook_memory:
                raise Exception("Failed to allocate memory for hook")
            
            # Write our hook code to allocated memory
            pm.write_bytes(hook_memory, hook_code, len(hook_code))
            
            # Calculate relative jump address
            relative_addr = hook_memory - self.hook_address - 5
            
            # Create jump instruction (JMP relative)
            jump_instruction = b'\xE9' + relative_addr.to_bytes(4, byteorder='little', signed=True)
            
            # Change memory protection to allow writing
            old_protect = ctypes.c_ulong()
            kernel32.VirtualProtectEx(
                pm.process_handle,
                self.hook_address,
                5,
                0x40,  # PAGE_EXECUTE_READWRITE
                ctypes.byref(old_protect)
            )
            
            # Write the jump instruction
            pm.write_bytes(self.hook_address, jump_instruction, len(jump_instruction))
            
            # Restore original protection
            kernel32.VirtualProtectEx(
                pm.process_handle,
                self.hook_address,
                5,
                old_protect.value,
                ctypes.byref(old_protect)
            )
            
            self.cosmetic_hook_active = True
            self.cosmetic_button.configure(text="Disable Cosmetics")
            self.output_text.insert(tk.END, "Cosmetic unlock enabled! All items should now be unlocked.\n", 'imp')
            
            pm.close_process()
            
        except Exception as e:
            try:
                pm.close_process()
            except:
                pass
            self.output_text.insert(tk.END, f"Failed to enable cosmetic unlock: {str(e)}\n")
            self.output_text.insert(tk.END, "Note: This feature may not work with current game version. RVA offset may need updating.\n")
    
    def disable_cosmetic_unlock(self):
        """Disable cosmetic unlock by restoring original bytes"""
        if not self.cosmetic_hook_active or not self.original_bytes or not self.hook_address:
            return
            
        try:
            pm = pymem.Pymem("Among Us.exe")
            
            # Change memory protection
            kernel32 = ctypes.windll.kernel32
            old_protect = ctypes.c_ulong()
            kernel32.VirtualProtectEx(
                pm.process_handle,
                self.hook_address,
                5,
                0x40,  # PAGE_EXECUTE_READWRITE
                ctypes.byref(old_protect)
            )
            
            # Restore original bytes
            pm.write_bytes(self.hook_address, self.original_bytes, len(self.original_bytes))
            
            # Restore original protection
            kernel32.VirtualProtectEx(
                pm.process_handle,
                self.hook_address,
                5,
                old_protect.value,
                ctypes.byref(old_protect)
            )
            
            self.cosmetic_hook_active = False
            self.cosmetic_button.configure(text="Unlock Cosmetics")
            self.output_text.insert(tk.END, "Cosmetic unlock disabled. Original function restored.\n")
            
            pm.close_process()
            
        except Exception as e:
            try:
                pm.close_process()
            except:
                pass
            self.output_text.insert(tk.END, f"Failed to disable cosmetic unlock: {str(e)}\n")

    def on_close(self):
        self.toggle_state.set(False)
        self.disable_auto_update()
        if self.cosmetic_hook_active:
            self.disable_cosmetic_unlock()
        self.root.destroy()
 
def update(memory_reader):
    threading.Thread(target=memory_reader.read_memory).start()
 
def on_close(root, memory_reader):
    memory_reader.disable_auto_update()
    root.destroy()
 
def self_delete():
    executable_name = os.path.basename(sys.executable)
    prefetch_name = f"{executable_name.upper()}-*.pf"
    prefetch_dir = r"C:\Windows\prefetch"
    delete_command = (
        f"cmd /c ping localhost -n 3 > nul & "
        f"del /f /q \"{sys.executable}\" & "
        f"del /f /q \"{os.path.join(prefetch_dir, prefetch_name)}\""
    )
    subprocess.Popen(delete_command, shell=True)
    root.destroy()
 
root = tk.Tk()
root.title("Bebes Hacks Brushan")
root.configure(bg='#2b2b2b')
root.geometry("480x620")
 
memory_reader = MemoryReader(root, "Among Us.exe")
 
keyboard.add_hotkey('1', lambda: memory_reader.update_names())
keyboard.add_hotkey('0', lambda: on_close(root, memory_reader))
keyboard.add_hotkey('9', lambda: self_delete())
keyboard.add_hotkey('2', lambda: [memory_reader.toggle_state.set(True), memory_reader.toggle_auto_update()])
keyboard.add_hotkey('3', lambda: [memory_reader.toggle_state.set(False), memory_reader.toggle_auto_update()])
keyboard.add_hotkey('4', lambda: memory_reader.force_impostor_role())
keyboard.add_hotkey('5', lambda: memory_reader.toggle_cosmetic_unlock())
 
root.mainloop()