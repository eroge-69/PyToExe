import random
import time

# Synonym dictionaries for verbs, directions, and objects
VERB_SYNONYMS = {
    "walk": "go", "move": "go", "head": "go", "proceed": "go", "advance": "go", "travel": "go",
    "run": "run", "sprint": "run", "dash": "run",
    "grab": "take", "pick up": "take", "get": "take", "seize": "take", "collect": "take",
    "look at": "look", "examine": "look", "inspect": "look", "observe": "look",
    "search for": "search", "dig": "search", "hunt": "search", "explore": "search",
    "use": "use", "activate": "use", "employ": "use", "operate": "use",
    "talk to": "talk", "speak with": "talk", "chat with": "talk", "address": "talk",
    "give to": "give", "hand over": "give", "offer": "give", "bestow": "give",
    "hide in": "hide", "conceal": "hide", "duck into": "hide", "cover": "hide",
    "sacrifice": "sacrifice", "offer up": "sacrifice", "forsake": "sacrifice",
    "listen to": "listen", "hear": "listen",
    "smell": "smell", "sniff": "smell",
    "break": "break", "smash": "break", "destroy": "break"
}

DIRECTION_SYNONYMS = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "northward": "north", "southward": "south", "eastward": "east", "westward": "west",
    "up": "north", "down": "south", "right": "east", "left": "west"
}

OBJECT_SYNONYMS = {
    "car": "car_key", "vehicle": "car_key",
    "key": "gate_key", "lock": "gate_key",
    "book": "journal", "diary": "journal",
    "text": "occult_text", "scripture": "occult_text",
    "light": "flashlight", "torch": "flashlight"
}

# Game state management class
class GameState:
    def __init__(self):
        self.player_location = "chalet"
        self.inventory = []
        self.turn = 0
        self.max_turns = 240
        self.demon_location = "forest_1"
        self.demon_active = True
        self.ritual_progress = 0
        self.game_over = False
        self.ending = None
        self.noise = 0
        self.scent = {loc: 0 for loc in locations}
        self.flashlight_lit = False
        self.hidden = False
        self.npcs = {
            "jake": {"location": "bungalows", "alive": True, "items": ["matches"], "traded": False, "help": False},
            "lisa": {"location": "refectory", "alive": True, "items": ["notebook"], "traded": False},
            "tom": {"location": "caretaker_house", "alive": True, "items": [], "traded": False}
        }
        self.blocked_exits = {}
        self.traps = {}
        self.clues = {}
        self.item_locations = self.distribute_items()
        self.lore_items = self.distribute_lore()
        self.ambient_counter = 0

    def distribute_items(self):
        items = ["fuel", "car_key", "hose", "gate_key", "journal", "inscription", "note", "knife", "crowbar"]
        possible_locations = ["garage", "fuel_storage", "shed", "caretaker_house", "barn", "chapel", "wooden_statue"]
        random.shuffle(items)
        item_map = {}
        for item, loc in zip(items, random.sample(possible_locations, len(items))):
            item_map[item] = loc
        return item_map

    def distribute_lore(self):
        lore = {
            "journal": "A journal with frantic scribbles: 'The shadow moves at midnight.'",
            "inscription": "Carved into the barn: 'Blood binds the pact.'",
            "note": "A crumpled note: 'It hunts the loudest first.'"
        }
        return lore

    def update_scent_and_noise(self):
        for loc in self.scent:
            self.scent[loc] *= 0.75
        if not self.hidden:
            self.scent[self.player_location] += 1
        if self.noise > 0:
            self.scent[self.player_location] += self.noise * 2
            self.noise -= 1
        self.ambient_counter += 1

    def check_traps(self):
        if self.player_location in self.traps:
            trap = self.traps[self.player_location]["type"]
            if random.random() < 0.4:
                self.game_over = True
                self.ending = "death_trap"
                print(f"The {trap} snaps shut, ending your struggle in an instant. Game over.")
                return True
        return False

# Locations with richer, unsettling descriptions
locations = {
    "chalet": {
        "desc": "The chalet's wooden walls groan faintly, the radio's static a desperate plea drowned by the oppressive silence.",
        "exits": {"north": "forest_1", "east": "bungalows", "south": "lake", "west": "refectory"},
        "items": ["radio"],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "bungalows": {
        "desc": "The bungalows loom like silent sentinels, their cracked windows reflecting a darkness that seems to breathe.",
        "exits": {"west": "chalet", "east": "garage", "north": "sanitarium", "south": "dump"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "lake": {
        "desc": "The lake stretches endlessly, its surface a glassy void swallowing the crimson moon, whispering secrets in ripples.",
        "exits": {"north": "chalet", "west": "dock"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": False
    },
    "dock": {
        "desc": "Rotten planks groan underfoot, the boat swaying as if tugged by unseen hands beneath the water.",
        "exits": {"east": "lake"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": False
    },
    "garage": {
        "desc": "The garage reeks of oil and despair, the car's rusted frame a hollow promise of escape.",
        "exits": {"west": "bungalows", "south": "barn", "east": "fuel_storage"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "barn": {
        "desc": "The barn's shadows twist, a noose dangling from the rafters like an invitation to oblivion.",
        "exits": {"north": "garage", "south": "bunker"},
        "items": ["rope"],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "forest_1": {
        "desc": "Twisted trees bear deep claw marks, the air thick with a silence that presses against your chest.",
        "exits": {"south": "chalet", "north": "forest_2", "east": "watchtower"},
        "items": [],
        "dark": False,
        "locked": False,
        "trap": "pit",
        "hideable": False
    },
    "forest_2": {
        "desc": "The forest hums with faint, unnatural whispers, branches clawing at the sky like skeletal fingers.",
        "exits": {"south": "forest_1", "east": "chapel", "north": "forest_3", "west": "greenhouse"},
        "items": [],
        "dark": False,
        "locked": False,
        "trap": "wolf_trap",
        "hideable": False
    },
    "forest_3": {
        "desc": "A clearing where the air grows colder, the ground scarred as if something vast once stood here.",
        "exits": {"south": "forest_2", "west": "cemetery", "east": "forest_path"},
        "items": [],
        "dark": False,
        "locked": False,
        "trap": "rigged_branch",
        "hideable": False
    },
    "forest_path": {
        "desc": "The path writhes through the trees, shadows pooling like blood in the hollows.",
        "exits": {"west": "forest_3"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": False
    },
    "chapel": {
        "desc": "The chapel's stained glass flickers with crimson light, occult runes pulsing faintly in the gloom.",
        "exits": {"west": "forest_2"},
        "items": ["occult_text"],
        "dark": False,
        "locked": True,
        "key": "chapel_key",
        "hideable": True
    },
    "sanitarium": {
        "desc": "The sanitarium's walls weep with decay, faint echoes of lost voices threading through the silence.",
        "exits": {"south": "bungalows"},
        "items": ["flashlight"],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "refectory": {
        "desc": "The refectory's tables are coated in dust, the air alive with the skittering of unseen vermin.",
        "exits": {"east": "chalet", "north": "shed"},
        "items": ["batteries"],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "cemetery": {
        "desc": "Tombstones tilt like broken teeth, watched over by a wooden statue whose gaze feels alive.",
        "exits": {"east": "forest_3", "west": "wooden_statue"},
        "items": ["shovel"],
        "dark": False,
        "locked": False,
        "hidden_items": ["boat_key"],
        "hideable": False
    },
    "bunker": {
        "desc": "The bunker's darkness is a living thing, coiling around you like a predator's embrace.",
        "exits": {"north": "barn"},
        "items": ["chapel_key"],
        "dark": True,
        "locked": True,
        "key": "bunker_code",
        "hideable": True
    },
    "shed": {
        "desc": "The shed is a chaos of rusted tools, the air sharp with the tang of mildew and metal.",
        "exits": {"south": "refectory"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "watchtower": {
        "desc": "The watchtower leans precariously, its cracked glass framing a camp shrouded in dread.",
        "exits": {"west": "forest_1"},
        "items": [],
        "dark": False,
        "locked": False,
        "trap": "fall",
        "hideable": False
    },
    "greenhouse": {
        "desc": "Broken glass glints in the greenhouse, vines strangling the air with humid decay.",
        "exits": {"east": "forest_2"},
        "items": ["herbs"],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "fuel_storage": {
        "desc": "Fuel cans line the walls, their fumes a suffocating prayer to a god of fire and ruin.",
        "exits": {"west": "garage"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "dump": {
        "desc": "The dump festers with refuse, rats darting through shadows with glinting, hungry eyes.",
        "exits": {"north": "bungalows"},
        "items": ["scrap_metal"],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "caretaker_house": {
        "desc": "The caretaker's house sags, its walls stained with time and something darker.",
        "exits": {"east": "bungalows"},
        "items": [],
        "dark": False,
        "locked": False,
        "hideable": True
    },
    "wooden_statue": {
        "desc": "The wooden statue looms, its carved eyes hollow yet piercing, as if judging your every step.",
        "exits": {"east": "cemetery"},
        "items": [],
        "dark": False,
        "locked": False,
        "hidden_items": ["cryptic_note"],
        "hideable": False
    }
}

# Demon movement with evolving behavior
def move_demon(state):
    if not state.demon_active:
        if state.demon_location in state.traps:
            state.traps[state.demon_location]["turns"] -= 1
            if state.traps[state.demon_location]["turns"] <= 0:
                state.demon_active = True
                del state.traps[state.demon_location]
                print("The demon tears free from the trap, its fury unleashed!")
        return

    possible_exits = list(locations[state.demon_location]["exits"].values())
    if not possible_exits:
        return

    scent_values = [state.scent.get(loc, 0) for loc in possible_exits]
    max_scent = max(scent_values) if scent_values else 0
    candidates = [loc for loc, scent in zip(possible_exits, scent_values) if scent == max_scent] if max_scent > 0 else possible_exits
    new_loc = random.choice(candidates)

    trap = locations[new_loc].get("trap")
    if trap and new_loc not in state.traps and random.random() < 0.35:
        print(f"The demon stumbles into a {trap} at {new_loc}, snarling in rage!")
        state.demon_active = False
        state.traps[new_loc] = {"type": trap, "turns": 4}
        state.ritual_progress -= 1
        return

    state.demon_location = new_loc
    state.clues[new_loc] = random.choice(["claw_marks", "blood_trail", "broken_twigs"])

    if state.ritual_progress > 7:
        if random.random() < 0.4:
            exits = locations[state.demon_location]["exits"]
            if exits:
                blocked_exit = random.choice(list(exits.keys()))
                state.blocked_exits[state.demon_location] = {blocked_exit: 4}
                print(f"The demon slams debris into the {blocked_exit} exit, sealing it shut!")
        elif random.random() < 0.25:
            trap_loc = random.choice(list(locations.keys()))
            locations[trap_loc]["trap"] = "demon_spike"
            print("The demon rigs a deadly trap somewhere in the camp.")

    if state.demon_location == state.player_location and not state.hidden:
        death_type = random.choice(["claw", "choke", "tear", "ritual"])
        if death_type == "claw":
            state.ending = "death_claw"
            print("Claws rend your flesh, the demon's breath hot on your neck. Game over.")
        elif death_type == "choke":
            state.ending = "death_choke"
            print("The demon's grip tightens, your vision fading to black. Game over.")
        elif death_type == "tear":
            state.ending = "death_tear"
            print("Torn apart, your screams echo briefly before silence. Game over.")
        else:
            state.ending = "death_ritual"
            print("The demon captures you, forcing you to your knees. It murmurs in an ancient tongue, then slits your throat with methodical precision. Your blood seeps into the ground, a sacrifice complete. Game over.")
        state.game_over = True

    for npc, data in state.npcs.items():
        if data["location"] == state.demon_location and data["alive"]:
            data["alive"] = False
            state.ritual_progress += 1
            print(f"{npc.capitalize()}'s cries cut off abruptly from {state.demon_location}.")

    state.ritual_progress += 0.015

# Enhanced ambient events for tension
def ambient_event(state):
    if state.ambient_counter % 5 == 0:
        events = [
            "A guttural growl rumbles nearby, too close for comfort.",
            "The wind carries a faint, mournful wail from the trees.",
            "Shadows flicker at the edge of your vision, vanishing when you turn.",
            "A sharp crack echoes, as if something massive stepped on a branch.",
            "The air grows heavy, a metallic tang stinging your nose."
        ]
        print(random.choice(events))

# Robust parser with expanded capabilities
def parse_command(state, command):
    command = command.lower().strip()
    if command in ["quit", "exit"]:
        state.game_over = True
        state.ending = "quit"
        return

    parts = command.split()
    if not parts:
        print("What do you want to do?")
        return

    verb = " ".join(parts[:2]) if " ".join(parts[:2]) in VERB_SYNONYMS else parts[0]
    verb = VERB_SYNONYMS.get(verb, verb)
    obj = " ".join(parts[1:]) if len(parts) > 1 and verb not in ["go", "run"] else " ".join(parts[2:]) if len(parts) > 2 else ""
    direction = parts[1] if len(parts) > 1 and verb in ["go", "run"] else ""

    if direction in DIRECTION_SYNONYMS:
        direction = DIRECTION_SYNONYMS[direction]
    if obj in OBJECT_SYNONYMS:
        obj = OBJECT_SYNONYMS[obj]

    loc = locations[state.player_location]
    is_dark = loc.get("dark", False) and not state.flashlight_lit

    if verb == "go" or verb == "run":
        if direction in loc["exits"]:
            dest = loc["exits"][direction]
            if state.player_location in state.blocked_exits and direction in state.blocked_exits[state.player_location]:
                print("The exit is blocked by twisted wreckage!")
                return
            if locations[dest].get("locked", False):
                key = locations[dest].get("key")
                if key not in state.inventory:
                    print("The way is locked, a barrier to your escape.")
                    return
            if state.check_traps():
                return
            state.player_location = dest
            state.hidden = False
            state.noise += 3 if verb == "run" else 1
            print(f"You {'sprint' if verb == 'run' else 'move'} to {dest}{' loudly!' if verb == 'run' else '.'}")
            if is_dark:
                print("The darkness here is suffocating, hiding all detail.")
            else:
                print(locations[dest]["desc"])
                if state.player_location in state.clues:
                    clue = state.clues[state.player_location]
                    print(f"You notice {clue}, a chilling sign of the demon's presence.")
        else:
            print("That direction leads nowhere.")

    elif verb == "look":
        if is_dark:
            print("The dark conceals everything, a shroud over your senses.")
        else:
            print(loc["desc"])
            items = loc["items"] + [item for item in state.item_locations if state.item_locations[item] == state.player_location]
            if items:
                print(f"Items here: {', '.join(items)}")
            if "hidden_items" in loc:
                print("Something lies concealed nearby...")
            print(f"Exits: {', '.join(loc['exits'].keys())}")
            for npc, data in state.npcs.items():
                if data["location"] == state.player_location and data["alive"]:
                    print(f"{npc.capitalize()} stands here, eyes darting nervously.")

    elif verb == "take":
        if is_dark:
            print("You fumble in the dark, unable to find anything.")
        else:
            items = loc["items"] + [item for item in state.item_locations if state.item_locations[item] == state.player_location]
            if obj in items:
                state.inventory.append(obj)
                if obj in loc["items"]:
                    loc["items"].remove(obj)
                else:
                    del state.item_locations[obj]
                print(f"You pick up the {obj}.")
            else:
                print("There's nothing like that here.")

    elif verb == "search":
        if is_dark:
            print("You search blindly, hands finding only shadows.")
        elif "hidden_items" in loc and ("shovel" in state.inventory or "crowbar" in state.inventory):
            for item in loc["hidden_items"]:
                state.inventory.append(item)
                print(f"You unearth {item} from its hiding place!")
            loc["hidden_items"] = []
        else:
            print("Nothing reveals itself, or you lack the means to find it.")

    elif verb == "use":
        if obj in state.inventory:
            if obj == "rope" and state.player_location == "barn" and "inscription" in state.inventory:
                print("The inscription guides you. The noose claims your breath, a quiet end.")
                state.game_over = True
                state.ending = "suicide"
            elif obj == "fuel" and state.player_location == "dock" and "boat_key" in state.inventory and "hose" in state.inventory:
                print("You fuel the boat and speed away, the camp shrinking behind you!")
                state.game_over = True
                state.ending = "escape_boat"
            elif obj == "car_key" and state.player_location == "garage" and "fuel" in state.inventory:
                print("The car roars to life, carrying you to safety!")
                state.game_over = True
                state.ending = "escape_car"
            elif obj == "gate_key" and state.player_location == "gate":
                print("The gate swings open, freedom just steps away!")
                state.game_over = True
                state.ending = "escape_gate"
            elif obj == "occult_text" and state.player_location == "chapel":
                print("The chant echoes, the demon vanishing in a howl of light!")
                state.game_over = True
                state.ending = "ritual_stopped"
            elif obj == "flashlight" and "batteries" in state.inventory:
                state.flashlight_lit = True
                state.inventory.remove("batteries")
                print("The flashlight flares to life, piercing the gloom.")
            elif obj == "radio":
                print("Static bursts from the radio, shattering the silence!")
                state.noise += 4
            elif obj == "crowbar" and locations[state.player_location].get("locked", False):
                print("The crowbar splinters the lock with a loud snap!")
                state.noise += 3
                locations[state.player_location]["locked"] = False
            else:
                print("That doesn't work here.")
        else:
            print("You don’t possess that.")

    elif verb == "talk":
        if obj in state.npcs and state.npcs[obj]["location"] == state.player_location and state.npcs[obj]["alive"]:
            print(f"{obj.capitalize()} whispers: 'We’re running out of time. Got anything to trade?'")
            if "knife" in state.inventory:
                print(f"You could persuade {obj.capitalize()} to face the demon...")
        else:
            print("No one answers your call.")

    elif verb == "give":
        if "to" in obj:
            item, target = obj.split(" to ")
            if target in state.npcs and state.npcs[target]["location"] == state.player_location and state.npcs[target]["alive"]:
                if item in state.inventory:
                    state.npcs[target]["items"].append(item)
                    state.inventory.remove(item)
                    print(f"You hand the {item} to {target.capitalize()}.")
                    if not state.npcs[target]["traded"]:
                        state.npcs[target]["traded"] = True
                        if state.npcs[target]["items"]:
                            trade_item = random.choice(state.npcs[target]["items"])
                            state.npcs[target]["items"].remove(trade_item)
                            state.inventory.append(trade_item)
                            print(f"{target.capitalize()} offers {trade_item} in thanks.")
                else:
                    print("You don’t have that to give.")
            else:
                print("No such person is here.")
        else:
            print("Give what to whom? (Use: give [item] to [npc])")

    elif verb == "sacrifice":
        if obj in state.npcs and state.npcs[obj]["location"] == state.player_location and state.npcs[obj]["alive"] and "knife" in state.inventory:
            print(f"You trick {obj.capitalize()} into staying. The demon’s growl follows your escape.")
            state.npcs[obj]["alive"] = False
            state.ritual_progress += 1
            state.game_over = True
            state.ending = "exchange_place"
        else:
            print("You can’t sacrifice anyone now. (Need knife and NPC)")

    elif verb == "hide":
        if locations[state.player_location].get("hideable", False):
            state.hidden = True
            print("You slip into hiding, the shadows your fragile shield.")
            state.noise -= 1 if state.noise > 0 else 0
        else:
            print("No refuge exists here.")

    elif verb == "listen":
        if state.noise > 0:
            print("Your own noise drowns out the world.")
        elif state.demon_location == state.player_location and not state.hidden:
            print("A low, guttural hum fills the air, chilling your blood.")
        else:
            print("Faint rustling and distant cries weave through the silence.")

    elif verb == "smell":
        if state.scent[state.player_location] > 5:
            print("A foul stench claws at your throat, the demon’s mark heavy here.")
        else:
            print("The air carries rot and damp earth, a quiet menace.")

    elif verb == "break":
        if obj in loc["items"] and "crowbar" in state.inventory:
            print(f"You smash the {obj} with the crowbar, the noise ringing out!")
            loc["items"].remove(obj)
            state.noise += 5
        else:
            print("You can’t break that, or lack the means.")

    elif verb == "inventory":
        print("You carry:", ", ".join(state.inventory) if state.inventory else "nothing")

    else:
        print("Command unclear. Try: go/run [direction], look, take [item], search, use [item], talk [npc], give [item] to [npc], sacrifice [npc], hide, listen, smell, break [item], inventory, quit")

# Main game loop
def main():
    print("Slasher Camp - Summer 1964")
    print("Created by Hohenstein256")
    print("\n--- Introduction ---")
    print("In the summer of 1964, a group of campers fled their site in terror. A demon known as The Forked One had been summoned, and it sought to claim their souls in a dark ritual. As Sally Brooks, you must survive until dawn, escape the camp, or stop the ritual. The campers fled because the demon was killing them one by one, and now it's your turn to face the horror.")
    input("\nPress Enter to continue...")
    print("\n--- How to Play ---")
    print("You control Sally with text commands. Your goal is to survive until dawn, escape, or stop the ritual.")
    print("Basic commands:")
    print("- go [direction]: Move to a new location (e.g., go north).")
    print("- run [direction]: Move quickly but loudly.")
    print("- look: Examine your surroundings.")
    print("- take [item]: Pick up an item.")
    print("- use [item]: Use an item in your inventory.")
    print("- talk [npc]: Speak with a non-player character.")
    print("- give [item] to [npc]: Trade items with NPCs.")
    print("- hide: Conceal yourself in certain locations.")
    print("- listen: Use your hearing to detect nearby threats.")
    print("- smell: Use your sense of smell to detect clues.")
    print("- inventory: Check what you're carrying.")
    print("- quit: Exit the game.")
    print("\nBe careful—noise attracts the demon, and time is running out.")
    input("\nPress Enter to start the game...")

    state = GameState()
    print(locations[state.player_location]["desc"])

    while not state.game_over:
        state.turn += 1
        state.update_scent_and_noise()

        for loc in list(state.blocked_exits.keys()):
            for exit_dir in state.blocked_exits[loc]:
                state.blocked_exits[loc][exit_dir] -= 1
                if state.blocked_exits[loc][exit_dir] <= 0:
                    del state.blocked_exits[loc]
                    print(f"The {exit_dir} exit at {loc} is free again.")

        if state.turn % 2 == 0:
            move_demon(state)

        ambient_event(state)

        if state.ritual_progress >= 12:
            state.game_over = True
            state.ending = "ritual_complete"
            print("The ritual finishes. Darkness consumes all. Game over.")
            break
        if state.turn >= state.max_turns:
            state.game_over = True
            state.ending = "survive_dawn"
            print("Dawn breaks. You’ve survived. Victory!")
            break

        command = input("> ")
        parse_command(state, command)

    endings = {
        "escape_boat": "You escape by boat, leaving terror behind. Victory!",
        "escape_car": "The car speeds you to safety. Victory!",
        "escape_gate": "Through the gate, freedom is yours. Victory!",
        "ritual_stopped": "The ritual ends, the demon banished. Victory!",
        "suicide": "The noose takes you. A somber end.",
        "death_claw": "Clawed to death. Game over.",
        "death_choke": "Strangled by the demon. Game over.",
        "death_tear": "Torn apart. Game over.",
        "death_trap": "A trap claims you. Game over.",
        "death_ritual": "The demon performs a ritual sacrifice, your blood feeding the earth. Game over.",
        "exchange_place": "You flee, another’s life traded. Dark victory.",
        "ritual_complete": "The ritual succeeds. Game over.",
        "survive_dawn": "You endure until dawn. Victory!",
        "quit": "You abandon the fight."
    }
    print(endings.get(state.ending, "Game over."))

if __name__ == "__main__":
    main()