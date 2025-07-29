from flask import Flask, request, jsonify, render_template
from faster_whisper import WhisperModel
import tempfile

app = Flask(__name__)
model = WhisperModel("base", device="cpu", compute_type="int8")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    file = request.files["file"]
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            file.save(tmp.name)
            segments, info = model.transcribe(tmp.name, beam_size=5)
            full_text = "".join([seg.text for seg in segments])
            return jsonify({"text": full_text})
    return jsonify({"error": "No file uploaded"}), 400

if __name__ == "__main__":
    app.run(debug=True)
