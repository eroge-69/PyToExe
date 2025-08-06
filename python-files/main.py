import tkinter as tk
#all code from chatgpt, i am trying to learn some python and tkinter :) 
#trying to learn how tkinter works and how to make a app with it!!
root = tk.Tk()  # this defines the root first, am assuming you have to do this first.

# Now it's safe to configure the window
root.title("riads app")             
root.geometry("1080x1080")         
root.resizable(True, False)      
root.configure(bg="lightblue")   

# Add something to see
label = tk.Label(root, text="hello!!!! this is my app, source code is here: https://replit.com/@yacinebaya9/riad1", bg="red") #bg color of label text and the label text is the visual label in the window of the app
label.pack() #am assuming that this is a command to display the label

root.mainloop() #am assuming this is a command to loop the app????
