def create_gui():
    window = tk.Tk()
    window.title("Interface Simples")
    window.geometry("300x200")
    window.resizable(False, False)
    button = tk.Button(
        window,
        text="Clique em Mim",
        font=("Arial", 12),
        padx=10,
        pady=5,
        command=lambda: None
    )
    button.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
    window.mainloop()

if __name__ == "__main__":
    create_gui()