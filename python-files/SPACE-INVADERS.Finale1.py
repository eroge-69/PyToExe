
import pgzrun
from pgzero.builtins import Actor


WIDTH = 1000
HEIGHT = 900
SHIP_SPEED = 5
BULLET_SPEED = 7
ALIEN_SPEED = 2 
alien_direction = 2 

ship = Actor('schiff', (WIDTH / 2, HEIGHT - 50))
bullets = []
aliens = []
score = 0  

def create_aliens():
    global aliens
    aliens = []
    for x in range(5):
        for y in range(3):
            alien = Actor('gegner2', (100 + x * 100, 50 + y * 60))
            aliens.append(alien)

create_aliens()

game_over = False

def update():
    global alien_direction, game_over, score, ALIEN_SPEED
    if game_over:
        return

   
    for bullet in bullets[:]:
        for alien in aliens[:]:
            if bullet.colliderect(alien):
                bullets.remove(bullet)
                aliens.remove(alien)
                score += 100 
                break

    if keyboard.left and ship.left > 0:
        ship.x -= SHIP_SPEED
    if keyboard.right and ship.right < WIDTH:
        ship.x += SHIP_SPEED

    for bullet in bullets[:]:
        bullet.y -= BULLET_SPEED
        if bullet.y < 0:
            bullets.remove(bullet)

    for alien in aliens[:]:
        alien.x += ALIEN_SPEED * alien_direction
        
        if alien.right > WIDTH or alien.left < 0:
            alien_direction *= -1  
            for a in aliens:
                a.y += 100  
            break
        
        if alien.bottom >= HEIGHT:
            game_over = True

    if len(aliens) == 0 and not game_over:
        ALIEN_SPEED += 4 
        restart_game()

def draw_game_over():
    screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2), fontsize=60, color="red")


def on_key_down(key):
    global game_over
    if key == keys.SPACE and not game_over: 
        bullet = Actor('bullet', (ship.x, ship.y - 20))
        bullets.append(bullet)
        
        

def restart_game():
    global game_over, bullets, aliens, alien_direction, ALIEN_SPEED, score
    game_over = False
    bullets = [] 
    create_aliens() 
    
    
    alien_direction = 1

def draw():
    screen.clear()
    screen.blit('background', (0, 0)) 
    if game_over:
        draw_game_over()
    else:
        screen.draw.text(f"Score: {score}", topleft=(820, 10), fontsize=42, color='lightgreen')  # Zeige den Score an
        ship.draw()
        for bullet in bullets:
            bullet.draw()
        for alien in aliens:
            alien.draw()

pgzrun.go()

