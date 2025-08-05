import tkinter as tk
import json
import os

SAVE_FILE = "story_save.json"

# --- Rocket League 10-step arc (from before, slight polish) ---
rocket_league_story = {
    "ROCKET_1": {
        "blurb": "🚗💨 You're warming up with some stylish aerials. What next?",
        "choices": {"Practice flicks": "ROCKET_2", "Play ranked match": "ROCKET_3"},
        "item": None
    },
    "ROCKET_2": {
        "blurb": "🛠️ Flicks on point! You feel a surge of confidence.",
        "choices": {"Try a flip reset": "ROCKET_4"},
        "item": "Confidence Boost"
    },
    "ROCKET_3": {
        "blurb": "🏆 Ranked match time! Your opponents sweat.",
        "choices": {"Score a goal": "ROCKET_5", "Block a shot": "ROCKET_6"},
        "item": None
    },
    "ROCKET_4": {
        "blurb": "🔥 Flip reset nailed! Your rank jumps by 100 points!",
        "choices": {"Queue another game": "ROCKET_3", "Take a break": "ROCKET_7"},
        "item": "Flip Reset Mastery"
    },
    "ROCKET_5": {
        "blurb": "⚽ Goal scored! The crowd goes wild.",
        "choices": {"Celebrate": "ROCKET_8"},
        "item": "Goal Celebration"
    },
    "ROCKET_6": {
        "blurb": "🛡️ You block the shot with style. Teammates cheer.",
        "choices": {"Assist a goal": "ROCKET_8"},
        "item": None
    },
    "ROCKET_7": {
        "blurb": "☕ You sip your caramel macchiato, recharging.",
        "choices": {"Get back to training": "ROCKET_2", "Join the tournament": "ROCKET_9"},
        "item": "Energy Boost"
    },
    "ROCKET_8": {
        "blurb": "🎉 Party time! You are the MVP tonight.",
        "choices": {"Keep playing": "ROCKET_3", "Stream the game": "ROCKET_10"},
        "item": None
    },
    "ROCKET_9": {
        "blurb": "🏆 Tournament time! Everyone's watching your stream.",
        "choices": {"Win the finals": "ROCKET_END"},
        "item": "Tournament Participant"
    },
    "ROCKET_10": {
        "blurb": (
            "✨ Congratulations! You conquered Rocket League and the internet.\n\n"
            "🏅 You earned the title: Rocket Queen of the Server!"
        ),
        "choices": {},
        "item": None
    }
}

# --- Carnival 10-step arc ---
carnival_story = {
    "CARNIVAL_1": {
        "blurb": "🎡 You enter the pixelated carnival, lights flashing and music playing.",
        "choices": {"Visit haunted house": "CARNIVAL_2", "Play ring toss": "CARNIVAL_3"},
        "item": None
    },
    "CARNIVAL_2": {
        "blurb": "👻 Spooky ghosts pop out! You scream but collect a mysterious glowing gem.",
        "choices": {"Explore deeper": "CARNIVAL_4", "Run to roller-coaster": "CARNIVAL_5"},
        "item": "Glowing Gem"
    },
    "CARNIVAL_3": {
        "blurb": "🎯 Ring toss champion! You win a shiny neon block.",
        "choices": {"Trade prize": "CARNIVAL_6", "Try another game": "CARNIVAL_5"},
        "item": "Neon Block"
    },
    "CARNIVAL_4": {
        "blurb": "🕯️ Deeper in the haunted house, shadows whisper secrets.",
        "choices": {"Listen closely": "CARNIVAL_7", "Run outside": "CARNIVAL_5"},
        "item": None
    },
    "CARNIVAL_5": {
        "blurb": "🎢 The roller-coaster roars! Diamonds sparkle in your pocket.",
        "choices": {"Take selfie": "CARNIVAL_8", "Look for snacks": "CARNIVAL_9"},
        "item": "Diamonds"
    },
    "CARNIVAL_6": {
        "blurb": "💡 You trade your neon block for a special glowing lantern.",
        "choices": {"Light up the dark path": "CARNIVAL_7", "Keep exploring": "CARNIVAL_5"},
        "item": "Glowing Lantern"
    },
    "CARNIVAL_7": {
        "blurb": "✨ Your glowing items reveal a hidden passage full of treasures!",
        "choices": {"Collect treasure": "CARNIVAL_10"},
        "item": "Hidden Treasure"
    },
    "CARNIVAL_8": {
        "blurb": "🤳 Your selfie goes viral! Fans send you virtual pies.",
        "choices": {"Eat pie": "CARNIVAL_9"},
        "item": "Virtual Pies"
    },
    "CARNIVAL_9": {
        "blurb": "🥧 You enjoy delicious treats, gaining energy for more fun.",
        "choices": {"Join pie contest": "CARNIVAL_10"},
        "item": "Energy Boost"
    },
    "CARNIVAL_10": {
        "blurb": (
            "🎉 You win the carnival contest and are crowned Queen of the Carnival!\n\n"
            "Your treasures and energy make you unstoppable!"
        ),
        "choices": {},
        "item": "Carnival Crown"
    }
}

# --- Music 10-step arc ---
music_story = {
    "MUSIC_1": {
        "blurb": "🎶 Studio 404 is buzzing. What vibe will you create today?",
        "choices": {"Record kawaii vocals": "MUSIC_2", "Build synth bass": "MUSIC_3"},
        "item": None
    },
    "MUSIC_2": {
        "blurb": "🎤 Your sweet vocals float over the beat.",
        "choices": {"Add reverb effect": "MUSIC_4", "Write lyrics": "MUSIC_5"},
        "item": "Kawaii Vocals"
    },
    "MUSIC_3": {
        "blurb": "🎛️ Bassline thumps with energy, ready to drop!",
        "choices": {"Add filters": "MUSIC_5", "Loop beat": "MUSIC_6"},
        "item": "Thumping Bass"
    },
    "MUSIC_4": {
        "blurb": "✨ Reverb adds dreamy depth to your vocals.",
        "choices": {"Mix vocals": "MUSIC_7"},
        "item": None
    },
    "MUSIC_5": {
        "blurb": "✍️ Lyrics are heartfelt and catchy.",
        "choices": {"Record again": "MUSIC_2", "Produce instrumental": "MUSIC_6"},
        "item": "Catchy Lyrics"
    },
    "MUSIC_6": {
        "blurb": "🔄 Looping beat locked in, the crowd will dance!",
        "choices": {"Add synth solo": "MUSIC_8"},
        "item": None
    },
    "MUSIC_7": {
        "blurb": "🎧 Mixing complete. Your track sounds amazing!",
        "choices": {"Upload to Spotify": "MUSIC_9"},
        "item": None
    },
    "MUSIC_8": {
        "blurb": "🎹 Synth solo electrifies the track!",
        "choices": {"Master track": "MUSIC_9"},
        "item": "Synth Solo"
    },
    "MUSIC_9": {
        "blurb": "🚀 Your track goes viral, climbing charts worldwide!",
        "choices": {"Perform live": "MUSIC_10"},
        "item": "Viral Hit"
    },
    "MUSIC_10": {
        "blurb": (
            "🌟 Standing ovation! You're the pop queen everyone loves.\n\n"
            "Your music career skyrockets!"
        ),
        "choices": {},
        "item": "Pop Queen Title"
    }
}

# --- Cat Fam 10-step arc ---
catfam_story = {
    "CATFAM_1": {
        "blurb": "🐾 Your cat friends lounge around, purring softly.",
        "choices": {"Play with yarn": "CATFAM_2", "Take a nap": "CATFAM_3"},
        "item": None
    },
    "CATFAM_2": {
        "blurb": "🧶 Yarn everywhere! The cats are playful and happy.",
        "choices": {"Chase laser pointer": "CATFAM_4"},
        "item": "Yarn Ball"
    },
    "CATFAM_3": {
        "blurb": "😴 Soft snores fill the room as you nap.",
        "choices": {"Dream about adventures": "CATFAM_5"},
        "item": None
    },
    "CATFAM_4": {
        "blurb": "🔴 Cats chase the laser with wild excitement.",
        "choices": {"Pet them gently": "CATFAM_6"},
        "item": None
    },
    "CATFAM_5": {
        "blurb": "🌈 You dream of flying through a pastel sky with your cat crew.",
        "choices": {"Wake up happy": "CATFAM_6"},
        "item": None
    },
    "CATFAM_6": {
        "blurb": "❤️ Warm purrs surround you. You're loved.",
        "choices": {"Plan cat cosplay": "CATFAM_7", "Give treats": "CATFAM_8"},
        "item": "Cat Love"
    },
    "CATFAM_7": {
        "blurb": "🎭 You craft adorable cat ear headbands.",
        "choices": {"Take photos": "CATFAM_9"},
        "item": "Cat Ears"
    },
    "CATFAM_8": {
        "blurb": "🍣 Treats are gobbled up with happy meows.",
        "choices": {"Cuddle time": "CATFAM_9"},
        "item": "Happy Cats"
    },
    "CATFAM_9": {
        "blurb": "📸 Your cosplay photos are Instagram gold!",
        "choices": {"Share online": "CATFAM_10"},
        "item": "Instagram Likes"
    },
    "CATFAM_10": {
        "blurb": (
            "🌟 Your cat fam adores you and your followers cheer!\n\n"
            "You’re the ultimate Catgirl influencer!"
        ),
        "choices": {},
        "item": "Catgirl Influencer Title"
    }
}

# Combine all stories into one dictionary for the app
story_nodes = {**rocket_league_story, **carnival_story, **music_story, **catfam_story}

# Add START_MENU node explicitly to story_nodes for validation and consistency
story_nodes["START_MENU"] = {
    "blurb": "This is the starting menu.", # This blurb is overridden by update_story for START_MENU
    "choices": {
        "Rocket League Quest": "ROCKET_1",
        "Carnival Chaos": "CARNIVAL_1",
        "Music Mastery": "MUSIC_1",
        "Cat Fam Fun": "CATFAM_1",
    },
    "item": None
}

# Add ROCKET_END as a proper ending node since ROCKET_9 points to it
story_nodes["ROCKET_END"] = {
    "blurb": (
        "🏆 You won the Rocket League tournament! You are the ultimate champion!\n\n"
        "Your legend will live on forever!"
    ),
    "choices": {}, # No choices means it's an ending node
    "item": "Tournament Champion Title"
}

class StoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Epic Interactive Catgirl Story ✨")
        self.root.geometry("700x650")
        self.root.configure(bg="#ffe6f7")

        self.story_frame = tk.Frame(root, bg="#ffe6f7")
        self.story_frame.pack(fill="both", expand=True)

        self.text = tk.Label(
            self.story_frame,
            text="",
            wraplength=650,
            justify="left",
            font=("Comic Sans MS", 14),
            bg="#ffe6f7",
            fg="#4b0082"
        )
        self.text.pack(pady=15)

        self.button_frame = tk.Frame(self.story_frame, bg="#ffe6f7")
        self.button_frame.pack()

        self.save_load_frame = tk.Frame(self.story_frame, bg="#ffe6f7")
        self.save_load_frame.pack(pady=10)

        tk.Button(
            self.save_load_frame,
            text="💾 Save",
            font=("Comic Sans MS", 10, "bold"),
            bg="#ff69b4",
            fg="white",
            command=self.save_game
        ).pack(side="left", padx=10)

        tk.Button(
            self.save_load_frame,
            text="📂 Load",
            font=("Comic Sans MS", 10, "bold"),
            bg="#9370DB",
            fg="white",
            command=self.load_game
        ).pack(side="left", padx=10)

        self.inventory_label = tk.Label(
            self.story_frame,
            text="🎒 Inventory: (empty)",
            font=("Comic Sans MS", 12, "italic"),
            bg="#ffe6f7",
            fg="#c71585",
            wraplength=650,
            justify="left",
        )
        self.inventory_label.pack(pady=10)

        self.restart_button = None # Initialize restart_button to None

        self.current_node = "START_MENU" # Default starting point
        self.inventory = [] # Default empty inventory

        # Attempt to load a saved game immediately on startup
        self.load_game(initial_load=True)

    def update_story(self):
        print(f"🐾 DEBUG: Updating story node → {self.current_node}")

        # Handle the special START_MENU node
        if self.current_node == "START_MENU":
            self.text.config(text=(
                "✨ Welcome to the Catgirl Interactive Story! ✨\n\n"
                "Choose your adventure arc to begin:\n"
                "▶ Rocket League Quest\n"
                "▶ Carnival Chaos\n"
                "▶ Music Mastery\n"
                "▶ Cat Fam Fun"
            ))
            # Clear existing buttons
            for widget in self.button_frame.winfo_children():
                widget.destroy()
            # Destroy restart button if it exists from a previous end-game state
            if self.restart_button:
                self.restart_button.destroy()
                self.restart_button = None

            # Reset inventory display for main menu
            self.inventory_label.config(text="🎒 Inventory: (empty)")

            # Create buttons for each story arc
            buttons = [
                ("Rocket League Quest", "ROCKET_1"),
                ("Carnival Chaos", "CARNIVAL_1"),
                ("Music Mastery", "MUSIC_1"),
                ("Cat Fam Fun", "CATFAM_1"),
            ]
            for text, node_key in buttons:
                btn = tk.Button(
                    self.button_frame,
                    text=text,
                    font=("Comic Sans MS", 12, "bold"),
                    bg="#ffb6c1",
                    fg="white",
                    relief="raised",
                    padx=10,
                    pady=5,
                    command=lambda n=node_key: self.start_arc(n)
                )
                btn.pack(pady=5, fill="x")
            return # Exit after handling START_MENU

        node = story_nodes.get(self.current_node, None)
        if not node:
            # If the current node is not found, reset to START_MENU
            self.text.config(text=f"⚠️ Oops! Story node '{self.current_node}' not found. Resetting to main menu.")
            print(f"🚨 DEBUG: Node '{self.current_node}' does not exist in story_nodes. Resetting.")
            self.current_node = "START_MENU"
            self.inventory = []
            self.update_story() # Recursively call update_story to display the main menu
            return

        # Display the blurb for the current node
        self.text.config(text=node["blurb"])

        # Update inventory display
        if self.inventory:
            inv_text = "🎒 Inventory: " + ", ".join(self.inventory)
        else:
            inv_text = "🎒 Inventory: (empty)"
        self.inventory_label.config(text=inv_text)

        # Clear previous choice buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        # Destroy restart button if it was present from a previous end-game state
        if self.restart_button:
            self.restart_button.destroy()
            self.restart_button = None

        # Add item to inventory if the current node has one and it's not already collected
        if "item" in node and node["item"]:
            if node["item"] not in self.inventory:
                self.inventory.append(node["item"])
                # Update inventory display immediately after adding a new item
                self.inventory_label.config(text="🎒 Inventory: " + ", ".join(self.inventory) if self.inventory else "🎒 Inventory: (empty)")

        # If there are no choices, it's an ending node
        if not node["choices"]:
            end_label = tk.Label(
                self.button_frame,
                text="✨ End of this story arc. Thanks for playing! ✨",
                font=("Comic Sans MS", 12),
                bg="#ffe6f7",
                fg="#ff69b4"
            )
            end_label.pack(pady=10)

            # Create a restart button to go back to the main menu
            self.restart_button = tk.Button(
                self.story_frame, # This button is placed on the main story_frame
                text="🏠 Restart Story",
                font=("Comic Sans MS", 12, "bold"),
                bg="#ff69b4",
                fg="white",
                padx=10,
                pady=5,
                command=self.restart_story
            )
            self.restart_button.pack(pady=15)
            return # Exit after handling an end node

        # Create choice buttons for the current node
        for choice_text, next_node_key in node["choices"].items():
            btn = tk.Button(
                self.button_frame,
                text=choice_text,
                font=("Comic Sans MS", 12, "bold"),
                bg="#ffb6c1",
                fg="white",
                relief="raised",
                padx=10,
                pady=5,
                command=lambda n=next_node_key: self.select_choice(n)
            )
            btn.pack(pady=5, fill="x")

    def start_arc(self, node_key):
        """Starts a new story arc, resetting inventory."""
        self.current_node = node_key
        self.inventory = [] # Clear inventory when starting a new arc
        self.update_story()

    def select_choice(self, next_node):
        """Moves to the next story node based on user choice."""
        self.current_node = next_node
        self.update_story()

    def restart_story(self):
        """Resets the game to the main menu."""
        self.current_node = "START_MENU"
        self.inventory = [] # Clear inventory on full restart
        self.update_story()

    def save_game(self):
        """Saves the current game state (current node and inventory) to a JSON file."""
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump({
                    "current_node": self.current_node,
                    "inventory": self.inventory
                }, f)
            self.text.config(text=f"✅ Game saved! You're at: {self.current_node}")
        except Exception as e:
            self.text.config(text=f"❌ Save failed: {e}")
            print(f"🚨 DEBUG: Save error: {e}")

    def load_game(self, initial_load=False):
        """Loads the game state from a JSON file. Handles initial load vs. user-initiated load."""
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    data = json.load(f)
                    loaded_node = data.get("current_node", "START_MENU")
                    loaded_inventory = data.get("inventory", [])

                    # Validate if the loaded node still exists in the story data
                    if loaded_node not in story_nodes and loaded_node != "START_MENU":
                        print(f"⚠️ DEBUG: Saved node '{loaded_node}' not found in story_nodes. Resetting to START_MENU.")
                        loaded_node = "START_MENU"
                        loaded_inventory = [] # Clear inventory if node is invalid

                    self.current_node = loaded_node
                    self.inventory = loaded_inventory
                    self.update_story() # Update the UI with the loaded state
                    if not initial_load: # Only show confirmation message if user clicked "Load"
                        self.text.config(text="🎉 Loaded your last adventure!")
            except Exception as e:
                self.text.config(text=f"❌ Load failed: {e}")
                print(f"🚨 DEBUG: Error during load: {e}")
                # If loading fails, ensure the game starts fresh
                self.current_node = "START_MENU"
                self.inventory = []
                self.update_story()
                if not initial_load:
                    self.text.config(text="❌ Load failed! Starting fresh.")
        else:
            if not initial_load: # Only show message if user clicked "Load" and no file exists
                self.text.config(text="⚠️ No save file found! Starting fresh.")
            # Ensure the story is updated to the start menu if no save file exists
            self.current_node = "START_MENU"
            self.inventory = []
            self.update_story()


def validate_story_arcs(story_nodes):
    """
    Validates the structure of the story arcs, checking for missing nodes,
    unreachable nodes, and consistency.
    """
    linked_nodes = set()
    all_nodes = set(story_nodes.keys())

    errors = []
    warnings = []
    suggestion_map = []
    backlink_map = {} # To track which nodes link to others

    for node_key, node in story_nodes.items():
        # Critical checks for each node
        if "blurb" not in node:
            errors.append(f"❌ Node '{node_key}' is missing the 'blurb' text.")
        if "choices" not in node:
            errors.append(f"❌ Node '{node_key}' is missing the 'choices' dictionary.")
            continue # Cannot validate choices if the key is missing

        choices = node.get("choices", {})
        for choice_text, next_node_key in choices.items():
            if not next_node_key:
                errors.append(f"❌ Node '{node_key}' has a choice '{choice_text}' with no target node key.")
            elif next_node_key not in story_nodes:
                errors.append(f"❌ Node '{node_key}' choice '{choice_text}' points to a missing node '{next_node_key}'.")
            else:
                linked_nodes.add(next_node_key) # Track all nodes that are linked to
                backlink_map.setdefault(next_node_key, []).append(node_key)

    # Identify unreachable nodes (excluding the starting menu)
    unreachable = all_nodes - linked_nodes - {"START_MENU"}
    for node in unreachable:
        warnings.append(f"⚠️ Node '{node}' is unreachable from other nodes (excluding START_MENU).")
        suggestion_map.append(f"💡 Suggestion: Link to '{node}' from a previous node to make it accessible.")

    # Check for arc lengths (assuming 10 steps per arc)
    arc_sections = {}
    for key in story_nodes:
        if key == "START_MENU": # Skip START_MENU for arc length validation
            continue
        arc_name = key.split("_")[0] # e.g., "ROCKET", "CARNIVAL"
        arc_sections.setdefault(arc_name, []).append(key)

    for arc, nodes in arc_sections.items():
        # The number of nodes in an arc should ideally be consistent (e.g., 10)
        # Note: ROCKET_END is now part of story_nodes, so ROCKET arc will have 11 nodes.
        # This warning is for general consistency, adjust expectation if needed.
        if len(nodes) != 10 and arc != "ROCKET": # ROCKET arc now has 11 nodes due to ROCKET_END
            warnings.append(f"⚠️ Arc '{arc}' has {len(nodes)} sections (expected 10).")
            suggestion_map.append(f"🔧 Suggestion: Consider adjusting nodes in arc '{arc}' to match 10 steps for consistency.")
        elif arc == "ROCKET" and len(nodes) != 11: # Specific check for ROCKET arc with ROCKET_END
             warnings.append(f"⚠️ Arc '{arc}' has {len(nodes)} sections (expected 11 with ROCKET_END).")
             suggestion_map.append(f"🔧 Suggestion: Ensure ROCKET arc has 11 nodes including ROCKET_END.")


    print("\n--- STORY VALIDATION REPORT ---")
    if errors:
        print("\n".join(errors))
    else:
        print("✅ No critical errors found!")

    if warnings:
        print("\n".join(warnings))
    else:
        print("✨ All good! Your story is well-structured.")

    if suggestion_map:
        print("\n--- SUGGESTIONS ---")
        print("\n".join(suggestion_map))

    print("\n💼 Validation complete.\n")

    return backlink_map

# Call this once on startup to verify story structure
story_backlinks = validate_story_arcs(story_nodes)

if __name__ == "__main__":
    root = tk.Tk()
    app = StoryApp(root)
    root.mainloop()

