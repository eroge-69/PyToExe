from flask import Flask, request, render_template_string
from playwright.sync_api import sync_playwright
from urllib.parse import urlencode
from datetime import datetime
import webbrowser
import threading

app = Flask(__name__)

def playwright_request(auth_token, url, method="GET", post_data=None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            extra_http_headers={
                "authorization": f"Bearer {auth_token}",
                "referer": "https://rec.net/",
            }
        )
        page = context.new_page()

        if method == "POST":
            form_data = urlencode({k: str(v) for k, v in post_data.items()})
            response = page.request.post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=form_data
            )
        else:
            response = page.goto(url)

        if response.ok:
            try:
                return response.json()
            except Exception:
                return {}
        else:
            context.close()
            browser.close()
            raise Exception(f"Request failed: {response.status}")

        context.close()
        browser.close()

def fetch_player_data(auth_token, username):
    url = f"https://accounts.rec.net/account?username={username}"
    user_info = playwright_request(auth_token, url)

    account_id = user_info.get("accountId")
    displayname = user_info.get("displayName")

    if not account_id:
        return "AccountID not found..."

    player_data = playwright_request(auth_token, "https://match.rec.net/player", method="POST", post_data={"id": account_id})

    result_text = ""

    for player in player_data:
        if player.get("isOnline"):
            room_instance = player.get("roomInstance")
            result_text += f"Account ID: {account_id}\nDisplayname: {displayname}\nUsername: {username}\n"

            if room_instance:
                result_text += f"Room Name: {room_instance.get('name')}\n"
                result_text += f"Max Capacity: {room_instance.get('maxCapacity')}\n"
                result_text += f"Is Full: {'True' if room_instance.get('isFull') else 'False'}\n"
                result_text += f"Is Private: {'True' if room_instance.get('isPrivate') else 'False'}\n"
                result_text += f"Is Event: {'True' if room_instance.get('roomInstanceType') == 3 else 'False'}\n"
            else:
                result_text += "Status: In the loading screen\n"
        else:
            last_online = player.get("lastOnline")
            if last_online:
                last_online_date = datetime.fromisoformat(last_online.replace("Z", "+00:00")).date()
                last_online_str = last_online_date.strftime("%d-%m-%Y")
                result_text += (
                    f"Account ID: {account_id}\nDisplayname: {displayname}\nUsername: {username}\n"
                    f"Player is offline.\nLast online: {last_online_str}\n"
                )

    return result_text

@app.route("/", methods=["GET"])
def index():
    return render_template_string(html_template)

@app.route("/track", methods=["POST"])
def track():
    auth_token = request.form.get("auth_token", "").strip()
    username = request.form.get("username", "").strip()

    if not auth_token or not username:
        return "Missing auth token or username", 400

    try:
        result = fetch_player_data(auth_token, username)
        return result
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Player Tracker</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg-solid: #1d1d1d;
      --card-bg: #303030;
      --outline-color: #616161;
      --label-color: #f16e46;
      --highlight-label: #fffff2;
      --text-color: #f2ffff;
    }

    body {
      font-family: 'Futura', 'Trebuchet MS', 'Segoe UI', sans-serif;
      font-weight: bold;
      background: var(--bg-solid);
      color: var(--text-color);
      margin: 0;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: flex-start;
      padding: 3rem 1rem;
    }

    .container {
      background: var(--card-bg);
      border-radius: 8px;
      width: 480px;
      padding: 3rem;
      border: 2px solid var(--outline-color);
      box-shadow: none;
    }

    h2 {
      font-weight: 600;
      font-size: 2rem;
      margin-bottom: 1rem;
      text-align: center;
      color: var(--label-color);
    }

    h4 {
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 2rem;
      text-align: center;
    }

    label {
      display: block;
      font-weight: 600;
      margin-bottom: 0.5rem;
      font-size: 1rem;
      color: var(--label-color);
    }

    /* Override specific labels to be white-ish */
    label[for="auth_token"],
    label[for="username"] {
      color: var(--highlight-label);
    }

    input[type="text"] {
      width: 100%;
      padding: 14px 20px;
      font-size: 1.1rem;
      border-radius: 8px;
      border: 2px solid var(--outline-color);
      background: var(--card-bg);
      color: var(--highlight-label);
      margin-bottom: 1.8rem;
      box-sizing: border-box;
    }

    input[type="text"]:focus {
      outline: none;
      border-color: var(--label-color);
    }

    button {
      margin-top: 1.8rem;
      width: 100%;
      padding: 16px 0;
      border-radius: 8px;
      border: 2px solid var(--label-color);
      background: var(--label-color);
      font-weight: 700;
      font-size: 1.2rem;
      color: #1d1d1d; /* Make button text white-ish */
      cursor: pointer;
      transition: background 0.3s ease, color 0.3s ease, transform 0.3s ease;
      letter-spacing: 0.05em;
    }

    button:hover:enabled {
      transform: scale(1.03);
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }

    pre#resultBox {
      margin-top: 2.5rem;
      background: var(--card-bg);
      border-radius: 8px;
      padding: 1.25rem 1.5rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: 1rem;
      font-weight: 400;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 260px;
      overflow-y: auto;
      color: var(--text-color);
      border: 2px solid var(--outline-color);
      box-sizing: border-box;
    }

    pre#resultBox::-webkit-scrollbar {
      width: 8px;
    }

    pre#resultBox::-webkit-scrollbar-thumb {
      background: var(--outline-color);
      border-radius: 8px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Rec Room Player Tracker</h2>
    <h4>Made by women0814</h4>
    <form id="trackerForm">
      <label for="auth_token">Auth Token</label>
      <input type="text" id="auth_token" name="auth_token" autocomplete="off" required />

      <label for="username">Username</label>
      <input type="text" id="username" name="username" autocomplete="off" required />

      <button type="submit">Search</button>
    </form>
    <pre id="resultBox">Waiting for input...</pre>
  </div>

  <script>
    const form = document.getElementById('trackerForm');
    const resultBox = document.getElementById('resultBox');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      resultBox.textContent = "Searching...";
      submitBtn.disabled = true;

      const formData = new FormData(form);
      try {
        const response = await fetch('/track', {
          method: 'POST',
          body: formData
        });
        const text = await response.text();
        resultBox.textContent = text;
      } catch {
        resultBox.textContent = "Error: Could not fetch player data.";
      } finally {
        submitBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""

# ------------------ Run the App ------------------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")
    webbrowser.open_new("https://rec.net/api/auth/session")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=False, use_reloader=False)

# Make sure to clean up Playwright on app exit
import atexit
@atexit.register
def cleanup_playwright():
    browser.close()
    playwright_instance.stop()
