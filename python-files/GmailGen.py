import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class GmailGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Gmail Address Generator")
        master.geometry("600x550")
        master.resizable(False, False) # Make window non-resizable

        # Configure styles for a modern look
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Inter', 10))
        self.style.configure('TButton', font=('Inter', 10, 'bold'), padding=8, relief="raised", borderwidth=2, foreground='#333')
        self.style.map('TButton',
                       background=[('active', '#e0e0e0'), ('!disabled', '#d0d0d0')],
                       foreground=[('active', '#000'), ('!disabled', '#333')])
        self.style.configure('TEntry', font=('Inter', 10), padding=5)
        self.style.configure('TCheckbutton', background='#f0f0f0', font=('Inter', 10))

        # Main frame
        self.main_frame = ttk.Frame(master, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Section
        self.input_frame = ttk.LabelFrame(self.main_frame, text="Base Gmail Address", padding="15")
        self.input_frame.pack(pady=10, fill=tk.X)

        ttk.Label(self.input_frame, text="Enter your Gmail address (e.g., johndoe@gmail.com):").pack(anchor=tk.W, pady=(0, 5))
        self.email_entry = ttk.Entry(self.input_frame, width=50)
        self.email_entry.pack(fill=tk.X, ipady=3) # Increased internal padding

        # Options Section
        self.options_frame = ttk.LabelFrame(self.main_frame, text="Generation Options", padding="15")
        self.options_frame.pack(pady=10, fill=tk.X)

        self.generate_dots_var = tk.BooleanVar(value=True)
        self.generate_plus_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(self.options_frame, text="Generate Dot Variations", variable=self.generate_dots_var).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(self.options_frame, text="Generate Plus Aliases", variable=self.generate_plus_var).pack(anchor=tk.W, pady=2)

        ttk.Label(self.options_frame, text="Plus Alias Tag (e.g., 'newsletter', 'signup'):").pack(anchor=tk.W, pady=(10, 5))
        self.plus_tag_entry = ttk.Entry(self.options_frame, width=30)
        self.plus_tag_entry.pack(fill=tk.X, ipady=3)
        self.plus_tag_entry.insert(0, "tag") # Default tag

        # Buttons
        self.button_frame = ttk.Frame(self.main_frame, padding="5")
        self.button_frame.pack(pady=10, fill=tk.X)

        self.generate_button = ttk.Button(self.button_frame, text="Generate Aliases", command=self.generate_aliases)
        self.generate_button.pack(side=tk.LEFT, expand=True, padx=5)

        self.copy_button = ttk.Button(self.button_frame, text="Copy All to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.RIGHT, expand=True, padx=5)

        # Output Section
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Generated Aliases", padding="15")
        self.output_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, width=60, height=10, font=('Inter', 10), relief="sunken", borderwidth=2)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.config(state=tk.DISABLED) # Make it read-only

    def generate_aliases(self):
        """
        Generates Gmail aliases based on user input and selected options.
        """
        base_email = self.email_entry.get().strip().lower()
        if not base_email:
            messagebox.showwarning("Input Error", "Please enter a base Gmail address.")
            return

        if "@gmail.com" not in base_email:
            messagebox.showwarning("Input Error", "Please enter a valid @gmail.com address.")
            return

        # Extract local part and domain
        local_part = base_email.split('@')[0]
        domain = "@" + base_email.split('@')[1]

        generated_emails = set()
        generated_emails.add(base_email) # Always include the original email

        # Generate dot variations
        if self.generate_dots_var.get():
            # Remove existing dots for canonical form
            canonical_local_part = local_part.replace('.', '')
            dot_variations = self._generate_dot_variations(canonical_local_part)
            for var in dot_variations:
                generated_emails.add(var + domain)

        # Generate plus aliases
        if self.generate_plus_var.get():
            plus_tag = self.plus_tag_entry.get().strip()
            if plus_tag:
                # Add plus alias to all currently generated emails (including original and dot variations)
                current_emails = list(generated_emails) # Create a copy to iterate
                for email in current_emails:
                    parts = email.split('@')
                    # Ensure we don't add multiple plus signs
                    if '+' not in parts[0]:
                        generated_emails.add(f"{parts[0]}+{plus_tag}@{parts[1]}")
            else:
                messagebox.showinfo("Info", "Plus Alias Tag is empty. Skipping plus alias generation.")


        # Display generated emails
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        for email in sorted(list(generated_emails)):
            self.output_text.insert(tk.END, email + "\n")
        self.output_text.config(state=tk.DISABLED)

    def _generate_dot_variations(self, s):
        """
        Recursively generates all possible dot variations for a string.
        Example: "abc" -> "abc", "a.bc", "ab.c", "a.b.c"
        """
        if not s:
            return {""}
        
        first_char = s[0]
        rest_of_string = s[1:]
        
        variations = set()
        for sub_variation in self._generate_dot_variations(rest_of_string):
            # Option 1: Add first_char without a dot
            variations.add(first_char + sub_variation)
            # Option 2: Add first_char with a dot, if sub_variation is not empty
            if sub_variation: # Avoid leading dot
                variations.add(first_char + "." + sub_variation)
        return variations

    def copy_to_clipboard(self):
        """
        Copies the content of the output text area to the clipboard.
        """
        content = self.output_text.get(1.0, tk.END).strip()
        if content:
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            messagebox.showinfo("Copied!", "All generated aliases copied to clipboard.")
        else:
            messagebox.showinfo("Empty", "No aliases to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GmailGeneratorApp(root)
    root.mainloop()
