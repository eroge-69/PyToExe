
places = {
    "Eiffel Tower": {
        "height": "300m",
        "who build": "Gustave Eiffel",
        "location": "Paris, France",
        "year": "1889"
    },
    "Taj Mahal": {
        "height": "73m",
        "who build": "Shah Jahan",
        "location": "Agra, India",
        "year": "1643"
    },
    "Statue of Liberty": {
        "height": "93m",
        "who build": "Frédéric Auguste Bartholdi",
        "location": "New York, USA",
        "year": "1886"
    },
    "Great Wall of China": {
        "height": "Varies",
        "who build": "Various Chinese dynasties",
        "location": "China",
        "year": "7th century BC"
    },
    "Christ the Redeemer": {
        "height": "30m",
        "who build": "Paul Landowski",
        "location": "Rio de Janeiro, Brazil",
        "year": "1931"
    }

}

# Main loop
while True:
    place = input("\nEnter the name of the place (or 'exit' to quit): ").strip()
    if place.lower() == "exit":
        break

    if place in places:
        query = input("What do you want to know? (height / who build / location / year): ").strip().lower()
        if query in places[place]:
            print(f"{query.title()} of {place}: {places[place][query]}")
        else:
            print("Sorry, I don't have that information.")
    else:
        print("Place not found. Try another.")