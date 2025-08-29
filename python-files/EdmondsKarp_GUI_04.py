import tkinter as tk
from tkinter import StringVar, OptionMenu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from collections import deque
import networkx as nx

# --- Edmonds-Karp Algorithm ---
def edmonds_karp(G, source, sink):
    flow = {(u,v):0 for u,v in G.edges()}
    steps = []

    def bfs():
        parent = {n: None for n in G.nodes()}
        queue = deque([source])
        while queue:
            u = queue.popleft()
            for v in G.successors(u):
                residual = G[u][v]['capacity'] - flow[(u,v)]
                if residual > 0 and parent[v] is None and v != source:
                    parent[v] = u
                    if v == sink:
                        path = []
                        bottleneck = float('inf')
                        cur = sink
                        while cur != source:
                            prev = parent[cur]
                            path.append((prev, cur))
                            bottleneck = min(bottleneck, G[prev][cur]['capacity']-flow[(prev,cur)])
                            cur = prev
                        path.reverse()
                        return path, bottleneck
                    queue.append(v)
        return None, 0

    max_flow = 0
    while True:
        path, bottleneck = bfs()
        if not path:
            break
        for u,v in path:
            flow[(u,v)] += bottleneck
        max_flow += bottleneck
        steps.append((flow.copy(), path.copy(), bottleneck))
    return max_flow, steps

# --- Bezier Drawing ---
def draw_bezier(ax, start, end, rad, color='black', width=2, arrow=True, node_radius=0.06):
    x0, y0 = start
    x1, y1 = end
    dx, dy = x1-x0, y1-y0
    dist = (dx**2 + dy**2)**0.5
    factor_start = node_radius / dist
    factor_end = 1 - node_radius / dist
    xs, ys = x0 + dx*factor_start, y0 + dy*factor_start
    xe, ye = x0 + dx*factor_end, y0 + dy*factor_end

    cx, cy = (xs+xe)/2 - rad*(ye-ys), (ys+ye)/2 + rad*(xe-xs)
    path = Path([(xs,ys),(cx,cy),(xe,ye)], [Path.MOVETO, Path.CURVE3, Path.CURVE3])
    patch = PathPatch(path, edgecolor=color, lw=width, facecolor='none', zorder=1)
    ax.add_patch(patch)

    if arrow:
        t=0.98
        xt = (1-t)**2*xs + 2*(1-t)*t*cx + t**2*xe
        yt = (1-t)**2*ys + 2*(1-t)*t*cy + t**2*ye
        dx_arrow, dy_arrow = xe-xt, ye-yt
        ax.arrow(xt, yt, dx_arrow, dy_arrow, length_includes_head=True,
                 head_width=0.03, head_length=0.02, fc=color, ec=color, linewidth=1)

    t_label=0.5
    xm = (1-t_label)**2*xs + 2*(1-t_label)*t_label*cx + t_label**2*xe
    ym = (1-t_label)**2*ys + 2*(1-t_label)*t_label*cy + t_label**2*ye
    return xm, ym

# --- Visualization ---
def visualize_step(ax, G, flow, path, bottleneck):
    ax.clear()
    for n,(x,y) in G.graph["pos"].items():
        ax.scatter(x, y, s=3000, c='lightblue', zorder=2)
        ax.text(x, y, n, fontsize=72*0.6, fontweight='bold', ha='center', va='center', zorder=3)

    drawn_pairs = {}
    bottleneck_edge = None
    if path:
        bottleneck_edge = min(path, key=lambda e: G[e[0]][e[1]]['capacity']-flow[e])

    for u,v in G.edges():
        pair = tuple(sorted([u,v]))
        rad = drawn_pairs.get(pair, 0.2 if pair not in drawn_pairs else -drawn_pairs[pair])
        drawn_pairs[pair] = rad

        color = 'black'
        width = 2*1.7
        if (u,v) in path:
            color = 'blue'
            width = 4*1.7
        if (u,v) == bottleneck_edge:
            color = 'red'
            width = 8*1.7

        xm, ym = draw_bezier(ax, G.graph["pos"][u], G.graph["pos"][v], rad, color=color, width=width, node_radius=0.06)

        ax.text(xm-0.01, ym, f"{flow[(u,v)]}", color='blue', fontsize=56*0.6, fontweight='bold', ha='right', va='center')
        ax.text(xm, ym, "/", color='black', fontsize=56*0.6, fontweight='bold', ha='center', va='center')
        ax.text(xm+0.01, ym, f"{G[u][v]['capacity']}", color='red', fontsize=56*0.6, fontweight='bold', ha='left', va='center')

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.2, 1.3)
    ax.axis('off')

# --- Example Graphs ---
def make_graph1():
    G = nx.DiGraph()
    G.add_edge('s','a', capacity=10)
    G.add_edge('s','b', capacity=5)
    G.add_edge('a','b', capacity=4)
    G.add_edge('b','a', capacity=2)
    G.add_edge('a','t', capacity=6)
    G.add_edge('b','t', capacity=10)
    G.graph["pos"] = {'s': (0,0.5), 'a': (0.4,0.7), 'b': (0.6,0.3), 't': (1,0.5)}
    return G
def make_graph1_alt():
    G = nx.DiGraph()
    G.add_edge('s','a', capacity=7)
    G.add_edge('s','b', capacity=12)
    G.add_edge('a','b', capacity=3)
    G.add_edge('b','a', capacity=1)
    G.add_edge('a','t', capacity=8)
    G.add_edge('b','t', capacity=6)
    G.graph["pos"] = {'s': (0,0.5), 'a': (0.4,0.7), 'b': (0.6,0.3), 't': (1,0.5)}
    return G
def make_graph2():
    G = nx.DiGraph()
    G.add_edge('s','a', capacity=30)
    G.add_edge('s','b', capacity=10)
    G.add_edge('a','c', capacity=10)
    G.add_edge('b','c', capacity=30)
    G.add_edge('c','d', capacity=30)
    G.add_edge('a', 'd', capacity=30)
    G.add_edge('b', 't', capacity=10)
    G.add_edge('d', 't', capacity=30)
    G.graph["pos"] = {'s': (0,0.8), 'a': (0.2,1.25), 'b': (0.5,0.3), 'c': (0.6,0.8),'d': (0.95,0.8),'t': (1.0,-0.1)}
    return G
def make_graph2_alt():
    G = nx.DiGraph()
    G.add_edge('s', 'a', capacity=30)
    G.add_edge('s', 'b', capacity=20)
    G.add_edge('a', 'c', capacity=10)
    G.add_edge('b', 'c', capacity=30)
    G.add_edge('c', 'd', capacity=30)
    G.add_edge('a', 'd', capacity=30)
    G.add_edge('b', 't', capacity=10)
    G.add_edge('d', 't', capacity=50)
    G.graph["pos"] = {'s': (0, 0.8), 'a': (0.2, 1.25), 'b': (0.5, 0.3), 'c': (0.6, 0.8), 'd': (0.95, 0.8),
                      't': (1.0, -0.1)}
    return G
def make_graph3():
    G = nx.DiGraph()
    G.add_edge('s','m', capacity=10)
    G.add_edge('s','n', capacity=5)
    G.add_edge('m','n', capacity=7)
    G.add_edge('m','t', capacity=8)
    G.add_edge('n','t', capacity=12)
    G.graph["pos"] = {'s': (0,0.5), 'm': (0.3,0.7), 'n': (0.3,0.3), 't': (1,0.5)}
    return G
def make_graph3_alt():
    G = nx.DiGraph()
    G.add_edge('s','m', capacity=15)
    G.add_edge('s','n', capacity=3)
    G.add_edge('m','n', capacity=2)
    G.add_edge('m','t', capacity=5)
    G.add_edge('n','t', capacity=9)
    G.graph["pos"] = {'s': (0,0.5), 'm': (0.3,0.7), 'n': (0.3,0.3), 't': (1,0.5)}
    return G

graph_builders = {
    "Graph 1": make_graph1,
    "Graph 1 different capacities": make_graph1_alt,
    "Lauda-Ingolstadt": make_graph2,
    "Lauda-Ingolstadt alternative": make_graph2_alt,
    "Graph 3": make_graph3,
    "Graph 3 different capacities": make_graph3_alt
}

# --- GUI ---
class EdmondsKarpGUI:
    def __init__(self, root, source, sink):
        self.root = root
        self.source = source
        self.sink = sink
        self.current_step = 0
        self.steps = []
        self.G = None

        self.top_label = tk.Label(root, text="", font=("Arial",36,'bold'))
        self.top_label.pack(pady=5)

        self.fig, self.ax = plt.subplots(figsize=(12,9), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(side=tk.BOTTOM, pady=5, fill=tk.X)

        # Exit Button links
        exit_btn = tk.Button(btn_frame, text="Exit", command=root.destroy,
                             font=("Arial",36,'bold'), height=2, width=15)
        exit_btn.pack(side=tk.LEFT, padx=10)

        # Previous / Next mittig
        middle_frame = tk.Frame(btn_frame)
        middle_frame.pack(side=tk.LEFT, expand=True)
        self.prev_btn = tk.Button(middle_frame, text="<< Previous", command=self.prev_step,
                                  font=("Arial",36,'bold'), height=2, width=15)
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        self.next_btn = tk.Button(middle_frame, text="Next >>", command=self.next_step,
                                  font=("Arial",36,'bold'), height=2, width=15)
        self.next_btn.pack(side=tk.LEFT, padx=10)

        # Dropdown rechts
        self.selected = StringVar(root)
        self.selected.set("Graph 1")
        dropdown = OptionMenu(btn_frame, self.selected, *graph_builders.keys(), command=self.load_graph)
        dropdown.config(font=("Arial",36,'bold'), height=2, width=30)
        menu = dropdown["menu"]
        for i in range(menu.index("end")+1):
            menu.entryconfig(i, font=("Arial",72))
        dropdown.pack(side=tk.RIGHT, padx=10, pady=5)

        self.load_graph("Graph 1")

    def load_graph(self, choice):
        builder = graph_builders[choice]
        self.G = builder()
        self.max_flow, self.steps = edmonds_karp(self.G, self.source, self.sink)
        self.current_step = 0
        self.show_step(0)

    def show_step(self, idx):
        flow, path, bottleneck = self.steps[idx]
        visualize_step(self.ax, self.G, flow, path, bottleneck)
        current_flow = sum(flow[(self.source,v)] for v in self.G.successors(self.source))
        self.top_label.config(
            text=f"Step {idx+1} — Current Flow = {current_flow} — Bottleneck = {bottleneck}"
        )
        self.canvas.draw()

    def next_step(self):
        if self.current_step < len(self.steps)-1:
            self.current_step += 1
            self.show_step(self.current_step)

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.show_step(self.current_step)

# --- Start ---
root = tk.Tk()
root.title("Edmonds-Karp Max Flow Visualization")
root.state("zoomed")
app = EdmondsKarpGUI(root, 's', 't')
root.mainloop()
