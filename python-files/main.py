from flask import Flask, request
import requests

app = Flask(__name__)

# ---------- Webhook Setup ----------
WEBHOOK_URL = "https://discord.com/api/webhooks/1416498149031153754/IWRIUpBZDpUdB6oqj3GwoXh2l52l6LaxSVL6202nOD3dnsSKJFJ2fIlsFIGB3CflCk03"  # <-- Hier Webhook einfügen

def send_webhook(page):
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    data = {
        "content": f"Seite aufgerufen: `{page}`\nIP: `{ip}`\nUser-Agent: `{user_agent}`"
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Webhook Error: {e}")

# ---------- Home ----------
@app.route("/")
def home():
    send_webhook("/")
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Aegis Antivirus</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #000; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow-x: hidden; }
    body::before { content: ""; position: fixed; top:0; left:0; width:100%; height:100%; background-image: linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px); background-size: 40px 40px; z-index:-2; }
    body::after { content:""; position: fixed; top:0; left:0; width:100%; height:100%; background-image: radial-gradient(white 1px, transparent 1px); background-size:50px 50px; animation: moveStars 60s linear infinite; z-index:-1; }
    @keyframes moveStars { from {background-position:0 0;} to {background-position:1000px 1000px;} }
    nav { width:100%; padding:20px 50px; display:flex; justify-content:space-between; align-items:center; position:fixed; top:0; left:0; background: rgba(0,0,0,0.6); backdrop-filter: blur(6px); z-index:100; }
    nav .logo { font-size:26px; font-weight:bold; color:#b26cff; text-transform:uppercase; }
    nav ul { list-style:none; display:flex; gap:25px; }
    nav ul li a { text-decoration:none; color:#fff; font-size:16px; transition: color 0.3s; }
    nav ul li a:hover { color:#b26cff; }
    .btn { background:#b26cff; border:none; padding:10px 20px; border-radius:8px; color:white; cursor:pointer; font-weight:bold; transition:background 0.3s; text-decoration:none; }
    .btn:hover { background:#8f4fd4; }
    .hero { height:100vh; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; padding:0 20px; }
    .hero h1 { font-size:52px; font-weight:bold; color:#b26cff; margin-bottom:20px; text-shadow:0 0 20px rgba(178,108,255,0.8); }
    .hero p { font-size:20px; margin-bottom:30px; color:#bbb; }
    .hero .btn { font-size:18px; padding:12px 30px; }
    .dashboard-preview { margin-top:50px; width:80%; max-width:1000px; background:#111; border-radius:15px; box-shadow:0 0 30px rgba(178,108,255,0.3); padding:30px; overflow:hidden; }
    .slider { position:relative; width:100%; height:250px; overflow:hidden; border-radius:10px; }
    .slides { display:flex; width:300%; animation:slide 12s infinite; }
    .slides img { width:100%; object-fit:cover; }
    @keyframes slide { 0% { transform: translateX(0%); } 30% { transform: translateX(0%); } 35% { transform: translateX(-100%); } 65% { transform: translateX(-100%); } 70% { transform: translateX(-200%); } 100% { transform: translateX(-200%); } }
    .stats { display:flex; justify-content:space-around; margin-top:20px; }
    .stat-box { background:#1a1a1a; padding:20px; border-radius:10px; text-align:center; flex:1; margin:0 10px; }
    .stat-box h2 { font-size:28px; color:#b26cff; text-shadow:0 0 10px rgba(178,108,255,0.6); }
    .stat-box p { color:#ccc; margin-top:5px; }
    footer { background:#111; color:#ccc; text-align:center; padding:40px 20px; margin-top:50px; border-top:1px solid #333; }
    footer a { color:#b26cff; text-decoration:none; margin:0 5px; }
    footer .contact-btn { background:#b26cff;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;margin:5px;display:inline-block; }
  </style>
</head>
<body>
  <nav>
    <div class="logo">Aegis</div>
    <ul>
      <li><a href="/download">Download</a></li>
      <li><a href="/features">Features</a></li>
      <li><a href="/pricing">Pricing</a></li>
      <li><a href="/support">Support</a></li>
      <li><a href="/docs">Docs</a></li>
      <li><a href="/changelog">Changelog</a></li>
      <li><a href="/contact">Contact</a></li>
    </ul>
    <a href="/login" class="btn">Login</a>
  </nav>

  <section class="hero">
    <h1>Aegis Antivirus Protection</h1>
    <p>Next-Gen Antivirus & Threat Detection – stay protected in real time.</p>
    <a href="/download" class="btn">Get Started</a>

    <div class="dashboard-preview">
      <div class="slider">
        <div class="slides">
          <img src="https://picsum.photos/1000/250?random=20" alt="Scan report" />
          <img src="https://picsum.photos/1000/250?random=21" alt="Threat detection" />
          <img src="https://picsum.photos/1000/250?random=22" alt="Realtime protection" />
        </div>
      </div>
      <div class="stats">
        <div class="stat-box">
          <h2>2.3M</h2>
          <p>Viruses Scanned</p>
        </div>
        <div class="stat-box">
          <h2>158K</h2>
          <p>Threats Blocked</p>
        </div>
        <div class="stat-box">
          <h2>45K</h2>
          <p>Active Users</p>
        </div>
      </div>
    </div>
  </section>

  <footer>
    <p>Contact us: <a href="mailto:support@aegisantivirus.com">support@aegisantivirus.com</a> | Phone: +1-800-123-4567</p>
    <div>
        <a href="mailto:support@aegisantivirus.com" class="contact-btn">Email Us</a>
        <a href="tel:+18001234567" class="contact-btn">Call Us</a>
        <a href="/support" class="contact-btn">Support Page</a>
    </div>
    <p>Follow us: 
      <a href="#">Twitter</a> | 
      <a href="#">Facebook</a> | 
      <a href="#">LinkedIn</a>
    </p>
    <p>&copy; 2025 Aegis Antivirus. All rights reserved.</p>
  </footer>
</body>
</html>
"""

# ---------- Other Pages ----------
@app.route("/login")
def login():
    send_webhook("/login")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Aegis Login Page</h1>"

@app.route("/download")
def download():
    send_webhook("/download")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Download Aegis Antivirus</h1>"

@app.route("/features")
def features():
    send_webhook("/features")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Aegis Features</h1>"

@app.route("/pricing")
def pricing():
    send_webhook("/pricing")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Aegis Pricing Plans</h1>"

@app.route("/support")
def support():
    send_webhook("/support")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Aegis Support</h1>"

@app.route("/docs")
def docs():
    send_webhook("/docs")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Aegis Documentation</h1>"

@app.route("/changelog")
def changelog():
    send_webhook("/changelog")
    return "<h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Aegis Changelog</h1>"

@app.route("/contact")
def contact():
    send_webhook("/contact")
    return """
    <h1 style='color:#b26cff;text-align:center;margin-top:50px;'>Contact Aegis</h1>
    <p style='color:#ccc;text-align:center;margin-top:20px;'>
        Email: <a href='mailto:support@aegisantivirus.com' style='color:#b26cff;'>support@aegisantivirus.com</a><br>
        Phone: +1-800-123-4567<br>
        Address: 123 Aegis Blvd, Cyber City, Internet
    </p>
    <div style='text-align:center;margin-top:20px;'>
        <a href='mailto:support@aegisantivirus.com' class='contact-btn'>Email Us</a>
        <a href='tel:+18001234567' class='contact-btn'>Call Us</a>
        <a href='/support' class='contact-btn'>Support Page</a>
    </div>
    """

if __name__ == "__main__":
    app.run(debug=True)