#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Calculator GUI (Tkinter)
- Safe expression evaluator (no eval)
- Supports +, -, *, /, %, **, parentheses, decimals
- Clear (C) and Backspace (⌫)
- Keyboard input: digits, operators, Enter (=), Backspace, Escape (clear)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ast
import operator as op

# ---------- Safe Evaluator ----------
# Allowed operators
_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.FloorDiv: op.floordiv,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}

def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Num):  # Py<3.8 fallback
        return node.n
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Paren) or isinstance(node, ast.Tuple):
        # Parentheses are represented in the tree structure; nothing to do explicitly.
        raise ValueError("Invalid expression.")
    raise ValueError("Unsupported or unsafe expression.")

def safe_eval(expr: str):
    """
    Safely evaluate a math expression string and return a float.
    Allowed: numbers, + - * / % **, parentheses, unary +/-
    """
    try:
        tree = ast.parse(expr, mode="eval")
        return _eval_node(tree.body)
    except ZeroDivisionError:
        raise
    except Exception as e:
        raise ValueError("Invalid expression.") from e

# ---------- GUI ----------
class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("200x300")
        self.minsize(400, 550)
        self.configure(padx=10, pady=10)
        self._build_ui()
        self._bind_keys()

    def _build_ui(self):
        # Style
        style = ttk.Style(self)
        try:
            self.call("tk", "scaling", 1.2)  # improve DPI scaling on some systems
        except Exception:
            pass
        style.configure("Display.TEntry", font=("Segoe UI", 18))
        style.configure("Calc.TButton", font=("Segoe UI", 14), padding=10)

        # Display
        self.var = tk.StringVar(value="")
        self.display = ttk.Entry(self, textvariable=self.var, justify="right", style="Display.TEntry")
        self.display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=(0,0), pady=(0,10))
        self.display.focus_set()

        # Buttons
        btns = [
            ("C", 1, 0), ("⌫", 1, 1), ("%", 1, 2), ("/", 1, 3),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),
            ("0", 5, 0), (".", 5, 1), ("(", 5, 2), (")", 5, 3),
            ("x²", 6, 0), ("xʸ", 6, 1), ("//", 6, 2), ("=", 6, 3),
        ]

        for (text, r, c) in btns:
            action = (lambda t=text: self.on_button(t))
            btn = ttk.Button(self, text=text, style="Calc.TButton", command=action)
            btn.grid(row=r, column=c, sticky="nsew", padx=5, pady=5)

        # Grid weights
        for i in range(7):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

    # --- logic ---
    def on_button(self, text: str):
        if text == "C":
            self.var.set("")
        elif text == "⌫":
            self.var.set(self.var.get()[:-1])
        elif text == "=":
            self.evaluate()
        elif text == "x²":
            self.var.set(self.var.get() + "**2")
        elif text == "xʸ":
            self.var.set(self.var.get() + "**")
        else:
            self.var.set(self.var.get() + text)

    def _insert(self, s: str):
        self.var.set(self.var.get() + s)

    def evaluate(self, event=None):
        expr = self.var.get().strip()
        if not expr:
            return
        try:
            res = safe_eval(expr)
            # remove trailing .0 for ints
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            self.var.set(str(res))
        except ZeroDivisionError:
            messagebox.showerror("Error", "Division by zero.")
        except Exception:
            messagebox.showerror("Error", "Invalid expression.")

    # --- key bindings ---
    def _bind_keys(self):
        self.bind("<Return>", self.evaluate)
        self.bind("<KP_Enter>", self.evaluate)
        self.bind("<Escape>", lambda e: self.var.set(""))
        self.bind("<BackSpace>", lambda e: self.var.set(self.var.get()[:-1]))
        # Allow typing into the entry directly
        self.display.bind("<Key>", lambda e: None)

def main():
    app = Calculator()
    app.mainloop()

if __name__ == "__main__":
    main()
