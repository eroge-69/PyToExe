import webbrowser

web = {
    "1": ("about", "about:blank"),
    "2": ("set", "https://www.github.com"),
    "3": ("wiki", "https://type.wiki"),
    "4": ("drive", "https://drive.google.com"),
    "5": ("none", None)
}

def show():
    print("\nInput")
    for key, (name, _) in web.items():
        print(f"{key}. {name}")

def open_web(choice):
    name, url = web.get(choice, (None, None))
    if url:
        print(f"\n open {name}")
        webbrowser.open(url)
    elif name == "none":
        print("\nend")
    else:
        print("\ninvalid")

def main():
    while True:
        show()
        choice = input("➡ input : ").strip()
        if choice == "5":
            open_web(choice)
            break
        else:
            open_web(choice)

if __name__ == "__main__":
    main()