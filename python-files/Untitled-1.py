def display_ascii_art():
    """
    Display ASCII art text in a clean and readable format.
    This is a self-contained function that prints the art directly.
    """
    ascii_art = [
        " ___       ___  ___  ________   ________  ________     ",
        "|\\  \\     |\\  \\|\\  \\|\\   ___  \\|\\   __  \\|\\   __  \\    ",
        "\\ \\  \\    \\ \\  \\\\\\  \\ \\  \\\\ \\  \\ \\  \\|\\  \\ \\  \\|\\  \\   ",
        " \\ \\  \\    \\ \\  \\\\\\  \\ \\  \\\\ \\  \\ \\   __  \\ \\   _  _\\  ",
        "  \\ \\  \\____\\ \\  \\\\\\  \\ \\  \\\\ \\  \\ \\  \\ \\  \\ \\  \\\\  \\| ",
        "   \\ \\_______\\ \\_______\\ \\__\\\\ \\__\\ \\__\\ \\__\\ \\__\\\\ _\\ ",
        "    \\|_______|\\|_______|\\|__| \\|__|\\|__|\\|__|\\|__|\\|__|",
        "                                                       ",
        "                                                       ",
        "                                                       "
    ]
    
    for line in ascii_art:
        print(line)

# Run the function to display the ASCII art
if __name__ == "__main__":
    display_ascii_art()