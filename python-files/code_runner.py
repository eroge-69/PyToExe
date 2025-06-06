import tkinter as tk
import sys

class ConsoleTerminal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Console Terminal")
        self.geometry("700x600")

        # Output (Console)
        self.output_text = tk.Text(self, height=20, bg="black", fg="white",
                                   font=("Consolas", 12), state=tk.NORMAL)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.output_text.insert(tk.END, "This is a output. Error messages or prints will appear here.\n")
        self.output_text.config(state=tk.DISABLED)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", pady=(0, 5))

        self.run_button = tk.Button(button_frame, text="Run Code", command=self.run_code)
        self.run_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = tk.Button(button_frame, text="Clear Output", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=10)

        # Input (Terminal)
        self.input_text = tk.Text(self, height=8, bg="black", fg="white",
                                  insertbackground="white", font=("Consolas", 12))
        self.input_text.pack(fill="both", padx=5, pady=(0, 5))
        self.input_text.insert(tk.END, "# Enter some code\n")

        # Redirect output
        sys.stdout = self
        sys.stderr = self

    def write(self, message):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, message)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def flush(self):
        pass

    def run_code(self):
        code = self.input_text.get("1.0", tk.END)
        self.input_text.delete("1.0", tk.END)
        try:
            exec(code, globals())
        except Exception as e:
            print(f"Error: {e}")

    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "This is a output. Error messages or prints will appear here.\n")
        self.output_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = ConsoleTerminal()
    app.mainloop()

# print('\u5350', "vs", '\u262d')
# print("DE*   USSR*")

