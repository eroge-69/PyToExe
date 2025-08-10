import tkinter as tk
from tkinter import messagebox

# ---------- Toggle Switch ----------
class ToggleSwitch(tk.Frame):
    def __init__(self, master=None, on_text="ON", off_text="OFF", command=None):
        super().__init__(master)
        self.command = command
        self.state = False
        self.canvas = tk.Canvas(self, width=60, height=30, bg="#1E1E1E", highlightthickness=0)
        self.canvas.pack()
        self.draw_switch()
        self.canvas.bind("<Button-1>", self.toggle)

    def draw_switch(self):
        self.canvas.delete("all")
        bg_color = "#4CAF50" if self.state else "#555"
        circle_x = 40 if self.state else 20
        self.canvas.create_rounded_rect = self.canvas.create_rectangle(5, 5, 55, 25, outline="", fill=bg_color, width=0)
        self.canvas.create_oval(circle_x-10, 5, circle_x+10, 25, fill="white", outline="")

    def toggle(self, event=None):
        self.state = not self.state
        self.draw_switch()
        if self.command:
            self.command(self.state)

# ---------- Main App ----------
class AimbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Aimbot Control")
        self.root.geometry("400x500")
        self.root.configure(bg="#1E1E1E")

        # Title
        tk.Label(root, text="🎯 Aimbot Control Panel", fg="white", bg="#1E1E1E", font=("Arial", 16, "bold")).pack(pady=10)

        # Login Frame
        login_frame = tk.LabelFrame(root, text="Login", fg="white", bg="#2C2C2C", padx=10, pady=10)
        login_frame.pack(pady=10)

        tk.Label(login_frame, text="Username:", fg="white", bg="#2C2C2C").grid(row=0, column=0, sticky="w")
        self.username_entry = tk.Entry(login_frame)
        self.username_entry.insert(0, "Num")
        self.username_entry.grid(row=0, column=1)

        tk.Label(login_frame, text="Password:", fg="white", bg="#2C2C2C").grid(row=1, column=0, sticky="w")
        self.password_entry = tk.Entry(login_frame, show="*")
        self.password_entry.insert(0, "Pass 1")
        self.password_entry.grid(row=1, column=1)

        tk.Button(login_frame, text="Login", bg="#4CAF50", fg="white", command=self.check_login).grid(row=2, column=0, columnspan=2, pady=5)

        # Connection Status
        self.status_label = tk.Label(root, text="🔴 Disconnected", fg="red", bg="#1E1E1E", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Aimbot Options
        aim_frame = tk.LabelFrame(root, text="Aimbot Settings", fg="white", bg="#2C2C2C", padx=10, pady=10)
        aim_frame.pack(pady=10, fill="x")

        tk.Label(aim_frame, text="Aim Location:", fg="white", bg="#2C2C2C").pack(anchor="w")
        self.location_var = tk.StringVar(value="Head")
        tk.OptionMenu(aim_frame, self.location_var, "Head", "Chest", "Legs").pack(anchor="w")

        self.drag_headshot_var = tk.BooleanVar()
        tk.Checkbutton(aim_frame, text="Drag Headshot", variable=self.drag_headshot_var, bg="#2C2C2C", fg="white", selectcolor="#333").pack(anchor="w")

        self.extra_feature = tk.BooleanVar()
        tk.Checkbutton(aim_frame, text="Extra Check Feature", variable=self.extra_feature, bg="#2C2C2C", fg="white", selectcolor="#333").pack(anchor="w")

        # On/Off Switch
        tk.Label(root, text="Aimbot Power:", fg="white", bg="#1E1E1E").pack(pady=5)
        self.toggle = ToggleSwitch(root, command=self.switch_changed)
        self.toggle.pack()

    def check_login(self):
        user = self.username_entry.get()
        pwd = self.password_entry.get()
        if user == "Num" and pwd == "Pass 1":
            self.status_label.config(text="🟢 Connected", fg="lime")
            messagebox.showinfo("Login", "Connected Successfully!")
        else:
            messagebox.showerror("Login Failed", "Invalid Username or Password")

    def switch_changed(self, state):
        if state:
            messagebox.showinfo("Aimbot", "Aimbot Enabled")
        else:
            messagebox.showinfo("Aimbot", "Aimbot Disabled")

# ---------- Run ----------
root = tk.Tk()
app = AimbotUI(root)
root.mainloop()

