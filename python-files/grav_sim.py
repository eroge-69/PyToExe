import math as m
import matplotlib.pyplot as plt
import csv as csv
import os


## Constanten
JAAR = 32850         # stappen/jaar
 
G = 6.67430e-20      # km^3 / (kg * s^2) (Binas 7)
AU = 149597870.700   # km (Binas 5)
TIME_STEP = 480*2    # seconden per frame
TOTAL_STEPS = m.floor(16*JAAR) # hoeveelheid stappen


## overig
objects = []

## Objecten
class Vector2D:
    def __init__(self, x, y): 
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __isub__(self, other):
        self.x -= other.x
        self.y -= self.y
        return self
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def turn_right(self):   #draait de vector 90 grade na rechts
        return Vector2D(self.y, -self.x)
    
    def turn_left(self):    #draait de vector 90 graden na links
        return Vector2D(-self.y, self.x)

    def length(self):   #geeft de lengte van de vector op basis van pythagras
        return m.sqrt(self.x**2 + self.y**2)

    def normalize(self): #geeft de genormaaliezeerde vector (lengte == 1)
        l = self.length()
        return Vector2D(self.x / l, self.y / l) if l != 0 else Vector2D(0, 0)

    def to_tuple(self): #veranderd de vector in een tuple 
        return (self.x, self.y)

class Object:
    def __init__(self, pos, mass, velocity):
        self.pos = pos
        self.mass = mass
        self.velocity = velocity
        self.history = []
        objects.append(self)
    
    def calculate_orbit_force(self, other): #berekend de kracht die nodig is voor een stabiel baan om 1 lichaam op basis van Binas 35
        v = m.sqrt(G * self.mass / (distance / 2))
        relative_location = other.pos - self.pos
        direction = relative_location.turn_left()
        force = Vector2D((direction.x/direction.length())*v,(direction.y/direction.length())*v)
        return force

    def get_acceleration(self, others): # berekend de verandering snelheid
        acc = Vector2D(0, 0)
        for other in others:
            if other is not self:
                r = other.pos - self.pos
                distance = r.length()
                if distance == 0:
                    continue
                force_mag = G * other.mass / distance**2
                acc += r.normalize() * force_mag
        return acc

    def update(self, others, dt): #berekend hoe ver het object zig verplaatst
        acc = self.get_acceleration(others)
        self.velocity += acc * dt
        

    def move(self, dt): #verplaatst het object
        self.pos += self.velocity * dt
        self.history.append(self.pos.to_tuple())

    def distance_to(self, other): #berekend de astand tot andere lichaamen
        return (self.pos - other.pos).length()

class Star(Object):
    def __init__(self, pos, mass, velocity, luminosity=3.828e26): #voegde de "luminosity" property toe wat uitdrukt hoe "vel" de ster is
        super().__init__(pos, mass, velocity)
        self.luminosity = luminosity  # W (default: Sun)

class Planet(Object):
    def __init__(self, pos, mass, velocity): #voegt min en max rad en min rad toe voor hoeveel straling de planeet kan hebben voor dat de planeet niet meer leef baar is 
        super().__init__(pos, mass, velocity)
        self.min_rad = 1000 
        self.max_rad =  1500
        self.radiation_history = []
        self.habitability_flags = []

    def calculate_radiation(self, stars): # berekend de hoeveel heid W/m^2 voor deze planeet
        total_radiation = 0
        for star in stars:
            distance = self.distance_to(star) * 1000  # veranderd naar meters
            if distance == 0:
                continue
            intensity = star.luminosity / (4 * m.pi * distance**2)  # W/m^2
            total_radiation += intensity
        self.radiation_history.append(total_radiation) #voegt het toe aan de radition_history voor het maken van het grafiek later
        return total_radiation

    def is_habitable(self, stars): #kijkt of de planeet binnen de grenze valt om leefbaar te zijn
        radiation = self.calculate_radiation(stars)
        habitable = self.min_rad <= radiation <= self.max_rad
        self.habitability_flags.append(habitable)
        print(f"rad: {radiation} | habitable: {habitable}")
        return habitable

## Functies
clear = lambda: os.system('cls') #maakt de console leeg

### CSV functsies
def save_object_positions_csv(objects, filename=f"{os.getcwd()}/object_positions.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Header
        headers = ["Step"]
        for i, obj in enumerate(objects):
            headers += [f"{obj.__class__.__name__}_{i}_x", f"{obj.__class__.__name__}_{i}_y"]
        writer.writerow(headers)

        # Data rows per time step
        for step in range(len(objects[0].history)):
            row = [step]
            for obj in objects:
                x, y = obj.history[step]
                row += [x, y]
            writer.writerow(row)
            


def save_radiation_csv(planet, filename=f"{os.getcwd()}/planet_radiation.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Step", "Radiation (W/m^2)", "Habitable"])
        for step, (rad, hab) in enumerate(zip(planet.radiation_history, planet.habitability_flags)):
            writer.writerow([step, rad, hab])

## sim setup
mass_star = 1.9889e30  # kg (Binas)
distance = 10*AU #afstand tussen de sterren in km

pos1 = Vector2D(-distance / 2, 0)
pos2 = Vector2D(distance / 2, 0)

v = m.sqrt(G * mass_star / (distance / 2)) # Binas 35

vel1 = Vector2D(0, v/2)
vel2 = Vector2D(0, -v/2)

# Create stars
star1 = Star(pos1, mass_star, vel1)
star2 = Star(pos2, mass_star, vel2)

planet = Planet(Vector2D(-3.5*AU, 0) , 5.972e24, Vector2D(0, 0))
planet.velocity = planet.calculate_orbit_force(star1) * 2


objects = [star1, star2, planet]

## de simulatie laten werken
for _ in range(TOTAL_STEPS):
    finished = True
    
    for obj in objects:
        obj.update(objects, TIME_STEP)
    
    for obj in objects:
        obj.move(TIME_STEP)

    
    planet.is_habitable([star1, star2])
    if _ % 10 == 0:
        clear()
    print(f"step: {_}/{TOTAL_STEPS}")
    print(os.getcwd())


## csv's maken
save_object_positions_csv(objects)
save_radiation_csv(planet)

## grafieken maken
plt.figure(figsize=(12, 6))

## baanen Plot
plt.subplot(1, 2, 1)
for obj in objects:
    x, y = zip(*obj.history)
    plt.plot(x, y, label=obj.__class__.__name__)
plt.title("Orbits")
plt.xlabel("x (km)")
plt.ylabel("y (km)")
plt.legend()
plt.axis('equal')

## Radiation Graph
plt.subplot(1, 2, 2)
radiation = planet.radiation_history
time_steps = range(len(radiation))
plt.plot(time_steps, radiation, label="Radiation (W/m²)", color='blue')

plt.axhline(y=planet.min_rad, color='green', linestyle='--', linewidth=1.2, label="Min Habitable")
plt.axhline(y=planet.max_rad, color='orange', linestyle='--', linewidth=1.2, label="Max Habitable")

plt.title("Radiation on Planet Over Time")
plt.xlabel("Time Step")
plt.ylabel("Radiation (W/m²)")
plt.legend()

plt.tight_layout()
plt.show()