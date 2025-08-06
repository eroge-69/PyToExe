import tkinter as tk
import random
import subprocess
import sys

score = 0   # Initialize global score variable

def bird_logic():
    global bird_y
    
    bird_y += 10        # Increases the y value of the bird window by 10, allowing the window to slowly move down the screen 
    bird.geometry(f"+{bird_x}+{bird_y}")    # Updates the bird window with the new values
    
    if bird_y < bird_screen_height - bird_window_height:    # Validates if the bird window hasn't reached the bottom of the screen
        bird.after(50, bird_logic)  # Loops the bird_logic function after 50 milliseconds has passed 
    else:
        quit_menu() # Runs the quit_menu function if the bird window has reached the bottom of the screen

# When the program is initially ran, all the windows start in the same location for a frame. This counts as a collision, which calls the quit_menu function.
# So to counter this, "hasattr" is used which can declare a variable onto the function. Then when the function is ran for the first time, it doesnt count the collision.  
def bird_collision():
    if not hasattr(bird_collision, "counter"):  # Defines a variable onto the bird_collision function called "counter"
        bird_collision.counter = 0  # Sets the variable bird_collision.counter to 0
        
    # Abreviating the variable names 
    tpx, tpy, tpw, tph = top_pipe.winfo_x(), top_pipe.winfo_y(), top_pipe.winfo_width(), top_pipe.winfo_height()
    bpx, bpy, bpw, bph = bottom_pipe.winfo_x(), bottom_pipe.winfo_y(), bottom_pipe.winfo_width(), bottom_pipe.winfo_height()
    bx, by, bw, bh = bird.winfo_x(), bird.winfo_y(), bird.winfo_width(), bird.winfo_height()  
    
    if ((tpx < bx + bw and tpx + tpw > bx and tpy < by + bh and tpy + tph > by) or (bpx < bx + bw and bpx + bpw > bx and bpy < by + bh and bpy + bph > by)):    # Check if the windows overlap
        if bird_collision.counter == 0: # Checks if bird_collision.counter is equal to 0
            bird_collision.counter = 1  # Sets bird_collision.counter to 1
        else:
            quit_menu() # Calls the quit_menu function if the bird window overlaps one of the pipe windows
            
    bird.after(50, bird_collision)  # Loops the bird_collision function after 50 milliseconds has passed

# Note the score will increase by 10 each time a pipe has been passed as the function runs 10 times each time the bird passes a pipe
def update_score():
    global score, top_pipe_x, bird_x
    
    if top_pipe_x + top_pipe_window_width < bird_x: # Check if bird window position has passed the pipes
        score += 1  # Increases the score variable by 1
        score_label.config(text=f"Score: {score}")  # Updates the score text with the correct score

def top_pipe_logic():
    global top_pipe_x
    
    top_pipe_x -= 10    # Decreases the x value of the top pipe window by 10, allowing the top pipe window position to move slowly to the left each time the function is called 
    top_pipe.geometry(f"+{top_pipe_x}+{top_pipe_y}")    # Updates the top_pipe window with the new values
    
    update_score()  # Calls the update_score function
    
    if top_pipe_x + top_pipe_window_width > 0:  # Checks if the top_pipe window hasn't reached the far left side of the screen
        top_pipe.after(50, top_pipe_logic)  # Loops the top_pipe_logic function after 50 milliseconds has passed 
    else:
        top_pipe.destroy()  # Destroys the top_pipe window if the window has reached the far left side of the screen
                
def bottom_pipe_logic():
    global bottom_pipe_x
    
    bottom_pipe_x -= 10 # Decreases the x value of the bottom pipe window by 10, allowing the bottom pipe window position to move slowly to the left each time the fuction is called
    bottom_pipe.geometry(f"+{bottom_pipe_x}+{bottom_pipe_y}")   # Updates the bottom_pipe window with the new values
    
    if bottom_pipe_x + bottom_pipe_window_width > 0:    # Checks if the bottom_pipe window hasn't reached the far left side of the screen
        bottom_pipe.after(50, bottom_pipe_logic)    # Loops the bottom_pipe_logic function after 50 milliseconds has passed
    else:
        bottom_pipe.destroy()   # Destroys the bottom_pipe window if the window has reached the far left side of the screen
        main()  # Calls the main functions

def key_pressed(event):
    if event.keysym == "space": # Checks if the spacebar was pressed
        global bird_y
        bird_y -= 150   # Decreases the y value of the bird window, allowing the window to move up the screen
        bird.geometry(f"+{bird_x}+{bird_y}")    # Updates the bird window with the new values

def quit_menu():
    bird.destroy()  # Destroys the bird window
    top_pipe.destroy()  # Destroys the top pipe window
    bottom_pipe.destroy()   # Destroys the bottom pipe window
    
    # Makes a window for the quit menu
    quit_win = tk.Tk()
    quit_win.title("Game Over")
    quit_window_width = 300
    quit_window_height = 200
    quit_screen_width = quit_win.winfo_screenwidth()
    quit_screen_height = quit_win.winfo_screenheight()
    quit_x = (quit_screen_width - quit_window_width) // 2
    quit_y = (quit_screen_height - quit_window_height) // 2
    quit_win.geometry(f"{quit_window_width}x{quit_window_height}+{quit_x}+{quit_y}")
    quit_label = tk.Label(quit_win, text="U DED", font=("Helvetica", 24))
    quit_label.pack(pady=30)
    quit_button = tk.Button(quit_win, text="AGAIN", font=("Helvetica", 16), command=restart_program)
    quit_button.pack()
    quit_win.mainloop() # Starts the event loops for the quits menu

# Allows the program to be re-run
def restart_program():
    subprocess.Popen([sys.executable] + sys.argv)
    sys.exit()

def main():
    global top_pipe, top_pipe_x, top_pipe_y, top_pipe_window_width, bottom_pipe, bottom_pipe_x, bottom_pipe_y, bottom_pipe_window_width

    pipe_diff_gen = random.randint(0, 200) # Declares a variable which generates a random number from 0 - 200. This variable will be used to change the heights of the pipes allowing variation of where is gap will be. 
    direction = random.randint(1, 2)    # Declares a variable which can either be 1 or 2
    if direction != 1:  # Checks if the direction variable is not 1
        pipe_diff_gen = -abs(pipe_diff_gen) # Makes the pipe_diff_gen variable a negative number
    
    # Makes a window for the pipe at the top of the screen
    top_pipe = tk.Tk()
    top_pipe.configure(background='green')  # Sets the background colour of the window to be green, to display that it is a pipe like in the original flappy bird
    top_pipe_window_width = 50
    top_pipe_window_height = 300 + pipe_diff_gen    # Sets the window height to a base level of 300 and offsets it by adding the number associated with pipe_diff_gen
    top_pipe_x = 1000
    top_pipe_y = 0
    top_pipe.geometry(f"{top_pipe_window_width}x{top_pipe_window_height}+{top_pipe_x}+{top_pipe_y}")

    # Makes a window for the pipe at the bottom of the screen
    bottom_pipe = tk.Tk()
    bottom_pipe.configure(background='green')   # Sets the background colour of the window to be green, to display that it is a pipe like in the original flappy bird
    bottom_pipe_screen_height = bottom_pipe.winfo_screenheight()
    bottom_pipe_window_width = 50
    bottom_pipe_window_height = 300 - pipe_diff_gen # Sets the window height to a base level of 300 and offsets it by subtracting the number associated with pipe_diff_gen 
    bottom_pipe_x = 1000
    bottom_pipe_y = bottom_pipe_screen_height - bottom_pipe_window_height
    bottom_pipe.geometry(f"{bottom_pipe_window_width}x{bottom_pipe_window_height}+{bottom_pipe_x}+{bottom_pipe_y}")    
    
    top_pipe_logic()    # Calls the top_pipe_logic function
    bottom_pipe_logic() # Calls the bottom_pipe_logic function
    bird_collision()    # Calls the bird_collision function
    
    bird.bind("<Key>", key_pressed) # Checks if a keyboard key is pressed

    top_pipe.mainloop() # Starts the event loop for the top pipe
    bottom_pipe.mainloop()  # Starts the event loop for the bottom pipe
    bird.mainloop() # Starts the event loop for the bird

# Makes the window for the bird
bird = tk.Tk()
bird.configure(background='yellow') # Sets the background colour of the window to be yellow, to display that it is the bird like in the original
bird_screen_width = bird.winfo_screenwidth()
bird_screen_height = bird.winfo_screenheight()
bird_window_width = 150
bird_window_height = 150
bird_x = 100
bird_y = 400
bird.geometry(f"{bird_window_width}x{bird_window_height}+{bird_x}+{bird_y}")


# Makes the window for the score
score_win = tk.Tk()
score_win_screen_width = score_win.winfo_screenwidth()
score_win_screen_height = score_win.winfo_screenheight()
score_win_width = 150
score_win_height = 150
score_win_x = (score_win_screen_width // 2) - (score_win_height // 2) # Centers the window at the top of the screen
score_win_y = 0
score_win.geometry(f"{score_win_width}x{score_win_height}+{score_win_x}+{score_win_y}")
score_label = tk.Label(score_win, text=f"Score: {score}", font=("Helvetica", 16)) # Allows the score to be changed when the score increases
score_label.pack()


bird_logic()    # Calls the bird_logic function
main()  # Calls the main function
