import streamlit as st
import subprocess
import re

# --------------------------
# Config
# --------------------------
OLLAMA_MODEL = "llama3"  # adjust to your local model

st.set_page_config(page_title="YouTube Tags Inspector", page_icon="🔍", layout="centered")

# --------------------------
# UI
# --------------------------
st.title("🔍 YouTube Tags Extractor / Inspector with AI (Ollama)")
st.write("Enter a YouTube video link to extract its tags and optionally calculate a relevance score.")

# Input field for YouTube link
video_link = st.text_input("📌 Enter YouTube Video Link", "")

# Checkbox: Calculate tags relevance score
calculate_score = st.checkbox("Calculate tags relevance score")

# --------------------------
# Generate Button
# --------------------------
if st.button("🔑 Inspect Tags"):
    if not video_link.strip():
        st.warning("Please enter a YouTube video link first.")
    else:
        with st.spinner("⏳ Inspecting tags..."):

            # Prepare prompt for Ollama
            prompt = f"""
            Extract the tags from the YouTube video at this link: {video_link}.
            Return them as a comma-separated list.
            """

            if calculate_score:
                prompt += "\nAlso calculate a relevance score (0-100) for each tag relative to the video content and return in the format 'tag: score'."

            prompt += "\nOnly return the tags and scores if requested. No extra commentary."

            try:
                result = subprocess.run(
                    ["ollama", "run", OLLAMA_MODEL],
                    input=prompt.encode("utf-8"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60
                )

                output = result.stdout.decode("utf-8").strip()
                stderr = result.stderr.decode("utf-8").strip()

                if not output and stderr:
                    st.error(f"No response from Ollama. Error:\n```\n{stderr}\n```")
                elif not output:
                    st.error("No response from Ollama. Check if the model is running.")
                else:
                    st.success("✅ Tags extracted successfully!")
                    st.text_area("🔑 Extracted Tags", value=output, height=300)

            except Exception as e:
                st.error(f"Error calling Ollama: {e}")
