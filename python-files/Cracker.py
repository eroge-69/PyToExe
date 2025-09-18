import random
import itertools

password = "hibeer07"
info = ["hibeer", "iivari", "iippa", "ik", "07", "22", "11", "2007"]

# generate all combinations of lengths 1 to len(info)
all_attempts = []

for r in range(1, len(info)+1):
    for combo in itertools.combinations(info, r):
        # add all permutations of this combination
        all_attempts.extend(itertools.permutations(combo))

# shuffle the order so it’s random
random.shuffle(all_attempts)

tries = 0
while all_attempts:
    attempt = all_attempts.pop()
    guess = ''.join(attempt)
    tries += 1
    if guess == password:
        print("The password was:", guess)
        print("Found after", tries, "tries")
        break
