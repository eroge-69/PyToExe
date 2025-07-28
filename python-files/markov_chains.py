import tkinter as tk
from tkinter import simpledialog, messagebox
import random
import matplotlib.pyplot as plt
from collections import defaultdict
import math

class StateNode:
    def __init__(self, canvas, x, y, name, simulator):
        self.canvas = canvas
        self.simulator = simulator
        self.x = x
        self.y = y
        self.name = name
        self.radius = 25
        self.id = canvas.create_oval(x - self.radius, y - self.radius, x + self.radius, y + self.radius, fill="lightblue")
        self.text_id = canvas.create_text(x, y, text=name)
        self.bind_events()

    def bind_events(self):
        self.canvas.tag_bind(self.id, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.text_id, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.id, "<Button-3>", self.on_right_click)
        self.canvas.tag_bind(self.text_id, "<Button-3>", self.on_right_click)

    def on_click(self, event):
        self.simulator.handle_state_click(self)

    def on_right_click(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Rename", command=self.rename)
        menu.add_command(label="Delete", command=lambda: self.simulator.remove_state(self))
        menu.post(event.x_root, event.y_root)

    def rename(self):
        new_name = simpledialog.askstring("Rename State", "Enter new name:", initialvalue=self.name)
        if new_name and new_name != self.name:
            self.name = new_name
            self.canvas.itemconfig(self.text_id, text=new_name)
            self.simulator.rename_state_references(self)

    def coords(self):
        return self.x, self.y

class Transition:
    def __init__(self, canvas, from_node, to_node, weight, simulator):
        self.canvas = canvas
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.simulator = simulator
        self.line = None
        self.text = None
        self.draw()

    def draw(self):
        fx, fy = self.from_node.coords()
        tx, ty = self.to_node.coords()

        dx, dy = tx - fx, ty - fy
        distance = math.hypot(dx, dy)

        if self.from_node == self.to_node:
            # Draw a self-loop
            r = self.from_node.radius
            loop_x = fx
            loop_y = fy - r - 20
            self.line = self.canvas.create_arc(fx - r, fy - r - 40, fx + r, fy - r, start=0, extent=300, style=tk.ARC, width=2)
            self.text = self.canvas.create_text(loop_x, loop_y, text=f"{self.weight:.2f}", font=("Arial", 10), fill="black")
        else:
            # Curved line if bidirectional
            offset = 20 if self.simulator.has_reverse_transition(self.from_node, self.to_node) else 0
            ctrl_x = (fx + tx) / 2 + offset * (dy / distance)
            ctrl_y = (fy + ty) / 2 - offset * (dx / distance)

            self.line = self.canvas.create_line(fx, fy, ctrl_x, ctrl_y, tx, ty, smooth=True, width=2, arrow=tk.LAST)
            self.text = self.canvas.create_text(ctrl_x, ctrl_y, text=f"{self.weight:.2f}", font=("Arial", 10), fill="black")

        self.bind_events()

    def bind_events(self):
        self.canvas.tag_bind(self.line, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.text, "<Button-1>", self.on_click)

    def on_click(self, event):
        new_weight = simpledialog.askfloat("Edit Weight", f"New weight from {self.from_node.name} to {self.to_node.name}:", initialvalue=self.weight)
        if new_weight is not None:
            self.weight = new_weight
            self.simulator.update_transition(self)

    def delete(self):
        self.canvas.delete(self.line)
        self.canvas.delete(self.text)

class MarkovSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Markov Chain Simulator")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack()

        self.states = []
        self.transitions = []
        self.transition_map = defaultdict(dict)
        self.click_buffer = []
        self.visits = defaultdict(int)

        self.teleport_chance = 0.1

        self.toolbar = tk.Frame(root)
        self.toolbar.pack()

        tk.Button(self.toolbar, text="Add State", command=self.add_state).pack(side=tk.LEFT)
        tk.Button(self.toolbar, text="Run Simulation", command=self.run_simulation).pack(side=tk.LEFT)

    def add_state(self):
        name = simpledialog.askstring("New State", "Enter state name:")
        if not name:
            return
        x = random.randint(50, 750)
        y = random.randint(50, 550)
        new_node = StateNode(self.canvas, x, y, name, self)
        self.states.append(new_node)

    def handle_state_click(self, node):
        self.click_buffer.append(node)
        if len(self.click_buffer) == 2:
            from_node, to_node = self.click_buffer
            weight = simpledialog.askfloat("Transition Weight", f"Weight from {from_node.name} to {to_node.name}:", minvalue=0.0, initialvalue=1.0)
            if weight is not None:
                self.add_or_update_transition(from_node, to_node, weight)
            self.click_buffer.clear()

    def add_or_update_transition(self, from_node, to_node, weight):
        # Remove existing transition first
        if to_node in self.transition_map[from_node]:
            self.transition_map[from_node][to_node].delete()
        transition = Transition(self.canvas, from_node, to_node, weight, self)
        self.transition_map[from_node][to_node] = transition
        self.transitions.append(transition)

    def update_transition(self, transition):
        transition.delete()
        self.add_or_update_transition(transition.from_node, transition.to_node, transition.weight)

    def remove_state(self, node):
        # Delete transitions involving this node
        for other in list(self.transition_map[node].keys()):
            self.transition_map[node][other].delete()
            del self.transition_map[node][other]
        for src in list(self.transition_map):
            if node in self.transition_map[src]:
                self.transition_map[src][node].delete()
                del self.transition_map[src][node]
        self.transition_map.pop(node, None)

        # Remove from GUI and list
        self.canvas.delete(node.id)
        self.canvas.delete(node.text_id)
        self.states.remove(node)

    def rename_state_references(self, renamed_node):
        # No action needed unless we store names instead of objects
        pass

    def has_reverse_transition(self, from_node, to_node):
        return from_node != to_node and from_node in self.transition_map[to_node]

    def run_simulation(self):
        steps = simpledialog.askinteger("Simulation", "How many steps?", minvalue=1, initialvalue=100)
        teleport_chance = simpledialog.askfloat("Teleport Chance", "Chance to teleport randomly (0-1):", minvalue=0.0, maxvalue=1.0, initialvalue=self.teleport_chance)
        if steps is None or teleport_chance is None:
            return
        self.teleport_chance = teleport_chance

        if not self.states:
            messagebox.showinfo("Error", "No states defined.")
            return

        current = random.choice(self.states)
        self.visits.clear()

        for _ in range(steps):
            self.visits[current.name] += 1
            if random.random() < teleport_chance:
                current = random.choice(self.states)
                continue
            transitions = self.transition_map[current]
            if not transitions:
                continue
            total_weight = sum(t.weight for t in transitions.values())
            r = random.uniform(0, total_weight)
            cumulative = 0
            for node, t in transitions.items():
                cumulative += t.weight
                if r <= cumulative:
                    current = node
                    break

        self.show_bar_chart()

    def show_bar_chart(self):
        names = list(self.visits.keys())
        counts = [self.visits[n] for n in names]
        total = sum(counts)
        percentages = [c / total * 100 for c in counts]
        plt.figure(figsize=(10, 5))
        bars = plt.bar(names, counts)
        for i, (bar, p) in enumerate(zip(bars, percentages)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{counts[i]} ({p:.1f}%)", ha='center', va='bottom')
        plt.ylabel("Visits")
        plt.title("State Visits after Simulation")
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkovSimulator(root)
    root.mainloop()
