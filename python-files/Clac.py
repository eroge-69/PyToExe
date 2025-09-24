import tkinter as tk
import random

#operations:
def add(a, b):
    answer = a + b
    print(answer)
    ans = tk.Label(root, text=answer)
    ans.grid(row=5, column=1)
    
def subtract(a,b):
    answer = a - b
    print(answer)
    ans = tk.Label(root, text=answer)
    ans.grid(row=5, column=1)

def multiply(a,b):
    answer = a * b
    print(answer)
    ans = tk.Label(root, text=answer)
    ans.grid(row=5, column=1)

def divide(a,b):
    answer = a / b
    print(answer)
    ans = tk.Label(root, text=answer)
    ans.grid(row=5, column=1)

#Calc func
def calculate():
    a = float(e1.get())
    b = float(e2.get())
    op = e3.get()
    if op == '+':
        add(a, b)
    elif op == '-':
        subtract(a, b)
    elif op == '*':
        multiply(a, b)
    elif op == '/':
        divide(a, b)

root = tk.Tk()
tk.Label(root, text="Value 1: ").grid(row=0)
tk.Label(root, text="Value 2: ").grid(row=1)
tk.Label(root, text="Operator: ").grid(row=2)
ans = tk.Label(root, text="........")

e1 = tk.Entry(root)
e2 = tk.Entry(root)
e3 = tk.Entry(root)
b1 = tk.Button(root, text="Calculate", command=calculate)


e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
b1.grid(row=5, column=0)
ans.grid(row=5, column=1)

root.mainloop()