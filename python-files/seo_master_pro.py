
import openai
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# --- CONFIGURATION ---
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"  # Replace with your OpenAI API key

# --- CORE LOGIC ---
def generate_description(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# --- GUI APP ---
class SEOMasterPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SEO Master Pro")
        self.geometry("700x500")

        tk.Label(self, text="Enter Keywords or Topic:").pack(pady=5)
        self.input_text = scrolledtext.ScrolledText(self, height=5)
        self.input_text.pack(fill="x", padx=10)

        tk.Button(self, text="Generate SEO Description", command=self.generate).pack(pady=10)

        tk.Label(self, text="SEO Description:").pack(pady=5)
        self.output_text = scrolledtext.ScrolledText(self, height=10)
        self.output_text.pack(fill="both", expand=True, padx=10)

    def generate(self):
        prompt = f"Write a professional SEO-friendly description based on these keywords or topic: {self.input_text.get('1.0', 'end').strip()}"
        result = generate_description(prompt)
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('end', result)


if __name__ == "__main__":
    app = SEOMasterPro()
    app.mainloop()
