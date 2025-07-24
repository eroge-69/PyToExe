import tkinter as tk
from tkinter import messagebox

class BaccaratPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Baccarat Analyzer Pro 🂡")
        self.root.geometry("600x600")
        self.root.resizable(False, False)

        self.dark_theme = True
        self.font_name = "Segoe UI"
        self.results = []
        self.win = 0
        self.loss = 0
        self.tie = 0
        self.player_pair = 0
        self.banker_pair = 0

        self.setup_ui()
        self.set_theme(self.dark_theme)

    def setup_ui(self):
        # Top Frame for logo & theme switch
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill='x')

        self.logo_label = tk.Label(top_frame, text="🂡 BACCARAT PRO", font=(self.font_name, 24, "bold"))
        self.logo_label.pack(side="left", padx=20)

        self.theme_btn = tk.Button(top_frame, text="Switch Theme", command=self.toggle_theme, width=12)
        self.theme_btn.pack(side="right", padx=20)

        # Result Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        btn_params = {"font": (self.font_name, 14), "width": 10, "padx": 5, "pady": 5}

        self.btn_player = tk.Button(btn_frame, text="Player (P)", bg="#3399FF", fg="white",
                                    command=lambda: self.add_result("P"), **btn_params)
        self.btn_player.grid(row=0, column=0)

        self.btn_banker = tk.Button(btn_frame, text="Banker (B)", bg="#FF5555", fg="white",
                                    command=lambda: self.add_result("B"), **btn_params)
        self.btn_banker.grid(row=0, column=1)

        self.btn_tie = tk.Button(btn_frame, text="Tie (T)", bg="#66CC66", fg="white",
                                 command=lambda: self.add_result("T"), **btn_params)
        self.btn_tie.grid(row=0, column=2)

        self.btn_player_pair = tk.Button(btn_frame, text="Player Pair (PP)", bg="#1E90FF", fg="white",
                                         command=lambda: self.add_result("PP"), **btn_params)
        self.btn_player_pair.grid(row=1, column=0)

        self.btn_banker_pair = tk.Button(btn_frame, text="Banker Pair (BP)", bg="#FF3333", fg="white",
                                         command=lambda: self.add_result("BP"), **btn_params)
        self.btn_banker_pair.grid(row=1, column=1)

        # Control Buttons
        ctrl_frame = tk.Frame(self.root)
        ctrl_frame.pack(pady=10)

        self.btn_undo = tk.Button(ctrl_frame, text="Undo Last", command=self.undo_last, width=12)
        self.btn_undo.grid(row=0, column=0, padx=10)

        self.btn_reset = tk.Button(ctrl_frame, text="Reset", command=self.reset_all, width=12)
        self.btn_reset.grid(row=0, column=1, padx=10)

        # Canvas for showing history cards
        self.canvas = tk.Canvas(self.root, width=560, height=220, bg="#222222")
        self.canvas.pack(pady=15)

        # Analysis & Stats Labels
        self.analysis_label = tk.Label(self.root, text="", font=(self.font_name, 14), fg="white")
        self.analysis_label.pack(pady=5)

        self.stats_label = tk.Label(self.root, text="", font=(self.font_name, 12), fg="white")
        self.stats_label.pack(pady=5)

    def set_theme(self, dark):
        bg_color = "#121212" if dark else "#F0F0F0"
        fg_color = "white" if dark else "black"
        btn_fg = "white" if dark else "black"

        self.root.config(bg=bg_color)
        self.logo_label.config(bg=bg_color, fg=fg_color)
        self.analysis_label.config(bg=bg_color, fg=fg_color)
        self.stats_label.config(bg=bg_color, fg=fg_color)

        # Buttons background adjustment
        btn_bg_map = {
            "P": "#3399FF" if dark else "#ADD8E6",
            "B": "#FF5555" if dark else "#FF9999",
            "T": "#66CC66" if dark else "#99CC99",
            "PP": "#1E90FF" if dark else "#4AA3FF",
            "BP": "#FF3333" if dark else "#FF6666"
        }

        for btn, key in [(self.btn_player, "P"), (self.btn_banker, "B"), (self.btn_tie, "T"),
                         (self.btn_player_pair, "PP"), (self.btn_banker_pair, "BP")]:
            btn.config(bg=btn_bg_map[key], fg=btn_fg)

        for btn in [self.btn_undo, self.btn_reset, self.theme_btn]:
            btn.config(bg=bg_color, fg=fg_color, relief="flat")

        self.canvas.config(bg="#222222" if dark else "#DDDDDD")

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.set_theme(self.dark_theme)

    def add_result(self, res):
        self.results.append(res)
        # Update pairs count
        if res == "PP":
            self.player_pair += 1
        elif res == "BP":
            self.banker_pair += 1
        elif res == "T":
            self.tie += 1
        elif res == "P":
            self.win += 1
        elif res == "B":
            self.loss += 1
        self.update_canvas()
        self.analyze()

    def undo_last(self):
        if not self.results:
            messagebox.showinfo("Info", "ไม่มีข้อมูลให้ลบ")
            return
        last = self.results.pop()
        if last == "PP":
            self.player_pair = max(0, self.player_pair - 1)
        elif last == "BP":
            self.banker_pair = max(0, self.banker_pair - 1)
        elif last == "T":
            self.tie = max(0, self.tie - 1)
        elif last == "P":
            self.win = max(0, self.win - 1)
        elif last == "B":
            self.loss = max(0, self.loss - 1)
        self.update_canvas()
        self.analyze()

    def reset_all(self):
        self.results.clear()
        self.win = self.loss = self.tie = self.player_pair = self.banker_pair = 0
        self.update_canvas()
        self.analysis_label.config(text="")
        self.stats_label.config(text="")

    def update_canvas(self):
        self.canvas.delete("all")
        box_size = 40
        for i, res in enumerate(self.results[-30:]):  # แสดงแค่ 30 ล่าสุด
            col = i // 5
            row = i % 5
            x = col * (box_size + 5) + 10
            y = row * (box_size + 5) + 10
            color_map = {
                "P": "#3399FF",
                "B": "#FF5555",
                "T": "#66CC66",
                "PP": "#1E90FF",
                "BP": "#FF3333"
            }
            color = color_map.get(res, "gray")
            self.canvas.create_oval(x, y, x + box_size, y + box_size, fill=color)
            self.canvas.create_text(x + box_size / 2, y + box_size / 2, text=res, fill="white", font=(self.font_name, 14, "bold"))

    def analyze(self):
        if len(self.results) < 2:
            self.analysis_label.config(text="กรุณาเพิ่มข้อมูลเพื่อวิเคราะห์")
            self.stats_label.config(text=self.get_stats_text())
            return

        pattern = self.detect_pattern()
        next_bet = self.recommend_bet(pattern)
        prob_text = self.get_probability_text()

        analysis_text = f"เค้าไพ่: {pattern}\nแนะนำแทง: {next_bet}\n{prob_text}"
        self.analysis_label.config(text=analysis_text)
        self.stats_label.config(text=self.get_stats_text())

    def detect_pattern(self):
        r = [x for x in self.results if x in ("P", "B")]
        if len(r) < 4:
            return "ไม่พอข้อมูล"

        # เช็ค มังกร
        if all(x == r[0] for x in r[-4:]):
            return "มังกร"

        # เช็ค ปิงปอง
        last4 = r[-4:]
        if last4 == [last4[0], last4[1], last4[0], last4[1]]:
            return "ปิงปอง"

        # เช็ค 2-2
        last4 = r[-4:]
        if last4[0] == last4[1] and last4[2] == last4[3] and last4[0] != last4[2]:
            return "2-2"

        # เช็ค 3-1
        last4 = r[-4:]
        counts = {k: last4.count(k) for k in set(last4)}
        if sorted(counts.values()) == [1,3]:
            return "3-1"

        # เช็ค 3-2-1 (เช็คจาก 6 ไม้ล่าสุด)
        if len(r) >= 6:
            last6 = r[-6:]
            count_map = {k: last6.count(k) for k in set(last6)}
            if sorted(count_map.values()) == [1,2,3]:
                return "3-2-1"

        return "ไม่ทราบเค้าไพ่"

    def recommend_bet(self, pattern):
        r = [x for x in self.results if x in ("P", "B")]
        if not r:
            return "-"

        last = r[-1]

        if pattern == "มังกร":
            return "แทง " + ("Player" if last == "P" else "Banker")
        elif pattern == "ปิงปอง":
            return "แทง " + ("Banker" if last == "P" else "Player")
        elif pattern == "2-2":
            return "แทง " + ("Banker" if last == "P" else "Player")
        elif pattern == "3-1":
            # แทงฝั่งที่ออก 3 ครั้ง
            counts = {k: r[-4:].count(k) for k in set(r[-4:])}
            max_side = max(counts, key=counts.get)
            return "แทง " + ("Player" if max_side == "P" else "Banker")
        elif pattern == "3-2-1":
            # แทงฝั่งที่ออก 3 ครั้งใน 6 ไม้ล่าสุด
            if len(r) < 6:
                return "-"
            last6 = r[-6:]
            counts = {k: last6.count(k) for k in set(last6)}
            max_side = max(counts, key=counts.get)
            return "แทง " + ("Player" if max_side == "P" else "Banker")
        else:
            return "-"

    def get_probability_text(self):
        total = max(1, len([x for x in self.results if x in ("P","B","T")]))
        p_count = self.results.count("P")
        b_count = self.results.count("B")
        t_count = self.results.count("T")
        pp_count = self.results.count("PP")
        bp_count = self.results.count("BP")

        prob_text = f"Player: {p_count} ({p_count/total*100:.1f}%)  |  Banker: {b_count} ({b_count/total*100:.1f}%)  |  Tie: {t_count} ({t_count/total*100:.1f}%)"
        pair_text = f"Player Pair: {pp_count} ({pp_count/total*100:.1f}%)  |  Banker Pair: {bp_count} ({bp_count/total*100:.1f}%)"
        return prob_text + "\n" + pair_text

    def get_stats_text(self):
        total = max(1, len(self.results))
        win_perc = self.win / total * 100 if total else 0
        loss_perc = self.loss / total * 100 if total else 0
        tie_perc = self.tie / total * 100 if total else 0

        return (f"Win: {self.win} ({win_perc:.1f}%)  |  "
                f"Loss: {self.loss} ({loss_perc:.1f}%)  |  "
                f"Tie: {self.tie} ({tie_perc:.1f}%)  |  "
                f"Player Pair: {self.player_pair}  |  Banker Pair: {self.banker_pair}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BaccaratPro(root)
    root.mainloop()
