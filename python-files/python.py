python
import random
def get_random_joke():
jokes = [
"Why don't scientists trust atoms? Because they make up everything!",
"Why did the scarecrow win an award? Because he was outstanding in his field!",
"What do you call fake spaghetti? An impasta!",
"Why do cows have hooves instead of feet? Because they lactose!",
"What did the fish say when it hit the wall? Dam!",
"Why was the math book sad? Because it had too many problems!"
]
return random.choice(jokes)
if name == "main":
print("Here's a random joke for you:\n")
print(get_random_joke())