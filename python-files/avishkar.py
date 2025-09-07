import tkinter as tk
from tkinter import messagebox

# Node structure for the Binary Search Tree
class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key

# BST Class containing core tree logic
class BST:
    def __init__(self):
        self.root = None

    def insert(self, root, key):
        if root is None:
            return Node(key)
        if key < root.val:
            root.left = self.insert(root.left, key)
        elif key > root.val:
            root.right = self.insert(root.right, key)
        return root

    def search(self, root, key):
        if root is None or root.val == key:
            return root
        if key < root.val:
            return self.search(root.left, key)
        else:
            return self.search(root.right, key)

    def delete(self, root, key):
        if root is None:
            return root
        if key < root.val:
            root.left = self.delete(root.left, key)
        elif key > root.val:
            root.right = self.delete(root.right, key)
        else:
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            temp = self.min_value_node(root.right)
            root.val = temp.val
            root.right = self.delete(root.right, temp.val)
        return root

    def min_value_node(self, node):
        current = node
        while current.left:
            current = current.left
        return current

    def inorder(self, root):
        return self.inorder(root.left) + [root.val] + self.inorder(root.right) if root else []

    def preorder(self, root):
        return [root.val] + self.preorder(root.left) + self.preorder(root.right) if root else []

    def postorder(self, root):
        return self.postorder(root.left) + self.postorder(root.right) + [root.val] if root else []

# GUI Class for visualization
class BSTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Binary Search Tree Visualizer")
        self.root.configure(bg="#1e1e1e")

        self.bst = BST()
        self.tree_root = None

        # Main frames
        main_frame = tk.Frame(root, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas_frame = tk.Frame(main_frame, bg="#1e1e1e")
        self.canvas_frame.pack(side="left", fill="both", expand=True)

        controls_frame = tk.Frame(main_frame, bg="#1e1e1e")
        controls_frame.pack(side="right", fill="y", padx=10, pady=10)

        # Canvas for tree visualization
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=600, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_x = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(side="bottom", fill="x")
        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Controls on the right
        tk.Label(controls_frame, text="Binary Search Tree", font=("Helvetica", 16, "bold"),
                 bg="#1e1e1e", fg="#61dafb").pack(pady=10)

        # Input Section
        input_label = tk.Label(controls_frame, text="Enter values (comma-separated):",
                               bg="#1e1e1e", fg="#ffffff", font=("Helvetica", 10))
        input_label.pack(pady=(5, 0))

        self.entry_val = tk.Entry(controls_frame, width=25, bg="#333333", fg="#ffffff", insertbackground="#ffffff")
        self.entry_val.pack(pady=5)

        btn_frame = tk.Frame(controls_frame, bg="#1e1e1e")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Insert", command=self.insert_values,
                  bg="#4caf50", fg="white", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_value,
                  bg="#f44336", fg="white", font=("Helvetica", 10)).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Search", command=self.search_value,
                  bg="#2196f3", fg="white", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_tree,
                  bg="#757575", fg="white", font=("Helvetica", 10)).grid(row=1, column=1, padx=5, pady=5)

        # Traversal buttons
        tk.Label(controls_frame, text="Traversals:", bg="#1e1e1e", fg="#ffffff", font=("Helvetica", 10)).pack(pady=(10, 0))

        traversal_frame = tk.Frame(controls_frame, bg="#1e1e1e")
        traversal_frame.pack(pady=5)

        tk.Button(traversal_frame, text="Inorder", command=lambda: self.show_traversal("inorder"),
                  bg="#2196f3", fg="white", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(traversal_frame, text="Preorder", command=lambda: self.show_traversal("preorder"),
                  bg="#ff9800", fg="black", font=("Helvetica", 10)).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(traversal_frame, text="Postorder", command=lambda: self.show_traversal("postorder"),
                  bg="#9c27b0", fg="white", font=("Helvetica", 10)).grid(row=0, column=2, padx=5, pady=5)

        # Traversal output
        self.traversal_label = tk.Label(controls_frame, text="Traversal: ", bg="#1e1e1e",
                                        fg="#ff9800", font=("Helvetica", 10, "bold"))
        self.traversal_label.pack(pady=10)

    def insert_values(self):
        try:
            text = self.entry_val.get()
            values = [int(v.strip()) for v in text.split(",") if v.strip().isdigit()]
            if not values:
                messagebox.showerror("Error", "Please enter at least one valid integer separated by commas.")
                return
            for val in values:
                self.tree_root = self.bst.insert(self.tree_root, val)
            self.draw_tree()
            self.entry_val.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers separated by commas.")

    def delete_value(self):
        try:
            val = int(self.entry_val.get())
            if self.tree_root is None:
                messagebox.showwarning("Warning", "Tree is empty!")
                return
            self.tree_root = self.bst.delete(self.tree_root, val)
            self.draw_tree()
            self.entry_val.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def search_value(self):
        try:
            val = int(self.entry_val.get())
            if self.tree_root is None:
                messagebox.showwarning("Warning", "Tree is empty!")
                return
            result = self.bst.search(self.tree_root, val)
            if result:
                messagebox.showinfo("Search Result", f"Value {val} found!")
            else:
                messagebox.showinfo("Search Result", f"Value {val} not found!")
            self.entry_val.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def clear_tree(self):
        self.tree_root = None
        self.canvas.delete("all")
        self.traversal_label.config(text="Traversal: ")

    def draw_tree(self):
        self.canvas.delete("all")
        if self.tree_root:
            self._draw_node(self.tree_root, 400, 50, 150)

    def _draw_node(self, node, x, y, x_offset):
        if node:
            self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20,
                                    outline="#61dafb", width=2, fill="#3b4048")
            self.canvas.create_text(x, y, text=str(node.val), fill="#ffffff",
                                    font=("Helvetica", 12, "bold"))
            if node.left:
                self.canvas.create_line(x, y + 20, x - x_offset, y + 80, fill="#888888", width=1)
                self._draw_node(node.left, x - x_offset, y + 100, x_offset // 2)
            if node.right:
                self.canvas.create_line(x, y + 20, x + x_offset, y + 80, fill="#888888", width=1)
                self._draw_node(node.right, x + x_offset, y + 100, x_offset // 2)
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def show_traversal(self, order):
        if not self.tree_root:
            messagebox.showwarning("Warning", "Tree is empty!")
            return
        if order == "inorder":
            traversal = self.bst.inorder(self.tree_root)
        elif order == "preorder":
            traversal = self.bst.preorder(self.tree_root)
        else:
            traversal = self.bst.postorder(self.tree_root)
        self.traversal_label.config(text=f"{order.capitalize()} Traversal: {traversal}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BSTVisualizer(root)
    root.mainloop()
