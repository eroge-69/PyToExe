import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import winsound
import webbrowser

# ----------------------------
# Matrix regen effect
# ----------------------------
class MatrixRain:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.font_size = 15
        self.columns = int(width / self.font_size)
        self.drops = [0 for _ in range(self.columns)]

    def draw(self):
        self.canvas.delete("matrix")
        for i in range(len(self.drops)):
            char = chr(random.randint(33, 126))
            x = i * self.font_size
            y = self.drops[i] * self.font_size
            self.canvas.create_text(x, y, text=char, fill="lime",
                                    font=("Consolas", 14), tags="matrix")
            if y > self.height and random.random() > 0.975:
                self.drops[i] = 0
            self.drops[i] += 1

# ----------------------------
# Fake ransomware scherm
# ----------------------------
def fake_ransomware(name="User"):
    rw = tk.Tk()
    rw.attributes("-fullscreen", True)
    rw.configure(bg="black")

    screen_width = rw.winfo_screenwidth()
    screen_height = rw.winfo_screenheight()
    canvas = tk.Canvas(rw, width=screen_width, height=screen_height, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    matrix = MatrixRain(canvas, screen_width, screen_height)
    btc_address = "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5"
    timer_seconds = 10  # voor test iets korter

    countdown_label = tk.Label(rw, text="", fg="white", bg="black", font=("Consolas", 24))
    countdown_label.place(relx=0.5, rely=0.8, anchor="center")

    info_label = tk.Label(rw, text=f"Hello {name}, your files are LOCKED!\nSend 0.5 BTC to:", fg="lime", bg="black", font=("Consolas", 18))
    info_label.place(relx=0.5, rely=0.25, anchor="center")

    btc_label = tk.Label(rw, text=btc_address, fg="white", bg="black", font=("Consolas", 18))
    btc_label.place(relx=0.5, rely=0.35, anchor="center")

    fake_email = "secure.transfer.alert99@cybermail.com"
    sending_text = f"Sending collected data to {fake_email}..."
    typing_index = 0

    def animate_matrix():
        matrix.draw()
        canvas.after(50, animate_matrix)

    def type_sending_text():
        nonlocal typing_index
        if typing_index <= len(sending_text):
            canvas.delete("typing")
            canvas.create_text(screen_width//2, screen_height - 50, text=sending_text[:typing_index], fill="white", font=("Consolas", 16), tags="typing")
            typing_index += 1
            canvas.after(100, type_sending_text)

    def countdown():
        nonlocal timer_seconds
        if timer_seconds > 0:
            countdown_label.config(text=f"Time left: {timer_seconds} seconds")
            timer_seconds -= 1
            winsound.Beep(1000, 120)
            rw.after(1000, countdown)
        else:
            rw.destroy()
            password_prompt()  # ga naar verplichte wachtwoordprompt

    def pay_now():
        messagebox.showinfo("Payment Failed", "Payment Failed")

    pay_button = tk.Button(rw, text="Pay Now", command=pay_now, font=("Arial", 14), fg="black", bg="red")
    pay_button.place(relx=0.5, rely=0.5, anchor="center")

    animate_matrix()
    type_sending_text()
    countdown()
    rw.mainloop()

# ----------------------------
# Verplichte wachtwoordprompt met link
# ----------------------------
def password_prompt():
    # Open automatisch de website
    webbrowser.open("https://www.tsaamcardijn.be/wie-we-zijn")

    root = tk.Tk()
    root.withdraw()  # verberg hoofdvenster

    wp = tk.Toplevel(root)
    wp.title("Enter Password")
    wp.geometry("400x200")
    wp.configure(bg="black")

    # Verwijder sluit-knop
    wp.protocol("WM_DELETE_WINDOW", lambda: None)

    tk.Label(wp, text="Enter your password to unlock:", fg="white", bg="black", font=("Arial", 14)).pack(pady=20)
    password_entry = tk.Entry(wp, show="*", font=("Arial", 14))
    password_entry.pack(pady=10)

    def submit_password():
        entered = password_entry.get()
        wp.destroy()
        root.destroy()
        print("Nep shutdown uitgevoerd")  # Veilig alternatief

    tk.Button(wp, text="Submit", command=submit_password, font=("Arial", 14), fg="white", bg="red").pack(pady=20)

    wp.grab_set()       # voorkomt interactie met andere vensters
    wp.focus_force()    # zet focus op dit venster
    wp.mainloop()

# ----------------------------
# Loading scherm
# ----------------------------
def loading_screen():
    loading = tk.Tk()
    loading.attributes("-fullscreen", True)
    loading.configure(bg="black")

    tk.Label(loading, text="Loading desktop... Please wait...", fg="white", bg="black", font=("Arial", 25)).pack(pady=50)
    progress = ttk.Progressbar(loading, orient="horizontal", length=500, mode="determinate")
    progress.pack(pady=20)
    progress["maximum"] = 100

    for i in range(101):
        progress["value"] = i
        loading.update()
        time.sleep(5/100)

    loading.destroy()

# ----------------------------
# Vragenlijst
# ----------------------------
def form_window():
    form = tk.Tk()
    form.title("User Form")
    form.geometry("400x250")

    tk.Label(form, text="Enter your name:").pack(pady=5)
    name_entry = tk.Entry(form)
    name_entry.pack(pady=5)

    tk.Label(form, text="Enter your email:").pack(pady=5)
    email_entry = tk.Entry(form)
    email_entry.pack(pady=5)

    def submit():
        name = name_entry.get()
        email = email_entry.get()
        if name.strip() == "" or email.strip() == "":
            messagebox.showwarning("Incomplete", "Please fill all fields!")
        else:
            form.destroy()
            loading_screen()
            fake_ransomware(name)

    tk.Button(form, text="Submit", command=submit).pack(pady=20)
    form.mainloop()

# Start programma
form_window()
