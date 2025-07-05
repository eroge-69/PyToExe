import tkinter as tk
from tkinter import simpledialog
import threading
import keyboard

class CounterOverlay:
    def __init__(self, root, num_counters=5):
        self.root = root
        self.root.title("Overlay")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.7)
        self.root.overrideredirect(True)
        self.root.config(bg="#222222")

        self.container = tk.Frame(self.root, bg="#222222")
        self.container.pack(padx=10, pady=10)

        # Close button with no red background
        self.close_btn = tk.Button(
            self.container, text="X", command=self.root.destroy,
            fg="white", bg="#222222", bd=0, padx=5, pady=2,
            font=("Arial", 10, "bold"), highlightthickness=0, relief="flat", activebackground="#333333"
        )
        self.close_btn.pack(anchor="ne")

        self.frame = tk.Frame(self.container, bg="#222222")
        self.frame.pack()

        self.active_index = 0
        self.counters = []

        for i in range(num_counters):
            counter = self.create_counter(f"Item {i+1}")
            self.counters.append(counter)

        self.listen_keys()

        # Allow drag
        self.container.bind("<Button-1>", self.start_move)
        self.container.bind("<B1-Motion>", self.do_move)
        self.offset_x = 0
        self.offset_y = 0

    def create_counter(self, name):
        frame = tk.Frame(self.frame, bg="#222222", padx=5)
        tk.Label(frame, text=name, fg="white", bg="#222222").pack()

        val = tk.IntVar(value=0)
        label = tk.Label(frame, textvariable=val, width=6, fg="white", bg="#444444", cursor="hand2")
        label.pack(pady=3)
        label.bind("<Button-1>", lambda e, v=val: self.manual_edit(v))

        frame.pack(side="left", padx=10)
        return {"var": val, "label": label}

    def manual_edit(self, val_var):
        new_val = simpledialog.askinteger("Set Value", "Enter new value:", initialvalue=val_var.get())
        if new_val is not None:
            val_var.set(new_val)

    def increment(self):
        self.counters[self.active_index]["var"].set(self.counters[self.active_index]["var"].get() + 1)

    def decrement(self):
        val = self.counters[self.active_index]["var"].get()
        self.counters[self.active_index]["var"].set(max(0, val - 1))

    def set_active(self, index):
        self.active_index = index
        print(f"Active counter: Item {index+1}")

    def listen_keys(self):
        def key_loop():
            while True:
                for i in range(len(self.counters)):
                    if keyboard.is_pressed(f"num {i+1}"):
                        self.set_active(i)
                        while keyboard.is_pressed(f"num {i+1}"):
                            pass

                if keyboard.is_pressed("add"):
                    self.increment()
                    while keyboard.is_pressed("add"):
                        pass

                if keyboard.is_pressed("subtract"):
                    self.decrement()
                    while keyboard.is_pressed("subtract"):
                        pass

        threading.Thread(target=key_loop, daemon=True).start()

    def start_move(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_pointerx() - self.offset_x
        y = self.root.winfo_pointery() - self.offset_y
        self.root.geometry(f"+{x}+{y}")

# Launch it
root = tk.Tk()
app = CounterOverlay(root, num_counters=5)
root.mainloop()
