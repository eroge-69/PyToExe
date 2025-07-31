import psutil
import tkinter as tk
import sys
import urllib.parse
import webbrowser

def open_url(base_url, args):
    def quote(arg):
        if ' ' in arg:
            arg = f'"{arg}"'
        return urllib.parse.quote_plus(arg)

    qstring = '+'.join(quote(arg) for arg in args)
    url = urllib.parse.urljoin(base_url, '?q=' + qstring)
    webbrowser.open(url)

def close_web_pages():
    label.config(text="Chiudo i browser...")
    browser_names = ['chrome', 'firefox', 'edge']
    finestra.destroy()
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'] and any(browser in process.info['name'].lower() for browser in browser_names):
                process.terminate()
                print(f"Closed: {process.info['name']}")
        except Exception as e:
            print(f"Error closing process: {e}")

# Creazione della finestra principale
finestra = tk.Tk()
finestra.title("Strumenti Online")
finestra.geometry("280x350")  # Adattamento dimensioni per due colonne
finestra.configure(bg="#2E2E2E")  # Sfondo scuro

# Creazione di un'etichetta
label = tk.Label(finestra, text="", font=("Helvetica", 10), bg="#2E2E2E", fg="white")
label.pack(pady=5)

# Creazione di un frame per contenere i pulsanti
frame = tk.Frame(finestra, bg="#2E2E2E")
frame.pack(pady=1)

# Definizione dei pulsanti con colori migliorati https://sts.leonardocompany.com/idp/S9LYExXumw/resumeSAML20/idp/SSO.ping
pulsanti_info = [
    ("Google Search", "#1E90FF", 'https://www.google.com/search'),
    ("Outlook", "#FF07FF", 'https://outlook.live.com/mail/0/'),
    ("LinkedIn", "#0077B5", 'https://www.linkedin.com/feed/'),
    ("Miro", "#00BFFF", 'https://www.coursera.org/'),
    ("Claude", "#9370DB", 'https://www.coursera.org/'),
    ("Infinity PMI", "#32CD32", 'https://infinity.pmi.org/chat'),
    ("Gemini", "#FF4500", 'https://gemini.google.com/app/2180eb0bfa7bc5a7?hl=it'),
    ("ChatGPT", "#00FA9A", 'https://chatgpt.com/gpts?utm_source=vimeo_912299249'),
    ("Copilot", "#4682B4", 'https://copilot.microsoft.com/chats/AqAGaHm7ddSrAJbiwZu7H'),
    ("NotebookLM", "#2FBFFA", 'https://notebooklm.google.com/'),
       
    ("Audio-converter", "#9370DB", 'https://online-audio-converter.com/it/'),
    
    ("Coursera", "#FF69B4", 'https://www.coursera.org/learn/program-management-execution-stakeholders-governance/lecture/JX7AT/stakeholder-identification-and-analysis'),

   
    
    ("HRNEXT", "#FF2BE2", 'https://gpnx-leonardo.datamanagement.it/cas/login'),
    
    ("Concur", "#FFB2AA", 'https://eu2.concursolutions.com/approvalsportal.asp'),
    
    ("Folder DAWN", "#0F02AA", 'https://sts.leonardocompany.com/idp/S9LYExXumw/resumeSAML20/idp/SSO.ping'),
    
    ("Timesheet", "#FF8B22", 'https://saphrportal.leonardo.com/irj/portal'),
   
   
    ("Chiudi Pagine", "#FF143C", None)
]

# Creazione dei pulsanti disposti in due colonne https://online-audio-converter.com/it/
for i, (nome, colore, url) in enumerate(pulsanti_info):
    comando = (lambda u=url: open_url(u, sys.argv[1:])) if url else close_web_pages
    pulsante = tk.Button(frame, text=nome, command=comando, bg=colore, fg="white", font=("Helvetica", 10, "bold"))
    pulsante.grid(row=i // 2, column=i % 2, padx=5, pady=3, sticky="ew")

# Avvio del loop principale
finestra.mainloop()