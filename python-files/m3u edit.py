import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

# ==================== פונקציות עיבוד ====================
def parse_m3u(file_path):
    channels = []
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF'):
            info = lines[i].strip()
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            group = ''
            if 'group-title="' in info:
                start = info.index('group-title="') + 13
                end = info.index('"', start)
                group = info[start:end]
            channels.append({'info': info, 'url': url, 'group': group})
            i += 2
        else:
            i += 1
    return channels

def save_m3u(channels, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('#EXTM3U\n')
        for ch in channels:
            f.write(ch['info'] + '\n')
            f.write(ch['url'] + '\n')

# ==================== GUI ====================
class M3UManager:
    def __init__(self, root):
        self.root = root
        root.title("עורך M3U מאוחד")
        root.geometry("1100x850")
        root.minsize(1100, 850)

        self.channels = []
        self.groups = []
        self.selected_groups = set()
        self.selected_channels = set()
        self.displayed_channels = []

        self.tab_control = ttk.Notebook(root)
        self.tab_edit = ttk.Frame(self.tab_control)
        self.tab_merge = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_edit, text="עריכה")
        self.tab_control.add(self.tab_merge, text="מיזוג")
        self.tab_control.pack(expand=1, fill="both")

        self.build_edit_tab()
        self.build_merge_tab()

    # ==================== טאב עריכה ====================
    def build_edit_tab(self):
        frm = tk.Frame(self.tab_edit)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        top_btn_frame = tk.Frame(frm)
        top_btn_frame.pack(pady=5)

        tk.Button(top_btn_frame, text="📂 טען קובץ M3U", command=self.load_file).pack(side="left", padx=5)
        tk.Button(top_btn_frame, text="💾 שמור קובץ חדש", command=self.save_file).pack(side="left", padx=5)
        tk.Button(top_btn_frame, text="✏️ שנה שם קבוצה", command=self.rename_selected_group).pack(side="left", padx=5)
        tk.Button(top_btn_frame, text="✏️ שנה שם ערוץ", command=self.rename_selected_channel).pack(side="left", padx=5)
        tk.Button(top_btn_frame, text="🔍 חפש קבוצה", command=self.search_group).pack(side="left", padx=5)
        tk.Button(top_btn_frame, text="🔍 חפש ערוץ", command=self.search_channel).pack(side="left", padx=5)

        content = tk.Frame(frm)
        content.pack(fill="both", expand=True)

        # --- קבוצות ---
        group_frame = tk.Frame(content)
        group_frame.pack(side="left", fill="y", padx=5)
        tk.Label(group_frame, text="קבוצות:").pack()
        group_scroll = tk.Scrollbar(group_frame)
        group_scroll.pack(side="right", fill="y")
        self.group_listbox = tk.Listbox(group_frame, selectmode=tk.MULTIPLE, yscrollcommand=group_scroll.set, width=50, height=30)
        self.group_listbox.pack(fill="y", expand=True)
        group_scroll.config(command=self.group_listbox.yview)
        self.group_listbox.bind("<Button-1>", self.on_group_click)

        btn_frame_g = tk.Frame(group_frame)
        btn_frame_g.pack(pady=5)
        tk.Button(btn_frame_g, text="▲ למעלה", command=lambda: self.move_group("up")).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame_g, text="▼ למטה", command=lambda: self.move_group("down")).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame_g, text="⏫ להתחלה", command=lambda: self.move_group("top")).grid(row=0, column=2, padx=2, pady=2)
        tk.Button(btn_frame_g, text="⏬ לסוף", command=lambda: self.move_group("bottom")).grid(row=0, column=3, padx=2, pady=2)
        tk.Button(btn_frame_g, text="✅ בחר הכול", command=lambda: self.select_all_groups(True)).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame_g, text="❌ בטל הכול", command=lambda: self.select_all_groups(False)).grid(row=1, column=1, padx=2, pady=2)
        tk.Button(btn_frame_g, text="🗑️ מחק", command=self.delete_selected_groups).grid(row=1, column=2, padx=2, pady=2)
        tk.Button(btn_frame_g, text="📤 יצא נבחרים", command=self.export_selected_groups).grid(row=1, column=3, padx=2, pady=2)

        # --- ערוצים ---
        channel_frame = tk.Frame(content)
        channel_frame.pack(side="right", fill="both", expand=True)
        tk.Label(channel_frame, text="ערוצים:").pack()
        channel_scroll = tk.Scrollbar(channel_frame)
        channel_scroll.pack(side="right", fill="y")
        self.channel_listbox = tk.Listbox(channel_frame, selectmode=tk.MULTIPLE, yscrollcommand=channel_scroll.set, width=65, height=30)
        self.channel_listbox.pack(fill="both", expand=True)
        channel_scroll.config(command=self.channel_listbox.yview)
        self.channel_listbox.bind("<Button-1>", self.on_channel_click)

        btn_frame_c = tk.Frame(channel_frame)
        btn_frame_c.pack(pady=5)
        tk.Button(btn_frame_c, text="▲ למעלה", command=lambda: self.move_channel("up")).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(btn_frame_c, text="▼ למטה", command=lambda: self.move_channel("down")).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(btn_frame_c, text="⏫ להתחלה", command=lambda: self.move_channel("top")).grid(row=0, column=2, padx=2, pady=2)
        tk.Button(btn_frame_c, text="⏬ לסוף", command=lambda: self.move_channel("bottom")).grid(row=0, column=3, padx=2, pady=2)
        tk.Button(btn_frame_c, text="✅ בחר הכול", command=lambda: self.select_all_channels(True)).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(btn_frame_c, text="❌ בטל הכול", command=lambda: self.select_all_channels(False)).grid(row=1, column=1, padx=2, pady=2)
        tk.Button(btn_frame_c, text="🗑️ מחק", command=self.delete_selected_channels).grid(row=1, column=2, padx=2, pady=2)
        tk.Button(btn_frame_c, text="📤 יצא נבחרים", command=self.export_selected_channels).grid(row=1, column=3, padx=2, pady=2)

    # ==================== טאב מיזוג ====================
    def build_merge_tab(self):
        frame = tk.Frame(self.tab_merge)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(frame, text="קובץ מקור:").grid(row=0, column=0, sticky="w")
        self.source_path_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.source_path_var, width=80).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="📂 טען מקור", command=self.load_source).grid(row=0, column=2, padx=5)
        tk.Label(frame, text="קובץ יעד:").grid(row=1, column=0, sticky="w")
        self.target_path_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.target_path_var, width=80).grid(row=1, column=1, padx=5)
        tk.Button(frame, text="📂 טען יעד", command=self.load_target).grid(row=1, column=2, padx=5)
        tk.Label(frame, text="קבוצות מקור:").grid(row=2, column=0, sticky="w", pady=5)
        self.source_group_listbox = tk.Listbox(frame, width=50, height=20)
        self.source_group_listbox.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=5)
        tk.Button(frame, text="➕ הוסף לקובץ יעד", command=self.merge_selected_group).grid(row=3, column=2, padx=5)

    # ==================== פונקציות חיפוש ====================
    def search_group(self):
        term = simpledialog.askstring("חיפוש קבוצה", "הכנס חלק מהשם לחיפוש:")
        if term is None: return
        for i, g in enumerate(self.groups):
            if term.lower() in g.lower():
                self.group_listbox.selection_clear(0, tk.END)
                self.group_listbox.selection_set(i)
                self.group_listbox.see(i)
                self.selected_groups = {g}
                self.update_displayed_channels()
                return
        messagebox.showinfo("חיפוש קבוצה", "לא נמצאה קבוצה מתאימה")

    def search_channel(self):
        term = simpledialog.askstring("חיפוש ערוץ", "הכנס חלק מהשם לחיפוש:")
        if term is None: return
        for i, ch in enumerate(self.channels):
            name = ch['info'].split(',')[-1]
            if term.lower() in name.lower():
                self.selected_groups = {ch['group']}
                self.update_displayed_channels()
                idx_in_display = self.displayed_channels.index(ch)
                self.channel_listbox.selection_clear(0, tk.END)
                self.channel_listbox.selection_set(idx_in_display)
                self.channel_listbox.see(idx_in_display)
                self.selected_channels = {name}
                return
        messagebox.showinfo("חיפוש ערוץ", "לא נמצא ערוץ מתאים")

    # ==================== מיזוג ====================
    def load_source(self):
        path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u")])
        if not path: return
        self.source_path_var.set(path)
        self.source_channels = parse_m3u(path)
        self.source_groups = sorted(set(ch['group'] for ch in self.source_channels))
        self.source_group_listbox.delete(0, tk.END)
        for idx, g in enumerate(self.source_groups, start=1):
            display = f"{idx}. {g}" if g else f"{idx}. (ללא קבוצה)"
            self.source_group_listbox.insert(tk.END, display)

    def load_target(self):
        path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u")])
        if not path: return
        self.target_path_var.set(path)
        self.target_channels = parse_m3u(path)

    def merge_selected_group(self):
        sel_idx = self.source_group_listbox.curselection()
        if not sel_idx:
            messagebox.showinfo("שים לב", "לא נבחרה קבוצה")
            return
        g = self.source_groups[sel_idx[0]]
        to_merge = [ch for ch in self.source_channels if ch['group'] == g]
        if not hasattr(self, 'target_channels'):
            messagebox.showinfo("שגיאה", "יש לטעון קובץ יעד")
            return
        self.target_channels.extend(to_merge)
        save_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U files", "*.m3u")])
        if save_path:
            save_m3u(self.target_channels, save_path)
            messagebox.showinfo("בוצע", f"הקבוצה '{g}' נוספה לקובץ יעד\nוהקובץ נשמר:\n{save_path}")

    # ==================== עריכה ====================
    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("M3U Files", "*.m3u")])
        if not path: return
        self.channels = parse_m3u(path)
        self.groups = []
        seen_groups = set()
        for ch in self.channels:
            if ch['group'] not in seen_groups:
                seen_groups.add(ch['group'])
                self.groups.append(ch['group'])
        self.selected_groups.clear()
        self.selected_channels.clear()
        self.displayed_channels.clear()
        self.update_group_list()
        self.update_displayed_channels()

    def update_group_list(self):
        self.group_listbox.delete(0, tk.END)
        for idx, g in enumerate(self.groups, start=1):
            count = sum(1 for ch in self.channels if ch['group'] == g)
            display = f"{idx}. [{count}] {g}" if g else f"{idx}. [{count}] (ללא קבוצה)"
            self.group_listbox.insert(tk.END, display)
        for i, g in enumerate(self.groups):
            if g in self.selected_groups:
                self.group_listbox.selection_set(i)

    def update_displayed_channels(self):
        self.displayed_channels = [ch for ch in self.channels if ch['group'] in self.selected_groups]
        self.update_channel_list()

    def update_channel_list(self):
        self.channel_listbox.delete(0, tk.END)
        for idx, ch in enumerate(self.displayed_channels, start=1):
            name = ch['info'].split(',')[-1]
            self.channel_listbox.insert(tk.END, f"{idx}. {name}")

    # ==================== אירועים ====================
    def on_group_click(self, event):
        idx = self.group_listbox.nearest(event.y)
        if idx < 0 or idx >= len(self.groups): return
        g = self.groups[idx]
        if g in self.selected_groups:
            self.selected_groups.remove(g)
        else:
            self.selected_groups.add(g)
        self.update_displayed_channels()

    def on_channel_click(self, event):
        idx = self.channel_listbox.nearest(event.y)
        if idx < 0 or idx >= len(self.displayed_channels): return
        ch_name = self.displayed_channels[idx]['info'].split(',')[-1]
        if ch_name in self.selected_channels:
            self.selected_channels.remove(ch_name)
        else:
            self.selected_channels.add(ch_name)

    # ==================== בחירה/תזוזה ====================
    def select_all_groups(self, state=True):
        self.group_listbox.selection_clear(0, tk.END)
        if state:
            self.selected_groups = set(self.groups)
            for i in range(len(self.groups)):
                self.group_listbox.selection_set(i)
        else:
            self.selected_groups.clear()
        self.update_displayed_channels()

    def select_all_channels(self, state=True):
        if state:
            self.selected_channels = set(ch['info'].split(',')[-1] for ch in self.displayed_channels)
        else:
            self.selected_channels.clear()
        self.channel_listbox.selection_clear(0, tk.END)
        for i, ch in enumerate(self.displayed_channels):
            if ch['info'].split(',')[-1] in self.selected_channels:
                self.channel_listbox.selection_set(i)
                self.channel_listbox.see(i)  # <-- תיקון גלילה

    # ==================== תזוזת קבוצות ====================
    def move_group(self, direction):
        sel_idx = list(self.group_listbox.curselection())
        if not sel_idx: return
        sel_groups = [self.groups[i] for i in sel_idx]

        if direction == "up":
            for i in sel_idx:
                if i>0: self.groups[i-1], self.groups[i] = self.groups[i], self.groups[i-1]
        elif direction == "down":
            for i in reversed(sel_idx):
                if i<len(self.groups)-1: self.groups[i+1], self.groups[i] = self.groups[i], self.groups[i+1]
        elif direction == "top":
            for i in sorted(sel_idx): self.groups.insert(0, self.groups.pop(i))
        elif direction == "bottom":
            for i in sorted(sel_idx, reverse=True): self.groups.append(self.groups.pop(i))

        new_channels = []
        for g in self.groups:
            group_chs = [ch for ch in self.channels if ch['group']==g]
            new_channels.extend(group_chs)
        self.channels = new_channels

        self.update_group_list()
        for g in sel_groups:
            if g in self.groups:
                idx = self.groups.index(g)
                self.group_listbox.selection_set(idx)
                self.group_listbox.see(idx)  # <-- תיקון גלילה
        self.update_displayed_channels()

    # ==================== תזוזת ערוצים (שמירת סמן + גלילה) ====================
    def move_channel(self, direction):
        sel_idx = list(self.channel_listbox.curselection())
        if not sel_idx: return
        sel_channels = [self.displayed_channels[i] for i in sel_idx]

        if direction == "up":
            for i in sel_idx:
                if i>0: self.displayed_channels[i-1], self.displayed_channels[i] = self.displayed_channels[i], self.displayed_channels[i-1]
        elif direction == "down":
            for i in reversed(sel_idx):
                if i<len(self.displayed_channels)-1: self.displayed_channels[i+1], self.displayed_channels[i] = self.displayed_channels[i], self.displayed_channels[i+1]
        elif direction == "top":
            for i in sorted(sel_idx): self.displayed_channels.insert(0, self.displayed_channels.pop(i))
        elif direction == "bottom":
            for i in sorted(sel_idx, reverse=True): self.displayed_channels.append(self.displayed_channels.pop(i))

        # עדכון סדר בקובץ המקורי
        new_channels = []
        for g in self.groups:
            group_chs = [ch for ch in self.displayed_channels if ch['group']==g]
            other_chs = [ch for ch in self.channels if ch['group']==g and ch not in group_chs]
            new_channels.extend(group_chs + other_chs)
        self.channels = new_channels

        # עדכון רשימת הערוצים
        self.update_channel_list()

        # ===== תיקון הסמן + גלילה =====
        self.channel_listbox.selection_clear(0, tk.END)
        for i, ch in enumerate(self.displayed_channels):
            name = ch['info'].split(',')[-1]
            if name in self.selected_channels:
                self.channel_listbox.selection_set(i)
                self.channel_listbox.see(i)  # <-- תיקון גלילה

    # ==================== שינוי שמות ====================
    def rename_selected_group(self):
        sel_idx = self.group_listbox.curselection()
        if not sel_idx: return
        new_name = simpledialog.askstring("שנה שם קבוצה", "הכנס שם חדש:")
        if not new_name: return
        old_name = self.groups[sel_idx[0]]
        self.groups[sel_idx[0]] = new_name
        for ch in self.channels:
            if ch['group']==old_name:
                ch['group'] = new_name
                if 'group-title="' in ch['info']:
                    start = ch['info'].index('group-title="') + 13
                    end = ch['info'].index('"', start)
                    ch['info'] = ch['info'][:start] + new_name + ch['info'][end:]
        self.update_group_list()
        self.update_displayed_channels()

    def rename_selected_channel(self):
        sel_idx = self.channel_listbox.curselection()
        if not sel_idx: return
        new_name = simpledialog.askstring("שנה שם ערוץ", "הכנס שם חדש:")
        if not new_name: return
        for i in sel_idx:
            ch = self.displayed_channels[i]
            parts = ch['info'].split(',',1)
            ch['info'] = f"{parts[0]},{new_name}" if len(parts)>1 else f"{parts[0]},{new_name}"
        self.update_channel_list()

    # ==================== מחיקה / יצוא ====================
    def delete_selected_groups(self):
        sel_idx = list(self.group_listbox.curselection())
        if not sel_idx: return
        for i in reversed(sel_idx):
            g = self.groups.pop(i)
            self.channels = [ch for ch in self.channels if ch['group']!=g]
        self.selected_groups.clear()
        self.update_group_list()
        self.update_displayed_channels()

    def delete_selected_channels(self):
        sel_idx = list(self.channel_listbox.curselection())
        if not sel_idx: return
        for i in reversed(sel_idx):
            ch = self.displayed_channels.pop(i)
            self.channels.remove(ch)
        self.selected_channels.clear()
        self.update_channel_list()

    def export_selected_groups(self):
        sel_idx = list(self.group_listbox.curselection())
        if not sel_idx: return
        sel_groups = [self.groups[i] for i in sel_idx]
        export_chs = [ch for ch in self.channels if ch['group'] in sel_groups]
        save_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U files", "*.m3u")])
        if save_path: save_m3u(export_chs, save_path)

    def export_selected_channels(self):
        sel_idx = list(self.channel_listbox.curselection())
        if not sel_idx: return
        sel_chs = [self.displayed_channels[i] for i in sel_idx]
        save_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U files", "*.m3u")])
        if save_path: save_m3u(sel_chs, save_path)

    # ==================== שמירה ====================
    def save_file(self):
        if not self.channels: return
        save_path = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U files", "*.m3u")])
        if save_path:
            save_m3u(self.channels, save_path)
            messagebox.showinfo("שמירה", f"קובץ נשמר בהצלחה:\n{save_path}")

# ==================== הפעלה ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = M3UManager(root)
    root.mainloop()
