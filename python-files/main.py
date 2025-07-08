import tkinter as tk


class SplashScreen1:
    def __init__(self, master):
        self.master = master
        master.title("Carrix Purview Key Generator")

        master.geometry("800x300")
        self.label = tk.Label(master, text="Welcome to Microsoft Purview Key Generator", font=('Arial', 20))
        self.label.pack(pady=20)

        self.button = tk.Button(master, text="Click To Continue", command=self.open_splash2)
        self.button.pack()

    def open_splash2(self):
        # Destroy the first splash screen
        self.master.destroy()

        # Create and open the second splash screen
        splash2_root = tk.Tk()
        splash2 = SplashScreen2(splash2_root)
        splash2_root.mainloop()


class SplashScreen2:
    def __init__(self, master):
        self.master = master
        master.title("What is wrong with you?")
        master.geometry("800x300")
        self.label = tk.Label(master, text="Seriously You Clicked On It!!! WTF????", font=('Arial', 20))
        self.label.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    splash1 = SplashScreen1(root)
    root.mainloop()

