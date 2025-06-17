import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import threading
import time
import pickle
from pynput import mouse, keyboard
import pydirectinput

# --- CONFIGURATION ---
pydirectinput.FAILSAFE = False
pydirectinput.PAUSE = 0

# Map for Virtual-Key codes to friendly names
VK_MAP = {
    96: 'numpad0', 97: 'numpad1', 98: 'numpad2', 99: 'numpad3', 100: 'numpad4',
    101: 'numpad5', 102: 'numpad6', 103: 'numpad7', 104: 'numpad8', 105: 'numpad9',
    106: '*', 107: '+', 109: '-', 110: '.', 111: '/'
}

# --- Core Classes for Recording and Playback ---

class MacroEvent:
    def __init__(self, event_type, details, timestamp):
        self.event_type = event_type
        self.details = details
        self.timestamp = timestamp
    def __repr__(self):
        return f"MacroEvent({self.event_type}, {self.details}, {self.timestamp})"

class MacroManagerCore:
    def __init__(self):
        self.recording = False
        self.playing = False
        self.recorded_events = []
        self.start_time = 0
        self.mouse_listener = None
        self.playback_thread = None

    def start_recording(self):
        if self.recording: return
        self.recording = True
        self.recorded_events = []
        self.start_time = time.time()
        self.mouse_listener = mouse.Listener(on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll)
        self.mouse_listener.start()

    def stop_recording(self):
        if not self.recording: return
        self.recording = False
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener.join()

    def start_playing(self, events, repetitions, on_complete_callback):
        if self.playing or not events: return
        self.playing = True
        self.playback_thread = threading.Thread(target=self._playback_loop, args=(events, repetitions, on_complete_callback), daemon=True)
        self.playback_thread.start()

    def stop_playing(self):
        self.playing = False

    def _smooth_move(self, end_pos, duration):
        start_pos = pydirectinput.position()
        start_time = time.time()
        if duration <= 0:
            pydirectinput.moveTo(end_pos[0], end_pos[1])
            return
        while True:
            if not self.playing: break
            elapsed = time.time() - start_time
            if elapsed >= duration: break
            t = elapsed / duration
            new_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
            new_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
            pydirectinput.moveTo(int(new_x), int(new_y))
            time.sleep(0.001)
        if self.playing:
            pydirectinput.moveTo(end_pos[0], end_pos[1])

    # --- MOUSE WHEEL FIX (LOGIC) ---: Rewritten playback loop
    def _playback_loop(self, events, repetitions, on_complete_callback):
        for i in range(repetitions):
            if not self.playing: break
            last_event_time = 0
            for event in events:
                if not self.playing: break
                
                delay = event.timestamp - last_event_time
                
                # If the event is a click, use the delay time to move the mouse.
                # This correctly handles both single clicks and the movement part of a drag.
                if event.event_type == 'click':
                    self._smooth_move(event.details['pos'], duration=delay)
                else:
                    # For all other events (scrolls, key presses), the delay is just a pause.
                    time.sleep(delay)

                if not self.playing: break
                
                self._execute_event_action(event)
                last_event_time = event.timestamp
        
        self.playing = False
        if on_complete_callback: on_complete_callback()

    # --- MOUSE WHEEL FIX (ACTION) ---: Updated scroll action
    def _execute_event_action(self, event):
        etype, details = event.event_type, event.details
        try:
            if etype == 'click':
                # The mouse is already in position from the main loop's _smooth_move
                button_str = details['button'].name
                if details['pressed']:
                    pydirectinput.mouseDown(button=button_str)
                else:
                    pydirectinput.mouseUp(button=button_str)

            elif etype == 'scroll':
                # Instantly move to the scroll position, as it's not handled by the main loop
                pydirectinput.moveTo(details['pos'][0], details['pos'][1])
                
                if details['dy'] != 0:
                    pydirectinput.scroll(details['dy'])
                if details['dx'] != 0:
                    pydirectinput.hscroll(details['dx'])

            elif etype == 'press' or etype == 'release':
                key_str = self._get_key_string(details['key'])
                if key_str:
                    if etype == 'press':
                        pydirectinput.keyDown(key_str)
                    else:
                        pydirectinput.keyUp(key_str)
        except Exception as e:
            print(f"Could not execute event action {event}: {e}")

    def _get_key_string(self, key):
        if hasattr(key, 'vk') and key.vk in VK_MAP:
            return VK_MAP[key.vk]
        if hasattr(key, 'name'):
            return key.name
        if hasattr(key, 'char'):
            return key.char
        return None

    def _add_event(self, event_type, **details):
        if not self.recording: return
        timestamp = time.time() - self.start_time
        self.recorded_events.append(MacroEvent(event_type, details, timestamp))

    def _on_move(self, x, y): pass
    def _on_click(self, x, y, button, pressed): self._add_event('click', pos=(x, y), button=button, pressed=pressed)
    def _on_scroll(self, x, y, dx, dy): self._add_event('scroll', pos=(x, y), dx=dx, dy=dy)
    def _on_press(self, key): self._add_event('press', key=key)
    def _on_release(self, key): self._add_event('release', key=key)

# --- UI Application Class (No changes needed in this class) ---

class MacroManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Manager")
        self.root.geometry("500x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.core = MacroManagerCore()
        self.loaded_macros = {}
        self.hotkeys = {
            'start_record': {keyboard.Key.f9},
            'stop_record': {keyboard.Key.f10},
            'start_play': {keyboard.Key.f11},
            'stop_play': {keyboard.Key.f12},
        }
        self.hotkey_listener_thread = None
        self.current_pressed_keys = set()
        self.callback_queue = []
        self.is_changing_hotkey = False
        self.action_to_change = None
        self.new_hotkey_set = set()

        self._setup_ui()
        self.update_status("Ready. Press a hotkey.")
        self.start_hotkey_listener()
        self.process_callbacks()

    def process_callbacks(self):
        while self.callback_queue:
            callback = self.callback_queue.pop(0)
            callback()
        self.root.after(100, self.process_callbacks)

    def queue_callback(self, func, *args, **kwargs):
        self.callback_queue.append(lambda: func(*args, **kwargs))

    def _setup_ui(self):
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        macro_list_frame = tk.Frame(self.root, padx=10, pady=5)
        macro_list_frame.pack(fill=tk.BOTH, expand=True)
        hotkey_frame = tk.Frame(self.root, padx=10, pady=10, relief=tk.RIDGE, borderwidth=2)
        hotkey_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        status_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(control_frame, text="Repetitions:").grid(row=0, column=0, sticky=tk.W)
        self.repetitions_var = tk.StringVar(value="1")
        self.repetitions_entry = tk.Entry(control_frame, textvariable=self.repetitions_var, width=5)
        self.repetitions_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.play_button = tk.Button(control_frame, text="Play Selected Macro", command=self.play_macro)
        self.play_button.grid(row=0, column=2, padx=10)
        tk.Label(macro_list_frame, text="Loaded Macros:").pack(anchor=tk.W)
        self.macro_listbox = tk.Listbox(macro_list_frame)
        self.macro_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))
        scrollbar = tk.Scrollbar(macro_list_frame, orient=tk.VERTICAL, command=self.macro_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.macro_listbox.config(yscrollcommand=scrollbar.set)
        list_button_frame = tk.Frame(macro_list_frame)
        list_button_frame.pack(fill=tk.Y, side=tk.LEFT, padx=(5,0))
        tk.Button(list_button_frame, text="Load Macro", command=self.load_macro_from_file).pack(pady=2, fill=tk.X)
        tk.Button(list_button_frame, text="Save Recording", command=self.save_macro_to_file).pack(pady=2, fill=tk.X)
        tk.Button(list_button_frame, text="Remove Selected", command=self.remove_selected_macro).pack(pady=2, fill=tk.X)
        tk.Label(hotkey_frame, text="Hotkeys:", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        self.hotkey_labels = {}
        self.hotkey_change_buttons = {}
        hotkey_actions = ['start_record', 'stop_record', 'start_play', 'stop_play']
        hotkey_display = ['Start Recording:', 'Stop Recording:', 'Start Playback:', 'Stop Playback:']
        for i, (action, display) in enumerate(zip(hotkey_actions, hotkey_display)):
            tk.Label(hotkey_frame, text=display).grid(row=i+1, column=0, sticky=tk.W, padx=5, pady=2)
            self.hotkey_labels[action] = tk.Label(hotkey_frame, text=self.get_hotkey_str(action), fg="blue", width=20, anchor='w')
            self.hotkey_labels[action].grid(row=i+1, column=1, sticky=tk.W)
            change_button = tk.Button(hotkey_frame, text="Change", command=lambda act=action: self.initiate_hotkey_change(act))
            change_button.grid(row=i+1, column=2, sticky=tk.E, padx=5)
            self.hotkey_change_buttons[action] = change_button
        self.status_label = tk.Label(status_frame, text="", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, padx=5)

    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()

    def get_hotkey_str(self, action_or_keyset):
        if isinstance(action_or_keyset, str):
            keys = self.hotkeys.get(action_or_keyset)
        else:
            keys = action_or_keyset
        if not keys: return "Not Set"
        key_names = []
        for k in keys:
            if hasattr(k, 'vk') and k.vk in VK_MAP:
                key_names.append(VK_MAP[k.vk])
            elif hasattr(k, 'name'):
                key_names.append(k.name)
            elif hasattr(k, 'char') and k.char:
                key_names.append(k.char)
            else:
                key_names.append(str(k).replace("'", ""))
        return ' + '.join(sorted(key_names))

    def start_hotkey_listener(self):
        self.hotkey_listener_thread = threading.Thread(target=self._hotkey_listen_loop, daemon=True)
        self.hotkey_listener_thread.start()

    def _hotkey_listen_loop(self):
        with keyboard.Listener(on_press=self._on_hotkey_press, on_release=self._on_hotkey_release) as listener:
            listener.join()

    def _on_hotkey_press(self, key):
        if self.core.recording:
            self.core._on_press(key)
        if self.is_changing_hotkey:
            self.new_hotkey_set.add(key)
            display_text = self.get_hotkey_str(self.new_hotkey_set)
            self.queue_callback(self.hotkey_labels[self.action_to_change].config, text=display_text)
            return
        
        self.current_pressed_keys.add(key)
        for action, keys in self.hotkeys.items():
            if keys and keys.issubset(self.current_pressed_keys):
                if action == 'start_record' and not self.core.recording and not self.core.playing:
                    self.queue_callback(self.start_recording)
                elif action == 'stop_record' and self.core.recording:
                    self.queue_callback(self.stop_recording)
                elif action == 'start_play' and not self.core.playing and not self.core.recording:
                    self.queue_callback(self.play_macro)
                elif action == 'stop_play' and self.core.playing:
                    self.queue_callback(self.stop_playing)

    def _on_hotkey_release(self, key):
        if self.core.recording:
            self.core._on_release(key)
        if self.is_changing_hotkey:
            if key == keyboard.Key.esc:
                self.queue_callback(self.cancel_hotkey_change)
            else:
                self.queue_callback(self.finalize_hotkey_change)
            return
        if key in self.current_pressed_keys:
            self.current_pressed_keys.remove(key)
    
    def _toggle_ui_for_hotkey_change(self, is_changing):
        state = tk.DISABLED if is_changing else tk.NORMAL
        self.play_button.config(state=state)
        for action, button in self.hotkey_change_buttons.items():
            if is_changing and action != self.action_to_change:
                button.config(state=tk.DISABLED)
            else:
                button.config(state=tk.NORMAL)
    def initiate_hotkey_change(self, action_to_change):
        if self.is_changing_hotkey: return
        self.is_changing_hotkey = True
        self.action_to_change = action_to_change
        self.new_hotkey_set = set()
        self.update_status(f"Listening for new hotkey... Press the desired key combination, then release. Press ESC to cancel.", "blue")
        self.hotkey_labels[action_to_change].config(text="Listening...", fg="red")
        self._toggle_ui_for_hotkey_change(True)
    def finalize_hotkey_change(self):
        if not self.is_changing_hotkey: return
        if not self.new_hotkey_set:
            self.cancel_hotkey_change()
            return
        for action, keyset in self.hotkeys.items():
            if action != self.action_to_change and keyset == self.new_hotkey_set:
                messagebox.showerror("Duplicate Hotkey", f"This key combination is already used for '{self.get_hotkey_str(action)}'.")
                self.cancel_hotkey_change()
                return
        self.hotkeys[self.action_to_change] = self.new_hotkey_set.copy()
        new_text = self.get_hotkey_str(self.action_to_change)
        self.hotkey_labels[self.action_to_change].config(text=new_text, fg="blue")
        self.update_status(f"Hotkey for '{self.action_to_change.replace('_', ' ')}' set to: {new_text}", "green")
        self.reset_hotkey_change_state()
    def cancel_hotkey_change(self):
        if not self.is_changing_hotkey: return
        original_text = self.get_hotkey_str(self.action_to_change)
        self.hotkey_labels[self.action_to_change].config(text=original_text, fg="blue")
        self.update_status("Hotkey change cancelled.", "black")
        self.reset_hotkey_change_state()
    def reset_hotkey_change_state(self):
        self.is_changing_hotkey = False
        self.action_to_change = None
        self.new_hotkey_set = set()
        self._toggle_ui_for_hotkey_change(False)
    def start_recording(self):
        if self.core.playing: self.update_status("Cannot record while playing.", "red"); return
        if self.core.recording: return
        self.update_status("Recording... Press hotkey to stop.", "red")
        self.core.start_recording()
    def stop_recording(self):
        if not self.core.recording: return
        self.core.stop_recording()
        self.update_status(f"Recording stopped. {len(self.core.recorded_events)} events captured.", "green")
        if not self.core.recorded_events:
            messagebox.showinfo("Empty Recording", "No keyboard or mouse actions were recorded.")
            return
        name = simpledialog.askstring("Save Recording", "Enter a name for this new macro:", parent=self.root)
        if name:
            self.loaded_macros[name] = self.core.recorded_events
            self._update_macro_listbox()
            self.macro_listbox.selection_set(self.macro_listbox.size() - 1)
        self.core.recorded_events = []
    def play_macro(self):
        if self.core.recording: self.update_status("Cannot play while recording.", "red"); return
        if self.core.playing: self.update_status("Already playing a macro.", "blue"); return
        selected_indices = self.macro_listbox.curselection()
        if not selected_indices: messagebox.showwarning("No Macro Selected", "Please select a macro from the list to play."); return
        macro_name = self.macro_listbox.get(selected_indices[0])
        events_to_play = self.loaded_macros.get(macro_name)
        try:
            repetitions = int(self.repetitions_var.get())
            if repetitions < 1: raise ValueError
        except ValueError: messagebox.showerror("Invalid Input", "Repetitions must be a positive integer."); return
        self.update_status(f"Playing '{macro_name}' ({repetitions}x)... Press hotkey to stop.", "blue")
        self.core.start_playing(events_to_play, repetitions, lambda: self.queue_callback(self._on_playback_complete))
    def stop_playing(self):
        if not self.core.playing: return
        self.core.stop_playing()
    def _on_playback_complete(self):
        self.update_status("Playback finished.", "green")
    def save_macro_to_file(self):
        selected_indices = self.macro_listbox.curselection()
        if not selected_indices:
            if self.core.recorded_events:
                events_to_save, default_name = self.core.recorded_events, "new_macro"
            else: messagebox.showwarning("No Macro Selected", "Please select a macro to save, or make a new recording."); return
        else:
            macro_name = self.macro_listbox.get(selected_indices[0])
            events_to_save, default_name = self.loaded_macros.get(macro_name), macro_name
        filepath = filedialog.asksaveasfilename(defaultextension=".macro", filetypes=[("Macro Files", "*.macro"), ("All Files", "*.*")], initialfile=default_name)
        if not filepath: return
        try:
            with open(filepath, 'wb') as f: pickle.dump(events_to_save, f)
            self.update_status(f"Macro saved to {filepath}", "green")
        except Exception as e: messagebox.showerror("Save Error", f"Failed to save macro file:\n{e}")
    def load_macro_from_file(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Macro Files", "*.macro"), ("All Files", "*.*")])
        if not filepaths: return
        for filepath in filepaths:
            try:
                with open(filepath, 'rb') as f: events = pickle.load(f)
                base_name = filepath.split('/')[-1].replace('.macro', '')
                name, count = base_name, 1
                while name in self.loaded_macros: name = f"{base_name}_{count}"; count += 1
                self.loaded_macros[name] = events
                self.update_status(f"Loaded macro '{name}'", "green")
            except Exception as e: messagebox.showerror("Load Error", f"Failed to load macro file:\n{filepath}\n\n{e}")
        self._update_macro_listbox()
    def remove_selected_macro(self):
        selected_indices = self.macro_listbox.curselection()
        if not selected_indices: messagebox.showwarning("No Macro Selected", "Please select a macro to remove."); return
        macro_name = self.macro_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove '{macro_name}' from the list?"):
            del self.loaded_macros[macro_name]
            self._update_macro_listbox()
            self.update_status(f"Removed '{macro_name}'.", "green")
    def _update_macro_listbox(self):
        self.macro_listbox.delete(0, tk.END)
        for name in sorted(self.loaded_macros.keys()): self.macro_listbox.insert(tk.END, name)
    def _on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.core.stop_recording(); self.core.stop_playing(); self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroManagerApp(root)
    root.mainloop()