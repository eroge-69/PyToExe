import pygame
import random
from pygame.locals import *
from pygame import mixer

pygame.init()
frame_size_x = 1200
frame_size_y = 750
window_screen = pygame.display.set_mode((frame_size_x, 
frame_size_y))
pygame.display.set_caption("Your game name")
clock = pygame.time.Clock()
FPS = 60
frame_width1 = 100
frame_height1 = 100

frame_width2 = 125
frame_height2 = 75
#game status decider
game_status = "menu"
user_status = "idle"
user_health = 100
font = pygame.font.Font('CBgallery/font/Tiny5-Regular.ttf', 32)

#combat variablezz
knight_status = "idle"
knight_health = 3
knight_attack_timer  = 0
next_attacktime = random.randint(60, 120)#random time before the next attack
#windup_clock = 45 #how long the knight winds up before he attacks
#attack_hurtsfor = 6 #how many frames the attacks hurt for
knight_recovery = 70 #how long the knight rests for 
knightblock_duration = 42
knightatk_anim_timer = 0

currentknightatk = 1 #current attack
knightattackdata = {} #stores attacks for later

success_parry = False #for success parry animation & others
sucparry_timer = 0 #starts parry animation
sucparry_duration = 60 # how long before successparry is done

success_strike = False
sucstrike_timer = 0
sucstrike_duration = 60

user_COURAGE = 0 #succesful parries
max_COURAGE = 4 #max success parries before user can attack
cOURAGE_RELEASE = False



#----------------------------------IMAGE LIST-------------------------------------------------#

#BATTLE BACKGROUND IMAGE
battlebackground = pygame.image.load("CBgallery/sprites/background.png").convert()
battlebackground = pygame.transform.scale(battlebackground, (1200,750))
battlebackground_rect = battlebackground.get_rect(midbottom=(0,0))

#STATUS BAR IMAGE
status_bar = pygame.image.load("CBgallery/sprites/CBStatusBar.png").convert_alpha()
status_bar = pygame.transform.scale(status_bar, (840,840))
statusbar_rect = status_bar.get_rect(midbottom=(600,740))

thankyou = pygame.image.load("CBgallery/sprites/thankyou.png").convert()
thankyou = pygame.transform.scale(thankyou, (1200,750))
thankyou_rect = thankyou.get_rect(midbottom=(0,0))

tutor = pygame.image.load("Cbgallery/sprites/tutor.png").convert()
tutor = pygame.transform.scale(tutor, (1200,750))
tutor_rect = tutor.get_rect(midbottom=(0,0))

#---------------------------------AUDIO LIST----------------------------------------------------------------------#
celebrate = pygame.mixer.Sound("CBgallery/sound effects/celebrae.wav")
gameoversound = pygame.mixer.Sound("CBgallery/sound effects/gameover.wav")
slashsound = pygame.mixer.Sound("CBgallery/sound effects/hit.wav")
parrysound = pygame.mixer.Sound("CBgallery/sound effects/parry.wav")
owiesound = pygame.mixer.Sound("CBgallery/sound effects/usergethit.wav")
#---------------------------------------------------MENU FLAG------------------------------------------------------#
menuflag = pygame.image.load("CBgallery/sprites/REALtitleflaguntitled.png").convert_alpha()
menuflag_framecount = 3

menuflag_frames = []
for i in range(menuflag_framecount) :
    menuflag_frame = menuflag.subsurface(pygame.Rect(i * frame_width2, 0, frame_width2, frame_height2))
    menuflag_frame = pygame.transform.scale(menuflag_frame, (frame_width2 * 10, frame_height2 * 10))
    menuflag_frames.append(menuflag_frame)

menuflag_index = 0
menuflag_image = menuflag_frames[menuflag_index]
menuflag_rect = menuflag_image.get_rect(center=(600,365))
menuflag_timer = 0

#----------------------------------------------USER ANIMATION LIST-----------------------------------------------------------#
useridle = pygame.image.load("CBgallery/sprites/userswordidle.png").convert_alpha()
useridle_framecount = 2

useridle_frames = []
for i in range(useridle_framecount) :
    useridle_frame = useridle.subsurface(pygame.Rect(i * frame_width2, 0, frame_width2, frame_height2))
    useridle_frame = pygame.transform.scale(useridle_frame, (frame_width2 * 10, frame_height2 * 10))
    useridle_frames.append(useridle_frame)

useridle_index = 0
useridle_image = useridle_frames[useridle_index]
useridle_rect = useridle.get_rect(midbottom=(100,72))
useridle_timer = 0

userparry = pygame.image.load("CBgallery/sprites/userswordparryuntitled.png").convert_alpha()
userparry_framecount = 7

userparry_frames = []
for i in range(userparry_framecount) :
    userparry_frame = userparry.subsurface(pygame.Rect(i * frame_width2, 0, frame_width2, frame_height2))
    userparry_frame = pygame.transform.scale(userparry_frame, (frame_width2 * 10, frame_height2 * 10))
    userparry_frames.append(userparry_frame)

userparry_index = 0
userparry_image = userparry_frames[userparry_index]
userparry_rect = userparry.get_rect(midbottom=(410,72))
userparry_timer = 0

userslash = pygame.image.load("CBgallery/sprites/userslash.png").convert_alpha()
userslash_framecount = 6

userslash_frames = []
for i in range(userslash_framecount) :
    userslash_frame = userslash.subsurface(pygame.Rect(i * frame_width2, 0, frame_width2, frame_height2))
    userslash_frame = pygame.transform.scale(userslash_frame, (frame_width2 * 10, frame_height2 * 10))
    userslash_frames.append(userslash_frame)

userslash_index = 0
userslash_image = userslash_frames[userslash_index]
userslash_rect = userslash.get_rect(midbottom=(410, 72))
userslash_timer = 0

#------------------------------------------KNIGHT OPPONENT ANIMATION LIST-----------------------------------------------------------#
knightstance = pygame.image.load("CBgallery/sprites/knightstance.png").convert_alpha()
knightwindup = pygame.image.load("CBgallery/sprites/windup1.png").convert_alpha()
knightwindup2 = pygame.image.load("CBgallery/sprites/swordshineuntitled.png").convert_alpha()
knightattack1 = pygame.image.load("CBgallery/sprites/NEWSLASH.png").convert_alpha()
knightattack2 = pygame.image.load("CBgallery/sprites/INSTASLASH.png").convert_alpha()
knightblock = pygame.image.load("CBgallery/sprites/KNIGHTBLOCK.png").convert_alpha()

knightstance_frame_count = 9 
knightwindup_framecount = 8 
knightwindup2_framecount = 4
knightatk1_framecount = 5
knightatk2_framecount = 3
knightblock_framecount = 6

knightstance_frames = []
for i in range(knightstance_frame_count) :
        knightstance_frame = knightstance.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
        knightstance_frame = pygame.transform.scale(knightstance_frame, (frame_width1 * 5, frame_height1 * 5))
        knightstance_frames.append(knightstance_frame)

knightstance_index = 0
knightstance_image = knightstance_frames[knightstance_index]
knightstance_rect = knightstance_image.get_rect(midbottom=(600, 550))
knightstance_timer = 0

knightwindup_frames = []
for i in range(knightwindup_framecount) :
    knightwindup_frame = knightwindup.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
    knightwindup_frame = pygame.transform.scale(knightwindup_frame, (frame_width1 * 5, frame_height1 * 5))
    knightwindup_frames.append(knightwindup_frame)

knightwindup_index = 0
knightwindup_image = knightwindup_frames[knightwindup_index]
knightwindup_rect = knightwindup.get_rect(midbottom=(600, 500))
knightwindup_timer = 0

knightatk1_frames = []
for i in range(knightatk1_framecount) :
    knightatk1_frame = knightattack1.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
    knightatk1_frame = pygame.transform.scale(knightatk1_frame, (frame_width1 * 5, frame_height1 * 5))
    knightatk1_frames.append(knightatk1_frame)

knightatk1_index = 0
knightatk1_image = knightatk1_frames[knightatk1_index]
knightatk1_rect = knightattack1.get_rect(midbottom=(600, 500))
knightatk1_timer = 0

knightatk2_frames = []
for i in range(knightatk2_framecount) :
    knightatk2_frame = knightattack2.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
    knightatk2_frame = pygame.transform.scale(knightatk2_frame, (frame_width1 * 5, frame_height1 * 5))
    knightatk2_frames.append(knightatk2_frame)

knightatk2_index = 0
knightatk2_image = knightatk2_frames[knightatk2_index]
knightatk2_timer = 0

knightwindup2_frames = []
for i in range(knightwindup2_framecount) :
    knightwindup2_frame = knightwindup2.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
    knightwindup2_frame = pygame.transform.scale(knightwindup2_frame, (frame_width1 * 5, frame_height1 * 5))
    knightwindup2_frames.append(knightwindup2_frame)

knightwindup2_index = 0
knightwindup2_image = knightwindup2_frames[knightwindup2_index]
knightwindup2_timer = 0

knightblock_frames = []
for i in range(knightblock_framecount):
    knightblock_frame = knightblock.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
    knightblock_frame = pygame.transform.scale(knightblock_frame, (frame_width1 * 5, frame_height1 * 5))
    knightblock_frames.append(knightblock_frame)

knightblock_index = 0
knightblock_image = knightblock_frames[knightblock_index]
knightblock_timer = 0

#--------------------------------------------ATTACK FUNCTION------------------------------------------------------#
attack_list = {
    1: {
        #NEWSLASH
        'windup_frames':knightwindup_frames,
        'windup_clock': 45,
        'damage':35,
        'attack_frames':knightatk1_frames,
        'attack_speed':5,
        'attack_hurtsfor' :6
    },
    2:{
        #INSTASLASH
        'windup_frames':knightwindup2_frames,
        'windup_clock': 45,
        'damage':10,
        'attack_frames':knightatk2_frames,
        'attack_speed':8,
        'attack_hurtsfor' :3
    }
}

def knightchoose_attack() :
    global currentknightatk, knightattackdata
    currentknightatk = random.randint(1,2)
    knightattackdata = attack_list[currentknightatk]
#------------------------------------------------MISC---------------------------------------------------------------------------#
tutorialersss = pygame.image.load("CBgallery/sprites/tutorial_infant.png").convert_alpha()
tutorialersss = pygame.transform.scale(tutorialersss, (170,170))
tutorial_talk = pygame.image.load("CBgallery/sprites/tutorinfa_talk.png").convert_alpha()
tut_text = pygame.image.load("CBgallery/sprites/tut_text.png").convert_alpha()
tut_text = pygame.transform.scale(tut_text, (500, 200))
parriedlol = pygame.image.load("CBgallery/sprites/parrieduntitled.png")

tuttext_rect = tut_text.get_rect(midbottom=(40,200))
tutinf_status = "hi"
parried_frame_count = 8

parried_frames = []
for i in range(parried_frame_count) :
    parried_frame = parriedlol.subsurface(pygame.Rect(i * frame_width1, 0, frame_width1, frame_height1))
    parried_frame = pygame.transform.scale(parried_frame, (frame_width1 * 3, frame_height1 * 3))
    parried_frames.append(parried_frame)

parried_index = 0 
parried_image = parried_frames[parried_index]
parried_timer = 0
#--------------------------------------------------SCREENS----------------------------------------------------------------#

def menu_screen () :
    global menuflag_timer, menuflag_index, menuflag_image, menuflag_rect
    window_screen.fill((64,64,64))

    game_name = font.render("Clashing Blades", False, "yellow")
    game_name = pygame.transform.scale(game_name, (705, 225))
    game_name_rect = game_name.get_rect(center=(600,200))
    start_name = font.render("Press 1 to play!", False, "white")
    start_name = pygame.transform.scale(start_name, (300,45))
    start_name_rect = start_name.get_rect(center=(600,550))
    thisademo = font.render("THIS IS STILL A DEMO! ! ! ! !", False, "firebrick3")
    thisademo = pygame.transform.scale(thisademo, (300, 100))

    menuflag_timer += 1
    if menuflag_timer >= 30:
        menuflag_index = (menuflag_index + 1) % len(menuflag_frames)
        menuflag_image = menuflag_frames[menuflag_index]
        menuflag_timer = 0

    window_screen.blit(menuflag_image, menuflag_rect)
    window_screen.blit(game_name, game_name_rect)
    window_screen.blit(thisademo, (300, 100))
    window_screen.blit(start_name, start_name_rect)
    
def option_screen() :
    window_screen.blit(tutor, (0,0))

def tutorial_screen() :
    window_screen.fill((255,255,255))
  
    #window_screen.blit(tutorialersss, (18, 562))

def cutscene_1() :
    window_screen.fill((144,24,239))
    ok_nice = font.render("ok nice", False, "black")
    window_screen.blit(ok_nice, (100, 550))

def GAME_OVER() :
    window_screen.fill((0,0,0))
    youRdead = font.render("GAME OVER", False, "white")
    youRdead = pygame.transform.scale(youRdead, (950, 179))
    goback = font.render("Go back to menu?", False, "white")
    goback = pygame.transform.scale(goback, (550, 65))
    presme = font.render("[Press Q]", False, "grey25")
    presme = pygame.transform.scale(presme,(290, 63))
    window_screen.blit(goback, (340, 500))
    window_screen.blit(presme, (464, 580))
    window_screen.blit(youRdead, (150, 200))


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == 
 		pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            exit()

        if game_status == "menu" :
         if event.type == pygame.KEYDOWN and event.key == pygame.K_1 :
            game_status = "optionz"

        if game_status == "optionz" :
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p :
             game_status = "battletime"

        if game_status == "YouAre?" :
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q :
                game_status = "menu"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE :
                pygame.quit()
                exit()

        if game_status == "battletime" :
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and user_status == "idle" :
                user_status = "parrying"
                print("parry")
                userparry_index = 0
                userparry_timer = 0
                userparry_image = userparry_frames[0]

            if event.type == pygame.KEYDOWN and event.key == pygame.K_f and user_status == "idle" and cOURAGE_RELEASE :
                user_status = "slashingg"
                print("look guys i slashed all over him")
                cOURAGE_RELEASE = False
                success_strike = True
                userslash_index = 0
                userslash_timer = 0
                userslash_image = userslash_frames[0]


    if game_status == "tutorialtime" :
        if tutinf_status == "hi" :
            window_screen.blit(tutorialersss, (18, 562))

        if tutinf_status == "talk" :
            window_screen.blit(tut_text, (179,380))
            print("shf")

    if game_status == "youwon" :
        window_screen.blit(thankyou, (0,0))
        celebrate.play()

    if game_status == "YouAre?" :
        gameoversound.play()




    if game_status == "battletime" :
        window_screen.blit(battlebackground, (0,0))
        window_screen.blit(status_bar, statusbar_rect)

        knight_attack_timer += 1

        if knight_status == "idle" :
            knightstance_timer += 1
            if knightstance_timer >= 5:
                knightstance_index = (knightstance_index + 1) % len(knightstance_frames)
                knightstance_image = knightstance_frames[knightstance_index]
                knightstance_timer = 0

            if knight_attack_timer > next_attacktime :
                knightchoose_attack()
                knight_status = "herehecomes"
                knight_attack_timer = 0
                knightwindup_index = 0
                knightwindup_timer = 0
            window_screen.blit(knightstance_image, knightstance_rect)
           

        elif knight_status == "herehecomes" :
            knightwindup_timer += 1
            currentwindup_frames = knightattackdata['windup_frames']
            windup_clock = knightattackdata['windup_clock']
            if knightwindup_timer >= 5 :
                knightwindup_index = (knightwindup_index + 1 ) % len(currentwindup_frames)
                knightwindup_image = currentwindup_frames[knightwindup_index]
                knightwindup_timer = 0

            if knight_attack_timer >= windup_clock :
                knight_status = "he_atak"
                knight_attack_timer = 0
                knightatk_anim_timer = 0
            window_screen.blit(knightwindup_image, knightstance_rect)

        elif knight_status == "he_atak" :
            knightatk_anim_timer += 1
            currentattack_frames = knightattackdata['attack_frames']
            currentattack_speed = knightattackdata['attack_speed']
            currentattack_damage = knightattackdata['damage']

            current_frame = knightatk_anim_timer // currentattack_speed
            
            if current_frame < len(currentattack_frames) :
                currentattack_image = currentattack_frames[current_frame]
                window_screen.blit(currentattack_image, knightstance_rect)
            else :
                if user_status == "parrying" :
                    parrysound.play()
                    user_COURAGE += 1
                    print('sd')
                    success_parry = True
                    sucparry_timer = 0
                    sucparry_duration = 60
                    if user_COURAGE >= max_COURAGE :
                        print("may courage.....")
                        cOURAGE_RELEASE = True
                        user_COURAGE = 0
                else :
                    print("zamn")
                    owiesound.play()
                    user_health -= currentattack_damage
                knight_status = "tireddboy"
                knight_attack_timer = 0
                knightatk1_index = 0
                knightatk1_timer = 0

        elif knight_status == "ah" :
            knightblock_timer += 1
            if knightblock_timer >= 7 :
                knightblock_timer = 0
                if knightblock_index < len(knightblock_frames) :
                    knightblock_image = knightblock_frames[knightblock_index]
                    knightblock_index += 1
                else :
                  knightblock_index = 0
                  knightblock_image = knightblock_frames[knightblock_index]
            window_screen.blit(knightblock_image, knightstance_rect)

            if knight_attack_timer >= knightblock_duration :
              knight_status = "idle"
              knight_attack_timer = 0
              next_attacktime = random.randint(64, 240)
              knightblock_index = 0

        elif knight_status == "tireddboy" :
            if knight_attack_timer >= knight_recovery :
                knight_status = "idle"
                knight_attack_timer = 0
                next_attacktime = random.randint(64, 240)
            window_screen.blit(knightstance_image, knightstance_rect)

        if success_parry :
            sucparry_timer += 1
            parried_timer += 1
            if parried_timer >= 8 :
                parried_timer = 0
                if parried_index < len(parried_frames) :
                    parried_image = parried_frames[parried_index]
                    parried_index += 1
            window_screen.blit(parried_image, (400,300))
            if sucparry_timer >= sucparry_duration :
                success_parry = False
                parried_index = 0
            

        if user_status == "idle" :
            useridle_timer += 1
            if useridle_timer >= 30 :
               useridle_index = (useridle_index + 1) % len(useridle_frames)
               useridle_image = useridle_frames[useridle_index]
               useridle_timer = 0
            window_screen.blit(useridle_image, useridle_rect)

        elif user_status == "parrying" :
          userparry_timer += 1
          if userparry_timer >= 8 :
              userparry_timer = 0
              if userparry_index < len(userparry_frames) :
                userparry_image = userparry_frames[userparry_index]
                userparry_index += 1
              else :
                user_status = "idle"
                useridle_index = 0
          window_screen.blit(userparry_image, userparry_rect)

        elif user_status == "slashingg" :
            userslash_timer += 1
            slashsound.play()
            if userslash_timer >= 6 :
                userslash_timer = 0
                if userslash_index < len(userslash_frames) :
                    userslash_image = userslash_frames[userslash_index]
                    userslash_index += 1
                else :
                    knight_health -= 1
                    knight_status = "ah"
                    knigntblock_timer = 0
                    knightblock_index = 0
                    knight_attack_timer = 0
                    user_status = "idle"
                    useridle_index = 0
            window_screen.blit(userslash_image, userslash_rect)

        if user_health == 0 :
            game_status = "YouAre?"

        userhealthidk = font.render(f"{user_health}", False, "green2")
        userhealthidk = pygame.transform.scale(userhealthidk, (100,45))
        window_screen.blit(userhealthidk, (600, 640))

        courage_text = font.render(f"YOUR PARRIES : {user_COURAGE}", False, "green2")
        courage_text = pygame.transform.scale(courage_text, (300, 45))
        window_screen.blit(courage_text, (450, 670))

        
        if cOURAGE_RELEASE :
            maxcour = font.render("SLASH AVAILABLE", False, "white")
            maxcour = pygame.transform.scale(maxcour, (280, 45))
            window_screen.blit(maxcour, (460, 640))

        knhealt = font.render(f"KNIGHT HEALTH : {knight_health}", False, "white")
        knhealt = pygame.transform.scale(knhealt , (320, 50))
        window_screen.blit(knhealt, (440, 600))


        if user_health <= 0 :
            game_status = "YouAre?"
            knight_status = "idle"
            user_status = "idle"
            knight_attack_timer = 0

        if knight_health <= 0 :
            game_status = "youwon"
            knight_status = "idle"
            user_status = "idle"
            knight_attack_timer = 0
        
    if game_status == "menu" :
        menu_screen()

    if game_status == "optionz" :
        option_screen()
        print("1")

    if game_status == "tutorialtime" :
        tutorial_screen()
        print("2")

    if game_status == "cutscene1" :
        cutscene_1()
        print("3")

    if game_status == "YouAre?" :
        GAME_OVER()
        print("4")
    
    pygame.display.update()
    clock.tick(FPS)

#KEYBINDS
 #- on cutscene, tutorial screen, and option screen, press 0 to go back to the menu
