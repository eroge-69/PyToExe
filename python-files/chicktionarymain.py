from tkinter import *


def chickpage():
    chick = Tk()  # Create a new window for the main game
    chick.geometry("800x600")  # Set the size of the window
    chick.title("Chicktionary")  # Set the title of the window
    chick.config(background="lightblue")  # Set the background color

    # Load and set the icon for the main game window
    mainIcon = PhotoImage(file="chick.png")
    chick.iconphoto(True, mainIcon)  # Set the icon for the window

    welcomeLabel = Label(chick, text="Welcome to Chicktionary!", bg="lightblue", font=("Arial", 24))
    welcomeLabel.pack(pady=20)  # Welcome message
    # remove the welcome message after the pause
    def removeWelcome():
        welcomeLabel.destroy()
    chick.after(3000, removeWelcome)  # Schedule the removal of the welcome message
    Label(chick, text="Santiana 5 foot 3", bg="lightblue", font=("Arial", 18)).pack(pady=20)  # Main game message
    chick.mainloop()  # Start the main loop to display the game window












def login():
    usn = unameEntry.get()  # Get the username from the entry widget
    pword = pwordEntry.get()  # Get the password from the entry widget
    print("Username:", usn)  # Print the username to the console
    print("Password:", pword)  # Print the password to the console
    if usn == "admin" and pword == "password":
        loginpage.destroy()  # Close the login window
        chickpage() # Call the function to open the main game window
    else:
        print("Login failed!")

loginpage = Tk()  # Create a window but not displaying it

loginpage.geometry("420x200")  # Geometry tool, can change size of window
loginpage.title("Chicktionary Login")  # Change titles
loginpage.config(background="lightblue")  # Change background color
# We can change window icon
mainIcon = PhotoImage(file="shrugging.png")
loginpage.iconphoto(True,mainIcon) #Two arguments "True,name" of variable above

#username and password entry
unameEntry = Entry(loginpage, width=30) #Create an entry widget for username
unameEntry.pack(pady=10)  # Pack it into the window with some padding
pwordEntry = Entry(loginpage, width=30, show='*')  # Create an entry widget for password
pwordEntry.pack(pady=10)  # Pack it into the window with some padding

Button(loginpage, text="Login", command=login).pack()



loginpage.mainloop()  # Displays the window
