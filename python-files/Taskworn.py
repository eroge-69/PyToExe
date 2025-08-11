def greet_user():
    name = raw_input("What's your name? ")  # 'raw_input' in Python 2.7 for strings
    print "Hello, {}! Welcome to Python 2.7.".format(name)

def main():
    greet_user()
    # Just adding a basic loop to show you some more Python 2.7 behavior
    while True:
        choice = raw_input("Do you want to exit? (yes/no): ")
        if choice.lower() == 'yes':
            print "Goodbye!"
            break
        else:
            print "Okay, let's keep going!"

if __name__ == "__main__":
    main()
