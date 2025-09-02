import pygame,sys,random

def init_game(screen_width, screen_height):
    ball = pygame.Rect(screen_width/2-15,screen_height/2-15,30,30)
    player = pygame.Rect(screen_width-20,screen_height/2-70,10,140)
    cpu = pygame.Rect(10,screen_height/2-70,10,140)
    
    ball_speed_x = 6 * random.choice((1,-1))
    ball_speed_y = 6 * random.choice((1,-1))
    player_speed = 0
    cpu_speed = 10
    
    player_score = 0
    cpu_score = 0
    score_time = True
    game_paused = False
    game_over = False
    winner = None
    
    # Add game timer variables
    start_time = None  # Will be set after countdown
    game_time = 0
    timer_started = False  # Flag to track if timer has started
    
    # Use normal font weight for game text
    game_font = pygame.font.Font("freesansbold.ttf", 32)
    
    pong_sound = pygame.mixer.Sound("pong.ogg")
    score_sound = pygame.mixer.Sound("score.ogg")
    
    # Create pause and play buttons
    pause_button = pygame.Rect(50, screen_height - 60, 140, 40)
    play_button = pygame.Rect(50, screen_height - 60, 140, 40)
    
    return {
        'ball': ball,
        'player': player,
        'cpu': cpu,
        'ball_speed_x': ball_speed_x,
        'ball_speed_y': ball_speed_y,
        'player_speed': player_speed,
        'cpu_speed': cpu_speed,
        'player_score': player_score,
        'cpu_score': cpu_score,
        'score_time': score_time,
        'game_font': game_font,
        'pong_sound': pong_sound,
        'score_sound': score_sound,
        'game_paused': game_paused,
        'pause_button': pause_button,
        'play_button': play_button,
        'game_over': game_over,
        'winner': winner,
        'start_time': start_time,
        'game_time': game_time,
        'timer_started': timer_started
    }

def ball_movement(game_vars):
    ball = game_vars['ball']
    ball_speed_x = game_vars['ball_speed_x']
    ball_speed_y = game_vars['ball_speed_y']
    player_score = game_vars['player_score']
    cpu_score = game_vars['cpu_score']
    score_time = game_vars['score_time']
    pong_sound = game_vars['pong_sound']
    score_sound = game_vars['score_sound']
    
    if not game_vars['game_over']:  # Only move ball if game is not over
        ball.x += ball_speed_x
        ball.y += ball_speed_y
        
        if ball.top <= 0 or ball.bottom >= screen_height:
            pygame.mixer.Sound.play(pong_sound)
            ball_speed_y *= -1
            
        if ball.left <= 0:
            pygame.mixer.Sound.play(score_sound)
            player_score += 1
            score_time = pygame.time.get_ticks()
            if player_score >= 5:
                game_vars['game_over'] = True
                game_vars['winner'] = "Player"
                ball_speed_x = 0
                ball_speed_y = 0
            else:
                ball.center = (screen_width/2, screen_height/2)
                ball_speed_x = 7 * random.choice((1,-1))
                ball_speed_y = 7 * random.choice((1,-1))
            
        if ball.right >= screen_width:
            pygame.mixer.Sound.play(score_sound)
            cpu_score += 1
            score_time = pygame.time.get_ticks()
            if cpu_score >= 5:
                game_vars['game_over'] = True
                game_vars['winner'] = "CPU"
                ball_speed_x = 0
                ball_speed_y = 0
            else:
                ball.center = (screen_width/2, screen_height/2)
                ball_speed_x = 7 * random.choice((1,-1))
                ball_speed_y = 7 * random.choice((1,-1))
            
        if ball.colliderect(game_vars['player']) and ball_speed_x > 0:
            pygame.mixer.Sound.play(pong_sound)
            ball_speed_x *= -1
            
        if ball.colliderect(game_vars['cpu']) and ball_speed_x < 0:
            pygame.mixer.Sound.play(pong_sound)
            ball_speed_x *= -1
    
    game_vars['ball'] = ball
    game_vars['ball_speed_x'] = ball_speed_x
    game_vars['ball_speed_y'] = ball_speed_y
    game_vars['player_score'] = player_score
    game_vars['cpu_score'] = cpu_score
    game_vars['score_time'] = score_time

def player_movement(game_vars):
    player = game_vars['player']
    player_speed = game_vars['player_speed']
    
    player.y += player_speed
    if player.top <= 0:
        player.top = 0
    if player.bottom >= screen_height:
        player.bottom = screen_height
    
    game_vars['player'] = player

def second_player_movement(game_vars):
    cpu = game_vars['cpu']
    cpu_speed = game_vars['cpu_speed']
    
    cpu.y += cpu_speed
    if cpu.top <= 0:
        cpu.top = 0
    if cpu.bottom >= screen_height:
        cpu.bottom = screen_height
    
    game_vars['cpu'] = cpu

def cpu_movement(game_vars):
    cpu = game_vars['cpu']
    cpu_speed = game_vars['cpu_speed']
    ball = game_vars['ball']
    
    if cpu.top + 10 < ball.y:
        cpu.top += cpu_speed
    if cpu.bottom - 10 > ball.y:
        cpu.bottom -= cpu_speed
    if cpu.top <= 0:
        cpu.top = 0
    if cpu.bottom >= screen_height:
        cpu.bottom = screen_height
    
    game_vars['cpu'] = cpu

def ball_restart(game_vars, screen, screen_width, screen_height, border):
    ball = game_vars['ball']
    ball_speed_x = game_vars['ball_speed_x']
    ball_speed_y = game_vars['ball_speed_y']
    score_time = game_vars['score_time']
    game_font = game_vars['game_font']
    
    current_time = pygame.time.get_ticks()
    ball.center = (screen_width/2, screen_height/2)
    
    # Position for timer (slightly left of center-top)
    timer_y = 50
    offset_from_center = 150  # pixels to move left from center
    
    if current_time - score_time < 700:
        three = game_font.render("3", True, border)
        timer_x = (screen_width/2 - three.get_width()/2) - offset_from_center
        screen.blit(three, (timer_x, timer_y))
        
    if 700 < current_time - score_time < 1400:
        two = game_font.render("2", True, border)
        timer_x = (screen_width/2 - two.get_width()/2) - offset_from_center
        screen.blit(two, (timer_x, timer_y))
        
    if 1400 < current_time - score_time < 2100:
        one = game_font.render("1", True, border)
        timer_x = (screen_width/2 - one.get_width()/2) - offset_from_center
        screen.blit(one, (timer_x, timer_y))
        
    if current_time - score_time < 2100:
        ball_speed_x, ball_speed_y = 0, 0
    else:
        if not game_vars['timer_started']:
            game_vars['start_time'] = pygame.time.get_ticks()
            game_vars['timer_started'] = True
        ball_speed_y = 7 * random.choice((1,-1))
        ball_speed_x = 7 * random.choice((1,-1))
        score_time = None
    
    game_vars['ball'] = ball
    game_vars['ball_speed_x'] = ball_speed_x
    game_vars['ball_speed_y'] = ball_speed_y
    game_vars['score_time'] = score_time

def run_game(game_mode, game_vars, player1_color, player2_color):
    global screen_width, screen_height, screen, green, border, white
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if game_vars['game_paused']:
                    if game_vars['play_button'].collidepoint(mouse_pos):
                        game_vars['game_paused'] = False
                else:
                    if game_vars['pause_button'].collidepoint(mouse_pos):
                        game_vars['game_paused'] = True
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Add pause/play toggle with P key
                    game_vars['game_paused'] = not game_vars['game_paused']
                
                if not game_vars['game_paused'] and not game_vars['game_over']:  # Only process game controls if not paused and not game over
                    if event.key == pygame.K_UP:
                        game_vars['player_speed'] -= 6
                    if event.key == pygame.K_DOWN:
                        game_vars['player_speed'] += 6
                    if game_mode == "two_player":
                        if event.key == pygame.K_w:
                            game_vars['cpu_speed'] = -6
                        if event.key == pygame.K_s:
                            game_vars['cpu_speed'] = 6
                if event.key == pygame.K_r and game_vars['game_over']:  # Restart game with R key
                    return "restart"
            
            if event.type == pygame.KEYUP:
                if not game_vars['game_paused'] and not game_vars['game_over']:  # Only process game controls if not paused and not game over
                    if event.key == pygame.K_UP:
                        game_vars['player_speed'] += 6
                    if event.key == pygame.K_DOWN:
                        game_vars['player_speed'] -= 6
                    if game_mode == "two_player":
                        if event.key == pygame.K_w:
                            game_vars['cpu_speed'] = 0
                        if event.key == pygame.K_s:
                            game_vars['cpu_speed'] = 0
        
        if not game_vars['game_paused']:  # Only update game if not paused
            ball_movement(game_vars)
            if not game_vars['game_over']:  # Only move paddles if game is not over
                player_movement(game_vars)
                if game_mode == "two_player":
                    second_player_movement(game_vars)
                else:
                    cpu_movement(game_vars)
        
        if not game_vars['game_paused'] and not game_vars['game_over'] and game_vars['start_time'] is not None:
            # Update game timer only if it has started
            current_time = pygame.time.get_ticks()
            game_vars['game_time'] = (current_time - game_vars['start_time']) // 1000  # Convert to seconds
        
        screen.fill(green)
        
        pygame.draw.rect(screen, player2_color, game_vars['cpu'])  # Left paddle (Player 2 or CPU)
        pygame.draw.rect(screen, player1_color, game_vars['player'])  # Right paddle (Player 1)
        pygame.draw.ellipse(screen, white, game_vars['ball'])
        
        # Draw center line with reduced thickness (2 pixels)
        pygame.draw.line(screen, white, (screen_width/2, 0), (screen_width/2, screen_height), 2)
        
        # Display game timer - adjusted position more to the left
        minutes = game_vars['game_time'] // 60
        seconds = game_vars['game_time'] % 60
        timer_text = game_vars['game_font'].render(f"{minutes:02d}:{seconds:02d}", True, white)
        screen.blit(timer_text, (screen_width - 300, 50))  # New position: 300px from right, 50px from top
        
        if game_vars['score_time'] and not game_vars['game_over']:
            ball_restart(game_vars, screen, screen_width, screen_height, border)
        
        # Update all text rendering to use anti-aliasing
        player_text = game_vars['game_font'].render(f"{game_vars['player_score']}", True, white)
        cpu_text = game_vars['game_font'].render(f"{game_vars['cpu_score']}", True, white)
        
        # Calculate positions for centered score display
        score_spacing = 50  # Space between scores
        total_width = player_text.get_width() + score_spacing + cpu_text.get_width()
        start_x = (screen_width - total_width) / 2
        
        screen.blit(player_text, (start_x, 50))
        screen.blit(cpu_text, (start_x + player_text.get_width() + score_spacing, 50))
        
        # Draw pause/play button with bold text
        if game_vars['game_paused']:
            pygame.draw.rect(screen, white, game_vars['play_button'])
            play_text = game_vars['game_font'].render("PLAY", True, green)
            text_x = game_vars['play_button'].x + (game_vars['play_button'].width - play_text.get_width()) // 2
            text_y = game_vars['play_button'].y + (game_vars['play_button'].height - play_text.get_height()) // 2
            screen.blit(play_text, (text_x, text_y))
        else:
            pygame.draw.rect(screen, white, game_vars['pause_button'])
            pause_text = game_vars['game_font'].render("PAUSE", True, green)
            text_x = game_vars['pause_button'].x + (game_vars['pause_button'].width - pause_text.get_width()) // 2
            text_y = game_vars['pause_button'].y + (game_vars['pause_button'].height - pause_text.get_height()) // 2
            screen.blit(pause_text, (text_x, text_y))
        
        if game_mode == "two_player":
            player1_text = game_vars['game_font'].render("Player 1", True, border)
            player2_text = game_vars['game_font'].render("Player 2", True, border)
            screen.blit(player1_text, (10, 10))
            screen.blit(player2_text, (screen_width-130, 10))
        else:
            CPU = game_vars['game_font'].render("PC", True, border)
            USER = game_vars['game_font'].render("USER", True, border)
            screen.blit(CPU, (10, 10))
            screen.blit(USER, (screen_width-130, 10))
        
        # Show game over message with bold text
        if game_vars['game_over']:
            win_text = game_vars['game_font'].render(f"{game_vars['winner']} WINS!", True, white)
            restart_text = game_vars['game_font'].render("Press R to Restart", True, white)
            screen.blit(win_text, (screen_width/2 - win_text.get_width()/2, screen_height/2 - 50))
            screen.blit(restart_text, (screen_width/2 - restart_text.get_width()/2, screen_height/2 + 50))
        
        pygame.display.flip()
        clock.tick(60)

def show_menu(screen, screen_width, screen_height, border):
    # Main title will be bold, other text normal
    menu_font = pygame.font.Font("freesansbold.ttf", 48)
    menu_font.set_bold(True)  # Only title remains bold
    small_font = pygame.font.Font("freesansbold.ttf", 32)
    
    # Load and scale background image
    background_image = pygame.image.load("pngtree-padel-tennis-racket-sport-court-and-balls-paddle-tennis-hobby-racket-and-balls-photo-image_48622122.jpg")
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
    
    # Add a semi-transparent overlay to make text more readable
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((50, 50, 50))  # Dark gray overlay instead of green
    overlay.set_alpha(180)  # Adjust transparency (0-255)
    
    # Colors for circles
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)
    gray = (128, 128, 128)  # Color for background rectangle
    colors = [black, red, blue, white]
    
    # Circle settings
    circle_radius = 15
    circles = [
        {'color': black, 'pos': (30, screen_height - 30)},
        {'color': red, 'pos': (70, screen_height - 30)},
        {'color': blue, 'pos': (110, screen_height - 30)},
        {'color': white, 'pos': (150, screen_height - 30)}
    ]
    
    # Background rectangle for circles
    circle_area_padding = 20  # Padding around circles
    rect_width = 160  # Width to cover all circles plus padding
    rect_height = 40  # Standard height for the rectangle
    rect_x = 10  # Position slightly left of first circle
    rect_y = screen_height - 50  # Position slightly above circles
    circle_background_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
    
    # Keep anti-aliasing but remove bold from most text
    title = menu_font.render("PONG GAME", True, border)  # Title stays bold
    single_player = small_font.render("1. Single Player", True, border)
    two_player = small_font.render("2. Two Players", True, border)
    instruction = small_font.render("Press 1 or 2 to select", True, border)
    color_instruction = small_font.render("Click circles to choose paddle colors", True, border)
    
    # Initialize selected colors
    player1_color = white
    player2_color = white
    current_player = 1  # Track which player is selecting color
    
    game_mode = None
    
    while True:
        # Draw background image first
        screen.blit(background_image, (0, 0))
        # Add semi-transparent overlay
        screen.blit(overlay, (0, 0))
        
        screen.blit(title, (screen_width/2 - title.get_width()/2, 150))
        screen.blit(single_player, (screen_width/2 - single_player.get_width()/2, 300))
        screen.blit(two_player, (screen_width/2 - two_player.get_width()/2, 350))
        screen.blit(instruction, (screen_width/2 - instruction.get_width()/2, 450))
        screen.blit(color_instruction, (screen_width/2 - color_instruction.get_width()/2, 500))
        
        # Draw the background rectangle with rounded corners
        pygame.draw.rect(screen, gray, circle_background_rect, border_radius=15)
        
        # Draw the colored circles
        for circle in circles:
            pygame.draw.circle(screen, circle['color'], circle['pos'], circle_radius)
            
        # Show current selection status
        if game_mode:
            if current_player == 1:
                status = small_font.render("Select Player 1 Color", True, border)
            else:
                status = small_font.render("Select Player 2 Color", True, border)
            screen.blit(status, (screen_width/2 - status.get_width()/2, screen_height - 50))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if not game_mode:
                    if event.key == pygame.K_1:
                        game_mode = "single_player"
                    if event.key == pygame.K_2:
                        game_mode = "two_player"
            if event.type == pygame.MOUSEBUTTONDOWN and game_mode:
                mouse_pos = pygame.mouse.get_pos()
                for circle in circles:
                    circle_x, circle_y = circle['pos']
                    # Check if click is within circle
                    if ((mouse_pos[0] - circle_x) ** 2 + (mouse_pos[1] - circle_y) ** 2) <= circle_radius ** 2:
                        if current_player == 1:
                            player1_color = circle['color']
                            current_player = 2
                            screen.fill(green)
                            screen.blit(title, (screen_width/2 - title.get_width()/2, 150))
                            screen.blit(single_player, (screen_width/2 - single_player.get_width()/2, 300))
                            screen.blit(two_player, (screen_width/2 - two_player.get_width()/2, 350))
                            screen.blit(color_instruction, (screen_width/2 - color_instruction.get_width()/2, 500))
                        else:
                            player2_color = circle['color']
                            return game_mode, player1_color, player2_color
                        break

if __name__ == "__main__":
    pygame.init()
    clock = pygame.time.Clock()
    
    screen_width = 1000
    screen_height = 600
    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption('Pong Game')
    
    # Change green to dark gray
    green = (50, 50, 50)  # Dark gray instead of green
    border = (200,200,200)
    white = (255,255,255)
    
    while True:
        game_vars = init_game(screen_width, screen_height)
        game_mode, player1_color, player2_color = show_menu(screen, screen_width, screen_height, border)
        result = run_game(game_mode, game_vars, player1_color, player2_color)
        if result != "restart":
            break
