import tkinter as tk

window = tk.Tk()
window.title("Prime Checker")
window.geometry("300x200")

number_var = tk.StringVar()
result_label = tk.Label(window, text="", font=("Arial", 14))
result_label.pack(pady=10)

def Submit():
    try:
        potPri = int(number_var.get())
        if potPri < 2:
            result_label.config(text="Not prime")
            return
        
        for i in range(2, int(potPri ** 0.5) + 1):
            if potPri % i == 0:
                result_label.config(text="Not prime")
                return
        
        result_label.config(text="Prime")
    except ValueError:
        result_label.config(text="Please enter a valid number")

tk.Label(window, text="Enter a Number").pack(pady=5)
tk.Entry(window, textvariable=number_var).pack(pady=5)
tk.Button(window, text="Submit", command=Submit).pack(pady=10)

window.mainloop()
