# First, ensure you have the necessary libraries installed.
# You can run this command in your terminal:
# pip install cohere pyperclip

import tkinter as tk
from tkinter import ttk, messagebox
import cohere
import sys
import pyperclip
import threading

# WARNING: This is NOT a recommended security practice.
# Your API key will be visible in the code.
# For a real application, consider using environment variables or a secure configuration file.
COHERE_API_KEY = "sztIbfwPJ9abhjxMm7lVGLHmBTzd7p3vL7Ks0sOG"

class QuoteGeneratorApp:
    """
    A Tkinter-based desktop application for generating quotes
    using the Cohere API.
    """
    def __init__(self, root):
        # Initialize the main application window
        self.root = root
        self.root.title("Awesome Quote Generator")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # --- Check for API Key and initialize Cohere client ---
        if not COHERE_API_KEY:
            messagebox.showerror("Error", "API key is not set. Please update the script.")
            sys.exit(1)
        
        try:
            self.co = cohere.Client(api_key=COHERE_API_KEY)
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize Cohere client: {e}")
            sys.exit(1)

        # --- Define available moods and setup the GUI ---
        self.moods = ['Happy', 'Sad', 'Motivational', 'Inspirational', 'Funny']
        self.create_widgets()

    def create_widgets(self):
        """
        Sets up all the graphical components of the application.
        """
        # Main frame for padding and structure
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        title_label = ttk.Label(main_frame, text="Awesome Quote Generator", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=(0, 20))

        # Mood selection label
        mood_label = ttk.Label(main_frame, text="Select a mood:", font=("Helvetica", 12))
        mood_label.pack(pady=(0, 10))

        # Buttons for each mood
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 20))
        
        for mood in self.moods:
            # Command function uses a lambda to pass the mood to the generation method
            btn = ttk.Button(button_frame, text=mood, command=lambda m=mood: self.start_generation_thread(m))
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Separator line
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=10)

        # Quote display area
        self.quote_label = ttk.Label(main_frame, text="Click a button to generate a quote!", wraplength=550, 
                                     font=("Helvetica", 14, "italic"), justify="center")
        self.quote_label.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Loading indicator label
        self.loading_label = ttk.Label(main_frame, text="", font=("Helvetica", 10), foreground="gray")
        self.loading_label.pack(pady=5)

        # Copy button
        self.copy_button = ttk.Button(main_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(pady=(10, 0))

    def generate_quote_async(self, mood):
        """
        The core function to generate a quote and update the GUI.
        This runs in a separate thread.
        """
        self.root.after(0, lambda: self.loading_label.config(text="Generating..."))
        self.root.after(0, lambda: self.quote_label.config(text=""))
        self.root.after(0, lambda: self.copy_button.config(state=tk.DISABLED))
        
        # Map moods to specific Cohere prompts
        prompt_map = {
            'Happy': "Generate a single, uplifting and memorable quote about finding happiness in everyday life, with a relevant emoji at the end.",
            'Sad': "Generate a single, thoughtful quote about navigating through a sad moment, with a relevant emoji at the end.",
            'Motivational': "Generate a single, powerful quote that motivates someone to take action and overcome challenges, with a relevant emoji at the end.",
            'Inspirational': "Generate a single, inspirational quote about believing in oneself and personal growth, with a relevant emoji at the end.",
            'Funny': "Generate a single, very short and clever quote that is humorous and light-hearted, with a relevant emoji at the end. Make it a funny saying or observation."
        }

        prompt = prompt_map.get(mood)
        
        try:
            response = self.co.generate(
                prompt=prompt,
                model="command",
                max_tokens=40,
                temperature=0.9,
            )
            quote = response.generations[0].text.strip()
        except Exception as e:
            quote = f"An error occurred: {e}"

        # Update the GUI from the main thread after generation is complete
        # Use .after() to safely call a function on the main thread
        self.root.after(0, self.update_gui_with_quote, quote)

    def update_gui_with_quote(self, quote):
        """
        Updates the quote label and other widgets with the generated text.
        """
        self.quote_label.config(text=quote)
        self.loading_label.config(text="")
        
        # Only enable copy button if the quote was generated successfully
        if not quote.startswith("An error occurred:"):
            self.copy_button.config(state=tk.NORMAL)

    def start_generation_thread(self, mood):
        """
        Spawns a new thread to run the quote generation to prevent the GUI from freezing.
        """
        thread = threading.Thread(target=self.generate_quote_async, args=(mood,))
        thread.daemon = True  # Allows the application to exit even if the thread is running
        thread.start()

    def copy_to_clipboard(self):
        """
        Copies the currently displayed quote to the clipboard.
        """
        quote_text = self.quote_label.cget("text")
        if quote_text:
            try:
                pyperclip.copy(quote_text)
                messagebox.showinfo("Success", "Quote copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Copy Error", f"Failed to copy to clipboard: {e}")
        else:
            messagebox.showwarning("No Quote", "There is no quote to copy.")

# --- Main application entry point ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()
