
#!/usr/bin/env python3
"""
Chat Player (Desktop) - Tkinter app
Save as chat_player.py and run with: python chat_player.py

Features:
- Paste or load a conversation script.
  * Lines can be "A: Hello" or "B: Hi" (explicit speakers),
    or plain lines (will be interpreted as alternating A/B).
- Choose which side you will play (A or B).
- Start session and use "Next" to progress:
  * Other party's lines are shown automatically.
  * When it's your turn, you get a text entry to type your reply.
  * You can optionally "Reveal expected" to see the scripted line.
- Save/load conversation files (.json) and export session log as text.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import json
import os
import sys
from datetime import datetime

APP_TITLE = "Chat Player - Desktop"

def parse_script_text(text):
    """
    Parse raw script text into a list of (speaker, message) pairs.
    Acceptable input:
      - Lines starting with 'A:' or 'B:' -> use those speakers.
      - Otherwise, lines are assigned alternating speakers starting with A.
    Empty lines are ignored.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    parsed = []
    alt = 'A'
    for ln in lines:
        if not ln:
            continue
        if ln.upper().startswith('A:') or ln.upper().startswith('B:'):
            sp = ln[0].upper()
            msg = ln[2:].strip()
            parsed.append((sp, msg))
        else:
            parsed.append((alt, ln))
            alt = 'B' if alt == 'A' else 'A'
    return parsed

class ChatPlayerApp:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("900x600")
        # Data
        self.script = []  # list of (speaker, message)
        self.user_side = 'A'
        self.index = 0
        self.session_log = []  # list of dicts with timestamp, speaker, expected, user_response (if any), shown
        # UI
        self.build_ui()

    def build_ui(self):
        # Top controls frame
        top = tk.Frame(self.root, pady=6)
        top.pack(fill='x')

        lbl = tk.Label(top, text="Script (each line 'A: message' or 'B: message' or plain alternating):")
        lbl.pack(anchor='w', padx=6)

        # Script text area with scroll
        self.script_text = tk.Text(self.root, height=10, wrap='word')
        self.script_text.pack(fill='x', padx=6)
        # Add small toolbar buttons under script
        toolbar = tk.Frame(self.root)
        toolbar.pack(fill='x', padx=6, pady=4)
        tk.Button(toolbar, text="Load Script", command=self.load_script).pack(side='left')
        tk.Button(toolbar, text="Save Script", command=self.save_script).pack(side='left', padx=4)
        tk.Button(toolbar, text="Clear Script", command=lambda: self.script_text.delete('1.0','end')).pack(side='left')
        tk.Button(toolbar, text="Parse Script", command=self.parse_from_text).pack(side='left', padx=6)

        # Left: options, Right: player
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=6, pady=6)

        left = tk.Frame(main_frame, width=300)
        left.pack(side='left', fill='y')
        right = tk.Frame(main_frame)
        right.pack(side='right', fill='both', expand=True)

        # Left controls
        tk.Label(left, text="Player side:").pack(anchor='w')
        self.side_var = tk.StringVar(value='A')
        tk.Radiobutton(left, text="Play A", variable=self.side_var, value='A').pack(anchor='w')
        tk.Radiobutton(left, text="Play B", variable=self.side_var, value='B').pack(anchor='w')

        tk.Button(left, text="Start Session", command=self.start_session).pack(fill='x', pady=8)
        tk.Button(left, text="Next ▶", command=self.next_turn).pack(fill='x')

        tk.Button(left, text="Reveal Expected / Toggle", command=self.toggle_reveal).pack(fill='x', pady=6)
        self.reveal_var = tk.BooleanVar(value=False)
        tk.Checkbutton(left, text="Auto reveal expected lines", variable=self.reveal_var).pack(anchor='w')

        tk.Label(left, text="Session controls:", pady=8).pack(anchor='w')
        tk.Button(left, text="Save session log", command=self.save_session_log).pack(fill='x')
        tk.Button(left, text="Export session as text", command=self.export_session_text).pack(fill='x', pady=4)
        tk.Button(left, text="Load script from file", command=self.load_script).pack(fill='x')

        tk.Label(left, text="", pady=6).pack()
        tk.Label(left, text="Shortcuts:").pack(anchor='w')
        tk.Label(left, text="Start: Ctrl+S   Next: Ctrl+N   Save log: Ctrl+L").pack(anchor='w')

        # Right: Player display
        display_frame = tk.Frame(right, bd=1, relief='sunken', padx=8, pady=8)
        display_frame.pack(fill='both', expand=True)

        self.turn_label = tk.Label(display_frame, text="Not started", font=('Arial', 14, 'bold'))
        self.turn_label.pack(anchor='w')

        self.show_area = tk.Text(display_frame, height=8, wrap='word', state='disabled', font=('Arial', 12))
        self.show_area.pack(fill='both', expand=False, pady=6)

        # User input area
        tk.Label(display_frame, text="Your reply (when it's your turn):").pack(anchor='w')
        self.user_entry = tk.Text(display_frame, height=6, wrap='word')
        self.user_entry.pack(fill='x', pady=4)

        entry_toolbar = tk.Frame(display_frame)
        entry_toolbar.pack(fill='x')
        tk.Button(entry_toolbar, text="Send (Next)", command=self.next_turn).pack(side='left')
        tk.Button(entry_toolbar, text="Clear", command=lambda: self.user_entry.delete('1.0','end')).pack(side='left', padx=4)
        tk.Button(entry_toolbar, text="Show expected", command=self.show_expected_dialog).pack(side='left', padx=6)

        # Session log display
        tk.Label(display_frame, text="Session log (latest at bottom):").pack(anchor='w', pady=(8,0))
        self.log_area = tk.Text(display_frame, height=8, wrap='word', state='disabled')
        self.log_area.pack(fill='both', expand=True, pady=4)

        # Keyboard shortcuts
        self.root.bind_all("<Control-s>", lambda e: self.start_session())
        self.root.bind_all("<Control-S>", lambda e: self.start_session())
        self.root.bind_all("<Control-n>", lambda e: self.next_turn())
        self.root.bind_all("<Control-N>", lambda e: self.next_turn())
        self.root.bind_all("<Control-l>", lambda e: self.save_session_log())
        self.root.bind_all("<Control-L>", lambda e: self.save_session_log())

    def load_script(self):
        path = filedialog.askopenfilename(title="Open script file", filetypes=[("JSON scripts","*.json"),("Text files","*.txt"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
            # Try JSON first
            try:
                obj = json.loads(data)
                if isinstance(obj, list):
                    # obj is list of pairs or dicts
                    parsed = []
                    for item in obj:
                        if isinstance(item, list) and len(item)>=2:
                            parsed.append((item[0], item[1]))
                        elif isinstance(item, dict) and 'speaker' in item and 'message' in item:
                            parsed.append((item['speaker'], item['message']))
                    if parsed:
                        self.script = parsed
                        self.populate_script_text_from_parsed()
                        messagebox.showinfo("Loaded", f"Loaded script ({len(parsed)} lines) from JSON.")
                        return
                # fallback: treat as plain text
            except Exception:
                pass
            # treat as plain text
            self.script_text.delete('1.0','end')
            self.script_text.insert('1.0', data)
            messagebox.showinfo("Loaded", "Script loaded into editor. Click 'Parse Script' to parse it.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_script(self):
        parsed = parse_script_text(self.script_text.get('1.0','end'))
        if not parsed:
            messagebox.showwarning("No script", "There is no script to save (or parsing produced zero lines).")
            return
        path = filedialog.asksaveasfilename(title="Save script as JSON", defaultextension=".json", filetypes=[("JSON scripts","*.json"),("Text files","*.txt")])
        if not path:
            return
        try:
            # Save as JSON list of dicts
            tosave = [{"speaker": s, "message": m} for s,m in parsed]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(tosave, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Saved", f"Script saved as JSON ({len(parsed)} lines).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save script: {e}")

    def parse_from_text(self):
        raw = self.script_text.get('1.0','end')
        parsed = parse_script_text(raw)
        if not parsed:
            messagebox.showwarning("No lines", "No valid lines found in the script.")
            return
        self.script = parsed
        messagebox.showinfo("Parsed", f"Parsed script: {len(parsed)} lines. Choose side and click Start Session.")
        self.populate_script_text_from_parsed()

    def populate_script_text_from_parsed(self):
        # update the script_text with explicit A:/B: lines for clarity
        self.script_text.delete('1.0','end')
        for s,m in self.script:
            self.script_text.insert('end', f"{s}: {m}\n")

    def start_session(self):
        if not self.script:
            # try parse from text
            self.parse_from_text()
            if not self.script:
                return
        self.user_side = self.side_var.get()
        self.index = 0
        self.session_log = []
        self.user_entry.delete('1.0','end')
        self.show_area.configure(state='normal'); self.show_area.delete('1.0','end'); self.show_area.configure(state='disabled')
        self.log_area.configure(state='normal'); self.log_area.delete('1.0','end'); self.log_area.configure(state='disabled')
        messagebox.showinfo("Session started", f"Session started. You play side {self.user_side}. Use Next to proceed.")
        self.update_display_for_current()

    def get_current_pair(self):
        if 0 <= self.index < len(self.script):
            return self.script[self.index]
        return None

    def update_display_for_current(self):
        pair = self.get_current_pair()
        if pair is None:
            self.turn_label.config(text="Finished")
            self.show_area.configure(state='normal'); self.show_area.insert('end', "End of script.\n"); self.show_area.configure(state='disabled')
            return
        speaker, expected = pair
        if speaker == self.user_side:
            # it's user's turn
            self.turn_label.config(text=f"Your turn ({self.user_side}) — type your reply and press Next")
            # clear user entry (but don't overwrite if user already typed)
            # optionally auto-reveal expected
            if self.reveal_var.get():
                self.user_entry.delete('1.0','end'); self.user_entry.insert('1.0', expected)
            # show expected optionally hidden
            self.show_area.configure(state='normal'); self.show_area.delete('1.0','end')
            self.show_area.insert('end', "(Your turn — expected line hidden. Use 'Show expected' to reveal.)\n")
            self.show_area.configure(state='disabled')
            self.user_entry.focus_set()
        else:
            # other party's turn -> show expected line and log that it was shown
            self.turn_label.config(text=f"Other party ({speaker}) says:")
            self.show_area.configure(state='normal'); self.show_area.delete('1.0','end')
            self.show_area.insert('end', expected + "\n")
            self.show_area.configure(state='disabled')
            # log that this line was shown
            self.append_to_log({
                "time": datetime.now().isoformat(),
                "speaker": speaker,
                "expected": expected,
                "shown": True,
                "user_response": None
            })

    def append_to_log(self, entry):
        self.session_log.append(entry)
        # update log area
        self.log_area.configure(state='normal')
        t = f"[{entry.get('time','')}] {entry.get('speaker','')} — {entry.get('expected','')}"
        if entry.get('user_response') is not None:
            t += f"  | user: {entry.get('user_response')}"
        self.log_area.insert('end', t + "\n")
        self.log_area.see('end')
        self.log_area.configure(state='disabled')

    def next_turn(self):
        if not self.script:
            messagebox.showwarning("No script", "No script loaded. Paste script into editor and click Parse Script.")
            return
        if self.index >= len(self.script):
            messagebox.showinfo("End", "End of script reached.")
            return
        pair = self.script[self.index]
        speaker, expected = pair
        if speaker == self.user_side:
            # capture user's reply from entry
            user_text = self.user_entry.get('1.0','end').strip()
            self.append_to_log({
                "time": datetime.now().isoformat(),
                "speaker": self.user_side,
                "expected": expected,
                "shown": False,
                "user_response": user_text
            })
            # after user's reply, advance index to next and update display
            self.index += 1
            self.user_entry.delete('1.0','end')
            self.update_display_for_current()
        else:
            # it was other party's line (we already showed it in update_display). Move to next.
            self.index += 1
            self.update_display_for_current()

    def toggle_reveal(self):
        # toggle reveal_var
        self.reveal_var.set(not self.reveal_var.get())
        messagebox.showinfo("Toggled", f"Auto reveal expected lines set to {self.reveal_var.get()}")

    def show_expected_dialog(self):
        pair = self.get_current_pair()
        if pair is None:
            messagebox.showinfo("No line", "No current line.")
            return
        speaker, expected = pair
        if speaker == self.user_side:
            # reveal expected to user
            messagebox.showinfo("Expected line", f"Expected ({speaker}):\n\n{expected}")
        else:
            messagebox.showinfo("Other party line", f"{speaker}: {expected}")

    def save_session_log(self):
        if not self.session_log:
            messagebox.showwarning("No log", "Session log is empty.")
            return
        path = filedialog.asksaveasfilename(title="Save session log (JSON)", defaultextension=".json", filetypes=[("JSON files","*.json")])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.session_log, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Saved", f"Session log saved ({len(self.session_log)} entries).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session log: {e}")

    def export_session_text(self):
        if not self.session_log:
            messagebox.showwarning("No log", "Session log is empty.")
            return
        path = filedialog.asksaveasfilename(title="Export session as text", defaultextension=".txt", filetypes=[("Text files","*.txt")])
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for entry in self.session_log:
                    ts = entry.get('time','')
                    sp = entry.get('speaker','')
                    ex = entry.get('expected','')
                    ur = entry.get('user_response')
                    line = f"[{ts}] {sp}: {ex}"
                    if ur is not None:
                        line += f"  || user reply: {ur}"
                    f.write(line + "\n")
            messagebox.showinfo("Exported", "Session exported as text.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

def main():
    root = tk.Tk()
    app = ChatPlayerApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
