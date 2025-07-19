import pygame
import sys
import random
import os

# --- NPC GENERATOR ---
def load_images_from_folder(folder_path):
    """Loads all .png images from a specified folder."""
    # This function requires the script to be run from a directory where 'assets' is a subfolder.
    # If you get a file not found error, ensure your folder structure is correct.
    try:
        return [pygame.image.load(os.path.join(folder_path, f)).convert_alpha()
                for f in os.listdir(folder_path) if f.endswith(".png")]
    except pygame.error as e:
        print(f"Error loading images from {folder_path}: {e}")
        print("Please ensure the 'assets' folder is in the same directory as the script.")
        sys.exit()

def generate_random_name():
    """Generates a random two-part name."""
    first = ["Alex", "Sam", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Jamie", "Drew", "Cameron", "Travis", "Turd"]
    last = ["Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Scott", "Derp", "Watson"]
    return f"{random.choice(first)} {random.choice(last)}"

npc_id_counter = 1
def generate_npc(male_heads, female_heads, male_faces, female_faces,
                 male_hair, female_hair, real_umbrellas, fake_umbrellas):
    """Creates a new NPC with randomized features and an umbrella."""
    global npc_id_counter
    gender = random.choice(["male", "female"])
    head = random.choice(male_heads if gender == "male" else female_heads)
    face = random.choice(male_faces if gender == "male" else female_faces)
    hair = random.choice(male_hair if gender == "male" else female_hair)

    width, height = head.get_width(), head.get_height()
    combined = pygame.Surface((width, height), pygame.SRCALPHA)
    for layer in [head, face, hair]:
        combined.blit(layer, (0, 0))

    # 50% chance for a real or fake umbrella
    if random.random() < 0.5:
        umbrella = random.choice(real_umbrellas)
        umbrella_type = "real"
    else:
        umbrella = random.choice(fake_umbrellas)
        umbrella_type = "fake"

    sprite = combined.copy()
    sprite.blit(umbrella, (10, height - umbrella.get_height() - 20))

    npc_data = {
        "gender": gender,
        "head": combined,
        "umbrella": umbrella,
        "umbrella_type": umbrella_type,
        "sprite": sprite,
        "name": generate_random_name(),
        "id": npc_id_counter
    }
    npc_id_counter += 1
    return npc_data

# --- NPC DISPLAY with sliding umbrella ---
class NPCDisplay:
    """Handles the visual representation and animation of an NPC card."""
    def __init__(self, npc):
        self.npc = npc
        # Card position & size
        self.card_x, self.card_y = 335, 150
        self.card_width, self.card_height = 300, 400
        # Door (umbrella window) position and size
        self.door_x = self.card_x + self.card_width + 30
        self.door_y, self.door_width, self.door_height = 200, 220, 240
        # Umbrella animation properties
        self.umbrella_x = self.door_x + (self.door_width - self.npc["umbrella"].get_width() * 3) // 2
        self.umbrella_y = self.door_y - self.npc["umbrella"].get_height() * 3 - 20 # Start above window
        self.umbrella_target_y = self.door_y + self.door_height - self.npc["umbrella"].get_height() * 3
        self.sliding_down = True
        self.slide_speed = 10

    def update(self):
        """Updates the umbrella sliding animation."""
        if self.sliding_down:
            self.umbrella_y += self.slide_speed
            if self.umbrella_y >= self.umbrella_target_y:
                self.umbrella_y = self.umbrella_target_y
                self.sliding_down = False

    def draw(self, surface):
        """Draws the NPC card and umbrella window onto the given surface."""
        # Draw card background & border
        pygame.draw.rect(surface, (50, 50, 50), (self.card_x, self.card_y, self.card_width, self.card_height))
        pygame.draw.rect(surface, (200, 200, 200), (self.card_x, self.card_y, self.card_width, self.card_height), 4)

        # Draw scaled NPC head in card
        scale = 4
        head_scaled = pygame.transform.scale(self.npc["head"], (self.npc["head"].get_width() * scale, self.npc["head"].get_height() * scale))
        sprite_x = self.card_x + (self.card_width - head_scaled.get_width()) // 2
        sprite_y = self.card_y + 40
        surface.blit(head_scaled, (sprite_x, sprite_y))

        # Draw NPC name and ID
        name = small_font.render(self.npc.get("name", "Unknown"), True, (255, 255, 255))
        id_text = small_font.render(f"ID: {self.npc.get('id', '???')}", True, (180, 180, 180))
        surface.blit(name, (self.card_x + (self.card_width - name.get_width()) // 2, sprite_y + head_scaled.get_height() + 30))
        surface.blit(id_text, (self.card_x + (self.card_width - id_text.get_width()) // 2, sprite_y + head_scaled.get_height() + 55))

        # Draw door/window rectangle
        door_rect = pygame.Rect(self.door_x, self.door_y, self.door_width, self.door_height)
        pygame.draw.rect(surface, (100, 100, 100), door_rect)
        pygame.draw.rect(surface, (200, 200, 200), door_rect, 2)

        # Draw umbrella scaled and clipped inside the door window
        umbrella_surf = pygame.Surface((self.door_width, self.door_height), pygame.SRCALPHA)
        umbrella_scaled = pygame.transform.scale(self.npc["umbrella"], (self.npc["umbrella"].get_width() * 3, self.npc["umbrella"].get_height() * 3))
        umbrella_surf.blit(umbrella_scaled, ((self.door_width - umbrella_scaled.get_width()) // 2, self.umbrella_y - self.door_y))
        surface.set_clip(door_rect)
        surface.blit(umbrella_surf, (self.door_x, self.door_y))
        surface.set_clip(None)

# --- Initialization ---
pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1020, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DOPPELGANGER")

# Load assets
try:
    small_font = pygame.font.Font("assets/fonts/daydream.ttf", 15)
    font = pygame.font.Font("assets/fonts/daydream.ttf", 25)
    pygame.mixer.music.load("assets/audio/bg_music.mp3")
    sound_correct = pygame.mixer.Sound("assets/audio/correct.wav")
    sound_wrong = pygame.mixer.Sound("assets/audio/wrong.wav")
    sound_menu_move = pygame.mixer.Sound("assets/audio/menu_move.wav")
    sound_select = pygame.mixer.Sound("assets/audio/select.wav")
except pygame.error as e:
    print(f"Error loading font or audio file: {e}")
    print("Please ensure the 'assets' folder and its contents are correct.")
    sys.exit()

clock = pygame.time.Clock()

# Sounds configuration
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Dialog options
dialogs = {
    "accepted_real": ["Thanks!", "Good service!", "You're doing great!"],
    "accepted_fake": ["Hehehehe", "See ya, sucker!", "Got away with it!"],
    "rejected_real": ["What the frick man?", "I got this at the store!", "That's not fair!"],
    "rejected_fake": ["Aww man...", "Curse you!", "You won't get away with this!"]
}

# Load all image assets once at the start
(male_heads, female_heads, male_faces, female_faces,
 male_hair, female_hair, real_umbrellas, fake_umbrellas) = (
    load_images_from_folder("assets/heads/male"),
    load_images_from_folder("assets/heads/female"),
    load_images_from_folder("assets/faces/male"),
    load_images_from_folder("assets/faces/female"),
    load_images_from_folder("assets/hair/male"),
    load_images_from_folder("assets/hair/female"),
    load_images_from_folder("assets/umbrellas/real"),
    load_images_from_folder("assets/umbrellas/fake"),
)

class Game:
    """Manages the overall game state, logic, and rendering."""
    def __init__(self):
        # Game states
        self.STATE_MENU = "menu"
        self.STATE_GAME = "game"
        self.STATE_INSTRUCTIONS = "instructions"
        self.STATE_CREDITS = "credits"
        self.STATE_GAME_OVER = "game_over"
        self.STATE_PERK_SELECTION = "perk_selection" # New state for perk selection
        self.state = self.STATE_MENU

        # Game variables
        self.player_money = 0
        self.round = 1
        self.MAX_ROUNDS = random.randint(3, 5)
        self.selected_menu_index = 0

        # Interview goal for the round
        self.interview_count = 0
        self.interviews_to_next_perk = random.randint(5, 10)

        # --- Round timer for perk challenge (now counts up) ---
        self.round_time_limit = 30000  # Still defines the goal time for a perk
        self.round_start_time = 0

        # Perks system
        self.active_perks = []
        self.perk_messages = []  # Stores [message, alpha, y_pos] for general perks (now used for all floating messages)
        self.speed_perk_messages = [] # This will now be integrated into perk_messages or removed if not needed for separate display

        self.ten_second_perk_awarded_this_round = False # Flag to ensure speed perk is awarded once per round

        # Speech bubble properties
        self.npc_speech = ""
        self.speech_start_time = 0
        self.SPEECH_DURATION = 2000

        # Initial NPC setup
        self.current_npc = self.generate_npc()
        self.npc_display = NPCDisplay(self.current_npc)

        # --- NEW: Perk Selection Screen Variables ---
        self.perk_cards = [] # List to hold perk data for the selection screen
        self.selected_perk_index = 0 # Index of the currently highlighted perk card
        self.perk_card_target_y = 150 # Target Y position for the top perk card
        self.perk_card_spacing = 50 # Spacing between perk cards
        self.perk_card_slide_speed = 5 # Speed at which perk cards slide up

        # Define all possible perks with their properties
        self.all_perk_definitions = {
            "double_money": {"name": "Double Money", "desc": "Earn 2x money per decision."},
            "triple_money": {"name": "Triple Money", "desc": "Earn 3x money per decision."},
            "good_service": {"name": "Good Service", "desc": "+$50 bonus per correct decision."},
            "speed_double_money": {"name": "Speed Demon: 2x Money", "desc": "Earn 2x money per decision (Fastest Round)."},
            "speed_triple_money": {"name": "Speed Demon: 3x Money", "desc": "Earn 3x money per decision (Fastest Round)."},
            # Add more general perks if desired
            "extra_life": {"name": "Extra Life", "desc": "Gain an extra chance to fail a round."},
            "money_magnet": {"name": "Money Magnet", "desc": "+$10 bonus per decision."},
        }
        # Separate general perks from speed perks for selection logic
        self.general_perk_ids = [pid for pid, pdata in self.all_perk_definitions.items() if not pid.startswith("speed_")]
        self.speed_perk_ids = [pid for pid, pdata in self.all_perk_definitions.items() if pid.startswith("speed_")]


    def generate_npc(self):
        """Generates a new NPC using the global function."""
        return generate_npc(male_heads, female_heads, male_faces, female_faces,
                            male_hair, female_hair, real_umbrellas, fake_umbrellas)

    def start_new_round(self):
        """Resets variables for the start of a new round."""
        # Start the main round timer
        self.round_start_time = pygame.time.get_ticks()
        self.interview_count = 0
        self.interviews_to_next_perk = random.randint(5, 10)
        # Perks are cleared at the start of a round; you must earn them again.
        # Active perks are NOT cleared, they persist through rounds
        self.perk_messages.clear()
        self.speed_perk_messages.clear() # This will be removed later as messages are consolidated
        self.ten_second_perk_awarded_this_round = False # Reset speed qualification for the new round

        self.current_npc = self.generate_npc()
        self.npc_display = NPCDisplay(self.current_npc)
        # No individual NPC timer to reset

    def finish_round(self):
        """Ends the current round and checks for game over or perk selection."""
        self.round += 1
        if self.round > self.MAX_ROUNDS:
            self.state = self.STATE_GAME_OVER
        elif self.round == 3: # After round 2, go to perk selection
            self.state = self.STATE_PERK_SELECTION
            self.prepare_perk_selection_cards()
        else:
            self.start_new_round()

    def prepare_perk_selection_cards(self):
        """Generates 4 perk cards for the selection screen."""
        self.perk_cards.clear()
        self.selected_perk_index = 0

        # Create a pool of perks to choose from
        selection_pool = list(self.general_perk_ids) # Start with all general perks

        # If qualified, add a random speed perk to the pool
        if self.ten_second_perk_awarded_this_round:
            # Ensure at least one speed perk is offered if qualified
            chosen_speed_perk_id = random.choice(self.speed_perk_ids)
            # Add it to the selection pool if not already there
            if chosen_speed_perk_id not in selection_pool:
                selection_pool.append(chosen_speed_perk_id)

        # Ensure we pick 4 unique perks, avoiding duplicates
        # Use a set to keep track of chosen perk IDs to ensure uniqueness
        chosen_perk_ids = set()
        
        # If qualified, ensure one speed perk is chosen first
        if self.ten_second_perk_awarded_this_round and self.speed_perk_ids:
            chosen_speed_perk_id = random.choice(self.speed_perk_ids)
            chosen_perk_ids.add(chosen_speed_perk_id)

        # Fill the remaining slots with random unique perks from the general pool
        while len(chosen_perk_ids) < 4:
            if not selection_pool: # No more perks to choose from
                break
            
            # Filter out perks already chosen
            available_for_random_pick = [pid for pid in selection_pool if pid not in chosen_perk_ids]
            if not available_for_random_pick: # No more unique perks left
                break

            random_perk_id = random.choice(available_for_random_pick)
            chosen_perk_ids.add(random_perk_id)

        # Convert set back to list for consistent ordering
        final_perk_ids = list(chosen_perk_ids)
        random.shuffle(final_perk_ids) # Shuffle to randomize display order

        for i, perk_id in enumerate(final_perk_ids):
            perk_info = self.all_perk_definitions[perk_id]
            # Start cards off-screen at the bottom, they will slide up
            initial_y = SCREEN_HEIGHT + i * (self.perk_card_spacing + 50) # Start further down
            target_y = self.perk_card_target_y + i * self.perk_card_spacing
            self.perk_cards.append({
                "id": perk_id,
                "name": perk_info["name"],
                "desc": perk_info["desc"],
                "current_y": initial_y,
                "target_y": target_y,
                "alpha": 255 # Full opacity for cards
            })

    def award_perk_effect(self, perk_id):
        """Adds the selected perk's effect to active perks."""
        if perk_id not in self.active_perks:
            self.active_perks.append(perk_id)
            # Display a confirmation message for the chosen perk
            self.perk_messages.append([f"Perk Acquired: {self.all_perk_definitions[perk_id]['name']}", 255, SCREEN_HEIGHT // 2])
            sound_select.play() # Play a sound when a perk is chosen

    def handle_game_input(self, accepted):
        """Processes player decisions (accept/reject)."""
        money_multiplier = 1
        # Apply all active money multiplier perks
        if "double_money" in self.active_perks:
            money_multiplier *= 2
        if "triple_money" in self.active_perks:
            money_multiplier *= 3
        if "speed_double_money" in self.active_perks:
            money_multiplier *= 2
        if "speed_triple_money" in self.active_perks:
            money_multiplier *= 3
        
        base_reward = 10
        extra_good_service = 50 if "good_service" in self.active_perks else 0
        
        # Check for "money_magnet" perk
        if "money_magnet" in self.active_perks:
            base_reward += 10 # Add 10 bonus money per decision

        # Determine outcome based on player action and umbrella type
        if accepted:
            if self.current_npc["umbrella_type"] == "fake":
                self.player_money -= 5
                self.npc_speech = random.choice(dialogs["accepted_fake"])
                sound_wrong.play()
            else:
                self.player_money += (base_reward * money_multiplier) + extra_good_service
                self.npc_speech = random.choice(dialogs["accepted_real"])
                sound_correct.play()
        else: # Player rejected
            if self.current_npc["umbrella_type"] == "real":
                self.player_money -= 5
                self.npc_speech = random.choice(dialogs["rejected_real"])
                sound_wrong.play()
            else:
                self.player_money += (base_reward // 2 * money_multiplier) + extra_good_service
                self.npc_speech = random.choice(dialogs["rejected_fake"])
                sound_correct.play()

        self.speech_start_time = pygame.time.get_ticks()
        self.interview_count += 1

        # This function just sets up the next NPC.
        self.current_npc = self.generate_npc()
        self.npc_display = NPCDisplay(self.current_npc)
        # No individual NPC timer to reset

    def draw_floating_messages(self):
        """Draws and animates all floating notification messages (general and speed)."""
        for msg_data in self.perk_messages[:]: # Use perk_messages for all floating messages
            msg, alpha, y = msg_data
            text_surf = font.render(msg, True, (255, 255, 0)) # Yellow color for all floating perks
            text_surf.set_alpha(alpha)
            x = SCREEN_WIDTH // 2 - text_surf.get_width() // 2 # Centered for general perks
            
            # Adjust x for speed perk messages to be bottom-left
            if "SPEED DEMON" in msg: # Simple check for speed demon messages
                x = 20 # Bottom-left alignment

            screen.blit(text_surf, (x, y))
            
            # Animate message: move up and fade out
            msg_data[2] -= 1.5 # Move up
            msg_data[1] -= 3 # Fade out
            if msg_data[1] <= 0:
                self.perk_messages.remove(msg_data)

    def draw_round_timer(self):
        """Draws the main timer for the round, counting up."""
        elapsed = pygame.time.get_ticks() - self.round_start_time
        seconds = elapsed // 1000
        millis = (elapsed % 1000) // 100 # Tenths of a second
        # Display elapsed time
        timer_text = font.render(f"Elapsed Time: {seconds}.{millis}s", True, (255, 255, 255))
        screen.blit(timer_text, (SCREEN_WIDTH - timer_text.get_width() - 20, 20))

    def draw_game(self):
        """Draws all elements for the main game screen."""
        screen.fill((30, 30, 30))
        self.npc_display.update()
        self.npc_display.draw(screen)

        # HUD
        screen.blit(font.render(f"Money: ${self.player_money}", True, (255, 255, 255)), (20, 20))
        screen.blit(small_font.render(f"Round: {self.round}/{self.MAX_ROUNDS}", True, (255, 255, 255)), (20, 60))
        # HUD now shows interview goal for the round
        goal_color = (200, 200, 255) if self.interview_count < self.interviews_to_next_perk else (0, 255, 0)
        screen.blit(small_font.render(f"Goal: {self.interview_count} / {self.interviews_to_next_perk}", True, goal_color), (20, 90))

        # Draw the round timer (counting up)
        self.draw_round_timer()

        # Draw speech bubble if active
        current_time = pygame.time.get_ticks()
        if self.npc_speech and current_time - self.speech_start_time < self.SPEECH_DURATION:
            bubble_width, bubble_height = 260, 60
            bubble_x = self.npc_display.card_x + (self.npc_display.card_width - bubble_width) // 2
            bubble_y = self.npc_display.card_y - bubble_height - 20
            pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), (bubble_x, bubble_y, bubble_width, bubble_height), 2, border_radius=10)
            tail_points = [(bubble_x + bubble_width // 2 - 10, bubble_y + bubble_height), (bubble_x + bubble_width // 2 + 10, bubble_y + bubble_height), (bubble_x + bubble_width // 2, bubble_y + bubble_height + 15)]
            pygame.draw.polygon(screen, (255, 255, 255), tail_points)
            pygame.draw.polygon(screen, (0, 0, 0), tail_points, 2)
            
            # Simple text wrapping for the bubble
            words = self.npc_speech.split()
            lines = []
            current_line = ""
            for word in words:
                if small_font.size(current_line + " " + word)[0] < bubble_width - 20:
                    current_line += " " + word
                else:
                    lines.append(current_line.strip())
                    current_line = word
            lines.append(current_line.strip())

            for i, line in enumerate(lines):
                text_surf = small_font.render(line, True, (0, 0, 0))
                screen.blit(text_surf, (bubble_x + 10, bubble_y + 10 + i * 18))

        self.draw_floating_messages() # Consolidated drawing for all floating messages
        pygame.display.flip()

    def draw_perk_selection_screen(self):
        """Draws the perk selection screen with sliding cards."""
        screen.fill((40, 40, 40)) # Darker background for selection screen

        title_text = font.render("Choose Your Perk!", True, (255, 255, 255))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        card_width = 200
        card_height = 450
        start_x = (SCREEN_WIDTH - (card_width * 4 + self.perk_card_spacing * 3)) // 2 # Center the cards

        for i, perk_data in enumerate(self.perk_cards):
            # Animate card sliding up
            if perk_data["current_y"] > perk_data["target_y"]:
                perk_data["current_y"] = max(perk_data["target_y"], perk_data["current_y"] - self.perk_card_slide_speed)

            card_x = start_x + i * (card_width + self.perk_card_spacing)
            card_y = perk_data["current_y"]
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)

            # Draw card background
            bg_color = (80, 80, 80)
            if i == self.selected_perk_index:
                bg_color = (120, 120, 120) # Highlight selected card
            pygame.draw.rect(screen, bg_color, card_rect, border_radius=10)
            pygame.draw.rect(screen, (200, 200, 200), card_rect, 3, border_radius=10) # Border

            # Draw perk name
            name_surf = small_font.render(perk_data["name"], True, (255, 255, 0)) # Yellow for perk names
            name_x = card_x + (card_width - name_surf.get_width()) // 2
            name_y = card_y + 10
            screen.blit(name_surf, (name_x, name_y))

            # Draw perk description (wrapped)
            desc_words = perk_data["desc"].split()
            desc_lines = []
            current_line = ""
            for word in desc_words:
                test_line = current_line + " " + word if current_line else word
                if small_font.size(test_line)[0] < card_width - 20:
                    current_line = test_line
                else:
                    desc_lines.append(current_line)
                    current_line = word
            desc_lines.append(current_line)

            for line_idx, line in enumerate(desc_lines):
                desc_surf = small_font.render(line, True, (200, 200, 200))
                desc_x = card_x + (card_width - desc_surf.get_width()) // 2
                desc_y = name_y + name_surf.get_height() + 5 + line_idx * 16
                screen.blit(desc_surf, (desc_x, desc_y))

        pygame.display.flip()


    def draw_menu(self):
        """Draws the main menu."""
        screen.fill((10, 10, 10))
        title = font.render("DOPPELGANGER", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        options = ["Play", "Instructions", "Credits", "Quit"]
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == self.selected_menu_index else (200, 200, 200)
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 60))
        pygame.display.flip()

    def draw_instructions(self):
        """Draws the instructions screen."""
        screen.fill((20, 20, 20))
        lines = [
            "You're a worker at the fashion company Vague.",
            "Your job is to spot FAKE umbrellas.",
            "Examine the umbrella closely for scratches and imperfections.",
            "",
            "Meet the interview goal before the ROUND TIMER runs out to earn a perk!",
            
            "After 2 rounds, you'll choose a powerful perk!", # Updated instruction
            "",
            "[SPACE] = Accept (Real Umbrella)",
            "[BACKSPACE] = Reject (Fake Umbrella)",
            "[ESC] = Return to Menu",
            "[UP/DOWN/ENTER] = Navigate Perk Selection" # New instruction
        ]
        for i, line in enumerate(lines):
            text = small_font.render(line, True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 100 + i * 40))
        pygame.display.flip()

    def draw_credits(self):
        """Draws the credits screen."""
        screen.fill((0, 0, 0))
        lines = [
            "Created by: ComicBoxComics",
            "Game Logic Modified by Gemini",
            "",
            "Thanks for playing!",
            "",
            "[ESC] to return"
        ]
        for i, line in enumerate(lines):
            text = small_font.render(line, True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 40))
        pygame.display.flip()

    def draw_game_over(self):
        """Draws the game over screen."""
        screen.fill((0, 0, 0))
        title = font.render("Game Over", True, (255, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        money_text = font.render(f"Total Money Earned: ${self.player_money}", True, (255, 255, 0))
        screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 230))
        instructions = small_font.render("Press ENTER to return to menu", True, (180, 180, 180))
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 350))
        pygame.display.flip()

    def run(self):
        """The main game loop."""
        running = True
        while running:
            clock.tick(60)

            # Main game logic is now controlled here in the loop
            if self.state == self.STATE_GAME:
                # Check if the interview goal was met for the round
                if self.interview_count >= self.interviews_to_next_perk:
                    # Calculate time taken to reach the goal
                    elapsed_time_to_goal = pygame.time.get_ticks() - self.round_start_time

                    # Set qualification flag for speed perk for the upcoming selection screen
                    self.ten_second_perk_awarded_this_round = (elapsed_time_to_goal <= 10000)
                    if self.ten_second_perk_awarded_this_round:
                        self.perk_messages.append(["SPEED DEMON QUALIFIED!", 255, SCREEN_HEIGHT - 50]) # Floating message for qualification

                    # Finish the current round (will transition to next round or perk selection)
                    self.finish_round()
                    continue # Skip the rest of this frame to start the new round fresh

                # Next, check if the main round timer has run out.
                elapsed_round_time = pygame.time.get_ticks() - self.round_start_time
                if elapsed_round_time > self.round_time_limit:
                    # Failure! Time's up. No qualification for speed perk.
                    self.ten_second_perk_awarded_this_round = False # Ensure flag is false
                    self.finish_round()
                    continue

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN: # Check for all keydown events here
                    if self.state == self.STATE_MENU:
                        if event.key == pygame.K_UP:
                            self.selected_menu_index = (self.selected_menu_index - 1) % 4
                            sound_menu_move.play()
                        elif event.key == pygame.K_DOWN:
                            self.selected_menu_index = (self.selected_menu_index + 1) % 4
                            sound_menu_move.play()
                        elif event.key == pygame.K_RETURN:
                            sound_select.play()
                            if self.selected_menu_index == 0: # Play
                                self.state = self.STATE_GAME
                                self.round = 1 # Start at round 1
                                self.player_money = 0
                                self.start_new_round()
                            elif self.selected_menu_index == 1: # Instructions
                                self.state = self.STATE_INSTRUCTIONS
                            elif self.selected_menu_index == 2: # Credits
                                self.state = self.STATE_CREDITS
                            elif self.selected_menu_index == 3: # Quit
                                running = False
                    elif self.state == self.STATE_GAME:
                        if event.key == pygame.K_SPACE:
                            self.handle_game_input(True)
                        elif event.key == pygame.K_BACKSPACE:
                            self.handle_game_input(False)
                    elif self.state == self.STATE_PERK_SELECTION: # Handle input for perk selection screen
                        if event.key == pygame.K_UP:
                            self.selected_perk_index = (self.selected_perk_index - 1) % len(self.perk_cards)
                            sound_menu_move.play()
                        elif event.key == pygame.K_DOWN:
                            self.selected_perk_index = (self.selected_perk_index + 1) % len(self.perk_cards)
                            sound_menu_move.play()
                        elif event.key == pygame.K_RETURN:
                            if self.perk_cards: # Ensure there's a perk to select
                                chosen_perk_id = self.perk_cards[self.selected_perk_index]["id"]
                                self.award_perk_effect(chosen_perk_id) # Award the effect
                                self.state = self.STATE_GAME # Go back to game
                                self.start_new_round() # Start the next round
                    elif self.state in (self.STATE_INSTRUCTIONS, self.STATE_CREDITS):
                        if event.key == pygame.K_ESCAPE:
                            self.state = self.STATE_MENU
                    elif self.state == self.STATE_GAME_OVER:
                        if event.key == pygame.K_RETURN:
                            self.state = self.STATE_MENU

            # Drawing states
            if self.state == self.STATE_MENU:
                self.draw_menu()
            elif self.state == self.STATE_GAME:
                self.draw_game()
            elif self.state == self.STATE_INSTRUCTIONS:
                self.draw_instructions()
            elif self.state == self.STATE_CREDITS:
                self.draw_credits()
            elif self.state == self.STATE_GAME_OVER:
                self.draw_game_over()
            elif self.state == self.STATE_PERK_SELECTION: # Draw the new perk selection screen
                self.draw_perk_selection_screen()

if __name__ == '__main__':
    # Ensure you have an 'assets' folder with the required subdirectories
    # (audio, fonts, heads, faces, hair, umbrellas) in the same directory as this script.
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()
