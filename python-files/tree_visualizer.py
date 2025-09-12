import json
from graphviz import Digraph

class Node:
    def __init__(self, acronym, avg_temp, left=None, right=None):
        self.acronym = acronym
        self.avg_temp = avg_temp
        self.left = left
        self.right = right

def build_tree(data):
    if data is None:
        return None
    return Node(
        data["acronym"],
        data["avg_temp"],
        build_tree(data["left"]),
        build_tree(data["right"])
    )

def draw_tree(root, filename="tree"):
    dot = Digraph(comment="Binary Tree")
    dot.attr('node', shape='circle', style='filled', color='lightblue2')

    def add_nodes_edges(node):
        if not node:
            return
        label = f"{node.acronym}\n{node.avg_temp:.2f}°C"
        dot.node(str(id(node)), label)

        if node.left:
            dot.edge(str(id(node)), str(id(node.left)))
            add_nodes_edges(node.left)
        if node.right:
            dot.edge(str(id(node)), str(id(node.right)))
            add_nodes_edges(node.right)

    add_nodes_edges(root)
    dot.render(filename, view=True, format="png")

if __name__ == "__main__":
    # Leer JSON generado por Java
    with open("tree.json", "r") as f:
        data = json.load(f)

    root = build_tree(data)
    draw_tree(root, "binary_tree")
