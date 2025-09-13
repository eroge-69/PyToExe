import webview
from flask import Flask

# === CONTENUTO HTML INCLUSO ===
html_files = {
    "index.html": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>iO&iA - Home</title>
    </head>
    <body>
        <h1>Benvenuto in iO&iA</h1>
        <button onclick=\"window.location.href='/adabot.html'\">Adabot</button>
        <button onclick=\"window.location.href='/iO&iA.html'\">iO&iA</button>
        <button onclick=\"window.location.href='/neurotrade.html'\">Neurotrade</button>
        <button onclick=\"window.location.href='/superneurotrade.html'\">SuperNeurotrade</button>
    </body>
    </html>
    """,

    "adabot.html": """
    <html><body><h2>Adabot</h2><a href='/'>🏠 Torna alla Home</a></body></html>
    """,

    "iO&iA.html": """
    <html><body><h2>iO&iA</h2><a href='/'>🏠 Torna alla Home</a></body></html>
    """,

    "neurotrade.html": """
    <html><body><h2>Neurotrade</h2><a href='/'>🏠 Torna alla Home</a></body></html>
    """,

    "superneurotrade.html": """
    <html><body><h2>SuperNeurotrade</h2><a href='/'>🏠 Torna alla Home</a></body></html>
    """
}

# === FLASK SERVER ===
app = Flask(__name__)

@app.route("/<path:filename>")
def serve_file(filename):
    if filename in html_files:
        return html_files[filename]
    return "<h1>404 - File non trovato</h1>", 404

@app.route("/")
def serve_index():
    return html_files["index.html"]

# === START APP ===
def start_app():
    import threading
    def run():
        app.run(host="127.0.0.1", port=5000, debug=False)
    threading.Thread(target=run, daemon=True).start()

    webview.create_window("iO&iA", "http://127.0.0.1:5000/")
    webview.start()

if __name__ == "__main__":
    start_app()
