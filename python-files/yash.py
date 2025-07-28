import msvcrt

def getch():
    return msvcrt.getch()

def print_box(text):
    width = len(text) + 6
    print("+" + "-" * (width - 2) + "+")
    print("|  " + text + "  |")
    print("+" + "-" * (width - 2) + "+")

def print_separator(char='-', text=""):
    width = len(text) + 6 if text else 40
    print(char * width)

print_box("Hello guys, I'm Yash")
print()
getch()

print_box("I AM A FOR 'A'")
getch()
print_separator()

print_box("I AM B FOR 'BIG'")
getch()
print_separator()

print_box("I AM C FOR 'CHAKKA'")
print()
getch()

print_separator('*', "HIP HIP HOORAY")
print_box("HIP HIP HOORAY")
print_separator('*', "HIP HIP HOORAY")
getch()

