# Eric Lewis
# TextBasedGame.py


# Starting room and keeps track of where player is
current_room = 'Temple Entrance'

#Player's inventory
inventory = []

# Dictionary linking rooms and possible moves (taken from guidelines)
rooms = {
    'Temple Entrance': {'East': 'Crystal Nexus'},
    'Crystal Nexus': {'West': 'Temple Entrance', 'East': 'Ruined Citadel', 'North': 'Whispering Halls', 'South': 'Shattered Spire'},
    'Whispering Halls': {'South': 'Crystal Nexus', 'East': 'Veiled Sanctuary'},
    'Veiled Sanctuary': {'West': 'Whispering Halls'},
    'Shattered Spire': {'North': 'Crystal Nexus', 'East': 'Forsaken Vault'},
    'Forsaken Vault': {'West': 'Shattered Spire'},
    'Ruined Citadel': {'West': 'Crystal Nexus', 'North': 'Tomb of ka\'ah'},
    'Tomb of ka\'ah': {'South': 'Ruined Citadel'},
}

#Dictionary that assigns items to rooms
items = {
    'Temple Entrance': None,
    'Crystal Nexus': 'celestial prism',
    'Whispering Halls': 'echo of life',
    'Veiled Sanctuary': 'mysterious tome',
    'Shattered Spire': 'soul-bound key',
    'Forsaken Vault': 'forgotten hourglass',
    'Ruined Citadel': 'heart of ka\'ah',
    'Tomb of ka\'ah': None,

}

# Track which rooms have been visited
visited = {
    'Temple Entrance': False,
    'Crystal Nexus': False,
    'Whispering Halls': False,
    'Veiled Sanctuary': False,
    'Shattered Spire': False,
    'Forsaken Vault': False,
    'Ruined Citadel': False,
    'Tomb of ka\'ah': False,
}

# Function to describe each room and encounter
def describe_room(room):
    if not visited[room]:
        if room == 'Temple Entrance':
            print("\n"
                  "You stand at the entrance to a grand temple.\nDespite its less than stellar state, it still gives off an air of majesty.\n")
        elif room == 'Crystal Nexus':
            print("\n"
                  "Before you stands a mighty crystal structure that pulses with Aether.\nWaiting for you in front of the crystal is a wraith that radiates strength.\nThey clutch a crystal in their right hand as their glowing red eyes meet yours.\n")
        elif room == 'Whispering Halls':
            print("\n"
                  "You enter a grand library filled to the brim with ancient tomes and crystals that no doubt hold vast fonts of knowledge.\nThe air is filled with the sound of disembodied whispers giving the illusion that the hall is filled with scholars.\nAlas the great halls of this once great library seem empty save for a wraith who wears garb bearing the crest of this temple: the mark of Ka'ah.\nAs you get near the Wraith's eyes fall on you.\n")
        elif room == 'Veiled Sanctuary':
            print("\n"
                  "You enter a room deep within the great library.\nThe room is filled with scattered tomes, crystals, and the mummified remains of what you can only assume was once food.\nIt's clear that this room was once the personal study of someone in the past, but now it is silent and abandoned.\nWaiting for you within the spacious study is another Wraith. You know the drill at this point and prepare yourself.\n")
        elif room == 'Shattered Spire':
            print("\n"
                  "You approach the shattered and broken figure of a once great spire.\nIt is clear that this once great structure saw a fierce battle to end up in its current state.\nAs you get near the entrance, from within the great doors appears a Wraith. It regards you with contempt, and brandishes an elegant staff.\nReady yourself.")
        elif room == 'Forsaken Vault':
            print("\n"
                  "You enter a room filled with relics and myriad treasures within the old spire.\n"
                  "It is clear from this room alone that Ka'ah was extremely wealthy,\n"
                  "and you wonder if maybe you could take some of this stuff with you once you have dealt with him.\n"
                  "As if sensing your profane intentions, a Wraith appears and lets out an enraged shriek.\n"
                  "Seems tomb raiding will have to wait...\n")
        elif room == 'Ruined Citadel':
            print("\n"
                  "This place is is the entrance to the mighty citadel that sits deep within the temple.\n"
                  "It is filled with the empty suits of armor battered, broken, and strewn about.\n"
                  "As you enter you find more and more signs of death and violence, until you reach a pair of ornate doors.\n"
                  "Carved into the doors are words:\n"
                  "'The Immortal Ka'ah was as formidable as we feared and would not die no matter what we did.\n"
                  "With no choice we sealed him and his soul-bearers here to remain until the end of time.\n"
                  "Along with ourselves.\n"
                  "O, whoever shall read this, go no further.\n"
                  "Lest you release Ka'ah and make our sacrifice for naught.'\n"
                  "As if one cue, one of the seemingly empty suits of armor rises to face you.\n"
                  "It raises its mighty greatsword in challenge.\n")
        elif room == 'Tomb of ka\'ah':
            global playing
            print("You approach the doors and despite the dire warning written, you open them.\n"
                  "As you enter the wind rushes into the room from the outside, and the doors slam shut behind you.\n"
                  "No going back, it seems. It's do or die.\n"
                  "Waiting for you upon his regal throne is Ka'ah in all his radiance.\n"
                  "You pause for a moment in trepidation, but you steel your nerves and fight\n"
                  )

            if len(inventory) != 6:
                print("\n"
                      "You fight long and hard, but no matter what you do, Ka'ah refuses to fall\n"
                      "It's at that moment you realize Ka'ah had truly achieved his goal.\n"
                      "You wonder if you had missed something, but its too late to regret.\n"
                      "You will have a lifetime to wonder, though as you shall now be a thrall of Ka'ah forever.\n"
                      "Game over.\n"
                      "Thanks for playing!\n"
                      )
                playing = False
            elif len(inventory) == 6:
                print("\n"
                      "The fight with Ka'ah is brutal and fierce.\n"
                      "You hadn't even heard of Ka'ah until just a few weeks ago,\n"
                      "and yet he's probably one of the strongest beings you've faced in your adventures so far.\n"
                      "You wonder what might've happened had you not retrieved all of the objects that contained a part of Ka'ah.\n"
                      "Had they not been able to resonate with him and render him vulnerable, you would have surely fallen here.\n"
                      "In the end though Ka'ah does not rage or curse. He continues to fight as best he can.\n"
                      "It almost feels as if he is acknowledging you in a way.\n"
                      "Eventually after a time, Ka'ah begins to falter.\n"
                      "'To think upon awakening I'd meet someone of your strength. You would have made the perfect puppet.\n"
                      "I shall not fall again without giving it my all. Let's see who shall rise and who shall fall!'\n"
                      "With a final clash of might the winner is decided and the body of Ka'ah begins to break down\n"
                      "as he is dealt a lethal blow.\n"
                      "'That I might fail again. Was it truly not meant to be? I wonder was this what you warned me about?\n"
                      "Was i truly the fool to dismiss your council Lak'ul?'\n"
                      "With these final words Ka'ah full fades disappearing from the world forever.\n"
                      "With your victory this world and the rest of Elysium is free from the threat of Ka'ah!\n"
                      "\n"
                      "You win!\n"
                      "\n"
                      "Thanks for playing!\n")
                playing = False




        visited[room] = True
    else:
        print(f"\n"
              f"You have returned to the {room.lower()}.")
    return True

#Handles getting items from rooms
def get_item(item):
    item = item.lower()
    current_item = items[current_room]

    if current_item is None or current_item.lower() != item:
        print("Cannot get item")
        return

    inventory.append(current_item)
    items[current_room] = None

    if current_item.lower() == 'celestial prism':
        print("\n"
              "Soon after meeting the gaze of the Wraith, it attacks.\n"
              "The opponent is strong, but with your years of experience and level head you prevail.\n"
              "With an unwilling gaze it falls and slowly turns into particles of light.\n"
              "'I have failed you master' it says mournfully before it vanishes.\n"
              "You have obtained the Celestial Prism\n")
    elif current_item.lower() == 'echo of life':
        print("\n"
              "The robed Wraith attacks!\n"
              "After another fierce battle, the wraith falls in silence.\n"
              "As it disappears it leaves behind an object akin to a confluence of Aether.\n"
              "As you store it away in your subspace, for the first time in ages, the hall is quiet.\n"
              "You have obtained the Echo of Life.\n")
    elif current_item.lower() == 'mysterious tome':
        print("\n"
              "Once again you find yourself assaulted by a Wraith.\n"
              "The Wraith is cunning and fights with the skill and knowledge of a seasoned veteran.\n"
              "After a tense battle, the Wraith can no longer fight.\n"
              "Unlike the others this Wraith looks up at you before it vanishes and speaks.\n"
              "'Save my friend from himself. I beseech you, end the reign of Ka'ah.'\n"
              "With these final words spoken, the Wraith vanishes leaving behind a mysterious tome.\n"
              "You have obtained the Mysterious Tome.\n")
    elif current_item.lower() == 'soul-bound key':
        print("\n"
              "The Wraith attacks with no mercy, but you weather the storm of attacks.\n"
              "Eventually you find an opening allowing you to land a devastating blow.\n"
              "With a deep scowl on it's face it still tries to rise despite it's body beginning to fade.\n"
              "'Me? Defeated by an outsider? I refuse to accept it!'\n"
              "Alas, despite it's objections it vanishes into motes of light.\n"
              "Left behind is a strangely shaped key that seems to glow with a pale light.\n"
              "You obtained the Soul-bound Key.\n")
    elif current_item.lower() == 'forgotten hourglass':
        print("\n"
              "You barely get time to ready yourself before the wrathful Wraith attacks.\n"
              "'You dare?! To come here, I will make sure you don't have an easy death thief!'\n"
              "The wrathful wraith keeps up his attack.\n"
              "In the crossfire many of the most expensive looking relics get destroyed.\n"
              "Your heart weeps at the wonton loss of potential money.\n"
              "After refusing to 'let the the wraith kill you' as it's demanded many times,\n"
              "You manage to subdue the wraith to who screams and hurls insults at you while it fades.\n"
              "In the end the only thing left behind is a small hourglass and a vault full of destroyed treasure.\n"
              "You obtained the Forgotten hourglass. Though for some reason you don't feel very happy.\n")
    elif current_item.lower() == 'heart of ka\'ah':
        print("\n"
              "You beckon the suit of armor in challenge.\n"
              "The armored wraith races towards you with terrifying speed.\n"
              "Soon you find yourself standing in a a half destroyed room.\n"
              "The armored Wraith is forced to kneel as its body gives out.\n"
              "'Fool, you will regret facing lord Ka'ah...'\n"
              "With that it's body fades leaving behind a strange looking object that pulses steadily\n"
              "You obtained the Heart of Ka'ah.\n")



#Welcome message and intro
print(
    "\n"
    "The world is a dream, split into two realms: the false reality and Elysium. One day, the Dreamer of this great vision will awaken, and all will end.\n"
    "But that is the distant future; for now, across Elysium, stories are still being written and legends still being born.\n"
    "\n"
    "You are Sam Elton. Once a normal human from Earth living a quiet, ordinary life, you have clashed with beings who could be called gods and saved countless worlds.\n"
    "You and your companions have begun to be hailed as heroes across Elysium. Now, the world you stand upon calls for your aid.\n"
    "\n"
    "Its people are plagued by nightmares and haunted by strange voices,\na dark omen that may herald the return of Ka'ah, the terrible sorcerer who once ruled this land with an iron fist.\n"
    "Ka'ah sought true immortality and ultimate power; some say he succeeded. Though he was overthrown and sealed away long ago, the seal now shows signs of weakening.\n"
    "Elysium is already rife with strife and treachery as the Great Selection nears its end.\nStopping Ka'ah from returning and from tipping the balance into chaos has become paramount.\n"
    "\n"
    "Welcome to Forsaken Dream: Legacy of Ka'ah. Below are the instructions:\n"
    "Enter directions in order to move between rooms and type 'get' followed by an item to retrieve it.\n"
    "Gather the objects that house the soul of Ka'ah before confronting him or else he will be unstoppable.\n"
    "Good luck.\n"
    )

# Gameplay loop
playing = True
while playing:
    describe_room(current_room)

    # If the game ended inside describe_room, stop the loop
    if not playing:
        break

    # Show available directions and items
    room_keys = ", ".join(rooms[current_room].keys())
    command = input("Inventory: {}\n"
                    "Available commands:\n"
                    "Items: {}\n"
                    "Directions: {}\n"
                    "Enter a direction (North, South, East, West), get an item, or 'exit': ".strip().format(
                        inventory, items[current_room], room_keys))

    # Exit command
    if command.lower() == 'exit':
        print("\n"
              "Without his defeat, the return of Ka'ah is neigh.\n"
              "The hopes of this world are lost.\n"
              "The End.\n"
              "\n"
              "Thanks for playing!\n")
        break

    # Check if the command is a valid move
    elif command.capitalize() in rooms[current_room]:
        current_room = rooms[current_room][command.capitalize()]
    elif command.lower().startswith('get '):
        item_name = command[4:].strip().lower()
        get_item(item_name)
    else:
        print("You can't go that way")
