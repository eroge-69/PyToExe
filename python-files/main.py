Je ne peux pas générer de fichiers directement téléchargeables, mais je peux te fournir le **main.py complet prêt à copier-coller**, avec toutes les fonctionnalités Twitch Chaos EXTREME intégrées (multijoueur, sorts, mini-boss, leaderboard, effets visuels et sonores).

---

**main.py**

```python
import asyncio
import random
import pygame
from twitchio.ext import commands
import os

# --- CONFIG TWITCH ---
TWITCH_TOKEN = "oauth:VOTRE_TOKEN"
TWITCH_NICK = "VotrePseudo"
TWITCH_CHANNEL = "NomDuChannel"

# --- CONFIG PYGAME ---
WIDTH, HEIGHT = 1000, 700
PLAYER_SIZE = 40
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Twitch Chaos Arena EXTREME")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont(None, 24)
font_big = pygame.font.SysFont(None, 36)

# --- EFFETS SONORES ---
pygame.mixer.init()
sound_paths = {
    "fire": "sounds/fire.wav",
    "freeze": "sounds/freeze.wav",
    "bomb": "sounds/bomb.wav",
    "powerup": "sounds/powerup.wav",
    "hit": "sounds/hit.wav"
}
sounds = {}
for k,v in sound_paths.items():
    if os.path.exists(v):
        sounds[k] = pygame.mixer.Sound(v)

# --- DONNÉES DU JEU ---
players = {}
effects = []
obstacles = []
powerups = []
bosses = []
events = []

# --- CLIENT TWITCH ---
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix="!", nick=TWITCH_NICK, initial_channels=[TWITCH_CHANNEL])

    async def event_ready(self):
        print(f"Connecté à Twitch en tant que {TWITCH_NICK}")

    async def event_message(self, message):
        global players, effects
        if message.echo:
            return
        viewer = message.author.name
        msg = message.content.lower()

        if msg == "!join" and viewer not in players:
            x = random.randint(50, WIDTH-50)
            y = random.randint(50, HEIGHT-50)
            color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
            players[viewer] = {"rect": pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE), "score":0, "speed":5, "color":color}
            await message.channel.send(f"{viewer} a rejoint l'arène EXTREME !")

        if viewer in players:
            player = players[viewer]
            r = player["rect"]
            s = player["speed"]
            if msg == "!up": r.y -= s
            elif msg == "!down": r.y += s
            elif msg == "!left": r.x -= s
            elif msg == "!right": r.x += s
            elif msg == "!fire":
                effects.append({"type":"fire","x":r.centerx,"y":r.centery,"owner":viewer})
                if "fire" in sounds: sounds["fire"].play()
            elif msg == "!freeze":
                effects.append({"type":"freeze","target":viewer,"duration":60})
                if "freeze" in sounds: sounds["freeze"].play()
            elif msg == "!speed": player["speed"] = 10
            elif msg == "!bomb":
                effects.append({"type":"bomb","x":r.centerx,"y":r.centery,"owner":viewer,"radius":80})
                if "bomb" in sounds: sounds["bomb"].play()

        await self.handle_commands(message)

bot = Bot()

# --- FONCTIONS DE JEU ---
def spawn_events():
    if random.randint(0,300)==0:
        for _ in range(10):
            x = random.randint(0, WIDTH)
            effects.append({"type":"fire","x":x,"y":0,"owner":"event"})
        events.append("Tempête de feu !")

    if random.randint(0,500)==0:
        bosses.append(pygame.Rect(random.randint(50,WIDTH-100),-100,100,100))
        events.append("Mini-boss géant apparu !")


def draw_game():
    global effects, obstacles, powerups, bosses, events

    screen.fill((5,5,30))

    for obs in obstacles:
        pygame.draw.rect(screen,(255,0,0),obs)
        obs.y += 3
    obstacles[:] = [o for o in obstacles if o.y<HEIGHT]

    for pu in powerups:
        pygame.draw.circle(screen,(0,255,0),(pu["x"],pu["y"]),15)

    for boss in bosses:
        pygame.draw.rect(screen,(0,0,255),boss)
        boss.y += 2
    bosses[:] = [b for b in bosses if b.y<HEIGHT]

    for name,data in players.items():
        r = data["rect"]
        pygame.draw.rect(screen,data["color"],r)
        text = font_small.render(f"{name}: {data['score']}", True, (255,255,255))
        screen.blit(text,(r.x,r.y-20))

    for effect in effects[:]:
        if effect["type"]=="fire":
            pygame.draw.circle(screen,(255,165,0),(effect["x"],effect["y"]),15)
            effect["y"]+=7
            for p_name,pdata in players.items():
                if p_name!=effect["owner"] and pdata["rect"].collidepoint(effect["x"],effect["y"]):
                    pdata["score"]-=5
                    if "hit" in sounds: sounds["hit"].play()
                    effects.remove(effect)
        elif effect["type"]=="freeze":
            target = effect["target"]
            if target in players: players[target]["speed"] = 1
            effect["duration"] -= 1
            if effect["duration"]<=0:
                if target in players: players[target]["speed"] = 5
                effects.remove(effect)
        elif effect["type"]=="bomb":
            pygame.draw.circle(screen,(255,0,255),(effect["x"],effect["y"]),effect["radius"],3)
            for pdata in players.values():
                if abs(pdata["rect"].centerx-effect["x"])<effect["radius"] and abs(pdata["rect"].centery-effect["y"])<effect["radius"]:
                    pdata["score"]-=10
            effect["radius"] -= 5
            if effect["radius"]<=0: effects.remove(effect)

    if random.randint(0,50)==0: obstacles.append(pygame.Rect(random.randint(0,WIDTH-30),-30,30,30))
    if random.randint(0,200)==0:
        x=random.randint(50,WIDTH-50)
        y=random.randint(50,HEIGHT-50)
        powerups.append({"x":x,"y":y})
        if "powerup" in sounds: sounds["powerup"].play()

    spawn_events()

    leaderboard = sorted(players.items(), key=lambda x:x[1]["score"], reverse=True)[:5]
    y=10
    for name,pdata in leaderboard:
        text = font_big.render(f"{name}: {pdata['score']}", True, (255,255,0))
        screen.blit(text,(WIDTH-300,y))
        y+=40

    y_event = HEIGHT-100
    for e in events[-5:]:
        text = font_big.render(e, True, (255,0,0))
        screen.blit(text,(10,y_event))
        y_event+=30

    pygame.display.flip()

# --- BOUCLE PRINCIPALE ---
async def main():
    asyncio.create_task(bot.start())
    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
                pygame.quit()
                return
        draw_game()
        for pdata in players.values(): pdata["score"] += 1
        clock.tick(30)

asyncio.run(main())
```

---

Avec ce fichier `main.py`, tu pourras suivre les étapes précédentes pour générer le `.exe` avec PyInstaller et créer le ZIP complet prêt à streamer.
