import customtkinter as ctk

root = ctk.CTk()
root.geometry("400x240")
root.title("CTkLabelFrame")

label_frame = ctk.CTkLabel(master=root, text="CTkLabelFrame")
label_frame.pack(pady=20, padx=60, fill="both", expand=True)




root.mainloop()