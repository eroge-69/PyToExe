def mostra_messaggio():
        messagebox.showinfo("Test", "Ciao, questo è un test!")

    root = tk.Tk()
    root.title("Test App")
    button = tk.Button(root, text="Cliccami", command=mostra_messaggio)
    button.pack(pady=20)
    root.mainloop()
    ```