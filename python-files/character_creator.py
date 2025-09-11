import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import random
import uuid
import json
import os

class ScrollableCombobox(ttk.Combobox):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(postcommand=self.show_scrollable_menu)

    def show_scrollable_menu(self):
        if not self['values']:
            return
        menu = tk.Menu(self, tearoff=0)
        for value in self['values']:
            menu.add_command(label=value, command=lambda v=value: self.set(v))
        menu.configure(yscrollcommand=True)
        menu_height = min(len(self['values']), 20) * 20
        x, y = self.winfo_rootx(), self.winfo_rooty() + self.winfo_height()
        menu.configure(height=menu_height)
        menu.post(x, y)

class CharacterCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Character Creator v3.1")
        self.config = {}
        self.character = {}
        self.setup_gui()

    def setup_gui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Configuration Frame
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")

        # Genre (100 options)
        ttk.Label(config_frame, text="Genre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.genre_var = tk.StringVar(value="Fantasy")
        genres = [
            "Fantasy", "Sci-fi", "Realism", "Cyberpunk", "Steampunk", "Horror", "Mystery",
            "Post-apocalyptic", "Historical", "Urban Fantasy", "High Fantasy", "Dark Fantasy",
            "Space Opera", "Dystopian", "Gothic", "Western", "Noir", "Adventure", "Romance",
            "Thriller", "Epic Fantasy", "Science Fantasy", "Magical Realism", "Alternate History",
            "Military Sci-fi", "Psychological Horror", "Sword and Sorcery", "Urban Sci-fi",
            "Historical Fantasy", "Mythic Fiction", "Low Fantasy", "Grimdark", "Cozy Mystery",
            "Hard Sci-fi", "Soft Sci-fi", "Space Western", "Time Travel", "Superhero",
            "Paranormal", "Crime", "Political Thriller", "Romantic Fantasy", "Historical Romance",
            "Steampunk Mystery", "Cyberpunk Noir", "Post-apocalyptic Fantasy", "Urban Horror",
            "Folklore", "Fairy Tale", "Surrealism", "Absurdist", "Satire", "Tragedy",
            "Comedy", "Epic", "Biopunk", "Clockpunk", "Dieselpunk", "Atompunk", "Solarpunk",
            "Mythpunk", "Silkpunk", "Hopepunk", "Grunge Fantasy", "Weird West", "Gaslamp Fantasy",
            "New Weird", "Cosmic Horror", "Dark Comedy", "Romantic Comedy", "Action Adventure",
            "Spy Thriller", "Survival", "Exploration", "Coming-of-Age", "Slice of Life",
            "Psychological Drama", "War", "Espionage", "Heist", "Legal Drama", "Medical Drama",
            "Sports Drama", "Family Saga", "Eco-fiction", "Cli-fi", "Utopian", "Anti-utopian",
            "Techno-thriller", "Gothic Romance", "Sword and Planet", "Planetary Romance",
            "Historical Mystery", "Dark Sci-fi", "Cyberfantasy", "Mythological Sci-fi",
            "Arcanepunk", "Wuxia", "Xianxia", "LitRPG", "GameLit"
        ]
        ttk.Label(config_frame, text=f"({len(genres)} options)").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.genre_combo = ScrollableCombobox(config_frame, textvariable=self.genre_var, values=genres, height=20)
        self.genre_combo.grid(row=0, column=1, padx=5, pady=5)

        # Role (100 options)
        ttk.Label(config_frame, text="Role:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.role_var = tk.StringVar(value="Hero")
        roles = [
            "Hero", "Antagonist", "NPC", "Mentor", "Sidekick", "Anti-hero", "Trickster",
            "Guardian", "Rival", "Wanderer", "Sage", "Outcast", "Rebel", "Leader", "Healer",
            "Explorer", "Scholar", "Warrior", "Thief", "Mage", "Assassin", "Prophet", "Vigilante",
            "Traitor", "Exile", "Survivor", "Merchant", "Diplomat", "Inventor", "Seer",
            "Knight", "Priest", "Shaman", "Bard", "Necromancer", "Alchemist", "Ranger",
            "Paladin", "Sorcerer", "Druid", "Monk", "Warlock", "Cleric", "Rogue", "Barbarian",
            "Scout", "Engineer", "Spy", "Captain", "Oracle", "Beastmaster", "Summoner",
            "Enchanter", "Illusionist", "Chronicler", "Blacksmith", "Navigator", "Tactician",
            "Herald", "Crafter", "Hermit", "Revolutionary", "Martyr", "Bounty Hunter", "Smuggler",
            "Pirate", "Mercenary", "Gladiator", "Philosopher", "Arcanist", "Elementalist",
            "Runesmith", "Shadowmancer", "Stargazer", "Timeweaver", "Dreamwalker", "Soulbinder",
            "Bloodmage", "Stormcaller", "Voidwalker", "Lightbringer", "Darkblade", "Skyforger",
            "Earthshaper", "Fireweaver", "Icebinder", "Starshaper", "Windrider", "Lorekeeper",
            "Pathfinder", "Spellbreaker", "Runecarver", "Ghostspeaker", "Demonhunter", "Angelslayer",
            "Mythweaver", "Doomsayer", "Peaceweaver", "Chaosbringer", "Fatebinder"
        ]
        ttk.Label(config_frame, text=f"({len(roles)} options)").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.role_combo = ScrollableCombobox(config_frame, textvariable=self.role_var, values=roles, height=20)
        self.role_combo.grid(row=1, column=1, padx=5, pady=5)

        # Purpose (100 options)
        ttk.Label(config_frame, text="Purpose:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.purpose_var = tk.StringVar(value="RPG")
        purposes = [
            "Novel", "RPG", "Film", "Short Story", "Theater", "Comic Book", "Video Game",
            "Tabletop Game", "Animation", "Web Series", "Interactive Fiction", "Visual Novel",
            "Audio Drama", "Poetry", "Graphic Novel", "Television Series", "Podcast", "Novella",
            "Anthology", "Campaign Setting", "Board Game", "Card Game", "Mobile Game",
            "VR Experience", "AR Experience", "Short Film", "Feature Film", "Documentary",
            "Experimental Media", "Live Performance", "Radio Play", "Serialized Fiction",
            "Choose-Your-Own-Adventure", "Fan Fiction", "Mythology Collection", "Epic Poem",
            "Fable Collection", "Screenplay", "Stage Play", "Improv Theater", "Motion Comic",
            "Webcomic", "Light Novel", "Interactive Comic", "Audio Book", "Story Podcast",
            "Game Supplement", "Worldbuilding Guide", "Character Study", "Narrative Art",
            "Concept Album", "Themed Anthology", "Serial Drama", "One-Shot RPG", "Campaign Book",
            "Visual Storyboard", "Cinematic Trailer", "Lore Book", "Mythic Chronicle",
            "Historical Reenactment", "Speculative Essay", "Narrative Game Mod", "Adventure Module",
            "Interactive Theater", "Digital Storybook", "Augmented Reality Game", "Escape Room",
            "Puzzle Game", "Narrative Podcast", "Fictional Biography", "Mockumentary",
            "Interactive Web Story", "Themed Exhibition", "Art Installation", "Story-Driven App",
            "Narrative VR Film", "Immersive Experience", "Roleplay Scenario", "Fiction Blog",
            "Narrative Advertisement", "Themed Novelization", "Story-Driven Campaign",
            "Interactive Documentary", "Fictional Journal", "Mythic Saga", "Epic Series",
            "Serialized Comic", "Narrative Audio Series", "Game Narrative Script", "Story Anthology",
            "Interactive Art Project", "Themed Short Film", "Narrative Game DLC", "Story Collection",
            "Cinematic Novel", "Interactive Stage Play", "Themed Performance", "Narrative Experience"
        ]
        ttk.Label(config_frame, text=f"({len(purposes)} options)").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.purpose_combo = ScrollableCombobox(config_frame, textvariable=self.purpose_var, values=purposes, height=20)
        self.purpose_combo.grid(row=2, column=1, padx=5, pady=5)

        # Detail Level (3 options, as per algorithm)
        ttk.Label(config_frame, text="Detail Level:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.detail_var = tk.StringVar(value="Medium")
        detail_levels = ["Low", "Medium", "High"]
        ttk.Label(config_frame, text="(3 options)").grid(row=3, column=2, padx=5, pady=5, sticky="w")
        ttk.Combobox(config_frame, textvariable=self.detail_var, values=detail_levels).grid(row=3, column=1, padx=5, pady=5)

        # Restrictions (100 options)
        ttk.Label(config_frame, text="Restrictions:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.restrictions_var = tk.StringVar(value="None")
        restrictions = [
            "No magic", "No technology", "No violence", "No romance", "No supernatural",
            "No political themes", "No religion", "No modern settings", "No aliens",
            "No time travel", "No shapeshifting", "No undead", "No fantasy creatures",
            "No advanced tech", "No historical figures", "No futuristic settings",
            "No mind control", "No superpowers", "No parallel worlds", "No war",
            "No dystopian themes", "No comedic elements", "No tragic endings",
            "No urban settings", "No rural settings", "No space exploration",
            "No divine intervention", "No steampunk elements", "No cybernetic enhancements",
            "No dragons", "No vampires", "No werewolves", "No ghosts", "No demons",
            "No angels", "No AI characters", "No portals", "No prophecies", "No curses",
            "No blessings", "No resurrection", "No immortality", "No clones",
            "No genetic engineering", "No psionics", "No telepathy", "No teleportation",
            "No invisibility", "No elemental magic", "No necromancy", "No alchemy",
            "No futuristic weapons", "No medieval settings", "No post-apocalyptic settings",
            "No utopian settings", "No dystopian societies", "No secret societies",
            "No conspiracies", "No betrayals", "No revenge arcs", "No redemption arcs",
            "No chosen one tropes", "No mentor figures", "No orphaned protagonists",
            "No royal characters", "No pirate themes", "No ninja themes", "No samurai themes",
            "No knight themes", "No barbarian themes", "No thief guilds", "No magic schools",
            "No tech corporations", "No ancient ruins", "No lost civilizations",
            "No space colonies", "No underwater settings", "No sky cities", "No desert settings",
            "No forest settings", "No mountain settings", "No island settings",
            "No arctic settings", "No jungle settings", "No volcanic settings",
            "No time loops", "No multiverse", "No alternate realities", "No dream worlds",
            "No afterlife settings", "No mythological gods", "No cosmic entities",
            "No interdimensional beings", "No robots", "No cybernetic organisms",
            "No virtual reality", "No augmented reality", "No historical wars",
            "No futuristic rebellions", "No magical artifacts", "Custom"
        ]
        ttk.Label(config_frame, text=f"({len(restrictions)} options)").grid(row=4, column=2, padx=5, pady=5, sticky="w")
        self.restrictions_combo = ScrollableCombobox(config_frame, textvariable=self.restrictions_var, values=restrictions, height=20)
        self.restrictions_combo.grid(row=4, column=1, padx=5, pady=5)

        # Priorities
        ttk.Label(config_frame, text="Psychology Priority (1-10):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.psych_priority_var = tk.StringVar(value="5")
        ttk.Spinbox(config_frame, textvariable=self.psych_priority_var, from_=1, to=10).grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="Skills Priority (1-10):").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.skills_priority_var = tk.StringVar(value="5")
        ttk.Spinbox(config_frame, textvariable=self.skills_priority_var, from_=1, to=10).grid(row=6, column=1, padx=5, pady=5)

        # Demographics Frame
        demo_frame = ttk.Frame(self.notebook)
        self.notebook.add(demo_frame, text="Demographics")

        # Gender (100 options)
        ttk.Label(demo_frame, text="Gender/Identity:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.gender_var = tk.StringVar(value="Non-binary")
        genders = [
            "Male", "Female", "Non-binary", "Genderqueer", "Agender", "Bigender",
            "Genderfluid", "Two-spirit", "Androgynous", "Demigender", "Pangender",
            "Transgender", "Cisgender", "Neutrois", "Genderless", "Demiboy", "Demigirl",
            "Transmasculine", "Transfeminine", "Genderflux", "Polygender", "Trigender",
            "Gender Nonconforming", "Aporagender", "Novigender", "Maverique", "Greygender",
            "Multigender", "Intergender", "Autigender", "Cassgender", "Colorgender",
            "Egender", "Endogender", "Epicene", "Faegender", "Genderfae", "Genderfaun",
            "Genderflor", "Genderlight", "Gendermaverick", "Genderpunk", "Genderqueerflux",
            "Gendersea", "Genderstellar", "Genderwave", "Librafeminine", "Libramasculine",
            "Libragender", "Paragender", "Perigender", "Proxvir", "Juxera", "Xenogender",
            "Aliagender", "Anongender", "Apogender", "Astralgender", "Caelgender",
            "Chaosgender", "Commongender", "Condigender", "Delphigender", "Echogender",
            "Eldergender", "Energender", "Equigender", "Exgender", "Existigender",
            "Fluidflux", "Genderblank", "Genderblur", "Genderfuzz", "Genderglitch",
            "Genderliminal", "Gendermirage", "Genderopaque", "Genderplasma", "Gendersphere",
            "Genderstatic", "Genderstorm", "Gendervague", "Gendervoid", "Genderwitched",
            "Glitchgender", "Hydrogender", "Illusogender", "Impedigender", "Mirrorgender",
            "Neogender", "Neurogender", "Nixgender", "Omnigender", "Quoigender",
            "Stargender", "Vapogender", "Venngender", "Vocigender", "Other"
        ]
        ttk.Label(demo_frame, text=f"({len(genders)} options)").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.gender_combo = ScrollableCombobox(demo_frame, textvariable=self.gender_var, values=genders, height=20)
        self.gender_combo.grid(row=0, column=1, padx=5, pady=5)

        # Orientation (100 options)
        ttk.Label(demo_frame, text="Orientation:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.orientation_var = tk.StringVar(value="Asexual")
        orientations = [
            "Heterosexual", "Homosexual", "Bisexual", "Asexual", "Pansexual", "Demisexual",
            "Queer", "Aromantic", "Polyamorous", "Biromantic", "Panromantic", "Graysexual",
            "Grayromantic", "Androsexual", "Gynesexual", "Skoliosexual", "Acespec",
            "Arospec", "Omnisexual", "Abrosexual", "Monosexual", "Polysexual", "Sapiosexual",
            "Lithosexual", "Fraysexual", "Cupiosexual", "Reciprosexual", "Akiosexual",
            "Autoromantic", "Allosexual", "Alloromantic", "Androromantic", "Gyneromantic",
            "Skolioromantic", "Aegosexual", "Apothisexual", "Autochorissexual",
            "Bellusromantic", "Caedsexual", "Ceterosexual", "Ceteroromantic", "Diamoric",
            "Enbian", "Fictosexual", "Fictoromantic", "Idemromantic", "Inactosexual",
            "Inactoromantic", "Lamvanosexual", "Neuteromantic", "Noetiromantic",
            "Noetisexual", "Novosexual", "Noviromantic", "Platonisexual", "Platonromantic",
            "Proculsexual", "Proculromantic", "Quoisexual", "Quoiromantic", "Requeeromantic",
            "Requeerosexual", "Sansromantic", "Sanssexual", "Sensualarian", "Spectrosexual",
            "Spectroromantic", "Splitattraction", "Tertian", "Vaposexual", "Vaporomantic",
            "Aliquasexual", "Aliquareomantic", "Amplusian", "Angled Aroace", "Apressexual",
            "Arcsexual", "Aspectusromantic", "Autosexual", "Boreasexual", "Caedromantic",
            "Caligosexual", "Cassromantic", "Ceasesexual", "Cessromantic", "Dreadsexual",
            "Dreadromantic", "Duosexual", "Duoromantic", "Egoistsexual", "Egoistromantic",
            "Fluxosexual", "Fluxoromantic", "Hypersexual", "Hyperromantic", "Icularomantic",
            "Iculosexual", "Metaromantic", "Metasexual", "Nebulasexual", "Nebularomantic",
            "Other"
        ]
        ttk.Label(demo_frame, text=f"({len(orientations)} options)").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.orientation_combo = ScrollableCombobox(demo_frame, textvariable=self.orientation_var, values=orientations, height=20)
        self.orientation_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(config_frame, text="Generate Character", command=self.generate_character).grid(row=7, column=0, columnspan=2, pady=20)

    def generate_character(self):
        self.config = {
            "genre": self.genre_var.get(),
            "role": self.role_var.get(),
            "purpose": self.purpose_var.get(),
            "detail": self.detail_var.get(),
            "restrictions": self.restrictions_var.get(),
            "psych_priority": int(self.psych_priority_var.get()),
            "skills_priority": int(self.skills_priority_var.get()),
            "gender": self.gender_var.get(),
            "orientation": self.orientation_var.get()
        }

        # Stage 1: Basic Identifiers
        self.character = {
            "name": self.generate_name(),
            "demographics": self.generate_demographics(),
            "race": self.generate_race(),
            "title": self.generate_title() if self.config["purpose"] == "RPG" else ""
        }

        # Stage 2: Background and Biography
        self.character["background"] = self.generate_background()

        # Stage 3: Appearance
        self.character["appearance"] = self.generate_appearance()

        # Stage 4: Personality
        self.character["personality"] = self.generate_personality()

        # Stage 5: Motivations and Conflicts
        self.character["motivations"] = self.generate_motivations()

        # Stage 6: Relationships
        self.character["relationships"] = self.generate_relationships()

        # Stage 7: Skills
        self.character["skills"] = self.generate_skills()

        self.generate_pdf()
        messagebox.showinfo("Success", "Character generated and saved as character_sheet.pdf")

    def generate_name(self):
        cultures = [
            "European", "Asian", "African", "Latin", "Indian", "Middle Eastern", "Nordic",
            "Slavic", "Polynesian", "Indigenous", "Celtic", "Semitic", "East African",
            "South Asian", "Central Asian", "Southeast Asian", "Pacific Islander", "Caribbean",
            "South American", "Central American"
        ]
        names = {
            "European": ["Elara Thorne", "Liam Blackwood", "Clara Weiss", "Finn O'Connor", "Sofia Bianchi"] * 5,
            "Asian": ["Mei Lin", "Hiro Tanaka", "Aiko Chen", "Ravi Kapoor", "Yuna Park"] * 5,
            "African": ["Aisha Okoye", "Kwame Ndugu", "Zuri Mensah", "Tunde Adebayo", "Nia Kofi"] * 5,
            "Latin": ["Sofia Vargas", "Mateo Cruz", "Luna Morales", "Diego Rivera", "Camila Ortiz"] * 5,
            "Indian": ["Aarav Sharma", "Priya Patel", "Rohan Desai", "Anika Gupta", "Vikram Singh"] * 5,
            "Middle Eastern": ["Layla Hassan", "Omar Khalid", "Zahra Amari", "Amir Reza", "Fatima Nour"] * 5,
            "Nordic": ["Freya Larsen", "Bjorn Eriksson", "Ingrid Olsen", "Sven Magnusson", "Astrid Nilsen"] * 5,
            "Slavic": ["Natasha Volkov", "Dmitri Ivanov", "Olga Petrova", "Viktor Sokolov", "Yana Moroz"] * 5,
            "Polynesian": ["Leilani Koa", "Tane Maui", "Moana Lani", "Kaimana Rangi", "Aloha Nui"] * 5,
            "Indigenous": ["Tala Cherokee", "Koda Navajo", "Winona Lakota", "Talon Apache", "Sequoia Cree"] * 5,
            "Celtic": ["Aisling Murphy", "Declan O’Neil", "Saoirse Kelly", "Cormac Walsh", "Niamh Doyle"] * 5,
            "Semitic": ["Yara Salem", "Elias Haddad", "Mira Abbas", "Samir Khalil", "Noor Jaber"] * 5,
            "East African": ["Fatuma Ali", "Juma Omondi", "Amina Hassan", "Baraka Mwangi", "Zawadi Kweka"] * 5,
            "South Asian": ["Lakshmi Nair", "Arjun Menon", "Sana Khan", "Vishal Reddy", "Meera Joshi"] * 5,
            "Central Asian": ["Aigul Temir", "Ruslan Bek", "Zarina Alim", "Nurlan Tursun", "Gulmira Kadyrova"] * 5,
            "Southeast Asian": ["Nia Sari", "Arief Santoso", "Linh Nguyen", "Sokha Lim", "Dewi Putri"] * 5,
            "Pacific Islander": ["Lani Tui", "Manoa Vaka", "Tala Moana", "Viliami Sefo", "Hina Loto"] * 5,
            "Caribbean": ["Jada Marley", "Kofi Grant", "Talia Beckford", "Malik James", "Zoe Lindo"] * 5,
            "South American": ["Ines Quispe", "Javier Condori", "Lucia Mamani", "Felipe Huanca", "Clara Yupanqui"] * 5,
            "Central American": ["Marisol Castañeda", "Esteban Morales", "Ximena Rojas", "Carlos Pineda", "Ana Tzoc"] * 5
        }
        culture = random.choice(cultures)
        return random.choice(names[culture])

    def generate_demographics(self):
        age_categories = {
            "Childhood": (0, 12), "Youth": (13, 25), "Adulthood": (26, 50), "Elderly": (51, 100)
        }
        category = random.choice(list(age_categories.keys()))
        age_range = age_categories[category]
        age = random.randint(age_range[0], age_range[1])
        return {
            "gender": self.config["gender"],
            "orientation": self.config["orientation"],
            "age": age,
            "age_category": category
        }

    def generate_race(self):
        d20 = random.randint(1, 20)
        race_table = {
            (1, 4): ("Human", "European", "Mutation"),
            (5, 8): ("Elf/Alien", "Asian", "Hybrid"),
            (9, 12): ("Orc/Robot", "African", "Clone"),
            (13, 16): ("Demon/Cyborg", "Latin", "Evolution"),
            (17, 20): ("Fairy/AI", "Indian", "Anomaly")
        }
        for (start, end), value in race_table.items():
            if start <= d20 <= end:
                return {"race": value[0], "culture": value[1], "variation": value[2]}
        return {"race": "Human", "culture": "European", "variation": "None"}

    def generate_title(self):
        titles = [
            "Blade of the Desert", "Star Wanderer", "Shadow Weaver", "Dawnbreaker", "Voidcaller",
            "Iron Sage", "Stormchaser", "Night Warden", "Soulforger", "Eclipse Hunter",
            "Sky Reaver", "Flame Keeper", "Mist Stalker", "Rune Carver", "Starborn",
            "Frost Sentinel", "Abyss Strider", "Dawn Herald", "Twilight Seer", "Blood Reaver",
            "Starforged", "Wind Whisperer", "Ironclad Oracle", "Shadow Sovereign", "Lightbringer",
            "Void Shepherd", "Storm Sovereign", "Rune Warden", "Celestial Blade", "Nightmare Stalker",
            "Ashen Voyager", "Crimson Harbinger", "Ethereal Guardian", "Glimmering Pathfinder",
            "Obsidian Knight", "Radiant Exile", "Spectral Warden", "Astral Nomad", "Duskblade",
            "Ember Prophet", "Galactic Seer", "Lunar Strider", "Solar Enchanter", "Nebula Shaper",
            "Cosmic Weaver", "Starlight Crusader", "Phantom Ranger", "Aurora Sentinel", "Void Dancer",
            "Eclipse Warden", "Dawn Sorcerer", "Twilight Alchemist", "Blood Oracle", "Skyforger",
            "Stormblade", "Frostweaver", "Shadowmancer", "Lightshaper", "Runeseer",
            "Starblade", "Windcarver", "Flamebinder", "Icestalker", "Earthsinger",
            "Soulreaver", "Nightforger", "Daybreaker", "Moonshadow", "Sunstrider",
            "Chaosweaver", "Orderkeeper", "Fateshaper", "Doomherald", "Hopebringer",
            "Skydancer", "Earthbinder", "Firecaller", "Waterweaver", "Airsinger",
            "Lightreaver", "Darkstrider", "Starshatterer", "Voidmender", "Dawncarver",
            "Duskweaver", "Bloodshaper", "Frostbinder", "Stormreaver", "Shadowcarver",
            "Lightwarden", "Nightseeker", "Skysinger", "Earthforger", "Fireshaper",
            "Waterstrider", "Airweaver", "Soulmender", "Starbreaker", "Voidseeker"
        ]
        return random.choice(titles)

    def generate_background(self):
        detail_levels = {"Low": 20, "Medium": 50, "High": 100}
        num_events = detail_levels[self.config["detail"]]
        event_types = [
            "Trauma", "Triumph", "Turning Point", "Reflection", "Discovery", "Loss",
            "Victory", "Betrayal", "Revelation", "Journey", "Sacrifice", "Awakening",
            "Conflict", "Reunion", "Exile", "Transformation", "Initiation", "Quest",
            "Redemption", "Failure"
        ]
        event_descriptions = {
            "Trauma": ["Loss of a loved one", "Surviving disaster", "Personal injury", "Abandonment", "Imprisonment"] * 5,
            "Triumph": ["First major achievement", "Winning a competition", "Overcoming odds", "Earning recognition", "Mastering a skill"] * 5,
            "Turning Point": ["Life-changing decision", "Meeting a mentor", "New path chosen", "Breaking tradition", "Discovering destiny"] * 5,
            "Reflection": ["Moment of self-discovery", "Finding purpose", "Reconciling past", "Accepting flaws", "Embracing truth"] * 5,
            "Discovery": ["Finding a hidden truth", "Uncovering a secret", "New knowledge", "Ancient artifact", "Lost civilization"] * 5,
            "Loss": ["Losing a home", "Friendship ended", "Broken trust", "Lost heirloom", "Fallen ally"] * 5,
            "Victory": ["Defeating a rival", "Saving someone", "Achieving a goal", "Winning a war", "Resolving conflict"] * 5,
            "Betrayal": ["Betrayed by a friend", "Deceived by a leader", "Broken promise", "Sabotaged mission", "False ally"] * 5,
            "Revelation": ["Learning a hidden truth", "Discovering heritage", "Spiritual awakening", "Unveiled prophecy", "Secret identity"] * 5,
            "Journey": ["Long travel", "Exile", "Quest for answers", "Pilgrimage", "Search for home"] * 5,
            "Sacrifice": ["Giving up a dream", "Losing a loved one", "Sacrificing for others", "Abandoning power", "Personal cost"] * 5,
            "Awakening": ["Gaining new power", "Spiritual enlightenment", "Realizing potential", "Breaking a curse", "New perspective"] * 5,
            "Conflict": ["Clash with authority", "Rivalry ignited", "Moral dilemma", "Civil unrest", "Personal vendetta"] * 5,
            "Reunion": ["Reconnecting with family", "Finding a lost friend", "Restoring a bond", "Returning home", "Forgiving an enemy"] * 5,
            "Exile": ["Banished from home", "Forced to flee", "Self-imposed isolation", "Cast out by society", "Lost in unknown lands"] * 5,
            "Transformation": ["Physical change", "Mental shift", "Spiritual rebirth", "New identity", "Power awakening"] * 5,
            "Initiation": ["Joining a group", "Rite of passage", "New role", "Secret society", "Trial success"] * 5,
            "Quest": ["Seeking a relic", "Saving a kingdom", "Finding a person", "Solving a mystery", "Epic journey"] * 5,
            "Redemption": ["Atoning for sins", "Restoring honor", "Making amends", "Forgiving self", "Proving worth"] * 5,
            "Failure": ["Failed mission", "Lost opportunity", "Broken promise", "Defeat in battle", "Personal setback"] * 5
        }
        events = []
        for i in range(min(num_events, 10)):  # Limited for simplicity
            age = random.randint(0, self.character["demographics"]["age"])
            event_type = random.choice(event_types)
            description = random.choice(event_descriptions[event_type])
            events.append({
                "age": age,
                "type": event_type,
                "description": description,
                "impact": random.randint(1, 10)
            })
        return {"family": {"parents": random.randint(1, 3), "siblings": random.randint(0, 4)}, "events": events}

    def generate_appearance(self):
        eyes = random.choice([
            "Blue", "Green", "Brown", "Hazel", "Amber", "Violet", "Glowing", "Heterochromic",
            "Silver", "Golden", "Crimson", "Emerald", "Sapphire", "Onyx", "Opal",
            "Turquoise", "Amethyst", "Ruby", "Jet", "Iridescent", "Clouded", "Starlit",
            "Molten", "Frosted", "Neon", "Crystal", "Shadowed", "Radiant", "Pale", "Deep",
            "Obsidian", "Coral", "Jade", "Topaz", "Pearl", "Smoky", "Copper", "Bronze",
            "Scarlet", "Azure", "Indigo", "Saffron", "Peridot", "Garnet", "Aquamarine",
            "Ochre", "Sienna", "Umber", "Celadon", "Vermilion", "Ebony", "Ivory", "Ashen",
            "Glinting", "Prismatic", "Flickering", "Luminous", "Dappled", "Mirrored",
            "Velvet", "Star-flecked", "Mossy", "Stormy", "Twilight", "Dawnlit", "Dusky",
            "Auroral", "Nebulous", "Glacial", "Fiery", "Mystic", "Ethereal", "Glimmering",
            "Shadow-flecked", "Crystaline", "Opalescent", "Radiating", "Shimmering",
            "Pulsing", "Fading", "Blazing", "Soft-glow", "Moonlit", "Sunlit", "Starless",
            "Void-black", "Sky-blue", "Earth-brown", "Sea-green", "Fire-red", "Mist-grey",
            "Dawn-pink", "Dusk-purple", "Night-blue", "Day-gold", "Eclipse-black",
            "Aurora-green", "Nebula-violet"
        ])
        skin_hair = random.choice([
            "Pale", "Dark", "Holographic", "Tanned", "Freckled", "Metallic", "Scaled",
            "Feathered", "Fur-covered", "Translucent", "Bronzed", "Porcelain", "Ebony",
            "Ivory", "Golden", "Ashen", "Glowing", "Tattooed", "Scarred", "Marbled",
            "Crystalized", "Mottled", "Iridescent", "Chameleonic", "Runed", "Veined",
            "Pearly", "Sooty", "Radiant", "Textured", "Matte", "Glossy", "Satin", "Velvet",
            "Crystalline", "Opalescent", "Prismatic", "Shimmering", "Dappled", "Speckled",
            "Mosaic", "Faceted", "Polished", "Rough", "Woven", "Embossed", "Engraved",
            "Burnished", "Patinaed", "Weathered", "Gilded", "Silvered", "Coppery",
            "Bronze-like", "Stone-like", "Wood-grained", "Glass-like", "Ceramic",
            "Porous", "Lustrous", "Dull", "Reflective", "Translucent", "Opaque",
            "Scintillating", "Flashing", "Flickering", "Pulsing", "Glinting", "Gleaming",
            "Radiating", "Shining", "Sparkling", "Glittering", "Frosted", "Smoky",
            "Clouded", "Misty", "Hazy", "Dewy", "Sleek", "Silken", "Coarse", "Rugged",
            "Craggy", "Smooth", "Rippled", "Wrinkled", "Pitted", "Knotted", "Braided",
            "Twisted", "Curled", "Wavy", "Straight", "Flowing", "Tangled", "Matted",
            "Brilliant", "Vivid"
        ])
        styles = [
            "Rugged", "Elegant", "Futuristic", "Traditional", "Minimalist", "Gothic",
            "Bohemian", "Military", "Cybernetic", "Ceremonial", "Nomadic", "Regal",
            "Peasant", "Arcane", "Steampunk", "Punk", "Victorian", "Tribal", "Urban",
            "Monastic", "Pirate", "Scholarly", "Baroque", "Renaissance", "Avant-garde",
            "Apocalyptic", "Mystical", "Casual", "Formal", "Eclectic", "Retro", "Vintage",
            "Artisan", "Nomad", "Warrior", "Priestly", "Shamanic", "Royal", "Mercantile",
            "Academic", "Adventurer", "Outlaw", "Rebel", "Mystic", "Futurist", "Primitive",
            "Ornate", "Spartan", "Celestial", "Infernal", "Elemental", "Cosmic", "Ethereal",
            "Spectral", "Chthonic", "Arcadian", "Urbanite", "Rural", "Seafaring",
            "Skybound", "Underground", "Desert-worn", "Forest-clad", "Mountain-forged",
            "Arctic", "Jungle-woven", "Volcanic", "Starforged", "Moonlit", "Sun-bleached",
            "Storm-wrought", "Shadow-clad", "Light-woven", "Blood-stained", "Ash-covered",
            "Frost-etched", "Flame-scorched", "Wind-tattered", "Earth-grounded", "Sea-soaked",
            "Sky-painted", "Void-touched", "Dawn-embraced", "Dusk-shrouded", "Night-woven",
            "Day-forged", "Star-stitched", "Nebula-draped", "Aurora-clad", "Eclipse-garbed",
            "Cosmic-threaded", "Mythic-woven", "Rune-etched", "Spirit-bound", "Time-worn"
        ]
        return {"eyes": eyes, "skin_hair": skin_hair, "style": random.choice(styles), "health": "Good"}

    def generate_personality(self):
        big_five = {
            "Extraversion": random.randint(1, 10),
            "Agreeableness": random.randint(1, 10),
            "Conscientiousness": random.randint(1, 10),
            "Neuroticism": random.randint(1, 10),
            "Openness": random.randint(1, 10)
        }
        mbti_types = [
            "INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
            "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"
        ]
        strengths = [
            "Resilient", "Clever", "Compassionate", "Determined", "Creative", "Loyal",
            "Brave", "Witty", "Empathetic", "Resourceful", "Charismatic", "Patient",
            "Honest", "Adaptable", "Perceptive", "Disciplined", "Optimistic", "Courageous",
            "Insightful", "Generous", "Tenacious", "Humble", "Inquisitive", "Reliable",
            "Visionary"
        ]
        weaknesses = [
            "Impulsive", "Stubborn", "Anxious", "Arrogant", "Indecisive", "Reckless",
            "Shy", "Pessimistic", "Obsessive", "Naive", "Skeptical", "Irritable",
            "Vain", "Distrustful", "Overconfident", "Perfectionist", "Aloof", "Cynical",
            "Impulsive", "Procrastinating", "Overcautious", "Gullible", "Reckless",
            "Secretive", "Temperamental"
        ]
        return {
            "big_five": big_five,
            "mbti": random.choice(mbti_types),
            "strengths": random.sample(strengths, 4),
            "weaknesses": random.sample(weaknesses, 4)
        }

    def generate_motivations(self):
        motivations = [
            "Survival", "Revenge", "Discovery", "Power", "Love", "Redemption", "Justice",
            "Freedom", "Knowledge", "Legacy", "Honor", "Fame", "Wealth", "Peace", "Adventure",
            "Truth", "Loyalty", "Revolution", "Balance", "Faith", "Exploration", "Duty",
            "Acceptance", "Vengeance", "Creation", "Protection", "Unity", "Discovery",
            "Immortality", "Reconciliation", "Mastery", "Harmony", "Glory", "Sacrifice",
            "Enlightenment", "Security", "Independence", "Community", "Vindication",
            "Exploration", "Restoration", "Conquest", "Preservation", "Innovation",
            "Retribution", "Devotion", "Understanding", "Ascension", "Survival", "Legacy",
            "Freedom", "Justice", "Power", "Love", "Redemption", "Knowledge", "Honor",
            "Fame", "Wealth", "Peace", "Adventure", "Truth", "Loyalty", "Revolution",
            "Balance", "Faith", "Exploration", "Duty", "Acceptance", "Vengeance", "Creation",
            "Protection", "Unity", "Discovery", "Immortality", "Reconciliation", "Mastery",
            "Harmony", "Glory", "Sacrifice", "Enlightenment", "Security", "Independence",
            "Community", "Vindication", "Exploration", "Restoration", "Conquest",
            "Preservation", "Innovation", "Retribution", "Devotion", "Understanding",
            "Ascension", "Hope", "Transformation", "Purpose", "Resilience"
        ]
        conflicts = [
            "Internal struggle", "External enemy", "Moral dilemma", "Societal pressure",
            "Personal sacrifice", "Betrayal", "Forbidden love", "Quest failure", "Identity crisis",
            "Family feud", "Cultural clash", "Power struggle", "Loss of faith", "Rivalry",
            "Exile", "Redemption arc", "Revenge cycle", "Love triangle", "Duty vs. desire",
            "Freedom vs. control", "Truth vs. loyalty", "Justice vs. mercy", "Self vs. society",
            "Past vs. future", "Faith vs. doubt", "Honor vs. survival", "Love vs. duty",
            "Power vs. responsibility", "Knowledge vs. ignorance", "Unity vs. division",
            "Hope vs. despair", "Change vs. tradition", "Courage vs. fear", "Trust vs. betrayal",
            "Peace vs. conflict"
        ]
        return {
            "motivations": random.sample(motivations, 5),
            "conflicts": random.sample(conflicts, 4)
        }

    def generate_relationships(self):
        relationship_types = [
            "Friend", "Rival", "Mentor", "Family", "Enemy", "Lover", "Ally", "Betrayer",
            "Comrade", "Stranger", "Teacher", "Student", "Leader", "Follower", "Partner",
            "Guardian", "Ward", "Sibling", "Parent", "Child", "Colleague", "Adversary",
            "Confidant", "Protector", "Rival", "Mentee", "Benefactor", "Traitor", "Guide",
            "Outcast", "Healer", "Challenger", "Supporter", "Opposer", "Inspirer",
            "Deceiver", "Savior", "Victim", "Hero", "Villain", "Counselor", "Apprentice",
            "Master", "Servant", "Lord", "Vassal", "Friend-turned-enemy", "Enemy-turned-friend",
            "Rival-turned-ally", "Ally-turned-rival", "Lover-turned-enemy", "Enemy-turned-lover",
            "Mentor-turned-rival", "Rival-turned-mentor", "Family-turned-enemy", "Enemy-turned-family",
            "Comrade-turned-betrayer", "Betrayer-turned-comrade", "Stranger-turned-friend",
            "Friend-turned-stranger", "Teacher-turned-adversary", "Student-turned-leader",
            "Leader-turned-outcast", "Follower-turned-rebel", "Partner-turned-opposer",
            "Guardian-turned-traitor", "Ward-turned-hero", "Sibling-turned-rival",
            "Parent-turned-enemy", "Child-turned-avenger", "Colleague-turned-betrayer",
            "Adversary-turned-ally", "Confidant-turned-deceiver", "Protector-turned-oppressor",
            "Challenger-turned-supporter", "Supporter-turned-opposer", "Inspirer-turned-deceiver",
            "Deceiver-turned-savior", "Savior-turned-villain", "Victim-turned-hero",
            "Hero-turned-villain", "Villain-turned-hero", "Counselor-turned-manipulator",
            "Apprentice-turned-master", "Master-turned-servant", "Servant-turned-lord",
            "Lord-turned-outcast", "Vassal-turned-rebel", "Guide-turned-betrayer",
            "Outcast-turned-leader", "Healer-turned-destroyer", "Destroyer-turned-healer",
            "Avenger-turned-peacemaker", "Peacemaker-turned-warrior", "Seeker-turned-finder",
            "Finder-turned-lost", "Dreamer-turned-realist", "Realist-turned-dreamer"
        ]
        contacts = [
            {"name": self.generate_name(), "type": random.choice(relationship_types), "loyalty": random.randint(1, 10)}
            for _ in range(8)
        ]
        return {"contacts": contacts}

    def generate_skills(self):
        skill_categories = {
            "Combat": [
                "Swordsmanship", "Archery", "Hand-to-hand", "Marksmanship", "Tactics",
                "Dual-wielding", "Shield Mastery", "Stealth Combat", "Guerilla Tactics", "Siege Warfare",
                "Knife Fighting", "Spear Mastery", "Axe Throwing", "Martial Arts", "Fencing",
                "Brawling", "Sniper Training", "Explosives", "Defensive Combat", "Offensive Strategy"
            ],
            "Intellect": [
                "Hacking", "Strategy", "Linguistics", "Engineering", "Medicine",
                "Cryptography", "Astronomy", "Philosophy", "Mathematics", "Archaeology",
                "Physics", "Chemistry", "Biology", "Psychology", "Sociology",
                "History", "Literature", "Economics", "Logic", "Ethics"
            ],
            "Social": [
                "Diplomacy", "Deception", "Leadership", "Persuasion", "Intimidation",
                "Negotiation", "Empathy", "Oratory", "Espionage", "Interrogation",
                "Mediation", "Public Speaking", "Crowd Control", "Charm", "Seduction",
                "Inspiration", "Counseling", "Manipulation", "Networking", "Cultural Awareness"
            ],
            "Craft": [
                "Smithing", "Alchemy", "Tech-building", "Artistry", "Cooking",
                "Tailoring", "Carpentry", "Runecrafting", "Mechanics", "Herbalism",
                "Pottery", "Leatherworking", "Jewelry-making", "Painting", "Sculpting",
                "Weaving", "Glassblowing", "Masonry", "Calligraphy", "Engraving"
            ]
        }
        skills = []
        for category, skill_list in skill_categories.items():
            for skill in random.sample(skill_list, 4):
                skills.append({
                    "category": category,
                    "name": skill,
                    "level": random.randint(1, 10)
                })
        return skills[:8]  # Limit to 8 for simplicity

    def generate_pdf(self):
        doc = SimpleDocTemplate("character_sheet.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Character Sheet", styles['Title']))
        story.append(Spacer(1, 12))

        # Character Data
        data = [
            ["Name", self.character["name"]],
            ["Genre", self.config["genre"]],
            ["Role", self.config["role"]],
            ["Purpose", self.config["purpose"]],
            ["Gender", self.character["demographics"]["gender"]],
            ["Orientation", self.character["demographics"]["orientation"]],
            ["Age", str(self.character["demographics"]["age"])],
            ["Race", self.character["race"]["race"]],
            ["Culture", self.character["race"]["culture"]],
            ["Variation", self.character["race"]["variation"]],
            ["Appearance", f"Eyes: {self.character['appearance']['eyes']}, Skin/Hair: {self.character['appearance']['skin_hair']}, Style: {self.character['appearance']['style']}"],
            ["Personality", f"MBTI: {self.character['personality']['mbti']}, Strengths: {', '.join(self.character['personality']['strengths'])}, Weaknesses: {', '.join(self.character['personality']['weaknesses'])}"],
            ["Motivations", ", ".join(self.character["motivations"]["motivations"])],
            ["Conflicts", ", ".join(self.character["motivations"]["conflicts"])],
            ["Skills", ", ".join([f"{skill['name']} ({skill['level']})" for skill in self.character["skills"]])]
        ]

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)

        # Background Events
        story.append(Spacer(1, 12))
        story.append(Paragraph("Background Events", styles['Heading2']))
        event_data = [["Age", "Type", "Description", "Impact"]]
        for event in self.character["background"]["events"]:
            event_data.append([str(event["age"]), event["type"], event["description"], str(event["impact"])])
        event_table = Table(event_data)
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(event_table)

        # Relationships
        story.append(Spacer(1, 12))
        story.append(Paragraph("Relationships", styles['Heading2']))
        rel_data = [["Name", "Type", "Loyalty"]]
        for contact in self.character["relationships"]["contacts"]:
            rel_data.append([contact["name"], contact["type"], str(contact["loyalty"])])
        rel_table = Table(rel_data)
        rel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(rel_table)

        doc.build(story)

if __name__ == "__main__":
    root = tk.Tk()
    app = CharacterCreator(root)
    root.mainloop()