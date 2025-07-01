import pygame as pg
import sys
from time import sleep
import random  # Import random for generating random positions

pg.init()

# Initialize screen
screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)  # Set fullscreen mode
screen_width, screen_height = screen.get_size()  # Get screen dimensions
pg.display.set_caption("a simple game")  # Set window title

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (100, 100, 100)

# Clock for controlling frame rate
clock = pg.time.Clock()

# Rectangle position
rect_x = 100
rect_y = 100
rect_width = 50
rect_height = 50
rect_color = BLUE

# Square position
square_x = 400
square_y = 300
square_width = 50
square_height = 50
square_speed = 2  # Speed of the square

# Function to randomize trail color
def randomize_trail_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Timer and speed increment setup
max_speed = 10  # Maximum speed of the square
start_time = pg.time.get_ticks()  # Record the start time

# FPS setting
fps = 69  # Default FPS

# Hide the mouse cursor
pg.mouse.set_visible(False)

# Circle trail setup
trail = []  # List to store trail positions
trail_length = 8  # Maximum number of trail points
circle_radius = 6  # Radius of the circle
circle_color = randomize_trail_color()  # Initialize trail color

# Settings menu
def settings_menu():
    global trail_length, circle_radius
    pg.mouse.set_visible(True)  # Make the mouse visible in settings
    in_settings = True

    while in_settings:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:  # Exit settings
                    in_settings = False
                elif event.key == pg.K_q:  # Quit game
                    pg.quit()
                    sys.exit()
                elif event.key == pg.K_1:  # Increase trail length
                    trail_length = min(20, trail_length + 1)  # Limit maximum trail length
                elif event.key == pg.K_2:  # Decrease trail length
                    trail_length = max(1, trail_length - 1)  # Ensure trail length doesn't go below 1
                elif event.key == pg.K_3:  # Increase circle radius
                    circle_radius = min(20, circle_radius + 1)  # Limit maximum circle radius
                elif event.key == pg.K_4:  # Decrease circle radius
                    circle_radius = max(1, circle_radius - 1)  # Ensure circle radius doesn't go below 1
                elif event.key == pg.K_UP:  # Increase FPS
                    fps = min(1000, fps + 0.2)  # Limit maximum FPS
                elif event.key == pg.K_DOWN:  # Decrease FPS
                    fps = max(1, fps - 0.2)  # Ensure FPS doesn't go below 1
                elif event.key == pg.K_5:  # Reset settings
                    trail_length = 8  # Reset trail length
                    circle_radius = 6  # Reset circle radius
                    fps = 69  # Reset FPS
                

        # Render settings menu
        screen.fill(GRAY)
        font = pg.font.Font(None, 74)
        settings_text = font.render("Settings", True, WHITE)
        trail_length_text = font.render(f"Trail Length: {trail_length}", True, WHITE)
        circle_radius_text = font.render(f"Circle Radius: {circle_radius}", True, WHITE)
        fps_text = font.render(f"FPS: {round(fps)}", True, WHITE)
        adjust_fps_text = font.render("Hold UP/DOWN to Adjust FPS", True, WHITE)
        cicle_text = font.render("Press 1 to Increase Trail Length, Press 2 to Decrease Trail Length", True, WHITE)
        square_text = font.render("Press 3 to Increase Circle Radius, Press 4 to Decrease Circle Radius", True, WHITE)
        exit_text = font.render("Press ESC to Exit", True, WHITE)

        screen.blit(settings_text, (screen_width // 2 - settings_text.get_width() // 2, 100))
        screen.blit(trail_length_text, (screen_width // 2 - trail_length_text.get_width() // 2, 200))
        screen.blit(fps_text, (screen_width // 2 - fps_text.get_width() // 2, 400))
        screen.blit(circle_radius_text, (screen_width // 2 - circle_radius_text.get_width() // 2, 300))
        screen.blit(adjust_fps_text, (screen_width // 2 - adjust_fps_text.get_width() // 2, 500))
        screen.blit(cicle_text, (screen_width // 2 - cicle_text.get_width() // 2, 600))
        screen.blit(square_text, (screen_width // 2 - square_text.get_width() // 2, 700))
        screen.blit("Press 5 to Reset Settings", (screen_width // 2 - square_text.get_width() // 2, 800))
        screen.blit(exit_text, (screen_width // 2 - exit_text.get_width() // 2, 900))

        pg.display.flip()
        clock.tick(30)  # Limit settings menu to 30 FPS

    pg.mouse.set_visible(False)  # Hide the mouse after exiting settings

# Pause menu
def pause_menu():
    global fps
    paused = True

    while paused:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:  # Resume game
                    paused = False
                elif event.key == pg.K_q:  # Quit game
                    pg.quit()
                    sys.exit()
                elif event.key == pg.K_s:  # Open settings menu
                    settings_menu()

        # Render pause menu
        screen.fill(GRAY)
        font = pg.font.Font(None, 74)
        pause_text = font.render("Paused", True, WHITE)
        resume_text = font.render("Press ESC to Resume", True, WHITE)
        quit_text = font.render("Press Q to Quit", True, WHITE)
        settings_text = font.render("Press S for Settings", True, WHITE)

        screen.blit(pause_text, (screen_width // 2 - pause_text.get_width() // 2, 100))
        screen.blit(resume_text, (screen_width // 2 - resume_text.get_width() // 2, 300))
        screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, 400))
        screen.blit(settings_text, (screen_width // 2 - settings_text.get_width() // 2, 600))

        pg.display.flip()
        clock.tick(30)  # Limit pause menu to 30 FPS

# Function to display a message on the screen
def display_message(message, color):
    font = pg.font.Font(None, 74)  # Create a font object
    text = font.render(message, True, color)  # Render the text
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))  # Center the text
    screen.fill(BLACK)  # Clear the screen with black
    screen.blit(text, text_rect)  # Draw the text on the screen
    pg.display.flip()  # Update the display

    # Wait for 3 seconds without blocking the event loop
    start_time = pg.time.get_ticks()
    while pg.time.get_ticks() - start_time < 3000:  # Wait for 3000 ms (3 seconds)
        for event in pg.event.get():
            if event.type == pg.QUIT:  # Allow quitting during the message display
                pg.quit()
                sys.exit()

# Function to get the duration of the game from the player
def get_duration():
    input_text = ""  # Store the player's input
    font = pg.font.Font(None, 74)  # Font for rendering text
    prompt_text = "How many seconds do you want to play? (Enter a number)"
    error_message = ""  # To display an error if the input is invalid

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:  # Enter key
                    if input_text.isdigit():  # Check if the input is a valid number
                        return int(input_text)  # Return the duration in seconds
                    else:
                        error_message = "Please enter a valid number!"
                elif event.key == pg.K_BACKSPACE:  # Backspace key
                    input_text = input_text[:-1]  # Remove the last character
                elif event.unicode.isdigit():  # Only allow numeric input
                    input_text += event.unicode

        # Render the input screen
        screen.fill(GRAY)
        prompt_surface = font.render(prompt_text, True, WHITE)
        input_surface = font.render(input_text, True, WHITE)
        error_surface = font.render(error_message, True, RED)

        # Display the prompt, input, and error message
        screen.blit(prompt_surface, (screen_width // 2 - prompt_surface.get_width() // 2, screen_height // 2 - 100))
        screen.blit(input_surface, (screen_width // 2 - input_surface.get_width() // 2, screen_height // 2))
        if error_message:
            screen.blit(error_surface, (screen_width // 2 - error_surface.get_width() // 2, screen_height // 2 + 100))

        pg.display.flip()
        clock.tick(60)  # Limit frame rate

# Main game loop
def main_game_loop():
    global rect_x, rect_y, square_x, square_y, square_speed, fps, circle_color
    duration = get_duration()  # Get the duration of the game in seconds
    print(f"Player wants to play for {duration} seconds.")  # Debugging output

    start_time = pg.time.get_ticks()  # Reset start time
    clone_timer = pg.time.get_ticks()  # Timer for spawning clones
    clones = []  # List to store clone positions and speeds
    max_clones = duration // 5  # Maximum number of clones
    clone_interval = 5000  # Spawn a clone every 5 seconds (5000 ms)
    running = True

    while running:
        # Event handling
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:  # Open pause menu
                    pause_menu()

        # Game logic update
        mouse_x, mouse_y = pg.mouse.get_pos()  # Get mouse position
        rect_x, rect_y = mouse_x - rect_width // 2, mouse_y - rect_height // 2  # Center rectangle on mouse

        # Update trail
        trail.append((mouse_x, mouse_y))  # Add current mouse position to the trail
        if len(trail) > trail_length:  # Limit the trail length
            trail.pop(0)

        # Change trail color periodically
        if len(trail) == trail_length:  # Sync color change with trail updates
            circle_color = randomize_trail_color()

        # Gradually increase square speed
        elapsed_time = (pg.time.get_ticks() - start_time) / 1000  # Time in seconds
        square_speed = min(max_speed, 2 + (elapsed_time / 60) * (max_speed - 2))  # Increase speed over 60 seconds

        # Check if the player survives for the specified duration
        if elapsed_time >= duration:
            display_message("You Win!", BLUE)  # Display win message on screen
            running = False

        # Spawn clones every 5 seconds
        if len(clones) < max_clones and pg.time.get_ticks() - clone_timer >= clone_interval:
            # Generate random positions for the clone
            while True:
                clone_x = random.randint(0, screen_width - square_width)
                clone_y = random.randint(0, screen_height - square_height)
                # Ensure the clone does not spawn on the main square
                if not (square_x < clone_x + square_width and square_x + square_width > clone_x and
                        square_y < clone_y + square_height and square_y + square_height > clone_y):
                    break
            # Assign a speed to the clone (20% faster than the previous clone)
            clone_speed = square_speed * (1.2 ** len(clones))
            clones.append({"pos": [clone_x, clone_y], "speed": clone_speed})  # Store position and speed
            clone_timer = pg.time.get_ticks()  # Reset the clone timer

        # Move the square
        if square_x < rect_x:
            square_x = min(screen_width - square_width, square_x + square_speed)
        elif square_x > rect_x:
            square_x = max(0, square_x - square_speed)

        if square_y < rect_y:
            square_y = min(screen_height - square_height, square_y + square_speed)
        elif square_y > rect_y:
            square_y = max(0, square_y - square_speed)

        # Move clones
        for clone in clones:
            clone_pos = clone["pos"]
            clone_speed = clone["speed"]
            if clone_pos[0] < rect_x:
                clone_pos[0] = min(screen_width - square_width, clone_pos[0] + clone_speed)
            elif clone_pos[0] > rect_x:
                clone_pos[0] = max(0, clone_pos[0] - clone_speed)

            if clone_pos[1] < rect_y:
                clone_pos[1] = min(screen_height - square_height, clone_pos[1] + clone_speed)
            elif clone_pos[1] > rect_y:
                clone_pos[1] = max(0, clone_pos[1] - clone_speed)

        # Check for collision with the main square
        if (
            square_x < rect_x + rect_width and
            square_x + square_width > rect_x and
            square_y < rect_y + rect_height and
            square_y + square_height > rect_y
        ):
            display_message("You Lose!", RED)  # Display lose message on screen
            running = False

        # Check for collision with clones
        for clone in clones:
            clone_pos = clone["pos"]
            if (
                clone_pos[0] < rect_x + rect_width and
                clone_pos[0] + square_width > rect_x and
                clone_pos[1] < rect_y + rect_height and
                clone_pos[1] + square_height > rect_y
            ):
                display_message("You Lose!", RED)  # Display lose message on screen
                running = False

        # Rendering
        screen.fill(BLACK)  # Clear screen with black

        # Draw the trail with the current color
        for pos in trail:
            pg.draw.circle(screen, circle_color, pos, circle_radius)

        pg.draw.rect(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))  # Draw the rectangle
        pg.draw.rect(screen, WHITE, (square_x, square_y, square_width, square_height))  # Draw the main square

        # Draw clones
        for clone in clones:
            clone_pos = clone["pos"]
            pg.draw.rect(screen, RED, (clone_pos[0], clone_pos[1], square_width, square_height))  # Draw each clone

        pg.display.flip()  # Update the display

        # Control frame rate
        clock.tick(fps)  # Limit to the current FPS

# Start the game
main_game_loop()
pg.quit()