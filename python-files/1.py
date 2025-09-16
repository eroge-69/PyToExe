import docx
import pymorphy2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Инициализация словаря замен
REPLACEMENTS = {
    "стол": ["стул", "кресло", "табурет"],
    "машина": ["автомобиль", "тачка", "транспорт"],
}

morph = pymorphy2.MorphAnalyzer()

def get_word_form(word, replacement):
    parsed_word = morph.parse(word)[0] if morph.parse(word) else None
    parsed_repl = morph.parse(replacement)[0] if morph.parse(replacement) else None
    if not parsed_word or not parsed_repl:
        return replacement
    form = parsed_repl.inflect(parsed_word.tag.grammemes)
    return form.word if form else replacement

def extract_replacements(doc):
    replacements = []
    for para in doc.paragraphs:
        for run in para.runs:
            words = run.text.split()
            for i, w in enumerate(words):
                base = morph.parse(w.lower())[0].normal_form
                if base in REPLACEMENTS:
                    start = max(0, i-2)
                    end = min(len(words), i+3)
                    context = " ".join(words[start:end])
                    if start > 0:
                        context = "..." + context
                    if end < len(words):
                        context += "..."
                    replacements.append((w, [get_word_form(w, opt) for opt in REPLACEMENTS[base]], context, run, i))
