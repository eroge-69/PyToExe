import tkinter as tk
window = tk.Tk()
# Cài đặt vị trí cửa sổ
width = 800
height = 600
window.resizable(False, False)
x = (window.winfo_screenwidth() - width)//2
y = (window.winfo_screenheight() - height)//2
window.geometry(f"{width}x{height}+{x}+{y}")
window.update_idletasks()
window.title("Demo Grid")
# Thêm label
lbl_title = tk.Label(window, text="Sử dụng Grid", font=("Monospace", 40))
lbl_title.pack()

### FRAME ###
frm = tk.Frame(master=window)
frm.pack(fill="both", expand=True)
frm.pack_propagate(False)
img1 = tk.PhotoImage(file="gundam1.png")
lbl_img1 = tk.Label(master=frm, image=img1)
lbl_img1.grid(row=0, column=0)

img2 = tk.PhotoImage(file="gundam2.png")
lbl_img2 = tk.Label(master=frm, image=img2)
lbl_img2.grid(row=0, column=1)

window.mainloop()



