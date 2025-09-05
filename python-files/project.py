import tkinter as tk
from tkinter import ttk, scrolledtext

from itertools import permutations

SWARAS = ['sa', 're', 'ga', 'ma', 'pa', 'dha', 'ni', 'sa']

# ...existing code...

# ...existing code...

class SwaraPermApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Swara Permutations")
        self.selected_swaras = []
        self.buttons = []

        # Main frame with two columns, placed at the center
        main_frame = ttk.Frame(root, padding=20)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')  # Center the main frame

        # Right frame for controls (now only one main frame, no image)
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=0, sticky='n')

        # Title
        title = ttk.Label(right_frame, text="Select Swaras", font=("Arial", 18, "bold"))
        title.pack(pady=(0, 10))

        # Swara buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(pady=10)
        for swara in SWARAS:
            btn = ttk.Button(btn_frame, text=swara.capitalize(), width=8,
                             command=lambda s=swara: self.toggle_swara(s))
            btn.pack(side='left', padx=5, pady=5)
            self.buttons.append((swara, btn))

        # Show permutations button
        show_btn = ttk.Button(right_frame, text="Show Permutations", command=self.show_permutations)
        show_btn.pack(pady=15)

        # Scrollable text area for results
        self.result_box = scrolledtext.ScrolledText(right_frame, width=40, height=15, font=("Consolas", 12))
        self.result_box.pack(pady=10)

        # Blinking developer credit label
        self.credit_label = ttk.Label(
            root,
            text="Developed By Vishnu Raghavendra Badasheshi",
            font=("Arial", 12, "bold"),
            foreground="red"
        )
        self.credit_label.pack(side='bottom', pady=10)
        self.blink_state = True
        self.blink_credit()

    def blink_credit(self):
        if self.blink_state:
            self.credit_label.configure(foreground="red")
        else:
            self.credit_label.configure(foreground="gray")
        self.blink_state = not self.blink_state
        self.root.after(600, self.blink_credit)

# ...existing code...

    def toggle_swara(self, swara):
        if swara in self.selected_swaras:
            self.selected_swaras.remove(swara)
        else:
            self.selected_swaras.append(swara)
        # Update button styles
        for s, btn in self.buttons:
            if s in self.selected_swaras:
                btn.state(['pressed'])
                btn.config(style='Accent.TButton')
            else:
                btn.state(['!pressed'])
                btn.config(style='TButton')

    def show_permutations(self):
        self.result_box.delete('1.0', tk.END)
        n = len(self.selected_swaras)
        if n == 0:
            self.result_box.insert(tk.END, "Please select at least one swara.\n")
            return
        perms = list(permutations(self.selected_swaras, n))
        for i, combi in enumerate(perms, 1):
            line = f"{i}) " + ' '.join(combi) + '\n'
            self.result_box.insert(tk.END, line)

# ...existing code...
if __name__ == "__main__":
    root = tk.Tk()
    root.state('zoomed')  # Maximizes the window on Windows
    style = ttk.Style(root)
    style.theme_use('clam')
    app = SwaraPermApp(root)
    root.mainloop()