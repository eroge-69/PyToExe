import tkinter as tk

root = tk.Tk()
root.title('Кто у кого сосал?')
root.geometry("400x200")

ans_label = tk.Label(root, text='', font=("Arial", 12), fg='black')
ans_label.place(relx=0.5, rely=0.6, anchor='center')


def kto_sosal_1():
    ans_label.config(text='У Антона сосала Полька конечно же!!!')


def kto_sosal_2():
    ans_label.config(text='У Мурада сосала Алиночка есстественно!!!')


btn_a = tk.Button(
                        root,
                        text='Кто сосал у Антона?',
                        command=kto_sosal_1,
                        font=("Arial", 12),
                        width=16
                    )
btn_a.pack(pady=5)
btn_m = tk.Button(
                        root,
                        text='Кто сосал у Мурада?',
                        command=kto_sosal_2,
                        font=("Arial", 12),
                        width=16
                    )
btn_m.pack(pady=5)

root.mainloop()
