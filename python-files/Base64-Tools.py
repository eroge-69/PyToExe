import webview
import base64
import tkinter as tk
from tkinter import filedialog
import os

try:
    import pyperclip
except ImportError:
    pyperclip = None

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Fancy Base64 Tool</title>
<style>
    body {
        font-family: 'Segoe UI', sans-serif;
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        padding: 40px;
        color: white;
    }
    h1 {
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 30px;
        text-shadow: 0 0 10px #00f0ff;
    }
    textarea {
        width: 100%;
        height: 120px;
        background: #1e1e2e;
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 15px;
        font-size: 1em;
        resize: none;
        margin-bottom: 20px;
        transition: box-shadow 0.3s ease;
    }
    textarea:focus {
        box-shadow: 0 0 10px #00f0ff;
        outline: none;
    }
    .btn {
        background: #00f0ff;
        color: #000;
        border: none;
        padding: 15px 25px;
        font-size: 1em;
        font-weight: bold;
        margin: 5px;
        border-radius: 12px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0, 240, 255, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .btn:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(0, 240, 255, 0.8);
    }
    #log {
        font-size: 1em;
        margin-top: 20px;
        text-align: center;
        color: #7fffd4;
        text-shadow: 0 0 5px #00f0ff;
    }
    .btn-container {
        text-align: center;
        flex-wrap: wrap;
    }
</style>
</head>
<body>
    <h1> Base64 Tools</h1>

    <textarea id="input" placeholder="Enter text or base64 here..."></textarea>
    <textarea id="output" placeholder="Result appears here..." readonly></textarea>

    <div class="btn-container">
        <button class="btn" onclick="encode()">Encode Text</button>
        <button class="btn" onclick="decode()">Decode Text</button>
        <button class="btn" onclick="copy()">Copy Output</button>
        <button class="btn" onclick="paste()">Paste Input</button>
        <button class="btn" onclick="validate()">Validate Base64</button><br>
        <button class="btn" onclick="encodeImage()">📤 Encode Image File</button>
        <button class="btn" onclick="decodeImage()">📥 Decode to Image File</button>
    </div>

    <div id="log"></div>

    <script>
        async function encode() {
            const text = document.getElementById("input").value;
            const result = await window.pywebview.api.encode(text);
            log(result.status === "ok" ? "✅ Encoded!" : "❌ " + result.message);
            if(result.status === "ok") document.getElementById("output").value = result.result;
        }

        async function decode() {
            const text = document.getElementById("input").value;
            const result = await window.pywebview.api.decode(text);
            log(result.status === "ok" ? "✅ Decoded!" : "❌ " + result.message);
            if(result.status === "ok") document.getElementById("output").value = result.result;
        }

        async function validate() {
            const result = await window.pywebview.api.validate(document.getElementById("input").value);
            log(result.status === "ok" ? "✅ Valid Base64!" : "❌ Invalid Base64");
        }

        async function copy() {
            const result = await window.pywebview.api.copy(document.getElementById("output").value);
            log(result.status === "ok" ? "📋 Copied!" : "❌ " + result.message);
        }

        async function paste() {
            const result = await window.pywebview.api.paste();
            if(result.status === "ok") {
                document.getElementById("input").value = result.text;
                log("📥 Pasted!");
            } else log("❌ " + result.message);
        }

        async function encodeImage() {
            const result = await window.pywebview.api.encode_image();
            if(result.status === "ok") {
                document.getElementById("output").value = result.result;
                log("🖼️ Image encoded!");
            } else log("❌ " + result.message);
        }

        async function decodeImage() {
            const result = await window.pywebview.api.decode_image(document.getElementById("input").value);
            log(result.status === "ok" ? "🖼️ Image saved!" : "❌ " + result.message);
        }

        function log(msg) {
            document.getElementById("log").innerText = msg;
        }
    </script>
</body>
</html>
"""

# ==== PYTHON BACKEND ====
class Api:
    def encode(self, text):
        try:
            return {"status": "ok", "result": base64.b64encode(text.encode()).decode()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def decode(self, b64text):
        try:
            return {"status": "ok", "result": base64.b64decode(b64text.encode()).decode()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def validate(self, b64text):
        try:
            base64.b64decode(b64text.encode())
            return {"status": "ok"}
        except:
            return {"status": "error"}

    def copy(self, text):
        try:
            if pyperclip:
                pyperclip.copy(text)
                return {"status": "ok"}
            else:
                return {"status": "error", "message": "pyperclip not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def paste(self):
        try:
            if pyperclip:
                return {"status": "ok", "text": pyperclip.paste()}
            else:
                return {"status": "error", "message": "pyperclip not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def encode_image(self):
        try:
            root = tk.Tk()
            root.withdraw()
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
            root.destroy()
            if not path:
                return {"status": "error", "message": "Cancelled"}
            with open(path, "rb") as f:
                b64data = base64.b64encode(f.read()).decode()
            return {"status": "ok", "result": b64data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def decode_image(self, b64data):
        try:
            root = tk.Tk()
            root.withdraw()
            path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")])
            root.destroy()
            if not path:
                return {"status": "error", "message": "Cancelled"}
            with open(path, "wb") as f:
                f.write(base64.b64decode(b64data.encode()))
            return {"status": "ok"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# === MAIN ===
if __name__ == '__main__':
    api = Api()
    webview.create_window("Base64 Tools", html=HTML, js_api=api, width=1000, height=780, resizable=True)
    webview.start()
