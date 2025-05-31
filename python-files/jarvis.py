from flask import Flask, render_template_string, request, session, redirect, url_for
import difflib
import requests
import random

app = Flask(__name__)
app.secret_key = "jarvis_secret"

# Sadece tek mod: Oto Öğrenen AI
ai_memory = {
    "train": []
}

def fetch_tdk_meaning(word):
    try:
        url = f"https://sozluk.gov.tr/gts?ara={word}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data:
                meanings = data[0].get('anlamlarListe', [])
                if meanings:
                    return meanings[0].get('anlam', None)
        return None
    except Exception:
        return None

def fetch_wikipedia_summary(word):
    try:
        url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{word.replace(' ', '_')}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            summary = data.get('extract')
            if summary:
                return summary
        return None
    except Exception:
        return None

def auto_learn(user_input):
    kelime = user_input.strip().lower()
    # Önce hafızada var mı bak
    questions = [pair['q'] for pair in ai_memory['train']]
    matches = difflib.get_close_matches(kelime, questions, n=1, cutoff=0.7)
    if matches:
        for pair in reversed(ai_memory['train']):
            if pair['q'] == matches[0]:
                return pair['a']
    # TDK'dan anlam bul
    tdk_meaning = fetch_tdk_meaning(kelime)
    if tdk_meaning:
        cevap = f"'{kelime}' kelimesi: {tdk_meaning}"
        ai_memory['train'].append({'q': kelime, 'a': cevap})
        return cevap
    # Wikipedia'dan özet bul
    wiki_summary = fetch_wikipedia_summary(kelime)
    if wiki_summary:
        cevap = f"'{kelime}' hakkında Wikipedia özeti: {wiki_summary}"
        ai_memory['train'].append({'q': kelime, 'a': cevap})
        return cevap
    return "Bunu bilmiyorum. Bana öğretebilirsin!"

@app.route("/", methods=["GET", "POST"])
def index():
    chat = session.get("chat", [])
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        if '|' in user_input:
            # Manuel eğitim
            question, answer = user_input.split('|', 1)
            ai_memory['train'].append({'q': question.strip().lower(), 'a': answer.strip()})
            response = f"Eğitim kaydedildi: '{question.strip()}' => '{answer.strip()}'"
        else:
            response = auto_learn(user_input)
        chat.append(("Sen", user_input))
        chat.append(("Jarvis", response))
        session["chat"] = chat
    return render_template_string("""
    <html><head><title>Jarvis AI - Oto Öğrenen Dev AI</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <style>
    body { background:linear-gradient(120deg,#181818 60%,#ff3333 100%); color:#fff; font-family:'Segoe UI',Arial,sans-serif; }
    .container { max-width:700px; margin:60px auto; background:#232323; border-radius:24px; padding:48px; box-shadow:0 4px 48px #000a; }
    h1 { color:#ff3333; font-size:2.5em; letter-spacing:2px; }
    .chat { background:#111; border-radius:12px; padding:24px; min-height:240px; color:#fff; margin-bottom:28px; font-size:1.15em; }
    .msg-user { color:#ff7b00; font-weight:bold; }
    .msg-ai { color:#fff; font-weight:bold; }
    input,button { padding:14px; border-radius:10px; border:none; font-size:1.1em; margin:10px 0; }
    input { width:70%; }
    button { background:linear-gradient(90deg,#ff3333 60%,#ff7b00 100%); color:#fff; font-weight:bold; cursor:pointer; transition:0.2s; }
    button:hover { background:linear-gradient(90deg,#ff7b00 60%,#ff3333 100%);}
    .reset-btn { background:#444; color:#fff; margin-left:20px; }
    @media (max-width:800px) {
      .container { max-width:98vw; padding:10vw 2vw; }
      input { width:100%; }
    }
    </style>
    </head><body>
    <div class="container">
        <h1>Jarvis AI <span style='font-size:0.6em;color:#fff;'>Oto Öğrenen Dev AI</span></h1>
        <div class="chat">
            {% for who, msg in chat %}
                <div><b class="msg-{{ 'user' if who == 'Sen' else 'ai' }}">{{ who }}:</b> {{ msg }}</div>
            {% endfor %}
        </div>
        <form method="post" style="display:flex;gap:10px;flex-wrap:wrap;">
            <input name="user_input" placeholder="Kelime, soru veya eğitim (soru|cevap)" autofocus autocomplete="off">
            <button type="submit">Gönder</button>
            <button type="submit" formaction="/reset" formmethod="post" class="reset-btn">Sıfırla</button>
        </form>
        <div style="margin-top:30px;color:#ff7b00;font-size:1em;">Oto öğrenme: Bilinmeyen kelime/soru yazınca TDK ve Wikipedia'dan otomatik öğrenir ve hafızasına ekler.</div>
    </div>
    </body></html>
    """, chat=session.get("chat", []))

@app.route("/reset", methods=["POST"])
def reset():
    session["chat"] = []
    ai_memory["train"] = []
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
