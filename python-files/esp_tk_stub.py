import tkinter as tk

def main():
    root = tk.Tk()
    root.title("ESP")
    root.geometry("300x100")
    label = tk.Label(root, text="ESP Stub (No Simulation Working)", font=("Arial", 14))
    label.pack(expand=True, fill="both")
    root.mainloop()

if __name__ == "__main__":
    main()