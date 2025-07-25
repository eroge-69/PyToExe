# AI Video Editor Core App (Demo Version - 480p)
# Supports: Prompt-to-Video/Image, Script Gen, OpenTTS, YT/IG Downloader, Trimmer

import os
import sys
import gradio as gr
import subprocess
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips

# === Script Generation with GPT (Mock) ===
def generate_script(prompt):
    return f"[Generated Script for: {prompt}]\nScene 1: ...\nScene 2: ...\n(Use GPT-4 or GPT-3.5 API for real output)"

# === Text-to-Speech (Hindi/English via OpenTTS) ===
def tts_generate(text, lang='en'):
    voice = 'en' if lang == 'en' else 'hi'
    url = f"http://localhost:5500/api/tts?text={text}&lang={voice}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open("output_audio.mp3", "wb") as f:
                f.write(response.content)
            return "output_audio.mp3"
        else:
            return "Failed to generate audio"
    except Exception as e:
        return str(e)

# === Basic Video Cutter ===
def trim_video(file, start, end):
    clip = VideoFileClip(file).subclip(start, end)
    output = "trimmed_output.mp4"
    clip.write_videofile(output, fps=24)
    return output

# === Image/Prompt to Video (Mock - placeholder) ===
def generate_video(prompt, image=None):
    # Replace this with an actual AI video generation pipeline like Sora or Runway
    return "sample_output.mp4"

# === Download from YouTube/Instagram ===
def download_video(url):
    cmd = f"yt-dlp -f best -o 'downloaded_video.%(ext)s' {url}"
    os.system(cmd)
    return "downloaded_video.mp4"

# === Gradio Interface ===
with gr.Blocks() as demo:
    gr.Markdown("## AI Video Creator - Demo 480p")

    with gr.Row():
        prompt = gr.Textbox(label="Enter Prompt")
        image = gr.Image(label="Optional Image")
        generate_btn = gr.Button("Generate Video")
        video_output = gr.Video()

    generate_btn.click(fn=generate_video, inputs=[prompt, image], outputs=[video_output])

    with gr.Row():
        script_prompt = gr.Textbox(label="Script Prompt")
        script_output = gr.Textbox(label="Generated Script")
        script_btn = gr.Button("Generate Script")

    script_btn.click(fn=generate_script, inputs=script_prompt, outputs=script_output)

    with gr.Row():
        tts_text = gr.Textbox(label="Text for TTS")
        tts_lang = gr.Radio(["en", "hi"], label="Language", value="en")
        tts_btn = gr.Button("Generate Audio")
        tts_audio = gr.Audio(label="Generated Audio")

    tts_btn.click(fn=tts_generate, inputs=[tts_text, tts_lang], outputs=tts_audio)

    with gr.Row():
        video_file = gr.File(label="Upload Video")
        start = gr.Number(label="Start Time (sec)")
        end = gr.Number(label="End Time (sec)")
        trim_btn = gr.Button("Trim Video")
        trimmed_output = gr.Video()

    trim_btn.click(fn=trim_video, inputs=[video_file, start, end], outputs=[trimmed_output])

    with gr.Row():
        url = gr.Textbox(label="YT or IG Video URL")
        download_btn = gr.Button("Download Video")
        downloaded = gr.Video()

    download_btn.click(fn=download_video, inputs=url, outputs=downloaded)

# Run locally with: python app.py
demo.launch()
