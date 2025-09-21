import tkinter as tk
from tkinter import font as tkfont
from threading import Thread
import time

class Calculator:
    """
    A simple GUI calculator with a professional look, themed with the
    colors of the Indian national flag, and a blinking light effect.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Indian Flag Calculator")
        self.master.geometry("400x550")
        self.master.resizable(False, False)
        self.master.config(bg="#F0F0F0")

        # Define colors of the Indian flag
        self.saffron = "#FF9933"
        self.white = "#FFFFFF"
        self.green = "#138808"
        self.navy_blue = "#000080"
        self.light_gray = "#E0E0E0"
        self.dark_gray = "#C0C0C0"

        # Fonts
        self.display_font = tkfont.Font(family="Arial", size=24, weight="bold")
        self.button_font = tkfont.Font(family="Arial", size=18, weight="bold")

        # Display for the calculator
        self.display = tk.Entry(
            master,
            font=self.display_font,
            bg=self.white,
            fg="#333333",
            bd=5,
            relief=tk.SUNKEN,
            justify=tk.RIGHT,
            insertbackground="#333333"
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Frame for blinking lights
        self.light_frame = tk.Frame(master, bg=self.navy_blue, height=10, relief=tk.RAISED)
        self.light_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="ew")

        # Start the blinking lights effect in a separate thread
        self.blinking_thread = Thread(target=self.blinking_lights)
        self.blinking_thread.daemon = True
        self.blinking_thread.start()

        # Button layout
        buttons = [
            'C', '/', '*', '-',
            '7', '8', '9', '+',
            '4', '5', '6', '(',
            '1', '2', '3', ')',
            '0', '.', '=', ' '
        ]

        # Create buttons and assign commands
        row_val = 2
        col_val = 0
        for button_text in buttons:
            if button_text == '=':
                button = tk.Button(
                    master,
                    text=button_text,
                    font=self.button_font,
                    bg=self.navy_blue,
                    fg=self.white,
                    activebackground=self.navy_blue,
                    activeforeground=self.white,
                    command=self.calculate,
                    relief=tk.RAISED,
                    bd=3
                )
            elif button_text == 'C':
                button = tk.Button(
                    master,
                    text=button_text,
                    font=self.button_font,
                    bg=self.saffron,
                    fg=self.white,
                    activebackground=self.saffron,
                    activeforeground=self.white,
                    command=self.clear,
                    relief=tk.RAISED,
                    bd=3
                )
            elif button_text in '+-*/()':
                button = tk.Button(
                    master,
                    text=button_text,
                    font=self.button_font,
                    bg=self.green,
                    fg=self.white,
                    activebackground=self.green,
                    activeforeground=self.white,
                    command=lambda x=button_text: self.on_button_click(x),
                    relief=tk.RAISED,
                    bd=3
                )
            elif button_text == ' ':  # Empty button for layout
                 button = tk.Label(master, bg="#F0F0F0")
            else:
                button = tk.Button(
                    master,
                    text=button_text,
                    font=self.button_font,
                    bg=self.light_gray,
                    fg="#333333",
                    activebackground=self.dark_gray,
                    activeforeground="#333333",
                    command=lambda x=button_text: self.on_button_click(x),
                    relief=tk.RAISED,
                    bd=3
                )

            # Grid the button
            button.grid(
                row=row_val,
                column=col_val,
                sticky="nsew",
                padx=5,
                pady=5,
                ipadx=10,
                ipady=10
            )

            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1
        
        # Configure row and column weights for a responsive layout
        for i in range(5):
            self.master.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.master.grid_columnconfigure(i, weight=1)

    def on_button_click(self, char):
        """Appends the clicked character to the display."""
        self.display.insert(tk.END, char)

    def clear(self):
        """Clears the display."""
        self.display.delete(0, tk.END)

    def calculate(self):
        """
        Calculates the result of the expression in the display.
        Uses a try-except block to handle calculation errors.
        """
        try:
            expression = self.display.get()
            result = eval(expression)
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, str(result))
        except (SyntaxError, NameError, ZeroDivisionError) as e:
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, "Error")

    def blinking_lights(self):
        """
        A function to create a blinking light effect on the GUI.
        It cycles through the Indian flag colors.
        """
        colors = [self.saffron, self.white, self.green, self.navy_blue]
        current_color_index = 0
        
        def cycle_colors():
            nonlocal current_color_index
            self.light_frame.config(bg=colors[current_color_index])
            current_color_index = (current_color_index + 1) % len(colors)
            self.master.after(500, cycle_colors) # Call itself again after 500ms
        
        cycle_colors()

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
