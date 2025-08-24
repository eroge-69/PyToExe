
import tkinter as tk

def create_calculator():
    root = tk.Tk()
    root.title("Simple Calculator")
    root.configure(bg="grey")

    # Entry widget to display the current input/result
    entry = tk.Entry(root, width=17, borderwidth=5, font=("Arial", 24))
    entry.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

    def button_click(number):
        current = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, str(current) + str(number))

    def button_clear():
        entry.delete(0, tk.END)

    def button_add():
        current_text = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, current_text + "+")

    def button_subtract():
        current_text = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, current_text + "-")

    def button_multiply():
        current_text = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, current_text + "*")

    def button_divide():
        current_text = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, current_text + "/")

    def button_backspace():
        current = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, current[:-1])

    def button_equal():
        full_expression = entry.get()
        try:
            result = eval(full_expression)
            entry.delete(0, tk.END)
            entry.insert(0, str(result))
        except (SyntaxError, ZeroDivisionError, TypeError):
            entry.delete(0, tk.END)
            entry.insert(0, "Error")

    # Define buttons
    button_1 = tk.Button(root, text="1", padx=40, pady=20, command=lambda: button_click(1))
    button_2 = tk.Button(root, text="2", padx=40, pady=20, command=lambda: button_click(2))
    button_3 = tk.Button(root, text="3", padx=40, pady=20, command=lambda: button_click(3))
    button_4 = tk.Button(root, text="4", padx=40, pady=20, command=lambda: button_click(4))
    button_5 = tk.Button(root, text="5", padx=40, pady=20, command=lambda: button_click(5))
    button_6 = tk.Button(root, text="6", padx=40, pady=20, command=lambda: button_click(6))
    button_7 = tk.Button(root, text="7", padx=40, pady=20, command=lambda: button_click(7))
    button_8 = tk.Button(root, text="8", padx=40, pady=20, command=lambda: button_click(8))
    button_9 = tk.Button(root, text="9", padx=40, pady=20, command=lambda: button_click(9))
    button_0 = tk.Button(root, text="0", padx=40, pady=20, command=lambda: button_click(0))
    button_add_btn = tk.Button(root, text="+", padx=39, pady=20, command=button_add)
    button_equal_btn = tk.Button(root, text="=", padx=91, pady=20, command=button_equal)
    button_clear_btn = tk.Button(root, text="Clear", padx=79, pady=20, command=button_clear)
    button_subtract_btn = tk.Button(root, text="-", padx=41, pady=20, command=button_subtract)
    button_multiply_btn = tk.Button(root, text="*", padx=40, pady=20, command=button_multiply)
    button_divide_btn = tk.Button(root, text="/", padx=41, pady=20, command=button_divide)
    button_backspace_btn = tk.Button(root, text="←", padx=35, pady=20, command=button_backspace)

    # Put the buttons on the screen
    button_1.grid(row=3, column=0)
    button_2.grid(row=3, column=1)
    button_3.grid(row=3, column=2)

    button_4.grid(row=2, column=0)
    button_5.grid(row=2, column=1)
    button_6.grid(row=2, column=2)

    button_7.grid(row=1, column=0)
    button_8.grid(row=1, column=1)
    button_9.grid(row=1, column=2)

    button_0.grid(row=4, column=0)

    button_clear_btn.grid(row=5, column=0, columnspan=3)
    button_equal_btn.grid(row=6, column=0, columnspan=4)

    button_add_btn.grid(row=5, column=3)
    button_subtract_btn.grid(row=4, column=3)
    button_multiply_btn.grid(row=3, column=3)
    button_divide_btn.grid(row=2, column=3)
    button_backspace_btn.grid(row=1, column=3)

    root.mainloop()

if __name__ == "__main__":
    create_calculator()




