import pygame, sys, random, math
pygame.init()
pygame.font.init()
clock = pygame.time.Clock()
background_colour = (20, 240, 16)
sc_w = 1000
sc_h = 600 
screen = pygame.display.set_mode((sc_w, sc_h)) 
pygame.display.set_caption('pool') 
pygame.display.flip() 
running = True
hole_r =math.sqrt(sc_h * sc_w)/23
hole_r2 = hole_r / 1.44
r = hole_r2 * 0.8
u = 0
μ = 0.02

class hole:
   def __init__(self,cx,cy,rad):
      self.cx = cx
      self.cy = cy
      self.rad = rad
   def IsHoleAt(self,x,y):
      if math.sqrt((x - self.cx)**2 + (y - self.cy)**2) <= self.rad:
         return True
      return False      

class line:
   def __init__(self,x0,y0,x1,y1):
    self.x0 = x0
    self.y0 = y0    
    self.x1 = x1
    self.y1 = y1
   def getpoint(self,point):
      if point == 0:
       return (self.x0,self.y0)
      if point == 1:
       return (self.x1,self.y1)
   def getVector(self):
      return (self.x1-self.x0,self.y1-self.y0,)

class ball:
    def __init__ (self, x0 , y0 , ux , uy, color):
        self.x0 = x0
        self.y0 = y0
        self.ux = ux
        self.uy = uy
        self.color = color
    def move(self, a,b):
        self.y0 += b
        self.x0 += a
        if math.sqrt(self.ux**2 + self.uy**2) > 0.3:
            self.ux -= μ*self.ux/math.sqrt(self.ux**2 + self.uy**2)
            self.uy -= μ*self.uy/math.sqrt(self.ux**2 + self.uy**2)
        else :
            self.ux = 0
            self.uy = 0
    def getspeed(self):
        return (math.sqrt((self.ux)** 2 + (self.uy)** 2))
    def getUnitVelocityVector(self):
        return self.ux / (math.sqrt((self.ux)** 2 + (self.uy)** 2)) , self.uy  / (math.sqrt((self.ux)** 2 + (self.uy)** 2))

def checkforCollisions(ball1 , ball2):
  global u
  cntr_vect = (ball1.x0 - ball2.x0,  ball1.y0 - ball2.y0)
  if ( cntr_vect[0] **2 + cntr_vect[1] **2) <= (2 * r)** 2 :
      ab = collision(ball1 , ball2)
      ball1 = ab[0]
      ball2 = ab[1]
  return (ball1, ball2)
    
def collision(ball1, ball2):
    cntr_vect = (ball1.x0 - ball2.x0,  ball1.y0 - ball2.y0)
    vect1_length = (cntr_vect[0] * ball1.ux + cntr_vect[1] * ball1.uy)/ ( cntr_vect[0] **2 + cntr_vect[1] **2)
    u1x = (vect1_length * cntr_vect[0], vect1_length * cntr_vect[1])
    u1y = (ball1.ux - u1x[0], ball1.uy - u1x[1])
    vect2_length = (cntr_vect[0] * ball2.ux + cntr_vect[1] * ball2.uy)/ ( cntr_vect[0] **2 + cntr_vect[1] **2)
    u2x = (vect2_length * cntr_vect[0], vect2_length * cntr_vect[1])
    u2y = (ball2.ux - u2x[0], ball2.uy - u2x[1])
    ball1.ux = u2x[0] + u1y[0]
    ball2.ux = u1x[0] + u2y[0]
    ball1.uy = u2x[1] + u1y[1]
    ball2.uy = u1x[1] + u2y[1]
    ball1.x0 += 2*cntr_vect[0] /math.sqrt( cntr_vect[0] **2 + cntr_vect[1] **2)
    ball1.y0 += 2*cntr_vect[1] /math.sqrt( cntr_vect[0] **2 + cntr_vect[1] **2)
    return (ball1,ball2)
def linecol(Ball,Line):
    global r, running
    ## line Ax + By + G = 0
    A = -1*Line.getVector()[1]
    B = Line.getVector()[0]
    G =-1*A*Line.x0 - B*Line.y0
    side = A*Ball.x0 + B*Ball.y0 + G
    dist = abs(side)/math.sqrt(A**2 + B**2)
    #ab * gd οπου α το διανυσμα γραμη(0) -> μπαλα και ... με τα συνημιτονα να καθοριζουν το προσημο
    if dist <= r and ((Ball.x0 - Line.x0)*(Line.x1-Line.x0) + (Ball.y0 - Line.y0)*(Line.y1-Line.y0))*((Ball.x0 - Line.x1)*(Line.x0-Line.x1) + (Ball.y0 - Line.y1)*(Line.y0-Line.y1)) >= 0:
       cntr_vect = (A, B)
       vect_length = (cntr_vect[0] * Ball.ux + cntr_vect[1] * Ball.uy)/ ( cntr_vect[0] **2 + cntr_vect[1] **2)
       u1x = (vect_length * cntr_vect[0], vect_length * cntr_vect[1])
       u1y = (Ball.ux - u1x[0], Ball.uy - u1x[1])
       Ball.ux = -1*u1x[0] + u1y[0]
       Ball.uy = -1*u1x[1] + u1y[1]
       Ball.move(3*(side / abs(side))*A/ math.sqrt(A **2 +B **2),3*(side / abs(side))*B/ math.sqrt( A **2 + B **2))
    return Ball

def HoleTouchingBall (ball,hole):
   global PoolBalls
   global Combinations
   if hole.IsHoleAt(ball.x0,ball.y0):
      if not ball == Whiteball:
         i=0
         while i < (len(Combinations)):
            if Combinations[i].count(len(PoolBalls) - 1):
               Combinations.remove(Combinations[i])
               i-=1
            i += 1
         PoolBalls.remove(ball)
      else:
         ball.x0 = 1000
         ball.y0 = 300
         ball.ux = 0
         ball.uy = 0



Combinations = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)] #Copy this: ),(   number of combos (n^2 - n)/2
Whiteball = ball(400, 400, 0, 0, "white")
Blueball = ball(500, 500, 0 , 0, "blue")  
Blackball = ball(400, 325, 0 , 0, "black")
Redball = ball(450, 100 , 0 , 0 , "red") 
PoolBalls= [Whiteball,Blueball,Blackball,Redball]

line1 = line(hole_r *1.4,hole_r * 2.46,hole_r * 1.4,sc_h - hole_r*2.46) #καθετη αριστερα
line3 = line(sc_w - hole_r*1.4,hole_r*2.46,sc_w - hole_r*1.4,sc_h - hole_r*2.46) #καθετη δεξιά
line2 = line(hole_r*2.46,hole_r*1.4,sc_w/2-hole_r2*1.1,hole_r*1.4) #οριζόντια πάνω αριστερά
line5 = line(sc_w/2+hole_r2*1.1,hole_r*1.4,sc_w - hole_r*2.46,hole_r*1.4) #οριζόντια πάνω δεξιά
line4 = line(hole_r*2.46,sc_h - hole_r*1.4,sc_w/2-hole_r2*1.1,sc_h - hole_r*1.4) #οριζόντια κάτω αριστερά
line6 = line(sc_w/2+hole_r2*1.1,sc_h - hole_r*1.4,sc_w - hole_r*2.46,sc_h - hole_r*1.4) #οριζόντια κάτω δεξιά
line7 = line(hole_r *1.4,hole_r * 2.46,0,hole_r)
line8 = line(hole_r*2.46,hole_r*1.4,hole_r,0)

Lines = [line1, line2, line3,line4,line5,line6, line7,line8]

hole1 = hole(hole_r,hole_r,hole_r)
hole2 = hole(hole_r,sc_h - hole_r,hole_r)
hole3 = hole(sc_w - hole_r,hole_r,hole_r)
hole4 = hole(sc_w - hole_r,sc_h - hole_r,hole_r)
hole5 = hole(sc_w/2,hole_r2,hole_r2)
hole6 = hole(sc_w/2,sc_h - hole_r2,hole_r2)
Holes = [hole1,hole2,hole3,hole4,hole5,hole6]


mousepos = [0,0]
sum_speed = 0
space_frames = 0.0
hit_step = 0
mode = "menu"
testf = pygame.font.SysFont('Arial', 50)
Title_surf = testf.render("Pool", False, "blue")
button_surf = testf.render("I>", True, "black")
button_rect = button_surf.get_rect(center = (500,500))

# game loop 
while running: 
 keyboard =pygame.key.get_pressed()
 mousepos = pygame.mouse.get_pos()
 clock.tick(100)
 screen.fill(background_colour)
 if mode == "game":    
  for e in Holes:
     pygame.draw.circle(screen,"black",(e.cx,e.cy),e.rad)
  for e in Lines:
       pygame.draw.line(screen,"black",e.getpoint(0),e.getpoint(1),5) 
      
  if keyboard[pygame.K_ESCAPE]:
     mode = "menu"
  if sum_speed > 0:
    hit_step = 0
    space_frames = 0.0
    
    sum_speed = 0
    for x in PoolBalls:
     sum_speed += x.ux**2 + x.uy**2   
     pygame.draw.circle(screen, x.color, (x.x0,x.y0), r)
     x.move(x.ux, x.uy)
     for e in Holes:
      HoleTouchingBall(x,e)

     for e in Lines:
       x = linecol(x, e)
    #update the PoolBalls list for the collision 0 - 1
    for i in Combinations:
     PoolBalls[i[0]], PoolBalls[i[1]] = checkforCollisions(PoolBalls[i[0]],PoolBalls[i[1]])    
  if sum_speed == 0 :
    for i in PoolBalls:
     pygame.draw.circle(screen, i.color, (i.x0,i.y0), r)
    if PoolBalls[0].x0 == 1000 and PoolBalls[0].y0 == 300 :
       mode = "holding"
    else:
     vectorx = (mousepos[0] - PoolBalls[0].x0) / math.sqrt((mousepos[0] - PoolBalls[0].x0) **2 + (mousepos[1] - PoolBalls[0].y0) **2)
     vectory = (mousepos[1] - PoolBalls[0].y0) / math.sqrt((mousepos[0] - PoolBalls[0].x0) **2 + (mousepos[1] - PoolBalls[0].y0) **2)
     pygame.draw.line(screen,"black",(PoolBalls[0].x0 + (1.25*r + space_frames)*vectorx,PoolBalls[0].y0 + (1.25*r + space_frames)*vectory), (PoolBalls[0].x0 + (1.25*r + 160 + space_frames)*vectorx, PoolBalls[0].y0 + (1.25*r + 160 + space_frames)*vectory ) ,3)
    if keyboard[pygame.K_SPACE]:
       if space_frames < 45.0:
         space_frames += 0.8
    elif space_frames > 0.0:  
       if hit_step == 0: hit_step = float(space_frames / 10)
       space_frames -= hit_step
       if abs(space_frames) <= 0.05:  
        PoolBalls[0].ux = -16*math.sin(math.pi*(vectorx* hit_step*10)/ 90) 
        PoolBalls[0].uy = -16*math.sin(math.pi*(vectory* hit_step*10)/ 90)
        sum_speed = 1 
        hit_step = 0
        space_frames = 0   

 if mode == "menu":
    screen.fill((100,100,100))
    screen.blit(Title_surf,Title_surf.get_rect(center = (300,300)))
    screen.blit(button_surf, button_rect)
    if button_rect.collidepoint(mousepos) and pygame.mouse.get_pressed(num_buttons=3)[0]:
       mode = "game"

 if mode == "holding" :
   for e in Holes:
     pygame.draw.circle(screen,"black",(e.cx,e.cy),e.rad)
   for e in Lines:
       pygame.draw.line(screen,"black",e.getpoint(0),e.getpoint(1),5)  
   for x in range (len(PoolBalls)):
     pygame.draw.circle(screen, PoolBalls[len(PoolBalls)-x-1].color, (PoolBalls[len(PoolBalls)-x-1].x0,PoolBalls[len(PoolBalls)-x-1].y0), r)   
   PoolBalls[0].x0 = mousepos[0]
   PoolBalls[0].y0 = mousepos[1]
 for event in pygame.event.get():       
        # Check for QUIT event       
        if event.type == pygame.QUIT: 
            running = False 
 pygame.display.flip()