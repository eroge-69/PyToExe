import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import time
import subprocess
import platform
import re
import webbrowser
import os
import pyperclip
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from PIL import Image, ImageTk

# Variáveis e configurações globais
THEME_FILE = "azure.tcl"
if os.path.exists(THEME_FILE):
    try:
        root = tk.Tk()
        root.tk.call("source", THEME_FILE)
        root.tk.call("set_theme", "dark")
        root.destroy()
    except tk.TclError:
        print("Aviso: Tema azure.tcl não pôde ser carregado. Usando o tema padrão.")

class PingMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PING INFO MUNDIVOX")
        self.root.geometry("1000x700")
        
        # Cria um ícone simples em formato de imagem a partir do texto
        # Não é possível criar um ícone com formatação (negrito, itálico) diretamente no Tkinter
        try:
            icon_text = "M"
            font_size = 30
            img = Image.new('RGB', (font_size, font_size), color = (0, 0, 255))
            d = ImageDraw.Draw(img)
            d.text((5, 5), icon_text, fill=(255,255,255))
            photo = ImageTk.PhotoImage(img)
            self.root.iconphoto(False, photo)
        except ImportError:
            # Caso o Pillow não esteja instalado
            pass

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.tabs = {}
        self.monitoring_threads = {}
        self.stop_events = {}
        self.graph_windows = {}

        self.create_default_tab()

    def create_default_tab(self):
        self.add_tab("Novo Grupo")

    def add_tab(self, name):
        tab_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_frame, text=name)
        
        tab_id = self.notebook.tabs()[-1]
        self.tabs[tab_id] = {
            "name": name,
            "data": [],
            "frame": tab_frame,
            "data_input": None,
            "tree": None,
            "stop_event": threading.Event(),
            "ping_counts": {},
            "latency_history": {},
            "highlighted_client": None
        }

        self.create_tab_widgets(tab_frame, tab_id)
        self.notebook.select(tab_frame)

    def create_tab_widgets(self, parent_frame, tab_id):
        # Frame de controle
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill="x")

        new_tab_button = ttk.Button(control_frame, text="Novo Grupo", command=lambda: self.add_tab("Novo Grupo"))
        new_tab_button.pack(side="left", padx=(0, 5))
        
        # Botão para o gráfico
        graph_button = ttk.Button(control_frame, text="Gráfico de Latência", command=lambda: self.show_latency_graph(tab_id))
        graph_button.pack(side="left", padx=(5, 5))

        # Frame de entrada de dados
        input_frame = ttk.Frame(parent_frame)
        input_frame.pack(fill="x")
        
        ttk.Label(input_frame, text="Cole as linhas de dados dos clientes aqui:").pack(pady=(0, 5))
        data_input = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=10)
        data_input.pack(fill="x")
        self.tabs[tab_id]["data_input"] = data_input

        start_button = ttk.Button(input_frame, text="Iniciar Monitoramento", command=lambda: self.start_monitoring(tab_id))
        start_button.pack(pady=(10, 0))

        # Frame da tabela de resultados
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(expand=True, fill="both", pady=(10, 0))

        columns = ("ip", "tipo", "codigo", "nome", "protocolo", "status", "latencia", "ping_count")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        tree.pack(expand=True, fill="both")
        self.tabs[tab_id]["tree"] = tree
        
        self.configure_treeview_columns(tree)
        
        tree.bind("<Button-1>", lambda event: self.on_tree_click(event, tree, tab_id))
        self.notebook.bind("<Double-1>", self.rename_tab)
        
    def configure_treeview_columns(self, tree):
        tree.heading("ip", text="IP", anchor=tk.W)
        tree.heading("tipo", text="Tipo", anchor=tk.W)
        tree.heading("codigo", text="Código", anchor=tk.W)
        tree.heading("nome", text="Nome do Cliente", anchor=tk.W)
        tree.heading("protocolo", text="Protocolo", anchor=tk.W)
        tree.heading("status", text="Status", anchor=tk.W)
        tree.heading("latencia", text="Latência", anchor=tk.W)
        tree.heading("ping_count", text="Pings", anchor=tk.W)

        tree.column("ip", width=120, minwidth=100)
        tree.column("tipo", width=60, minwidth=50)
        tree.column("codigo", width=80, minwidth=70)
        tree.column("nome", width=300, minwidth=200)
        tree.column("protocolo", width=150, minwidth=100)
        tree.column("status", width=80, minwidth=70)
        tree.column("latencia", width=80, minwidth=70)
        tree.column("ping_count", width=60, minwidth=50)
        
        # Tags de cores para as linhas
        tree.tag_configure("online", background="#A5D6A7", foreground="black")  # Verde pastel com texto preto
        tree.tag_configure("offline", background="#EF9A9A", foreground="black") # Vermelho pastel com texto preto
        tree.tag_configure("protocolo_link", foreground="#03A9F4") # Azul vibrante

    def rename_tab(self, event):
        tab_index = self.notebook.tk.call(self.notebook, "identify", "tab", event.x, event.y)
        if tab_index:
            tab_id = self.notebook.tabs()[tab_index]
            current_name = self.notebook.tab(tab_id, "text")
            new_name = simpledialog.askstring("Renomear Grupo", "Digite o novo nome para o grupo:", initialvalue=current_name)
            if new_name and new_name.strip() and new_name != current_name:
                self.notebook.tab(tab_id, text=new_name.strip())
                self.tabs[tab_id]["name"] = new_name.strip()

    def parse_data(self, tab_id):
        raw_data = self.tabs[tab_id]["data_input"].get("1.0", tk.END).strip()
        lines = raw_data.split('\n')
        
        current_data = {client["ip"]: client for client in self.tabs[tab_id]["data"]}
        self.tabs[tab_id]["data"] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(' - ')
            
            # Encontra o código do cliente (ex: 11011952)
            match = re.search(r'LAN - (\d+) - |WAN - (\d+) - ', line)
            client_code = match.group(1) or match.group(2) if match else "N/A"
            
            # Ajusta para pegar os outros dados corretamente, ignorando o código
            # partes_ajustadas = [p for p in parts if p != client_code]
            
            if len(parts) >= 6:
                ip = parts[0]
                ip_type = parts[1]
                name = parts[3]
                protocol = parts[-1]
                
                if ip in current_data:
                    client_data = current_data[ip]
                    client_data["name"] = name
                    client_data["protocol"] = protocol
                    client_data["client_code"] = client_code
                else:
                    client_data = {
                        "ip": ip,
                        "type": ip_type,
                        "client_code": client_code,
                        "name": name,
                        "protocol": protocol,
                        "status": "Aguardando...",
                        "latency": ""
                    }
                    self.tabs[tab_id]["ping_counts"][ip] = 0
                    self.tabs[tab_id]["latency_history"][ip] = []
                
                self.tabs[tab_id]["data"].append(client_data)
        
        self.populate_treeview(tab_id)

    def populate_treeview(self, tab_id):
        tree = self.tabs[tab_id]["tree"]
        for i in tree.get_children():
            tree.delete(i)

        for client in self.tabs[tab_id]["data"]:
            item_id = tree.insert("", "end", values=(
                client["ip"],
                client["type"],
                client["client_code"],
                client["name"],
                client["protocol"],
                client["status"],
                client["latency"],
                self.tabs[tab_id]["ping_counts"].get(client["ip"], 0)
            ))
            tree.item(item_id, tags=("protocolo_link",))

    def start_monitoring(self, tab_id):
        self.tabs[tab_id]["stop_event"].clear()
        self.parse_data(tab_id)

        if not self.tabs[tab_id]["data"]:
            return

        if tab_id in self.monitoring_threads and self.monitoring_threads[tab_id].is_alive():
            self.tabs[tab_id]["stop_event"].set()
            self.monitoring_threads[tab_id].join()

        thread = threading.Thread(target=self.run_ping_monitor, args=(tab_id,), daemon=True)
        self.monitoring_threads[tab_id] = thread
        thread.start()

    def run_ping_monitor(self, tab_id):
        param = '-n' if platform.system().lower() == 'windows' else '-c'

        while not self.tabs[tab_id]["stop_event"].is_set():
            for i, client in enumerate(self.tabs[tab_id]["data"]):
                if self.tabs[tab_id]["stop_event"].is_set():
                    break

                ip = client["ip"]
                try:
                    command = ['ping', param, '1', ip]
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               text=True, encoding='utf-8', errors='ignore')
                    stdout, _ = process.communicate(timeout=1)

                    if process.returncode == 0:
                        delay_match = re.search(r'tempo=(\d+)ms|time=(\d+)ms', stdout)
                        if delay_match:
                            delay = int(delay_match.group(1) or delay_match.group(2))
                            client["status"] = "Online"
                            client["latency"] = f"{delay}ms"
                            self.tabs[tab_id]["ping_counts"][ip] += 1
                            self.tabs[tab_id]["latency_history"][ip].append(delay)
                        else:
                            client["status"] = "Online"
                            client["latency"] = "-"
                            self.tabs[tab_id]["latency_history"][ip].append(None)
                    else:
                        client["status"] = "Offline"
                        client["latency"] = "-"
                        self.tabs[tab_id]["latency_history"][ip].append(None)
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                    client["status"] = "Offline"
                    client["latency"] = "-"
                    self.tabs[tab_id]["latency_history"][ip].append(None)

            self.root.after(100, self.update_treeview, tab_id)
            time.sleep(1)

    def update_treeview(self, tab_id):
        tree = self.tabs[tab_id]["tree"]
        for i, item_id in enumerate(tree.get_children()):
            client = self.tabs[tab_id]["data"][i]
            ip = client["ip"]
            
            tree.set(item_id, "status", client["status"])
            tree.set(item_id, "latencia", client["latency"])
            tree.set(item_id, "ping_count", self.tabs[tab_id]["ping_counts"].get(ip, 0))
            
            if client["status"] == "Online":
                tree.item(item_id, tags=("online",))
            else:
                tree.item(item_id, tags=("offline",))
            
            tree.tag_configure("protocolo_link", foreground="#03A9F4")

    def on_tree_click(self, event, tree, tab_id):
        item_id = tree.identify_row(event.y)
        if not item_id:
            return

        column_id = tree.identify_column(event.x)
        values = tree.item(item_id, "values")
        
        if column_id == "#5": # Coluna 'protocolo'
            protocol = values[4]
            self.open_protocol_link(protocol)
        
        ip = values[0]
        self.tabs[tab_id]["highlighted_client"] = ip

    def open_protocol_link(self, protocol):
        if protocol:
            url = f"https://erp.mundivox.com/redirecionars?url=https://oc.mundivox.com/ocorrencias/detalhes/{protocol}/"
            webbrowser.open_new_tab(url)
            print(f"Abrindo link para o protocolo: {protocol}")

    def show_latency_graph(self, tab_id):
        if not self.tabs[tab_id]["data"]:
            messagebox.showinfo("Aviso", "Não há dados de clientes para exibir no gráfico.")
            return
            
        if tab_id in self.graph_windows and self.graph_windows[tab_id].winfo_exists():
            self.graph_windows[tab_id].focus()
            return

        graph_window = tk.Toplevel(self.root)
        graph_window.title(f"Gráfico de Latência - {self.tabs[tab_id]['name']}")
        graph_window.geometry("800x600")
        self.graph_windows[tab_id] = graph_window
        graph_window.protocol("WM_DELETE_WINDOW", lambda: self.on_graph_closing(tab_id))

        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.legend().set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.LEFT, expand=True, fill="both")
        
        canvas_widget.bind("<Button-1>", lambda event: self.on_graph_click(event, tab_id, ax))

        legend_frame = ttk.Frame(graph_window)
        legend_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        
        legend_canvas = tk.Canvas(legend_frame, width=150, bg="#2d2d2d")
        legend_canvas.pack(fill="y", expand=True)

        legend_canvas.bind("<Button-1>", lambda event: self.on_legend_click(event, tab_id, legend_canvas))

        self.update_graph(tab_id, ax, canvas, legend_canvas)

    def on_graph_closing(self, tab_id):
        if tab_id in self.graph_windows:
            self.graph_windows[tab_id].destroy()
            del self.graph_windows[tab_id]

    def on_graph_click(self, event, tab_id, ax):
        try:
            x_data_click = event.x
            y_data_click = event.y
            
            # Ajuste de coordenadas
            trans = ax.transData.inverted()
            x_click_plot, y_click_plot = trans.transform((x_data_click, y_data_click))
            
            min_distance = float('inf')
            closest_line = None
            
            for line in ax.lines:
                x_coords, y_coords = line.get_data()
                
                if not x_coords.size or not y_coords.size:
                    continue
                
                # Encontra o ponto mais próximo no eixo X
                closest_x_index = (abs(x_coords - x_click_plot)).argmin()
                
                # Coordenadas do ponto mais próximo na linha
                line_x = x_coords[closest_x_index]
                line_y = y_coords[closest_x_index]
                
                # Calcula a distância do clique até a linha
                distance = ( (x_click_plot - line_x)**2 + (y_click_plot - line_y)**2 )**0.5
                
                if distance < min_distance:
                    min_distance = distance
                    closest_line = line
            
            if closest_line and min_distance < 10: # Define um limite de distância para o clique
                label = closest_line.get_label()
                if label:
                    client_data = [d for d in self.tabs[tab_id]["data"] if d["client_code"] == label]
                    if client_data:
                        protocol = client_data[0]["protocol"]
                        self.open_protocol_link(protocol)

        except Exception as e:
            print(f"Erro ao processar clique no gráfico: {e}")


    def on_legend_click(self, event, tab_id, legend_canvas):
        y = event.y
        client_codes = []
        for client in self.tabs[tab_id]["data"]:
            client_codes.append(client["client_code"])
        
        item_height = 20
        index = y // item_height
        
        if 0 <= index < len(client_codes):
            client_code = client_codes[index]
            client_data = [d for d in self.tabs[tab_id]["data"] if d["client_code"] == client_code]
            if client_data:
                protocol = client_data[0]["protocol"]
                self.open_protocol_link(protocol)

    def update_graph(self, tab_id, ax, canvas, legend_canvas):
        if tab_id not in self.graph_windows or not self.graph_windows[tab_id].winfo_exists():
            return

        ax.clear()
        ax.set_title("Latência dos Clientes")
        ax.set_xlabel("Tempo (segundos)")
        ax.set_ylabel("Latência (ms)")
        ax.grid(True)

        history = self.tabs[tab_id]["latency_history"]
        highlighted_ip = self.tabs[tab_id]["highlighted_client"]

        all_lats = []
        for ip, lats in history.items():
            valid_lats = [l for l in lats if l is not None]
            all_lats.extend(valid_lats)

        max_lat = max(all_lats) if all_lats else 100
        ax.set_ylim(bottom=0, top=max_lat + (max_lat * 0.1) if max_lat > 0 else 10)
        
        num_clients = len(history)
        max_len = max(len(lats) for lats in history.values()) if num_clients > 0 else 100
        ax.set_xlim(left=0, right=max_len + 5)

        legend_canvas.delete("all")
        y_pos = 10
        colors = plt.cm.get_cmap('hsv', num_clients + 1)
        
        for i, (ip, lats) in enumerate(history.items()):
            client_data = [d for d in self.tabs[tab_id]["data"] if d["ip"] == ip]
            if not client_data:
                continue
            client_code = client_data[0]["client_code"]
            
            line_color = colors(i)
            line_width = 1
            if ip == highlighted_ip:
                line_color = 'blue'
                line_width = 3
                
            ax.plot(lats, label=client_code, linewidth=line_width, color=line_color)
            
            legend_canvas.create_rectangle(10, y_pos, 30, y_pos + 10, fill=plt.matplotlib.colors.to_hex(line_color))
            legend_canvas.create_text(40, y_pos + 5, anchor="w", text=f"• {client_code}", fill="white")
            
            y_pos += 20
            
        canvas.draw()
        
        self.root.after(1000, self.update_graph, tab_id, ax, canvas, legend_canvas)

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Treeview", foreground="black")
    style.configure("Treeview.Heading", foreground="black")

    app = PingMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(app, root))
    root.mainloop()

def on_closing(app, root):
    for tab_id, tab_info in app.tabs.items():
        tab_info["stop_event"].set()
    for tab_id, window in app.graph_windows.items():
        if window.winfo_exists():
            window.destroy()
    root.destroy()

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageTk
        main()
    except ImportError:
        print("Aviso: A biblioteca 'Pillow' (PIL) não está instalada. O ícone não será exibido.")
        root = tk.Tk()
        root.title("PING INFO MUNDIVOX")
        app = PingMonitorApp(root)
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(app, root))
        root.mainloop()