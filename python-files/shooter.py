import pygame
import math
import random
from copy import copy
import time
import sys

pygame.init()

SW = 1200
SH = 800
screen = pygame.display.set_mode((SW, SH))

pygame.display.set_caption("Shooter Game")

clock = pygame.time.Clock()


RED = (190, 49, 68)

def renderText(what, color, where):
    font = font = pygame.font.SysFont(None, 32)
    text = font.render(what, 1, pygame.Color(color))
    screen.blit(text, where)


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    def to_tuple(self):
        return (self.x, self.y)
    
    def __getitem__(self, index):
        return (self.x, self.y)[index]

    def __len__(self):
        return 2
    
    def magnetude(self) -> float:
        return math.sqrt((self.x**2) + (self.y**2))
    
    def norm(self):
        return self / self.magnetude()
    
    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.x * other.x + self.y * other.y
        
        elif type(other) in (int, float):
            return Vector(self.x * other, self.y * other)

        else:
            raise ValueError(f"unable to perform multiplication with Type <class 'Vector'> and {type(other)}")

    def __truediv__(self, other):
        
        if type(other) in (int, float):
            return Vector(self.x / other, self.y / other)

        else:
            raise ValueError(f"unable to perform division with Type <class 'Vector'> and {type(other)}")

    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x + other.x, self.y + other.y)
        
        else:
            raise ValueError(f"unable to perform addition with Type <class 'Vector'> and {type(other)} (non-Vector)")
        
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(self.x - other.x, self.y - other.y)
        
        else:
            raise ValueError(f"unable to perform subtraction with Type <class 'Vector'> and {type(other)} (non-Vector)")

def getVerctor(pos1, pos2):
    if isinstance(pos1, Vector) and isinstance(pos2, Vector):
        return pos2 - pos1
    
    else:
        raise ValueError(f"unable to get a vector with {type()} and {type()}")

def toVector(nonvec):
    if type(nonvec) in (list, tuple):
        return Vector(nonvec[0], nonvec[1])
    
    else:
        raise ValueError(f"unable to get a vector with {type()} and {type()}")


class Game:
    def __init__(self):
        self.running = True
        self.bulletR = 7
        self.bulletSpeed = 20

        self.intervalls = []

        self.maxShotCooldown = 0 # in seconds
        self.shotCooldown = 0

    def update(self):
        
        renderText(f"Level: {levelManager.level}, HP: {player.hp} | [FPS: {str(int(clock.get_fps()))}]", (255,255,255), (12, 12))

        self.shotCooldown -= 0.01666

        for interval in self.intervalls:
            interval.update()


    def handleInput(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and player.pos.y > 0+player.r:
            player.pos.y -= player.speed

        if keys[pygame.K_s] and player.pos.y < SH-player.r:
            player.pos.y += player.speed

        if keys[pygame.K_a] and player.pos.x > 0+player.r:
            player.pos.x -= player.speed

        if keys[pygame.K_d] and player.pos.x < SW-player.r:
            player.pos.x += player.speed


        if self.shotCooldown <= 0 and (keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]):
            bulletManager.new()
            self.shotCooldown = self.maxShotCooldown

game = Game()

class Player:
    def __init__(self):
        self.pos = Vector(SW/2, SH/2)
        self.hp = 3
        self.speed = 4
        self.r = 20

    def render(self):
        if self.hp <= 0:
            game.running = False
            screen.fill((255,255,255))
            pygame.display.update()
        pygame.draw.circle(screen, RED, self.pos, self.r)

player = Player()

class Bullet:
    def __init__(self):
        
        self.moveVector = getVerctor(player.pos, toVector(pygame.mouse.get_pos())).norm() * game.bulletSpeed
        self.pos = copy(player.pos) + self.moveVector / game.bulletSpeed * (player.r + 5)

        particleManager.new(self.pos, (213, 69, 27), 5)

    def move(self):

        particleManager.new(self.pos, (100, 100, 100), 1)
        self.pos += self.moveVector

        if self.pos.x > SW:
            self.kill()
        elif self.pos.x < 0:
            self.kill()
        elif self.pos.y > SH:
            self.kill()
        elif self.pos.y < 0:
            self.kill()
    
    def kill(self):
        if self in bulletManager.bullets:
            particleManager.new(self.pos, (255, 155, 69), 10)
            bulletManager.bullets.pop(bulletManager.bullets.index(self))

class BulletManager:
    def __init__(self):
        self.bullets = []

    def render(self):
        for bullet in self.bullets[:]:
            bullet.move()
            pygame.draw.circle(screen, RED, bullet.pos, game.bulletR)

    def new(self):
        newBullet = Bullet()
        self.bullets.append(newBullet)

bulletManager = BulletManager()

def randomUnitVector() -> Vector:
    angle = random.uniform(0, 2 * math.pi)
    x = math.cos(angle)
    y = math.sin(angle)
    return Vector(x, y)


class Particle:
    def __init__(self, pos: Vector, color: tuple = RED, r: int = 0):
        self.moveVector = randomUnitVector()
        self.pos = pos + self.moveVector * r
        self.moveVector = randomUnitVector()
        self.color = color
        self.r = 10
    
    def move(self):
        self.pos += self.moveVector
        self.r -= 0.5
        if self.r <= 0:
            self.kill()

    def kill(self):
        if self in particleManager.particles:
            particleManager.particles.pop(particleManager.particles.index(self))

class ParticleManager:
    def __init__(self):
        self.particles = []

    def render(self):
        for part in self.particles[:]:
            part.move()
            pygame.draw.circle(screen, part.color, part.pos, part.r)

    def new(self, pos: Vector, color: tuple = RED, r: int = 0):

        

        for i in range(r):
            newP = Particle(pos, color, r)
            self.particles.append(newP)

particleManager = ParticleManager()



class TypeNormal:
    def __init__(self):
        self.r = 25
        self.hp = 2
        self.speed = 3.3
        self.color = (120, 156, 110)

class TypeFast:
    def __init__(self):
        self.r = 20
        self.hp = 1
        self.speed = 4.5
        self.color = (255, 255, 110)

class TypeStrong:
    def __init__(self):
        self.r = 30
        self.hp = 3
        self.speed = 2.6
        self.color = (110, 146, 100)

class TypeUltra:
    def __init__(self):
        self.r = 60
        self.hp = 10
        self.speed = 1
        self.color = (50, 80, 60)

class Zombie:
    def __init__(self, type):
        typeInfo = type()

        self.pos = Vector(random.randint(0, SW), 0)

        self.speed = typeInfo.speed
        self.r = typeInfo.r
        self.hp = typeInfo.hp
        self.fullHp = self.hp
        self.color = typeInfo.color
        self.width = self.r

        self.last_time_hit = time.time() - 1

        self.vectorToPlayer = Vector(0, 100)

        self.moveVector = None

    def move(self):

        self.moveVector = self.getMoveVector()

        self.bulletCollision()
        self.playerCollision()

        if self.last_time_hit + 1 <= time.time():
            self.pos += self.moveVector





    def playerCollision(self):
            
        if self.vectorToPlayer.magnetude() < self.r + player.r:
            player.hp -= 1
            particleManager.new(player.pos, RED, player.r)
            self.kill()

    def bulletCollision(self):
        
        for bullet in bulletManager.bullets:

            dist = getVerctor(self.pos, bullet.pos).magnetude()

            if game.bulletR + self.r > dist:

                self.hp -= 1
                bullet.kill()

                if self.hp <= 0:
                    self.kill()
                else:
                    self.width = self.r * math.floor(self.r * (self.hp / self.fullHp))


    def getMoveVector(self):
        
        self.vectorToPlayer = getVerctor(self.pos, player.pos)
        return self.vectorToPlayer.norm() * self.speed

    def kill(self):
        if self in zombieManager.zombies:
            particleManager.new(self.pos, self.color, self.r)
            zombieManager.zombies.pop(zombieManager.zombies.index(self))


def getZombieWidth(zombie):
    if zombie.hp <= 0:
        return -1
    else:
        return math.floor(zombie.r * (zombie.hp / zombie.fullHp))


class ZombieManager:
    def __init__(self):
        self.zombies = []

    def render(self):
        for zombie in self.zombies[:]:
            zombie.move()
            pygame.draw.circle(screen, zombie.color, zombie.pos, zombie.r, getZombieWidth(zombie))

    def new(self, type=TypeNormal):
        newZombie = Zombie(str_to_class(type))
        self.zombies.append(newZombie)

zombieManager = ZombieManager()

class Interval:
    def __init__(self, cooldown: float, function):
        self.cooldown = cooldown
        self.time = self.cooldown
        self.function = function

        game.intervalls.append(self)


    def update(self):
        if self.time <= 0:
            self.time = self.cooldown
            self.function()
        else:
            self.time -= 0.01666

LEVELS = [
    {
        "TypeNormal": 4,
        "TypeFast": 4,
        "TypeStrong": 4,
        "TypeUltra": 4
    },
    {
        "TypeNormal": 4
    },
    {
        "TypeNormal": 3.5
    },
    {
        "TypeFast": 6
    },
    {
        "TypeNormal": 3.4
    },
    {
        "TypeNormal": 5,
        "TypeFast": 5
    },
]

class LevelManager:
    def __init__(self):
        self.level = -1

        self.newLevelIn = 600

        self.newLevel()

    def update(self):
        self.newLevelIn -= 1

        if self.newLevelIn <= 0:
            self.newLevelIn = 600
            self.newLevel()
            

    def newLevel(self):
        self.level += 1
        
        game.intervalls = []

        for type in LEVELS[self.level]:
            
            # Pass a lambda to defer the call to zombieManager.new(type)
            game.intervalls.append(Interval(LEVELS[self.level].get(type), lambda t=type: zombieManager.new(t)))
    



levelManager = LevelManager()

while game.running:
    screen.fill((14,14,14))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.running = False
            break
    
    levelManager.update()



    bulletManager.render()

    zombieManager.render()

    particleManager.render()

    player.render()

    game.update()
    game.handleInput()

    pygame.display.update()
    clock.tick(60)
pygame.quit()
























