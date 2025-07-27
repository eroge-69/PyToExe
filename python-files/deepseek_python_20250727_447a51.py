import time
import sys
import json
import os

# Game state management
class GameState:
    def __init__(self):
        self.current_chapter = "start"
        self.inventory = []
        self.stats = {
            "Courage": 5,
            "Wisdom": 5,
            "Power": 5
        }
        self.visited_chapters = set()
        self.decisions = []
        
    def save_game(self, filename="savegame.json"):
        """Save current game state to a file"""
        data = {
            "current_chapter": self.current_chapter,
            "inventory": self.inventory,
            "stats": self.stats,
            "visited_chapters": list(self.visited_chapters),
            "decisions": self.decisions
        }
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True
            
    def load_game(self, filename="savegame.json"):
        """Load game state from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.current_chapter = data["current_chapter"]
            self.inventory = data["inventory"]
            self.stats = data["stats"]
            self.visited_chapters = set(data["visited_chapters"])
            self.decisions = data["decisions"]
            return True
        except:
            return False

# Game functions
def typewriter(text, delay=0.03):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def make_choice(options, state):
    """Present choices and validate input"""
    typewriter("\nWhat will you do?")
    for i, option in enumerate(options, 1):
        typewriter(f"{i}. {option}")
    
    while True:
        choice = input("\nEnter your choice (1-4): ")
        if choice in ['1', '2', '3', '4']:
            state.decisions.append((state.current_chapter, int(choice)))
            return int(choice)
        elif choice.lower() == 'save':
            if state.save_game():
                typewriter("Game saved successfully!")
            else:
                typewriter("Save failed!")
        elif choice.lower() == 'load':
            if state.load_game():
                typewriter("Game loaded successfully!")
                return "load"
            else:
                typewriter("Load failed!")
        elif choice.lower() == 'inv':
            show_inventory(state)
        elif choice.lower() == 'stats':
            show_stats(state)
        else:
            typewriter("Invalid choice! Please enter 1-4 or type 'save', 'load', 'inv', or 'stats'")

def show_inventory(state):
    """Display player's inventory"""
    if not state.inventory:
        typewriter("\nYour inventory is empty.")
    else:
        typewriter("\nINVENTORY:")
        for item in state.inventory:
            typewriter(f"- {item}")
    return True

def show_stats(state):
    """Display character stats"""
    typewriter("\nCHARACTER STATS:")
    for stat, value in state.stats.items():
        typewriter(f"{stat}: {value}/10")

def stat_check(stat, difficulty, state):
    """Check if player succeeds at a stat-based challenge"""
    value = state.stats[stat]
    roll = value + random.randint(1, 6)  # Add some randomness
    
    typewriter(f"\n{stat} check: {value} + roll vs {difficulty}")
    if roll >= difficulty:
        typewriter("Success!")
        return True
    else:
        typewriter("Failure!")
        return False

def modify_stat(stat, amount, state):
    """Modify a character stat with bounds checking"""
    state.stats[stat] = max(1, min(10, state.stats[stat] + amount))
    typewriter(f"\n{stat} {'increased' if amount > 0 else 'decreased'} to {state.stats[stat]}!")

# ========================
# CHAPTER 1: THE AWAKENING
# ========================
def chapter_1(state):
    state.current_chapter = "chapter_1"
    state.visited_chapters.add("chapter_1")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 1: THE AWAKENING")
    typewriter("="*50)
    
    typewriter("\nYou awaken in a dimly lit stone chamber. Dust dances in the shafts of moonlight")
    typewriter("streaming through cracks in the ancient walls. The air smells of damp earth and")
    typewriter("something else... something metallic. Your head throbs as fragmented memories")
    typewriter("surface: a violent storm, blinding light, then darkness.")
    
    typewriter("\nAs your eyes adjust, you notice:")
    typewriter("- A flickering torch in a rusted sconce")
    typewriter("- Strange glowing runes on the far wall")
    typewriter("- A heavy wooden door with an iron latch")
    typewriter("- Your own hands, covered in unfamiliar tattoos")
    
    choices = [
        "Approach the glowing runes",
        "Take the torch from the wall",
        "Examine the mysterious tattoos",
        "Try to open the door"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nAs you touch the runes, they flare with blue energy! Knowledge floods your mind:")
        typewriter("- You're in the Temple of the Forgotten Moon")
        typewriter("- An ancient evil has awakened")
        typewriter("- You bear the Mark of the Starborn")
        typewriter("\nThe door creaks open of its own accord...")
        state.inventory.append("Runic Knowledge")
        modify_stat("Wisdom", 1, state)
        return chapter_2a(state)
    elif choice == 2:
        typewriter("\nThe torch comes loose with a shower of sparks. As you hold it aloft,")
        typewriter("shadows dance revealing hidden carvings: a serpent coiled around a tower.")
        typewriter("The door's lock mechanism becomes visible - it seems jammed with debris.")
        state.inventory.append("Torch")
        modify_stat("Courage", 1, state)
        return chapter_2b(state)
    elif choice == 3:
        typewriter("\nThe tattoos shimmer as you focus. Suddenly, you can see magical energy!")
        typewriter("The runes glow with protective magic, the door radiates dark energy,")
        typewriter("and your own hands pulse with untapped power. You sense a presence behind the door...")
        state.inventory.append("Tattoo Insight")
        modify_stat("Power", 1, state)
        return chapter_2c(state)
    else:
        typewriter("\nThe heavy door groans open to reveal a moonlit courtyard in ruins.")
        typewriter("Before you stands a hooded figure, face hidden in shadow. 'You're late,'")
        typewriter("a raspy voice whispers. 'The Voidspawn already stirs beneath the Black Spire.'")
        modify_stat("Courage", 2, state)
        return chapter_2d(state)

# ========================
# CHAPTER 2: PATHWAYS
# ========================
def chapter_2a(state):
    state.current_chapter = "chapter_2a"
    state.visited_chapters.add("chapter_2a")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 2: THE CRYPT OF WHISPERS")
    typewriter("="*50)
    
    typewriter("\nBeyond the door lies a vast crypt filled with floating wisps of blue light.")
    typewriter("Ancient sarcophagi line the walls, carved with images of winged warriors.")
    typewriter("The air hums with energy as ghostly voices whisper warnings:")
    typewriter("\n'Beware the Shattered King...' 'The Key of Stars is your only hope...'")
    
    choices = [
        "Follow the brightest wisps",
        "Examine the warrior carvings",
        "Try to communicate with the whispers",
        "Search for hidden passages"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nThe wisps lead you to a stone dais holding a crystalline orb. As you touch it,")
        typewriter("visions assault you: a city in flames, a tower piercing the sky, and a dark")
        typewriter("presence laughing from the void. The orb cracks and dark energy swirls around you!")
        state.inventory.append("Cracked Orb")
        return chapter_3a(state)
    elif choice == 2:
        typewriter("\nThe carvings depict an epic battle against shadow creatures. One warrior holds")
        typewriter("a blazing sword that looks identical to your tattoo! You notice his shield bears")
        typewriter("a sigil matching a depression in the wall. When you press it, a hidden chamber opens.")
        state.inventory.append("Warrior's Sigil")
        return chapter_3b(state)
    elif choice == 3:
        typewriter("\nFocusing your will, you project thoughts: 'Who are you? What danger approaches?'")
        typewriter("The voices coalesce into a spectral knight. 'I am Alaric, last guardian of the")
        typewriter("Temple. The Shattered King returns! Only the Starforged Blade can stop him.'")
        state.inventory.append("Ghostly Ally")
        return chapter_3c(state)
    else:
        typewriter("\nYour search reveals a loose stone. Behind it lies a silver compass that glows")
        typewriter("with inner light. The needle points insistently northwest as ghostly voices warn:")
        typewriter("'Hurry! Before the eclipse is complete!'")
        state.inventory.append("Star Compass")
        return chapter_3d(state)

def chapter_2b(state):
    state.current_chapter = "chapter_2b"
    state.visited_chapters.add("chapter_2b")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 2: THE CHARRED CORRIDOR")
    typewriter("="*50)
    
    typewriter("\nThe torchlight reveals a long corridor scarred by fire. Skeletons in rusted armor")
    typewriter("lie broken against walls covered in claw marks. The air grows hotter as you proceed,")
    typewriter("and distant roars echo through the stone halls. Suddenly, the ground trembles!")
    
    choices = [
        "Run toward the roars",
        "Hide in a side alcove",
        "Investigate the skeletons",
        "Extinguish the torch and listen"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nYou charge forward into a massive chamber where a lava river flows. On an island")
        typewriter("in the center, a juvenile magma dragon gnaws on a carcass. It hasn't noticed you...")
        return chapter_3e(state)
    elif choice == 2:
        typewriter("\nYou squeeze into a narrow alcove as the tremors intensify. Through the dust,")
        typewriter("you see massive stone golems stomping past! One pauses, its crystal eye scanning")
        typewriter("near your hiding place...")
        return chapter_3f(state)
    elif choice == 3:
        typewriter("\nOne skeleton clutches a journal. The last entry reads: 'The earth shakes as")
        typewriter("the Spawn drills toward the surface. Only silverfire hurts them. May the Light")
        typewriter("forgive us for awakening the Crystal Heart.' A silver pendant falls from the pages.")
        state.inventory.append("Silver Pendant")
        modify_stat("Wisdom", 1, state)
        return chapter_3g(state)
    else:
        typewriter("\nIn darkness, your other senses sharpen. You hear skittering from multiple")
        typewriter("directions and deep breathing above you. Looking up, you see massive bat-like")
        typewriter("creatures clinging to the ceiling! One begins to stir...")
        return chapter_3h(state)

def chapter_2c(state):
    state.current_chapter = "chapter_2c"
    state.visited_chapters.add("chapter_2c")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 2: THE VEILED LIBRARY")
    typewriter("="*50)
    
    typewriter("\nYou enter an enormous library where books float in midair. Starlight filters through")
    typewriter("a shattered dome ceiling. As you walk, books rearrange themselves. One slams open")
    typewriter("before you, pages rapidly flipping to show an illustration of your tattoo!")
    
    choices = [
        "Read the open book",
        "Ask the library about the tattoo",
        "Search for books on the Voidspawn",
        "Try to repair the ceiling"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nThe book reveals you're a Starborn - chosen to wield cosmic magic. The tattoos")
        typewriter("are Celestial Script containing spells. To awaken them, you must 'drink starlight'")
        typewriter("and face your deepest fear. A beam of moonlight suddenly focuses on you...")
        modify_stat("Power", 2, state)
        return chapter_3i(state)
    elif choice == 2:
        typewriter("\nYou shout your question. All books snap shut except three that zoom toward you:")
        typewriter("- 'The Book of Bound Stars' pulses with blue energy")
        typewriter("- 'Chronicles of the Shattered King' leaks black smoke")
        typewriter("- 'The Last Starborn's Diary' glows with your tattoo pattern")
        return chapter_3j(state)
    elif choice == 3:
        typewriter("\nBooks about dark entities swirl around you. One shows the Voidspawn - a cosmic")
        typewriter("horror that consumes realities. Another reveals its prison is weakening because")
        typewriter("the Three Pillars of Light have been corrupted! The books then form a bridge upward.")
        modify_stat("Wisdom", 2, state)
        return chapter_3k(state)
    else:
        typewriter("\nFocusing your will, you gesture at the broken dome. Shards of glass reassemble")
        typewriter("into a star map! Constellations shift to form your tattoo pattern. A hidden")
        typewriter("balcony descends, holding an ornate telescope pointed at a dying star...")
        state.inventory.append("Star Map")
        return chapter_3l(state)

def chapter_2d(state):
    state.current_chapter = "chapter_2d"
    state.visited_chapters.add("chapter_2d")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 2: THE MOONLIGHT COVENANT")
    typewriter("="*50)
    
    typewriter("\nThe hooded figure leads you through ruins to a circle of standing stones. Thirteen")
    typewriter("cloaked figures chant around a stone altar where moonlight forms a shimmering portal.")
    typewriter("'We are the Keepers,' your guide explains. 'We've preserved the temple until a Starborn")
    typewriter("could return. The eclipse approaches. You must choose your path to the Black Spire.'")
    
    choices = [
        "Step through the moon portal",
        "Demand more information first",
        "Ask to meet their leader",
        "Inspect the standing stones"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nYou leap through the portal! Energy tears at your being as you tumble through")
        typewriter("cosmic pathways. You land hard in an alien forest where trees have crystalline")
        typewriter("leaves. The Black Spire looms in the distance, pulsing with dark energy...")
        return chapter_3m(state)
    elif choice == 2:
        typewriter("\n'Very well,' sighs your guide. 'Long ago, the First Starborn imprisoned the")
        typewriter("Voidspawn using the Key of Stars. Now the Key is lost and the prison fails. Three")
        typewriter("artifacts remain that might help: the Starforged Blade, the Eclipse Amulet, and...'")
        state.inventory.append("Keeper's Knowledge")
        return chapter_3n(state)
    elif choice == 3:
        typewriter("\nThe chanters part as an ancient woman approaches. Her eyes glow white. 'I am")
        typewriter("Elara, last of the High Keepers. Your coming was foretold, but time grows short.")
        typewriter("Take this.' She offers a moonstone dagger. 'Blood of the Starborn must awaken the...'")
        state.inventory.append("Moonstone Dagger")
        return chapter_3o(state)
    else:
        typewriter("\nThe stones are covered in intricate carvings showing celestial events. One stone")
        typewriter("depicts the upcoming eclipse. Another shows three artifacts converging at a tower.")
        typewriter("When you touch it, your tattoo flares and the carvings rearrange to show a secret path!")
        state.inventory.append("Celestial Map")
        return chapter_3p(state)

# ========================
# CHAPTER 3: CONVERGENCE
# ========================
def chapter_3a(state):
    state.current_chapter = "chapter_3a"
    state.visited_chapters.add("chapter_3a")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 3: THE SHADOW SEED")
    typewriter("="*50)
    
    typewriter("\nDark energy forms into shadowy tendrils that lash at you! The tattoos on your arms")
    typewriter("glow brightly as instinct takes over. You realize you can manipulate the energy!")
    
    choices = [
        "Absorb the dark energy",
        "Fight back with light",
        "Try to contain the energy",
        "Flee back through the door"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nYou draw the shadows into yourself! Pain gives way to incredible power as")
        typewriter("new tattoos spread across your skin. A dark voice whispers: 'Embrace the void...'")
        typewriter("You've gained power but at what cost? The path to corruption begins...")
        state.inventory.append("Shadow Seed")
        modify_stat("Power", 3, state)
        modify_stat("Wisdom", -2, state)
        return chapter_4a(state)
    elif choice == 2:
        typewriter("\nBlinding light erupts from your hands, vaporizing the shadows! The cracked orb")
        typewriter("reforms into a perfect sphere showing a map to the Starforged Blade!")
        state.inventory.append("Stellar Map")
        return chapter_4b(state)
    elif choice == 3:
        typewriter("\nYou weave the energy into a protective sphere around the orb. It stabilizes and")
        typewriter("floats gently, projecting images of the three artifact locations. The wisps form")
        typewriter("into a protective escort around you.")
        state.inventory.append("Stabilized Orb")
        return chapter_4c(state)
    else:
        typewriter("\nYou barely escape as the chamber collapses behind you. Back in the crypt, the")
        typewriter("ghosts wail in despair. 'Fool! You've released the Shadow Seed! The end comes...'")
        return bad_ending(state)

def chapter_3b(state):
    state.current_chapter = "chapter_3b"
    state.visited_chapters.add("chapter_3b")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 3: THE STARFORGE")
    typewriter("="*50)
    
    typewriter("\nThe hidden chamber reveals an ancient starmetal forge. Blue flames dance")
    typewriter("around a sword-shaped mold. Ghostly blacksmiths await your command.")
    typewriter("\n'Only starlight and sacrifice can rekindle the Starforge,' echoes a voice.")
    
    choices = [
        "Offer your blood to the flames",
        "Channel cosmic energy through your tattoos",
        "Search for celestial ingredients",
        "Attempt to force the mechanism"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nYour blood makes the flames roar crimson! The sword forms but drinks")
        typewriter("your life force. A dark voice whispers: 'The Bloodedge is born...'")
        state.inventory.append("Bloodedge Sword")
        modify_stat("Power", 2, state)
        modify_stat("Courage", -1, state)
        return chapter_4d(state)
    elif choice == 2:
        typewriter("\nStarlight streams through the ceiling as your tattoos blaze!")
        typewriter("The forge awakens, crafting a blade of pure moonlight. 'The Starforged")
        typewriter("Blade returns!' cheers the spectral smiths.")
        state.inventory.append("Starforged Blade")
        return chapter_4e(state)
    elif choice == 3:
        typewriter("\nYou find moonpetals and comet dust. The ghost-smiths nod approvingly")
        typewriter("and craft a balanced blade - powerful but not overwhelming.")
        state.inventory.append("Moonlit Blade")
        return chapter_4f(state)
    else:
        typewriter("\nThe mechanism jams and collapses! Celestial fire rages out of")
        typewriter("control, consuming you and the ancient forge...")
        return bad_ending(state)

def chapter_3c(state):
    state.current_chapter = "chapter_3c"
    state.visited_chapters.add("chapter_3c")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 3: THE SPECTRAL ALLY")
    typewriter("="*50)
    
    typewriter("\nThe spectral knight Alaric bows before you. 'Starborn, the temple's defenses")
    typewriter("are failing. We must reach the Astral Observatory before the eclipse peaks.")
    typewriter("Two paths remain: the Crystal Bridge or the Whispering Catacombs.'")
    
    choices = [
        "Take the Crystal Bridge",
        "Venture into the Catacombs",
        "Ask Alaric to teach you combat",
        "Request knowledge of the Voidspawn"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nThe bridge glows with rainbow light as you cross a bottomless chasm.")
        typewriter("Halfway across, shadow creatures emerge from the abyss! Alaric raises")
        typewriter("his spectral sword: 'Stand behind me!'")
        return chapter_4g(state)
    elif choice == 2:
        typewriter("\nThe catacombs are filled with the bones of ancient Starborn. As you walk,")
        typewriter("ghostly hands reach from the walls. Alaric's presence keeps them at bay.")
        typewriter("At the end lies a chamber pulsing with dark energy...")
        return chapter_4h(state)
    elif choice == 3:
        typewriter("\nAlaric teaches you ancient combat techniques. Your movements become fluid,")
        typewriter("instinctive. 'Remember this stance when facing the Shadowguard,' he advises.")
        modify_stat("Courage", 3, state)
        return chapter_4i(state)
    else:
        typewriter("\nAlaric shares terrible knowledge: 'The Voidspawn is not a single entity,")
        typewriter("but a hive mind. Its true form exists between dimensions. Only cosmic")
        typewriter("magic can banish it.' Your mind reels with this revelation.")
        modify_stat("Wisdom", 3, state)
        return chapter_4j(state)

# Additional chapter_3 functions would follow the same pattern...

# ========================
# CHAPTER 4: ASCENSION
# ========================
def chapter_4a(state):
    state.current_chapter = "chapter_4a"
    state.visited_chapters.add("chapter_4a")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 4: THE CORRUPTED STAR")
    typewriter("="*50)
    
    typewriter("\nThe Shadow Seed pulses within you as you approach the Black Spire. The Keepers")
    typewriter("recognize your corrupted power and attack! Dark energy flows through you...")
    
    choices = [
        "Embrace the darkness fully",
        "Fight the corruption within",
        "Use the power but resist its influence",
        "Seek purification in the Spire's core"
    ]
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        typewriter("\nYou unleash the Shadow Seed's full power! Keepers fall before you as")
        typewriter("you ascend the Spire. The Voidspawn kneels before its new master...")
        return dark_ending(state)
    elif choice == 2:
        typewriter("\nA titanic struggle rages within you. Light and dark energies clash as")
        typewriter("you fight for your soul. The Keepers watch in awe as a new equilibrium forms...")
        return balanced_ending(state)
    elif choice == 3:
        typewriter("\nYou walk a razor's edge - using the darkness but maintaining control.")
        typewriter("The Voidspawn hesitates, sensing both threat and kinship. This is your chance...")
        return twilight_ending(state)
    else:
        typewriter("\nAt the Spire's heart, you plunge yourself into pure starlight! The pain")
        typewriter("is excruciating as the darkness burns away. When you emerge, you're changed...")
        return purified_ending(state)

def chapter_4b(state):
    state.current_chapter = "chapter_4b"
    state.visited_chapters.add("chapter_4b")
    
    typewriter("\n" + "="*50)
    typewriter("CHAPTER 4: THE BLADE'S CALL")
    typewriter("="*50)
    
    typewriter("\nFollowing the Stellar Map, you arrive at a floating island where the legendary")
    typewriter("Starforged Blade rests in a pillar of light. Ancient guardians stand watch.")
    
    if "Ghostly Ally" in state.inventory:
        typewriter("\nAlaric appears beside you: 'I will distract them! Claim the blade!'")
    
    choices = [
        "Charge straight for the blade",
        "Find a stealthy approach",
        "Parley with the guardians",
        "Create a diversion"
    ] + (["Use Ghostly Ally"] if "Ghostly Ally" in state.inventory else [])
    
    choice = make_choice(choices, state)
    if choice == "load":
        return state.current_chapter
    
    if choice == 1:
        if stat_check("Courage", 8, state):
            typewriter("\nYou dodge the guardians' strikes and grasp the Blade! Cosmic power")
            typewriter("surges through you as the sword recognizes its Starborn master.")
            state.inventory.append("Starforged Blade")
            return hero_ending(state)
        else:
            typewriter("\nThe guardians intercept you! Their ancient weapons pierce your defenses")
            typewriter("as you're thrown from the platform into the abyss below...")
            return bad_ending(state)
    elif choice == 2:
        typewriter("\nYou circle around, using fallen pillars as cover. Just as you reach the blade,")
        typewriter("the head guardian blocks your path! 'Prove your worth, Starborn!'")
        return trial_ending(state)
    elif choice == 3:
        typewriter("\n'Why should we trust a mortal?' the lead guardian booms. 'The last Starborn")
        typewriter("failed us!' You must convince them of your worth...")
        if stat_check("Wisdom", 7, state):
            typewriter("\nYour words reach them. 'Perhaps hope remains... Take the blade and go.'")
            state.inventory.append("Starforged Blade")
            return hero_ending(state)
        else:
            typewriter("\nThey shake their heads. 'You lack the wisdom needed. Begone!'")
            return bad_ending(state)
    elif choice == 4:
        typewriter("\nYou hurl a rock to the far side of the platform. As guardians investigate,")
        typewriter("you make your move...")
        if stat_check("Power", 6, state):
            typewriter("\nYou grab the blade just as they turn back! Power floods you as you teleport away.")
            state.inventory.append("Starforged Blade")
            return hero_ending(state)
        else:
            typewriter("\nThey were expecting a trick! You're surrounded before you get close.")
            return bad_ending(state)
    elif choice == 5:  # Use Ghostly Ally
        typewriter("\nAlaric materializes, shouting challenges. As all guardians focus on him,")
        typewriter("you easily claim the blade! He fades with a satisfied smile.")
        state.inventory.append("Starforged Blade")
        return hero_ending(state)

# Additional chapter_4 functions would follow...

# =================
# ENDINGS
# =================
def dark_ending(state):
    typewriter("\n\n" + "="*50)
    typewriter("ENDING: VOID'S EMBRACE")
    typewriter("="*50)
    typewriter("\nWith each passing hour, the dark power grows. You crush the Voidspawn")
    typewriter("only to take its place. As the eclipse reaches totality, you ascend the")
    typewriter("Black Spire not as savior, but as the new Shadow Sovereign. The world")
    typewriter("kneels before its dark star... for now.")
    game_over(state)

def hero_ending(state):
    typewriter("\n\n" + "="*50)
    typewriter("ENDING: DAWN OF THE STARBORN")
    typewriter("="*50)
    typewriter("\nThe Starforged Blade blazes in your hands as you strike the final blow!")
    typewriter("The Voidspawn shrieks as it's banished to the cosmic void. As the first")
    typewriter("sunlight breaks the eclipse, the people cheer their savior. But high in")
    typewriter("the tower, you see new stars falling - and they look like eyes...")
    game_over(state)

def balanced_ending(state):
    typewriter("\n\n" + "="*50)
    typewriter("ENDING: THE THIRD PATH")
    typewriter("="*50)
    typewriter("\nUsing all three artifacts, you don't destroy the Voidspawn - you transform")
    typewriter("it! Cosmic energy reshapes the entity into a newborn star. The Keepers")
    typewriter("establish a new covenant to maintain balance between light and shadow.")
    typewriter("As the first Starborn Guardian, you watch over the eternal twilight...")
    game_over(state)

def twilight_ending(state):
    typewriter("\n\n" + "="*50)
    typewriter("ENDING: TWILIGHT SOVEREIGN")
    typewriter("="*50)
    typewriter("\nYou establish a delicate balance - containing the Voidspawn within")
    typewriter("yourself. The world exists in perpetual twilight, protected by your")
    typewriter("sacrifice. Neither fully human nor entirely cosmic, you become the")
    typewriter("eternal guardian of the balance, feared and revered in equal measure.")
    game_over(state)

def bad_ending(state):
    typewriter("\n\n" + "="*50)
    typewriter("ENDING: ECLIPSE OF HOPE")
    typewriter("="*50)
    typewriter("\nAs the eclipse reaches totality, the Voidspawn emerges. Reality unravels")
    typewriter("as the creature feasts on the world's magic. The last thing you see is the")
    typewriter("dying light of stars before endless darkness consumes everything...")
    game_over(state)

def game_over(state):
    typewriter("\n\nYOUR JOURNEY ENDS")
    typewriter(f"Visited locations: {len(state.visited_chapters)}")
    typewriter(f"Final inventory: {', '.join(state.inventory)}")
    typewriter("\nStats:")
    for stat, value in state.stats.items():
        typewriter(f"{stat}: {value}")
    
    typewriter("\n\nWould you like to play again?")
    choice = input("(y/n): ").lower()
    if choice == 'y':
        state = GameState()
        start_game(state)
    else:
        typewriter("\nThank you for playing!")
        sys.exit()

# =================
# START THE GAME
# =================
def start_game(state=None):
    if not state:
        state = GameState()
    
    typewriter("\n" + "="*50)
    typewriter("SHADOWS OF THE SHATTERED KING")
    typewriter("="*50)
    typewriter("\nA Text-Based Fantasy Adventure")
    typewriter("Your choices shape your destiny...")
    typewriter("\nSpecial commands: 'save', 'load', 'inv', 'stats'")
    
    # Check for existing save
    if os.path.exists("savegame.json"):
        typewriter("\nA saved game was detected. Would you like to load it?")
        if input("(y/n): ").lower() == 'y':
            if state.load_game():
                typewriter("Game loaded successfully!")
            else:
                typewriter("Load failed! Starting new game.")
    
    chapter_1(state)

if __name__ == "__main__":
    import random
    start_game()