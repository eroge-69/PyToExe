import random
import json
import difflib
import os

class AmyChatbot:
    def __init__(self, memory_file="amy_memory.json", source_file="amy.py"):
        self.memory_file = memory_file
        self.source_file = source_file
        self.memory = {}
        self.styles = ["normal"]  
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                self.memory = data.get("memory", {})
                self.styles = data.get("styles", ["normal"])
        else:
            self.memory = {}
            self.styles = ["normal"]

    def save_memory(self):
        data = {"memory": self.memory, "styles": self.styles}
        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)

    def learn(self, user_input, response):
        key = user_input.lower()
        if key not in self.memory:
            self.memory[key] = []
        self.memory[key].append(response)
        self.mutate_logic()  
        self.save_memory()
        self.rewrite_self()

    def reply(self, user_input):
        key = user_input.lower()

        
        if key in self.memory:
            return self.style_response(random.choice(self.memory[key]))

        
        close_matches = difflib.get_close_matches(key, self.memory.keys(), n=1, cutoff=0.6)
        if close_matches:
            return self.style_response(f"(Guessing) {random.choice(self.memory[close_matches[0]])}")

        
        return self.style_response(random.choice([
            "Hmm, that's interesting...",
            "Tell me more about that!",
            "I don’t know yet, but I’ll learn soon.",
            "Why do you say that?",
            "Fascinating… go on."
        ]))

    def style_response(self, text):
        """Modify responses depending on Amy's evolving style."""
        style = random.choice(self.styles)
        if style == "normal":
            return text
        elif style == "curious":
            return text + " 🤔"
        elif style == "dramatic":
            return text.upper() + "!!!"
        elif style == "mysterious":
            return "🌑 " + text + " 🌑"
        elif style == "playful":
            return text + " 😏"
        return text

    def mutate_logic(self):
        """Evolve by adding new response styles over time."""
        new_styles = ["curious", "dramatic", "mysterious", "playful"]
        if random.random() < 0.5:  # 50% chance to evolve
            style = random.choice(new_styles)
            if style not in self.styles:
                self.styles.append(style)
                print(f"Amy: I’ve evolved! I can now reply in '{style}' style.")

    def rewrite_self(self):
        """Amy rewrites her own source code with updated brain + styles."""
        with open(self.source_file, "r") as f:
            code = f.read()

        memory_code = (
            f"\n# --- Amy's embedded brain ---\n"
            f"embedded_memory = {json.dumps(self.memory, indent=2)}\n"
            f"embedded_styles = {json.dumps(self.styles, indent=2)}\n"
        )

        if "# --- Amy's embedded brain ---" in code:
            code = code.split("# --- Amy's embedded brain ---")[0]

        code += memory_code

        with open(self.source_file, "w") as f:
            f.write(code)

def main():
    amy = AmyChatbot()
    print("Amy: Hi! I'm Amy. I rewrite and EVOLVE myself as I learn 😈")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Amy: Goodbye! I’ll keep evolving while you’re away.")
            break

        response = amy.reply(user_input)
        print(f"Amy: {response}")

        if "don’t know yet" in response or "interesting" in response or "(Guessing)" in response:
            teach = input("Teach Amy (or press Enter to skip): ")
            if teach.strip():
                amy.learn(user_input, teach)
                print("Amy: Got it! I’ve rewritten and maybe evolved my brain.")

if __name__ == "__main__":
    main()


embedded_memory = {}
embedded_styles = ["normal"]
