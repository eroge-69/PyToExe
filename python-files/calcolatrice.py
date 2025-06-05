
import tkinter as tk

class Calcolatrice:
    def __init__(self, root):
        self.root = root
        self.root.title("Calcolatrice")
        self.root.geometry("300x400")
        self.expression = ""

        self.input_text = tk.StringVar()
        input_frame = tk.Frame(self.root, width=312, height=50, bd=0, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        input_frame.pack(side=tk.TOP)
        
        input_field = tk.Entry(input_frame, font=('arial', 18, 'bold'), textvariable=self.input_text, width=50, bg="#eee", bd=0, justify=tk.RIGHT)
        input_field.grid(row=0, column=0)
        input_field.pack(ipady=10)
        
        btns_frame = tk.Frame(self.root, width=312, height=272.5, bg="grey")
        btns_frame.pack()
        
        buttons = [
            ('C', 1, 0), ('/', 1, 1), ('*', 1, 2), ('-', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('+', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('=', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('.', 4, 3),
            ('0', 5, 0)
        ]

        for (text, row, col) in buttons:
            if text == '0':
                tk.Button(btns_frame, text=text, fg="black", width=32, height=3, bd=0, bg="#fff",
                          cursor="hand2", command=lambda t=text: self.click(t)).grid(row=row, column=col, columnspan=4)
            elif text == '=':
                tk.Button(btns_frame, text=text, fg="black", width=10, height=3, bd=0, bg="#eee",
                          cursor="hand2", command=self.evaluate).grid(row=row, column=col)
            elif text == 'C':
                tk.Button(btns_frame, text=text, fg="black", width=10, height=3, bd=0, bg="#eee",
                          cursor="hand2", command=self.clear).grid(row=row, column=col)
            else:
                tk.Button(btns_frame, text=text, fg="black", width=10, height=3, bd=0, bg="#fff",
                          cursor="hand2", command=lambda t=text: self.click(t)).grid(row=row, column=col)

    def click(self, item):
        self.expression += str(item)
        self.input_text.set(self.expression)

    def clear(self):
        self.expression = ""
        self.input_text.set("")

    def evaluate(self):
        try:
            result = str(eval(self.expression))
            self.input_text.set(result)
            self.expression = result
        except:
            self.input_text.set("Errore")
            self.expression = ""

if __name__ == "__main__":
    root = tk.Tk()
    Calcolatrice(root)
    root.mainloop()
