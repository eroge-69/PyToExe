import pgzrun 

#PLAYER-1 FRAMES:#
idle_frame_right = "idle1" 
walk_frames_right = ["walk1", "walk2", "walk3", "walk4","walk5","walk6","walk7","walk8"] 
jump_frames_right = ["jump1", "jump2", "jump3", "jump4","jump5","jump6"]  
duck_frame_right = "dead2"  
run_frames_right = ["run1", "run2", "run3", "run4","run5","run6","run7"] 
idle_frame_left = "idle1_left" 
walk_frames_left = ["walk1_left", "walk2_left", "walk3_left", "walk4_left","walk5_left","walk6_left","walk7_left","walk8_left"]
jump_frames_left = ["jump1_left", "jump2_left", "jump3_left", "jump4_left","jump5_left","jump6_left"]  
duck_frame_left = "dead2_left"  
run_frames_left = ["run1_left", "run2_left", "run3_left", "run4_left","run5_left","run6_left","run7_left"] 
attack_frames_right = ["attack2-1","attack2-2","attack2-3","attack2-4"] 
attack_frames_left = ["attack2-1_left","attack2-2_left","attack2-3_left","attack2-4_left"] 
player_1 = Actor("idle1", (400, 300)) 
player_1.x = 200 
player_1.y = 390 
players = [] 

#PLAYER-2 FRAMES:#
p2_idle_frame_right = "idle1" 
p2_walk_frames_right = ["walk1", "walk2", "walk3", "walk4","walk5","walk6","walk7","walk8"] 
p2_jump_frames_right = ["jump1", "jump2", "jump3", "jump4","jump5","jump6"]  
p2_duck_frame_right = "dead2"  
p2_run_frames_right = ["run1", "run2", "run3", "run4","run5","run6","run7"] 
p2_idle_frame_left = "idle1_left" 
p2_walk_frames_left = ["walk1_left", "walk2_left", "walk3_left", "walk4_left","walk5_left","walk6_left","walk7_left","walk8_left"] 
p2_jump_frames_left = ["jump1_left", "jump2_left", "jump3_left", "jump4_left","jump5_left","jump6_left"] 
p2_duck_frame_left = "dead2_left"  
p2_run_frames_left = ["run1_left", "run2_left", "run3_left", "run4_left","run5_left","run6_left","run7_left"]
p2_attack_frames_right = ["attack2-1","attack2-2","attack2-3","attack2-4"] 
p2_attack_frames_left= ["attack2-1_left","attack2-2_left","attack2-3_left","attack2-4_left"]
player_2 = Actor("idle1", (400, 300)) 
player_2.x = 1600 
player_2.y = 390 
players = [] 

#ANIMATION Einstellungen:#
frame_index = 0 
frame_delay = 10 
frame_timer = 0

#WELT Einstellungen:#
HEIGHT = 1000 
WIDTH = 1800 

#Allgemeine Physic:#
speed_x = [] 
speed_y = [] 
gravity = 0.5 
ground_level =  HEIGHT - 800 #

#PLAYER-1 PHYSIC:#
y_velocity = 0 
jump_strength = -10 
walk_speed = 2 
run_speed = 6  
player_1_attack_timer = 0
player_1_attack_cooldown = 20 
player_1_is_jumping = False 
player_1_is_ducking = False 
player_1_is_running = False 
player_1_facing_right = True 
player_1_is_attacking = False 
p1_health = 100 
p1_max_health = 100
p1_dead = False 

#PLAYER-2 PHYSIC:#
p2_y_velocity = 0 
p2_jump_strength = -10 
p2_walk_speed = 2 
p2_run_speed = 6  
player_2_attack_timer = 0
player_2_attack_cooldown = 20 
player_2_is_jumping = False 
player_2_is_ducking = False 
player_2_is_running = False 
player_2_facing_right = True 
player_2_is_attacking = False 
p2_health = 100 
p2_max_health = 100 
p2_dead = False 

def update():
    #Allgemein GLOBAL:#
    global frame_index, frame_delay, frame_timer
    
    #PLAYER-1 GLOBAL:#
    global y_velocity
    global player_1_is_jumping, player_1_is_ducking, player_1_is_running, p1_moving
    global player_1_facing_right, player_1_is_attacking, player_1_attack_timer, player_1_attack_cooldown
    global p1_dead, p1_health, p1_max_health, p1_got_hit
    
    #PLAYER-1 GLOBAL:#
    global p2_y_velocity
    global player_2_is_jumping, player_2_is_ducking, player_2_is_running, p2_moving
    global player_2_facing_right, player_2_is_attacking, player_2_attack_timer, player_2_attack_cooldown
    global p2_dead, p2_health, p2_max_health, p2_got_hit
    
    #PLAYER-1 HP und Tot#
    if p1_health <= 0 and not p1_dead: 
        p1_dead = True 
        player_1.image = "death_right" if player_1_facing_right else "death_left" 
    
    #PLAYER-2 HP und tot#
    if p2_health <= 0 and not p2_dead: 
        p2_dead = True 
        player_2.image = "death_right" if player_2_facing_right else "death_left" 
    
    
    
    if not p1_dead: 
        if not p2_dead:
    
            #PLAYER-1 GRAVITATION:#
            y_velocity += gravity
            player_1.y += y_velocity
            
            #PLAYER-2 GRAVITATION:#
            p2_y_velocity += gravity
            player_2.y += p2_y_velocity
            
            #PLAYER-1 SPRUNG PHYSICS:#
            if player_1.y > ground_level:
                player_1.y = ground_level
                y_velocity = 0
                if player_1_is_jumping:
                    player_1_is_jumping = False
                
            #PLAYER-2 SPRUNG PHYSICS:#
            if player_2.y > ground_level:
                player_2.y = ground_level
                p2_y_velocity = 0
                if player_2_is_jumping:
                    player_2_is_jumping = False
            
            #PLAYER-1 SPRINGEN:#
            if keyboard.W and player_1.y == ground_level:
                y_velocity = jump_strength  
                player_1_is_jumping = True
            
            #PLAYER-2 SPRINGEN:#
            if keyboard.UP and player_2.y == ground_level:
                p2_y_velocity = jump_strength  
                player_2_is_jumping = True
            
            #PLAYER-1 RUNNING:#
            player_1_is_running = keyboard.V  
            move_speed = run_speed if player_1_is_running else walk_speed
            
            #PLAYER-2 RUNNING:#
            player_2_is_running = keyboard.N  
            p2_move_speed = p2_run_speed if player_2_is_running else walk_speed
        
            #PLAYER-1 MOVEMENT:#
            p1_moving = False
            if keyboard.A:
                player_1.x -= move_speed
                player_1_facing_right = False
                p1_moving = True
            elif keyboard.D:
                player_1.x += move_speed
                player_1_facing_right = True
                p1_moving = True
            
            #PLAYER-2 MOVEMENT:#
            p2_moving = False
            if keyboard.LEFT:
                player_2.x -= p2_move_speed
                player_2_facing_right = False
                p2_moving = True
            elif keyboard.RIGHT:
                player_2.x += p2_move_speed
                player_2_facing_right = True
                p2_moving = True
            
            #PLAYER-1 DUCKING:#                  
            if keyboard.S and player_1.y == ground_level:
                player_1_is_ducking = True
            else:
                player_1_is_ducking = False
           
            #PLAYER-2 DUCKING:#                  
            if keyboard.DOWN and player_2.y == ground_level:
                player_2_is_ducking = True
            else:
                player_2_is_ducking = False
        
            #PLAYER-1 ATTACKING:#
            if keyboard.B and not player_1_is_attacking:
                player_1_is_attacking = True
                player_1_attack_timer = player_1_attack_cooldown
        
        
            #PLAYER-2 ATTACKING:#
            if keyboard.M and not player_1_is_attacking:
                player_2_is_attacking = True
                player_2_attack_timer = player_2_attack_cooldown
        
            #PLAYER-1 ATTACKING ANIMATION:#
            if player_1_is_attacking:
                player_1_attack_timer  -=1
                if player_1_is_attacking <= 0:
                    player_1_is_attacking = False
        
            #PLAYER-1 ATTACKING ANIMATION:#
            if player_2_is_attacking:
                player_2_attack_timer  -=1
                if player_2_is_attacking <= 0:
                    player_2_is_attacking = False
        
            
            if player_1_is_attacking and not p1_dead and not p2_dead:
             if player_1.colliderect(player_2):
                 p2_health -= 10
                 p2_got_hit = True
                 player_1_is_attacking = False  
        
            if player_2_is_attacking and not p1_dead and not p2_dead:
                if player_2.colliderect(player_1):
                    p1_health -= 10
                    p1_got_hit = True
                    player_1_is_attacking = False
        
            p1_got_hit = False
            p2_got_hit = False
        
            #ANIMATION SETTINGS/UPDATES:# 
            frame_timer += 1
            if frame_timer >= frame_delay:
                frame_timer = 0 
                frame_index = (frame_index + 1) % len(idle_frame_right) 
        
            #PLAYER-1 MIRROR:#
            if player_1_facing_right:
                idle_frame = idle_frame_right
                walk_frames = walk_frames_right
                jump_frames = jump_frames_right
                duck_frame = duck_frame_right
                run_frames = run_frames_right
                attack_frames = attack_frames_right
            else:
                idle_frame = idle_frame_left
                walk_frames = walk_frames_left
                jump_frames = jump_frames_left
                duck_frame = duck_frame_left
                run_frames = run_frames_left
                attack_frames = attack_frames_left
                
        
            #PLAYER-2 MIRROR:#
            if player_2_facing_right:
                p2_idle_frame = p2_idle_frame_right
                p2_walk_frames = p2_walk_frames_right
                p2_jump_frames = p2_jump_frames_right
                p2_duck_frame = p2_duck_frame_right
                p2_run_frames = p2_run_frames_right
                p2_attack_frames = p2_attack_frames_right
            else:
                p2_idle_frame = p2_idle_frame_left
                p2_walk_frames = p2_walk_frames_left
                p2_jump_frames = p2_jump_frames_left
                p2_duck_frame = p2_duck_frame_left
                p2_run_frames = p2_run_frames_left
                p2_attack_frames = p2_attack_frames_left
                
        
            #PLAYER-1 PLAY ANIMATIONS:#
            if player_1_is_jumping:
                player_1.image = jump_frames[frame_index % len(jump_frames)] 
            elif player_1_is_ducking:
                player_1.image = duck_frame 
            elif player_1_is_running:
                player_1.image = run_frames[frame_index % len(run_frames)]  
            elif p1_moving:
                player_1.image = walk_frames[frame_index % len(walk_frames)] 
            elif player_1_is_attacking:
                player_1_attack_timer -= 1
                player_1.image = attack_frames[frame_index % len(attack_frames)]
                if player_1_attack_timer <= 0:
                  player_1_is_attacking = False
            else:
                player_1.image = idle_frame  
        
            #PLAYER-2 PLAY ANIMATIONS:#
            if player_2_is_jumping:
                player_2.image = p2_jump_frames[frame_index % len(p2_jump_frames)]  
            elif player_2_is_ducking:
                player_2.image = p2_duck_frame 
            elif player_2_is_running:
                player_2.image = p2_run_frames[frame_index % len(p2_run_frames)] 
            elif p2_moving:
                player_2.image = p2_walk_frames[frame_index % len(p2_walk_frames)] 
            elif player_2_is_attacking:
                player_2.image = p2_attack_frames[frame_index % len(p2_attack_frames)]
                if player_2_attack_timer <= 0:
                  player_2_is_attacking = False
            else:
                player_2.image = p2_idle_frame  
        
            #PLAYER-1 ATTACK REGISTRATION:#
            if player_1_is_attacking and player_1_attack_timer == player_1_attack_cooldown - 1:
                if abs(player_1.x - player_2.x) < 60 and abs(player_1.y - player_2.y) < 40:
                    print("Player-2 got HIT!")
                    
            #PLAYER-2 ATTACK REGISTRATION:#
            if player_2_is_attacking and player_2_attack_timer == player_2_attack_cooldown - 1:
                if abs(player_2.x - player_1.x) < 60 and abs(player_2.y - player_1.y) < 40:
                    print("Player-1 got HIT!")        

#ADD VISUALS:#
def draw():
    screen.clear() 
    screen.blit('bg2',(0,0)) 
    player_1.draw() 
    player_2.draw()
    
        # Player 1 healthbar
    screen.draw.filled_rect(Rect((player_1.x - 50, player_1.y - 80), (100, 10)), "red")
    screen.draw.filled_rect(Rect((player_1.x - 50, player_1.y - 80), (p1_health, 10)), "green")
    
    # Player 2 healthbar
    screen.draw.filled_rect(Rect((player_2.x - 50, player_2.y - 80), (100, 10)), "turquoise")
    screen.draw.filled_rect(Rect((player_2.x - 50, player_2.y - 80), (p2_health, 10)), "purple")
        
    if p1_dead:
     screen.draw.text("Player 2 Wins!", center=(WIDTH // 2, 50), fontsize=60, color="white")
    elif p2_dead:
     screen.draw.text("Player 1 Wins!", center=(WIDTH // 2, 50), fontsize=60, color="white")

pgzrun.go() #PGZ GO#