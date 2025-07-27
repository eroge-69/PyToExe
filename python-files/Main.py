import tkinter as tk
import random


class TeamNameGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Team Name Generator")

        self.adjectives = []
        self.nouns = []

        # UI Elements
        self.adjective_label = tk.Label(root, text="Add Adjective:")
        self.adjective_label.pack()

        self.adjective_entry = tk.Entry(root)
        self.adjective_entry.pack()

        self.noun_label = tk.Label(root, text="Add Noun:")
        self.noun_label.pack()

        self.noun_entry = tk.Entry(root)
        self.noun_entry.pack()

        self.add_button = tk.Button(root, text="Add", command=self.add_words)
        self.add_button.pack()

        self.generate_button = tk.Button(root, text="Generate Team Name", command=self.generate_team_name)
        self.generate_button.pack()

        self.result_label = tk.Label(root, text="", font=("Helvetica", 16))
        self.result_label.pack()

    def add_words(self):
        adjective = self.adjective_entry.get().strip()
        noun = self.noun_entry.get().strip()

        if adjective:
            self.adjectives.append(adjective)
            self.adjective_entry.delete(0, tk.END)

        if noun:
            self.nouns.append(noun)
            self.noun_entry.delete(0, tk.END)

    def generate_team_name(self):
        if self.adjectives and self.nouns:
            adjective = random.choice(self.adjectives)
            noun = random.choice(self.nouns)
            team_name = f"{adjective} {noun}"
            self.result_label.config(text=team_name)
        else:
            self.result_label.config(text="Please add adjectives and nouns.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TeamNameGenerator(root)
    root.mainloop()
