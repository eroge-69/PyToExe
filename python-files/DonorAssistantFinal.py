# DonorAssistantFinal.py
# Versión lista para .exe - Solo comentarios de donadores
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import threading, queue, csv, os
from datetime import datetime
try:
    import winsound
    def ding():
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
except Exception:
    def ding():
        pass
from tiktoklive import TikTokLiveClient
from tiktoklive.events import GiftEvent, ConnectEvent, DisconnectEvent, LiveEndEvent

class DonorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Donor Assistant TikTok")
        self.root.geometry("720x540")
        self.root.attributes("-topmost", True)
        self.q = queue.Queue()
        self.running = False
        self.client = None
        self.csv_path = os.path.join(os.path.dirname(__file__), "donadores_historial.csv")

        # UI
        ttk.Label(root, text="Último donador destacado", font=("Segoe UI", 16, "bold")).pack(pady=8)
        self.big_msg = tk.StringVar(value="Aquí aparecerán los comentarios de los donadores")
        self.lbl_big_msg = ttk.Label(root, textvariable=self.big_msg, font=("Segoe UI", 14), wraplength=680, justify="left")
        self.lbl_big_msg.pack(pady=8)

        btns = ttk.Frame(root)
        btns.pack(pady=8)
        ttk.Button(btns, text="Guardar historial CSV", command=self.save_csv).pack(side="left", padx=6)
        ttk.Button(btns, text="Salir", command=self.on_close).pack(side="right", padx=6)

        self.donors_tree = ttk.Treeview(root, columns=("usuario","mensaje","regalo","cantidad","hora"), show="headings")
        for c,h,w in [("usuario","Usuario",140),("mensaje","Mensaje",300),("regalo","Regalo",100),("cantidad","Cantidad",80),("hora","Hora",80)]:
            self.donors_tree.heading(c,text=h)
            self.donors_tree.column(c,width=w)
        self.donors_tree.pack(fill="both", expand=True, padx=4, pady=4)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(100, self.process_queue)

        # Pedir usuario TikTok
        self.username = simpledialog.askstring("Usuario TikTok", "Ingresa tu usuario (sin @)")
        if self.username:
            self.start_client(self.username)
        else:
            messagebox.showinfo("Info", "Se requiere usuario para iniciar.")
            self.root.destroy()

    def start_client(self, username):
        self.client = TikTokLiveClient(unique_id=username)
        @self.client.on(ConnectEvent)
        async def on_connect(event): self.q.put(("status","Conectado"))
        @self.client.on(DisconnectEvent)
        async def on_disconnect(event): self.q.put(("status","Desconectado"))
        @self.client.on(LiveEndEvent)
        async def on_live_end(event): self.q.put(("status","El live terminó"))
        @self.client.on(GiftEvent)
        async def on_gift(event):
            if event.gift and (event.gift.repeat_end or not event.gift.streakable):
                user = event.user.nickname or event.user.unique_id
                gift_name = event.gift.name or "Regalo"
                repeat_count = event.gift.repeat_count or 1
                ts = datetime.now().strftime("%H:%M:%S")
                self.q.put(("gift",(user,event.comment or "",gift_name,repeat_count,ts)))
        self.running = True
        threading.Thread(target=self.client.run, daemon=True).start()

    def process_queue(self):
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind=="status":
                    self.root.title(f"Donor Assistant TikTok - {data}")
                elif kind=="gift":
                    user,msg,gift,cantidad,ts = data
                    self.donors_tree.insert("", "end", values=(user,msg,gift,cantidad,ts))
                    self.big_msg.set(f"{user} envió {cantidad} × {gift}\nMensaje: {msg}")
                    ding()
        except queue.Empty: pass
        self.root.after(100, self.process_queue)

    def save_csv(self):
        rows = [self.donors_tree.item(child)["values"] for child in self.donors_tree.get_children()]
        if not rows:
            messagebox.showinfo("CSV","No hay donadores para guardar.")
            return
        write_header = not os.path.exists(self.csv_path)
        with open(self.csv_path,"a",newline="",encoding="utf-8") as f:
            writer=csv.writer(f)
            if write_header: writer.writerow(["usuario","mensaje","regalo","cantidad","hora"])
            writer.writerows(rows)
        messagebox.showinfo("CSV",f"Guardado en: {self.csv_path}")

    def on_close(self):
        try: self.client.stop()
        except: pass
        self.root.destroy()

if __name__=="__main__":
    root=tk.Tk()
    app=DonorApp(root)
    root.mainloop()
