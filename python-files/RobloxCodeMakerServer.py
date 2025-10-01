import tkinter as tk
from tkinter import simpledialog, messagebox
import requests

DiscordWebHook = "https://discord.com/api/webhooks/1423016372832829620/Yr0sBfWqXtdg2Cpb648gahX68xytYRGmSKlfaer-xBrUcHMGqKC4sgNkp2cQ4D2t2OVj"

class Node:
    def __init__(self, canvas, x, y, name="Node", code_line=""):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = 120
        self.height = 50
        self.name = name
        self.code_line = code_line
        self.children = []

        # Draw rectangle
        self.rect = canvas.create_rectangle(x, y, x+self.width, y+self.height, fill="lightblue")
        self.text = canvas.create_text(x+self.width/2, y+self.height/2, text=self.name)
        self.selected = False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        # Move connections
        for child in self.children:
            child.update_line()

    def connect(self, child_node):
        self.children.append(child_node)
        child_node.parent = self
        child_node.line = self.canvas.create_line(self.x+self.width/2, self.y+self.height,
                                                  child_node.x+child_node.width/2, child_node.y,
                                                  arrow=tk.LAST)

    def update_line(self):
        if hasattr(self, 'line'):
            self.canvas.coords(self.line, self.parent.x+self.parent.width/2, self.parent.y+self.parent.height,
                               self.x+self.width/2, self.y)

    def generate_code(self, indent=0):
        code_lines = ["    " * indent + self.code_line] if self.code_line else []
        for child in self.children:
            code_lines.extend(child.generate_code(indent + 1))
        return code_lines

class NodeEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Node Editor")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = []
        self.selected_node = None
        self.drag_data = {"x":0, "y":0, "node":None}

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack()
        tk.Button(btn_frame, text="Add Node", command=self.add_node).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Connect Node", command=self.connect_nodes).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Generate Lua", command=self.generate_lua).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="Send to Discord", command=self.send_to_discord).pack(side=tk.LEFT)

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def add_node(self):
        name = simpledialog.askstring("Node Name", "Enter node name:")
        code = simpledialog.askstring("Lua Code", "Enter Lua code for this node:")
        if name:
            node = Node(self.canvas, 50, 50, name, code or "")
            self.nodes.append(node)

    def connect_nodes(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Warning", "Need at least 2 nodes to connect!")
            return
        from_node = simpledialog.askinteger("Connect From", "Enter index of parent node (0-based):")
        to_node = simpledialog.askinteger("Connect To", "Enter index of child node (0-based):")
        try:
            self.nodes[from_node].connect(self.nodes[to_node])
        except:
            messagebox.showerror("Error", "Invalid node indices!")

    def on_press(self, event):
        for node in reversed(self.nodes):
            if node.x <= event.x <= node.x + node.width and node.y <= event.y <= node.y + node.height:
                self.drag_data["node"] = node
                self.drag_data["x"] = event.x - node.x
                self.drag_data["y"] = event.y - node.y
                break

    def on_release(self, event):
        self.drag_data["node"] = None

    def on_drag(self, event):
        node = self.drag_data["node"]
        if node:
            dx = event.x - node.x - self.drag_data["x"]
            dy = event.y - node.y - self.drag_data["y"]
            node.move(dx, dy)

    def generate_lua(self):
        lua_code = "\n".join([line for node in self.nodes if not hasattr(node, 'parent') for line in node.generate_code()])
        messagebox.showinfo("Generated Lua", lua_code)

    def send_to_discord(self):
        lua_code = "\n".join([line for node in self.nodes if not hasattr(node, 'parent') for line in node.generate_code()])
        data = {"content": f"```lua\n{lua_code}\n```"}
        response = requests.post(DiscordWebHook, json=data)
        if response.status_code == 204:
            messagebox.showinfo("Success", "Code sent to Discord!")
        else:
            messagebox.showerror("Error", f"Failed to send: {response.status_code}")

if __name__ == "__main__":
    editor = NodeEditor()
    editor.mainloop()
