import ast
import os
import unicodedata
import textwrap
from graphviz import Digraph

INPUT_FILE = "exemplu.py"
FLOWCHART_IMG = "victorloh.png"

os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

def clean_code(source_code):
    normalized = unicodedata.normalize("NFKD", source_code)
    cleaned = ''.join(c if ord(c) < 128 else '?' for c in normalized)
    return cleaned

def wrap_text(text, width=30):
    return "\n".join(textwrap.wrap(text, width=width))

class CodeFlowParser(ast.NodeVisitor):
    def __init__(self):
        self.dot = Digraph(format='png', engine='dot')
        self.counter = 0
        self.last_node = None

        self.dot.attr(dpi='600', splines='ortho', rankdir='TB', nodesep='0.4', ranksep='0.6')
        self.dot.node_attr.update(fontsize='10', width='0.3', height='0.3', margin='0.05')
        self.dot.edge_attr.update(arrowsize='0.7')

    def unique_id(self):
        self.counter += 1
        return f"node{self.counter}"

    def add_node(self, label, shape="box"):
        label = wrap_text(clean_code(label))
        node_id = self.unique_id()
        self.dot.node(node_id, label, shape=shape)
        if self.last_node:
            self.dot.edge(self.last_node, node_id)
        self.last_node = node_id
        return node_id

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name):
                if func.id == 'input':
                    self.add_node("Input", shape="parallelogram")
                elif func.id == 'print':
                    args = ", ".join([ast.unparse(arg) for arg in node.value.args])
                    self.add_node(f"Output: print({args})", shape="parallelogram")
        self.generic_visit(node)

    def visit_If(self, node):
        cond = wrap_text(clean_code(f"If {ast.unparse(node.test)}?"))
        cond_id = self.unique_id()
        self.dot.node(cond_id, cond, shape='diamond')

        if self.last_node:
            self.dot.edge(self.last_node, cond_id)

       
        self.last_node = None
        true_nodes = []
        for stmt in node.body:
            self.visit(stmt)
            if self.last_node:
                true_nodes.append(self.last_node)
        true_entry = true_nodes[0] if true_nodes else None
        true_exit = true_nodes[-1] if true_nodes else None

        
        self.last_node = None
        false_nodes = []
        for stmt in node.orelse:
            self.visit(stmt)
            if self.last_node:
                false_nodes.append(self.last_node)
        false_entry = false_nodes[0] if false_nodes else None
        false_exit = false_nodes[-1] if false_nodes else None

        
        if true_entry:
            self.dot.edge(cond_id, true_entry, label="DA")
        else:
            
            true_exit = cond_id  
        if false_entry:
            self.dot.edge(cond_id, false_entry, label="NU")
        else:
            false_exit = cond_id

        
        join_id = self.unique_id()
        self.dot.node(join_id, "", shape="point")

        if true_exit and true_exit != cond_id:
            self.dot.edge(true_exit, join_id)
        if false_exit and false_exit != cond_id:
            self.dot.edge(false_exit, join_id)

        self.last_node = join_id

    def visit_While(self, node):
        cond = wrap_text(clean_code(f"While {ast.unparse(node.test)}?"))
        cond_id = self.unique_id()
        self.dot.node(cond_id, cond, shape='diamond')

        if self.last_node:
            self.dot.edge(self.last_node, cond_id)

        
        self.last_node = None
        body_nodes = []
        for stmt in node.body:
            self.visit(stmt)
            if self.last_node:
                body_nodes.append(self.last_node)
        body_entry = body_nodes[0] if body_nodes else None
        body_exit = body_nodes[-1] if body_nodes else None

        if body_entry:
            self.dot.edge(cond_id, body_entry, label="DA")
        if body_exit:
            self.dot.edge(body_exit, cond_id)

        
        after_while_id = self.unique_id()
        self.dot.node(after_while_id, "", shape="point")
        self.dot.edge(cond_id, after_while_id, label="NU")
        self.last_node = after_while_id

    def visit_For(self, node):
        header = wrap_text(clean_code(f"For {ast.unparse(node.target)} in {ast.unparse(node.iter)}?"))
        cond_id = self.unique_id()
        self.dot.node(cond_id, header, shape='diamond')

        if self.last_node:
            self.dot.edge(self.last_node, cond_id)

        self.last_node = None
        body_nodes = []
        for stmt in node.body:
            self.visit(stmt)
            if self.last_node:
                body_nodes.append(self.last_node)
        body_entry = body_nodes[0] if body_nodes else None
        body_exit = body_nodes[-1] if body_nodes else None

        if body_entry:
            self.dot.edge(cond_id, body_entry, label="DA")
        if body_exit:
            self.dot.edge(body_exit, cond_id)

        after_for_id = self.unique_id()
        self.dot.node(after_for_id, "", shape="point")
        self.dot.edge(cond_id, after_for_id, label="NU")
        self.last_node = after_for_id

    def visit_FunctionDef(self, node):
        func_id = self.add_node(f"Functie: {node.name}", shape="oval")
        prev_last = self.last_node
        self.last_node = func_id
        for stmt in node.body:
            self.visit(stmt)
        self.last_node = func_id if prev_last is None else prev_last



with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_code = f.read()

if raw_code.startswith('\ufeff'):
    raw_code = raw_code[1:]

try:
    tree = ast.parse(raw_code)
except SyntaxError as e:
    print(f"[Eroare] Codul sursa are o problema de sintaxa: {e}")
    exit(1)

parser = CodeFlowParser()
parser.add_node("Start", shape="oval")
parser.visit(tree)
parser.add_node("End", shape="oval")

parser.dot.render(FLOWCHART_IMG.replace('.png', ''), cleanup=True)
print(f"Shcemea logica a fost generata: {FLOWCHART_IMG}")
