import tkinter as tk

class Error:
    def __init__(self, root):
        self.root = root
        self.root.title("Error!")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=10, height=10, bg='#000000')
        self.canvas.pack()
        self.root.after(0, self.error)

    def error(self):
        root.withdraw()
        self.error = self.error
        score_window = tk.Toplevel(self.root)
        score_window.title("Error!")
        score_window.geometry("200x150")
        score_window.resizable(False, False)
        self.canvas = tk.Canvas(score_window, width=200, height=150, bg='#FFFFFF')
        self.canvas.pack()
        self.canvas.create_text(100, 75, text="Error!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!"
        "\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!\nError!Error!Error!Error!Error!Error!Error!")
        self.root.after(100, self.error)

if __name__ == "__main__":
    root = tk.Tk()
    game = Error(root)
    root.mainloop()