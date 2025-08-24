import tkinter as tk
import webview

class WebviewApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Webview Browser")
        self.master.geometry("800x600")  # Dimensioni iniziali della finestra
        
        # Pulsante per chiudere l'applicazione
        self.close_button = tk.Button(self.master, text="Chiudi", command=self.close)
        self.close_button.pack(pady=20)

        # Avvia direttamente il webview al caricamento
        self.open_webview()

    def open_webview(self):
        # Crea una finestra webview e apri la pagina automaticamente
        webview.create_window('gAItano', 'http://localhost:3080/', width=800, height=600)
        # Avvia l'app in modo che si apra automaticamente
        webview.start()

    def close(self):
        # Chiudi l'app
        self.master.quit()

# Eseguire l'app
if __name__ == "__main__":
    root = tk.Tk()
    app = WebviewApp(root)
    root.mainloop()