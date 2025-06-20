import customtkinter as ctk
import random
import re
from textblob import TextBlob
import pyperclip

class TextHumanizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clitext humanizer")
        self.root.geometry("800x600")
        self.root.iconbitmap("clitext.ico")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tabview.add("Humanize Text")
        self.tabview.add("AI Detection")
        self.tabview.add("About the software")

        self.setup_humanize_tab()
        self.setup_detection_tab()
        self.setup_about_tab()

    def setup_humanize_tab(self):
        tab = self.tabview.tab("Humanize Text")

        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(input_frame, text="Input content:", font=("Arial", 14)).pack(anchor="w", padx=5)
        self.input_text = ctk.CTkTextbox(input_frame, height=150, font=("Arial", 12))
        self.input_text.pack(padx=5, pady=5, fill="both", expand=True)

        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Humanize Text", command=self.humanize_text).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_humanize).pack(side="left", padx=5)

        output_frame = ctk.CTkFrame(tab)
        output_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(output_frame, text="Humanized Text:", font=("Arial", 14)).pack(anchor="w", padx=5)
        self.output_text = ctk.CTkTextbox(output_frame, height=150, font=("Arial", 12))
        self.output_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.output_text.configure(state="disabled")

        ctk.CTkButton(output_frame, text="Copy", command=self.copy_humanized_text).pack(pady=5)

    def setup_detection_tab(self):
        tab = self.tabview.tab("AI Detection")

        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(input_frame, text="Text to Analyze:", font=("Arial", 14)).pack(anchor="w", padx=5)
        self.detect_text = ctk.CTkTextbox(input_frame, height=150, font=("Arial", 12))
        self.detect_text.pack(padx=5, pady=5, fill="both", expand=True)

        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(pady=10)
        ctk.CTkButton(button_frame, text="Analyze Text", command=self.analyze_text).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Clear", command=self.clear_detection).pack(side="left", padx=5)

        result_frame = ctk.CTkFrame(tab)
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)

        ctk.CTkLabel(result_frame, text="Analysis Result:", font=("Arial", 14)).pack(anchor="w", padx=5)
        self.result_text = ctk.CTkTextbox(result_frame, height=150, font=("Arial", 12))
        self.result_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.result_text.configure(state="disabled")

        ctk.CTkButton(result_frame, text="Copy", command=self.copy_detection_result).pack(pady=5)

    def setup_about_tab(self):
        tab = self.tabview.tab("About the software")

        about_text = """
ABOUT THE CLITEXT HUMANIZER SOFTWARE


This application helps you humanize AI-generated text and detect AI-written content. It can assist in humanizing AI-generated research content, job support letters, and more.
 

📝 HOW TO USE:
1. **Humanize Text Tab**
   - Paste your text into the input box.
   - Click "Humanize Text" to transform it into a more natural, human-like format.
   - Use the "Copy" button to copy the result.

2. **AI Detection Tab**
   - Paste any text into the input box.
   - Click "Analyze Text" to check if it's likely AI-generated.
   - The result will show a score and reasoning.
   - Use the "Copy" button to copy the analysis.


N.B: You can use external humanizer website to confirm the effectiveness of the harmonized text from this software.


__________________________________________________________________________________________________________________________
   

👨‍💻 DEVELOPED BY: Abdulazeez Alao

📞 Phone: +353899476367

📧 Email: gearcoin@gmail.com
        """

        text_box = ctk.CTkTextbox(tab, font=("Arial", 13), wrap="word")
        text_box.insert("1.0", about_text.strip())
        text_box.configure(state="disabled")
        text_box.pack(padx=10, pady=10, fill="both", expand=True)

    def humanize_text(self):
        input_text = self.input_text.get("1.0", "end").strip()
        if not input_text:
            return

        blob = TextBlob(input_text)
        humanized = str(blob)

        variations = [
            (" is ", " seems to be "),
            (" are ", " appear to be "),
            (" very ", random.choice([" quite ", " rather ", " somewhat "])),
            (" therefore ", random.choice([" so ", " thus ", " hence "])),
        ]
        for old, new in variations:
            humanized = humanized.replace(old, new)

        sentences = humanized.split(". ")
        humanized = ". ".join(
            s + random.choice(["", " you know", " I mean"]) if random.random() < 0.1 else s
            for s in sentences
        )

        humanized = str(TextBlob(humanized).correct())

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", humanized)
        self.output_text.configure(state="disabled")

    def analyze_text(self):
        input_text = self.detect_text.get("1.0", "end").strip()
        if not input_text:
            return

        score = 0
        reasons = []

        formal_words = ["hence", "thus", "therefore", "moreover"]
        if any(word in input_text.lower() for word in formal_words):
            score += 20
            reasons.append("Contains formal language typical of AI output")

        sentences = re.split(r"[.!?]+", input_text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if len(set(sentence_lengths)) < len(sentence_lengths) / 2:
            score += 20
            reasons.append("Repetitive sentence structure detected")

        if " is " in input_text.lower() and "isn't" not in input_text.lower():
            score += 15
            reasons.append("Lack of contractions, common in AI text")

        if len(input_text.split()) > 100:
            score += 10
            reasons.append("Long text, potentially AI-generated")

        result = f"AI Likelihood Score: {score}%\n\n"
        if score > 50:
            result += "This text is likely AI-generated.\n"
        else:
            result += "This text appears human-written.\n"
        result += "\nReasons:\n" + "\n".join(f"- {r}" for r in reasons) if reasons else "No specific indicators found."

        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", result)
        self.result_text.configure(state="disabled")

    def clear_humanize(self):
        self.input_text.delete("1.0", "end")
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")

    def clear_detection(self):
        self.detect_text.delete("1.0", "end")
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.configure(state="disabled")

    def copy_humanized_text(self):
        humanized = self.output_text.get("1.0", "end").strip()
        pyperclip.copy(humanized)

    def copy_detection_result(self):
        result = self.result_text.get("1.0", "end").strip()
        pyperclip.copy(result)

if __name__ == "__main__":
    root = ctk.CTk()
    app = TextHumanizerApp(root)
    root.mainloop()
