import tkinter as tk
from tkinter import ttk, messagebox, font
import os
import re
import random
import sys
import threading
import queue
import datetime

# --- CONFIGURATION ---
# The complete list of characters provided by the user.
CHARACTER_LIST = [
    "Ryu", "Ken", "Terry", "Kyo", "Guile", "Joe", "Andy", "Adon", "Akuma", "Alex", "Balrog", "Birdie",
    "Blanka", "Charlie", "Chun-Li", "Cody", "Dan", "Decapre", "Dhalsim", "DivineEliza", "DivineJuli",
    "DivineSkullo", "Dudley", "Eagle", "Evil Ryu", "Fei-Long", "Gen", "Gill", "Gouken", "Guy", "Hugo",
    "Ibuki", "Ingrid", "Juri", "Karin", "MBison", "Makoto", "Mech Zangief", "Mike Haggar", "Necro",
    "Oro", "Q", "R. Mika", "Remy", "Rolento", "Rose", "Sagat", "Sakura", "Sean", "Seth", "ShadowLady",
    "Sodom", "T.Hawk", "Twelve", "Urien", "Vega", "Yang", "Yun", "Zangief", "cvsMarz", "elena",
    "poison", "Adelheid", "Alice", "Angel", "Ash", "Athena", "B.Jenet", "Benimaru", "BlueMary",
    "CVS_Hibiki", "Chang", "Clark", "Daimon", "Duo Lon", "Geese", "Goenitz", "Grant", "Griffon",
    "Heidern", "Hinako", "Iori", "Jimmy-POTS", "Kdash", "Kim", "King", "Kula", "Kusanagi", "Leona",
    "Mai", "Marco", "Mature", "Maxima", "Mr.Karate", "NeoGeegus", "Original_Zero", "Orochi Iori",
    "Raiden", "Ralf", "Robert", "Rock", "Rugal", "Ryo", "Shermie", "Shingo", "Takuma", "TungCVS",
    "Vanessa", "Vice", "Yamazaki", "Yashiro", "Yuri", "cvssilber", "BBHood", "Bishamon", "Demitri",
    "Donovan", "Felicia", "Jedah", "Jon Talbain", "Lilith", "Queen Bee", "Sasquatch", "Huitzil",
    "ChamCham", "Genjuro", "Haohmaru", "Jubei", "Rasetsumaru", "Ukyo-POTS", "Warachia", "irohapots",
    "Jin", "Kazuya", "Lee", "Nina", "Paul", "Akira Kazama", "Batsu", "Hinata", "Kyosuke", "AkiraYuki",
    "Akito_CVS", "Andrew", "Angela", "Axel Stone", "Blaze", "CVS_Jill", "Cable", "Chonshu", "Cyclops",
    "DIO", "DivinePsy", "Foxy", "Fuuma", "Gai", "Gambit", "Hayate", "Heavy D!", "Hol Horse", "Hon Fu",
    "Jet[Cafe]", "Jin Saotome", "JoeSF", "Jotaro", "Kaede", "Kasumi", "Kenji", "Kensou",
    "Kisarah-POTS", "Kohaku_K", "Krizalid", "Kuroko", "LiXiangfei", "Lynn", "Maki", "Malin", "Megaman",
    "Oni", "Oswald", "RajaaAmingo", "RajaaAoko", "RajaaArcueid", "RajaaLen", "RajaaMech-Hisui",
    "RajaaMiyako", "RajaaRiesbyfe", "RajaaRoa", "RajaaSatsuki", "RajaaSion", "Ryunmei Ranka",
    "Scorpion", "Shen_Woo", "ShikiT", "Squall", "SubZero", "Thirteen", "Tiffany", "Todoh",
    "WWStrowd", "Whip", "Wong", "Yuki", "Zero", "cvshotaru", "cvsmina", "Mars People", "Morrigan",
    "DaRk=Morrigan_Second", "Anakaris", "Leo", "Roll", "Sonson_SE", "pyron", "Juggernaut", "Colossus",
    "Capcom", "Marrow", "OmegaRed", "Thanos", "Wolverine", "War Machine", "Hulk", "Venom",
    "Spiderman", "Ironman", "CFJ_Oni", "Dee Jay", "Juni", "Tessa", "Rikuo", "Lord Raptor",
    "Devilotte", "Haruhi Suzumiya", "Bao", "Kagami Shinnosuke"
]

# --- VASTLY EXPANDED TEMPLATES V6 (MASSIVE LORE EXPANSION) ---
EVENT_NAME_TEMPLATES = [
    "Ashes of Makai", "Resonance Requiem", "The Shintai Showdown", "Heartbeats of the Rift", "Satsui vs. Soul", "Neo-Makai Skirmish", "Saikyo Salvation", "Judgment of the Fallen", "Harmony Break", "Echo Surge", "Dance of Light", "Hearts Collide", "War of Wills", "Dimensional Descent", "Flames of the Forgotten", "Storm in the Soul", "Test of Harmony", "Savage Soul Clash", "Under the Dying Sky", "Crossfire in Neo-Esaka", "Shadow Pulse", "Oblivion Waltz", "The Last Pulse", "Final Consonance", "The Rift’s Choir", "Echo vs. Echo", "Neo-Makai Grudge", "Guardian of Rhythm", "The Demon’s Wager", "Arc of Rebirth", "Dead Soul Waltz", "The Orochi Disruption", "Fangs of the Rift", "Capoeira Reverberation", "The Pulse Remains", "Awakened Bloodlines", "Scars of the Shadaloo Rift", "Trial of the Forgotten Flame", "Mirrored Harmonics", "Elena’s Last Dance", "When Hope Stands Tall", "Soulstorm Prelude", "The Demon Bell Tolls", "Blaze of the Blacknoah", "Tears of the Rift", "Gaia's Will", "Shadow of Lilith", "Hearts of the Converging Flame", "Beneath the Blood Sky", "Arcane Duel", "Light Versus Hunger", "Rebirth Through Chaos", "Screams Across Dimensions", "Broken Mirror Battle", "The Rift Between Us", "Last Signal From the Echoes", "Souls of the Brave", "Under Twilight's Burden", "Flames of the Fusion Rift", "Cursed Alliance", "Oblivion Pact", "The Dance of Oblivion", "Prophets of Fire and Silence", "The Rhythm That Defied Makai", "Collapse of Psyche and Soul", "Sonic Flashpoint", "Endless Reckoning", "No Return Duel", "The Beat That Heals", "From Soul to Silence", "When the Rift Breathes", "Twin Hells Collide", "Convergence Flashback", "Shadaloo’s Last Gambit", "Dissonance Ascends", "The Spiral of Echoes", "Heaven Cracked", "Apocalypse Remix", "Through Fire and Soul", "The King of Fighters: Echo Chapter", "Street Fighter Alpha: Makai Dawn", "Capcom vs. SNK 3: The Shintai Engine", "Darkstalkers' Requiem", "Rival Schools: Dimensional Class", "Samurai Shodown: Wandering Soul", "The Satsui Instict", "Psycho Power Overload", "Orochi's Return: A Fated Clash", "The NESTS Legacy", "Ikari Warriors: Jungle Rift", "Art of Fighting: The Kyokugen Legacy", "Fatal Fury: A Legend's Challenge", "Gaias Emergency", "A Message from Haruhi", "The Melancholy of {c2}", "Marvel vs. Capcom: Infinity Echoes", "Tekken: The Mishima Rift", "Soul Calibur: Edge of Convergence", "Mortal Kombat: The Soulnado's Pull", "The Kusanagi-Yagami Truce", "A Rose's Final Prophecy", "Athena's Psychic Plea", "The K' Project: Final Contingency", "Maxima's Last Broadcast", "The Price of Harmony", "Jedah's Collection: A New Soul", "Demitri's Midnight Bliss", "The Howl of Jon Talbain", "Anakaris's Judgment", "Huitzil's Final Protocol", "Pyron's Descent", "The Raging Demon's Test", "Oni's Advent", "Gill's Utopia: A New Order", "The Secret of Q", "Twelve's Genesis", "Seth's Data Hunt", "Juri's Game: A New Toy", "Gouken's Lesson", "The Power of Nothingness", "Geese's Nightmare: A Reppuken Echo", "Rugal's Collection: A New Statue", "Goenitz's Gospel: The Wind's Call", "Ash's Gambit: A Stolen Power", "Saiki's Fall: The End of an Era", "Verse's Fragments", "The Judge's Decree: Reality Error", "The Price of a Sister's Love", "Elena's Dance of Mending", "A Campfire Confession", "DivineEliza's Requiem", "The Song of DivineJuli", "DivineSkullo's Harvest", "The Echo of Mr. Karate", "The Enigma of cvssilber", "Jimmy-POTS reports: A New Anomaly", "NeoGeegus's Prediction", "A Challenge from RajaaMiyako", "The Final Resonance", "The Metallic Tang of a Fought Dimension", "Planetary Arrhythmia", "A Weeping of Wrong Colours", "The Sickness Seeps In", "Jedah's Influence: The Cold Consumption", "Morrigan's Influence: The Fever Pitch", "A Dance of Affirmation", "The Unsteady Ground", "A Rasteira for the Void-Shadows", "An Armada for the Chaotic Energy", "A Small Point of Light", "Looming Figures of Cold Obsidian", "The Song of a Ruined City", "A Resonant Wave of Healing Harmony", "The Stillness After the Storm", "The Faint Lines on the Soul of Reality", "A Solitary Dance in the Savanna", "The Unwavering Heartbeat of the Restored Savanna", "The Beat Goes On", "The Resonance of Worlds Begins", "Cracks in the World", "A Wound in the Fabric of Reality", "The Grey-Suited Agents of Convergence", "Annihilation Event 734 Logged", "Successful Convergence Protocol 912", "Aggressive Red Echoes, Defensive Blue Echoes", "Potential Futures Fighting for Existence", "Ripples Across Dimensions", "Blacknoah's Trophy Room", "The Coming Judgment of Gill", "The Ultimate Culmination of Darkness", "Forces Across Myriad Realities", "The First Fractures", "A Phantom Metsu Hadoken", "What It Means When Your Darkness Bleeds Through", "A Ghostly Green Blast of Energy", "A Version of a Hero Who Lost Everything", "They're Not Just Copies, They're Possibilities", "Agonizing Visions", "An Army Forged from the Displaced", "ACT I: CONVERGENCE", "Still NESTS' Puppet!", "Flashes of the Cruel Krizalid", "A Quiet Resolve Hardened Within Her", "The Rhythm of the Universe is Off-Key", "The Unmistakable Signature of CE's Manipulation", "A Feral Orochi Echo", "The Multiverse Grand Prix", "Face Your Echoes! Master Your Potential!", "A Tournament Run by Creeps", "Harvesting the Energy", "The Crucible Grand Prix: Neo-Esaka", "A Dizzying, Unstable Metropolis", "Impossible Matchups on Flickering Billboards", "Raw, Untamed Potential", "Calculated, Robotic Defense", "Fighter Adaptation is Accelerating", "A Death Spiral with an Orochi Echo", "The Final Contingency Protocol", "ACT II: VILLAINS FALL, THE JUDGE RISES", "PsycheOmega Bison's Debut", "A Flawless Strategic Retreat", "The Monstrous Omega Rugal", "The New, True God of the Flawed Multiverse", "Emergence of the Final Judge", "Sentient Resistance Detected", "It Cannot Comprehend True Unity", "A Tapestry of Defiant Consciousness", "CHAPTER 5: DARK MORRIGAN'S REIGN", "The Ultimate Potential for Chaotic Power", "A Terrifying Singularity of Desire", "Designation: Dark Morrigan", "Stabilize the Prime Anomaly", "This Imbalance is Unacceptable. Messatsu.", "ACT III: COSMIC RESOLUTION", "The Price of Harmony", "The Echoes Are Not Weapons To Command", "A Symphony of Balanced Aggression", "The Ultimate Sacrifice", "CHAPTER 7: ECHOES FADE", "The Ultimate Battle Lies Within", "A Universal, Painful Evolution", "CHAPTER 8: RESONANCE RESTORED", "A Community Forged in Crisis", "A Silent Memorial for Maxima", "Sharing This Burden", "Passing the Torch", "The Tentative Start of Reconciliation", "The Lingering Dimensional Instability", "A Campfire Under a Brighter Sky", "Game Over? No. Game Won.", "Post-Credits Reflection", "A Particularly Interesting Knot of Unstable Energy", "The Game Was Just Beginning", "Warachia's Bloody Night", "The Blade of Kagami", "Devilotte's Infernal Machine", "Tessa's Scholarly Pursuit", "Haruhi's Divine Intervention", "Capcom's Will vs. SNK's Spirit", "Juggernaut's Unstoppable Charge", "Colossus's Fastball Special", "The Sonson Legacy", "Lord Raptor's Power Chord", "The Fierce Glare of CFJ_Oni", "T. Hawk's Ancestral Call", "Dee Jay's Maximum Rhythm", "A Rematch for Tiffany", "A Battle Under the Crimson Moon", "The Counter Force's Intervention", "A Duel at the Center of the Spiral", "The Roar of the Dead Apostle", "A Vampire's Whim", "The Truth of the Tohno Blood", "Akiha's Vermillion Command", "Ciel's Seventh Scripture", "Shiki's Nanaya Instincts", "Arcueid's True Power", "Aoko's Fifth Magic", "The Final Arc Drive", "A Duel in Misaki Town", "Souren Araya's Paradigm", "Kara no Kyoukai: The Void's Edge", "A Battle Against Paradox", "A Fight for the Akasha", "The Eyes of Death Perception", "A Clash at the Ogawa Apartment", "Touko's Puppets: A Gauntlet", "The Pain of Lio Shirazumi", "Fujino Asagami's Distorted Vision", "A Battle with the Origin Awakened", "The Shield of the Unmoving Lord", "A Final Stand at the Reien Academy", "The False Saint's Stratagem", "A Servant's Last Command", "The Holy Grail's Call", "A War in Fuyuki City", "A Duel on the Fuyuki Bridge", "The Shadow's Consumption", "The Golden King's Gate of Babylon", "The Holy Church's Executioner", "A Heretic's Final Plea", "A Duel of True Ancestors", "The 27 Dead Apostle Ancestors", "Primate Murder's Rampage", "Type-Mercury's Invasion", "The Ultimate One of the Earth", "A Battle for the Planet's Soul", "The Crimson Moon's Return", "A Duel under the Millennium Castle", "The Alchemist's Gambit", "The Church's Black Keys", "A Burial Agency's Assignment", "A Beast of Humanity's Advent", "The Grand Order's Final Mission", "A Singularity's Correction", "A Lostbelt's Pruning", "A Threat to Human Order", "A Last Stand at the Throne of Heroes", "The Incineration of Humanity", "A Remnant of Goetia", "A Temple in Time", "The Alien God's Descent", "A Chaldea in Peril", "A Rayshift Gone Wrong", "A Duel with the Foreigner", "A Madness Enhancement", "The Pretender's Masquerade", "The Faker's Gambit", "The Beast's Calamity", "A Threat from the Imaginary Sea", "A Demonic Bodhisattva's Mercy", "A Clash in the Demonic Capital", "The Sword of the Shogun", "A Duel under the Cherry Blossoms", "The Onlooker from the Throne", "Temporal Paradox", "The {adj} Cipher", "Quantum Entanglement", "A Rift in Spacetime", "The Dragon's Maw", "Oracle's Decree", "The Cybernetic Ghost", "Protocol Omega", "A Promise Sealed in Blood", "The Unforgiven Blade", "Fist of the {adj} Star", "Iron Fist Aftermath", "Downtown Beatdown", "Back-Alley Brawl", "Nocturne in {adj}", "The Final Verse", "Requiem for a Dream", "When Angels Weep", "Symphony of Destruction", "The God-Slayer's Challenge", "Nexus of Souls", "The {adj} Labyrinth", "A Warrior's Lament", "The Phoenix's Rebirth", "Where Heroes Fall", "The Edge of the World", "Clash of Ideals", "The Star-Eater's Arrival", "A {adj} Heresy", "The Saint's Gambit", "The Serpent's Kiss", "Lunar Eclipse", "Solar Flare", "The Last Stand on the Bridge", "A Duel in the Hanging Gardens", "The Colosseum of the Damned", "Trial by Combat", "The Maelstrom's Heart", "A Whisper in the Void", "The Price of a Crown", "King's Ransom", "The Jester's Game", "A Shadow Play", "The Sunken City's Secret", "The Mountain's Peak", "A Path of Thorns", "The Road to Ruin", "A Hero's Welcome", "The Traitor's Reward", "A Duel at Dawn", "Showdown at Sunset", "Midnight Mayhem", "The Hour of the Wolf", "A {adj} Gambit", "The Unseen Hand", "A Web of Lies", "The Truth in Steel", "A Song of Ice and Fire", "The Dance of Dragons", "The Blood Moon's Call", "The Hunter's Quarry", "A Test of Faith", "The Heretic's Brand", "The Inquisitor's Judgement", "A Battle for a Soul", "The {adj} Crusade", "The Last Pilgrim", "A World in Balance", "The Fulcrum Point", "The Catalyst Event", "A Ripple in Time", "The Butterfly Effect", "A Cascade Failure", "The Domino Chain", "The Point of No Return", "A Desperate Alliance", "An Unholy Pact", "The Enemy of My Enemy", "A Truce for a Day", "A Ceasefire Broken", "The {adj} Accord", "The Treaty of Broken Glass", "The War of Lost Children", "The Battle of the Twin Peaks", "The Siege of the {adj} Citadel", "The Fall of the Spire", "The Last Bastion", "A Forlorn Hope", "The Vanguard's Charge", "The Rearguard's Sacrifice", "A Phyrric Victory", "A Costly Defeat", "The Ashes of Victory", "The Bitter Taste of Survival", "A New Dawn", "An Endless Night", "The Twilight of the Gods", "Ragnarok's Eve", "The Age of Man", "The Era of Chaos", "The Reign of Monsters", "The Rise of the Machines", "The Singularity", "The Event Horizon", "A Glitch in the Matrix", "The System's Correction", "An Unforeseen Variable", "A Ghost in the Machine", "The Turing Test", "The Electric Sheep's Dream", "A Scanner Darkly", "The Man in the High Castle", "The Road Not Taken", "A Sound of Thunder", "The City and the Stars", "The Fountains of Paradise", "Childhood's End", "The Nine Billion Names of God", "The Sentinel", "A Space Odyssey", "The monolith's beckoning", "A journey beyond the infinite", "My God, it's full of stars", "The Overmind's Game", "The Last Question", "The Final Answer", "The Heat-Death of the Universe", "The Rebirth of a Cosmos", "The Cycle Anew"
]
EVENT_ADJECTIVES = [
    "Crimson", "Azure", "Forgotten", "Fateful", "Legendary", "Ultimate", "Grand", "Final", "Golden", "Shadow", "Shining", "Burning", "Frozen", "Storming", "Silent", "Raging", "Divine", "Infernal", "Lost", "Sacred", "Cursed", "Broken", "Fallen", "Soulburned", "Fractured", "Makai-Touched", "Resonant", "Dimensional", "Twilight", "Sanctified", "Harmonic", "Cursed-Blooded", "Flareborn", "Wounded", "Oblivion-Bound", "Sacrificial", "Cataclysmic", "Shattered-Sky", "Psycho-Fused", "Final-Rhythm", "Orochi-Born", "Wistful", "Void-Echoed", "Flickering", "Reverent", "Broken-Hearted", "Tempestuous", "Choral", "Spectral", "Aetherial", "Beat-Linked", "Mythwoven", "Unsilenced", "Searing", "Echo-Laced", "Sorrowful", "Flame-Bound", "Luminous", "Fevered", "Shadowroot", "Glimmering", "Ash-Kissed", "Silent-Raging", "Mournful", "Nether-Forged", "Starlit", "Pulse-Stained", "Primal", "Epiphany-Driven", "Heavenfall", "Pact-Forged", "Soulchained", "Rift-Born", "Grayscale", "Faithbound", "Kusanagi-Style", "Yagami-Infused", "Kyokugenryu", "Art-of-Fighting", "Fatal-Fury", "South-Town", "Garou-Marked", "Ikari-Trained", "Psycho-Soldier", "NESTS-Engineered", "Orochi-Sealed", "Shiranui-Style", "Satsui-Awakened", "Ansatsuken", "Shadaloo-Controlled", "Hadou-Powered", "Kanzuki-Sponsored", "Saikyo-Style", "Bushinryu", "Darkstalker-Night", "Aensland-Grace", "Dohma-Chosen", "Maximoff-Rule", "Shintai-Bound", "Samurai-Shodown", "Bushido-Blade", "Mishima-Zaibatsu", "G-Corporation", "Devil-Gene", "Lin-Kuei", "Shirai-Ryu", "Netherrealm", "Elder-God", "Joestar-Bloodline", "Stand-Powered", "Hamon-Infused", "Stark-Industries", "X-Men", "Avenger-Level", "S.H.I.E.L.D.-Sanctioned", "Weapon-X", "Symbiote-Bonded", "Gamma-Irradiated", "Asgardian", "Celestial", "Skrull-Infested", "Kree-Engineered", "Infinity-Stone", "Shi'ar-Imperial", "Hellfire-Club", "Phoenix-Force", "Chaos-Magic", "Pym-Particle", "Vibranium-Weave", "Mutant-Gene", "Inhuman-Terrigen", "Deviant-Touched", "Eternal-Flame", "Watcher-Observed", "Galactus-Herald", "Negative-Zone", "Microverse", "Mojoverse", "Savage-Land", "Latverian-Decree", "Wakandan-Pride", "Atlantis-Risen", "Genoshan", "Krakoan", "Arakko-Born", "Otherworld-Fae", "Vampire-Nation", "Midnight-Sun", "Darkhold-Empowered", "Cyttorak-Crimson", "Serpent-Crown", "Ashen-Haired", "Clock-Tower", "Atlas-Institute", "Wandering-Sea", "Mage-Association", "Burial-Agency", "27-Ancestor", "Dead-Apostle", "True-Ancestor", "Servant-Class", "Noble-Phantasm", "Holy-Grail", "Singularity-Point", "Lostbelt-King", "Grand-Order", "Chaldean", "Crypter-Led", "Fantasy-Tree", "Alien-God", "Foreigner-Class", "Beast-of-Calamity", "Counter-Guardian", "Alayashiki", "Gaia-Will", "Akashic-Record", "Root-Connected", "Origin-Awakened", "Mystic-Eyes", "Reality-Marble", "Einzbern-Homunculus", "Matou-Sorcery", "Tohsaka-Jewel", "Seventh-Scripture", "Black-Key", "Pure-Eyes", "Conceptual-Weapon", "Age-of-Gods", "Divine-Spirit", "Heroic-Spirit", "Throne-of-Heroes", "Paper-Moon", "Imaginary-Sea", "Avalon-Guarded", "Caliburn-Forged", "Excalibur-Promised", "Gae-Bolg-Pierced", "Bellerophon-Ridden", "Rule-Breaker", "Zabaniya-Heartbeat", "God-Hand", "Gate-of-Babylon", "Unlimited-Blade-Works", "Heaven's-Feel", "Hollow-Ataraxia", "Tsukihime-Lunar", "Melty-Blood", "Tohno-Blood", "Nanaya-Instinct", "Vermillion-Akiha", "Ciel-Route", "Arcueid-Path", "Far-Side", "Near-Side", "Marble-Phantasm", "Aoko-Blue", "Touko-Orange", "Souren-Gray", "Kara-no-Kyoukai", "Void-Shiki", "Distortion-Twisted", "Lio-Consumed", "Enjou-Paradox", "Fujino-Bent", "Kiritsugu-Emiya", "Zero-Event", "Apocrypha-Red", "Apocrypha-Black", "Strange-Fake", "Case-Files", "El-Melloi", "Lord-Waver", "Gray-Tan", "Add-Infused", "Iskandar-Golden", "Diarmuid-Love-Spot", "Gilles-de-Rais", "Lancelot-Grief", "Artoria-Pendragon", "EMIYA-Archer", "Cu-Chulainn", "Medusa-Rider", "Medea-Caster", "Hassan-of-the-Cursed-Arm", "Heracles-Berserker", "Gilgamesh-King-of-Heroes", "Angra-Mainyu", "All-the-World's-Evils", "Saber-Alter", "Dark-Sakura", "True-Assassin", "Kojirou-Sasaki", "Solomon-Grand-Caster", "Goetia-Demon-God", "Tiamat-Beast-II", "Kiara-Sessyoin", "Kama-Mara", "BB-Moon-Cancer", "Abigail-Williams", "Hokusai-Foreigner", "Voyager-Class", "Pretender-Class", "Shielder-Galahad", "Ruler-Jeanne-d'Arc", "Avenger-Edmond-Dantes", "Alter-Ego-Meltryllis", "Passionlip-Ego", "Kingprotea-Ego", "Mash-Kyrielight", "Fou-Primate-Murder", "Merlin-Magus-of-Flowers", "Scathach-Land-of-Shadows", "Ozymandias-Ramesside", "Nitocris-Mirror-Maker", "Quetzalcoatl-Lucha-Goddess", "Gorgon-Monstrous", "Jaguar-Warrior", "Ereshkigal-Underworld", "Ishtar-Heavenly", "Enkidu-Clay-of-Gods", "First-Hassan-Gramps", "Leonardo-Da-Vinci", "Sherlock-Holmes-Detective", "Moriarty-Spider", "James-Moriarty-Ruler", "Shinjuku-Avenger", "Agartha-Rider", "Shimousa-Saber", "Salem-Caster", "Anastasia-Lostbelt", "Gotterdammerung-Lostbelt", "SIN-Lostbelt", "Yuga-Kshetra-Lostbelt", "Atlantis-Lostbelt", "Olympus-Lostbelt", "Avalon-le-Fae-Lostbelt", "Nahui-Mictlan-Lostbelt", "Ordeal-Call", "Cosmos-in-the-Lostbelt", "Observer-on-Timeless-Temple", "Fujimaru-Ritsuka", "Gudako-Beast", "Gudao-Savior", "Riyo-Learning-with-Manga", "Bunyan-Paul", "Final-Fantasy", "SOLDIER-First-Class", "SeeD-Graduate", "Guardian-Sworn", "Jenova-Cell", "Lifestream-Infused", "Mako-Powered", "Summoner-Yuna", "Aeon-Final", "Sin-Toxin", "Zanarkand-Dream", "Blitzball-Champion", "Fayth-Sealed", "Spira-Sorrow", "Al-Bhed", "Yevon-Dogma", "Machina-Powered", "Tidus-Laughing", "Auron-Legendary", "Lulu-Black-Mage", "Wakka-Besaid", "Rikku-Thief", "Kimahri-Ronso", "Seymour-Guado", "Jecht-Shot", "Braska-Calm", "Yunalesca-Undying", "Shuyin-Grief", "Lenne-Songstress", "Gullwings-Sphere-Hunter", "Vegnagun-Powered", "Shinra-Company", "Turk-Assigned", "Avalanche-Eco", "Nibelheim-Incident", "Midgar-Slums", "Sector-7", "Honey-Bee-Inn", "Wall-Market", "Cosmo-Canyon", "Wutai-Pagoda", "Gold-Saucer", "Temple-of-the-Ancients", "Forgotten-Capital", "Northern-Crater", "Weapon-Awakened", "Meteor-Summoned", "Holy-Spell", "Black-Materia", "White-Materia", "Highwind-Legacy", "Cloud-Strife", "Aerith-Gainsborough", "Tifa-Lockhart", "Barret-Wallace", "Red-XIII-Nanaki", "Cid-Highwind", "Yuffie-Kisaragi", "Vincent-Valentine", "Cait-Sith", "Zack-Fair", "Sephiroth-One-Winged-Angel", "Genesis-Rhapsodos", "Angeal-Hewley", "Deepground-Soldier", "Kadaj-Remnant", "Yazoo-Shooter", "Loz-Brawler", "Rufus-Shinra", "Tseng-Turk", "Reno-Rude", "Elena-Turk", "Cissnei-Turk", "Hojo-Mad", "Lucrecia-Crescent", "Ifalna-Cetra", "Bugenhagen-Wise", "Dyne-Corel", "Elmyra-Gainsborough", "Marlene-Wallace", "Zangan-Master", "Squall-Leonhart", "Rinoa-Heartilly", "Zell-Dincht", "Selphie-Tilmitt", "Irvine-Kinneas", "Quistis-Trepe", "Seifer-Almasy", "Laguna-Loire", "Kiros-Seagill", "Ward-Zabac", "Edea-Kramer", "Ultimecia-Sorceress", "Adel-Sorceress", "Time-Compression", "Balamb-Garden", "Trabia-Garden", "Galbadia-Garden", "Esthar-City", "Lunar-Cry", "Ragnarok-Ship", "Junction-System", "Guardian-Force", "Para-Magic", "Veridian", "Indigo", "Onyx", "Jubilant", "Vengeful", "Sorrowful", "Temporal", "Quantum", "Adamantine", "Waning", "Ascendant", "Hollow", "Timeless", "Fleeting", "Corrupted", "Unbound", "Abyssal", "Celestial", "Lucid", "Phantasmal", "Ironclad", "Gilded", "Obsidian", "Opaline", "Sanguine", "Verdant", "Ashen", "Umber", "Cerulean", "Viridian", "Ebon", "Ivory", "Argent", "Garnet", "Topaz", "Amethyst", "Sapphire", "Ruby", "Emerald", "Diamond", "Vitreous", "Crystalline", "Meteoric", "Cosmic", "Galactic", "Stellar", "Nebulous", "Pulsing", "Singular", "Eventful", "Hypothetical", "Canonical", "Apocryphal", "Gnostic", "Heresy-marked", "Dogmatic", "Zealous", "Apathetic", "Stoic", "Frenzied", "Manic", "Melancholic", "Phlegmatic", "Choleric", "Epicurean", "Nihilistic", "Existential", "Absurdist", "Surreal", "Dadaist", "Futurist", "Cubist", "Impressionist", "Expressionist", "Romantic", "Classical", "Baroque", "Gothic", "Art-Nouveau", "Art-Deco", "Modernist", "Post-Modern", "Deconstructed", "Reconstructed", "Metafictional", "Pataphysical", "Ontological", "Epistemological", "Metaphysical", "Alchemical", "Theurgical", "Goetic", "Hermetic", "Kabbalistic", "Rosicrucian", "Masonic", "Illuminated", "Enlightened", "Transcendent", "Immanent", "Emanated", "Uncreated", "Primordial", "Ante-Diluvian", "Post-Apocalyptic", "Pre-Lapsarian", "Post-Lapsarian", "Utopian", "Dystopian", "Arcadian", "Elysian", "Tartarean", "Paradisiacal", "Nirvanic", "Samsaric", "Karmic", "Dharmic", "Moksha-bound", "Bodhisattvic", "Arhat-like", "Devic", "Asuric", "Rakshasic", "Yakshan", "Gandharvan", "Kinnaran"
]
EVENT_DESC_TEMPLATES = [
    "Two worlds collide as {c1} and {c2} cross paths. Who will emerge victorious?", "A duel for the ages is about to unfold. Will {c1}'s strength be enough to overcome {c2}'s skill?", "In the heart of the storm, {c1} and {c2} meet. Only one will walk away.", "The crowd is roaring for a spectacle, and {c1} and {c2} are ready to deliver!", "Legends tell of a battle like this. Now, {c1} and {c2} will make it a reality.", "Power, skill, and determination. {c1} and {c2} have it all, but only one can be the victor.", "The fate of the world hangs in the balance as {c1} and {c2} prepare for their ultimate confrontation.", "It's a clash of titans! {c1} versus {c2} in a battle that will shake the very foundations of the earth.", "Get ready for the fight of the century! {c1} and {c2} are about to rewrite history!", "More than just a fight, it's a battle of wills. Can {c1} outlast the indomitable spirit of {c2}?",
    "A pulse echoes through the scarred sky. {c1} and {c2} step into the rhythm of fate.", "Makai’s remnants surge anew. Only {c1} and {c2} stand between salvation and silence.", "When the world forgot its song, {c1} remembered. But {c2} wants to silence it forever.", "Beyond time, beyond sorrow—{c1} meets {c2} in a battle that echoes across realities.", "Jedah's last whisper stirs the wind. {c1} and {c2} are caught in its message.", "They were not meant to meet. But the rift had other plans. {c1} vs. {c2} begins now.", "The Rift pulses with pain. Only a dance between {c1} and {c2} can restore its beat.", "Echoes don’t forget. {c1} and {c2} are trapped in one such memory—one that burns.", "The savanna healed, but new wounds opened. {c1} must face {c2} before the world bleeds again.", "Each step forward cracks reality. {c1} and {c2} walk a path where one must fall.", "The last resonance of the universe hinges on this battle: {c1} vs. {c2}.", "ShadowLady watches silently. {c1} and {c2} must prove the world still holds light.", "Demons hunger for the victor’s soul. {c1} and {c2} must decide if the fight is worth that price.", "A fight framed in prophecy. A duel defined by heart. {c1} meets {c2} under a dying sky.", "From the ashes of the Convergence, new conflicts rise. {c1} and {c2} answer the call.", "Their fists carry the memories of fallen worlds. This battle between {c1} and {c2} is sacred.", "Elena’s light reaches far. It shines now between {c1} and {c2}. Will it endure?", "A memory twisted by Makai energy replays once more. {c1} vs. {c2}.", "Each movement is music. Each clash is discord. {c1} and {c2} write a symphony of survival.", "No heroes here. Just two souls and a war waiting to be reborn.",
    "The story said it was over. The story lied. {c1} faces {c2} as a new chapter begins.", "Convergence Enterprises may be gone, but their failsafes remain. {c1} and {c2} are trapped in one.", "The Red Echo demands aggression. The Blue Echo demands focus. {c1} and {c2} must choose a path.", "Lilith's sacrifice bought them time. Now, {c1} and {c2} will decide if that time was well spent.", "The Final Judge fell, but its logic persists. {c1} must prove to {c2} that emotion is not a flaw.", "Dark Morrigan's agony still stains the dimensions. Can {c1} and {c2} fight without feeding the chaos?", "The Satsui no Hado versus the Power of Nothingness. {c1} and {c2} represent the ultimate duality.", "A Kusanagi flame meets a Yagami curse. For {c1} and {c2}, this is more than a fight; it's destiny.", "Kyokugenryu karate's ultimate test. {c1} puts it all on the line against the might of {c2}.", "In the ruins of Neo-Esaka, two figures meet. {c1} seeks answers. {c2} seeks a worthy opponent.", "The weight of their Echoes is a heavy burden. Can {c1} carry it to victory against {c2}?", "This isn't about good or evil. For {c1} and {c2}, it's about whose reality is stronger.", "A single, perfect flower blooms in the rubble. {c1} and {c2} fight to protect it... or to claim it.", "The beat of the Earth has returned, but it is fragile. {c1} and {c2}'s clash could shatter it forever.", "The world is watching. The heroes are watching. Even the villains are watching. {c1} vs. {c2}. No pressure.", "This battle will be recorded in the Akashic records. {c1} and {c2}, make it a good one.", "A fragment of Verse, a sliver of the Judge, a whisper of Orochi. The chaos finds purchase in {c1} and {c2}.", "Can you hear it? The sound of the world holding its breath. {c1} vs. {c2} is about to begin.", "Juri Han is watching this fight from a rooftop, a predatory smile on her face. Better make it interesting for her.", "What is the price of victory? {c1} and {c2} are about to find out, whether they want to or not.", "A challenge from the Mishima Zaibatsu has been issued. {c1} answers, only to find {c2} waiting.", "The Lin Kuei seek to contain the anomaly. The Shirai Ryu seek vengeance. {c1} and {c2} are caught between them.", "A Stand user's power is absolute. But what happens when two, {c1} and {c2}, meet in a torn reality?", "Tony Stark's sensors are going haywire. The power levels of {c1} and {c2} are off the charts.", "This fight is sponsored by the Kanzuki Zaibatsu. Ohohoho!", "A new King of Fighters tournament has been announced, but the rules are strange... and so are the combatants. {c1} vs. {c2}.", "The dimensional bleed has brought them here. {c1} from one world, {c2} from another. There's no way home but through.", "It began with a simple invitation. It will end in a battle that will be felt across the multiverse. {c1} vs. {c2}.", "The soul of a warrior never rests. For {c1} and {c2}, peace was never an option.", "In the quiet after the storm, a new conflict brews. {c1} faces {c2} under a sky still healing.", "Was it destiny? Or just a cruel joke by the cosmos? Either way, {c1} and {c2} must now fight.", "The embers of the last war still glow. {c1} and {c2} are about to fan them into a new inferno.", "They fought for the world. Now, do {c1} and {c2} fight for themselves, or for something more?", "An old score needs to be settled. {c1} and {c2} finally get their rematch.", "This is a test. A test of strength, a test of will, a test of soul. {c1} vs. {c2}.", "The stage is set. The fighters are ready. Let the Resonance of Worlds begin with {c1} and {c2}!", "The beat of Capoeira meets the stillness of the killing intent. A dance of life and death between {c1} and {c2}.", "One fights for a future with their family. The other fights to erase a cursed past. {c1} vs. {c2}.", "The raw power of a Red Echo clashes with the perfect defense of a Blue Echo. {c1} and {c2} are balance personified.", "Can a single act of healing mend a world? {c1} believes so. {c2} is about to test that belief.", "The silence left by Jedah's ambition is broken by the clash of {c1} and {c2}.", "The fever of Morrigan's loneliness is soothed only by the rhythm of this battle. {c1} vs. {c2}.", "They are survivors of a war that should have ended all wars. Now, {c1} and {c2} must fight again.", "A message from the future warns of this battle. But can {c1} and {c2} change their fate?", "In the world of Melty Blood, where reality is thin, {c1} and {c2} find their duel has dire consequences.", "The Counter Force has deemed them a threat. A Grand Servant is dispatched. Can {c1} and {c2} survive?", "This isn't a Holy Grail War, but the prize is just as great: survival. {c1} vs. {c2} in a battle for existence.", "The Einzbern homunculi observe, the Matou worms stir, and the Tohsaka gems shine. This battle between {c1} and {c2} has attracted attention.", "A Reality Marble is about to be deployed. Can {c1} fight a war within the soul of {c2}?", "The Mystic Eyes of Death Perception can see the end of all things. Do they see the end of this fight between {c1} and {c2}?", "A new Singularity has been detected, centered on a single duel: {c1} vs. {c2}. Chaldea must intervene.", "The Alien God's plan did not account for this. The raw, untamed power of {c1} and {c2} is a variable it cannot compute.", "From the throne of heroes, spirits watch. They see their own legends reflected in the struggle of {c1} and {c2}.", "One is a Beast of Calamity, the other a Savior of Humanity. Their clash, {c1} vs. {c2}, will decide the texture of the world.", "Summoned from the Lifestream, a memory of a hero appears. Can {c1} defeat the lingering spirit of {c2}?", "This duel is powered by Mako, fueled by memories, and will end with a Limit Break. {c1} vs. {c2}.", "A Guardian Force has been junctioned. A Sorceress's power is about to be unleashed. {c1} and {c2} fight at the edge of time.", "The Ragnarok descends, the Lunar Cry begins, and two lone figures stand against it all. Or will they fight each other first? {c1} vs. {c2}.",
    # New Additions
    "The air grows thin. A challenge has been made between {c1} and {c2}, and the world itself seems to be listening.", "Before the eyes of gods and monsters, {c1} and {c2} will settle their differences. There will be no interruptions.", "This is not a battle for glory, but for existence. The loser will be forgotten by time itself.", "A temporal storm rages, and at its eye, {c1} and {c2} are locked in a combat that could rewrite history.", "Their paths were never meant to cross, yet here they are. {c1} versus {c2}. Let the paradox begin.", "The old magic awakens at the clash of their auras. {c1} and {c2} are now pawns in a much older game.", "A single coin was flipped in the void. It landed on its edge. As a result, {c1} and {c2} must now fight.", "The prophecy was a lie, a trick to bring {c1} and {c2} to this very spot. Who benefits from their conflict?", "In the silence between heartbeats, their fates were sealed. This duel between {c1} and {c2} was always meant to be.", "One seeks redemption, the other seeks oblivion. Their goals are different, but their path is the same: victory over the other.", "Look to the sky. The stars are going out, one by one. The battle between {c1} and {c2} has cosmic consequences.", "This is the final test of the 'human heart' that the Judge could not understand. {c1} and {c2} are its subjects.", "A fragment of Lilith's soul resonates with them both, urging them to fight, to prove life is worth the struggle.", "The agents in grey suits are taking notes. This fight between {c1} and {c2} is a data point in their grand experiment.", "They are fighting on the corpse of a dead god, its fading power infusing their every move.", "The Blacknoah wasn't destroyed. It's watching. It's waiting for a new champion to emerge from this fight.", "One carries the will of Capcom. The other, the spirit of SNK. This is more than a fight; it's a clash of legacies.", "Haruhi Suzumiya is bored. She thought it would be interesting if {c1} and {c2} had a sudden, dramatic showdown. So they are.", "The data from this battle will be used to create the next generation of Urien's clones. They'd better make it a good show.", "This isn't just a fight. It's a debate, and their fists are their arguments. Which philosophy will win out?", "The winner of this fight gets a free meal at Pao Pao Cafe. The loser has to wash dishes for a week.", "A portal to the Netherrealm has opened, and Scorpion demands a worthy opponent. {c1} and {c2} must fight to decide who faces him.", "Stark Industries has offered a sponsorship deal to the winner. The loser gets a bill for property damage.", "The Watcher observes from his moon base, a single tear rolling down his cheek. This battle between {c1} and {c2} is truly a pivotal moment.", "It's just another Tuesday for {c1}. For {c2}, it's the most important fight of their life. That imbalance will be interesting.", "The Spiral of Echoes has chosen them. They must fight, or be consumed by the temporal feedback loop.", "They fight for the last patch of green grass in a world consumed by concrete and steel.", "A child is watching them from a broken window. {c1} and {c2} must decide what kind of lesson to teach.", "This fight is a prayer. A violent, desperate prayer that tomorrow might be better than today."
]

# --- PARSED STAGE LIST ---
RAW_STAGE_LIST = """
"C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\5thAveTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ArenaTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\balrog.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\BasementTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\BelfryDayTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\BelfryNightTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\bison.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\blanka.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Burning_Osaka_CVS2.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cammy.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\CasinoTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_hongkong.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_infinity_chamber.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_infinity_chamber_remains.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_japan.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_jungle.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_myanmar.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_newyork.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_ruins.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_training_zone.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cfj_underworld.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\chunli.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\CvS2_Aomori.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\CvS2_Kinderdijk.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\CvS2_OsakaTower.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cvs2_shanghai_D4_a.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\cvs2_stadium.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2K_pro-ayutaya.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2k_pro-Ayutaya_EX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2k_pro-GeeseTower.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2k_pro-GeeseTower-F.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\CVS2K_Pro-Hansin_highway.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2k_pro-Metro_City.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2k_pro-paopao_cafe.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\CVS2K_Pro-ryu.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\Cvs2k_pro-train-M.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\deejay.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\dhalsim.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\DonjonTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ExpressBridgeTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ExpressSeaTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ExpressStopTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\FallsDayTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\FallsMornTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\FallsNightTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\feilong.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ForestTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\FreeTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\guile.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\HarbourTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\honda.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ken.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\kfm.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ManeuverEveTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ManeuverNightTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ManeuverSunsetTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\MarketTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\OldlineTX.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\ryu.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\sagat.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\stage0.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\stage0-720.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\stage1.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\stage3d.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\stageZ.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_boss.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_chapel.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_factory.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_forest.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_heaven.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_hell.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_omake.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_railway.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_sanctua.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\svc_sf.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\thawk.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\TrainingGridCvS2.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\vega.def" "C:\\Users\\ShasdenXa\\Desktop\\Games\\CAPCOM VS SNK ECHOES ULTIMATE\\stages\\zangief.def"
"""
parsed_stages = set()
for line in RAW_STAGE_LIST.strip().split():
    clean_line = line.strip().replace('"', '')
    if clean_line.lower().endswith('.def'):
        filename = os.path.basename(clean_line)
        parsed_stages.add(f"stages/{filename}")
RANDOM_STAGES = list(parsed_stages) if parsed_stages else ["stages/stage0.def"]

# Explicitly remove kfm.def as requested
target_stage_to_remove = "stages/kfm.def"
if target_stage_to_remove in RANDOM_STAGES:
    RANDOM_STAGES.remove(target_stage_to_remove)


class RandomEventGenerator:
    """Handles the core logic of creating and writing event files."""
    def __init__(self, game_root_path, log_queue):
        self.log_queue = log_queue
        self.game_root = game_root_path
        self.events_path = os.path.join(self.game_root, 'data', 'events')
        self.select_def_path = os.path.join(self.game_root, 'data', 'VPFG_640', 'VP_Select.def')

    def log(self, message):
        self.log_queue.put(message)

    def run_generation(self, num_to_generate, start_event_id):
        try:
            self.log(f"Starting generation of {num_to_generate} random events...")
            
            num_chars = len(CHARACTER_LIST)
            max_pairs = (num_chars * (num_chars - 1)) // 2
            if num_to_generate > max_pairs:
                self.log(f"WARNING: Requested {num_to_generate} events, but only {max_pairs} unique pairs are possible.")
                self.log(f"Generating {max_pairs} events instead to prevent errors.")
                num_to_generate = max_pairs
            
            self.log(f"Using {len(RANDOM_STAGES)} unique stages (kfm.def excluded).")
            self.log("Creating a backup of VP_Select.def...")
            backup_path = self.select_def_path + ".bak"
            with open(self.select_def_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            self.log(f"Backup created at: {backup_path}")

            os.makedirs(self.events_path, exist_ok=True)
            
            used_pairs = set()
            select_def_entries = []
            
            for i in range(num_to_generate):
                event_disk_id = start_event_id + i
                event_display_num = i + 1

                while True:
                    char1, char2 = random.sample(CHARACTER_LIST, 2)
                    pair = tuple(sorted((char1, char2)))
                    if pair not in used_pairs:
                        used_pairs.add(pair)
                        break
                
                name_template = random.choice(EVENT_NAME_TEMPLATES)
                event_name = name_template.format(c1=char1, c2=char2, adj=random.choice(EVENT_ADJECTIVES))
                
                desc_template = random.choice(EVENT_DESC_TEMPLATES)
                event_desc = desc_template.format(c1=char1, c2=char2).replace('"', "'")
                
                random_stage = random.choice(RANDOM_STAGES)
                
                lua_filename = f"event{event_disk_id}.lua"
                lua_content = f"""launchStoryboard()
if not launchFight{{ p1char = {{"{char1}"}}, p2char = {{"{char2}"}}, p1numchars = 1, p2numchars = 1, p1teammode = "single", p2teammode = "single", p1rounds = 1, p2rounds = 1, time = -1, stage = "{random_stage}" }} then return end
setMatchNo(-1) --END
"""
                with open(os.path.join(self.events_path, lua_filename), 'w', encoding='utf-8') as f:
                    f.write(lua_content)
                
                select_entry = f"""; Event R{event_display_num}: {event_name}
id = event{event_disk_id}
name = "R{event_display_num}: {event_name}"
description = "{event_desc}"
characterselect = false
simulmode = false
tagmode = false
turnsmode = false
ratiomode = false
path = data/events/{lua_filename}
"""
                select_def_entries.append(select_entry)

                if (i + 1) % 50 == 0 or (i + 1) == num_to_generate:
                    self.log(f"  ... Generated {i+1}/{num_to_generate} unique events.")

            self.log("Appending new events to VP_Select.def...")
            with open(self.select_def_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n; --- RANDOMLY GENERATED EVENTS - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                f.write("\n".join(select_def_entries))
            
            self.log("\n--- GENERATION COMPLETE! ---")
            self.log(f"Successfully added {num_to_generate} new, unique random events.")
            self.log("You can now close this window and start your game.")

        except Exception as e:
            self.log(f"\n--- AN ERROR OCCURRED! ---")
            self.log(f"Error: {e}")
            import traceback
            self.log(traceback.format_exc())
            messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}\n\nPlease check the log for details.")


class GeneratorApp:
    """The main Tkinter application window and UI logic."""
    def __init__(self, root, game_root_path):
        self.root = root
        self.game_root_path = game_root_path
        self.root.title("IKEMEN GO - Fun Random Event Generator v5")
        self.root.geometry("750x550")
        self.root.minsize(600, 450)
        self.root.configure(bg="#2E2E2E")

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2E2E2E")
        self.style.configure("TLabel", background="#2E2E2E", foreground="white")
        self.style.configure("TLabelframe", background="#2E2E2E", bordercolor="#555555")
        self.style.configure("TLabelframe.Label", background="#2E2E2E", foreground="cyan")
        self.style.configure("TButton", background="#007ACC", foreground="white", borderwidth=0)
        self.style.map("TButton", background=[('active', '#005f9e')])
        
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_font = font.Font(family="Segoe UI", size=16, weight="bold")
        ttk.Label(main_frame, text="IKEMEN GO Random Event Generator", font=title_font, foreground="cyan").pack(pady=(0, 10))
        
        info_frame = ttk.Labelframe(main_frame, text="Detected Game Paths (Portable Mode)", padding="10")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Game Root:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=self.game_root_path, foreground="#CCCCCC").grid(row=0, column=1, sticky=tk.W, padx=5)
        
        select_def_path = os.path.join(self.game_root_path, 'data', 'VPFG_640', 'VP_Select.def')
        ttk.Label(info_frame, text="Select DEF:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=select_def_path, foreground="#CCCCCC").grid(row=1, column=1, sticky=tk.W, padx=5)
        info_frame.columnconfigure(1, weight=1)

        controls_frame = ttk.Labelframe(main_frame, text="Generation Settings", padding="10")
        controls_frame.pack(fill=tk.X, pady=10)

        ttk.Label(controls_frame, text="Number of Random Events to Generate:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.num_events_var = tk.IntVar(value=50)
        self.num_events_spinbox = ttk.Spinbox(controls_frame, from_=1, to=25000, textvariable=self.num_events_var, width=10)
        self.num_events_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="Starting Event ID (from select.def):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_id_var = tk.IntVar(value=402)
        ttk.Entry(controls_frame, textvariable=self.start_id_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        self.generate_button = ttk.Button(main_frame, text="GENERATE EVENTS", command=self.start_generation, style="TButton")
        self.generate_button.pack(pady=15, ipady=8, ipadx=10)
        
        log_frame = ttk.Labelframe(main_frame, text="Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_queue = queue.Queue()
        self.log_text = tk.Text(log_frame, state=tk.DISABLED, wrap=tk.WORD, bg="#1E1E1E", fg="#D4D4D4", relief="flat", borderwidth=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.root.after(100, self.process_log_queue)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log(message)
        except queue.Empty:
            pass
        self.root.after(100, self.process_log_queue)

    def start_generation(self):
        try:
            num_events = self.num_events_var.get()
            start_id = self.start_id_var.get()
        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for the event settings.")
            return

        if num_events < 1:
            messagebox.showwarning("Invalid Input", "Please enter a number of events greater than zero.")
            return

        msg = (f"This will generate {num_events} unique random events and append them to your VP_Select.def file.\n\n"
               "A backup (VP_Select.def.bak) will be created.\n\n"
               "Are you sure you want to continue?")
        if not messagebox.askyesno("Confirm Generation", msg):
            return

        self.generate_button.config(state=tk.DISABLED)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.generator = RandomEventGenerator(self.game_root_path, self.log_queue)
        self.thread = threading.Thread(target=self.generator.run_generation, args=(num_events, start_id))
        self.thread.daemon = True
        self.thread.start()
        self.check_thread()

    def check_thread(self):
        if self.thread.is_alive():
            self.root.after(200, self.check_thread)
        else:
            self.generate_button.config(state=tk.NORMAL)

def find_game_root():
    """
    Finds the root directory of the game, ensuring the script is portable.
    It works by checking its own directory, then parent directories, for a valid
    game structure (specifically, the select.def file).
    """
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    path_to_check = application_path
    for _ in range(3):
        select_def_path = os.path.join(path_to_check, 'data', 'VPFG_640', 'VP_Select.def')
        if os.path.exists(select_def_path):
            return path_to_check
        path_to_check = os.path.dirname(path_to_check)
        
    return None

if __name__ == "__main__":
    game_root = find_game_root()
    if game_root is None:
        messagebox.showerror(
            "Game Not Found!",
            "Could not find the game's root directory.\n\n"
            "Please make sure this script is placed somewhere inside your "
            "'CAPCOM VS SNK ECHOES ULTIMATE' folder and that the folder "
            "'data/VPFG_640/VP_Select.def' exists."
        )
    else:
        root = tk.Tk()
        app = GeneratorApp(root, game_root)
        root.mainloop()