import tkinter as tk
from tkinter import messagebox
import asyncio
import threading


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tooltip or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self.tooltip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Arial", 10),
        )
        label.pack(ipadx=5, ipady=2)

    def hide(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class LagProxy:
    def __init__(self):
        self.delay = 0.3
        self.is_on = False
        self.loop = None
        self.server = None

    async def handle_client(self, reader, writer):
        try:
            peer = writer.get_extra_info("peername")
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                if self.is_on:
                    await asyncio.sleep(self.delay)
                writer.write(data)
                await writer.drain()
        except Exception as e:
            print("Error:", e)
        finally:
            writer.close()
            await writer.wait_closed()

    async def start_proxy(self):
        self.server = await asyncio.start_server(self.handle_client, "127.0.0.1", 8888)
        async with self.server:
            await self.server.serve_forever()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start_proxy())


class LagSimulatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Lag Simulator")
        root.geometry("350x400")
        root.resizable(False, False)

        self.proxy = LagProxy()

        threading.Thread(target=self.proxy.run, daemon=True).start()

        self.label = tk.Label(root, text="Delay (ms):")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.delay_var = tk.StringVar(value="300")
        vcmd = (root.register(self.validate_input), "%P")
        self.entry = tk.Entry(
            root,
            textvariable=self.delay_var,
            width=12,
            validate="key",
            validatecommand=vcmd,
        )
        self.entry.grid(row=0, column=1, padx=10, pady=10)
        Tooltip(self.entry, "Enter delay in milliseconds")

        presets_frame = tk.Frame(root)
        presets_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.presets = {"Wi-Fi": 500, "3G": 300, "Edge": 800}
        for i, (name, val) in enumerate(self.presets.items()):
            btn = tk.Button(
                presets_frame,
                text=name,
                width=8,
                command=lambda v=val: self.set_preset(v),
            )
            btn.grid(row=0, column=i, padx=5)

        self.turn_on_btn = tk.Button(
            root, text="Turn on", width=15, command=self.turn_on
        )
        self.turn_on_btn.grid(row=2, column=0, padx=10, pady=10)

        self.turn_off_btn = tk.Button(
            root, text="Turn off", width=15, command=self.turn_off, state=tk.DISABLED
        )
        self.turn_off_btn.grid(row=2, column=1, padx=10, pady=10)

        self.reset_btn = tk.Button(root, text="Reset", width=34, command=self.reset_all)
        self.reset_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.status_label = tk.Label(root, text="Status: OFF", fg="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)

        log_label = tk.Label(root, text="Log:")
        log_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10)

        self.log_text = tk.Text(
            root, height=8, width=40, state=tk.DISABLED, bg="#f0f0f0"
        )
        self.log_text.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    def validate_input(self, value_if_allowed):
        if value_if_allowed == "":
            return True
        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False

    def set_preset(self, val):
        self.delay_var.set(str(val))
        self.log(f"Preset selected: {val} ms delay")

    def turn_on(self):
        try:
            delay = int(self.delay_var.get())
            if delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Please enter a valid non-negative integer for delay"
            )
            return

        self.proxy.delay = delay / 1000
        self.proxy.is_on = True
        self.status_label.config(text=f"Status: ON (Delay {delay} ms)", fg="green")
        self.turn_on_btn.config(state=tk.DISABLED)
        self.turn_off_btn.config(state=tk.NORMAL)
        self.log(f"Lags turned ON with delay: {delay} ms")

    def turn_off(self):
        self.proxy.is_on = False
        self.status_label.config(text="Status: OFF", fg="red")
        self.turn_on_btn.config(state=tk.NORMAL)
        self.turn_off_btn.config(state=tk.DISABLED)
        self.log("Lags turned OFF")

    def reset_all(self):
        self.delay_var.set("300")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.status_label.config(text="Status: OFF", fg="red")
        self.turn_on_btn.config(state=tk.NORMAL)
        self.turn_off_btn.config(state=tk.DISABLED)
        self.proxy.is_on = False
        self.log("Settings and log reset")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = LagSimulatorApp(root)
    root.mainloop()
