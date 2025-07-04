import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
from physaix_ultimate import *
import json
import os
from PIL import Image
import base64
from transformers import pipeline
import cv2
import pytesseract
import tempfile
from datetime import datetime

# === Self-learning memory ===
MEMORY_FILE = "hamo_memory.json"
BENCH_FILE = "hamo_bench.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory(mem):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(mem, f, indent=4)

def load_bench():
    if os.path.exists(BENCH_FILE):
        with open(BENCH_FILE, 'r') as f:
            return json.load(f)
    return []

def save_bench(posts):
    with open(BENCH_FILE, 'w') as f:
        json.dump(posts, f, indent=4)

memory = load_memory()
bench_posts = load_bench()

# === Load AI Model (simple QA using transformers) ===
try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
except:
    qa_pipeline = None

# === Streamlit UI ===
st.set_page_config(page_title="Hamo el-Naggar", page_icon="🧠", layout="centered")
st.title("🛠️ Hamo el-Naggar")
st.caption("Your local AI physics blacksmith")

menu = st.sidebar.radio("Navigate", ["Ask Hamo", "Circuit Lab", "Learn", "Upload & OCR", "Discussion"])

if menu == "Ask Hamo":
    st.subheader("Ask Hamo")
    st.markdown("Ask anything about physics, math, or circuits.")
    user_q = st.text_input("Question:", placeholder="e.g. Explain Faraday's Law")

    if user_q:
        if user_q in memory:
            st.success("(From memory)")
            st.write(memory[user_q])
        elif qa_pipeline:
            context = "\n".join([f"{k}: {v}" for k, v in memory.items()])
            try:
                result = qa_pipeline(question=user_q, context=context)
                memory[user_q] = result['answer']
                save_memory(memory)
                st.success("AI answer saved to memory")
                st.write(result['answer'])
            except:
                st.warning("Still learning…")
        else:
            try:
                result = sp.sympify(user_q)
                simplified = sp.simplify(result)
                memory[user_q] = str(simplified)
                save_memory(memory)
                st.success("Answer saved to memory")
                st.write(simplified)
            except Exception:
                st.warning("Could not understand that.")

elif menu == "Circuit Lab":
    st.subheader("🔌 Build & Solve Circuits")
    if "circuit" not in st.session_state:
        st.session_state.circuit = Circuit()

    comp_type = st.selectbox("Component Type", ["Resistor", "VoltageSource"])
    name = st.text_input("Name", value="R1")
    val = st.number_input("Value", value=100.0)
    n1 = st.text_input("Node 1", value="n1")
    n2 = st.text_input("Node 2", value="n2")

    if st.button("Add Component"):
        if comp_type == "Resistor":
            st.session_state.circuit.add(Resistor(name, val, n1, n2))
        elif comp_type == "VoltageSource":
            st.session_state.circuit.add(VoltageSource(name, val, n1, n2))
        st.success(f"{comp_type} {name} added.")

    if st.button("Visualize & Solve Circuit"):
        st.pyplot(st.session_state.circuit.visualize())
        result = MeshAnalyzer(st.session_state.circuit).solve()
        st.subheader("Mesh Current Result")
        st.json(result)

    if st.button("Reset Circuit"):
        st.session_state.circuit = Circuit()
        st.warning("Circuit reset.")

elif menu == "Learn":
    st.subheader("📚 Physics Concepts")
    concepts = {
        "Kirchhoff’s Laws": "KCL: Sum of currents in = currents out.\nKVL: Sum of voltages in loop = 0.",
        "Electromagnetic Induction": "Faraday’s Law: EMF is induced by change in magnetic flux.\nLenz’s Law: The direction opposes the change.",
        "Modern Physics": "Covers relativity, quantum mechanics, and subatomic physics.",
        "Ohm’s Law": "V = IR — core rule of circuits."
    }
    chosen = st.selectbox("Pick a topic:", list(concepts.keys()))
    st.info(concepts[chosen])

elif menu == "Upload & OCR":
    st.subheader("📎 Upload Diagram or Text")
    uploaded_file = st.file_uploader("Upload PNG, JPG, JPEG, or PDF", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            image_path = tmp_file.name
        st.image(image_path, caption="Uploaded")
        try:
            img = cv2.imread(image_path)
            text = pytesseract.image_to_string(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
            st.subheader("Detected Text")
            st.code(text)
        except:
            st.warning("OCR Failed. Is Tesseract installed?")

elif menu == "Discussion":
    st.subheader("💬 The Bench")
    with st.expander("Post a Message"):
        user_name = st.text_input("Your Name")
        user_msg = st.text_area("Message")
        if st.button("Post") and user_name and user_msg:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            post = {"name": user_name, "msg": user_msg, "time": timestamp}
            bench_posts.append(post)
            save_bench(bench_posts)
            st.success("Posted!")

    st.subheader("Latest Messages")
    for post in reversed(bench_posts[-10:]):
        st.markdown(f"**{post['name']}** at *{post['time']}* said:")
        st.info(post['msg'])
