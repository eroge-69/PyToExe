import tkinter as tk
import threading
import time

class OneBitComputer:
    def __init__(self, root):
        self.root = root
        self.root.title("1-BIT COMPUTER")
        self.root.configure(bg="#2b2b2b")
        self.running = False
        self.power_on = False
        self.memory = [0]*8
        self.create_widgets()
        self.reset()

    def create_widgets(self):
        font = ("Courier", 12, "bold")
        label_fg = "#f4f4c4"
        bg = "#2b2b2b"

        # Power Button
        self.power_button = tk.Button(
            self.root, text="POWER OFF", font=font,
            bg="gray", fg="white", command=self.toggle_power
        )
        self.power_button.grid(row=0, column=0, columnspan=4, pady=5)

        # Instruction Input
        tk.Label(
            self.root, text="INSTRUCTIONS",
            font=font, fg=label_fg, bg=bg
        ).grid(row=1, column=0, columnspan=4)
        self.instruction_entry = tk.Entry(
            self.root, font=font, width=30,
            bg="#1a1a1a", fg="#aaffaa"
        )
        self.instruction_entry.insert(0, "01 01 00 10")
        self.instruction_entry.grid(row=2, column=0, columnspan=4, pady=5)

        # Logic Indicator
        self.logic_indicator = tk.Label(
            self.root, text="● LOGIC 1",
            font=font, fg="#444", bg=bg
        )
        self.logic_indicator.grid(row=3, column=0, columnspan=4)

        # Core Registers (PC, IR, ACC, OUT)
        self.pc_value = self.add_display("PROGRAM COUNTER", 4, 0, font, label_fg, bg)
        self.ir_value = self.add_display("INSTRUCTION REGISTER", 4, 1, font, label_fg, bg)
        self.acc_value = self.add_display("ACCUMULATOR", 4, 2, font, label_fg, bg, fg_val="red")
        self.out_value = self.add_display("OUTPUT", 4, 3, font, label_fg, bg)

        # Sequencer LEDs
        self.seq_phase = tk.StringVar(value="FETCH")
        tk.Label(self.root, text="SEQUENCER", font=font, fg=label_fg, bg=bg)\
            .grid(row=5, column=0, columnspan=4)
        self.seq_buttons = []
        for i, phase in enumerate(["FETCH", "DECODE", "EXECUTE", "HLT"]):
            btn = tk.Radiobutton(
                self.root, text=phase, variable=self.seq_phase, value=phase,
                font=font, fg=label_fg, bg=bg, selectcolor="red", state="disabled"
            )
            btn.grid(row=6, column=i)
            self.seq_buttons.append(btn)

        # STEP Button
        self.step_button = tk.Button(
            self.root, text="STEP", font=font,
            command=self.step, state="disabled"
        )
        self.step_button.grid(row=7, column=3, pady=10)

        # Speed Slider
        tk.Label(
            self.root, text="SPEED (Hz)",
            font=font, fg=label_fg, bg=bg
        ).grid(row=8, column=0)
        self.speed = tk.Scale(
            self.root, from_=0.5, to=10, resolution=0.5,
            orient="horizontal", bg=bg, fg=label_fg
        )
        self.speed.set(1)
        self.speed.grid(row=9, column=0)

        # AUTO Toggle
        self.auto_run = tk.BooleanVar()
        self.auto_check = tk.Checkbutton(
            self.root, text="AUTO", variable=self.auto_run,
            font=font, fg=label_fg, bg=bg, selectcolor="#444",
            command=self.toggle_auto, state="disabled"
        )
        self.auto_check.grid(row=9, column=1)

        # RESET Button
        tk.Button(
            self.root, text="RESET", font=font,
            command=self.reset, bg="red", fg="white"
        ).grid(row=9, column=3)

        # Log Window
        tk.Label(
            self.root, text="LOG",
            font=font, fg=label_fg, bg=bg
        ).grid(row=10, column=0, columnspan=4)
        self.log = tk.Text(
            self.root, height=6, width=50,
            bg="#1a1a1a", fg=label_fg, font=("Courier", 10)
        )
        self.log.grid(row=11, column=0, columnspan=4)

        # Extras Frame
        extras = tk.LabelFrame(
            self.root, text="EXTRAS", font=font,
            fg=label_fg, bg=bg, bd=2, relief="groove"
        )
        extras.grid(row=12, column=0, columnspan=4, pady=5, sticky="we")

        # Manual Instruction Loader
        tk.Label(
            extras, text="MANUAL INSTRUCTION LOADER",
            font=font, fg=label_fg, bg=bg
        ).grid(row=0, column=0, columnspan=4)
        self.switch_vars = []
        for i in range(8):
            var = tk.IntVar()
            chk = tk.Checkbutton(
                extras, text=str(i), variable=var,
                font=font, fg=label_fg, bg=bg,
                selectcolor="#444", command=self.load_manual
            )
            chk.grid(row=1 + (i//4), column=i%4, padx=2)
            self.switch_vars.append(var)

        # Opcode Decoder
        tk.Label(
            extras, text="OPCODE DECODER",
            font=font, fg=label_fg, bg=bg
        ).grid(row=3, column=0, columnspan=2)
        self.decoder = tk.Label(
            extras,
            text="00 = NOP\n01 = LOAD\n10 = OUT\n11 = HLT",
            font=font, fg=label_fg, bg=bg, justify="left"
        )
        self.decoder.grid(row=4, column=0, columnspan=2)

        # Microcode Viewer
        tk.Label(
            extras, text="MICROCODE VIEWER",
            font=font, fg=label_fg, bg=bg
        ).grid(row=3, column=2, columnspan=2)
        self.microcode = tk.Label(
            extras, text="", font=font,
            fg=label_fg, bg=bg, justify="left"
        )
        self.microcode.grid(row=4, column=2, columnspan=2)

        # Memory Viewer
        tk.Label(
            extras, text="MEMORY VIEWER",
            font=font, fg=label_fg, bg=bg
        ).grid(row=5, column=0, columnspan=4)
        self.memory_vars = []
        for i in range(8):
            var = tk.IntVar()
            chk = tk.Checkbutton(
                extras, text=str(i), variable=var,
                font=font, fg=label_fg, bg=bg,
                selectcolor="#444", command=self.update_memory
            )
            chk.grid(row=6 + (i//4), column=i%4, padx=2)
            self.memory_vars.append(var)

        # Status Panel
        tk.Label(
            extras, text="STATUS PANEL",
            font=font, fg=label_fg, bg=bg
        ).grid(row=8, column=0, columnspan=4)
        self.status_vars = {}
        for idx, flag in enumerate(["ZERO", "CARRY", "HALT", "ERROR"]):
            tk.Label(
                extras, text=flag,
                font=font, fg=label_fg, bg=bg
            ).grid(row=9, column=idx)
            sv = tk.Label(
                extras, text="●",
                font=font, fg="#444", bg=bg
            )
            sv.grid(row=10, column=idx)
            self.status_vars[flag] = sv

        # Easter Egg Terminal
        tk.Label(
            extras, text="EASTER EGG TERMINAL",
            font=font, fg=label_fg, bg=bg
        ).grid(row=11, column=0, columnspan=4)
        self.easter_entry = tk.Entry(
            extras, font=font, bg="#1a1a1a", fg="#aaffaa"
        )
        self.easter_entry.grid(row=12, column=0, columnspan=2, pady=2)
        self.easter_button = tk.Button(
            extras, text="ENTER",
            font=font, command=self.check_easter
        )
        self.easter_button.grid(row=12, column=2, columnspan=2)
        self.easter_log = tk.Text(
            extras, height=3, width=50,
            bg="#1a1a1a", fg=label_fg,
            font=("Courier", 10)
        )
        self.easter_log.grid(row=13, column=0, columnspan=4, pady=2)

        # Center columns on resize
        for col in range(4):
            self.root.grid_columnconfigure(col, weight=1)

    def add_display(self, label, row, col, font, fg, bg, fg_val="#00ff00"):
        tk.Label(
            self.root, text=label, font=font, fg=fg, bg=bg
        ).grid(row=row, column=col)
        val = tk.Label(
            self.root, text="0", font=font, fg=fg_val, bg="#1a1a1a", width=5
        )
        val.grid(row=row+1, column=col)
        return val

    def toggle_power(self):
        self.power_on = not self.power_on
        if self.power_on:
            self.power_button.config(text="POWER ON", bg="green")
            self.enable_controls()
            self.update_display()
        else:
            self.power_button.config(text="POWER OFF", bg="gray")
            self.disable_controls()
            self.clear_display()

    def enable_controls(self):
        self.step_button.config(state="normal")
        self.auto_check.config(state="normal")
        for btn in self.seq_buttons:
            btn.config(state="normal")

    def disable_controls(self):
        self.step_button.config(state="disabled")
        self.auto_check.config(state="disabled")
        for btn in self.seq_buttons:
            btn.config(state="disabled")
        self.running = False

    def clear_display(self):
        blank = " "
        self.pc_value.config(text=blank, fg="#444")
        self.ir_value.config(text=blank, fg="#444")
        self.acc_value.config(text=blank, fg="#444")
        self.out_value.config(text=blank, fg="#444")
        self.logic_indicator.config(fg="#444")
        self.microcode.config(text="")
        for sv in self.status_vars.values():
            sv.config(fg="#444")

    def reset(self):
        self.pc = 0
        self.acc = 0
        self.output = 0
        self.seq_phase.set("FETCH")
        self.running = False
        self.instructions = self.parse_instructions()
        self.log.delete("1.0", tk.END)
        if self.power_on:
            self.update_display()

    def parse_instructions(self):
        raw = self.instruction_entry.get().strip().split()
        valid = {"00", "01", "10", "11"}
        return [instr if instr in valid else "00" for instr in raw]

    def update_display(self):
        self.pc_value.config(text=str(self.pc), fg="#00ff00")
        instr = self.instructions[self.pc] if self.pc < len(self.instructions) else None
        ir_text = instr if instr else "XX"
        self.ir_value.config(text=ir_text, fg="#00ff00")
        self.acc_value.config(text=str(self.acc), fg="red")
        self.out_value.config(text=str(self.output), fg="#00ff00")
        self.logic_indicator.config(fg="red" if self.output == 1 else "#444")
        self.update_microcode(instr)
        self.update_status()

    def update_microcode(self, instr):
        signals = []
        if instr:
            signals.append("IR_LOAD")
            if instr == "01":
                signals.append("ACC_SET")
            if instr == "10":
                signals.append("OUT_ENABLE")
            if instr in ["00", "01", "10"]:
                signals.append("PC_INC")
        self.microcode.config(text="\n".join(signals))

    def update_status(self):
        states = {
            "ZERO": (self.acc == 0),
            "CARRY": False,
            "HALT": (self.seq_phase.get() == "HLT"),
            "ERROR": (self.pc >= len(self.instructions))
        }
        for flag, sv in self.status_vars.items():
            sv.config(fg="red" if states[flag] else "#444")

    def step(self):
        if not self.power_on:
            return
        if self.pc >= len(self.instructions):
            self.seq_phase.set("HLT")
            self.log.insert(tk.END, "[HLT] End of program\n")
            self.update_status()
            return

        instr = self.instructions[self.pc]
        self.ir_value.config(text=instr)
        self.seq_phase.set("FETCH")
        self.log.insert(tk.END, f"[{self.pc:02}] FETCH {instr}\n")

        self.seq_phase.set("DECODE")
        if instr == "00":
            self.log.insert(tk.END, f"[{self.pc:02}] DECODE NOP\n")
        elif instr == "01":
            self.acc = 1
            self.log.insert(tk.END, f"[{self.pc:02}] DECODE LOAD\n")
        elif instr == "10":
            self.output = self.acc
            self.log.insert(tk.END, f"[{self.pc:02}] DECODE OUT\n")
        elif instr == "11":
            self.seq_phase.set("HLT")
            self.log.insert(tk.END, f"[{self.pc:02}] DECODE HLT\n")
            self.update_display()
            return

        self.seq_phase.set("EXECUTE")
        self.log.insert(tk.END, f"[{self.pc:02}] EXECUTE ACC ← {self.acc}, OUT ← {self.output}\n")
        self.pc += 1
        self.update_display()

    def toggle_auto(self):
        if self.auto_run.get() and self.power_on and not self.running:
            self.running = True
            threading.Thread(target=self.auto_loop, daemon=True).start()
        else:
            self.running = False

    def auto_loop(self):
        while self.running and self.pc < len(self.instructions):
            self.step()
            time.sleep(1 / self.speed.get())

    def load_manual(self):
        bits = ''.join(str(var.get()) for var in self.switch_vars)
        instrs = [bits[i:i+2] for i in range(0, 8, 2)]
        self.instruction_entry.delete(0, tk.END)
        self.instruction_entry.insert(0, ' '.join(instrs))
        self.reset()

    def update_memory(self):
        self.memory = [var.get() for var in self.memory_vars]

    def check_easter(self):
        cmd = self.easter_entry.get().strip()
        self.easter_log.delete("1.0", tk.END)
        if cmd == "01101100":
            self.easter_log.insert(tk.END, "The Lab was never abandoned. It was sealed.")
        else:
            self.easter_log.insert(tk.END, "...")

if __name__ == "__main__":
    root = tk.Tk()
    app = OneBitComputer(root)
    root.mainloop()