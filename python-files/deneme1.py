import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, scrolledtext, filedialog
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import csv
import os
import sys
import threading
import nltk
from nltk.corpus import stopwords

# Download stopwords if not already
nltk.download('stopwords', quiet=True)

QUESTIONS = [
    "What is your favorite food?",
    "Do you believe in fate?",
    "How many hours do you sleep on average?",
    "What is your go-to comfort food?",
    "Do you think money can buy happiness?"
]

NUM_RESPONDENTS = 10

class SurveyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Data Analyst Survey Game")
        self.geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Data storage
        self.responses = {q: [] for q in QUESTIONS}
        self.sentiments = {q: [] for q in QUESTIONS}
        self.current_respondent = 1
        self.current_question_index = 0

        self.create_widgets()
        self.show_question()

    def create_widgets(self):
        self.lbl_respondent = ttk.Label(self, text=f"Respondent: {self.current_respondent} / {NUM_RESPONDENTS}", font=("Arial", 14))
        self.lbl_respondent.pack(pady=10)

        self.lbl_question = ttk.Label(self, text="", font=("Arial", 16), wraplength=550)
        self.lbl_question.pack(pady=15)

        self.answer_var = tk.StringVar()
        self.entry_answer = ttk.Entry(self, textvariable=self.answer_var, font=("Arial", 14), width=50)
        self.entry_answer.pack(pady=5)
        self.entry_answer.focus()

        self.btn_submit = ttk.Button(self, text="Submit Answer", command=self.submit_answer)
        self.btn_submit.pack(pady=10)

        self.lbl_feedback = ttk.Label(self, text="", font=("Arial", 12), foreground="blue")
        self.lbl_feedback.pack(pady=5)

        self.btn_show_results = ttk.Button(self, text="Show Results", command=self.show_results)
        self.btn_show_results.pack(pady=10)
        self.btn_show_results.config(state="disabled")

        self.btn_export_json = ttk.Button(self, text="Export Results as JSON", command=self.export_json)
        self.btn_export_json.pack(pady=5)
        self.btn_export_json.config(state="disabled")

        self.btn_export_csv = ttk.Button(self, text="Export Results as CSV", command=self.export_csv)
        self.btn_export_csv.pack(pady=5)
        self.btn_export_csv.config(state="disabled")

        self.txt_results = scrolledtext.ScrolledText(self, width=70, height=10, state="disabled")
        self.txt_results.pack(pady=10)

    def show_question(self):
        if self.current_respondent > NUM_RESPONDENTS:
            self.finish_survey()
            return

        question = QUESTIONS[self.current_question_index]
        self.lbl_question.config(text=question)
        self.lbl_respondent.config(text=f"Respondent: {self.current_respondent} / {NUM_RESPONDENTS}")
        self.answer_var.set("")
        self.lbl_feedback.config(text="")

    def submit_answer(self):
        answer = self.answer_var.get().strip()
        if not answer:
            messagebox.showwarning("Input Error", "Please enter an answer before submitting.")
            return

        question = QUESTIONS[self.current_question_index]
        self.responses[question].append(answer)

        # Analyze sentiment
        polarity = TextBlob(answer).sentiment.polarity
        self.sentiments[question].append(polarity)

        # Feedback message
        feedback = self.sentiment_feedback(polarity)
        self.lbl_feedback.config(text=feedback)

        # Move to next question/respondent
        self.current_question_index += 1
        if self.current_question_index >= len(QUESTIONS):
            self.current_question_index = 0
            self.current_respondent += 1

        if self.current_respondent > NUM_RESPONDENTS:
            self.finish_survey()
        else:
            # Clear answer after a short delay so user can see feedback
            self.after(1200, self.show_question)

    def sentiment_feedback(self, polarity):
        if polarity > 0.5:
            return "Great answer! 😊 Positive vibe detected."
        elif polarity > 0:
            return "Nice, a somewhat positive answer!"
        elif polarity == 0:
            return "Neutral response noted."
        else:
            return "Hmm, that sounds a bit negative. 🤔"

    def finish_survey(self):
        self.lbl_question.config(text="Survey completed! You can now view or export results.")
        self.entry_answer.config(state="disabled")
        self.btn_submit.config(state="disabled")
        self.btn_show_results.config(state="normal")
        self.btn_export_json.config(state="normal")
        self.btn_export_csv.config(state="normal")
        self.lbl_respondent.config(text="All respondents completed")

    def aggregate_counts(self):
        counts = {q: {} for q in QUESTIONS}
        for question, answers in self.responses.items():
            for answer in answers:
                counts[question][answer] = counts[question].get(answer, 0) + 1
        return counts

    def average_sentiments(self):
        avg_sents = {}
        for question, vals in self.sentiments.items():
            avg_sents[question] = sum(vals) / len(vals) if vals else 0
        return avg_sents

    def extract_keywords(self):
        stop_words = set(stopwords.words('english'))
        keywords_per_question = {}
        for question, answers in self.responses.items():
            if not answers:
                keywords_per_question[question] = []
                continue
            vectorizer = TfidfVectorizer(stop_words=stop_words, max_features=5)
            vectorizer.fit(answers)
            keywords_per_question[question] = vectorizer.get_feature_names_out().tolist()
        return keywords_per_question

    def show_results(self):
        counts = self.aggregate_counts()
        avg_sents = self.average_sentiments()
        keywords = self.extract_keywords()

        self.txt_results.config(state="normal")
        self.txt_results.delete("1.0", tk.END)

        for question in QUESTIONS:
            self.txt_results.insert(tk.END, f"Question: {question}\n")
            self.txt_results.insert(tk.END, f"Average Sentiment Score: {avg_sents[question]:.3f}\n")
            self.txt_results.insert(tk.END, "Top Keywords: " + ", ".join(keywords[question]) + "\n")
            self.txt_results.insert(tk.END, "Response Counts:\n")
            for answer, count in counts[question].items():
                self.txt_results.insert(tk.END, f"  - {answer}: {count}\n")
            self.txt_results.insert(tk.END, "\n")

        self.txt_results.config(state="disabled")

    def export_json(self):
        counts = self.aggregate_counts()
        avg_sents = self.average_sentiments()
        keywords = self.extract_keywords()

        data = {
            "responses": self.responses,
            "counts": counts,
            "average_sentiments": avg_sents,
            "keywords": keywords
        }

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")],
                                                 title="Save Results As JSON")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Export Successful", f"Results saved to:\n{file_path}")

    def export_csv(self):
        counts = self.aggregate_counts()
        avg_sents = self.average_sentiments()
        keywords = self.extract_keywords()

        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")],
                                                 title="Save Results As CSV")
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Question", "Answer", "Count", "Average Sentiment", "Top Keywords"])
                for question in QUESTIONS:
                    avg_sent = avg_sents.get(question, 0)
                    keys = ", ".join(keywords.get(question, []))
                    for answer, count in counts[question].items():
                        writer.writerow([question, answer, count, f"{avg_sent:.3f}", keys])
            messagebox.showinfo("Export Successful", f"Results saved to:\n{file_path}")

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to quit? Unsaved results will be lost."):
            self.destroy()

def main():
    app = SurveyApp()
    app.mainloop()

if __name__ == "__main__":
    main()
