import tkinter as tk

def main():
    window = tk.Tk()
    window.title("A Special Message")
    window.geometry("600x600")
    canvas = tk.Canvas(window, width=600, height=600, bg="white")
    canvas.pack()

    canvas.create_oval(275, 150, 325, 450, fill="peach puff", outline="black", width=2)
    canvas.create_oval(265, 140, 335, 200, fill="light salmon", outline="black", width=2)

    canvas.create_oval(225, 440, 295, 500, fill="peach puff", outline="black", width=2)
    canvas.create_oval(305, 440, 375, 500, fill="peach puff", outline="black", width=2)

    canvas.create_text(150, 300, text="FUCK YOU", font=("Impact", 40), fill="red")
    canvas.create_text(450, 300, text="NIGGER", font=("Impact", 40), fill="dark blue")

    window.mainloop()

if __name__ == "__main__":
    main()