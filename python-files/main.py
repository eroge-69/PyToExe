
import random

# List of anime characters with name, anime, and image URL
characters = [
    {
        "name": "Monkey D. Luffy",
        "anime": "One Piece",
        "image": "https://cdn.myanimelist.net/images/characters/10/284121.jpg"
    },
    {
        "name": "Naruto Uzumaki",
        "anime": "Naruto",
        "image": "https://cdn.myanimelist.net/images/characters/10/284122.jpg"
    },
    {
        "name": "Goku",
        "anime": "Dragon Ball Z",
        "image": "https://cdn.myanimelist.net/images/characters/5/284123.jpg"
    },
    {
        "name": "Levi Ackerman",
        "anime": "Attack on Titan",
        "image": "https://cdn.myanimelist.net/images/characters/10/261326.jpg"
    },
    {
        "name": "Satoru Gojo",
        "anime": "Jujutsu Kaisen",
        "image": "https://cdn.myanimelist.net/images/characters/6/429355.jpg"
    }
]

# Pick a random character
selected = random.choice(characters)

# Print the result
print("🎴 Random Anime Character:")
print(f"Name : {selected['name']}")
print(f"Anime: {selected['anime']}")
print(f"Image: {selected['image']}")