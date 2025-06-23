import webbrowser
print("hello")
print("who are you?")
answer = input("Please enter your name: ")
print("Hello " + answer)

while True:
    print("How old are you?")
    age = input("Please enter your age: ")
    if age.isdigit():
        age = int(age)
        if age < 18:
            print("You are not of legal age yet.")
        else:
            webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            break
    else:
        print("Please enter a valid number for your age.")
        age = input("Please enter your age: ")
exit()