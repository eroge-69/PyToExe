import tkinter as tk
from tkinter import messagebox, scrolledtext
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Full textbook content (shortened here for brevity — use your full text)
BOOK_TEXT = """[INSERT YOUR FULL SCIENCE TEXT HERE]"""  # Paste your full BOOK_TEXT here

class FullTextScienceChatbot:
    def __init__(self, full_text):
        self.paragraphs = [p.strip() for p in full_text.split('\n\n') if len(p.strip()) > 20]
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.doc_vectors = self.vectorizer.fit_transform(self.paragraphs)

    def get_answer(self, question):
        question_vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vec, self.doc_vectors).flatten()
        best_idx = similarities.argmax()
        if similarities[best_idx] < 0.1:
            return "Sorry, I couldn't find a good answer. Try rephrasing your question."
        return self.paragraphs[best_idx]

# GUI application
class ChatbotGUI:
    def __init__(self, root):
        self.chatbot = FullTextScienceChatbot(BOOK_TEXT)
        self.root = root
        self.root.title("Class 6 Science Chatbot")
        self.root.geometry("600x500")
        self.root.configure(bg="#eef2f3")

        # Widgets
        self.label = tk.Label(root, text="Ask any Class 6 Science question:", bg="#eef2f3", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, font=("Arial", 12), width=60)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.get_response)

        self.ask_btn = tk.Button(root, text="Get Answer", command=self.get_response, font=("Arial", 12), bg="#4caf50", fg="white")
        self.ask_btn.pack()

        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20, font=("Arial", 11))
        self.output.pack(padx=10, pady=10)

    def get_response(self, event=None):
        question = self.entry.get().strip()
        if not question:
            messagebox.showwarning("Input Needed", "Please type a question.")
            return

        answer = self.chatbot.get_answer(question)
        self.output.insert(tk.END, f"You: {question}\nChatBot: {answer}\n\n")
        self.output.see(tk.END)
        self.entry.delete(0, tk.END)

# Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGUI(root)
    root.mainloop()