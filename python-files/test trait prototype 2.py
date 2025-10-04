import random
import matplotlib.pyplot as pt
# Parameters
population_size = int(input('Mice Population:'))
generations = int(input('Total  Generations:'))
environment = input('light/dark:')

# Create initial population (half light, half dark)
population = ["L"] * (population_size // 2) + ["D"] * (population_size // 2)
light_count = []
dark_count = []

for g in range(generations + 1):
    light = population.count("L")
    dark = population.count("D")
    light_count.append(light)
    dark_count.append(dark)
    print("Generation", g, ": Light =", light, "Dark =", dark)

    # Skip last generation
    if g == generations:
        break

    # Survival step
    survivors = []
    for indiv in population:
        if environment == "light" and indiv == "L":
            if random.random() < 0.9:  
                survivors.append(indiv)
        elif environment == "dark" and indiv == "D":
            if random.random() < 0.9:
                survivors.append(indiv)
        else:
            if random.random() < 0.2:  # bad camouflage
                survivors.append(indiv)

    # Reproduction step (make next generation same size)
    if len(survivors) == 0:
        survivors = ["L"]  # avoid extinction
    population = [random.choice(survivors) for _ in range(population_size)]


pt.figure(figsize = (10,8)) 
pt.plot(range(generations + 1), light_count, marker = "o")
pt.plot(range(generations + 1), dark_count, marker = "o")
pt.xlabel(f'Environment: {environment} Generations')
pt.ylabel('Mice')
pt.title("Mice Populations over time")
pt.legend()
pt.grid(True)
pt.show()
