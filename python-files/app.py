from flask import Flask, request, render_template_string
import threading
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from urllib.parse import urlparse, parse_qs
from fake_useragent import UserAgent
import os
import sys

app = Flask(__name__)

# Daftar proxy yang diberikan
PROXIES = [
    "184.174.44.114:6540:dmproxy57:dmproxy57",
    "31.58.20.107:5791:dmproxy57:dmproxy57",
    "107.173.93.106:6060:dmproxy57:dmproxy57",
    "192.177.103.41:6534:dmproxy57:dmproxy57",
    "208.70.11.183:6264:dmproxy57:dmproxy57",
    "45.38.111.61:5976:dmproxy57:dmproxy57",
    "92.113.231.229:7314:dmproxy57:dmproxy57",
    "92.113.231.246:7331:dmproxy57:dmproxy57",
    "92.113.231.194:7279:dmproxy57:dmproxy57",
    "92.113.231.154:7239:dmproxy57:dmproxy57",
]

# List untuk menyimpan instance driver
drivers = []

def open_browser(proxy, video_id):
    try:
        ip, port, user, passw = proxy.split(":")
        proxy_url = f"http://{user}:{passw}@{ip}:{port}"
        options = {
            'proxy': {
                'http': proxy_url,
                'https': proxy_url,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
        ua = UserAgent()
        user_agent = ua.chrome  # User agent acak kompatibel dengan Chrome
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            seleniumwire_options=options,
            options=chrome_options
        )
        drivers.append(driver)
        url = f"https://www.youtube.com/watch?v={video_id}&list={video_id}"
        driver.get(url)
    except Exception as e:
        print(f"Error dengan proxy {proxy} dan user agent {user_agent}: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        if 'stop' in request.form:
            for driver in drivers:
                try:
                    driver.quit()
                except:
                    pass
            drivers.clear()
            return render_template_string('''
                <h2>Pemutar Video YouTube dengan Proxy</h2>
                <form method="post">
                    <label for="url">URL YouTube:</label>
                    <input type="text" id="url" name="url">
                    <input type="submit" value="Start">
                </form>
                <form method="post">
                    <input type="submit" name="stop" value="Stop">
                </form>
                <p>Semua browser telah ditutup.</p>
            ''')
        url = request.form['url']
        if not url:
            error = "Masukkan URL YouTube"
        else:
            parsed = urlparse(url)
            if parsed.netloc != "www.youtube.com" or parsed.path != "/watch":
                error = "URL YouTube tidak valid"
            else:
                query = parse_qs(parsed.query)
                video_id = query.get("v", [None])[0]
                if not video_id:
                    error = "Tidak dapat mengekstrak ID video"
                else:
                    for proxy in PROXIES:
                        t = threading.Thread(target=open_browser, args=(proxy, video_id))
                        t.start()
                    return render_template_string('''
                        <h2>Pemutar Video YouTube dengan Proxy</h2>
                        <form method="post">
                            <label for="url">URL YouTube:</label>
                            <input type="text" id="url" name="url">
                            <input type="submit" value="Start">
                        </form>
                        <form method="post">
                            <input type="submit" name="stop" value="Stop">
                        </form>
                        <p>Jendela browser telah dibuka.</p>
                    ''')
    return render_template_string('''
        <h2>Pemutar Video YouTube dengan Proxy</h2>
        <form method="post">
            <label for="url">URL YouTube:</label>
            <input type="text" id="url" name="url">
            <input type="submit" value="Start">
        </form>
        <form method="post">
            <input type="submit" name="stop" value="Stop">
        </form>
        {% if error %}
            <p style="color: red;">{{ error }}</p>
        {% endif %}
    ''', error=error)

if __name__ == '__main__':
    # Jalankan Flask di port 5000
    app.run(host='0.0.0.0', port=5000)