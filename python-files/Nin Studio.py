import tkinter as tk
from tkinter import filedialog, scrolledtext, Menu, messagebox
import webbrowser
import tempfile

APP_VERSION = "1.0.0"

# ---------------- Notescript++ ----------------
class NotepadClone(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Notescript++")
        self.geometry("1000x700")
        self.theme = "light"
        self.current_file = None

        # Menu
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", command=lambda: self.text_area.event_generate("<<Undo>>"))
        editmenu.add_command(label="Redo", command=lambda: self.text_area.event_generate("<<Redo>>"))
        editmenu.add_separator()
        editmenu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        editmenu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        editmenu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Edit", menu=editmenu)

        settingsmenu = Menu(menubar, tearoff=0)
        settingsmenu.add_command(label="Toggle Theme", command=self.toggle_theme)
        menubar.add_cascade(label="Settings", menu=settingsmenu)
        self.config(menu=menubar)

        # Editor met line numbers
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True)
        self.line_numbers = tk.Text(frame, width=4, padx=3, takefocus=0, border=0,
                                    background="lightgray", state="disabled")
        self.line_numbers.pack(side="left", fill="y")
        self.text_area = scrolledtext.ScrolledText(frame, wrap="word", undo=True, font=("Consolas", 12))
        self.text_area.pack(fill="both", expand=True)
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<ButtonRelease-1>", self.update_cursor_position)

        # Status bar
        self.statusbar = tk.Label(self, text="Line 1, Col 1", anchor="w")
        self.statusbar.pack(side="bottom", fill="x")
        self.update_line_numbers()

    def new_file(self):
        self.text_area.delete("1.0", tk.END)
        self.current_file = None
        self.title("Notescript++ - Untitled")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, content)
            self.current_file = file_path
            self.title(f"Notescript++ - {file_path}")

    def save_file(self):
        if not self.current_file:
            self.save_as()
        else:
            with open(self.current_file, "w", encoding="utf-8") as file:
                file.write(self.text_area.get("1.0", tk.END))
            self.title(f"Notescript++ - {self.current_file}")

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("All Files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.text_area.get("1.0", tk.END))
            self.current_file = file_path
            self.title(f"Notescript++ - {file_path}")

    def update_line_numbers(self, event=None):
        lines = self.text_area.get("1.0", "end-1c").split("\n")
        line_numbers = "\n".join(str(i+1) for i in range(len(lines)))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers)
        self.line_numbers.config(state="disabled")
        self.update_cursor_position()

    def update_cursor_position(self, event=None):
        row, col = self.text_area.index(tk.INSERT).split(".")
        self.statusbar.config(text=f"Line {row}, Col {int(col)+1}")

    def toggle_theme(self):
        if self.theme == "light":
            self.theme = "dark"
            self.configure(bg="#2b2b2b")
            self.text_area.config(bg="#2b2b2b", fg="white", insertbackground="white")
            self.line_numbers.config(bg="#444", fg="white")
            self.statusbar.config(bg="#2b2b2b", fg="white")
        else:
            self.theme = "light"
            self.configure(bg="white")
            self.text_area.config(bg="white", fg="black", insertbackground="black")
            self.line_numbers.config(bg="lightgray", fg="black")
            self.statusbar.config(bg="white", fg="black")

# ---------------- Template Window ----------------
class TemplateWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Website Templates")
        self.geometry("900x600")
        tk.Label(self, text="Select a template:", font=("Arial", 14, "bold")).pack(pady=10)

        # ---------------- Alle 8 templates ----------------
        self.templates = {
            "Template 1 - Portfolio": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Portfolio</title>
  <style>
    body { font-family: Arial, sans-serif; margin:0; padding:0; }
    header { background:#222; color:#fff; padding:20px; text-align:center; }
    nav a { color:#fff; margin:0 10px; }
    section { padding:40px; }
    .projects { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:20px; }
    .project { background:#f4f4f4; padding:20px; border-radius:8px; }
  </style>
</head>
<body>
  <header>
    <h1>John Doe</h1>
    <nav><a href="#about">About</a><a href="#projects">Projects</a><a href="#contact">Contact</a></nav>
  </header>
  <section id="about"><h2>About Me</h2><p>Creative web developer with a passion for modern design.</p></section>
  <section id="projects">
    <h2>Projects</h2>
    <div class="projects"><div class="project">Project 1</div><div class="project">Project 2</div><div class="project">Project 3</div></div>
  </section>
  <section id="contact"><h2>Contact</h2><p>Email: john@example.com</p></section>
</body>
</html>""",

            "Template 2 - Business": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Business</title>
  <style>
    body { font-family:sans-serif; margin:0; background:#fafafa; }
    header { background:#004080; color:#fff; padding:20px; text-align:center; }
    section { padding:40px; }
    .services { display:flex; gap:20px; }
    .service { flex:1; background:#fff; padding:20px; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); }
  </style>
</head>
<body>
  <header>
    <h1>BizCorp</h1>
    <p>Professional Solutions for Your Business</p>
  </header>
  <section>
    <h2>Our Services</h2>
    <div class="services">
      <div class="service">Consulting</div>
      <div class="service">Development</div>
      <div class="service">Marketing</div>
    </div>
  </section>
</body>
</html>""",

            "Template 3 - Blog": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog</title>
  <style>
    body { font-family:Georgia, serif; margin:0; padding:0; }
    header { background:#333; color:#fff; padding:20px; text-align:center; }
    .posts { display:grid; grid-template-columns:repeat(auto-fit, minmax(250px,1fr)); gap:20px; padding:20px; }
    .post { background:#f4f4f4; padding:20px; border-radius:6px; }
  </style>
</head>
<body>
  <header>
    <h1>My Blog</h1>
  </header>
  <section class="posts">
    <div class="post"><h2>Post 1</h2><p>Lorem ipsum...</p></div>
    <div class="post"><h2>Post 2</h2><p>Lorem ipsum...</p></div>
    <div class="post"><h2>Post 3</h2><p>Lorem ipsum...</p></div>
  </section>
</body>
</html>""",

            "Template 4 - Landing Page": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Landing Page</title>
  <style>
    body { margin:0; font-family:sans-serif; }
    .hero { height:100vh; background:linear-gradient(#0008,#0008), url('https://via.placeholder.com/1600x900') center/cover; display:flex; flex-direction:column; justify-content:center; align-items:center; color:#fff; text-align:center; }
    .btn { background:#ff6600; padding:15px 30px; border-radius:6px; margin-top:20px; color:#fff; }
  </style>
</head>
<body>
  <section class="hero">
    <h1>Grow Your Business</h1>
    <p>All-in-one platform to reach your goals.</p>
    <a href="#" class="btn">Get Started</a>
  </section>
</body>
</html>""",

            "Template 5 - Shop": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Shop</title>
  <style>
    body { font-family:Arial; margin:0; }
    header { background:#222; color:#fff; padding:20px; text-align:center; }
    .products { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:20px; padding:20px; }
    .product { border:1px solid #ccc; border-radius:8px; padding:20px; text-align:center; }
    .price { color:green; font-weight:bold; }
  </style>
</head>
<body>
  <header><h1>My Shop</h1></header>
  <section class="products">
    <div class="product"><h2>Product 1</h2><p class="price">$19.99</p></div>
    <div class="product"><h2>Product 2</h2><p class="price">$29.99</p></div>
    <div class="product"><h2>Product 3</h2><p class="price">$39.99</p></div>
  </section>
</body>
</html>""",

            "Template 6 - Restaurant": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Restaurant</title>
  <style>
    body { font-family:serif; margin:0; }
    header { background:#8B0000; color:#fff; padding:30px; text-align:center; }
    section { padding:40px; }
    .menu { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:20px; }
    .item { background:#f4f4f4; padding:20px; border-radius:6px; }
  </style>
</head>
<body>
  <header><h1>La Bella Vita</h1><p>Fine Italian Cuisine</p></header>
  <section>
    <h2>Menu</h2>
    <div class="menu">
      <div class="item">Pizza Margherita</div>
      <div class="item">Spaghetti Carbonara</div>
      <div class="item">Tiramisu</div>
    </div>
  </section>
</body>
</html>""",

            "Template 7 - Photography": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Photography</title>
  <style>
    body { margin:0; font-family:sans-serif; background:#000; color:#fff; }
    header { padding:20px; text-align:center; background:#111; }
    .gallery { display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:10px; padding:20px; }
    .gallery img { width:100%; border-radius:6px; }
  </style>
</head>
<body>
  <header><h1>My Photography</h1></header>
  <section class="gallery">
    <img src="https://via.placeholder.com/400x300" alt="">
    <img src="https://via.placeholder.com/400x300" alt="">
    <img src="https://via.placeholder.com/400x300" alt="">
  </section>
</body>
</html>""",

            "Template 8 - Minimalist": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Minimalist</title>
  <style>
    body { font-family:Arial; background:#fff; color:#222; text-align:center; margin:0; padding:40px; }
    h1 { margin-bottom:20px; }
    p { max-width:600px; margin:auto; }
  </style>
</head>
<body>
  <h1>Minimalist Design</h1>
  <p>Keep it simple. Focus on content. Remove the clutter.</p>
</body>
</html>""",

            "Template 9 - Classic Website": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My Website</title>
  <style>
    /* General styles */
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
    body { line-height: 1.6; background-color: #f4f4f4; color: #333; }
    a { text-decoration: none; color: inherit; }
    header { background-color: #4CAF50; color: #fff; padding: 20px 0; text-align: center; }
    header h1 { margin-bottom: 10px; }
    nav a { margin: 0 15px; font-weight: bold; transition: color 0.3s; }
    nav a:hover { color: #ffeb3b; }
    .hero { background: url('https://via.placeholder.com/1200x400') no-repeat center center/cover; height: 400px;
      display: flex; justify-content: center; align-items: center; color: white; text-shadow: 2px 2px 4px #000; }
    .hero h2 { font-size: 3em; }
    section { padding: 60px 20px; max-width: 1000px; margin: auto; }
    .about, .services { background-color: #fff; margin-bottom: 20px; padding: 20px; border-radius: 8px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .services .service { margin-bottom: 15px; }
    footer { background-color: #333; color: #fff; text-align: center; padding: 20px 0; margin-top: 20px; }
    @media (max-width: 768px) { nav a { display: block; margin: 10px 0; } .hero h2 { font-size: 2em; text-align: center; } }
  </style>
</head>
<body>
  <header>
    <h1>Welcome to My Website</h1>
    <nav><a href="#home">Home</a><a href="#about">About</a><a href="#services">Services</a><a href="#contact">Contact</a></nav>
  </header>
  <section class="hero" id="home"><h2>Your Slogan Here</h2></section>
  <section class="about" id="about"><h2>About Us</h2><p>Lorem ipsum dolor sit amet...</p></section>
  <section class="services" id="services">
    <h2>Our Services</h2>
    <div class="service"><h3>Service 1</h3><p>Description of service 1.</p></div>
    <div class="service"><h3>Service 2</h3><p>Description of service 2.</p></div>
    <div class="service"><h3>Service 3</h3><p>Description of service 3.</p></div>
  </section>
  <section class="contact" id="contact"><h2>Contact</h2><p>Email: info@example.com</p><p>Phone: 012-3456789</p></section>
  <footer>&copy; 2025 My Website. All rights reserved.</footer>
</body>
</html>""",

            "Template 10 - Modern Website": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Modern Website</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; font-family: "Segoe UI", Arial, sans-serif; }
    body { background: #121212; color: #e0e0e0; line-height: 1.6; }
    a { text-decoration: none; color: inherit; }
    header { background: #1f1f1f; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; }
    header h1 { color: #4CAF50; font-size: 1.5em; }
    nav a { margin-left: 20px; font-weight: bold; transition: color 0.3s; }
    nav a:hover { color: #4CAF50; }
    .hero { height: 100vh; background: linear-gradient(to right, rgba(0,0,0,0.7), rgba(0,0,0,0.5)), url('https://via.placeholder.com/1600x900') center/cover no-repeat;
      display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; color: white; padding: 0 20px; }
    .hero h2 { font-size: 3em; margin-bottom: 20px; }
    .hero p { font-size: 1.2em; margin-bottom: 30px; }
    .hero .btn { background: #4CAF50; padding: 15px 30px; border-radius: 8px; font-size: 1em; color: white; transition: background 0.3s; }
    .hero .btn:hover { background: #45a049; }
    section { padding: 60px 20px; max-width: 1100px; margin: auto; }
    .services h2 { text-align: center; margin-bottom: 40px; font-size: 2em; color: #4CAF50; }
    .service-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
    .service { background: #1f1f1f; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5); transition: transform 0.3s; }
    .service:hover { transform: translateY(-5px); }
    .contact h2 { text-align: center; margin-bottom: 20px; color: #4CAF50; }
    .contact p { text-align: center; margin-bottom: 10px; }
    footer { background: #1f1f1f; text-align: center; padding: 20px; margin-top: 40px; color: #aaa; }
  </style>
</head>
<body>
  <header><h1>ModernSite</h1><nav><a href="#home">Home</a><a href="#services">Services</a><a href="#contact">Contact</a></nav></header>
  <section class="hero" id="home"><h2>Build Something Great</h2><p>We help you create modern websites with style and performance.</p><a href="#services" class="btn">Explore Services</a></section>
  <section class="services" id="services">
    <h2>Our Services</h2>
    <div class="service-grid">
      <div class="service"><h3>Web Design</h3><p>Clean and modern website designs tailored to your needs.</p></div>
      <div class="service"><h3>Development</h3><p>Fast and reliable websites built with the latest technologies.</p></div>
      <div class="service"><h3>SEO</h3><p>Optimize your site to rank higher and reach more customers.</p></div>
    </div>
  </section>
  <section class="contact" id="contact"><h2>Contact Us</h2><p>Email: hello@modernsite.com</p><p>Phone: +1 234 567 890</p></section>
  <footer>&copy; 2025 ModernSite. All rights reserved.</footer>
</body>
</html>""",

 "Template 9 - Wikipedia-style": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Wikipedia Template</title>
  <style>
    body {
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      line-height: 1.6;
      background: #f8f9fa;
      color: #202122;
      margin: 0;
      padding: 0;
    }
    header {
      background: #f8f9fa;
      border-bottom: 1px solid #aaa;
      padding: 20px;
      text-align: center;
    }
    header h1 { font-size: 2em; margin-bottom: 5px; }
    header p { font-size: 0.9em; color: #555; }
    nav.toc {
      background: #f1f1f1;
      padding: 15px;
      margin: 20px;
      border: 1px solid #ccc;
      border-radius: 4px;
    }
    nav.toc h2 { margin-top: 0; font-size: 1.2em; }
    nav.toc ul { list-style-type: none; padding-left: 0; }
    nav.toc li { margin: 5px 0; }
    nav.toc a { text-decoration: none; color: #0645ad; }
    nav.toc a:hover { text-decoration: underline; }
    section {
      max-width: 900px;
      margin: 20px auto;
      padding: 0 20px;
      background: #fff;
      border-radius: 4px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    section h2 { border-bottom: 1px solid #aaa; padding-bottom: 5px; margin-top: 30px; }
    section h3 { margin-top: 20px; font-size: 1.2em; }
    p { margin: 10px 0; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; }
    table, th, td { border: 1px solid #aaa; }
    th, td { padding: 8px; text-align: left; }
    img { max-width: 100%; height: auto; display: block; margin: 10px 0; }
    footer {
      text-align: center;
      padding: 20px;
      font-size: 0.9em;
      color: #555;
      border-top: 1px solid #aaa;
      margin-top: 40px;
    }
    @media (max-width: 768px) {
      section { margin: 10px; padding: 10px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Example Article</h1>
    <p>From Wikipedia, the free encyclopedia</p>
  </header>
  <nav class="toc">
    <h2>Contents</h2>
    <ul>
      <li><a href="#introduction">1. Introduction</a></li>
      <li><a href="#history">2. History</a></li>
      <li><a href="#features">3. Features</a></li>
      <li><a href="#references">4. References</a></li>
    </ul>
  </nav>
  <section id="introduction">
    <h2>Introduction</h2>
    <p>This is a high-quality Wikipedia-style template. It is clean, readable, and includes a table of contents, sections, and references.</p>
    <img src="https://via.placeholder.com/600x300" alt="Example Image">
  </section>
  <section id="history">
    <h2>History</h2>
    <p>The history section typically provides background and context. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
    <p>Additional details can be structured in paragraphs or lists.</p>
  </section>
  <section id="features">
    <h2>Features</h2>
    <h3>Tables</h3>
    <table>
      <tr><th>Feature</th><th>Description</th></tr>
      <tr><td>Responsive Design</td><td>Looks good on both desktop and mobile devices.</td></tr>
      <tr><td>Table of Contents</td><td>Easy navigation to different sections.</td></tr>
    </table>
    <h3>Lists</h3>
    <ul>
      <li>Clean typography</li>
      <li>Images with captions</li>
      <li>Semantic HTML structure</li>
    </ul>
  </section>
  <section id="references">
    <h2>References</h2>
    <ol>
      <li><a href="#">Reference 1</a></li>
      <li><a href="#">Reference 2</a></li>
    </ol>
  </section>
  <footer>© 2025 Wikipedia-style Template Example</footer>
</body>
</html>"""
        }

        # Listbox voor templates
        self.listbox = tk.Listbox(self, width=40, font=("Arial", 12))
        for t in self.templates.keys():
            self.listbox.insert(tk.END, t)
        self.listbox.pack(side="left", fill="y", padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_html)

        # Code area
        self.code_area = scrolledtext.ScrolledText(self, width=80, height=30, font=("Consolas", 12))
        self.code_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def show_html(self, event):
        sel = self.listbox.curselection()
        if sel:
            name = self.listbox.get(sel[0])
            code = self.templates[name]
            self.code_area.delete("1.0", tk.END)
            self.code_area.insert(tk.END, code)



# ---------------- Website Preview ----------------
class WebsitePreview(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Website Preview")
        self.geometry("800x600")

        tk.Label(self, text="Paste or load your code:", font=("Arial", 14, "bold")).pack(pady=5)

        # Editor
        self.text_area = scrolledtext.ScrolledText(self, wrap="word", font=("Consolas", 12))
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Preview", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                  command=self.preview_website).pack(side="left", padx=5)

        tk.Button(button_frame, text="Load File", bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                  command=self.load_file).pack(side="left", padx=5)

    def preview_website(self):
        html_code = self.text_area.get("1.0", tk.END)
        try:
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            tmp_file.write(html_code.encode("utf-8"))
            tmp_file.close()
            webbrowser.open(f"file://{tmp_file.name}")
        except Exception as e:
            messagebox.showerror("Error", f"HTML code error:\n{str(e)}")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Text and Code Files", "*.txt;*.html;*.htm;*.css;*.js;*.py;*.json;*.xml;*.php"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

# ---------------- Home Page ----------------
class HomePage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Nin Studio - v{APP_VERSION}")
        self.geometry("600x500")
        self.configure(bg="#f0f0f0")

        # Frame voor titel en subtitel
        title_frame = tk.Frame(self, bg="#f0f0f0")
        title_frame.pack(pady=20)

        # Hoofd titel
        tk.Label(title_frame, text=f"Nin Studio - v{APP_VERSION}", font=("Arial", 28, "bold"), bg="#f0f0f0").pack()
        # Subtitel
        tk.Label(title_frame, text="Helps with making websites", font=("Arial", 16), bg="#f0f0f0").pack()

        # Frame voor knoppen
        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=20)

        button_style = {
            "width":30, "height":2, "font":("Arial",14,"bold"),
            "bd":0, "relief":"raised", "bg":"#2196F3", "fg":"white", "activebackground":"#1976D2"
        }

        # Knoppen, Notescript++ eerst, dan Templates
        tk.Button(button_frame, text="Notescript++", command=self.open_notescript, **button_style).pack(pady=10)
        tk.Button(button_frame, text="Templates", command=self.open_templates, **button_style).pack(pady=10)
        tk.Button(button_frame, text="Website Preview", command=self.open_website_preview, **button_style).pack(pady=10)

    def open_templates(self): TemplateWindow()
    def open_notescript(self): NotepadClone()
    def open_website_preview(self): WebsitePreview()

# ---------------- Splash Screen ----------------
class SplashScreen(tk.Tk):
    def __init__(self, delay=2):
        super().__init__()
        self.delay = delay
        self.overrideredirect(True)
        self.geometry("500x300+500+200")
        self.configure(bg="#2196F3")
        tk.Label(self, text="Nin Studio", font=("Arial", 36, "bold"), fg="white", bg="#2196F3").pack(expand=True)
        self.loading_label = tk.Label(self, text="Loading", font=("Arial", 16), fg="white", bg="#2196F3")
        self.loading_label.pack(pady=20)
        self.dot_count = 0
        self.animate()
        self.after(int(self.delay*1000), self.close_splash)

    def animate(self):
        dots = "." * (self.dot_count % 4)
        self.loading_label.config(text=f"Loading{dots}")
        self.dot_count += 1
        self.after(500, self.animate)

    def close_splash(self):
        self.destroy()
        HomePage().mainloop()

if __name__ == "__main__":
    SplashScreen(delay=3).mainloop()
