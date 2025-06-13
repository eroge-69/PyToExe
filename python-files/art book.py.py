
import tkinter as tk

def calculate():
    try:
        # პირველი გრაფა
        sigarshi1 = float(entry_sigarshi1.get())
        simetria1 = float(entry_simetria1.get())
        raodenoba1 = int(sigarshi1 // simetria1)
        darcheuli1 = round(sigarshi1 - (raodenoba1 * simetria1), 2)

        # მეორე გრაფა (სიმაღლე)
        simagle2 = float(entry_sigarshi2.get())
        simetria2 = float(entry_simetria2.get())
        raodenoba2 = int(simagle2 // simetria2)
        darcheuli2 = round(simagle2 - (raodenoba2 * simetria2), 2)

        # ჯამური რაოდენობა = raodenoba1 * raodenoba2
        jami_raodenoba = raodenoba1 * raodenoba2

        # შედეგების გამოტანა
        label_raq1.config(text=f"რაოდენობა: {raodenoba1}")
        label_dar1.config(text=f"დარჩენილი მმ: {darcheuli1}")

        label_raq2.config(text=f"რაოდენობა: {raodenoba2}")
        label_dar2.config(text=f"დარჩენილი მმ: {darcheuli2}")

        label_jami.config(text=f"ჯამური რაოდენობა: {jami_raodenoba}")

    except ValueError:
        label_raq1.config(text="შეიყვანე სწორი რიცხვები")
        label_dar1.config(text="")
        label_raq2.config(text="")
        label_dar2.config(text="")
        label_jami.config(text="")

root = tk.Tk()
root.title("არტბუკი")
root.geometry("350x400")

# პირველი გრაფა
tk.Label(root, text="I გრაფა").pack()
tk.Label(root, text="სიგრძე:").pack()
entry_sigarshi1 = tk.Entry(root)
entry_sigarshi1.pack()

tk.Label(root, text="სიმეტრია:").pack()
entry_simetria1 = tk.Entry(root)
entry_simetria1.pack()

label_raq1 = tk.Label(root, text="რაოდენობა:")
label_raq1.pack()
label_dar1 = tk.Label(root, text="დარჩენილი მმ:")
label_dar1.pack()

tk.Label(root, text="").pack()  # სიცარიელე

# მეორე გრაფა
tk.Label(root, text="II გრაფა").pack()
tk.Label(root, text="სიმაღლე:").pack()  # შეცვლილია სიგრძე → სიმაღლე
entry_sigarshi2 = tk.Entry(root)
entry_sigarshi2.pack()

tk.Label(root, text="სიმეტრია:").pack()
entry_simetria2 = tk.Entry(root)
entry_simetria2.pack()

label_raq2 = tk.Label(root, text="რაოდენობა:")
label_raq2.pack()
label_dar2 = tk.Label(root, text="დარჩენილი მმ:")
label_dar2.pack()

tk.Label(root, text="").pack()  # სიცარიელე

# გამოთვლა
tk.Button(root, text="გამოთვალე", command=calculate).pack(pady=10)
label_jami = tk.Label(root, text="ჯამური რაოდენობა:")
label_jami.pack()

root.mainloop()
