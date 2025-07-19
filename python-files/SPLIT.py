import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText


def split_text(text: str, max_len: int) -> str:
    """
    Re-wrap *text* so that every output line is **≤ max_len** characters.

    • Prefers breaking at word boundaries (spaces).
    • If a single word is longer than *max_len* it is hyphenated:
      the first chunk takes *max_len − 1* characters plus “-”,  
      the remainder is processed again.

    Returns a newline-joined string.
    """
    words = text.split()                 # collapse all whitespace
    lines = []
    current = ""

    for word in words:
        # Handle over-long words by hyphenation
        while len(word) > max_len:
            # flush any accumulated text first
            if current:
                lines.append(current.rstrip())
                current = ""
            # split the word, keeping room for the hyphen
            lines.append(word[: max_len - 1] + "-")
            word = word[max_len - 1 :]

        # Try to append the (now short enough) word to the current line
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_len:
            current += " " + word
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return "\n".join(lines)


class SplitterGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Line-length text splitter")

        # --- input area ----------------------------------------------------
        ttk.Label(self, text="Input text:").grid(row=0, column=0, sticky="w")
        self.input_txt = ScrolledText(self, width=60, height=10, wrap=tk.WORD)
        self.input_txt.grid(row=1, column=0, columnspan=3, padx=4, pady=2)

        # --- options -------------------------------------------------------
        ttk.Label(self, text="Max line length:").grid(row=2, column=0, sticky="e")
        self.len_var = tk.StringVar(value="40")
        ttk.Entry(self, textvariable=self.len_var, width=6).grid(row=2, column=1, sticky="w")

        ttk.Button(self, text="Split text", command=self.do_split).grid(
            row=2, column=2, padx=6, pady=4
        )

        # --- output area ---------------------------------------------------
        ttk.Label(self, text="Result:").grid(row=3, column=0, sticky="w")
        self.output_txt = ScrolledText(self, width=60, height=10, wrap=tk.NONE)
        self.output_txt.grid(row=4, column=0, columnspan=3, padx=4, pady=(2, 6))

        # Nice spacing
        for col in range(3):
            self.grid_columnconfigure(col, weight=1)

    # ---------------------------------------------------------------------
    def do_split(self) -> None:
        try:
            max_len = int(self.len_var.get())
            if max_len < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid length", "Please enter an integer ≥ 2.")
            return

        raw = self.input_txt.get("1.0", tk.END).rstrip()
        result = split_text(raw, max_len)
        self.output_txt.delete("1.0", tk.END)
        self.output_txt.insert(tk.END, result)


if __name__ == "__main__":
    SplitterGUI().mainloop()