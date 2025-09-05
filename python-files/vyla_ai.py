import streamlit as st
import sqlite3
import plotly.express as px
import requests
import os
import json
import sys
import pypdf

# Constants
SUBJECTS = ["Math", "Science", "English", "Social Science"]
CBSE_SYLLABUS_FILE = "cbse_syllabus.json"  # Pre-load with CBSE data
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Database Setup (Local SQLite)
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect('data/vyla_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, pin TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS progress (user_id INT, subject TEXT, topic TEXT, score REAL)''')
    conn.commit()
    return conn

# OpenRouter API Call
def call_openrouter(messages, model="mistralai/mistral-7b-instruct"):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages
    }
    r = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {r.text}"

# Adaptive Explanation
def get_explanation(question, subject, user_progress):
    difficulty = "easy" if user_progress.get(subject, 0) < 50 else "advanced"
    prompt = f"Explain {question} for CBSE {subject} at {difficulty} level."
    messages = [
        {"role": "system", "content": "You are VYLA, a friendly CBSE tutor for middle school."},
        {"role": "user", "content": prompt}
    ]
    return call_openrouter(messages)

# PDF Ingestion
def ingest_pdf(file):
    reader = pypdf.PdfReader(file)
    text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
    
    # Summarize
    messages = [
        {"role": "system", "content": "You are a summarization assistant."},
        {"role": "user", "content": f"Summarize this text in 200 words:\n\n{text[:3000]}"}  # limit size
    ]
    summary = call_openrouter(messages)
    
    # Flashcards
    flashcards = generate_flashcards(summary)
    
    # Quiz
    quiz = generate_quiz(summary)
    
    return summary, flashcards, quiz

def generate_flashcards(text):
    messages = [
        {"role": "system", "content": "You are a flashcard generator."},
        {"role": "user", "content": f"Create 5 Q&A flashcards from this text:\n\n{text}"}
    ]
    content = call_openrouter(messages)
    flashcards = []
    for line in content.split("\n"):
        if "Q:" in line and "A:" in line:
            parts = line.split("A:")
            flashcards.append({"q": parts[0].replace("Q:", "").strip(), "a": parts[1].strip()})
    return flashcards

def generate_quiz(text):
    messages = [
        {"role": "system", "content": "You are a quiz generator."},
        {"role": "user", "content": f"Generate 5 multiple-choice questions (with 4 options each, mark the correct one) from this text:\n\n{text}"}
    ]
    content = call_openrouter(messages)
    return content.split("\n")

# Load Syllabus (Local JSON)
def load_syllabus_context(subject):
    if os.path.exists(CBSE_SYLLABUS_FILE):
        with open(CBSE_SYLLABUS_FILE, 'r') as f:
            data = json.load(f)
        return data.get(subject, "")
    return "Default CBSE context for " + subject + "."

# Main App
def main():
    conn = init_db()
    st.set_page_config(page_title="VYLA - AI Tutor", layout="wide")

    # User Auth
    if 'user_id' not in st.session_state:
        st.title("Login to VYLA")
        username = st.text_input("Username")
        pin = st.text_input("PIN", type="password")
        if st.button("Login"):
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE username=? AND pin=?", (username, pin))
            user = c.fetchone()
            if user:
                st.session_state.user_id = user[0]
            else:
                c.execute("INSERT INTO users (username, pin) VALUES (?, ?)", (username, pin))
                conn.commit()
                st.session_state.user_id = c.lastrowid
            st.rerun()

    else:
        user_id = st.session_state.user_id
        st.sidebar.title("VYLA Dashboard")
        page = st.sidebar.radio("Sections", ["Chat Tutor", "Notes Ingestion", "Flashcards", "Quizzes", "Analytics"])

        # Fetch Progress
        c = conn.cursor()
        c.execute("SELECT subject, AVG(score) FROM progress WHERE user_id=? GROUP BY subject", (user_id,))
        progress = {row[0]: row[1] for row in c.fetchall()}

        if page == "Chat Tutor":
            st.title("AI Chat Tutor")
            subject = st.selectbox("Subject", SUBJECTS)
            question = st.text_area("Ask a question:")
            if st.button("Explain"):
                explanation = get_explanation(question, subject, progress)
                st.write(explanation)

        elif page == "Notes Ingestion":
            st.title("Upload Notes/PDF")
            uploaded_file = st.file_uploader("Choose PDF", type="pdf")
            if uploaded_file:
                summ, flashcards, quiz = ingest_pdf(uploaded_file)
                st.subheader("Summary")
                st.write(summ)
                st.session_state.flashcards = flashcards
                st.session_state.quiz = quiz

        elif page == "Flashcards":
            st.title("Flashcards")
            if 'flashcards' in st.session_state:
                for card in st.session_state.flashcards:
                    with st.expander(card['q']):
                        st.write(card['a'])

        elif page == "Quizzes":
            st.title("Practice Quizzes")
            if 'quiz' in st.session_state:
                for i, q in enumerate(st.session_state.quiz):
                    st.write(q)
                    answer = st.text_input(f"Answer {i+1}")
                    if st.button(f"Submit {i+1}"):
                        score = 80 if "correct" in answer.lower() else 40  # Placeholder scoring
                        c.execute("INSERT INTO progress (user_id, subject, topic, score) VALUES (?, ?, ?, ?)",
                                  (user_id, "Science", "Quiz", score))  # Adapt subject/topic
                        conn.commit()
                        st.write(f"Score: {score}%")

        elif page == "Analytics":
            st.title("Learning Analytics")
            if progress:
                fig = px.bar(x=list(progress.keys()), y=list(progress.values()), title="Subject Progress")
                st.plotly_chart(fig)

if __name__ == "__main__":
    main()
