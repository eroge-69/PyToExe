import pygame, math, time

pygame.init()

#CLASSES AND FUNCTIONS START
class Objects:
	def __init__(self, mass, velocity, size, x, y, locked=False):
		self.mass = mass
		self.v_x = velocity[0]
		self.v_y = velocity[1]
		self.size = size
		self.x = x
		self.y = y
		self.locked = locked
	
	def move(self):
		self.x += (self.v_x*SCALE/(100*SCALE))*timeclick
		self.y += (self.v_y*SCALE/(100*SCALE))*timeclick
		
	def draw(self):
		pygame.draw.circle(screen, (0,0,255),(int(self.x*SCALE),int(self.y*SCALE)), self.size*SCALE)
		
	def collide(self):
			for i in reversed(range(len(objs))):
				if i > len(objs):
					i = 0
				if objs[i] != self:
					if math.sqrt((objs[i].x - self.x)**2 + (objs[i].y - self.y)**2) < self.size:
						self.size += objs[i].size
						self.mass += objs[i].mass
						if not self.locked and not objs[i].locked:
							self.v_x += (self.v_x + objs[i].v_x)/((self.mass + objs[i].mass)/10)
							self.v_y += (self.v_y + objs[i].v_y)/((self.mass + objs[i].mass)/10)
						objs.pop(i)
	
	def gravpull(self, Fg, D, A, theta):
		ax = 0
		ay = 0
		y = 100
		for i in range(len(objs)):
			pygame.draw.line(screen, (108,13,196),(int(self.x*SCALE), int(self.y*SCALE)),(int(objs[i].x*SCALE), int(objs[i].y*SCALE)), 2)
		if not self.locked:
			for i in range(len(objs)):
				theta = math.atan2((objs[i].y - self.y)*SCALE,(objs[i].x - self.x)*SCALE)
				D = math.sqrt(((objs[i].x - self.x)**2)+ ((objs[i].y  - self.y)**2))
				if D != 0:
					Fg = ((((G*(objs[i].mass*20)*(self.mass*20))/((D**2)))))*timeclick
					A = Fg/self.mass
					ax = (math.cos(theta)*A)
					ay = (math.sin(theta)*A)
					self.v_x += ax
					self.v_y += ay
			
		
		
	
def createobject(temploc, mouse):
	try:
		x,y = temploc
		velocity = (int((mouse[0]-x)),int((mouse[1]-y)))
		obj = Objects(SHIPMASS, velocity, size, x/SCALE, y/SCALE, Locked)
		return obj
	except:
		pass
#CLASSES AND FUNCTIONS END

screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
clock = pygame.time.Clock()

#CONSTANTS START
G = 5
SHIPMASS = 100
SCALE = 1
COPSCALE = SCALE
size = 10
#CONSTANTS END

font = pygame.font.SysFont("character.tt", 60)
objs = []
temploc = 0
iteration = 0
Fg = 0
D = 0
A = 0
theta = 0
scalechange = False
first = True
Locked = False
MSL = False
sliding = False
mouselocs = [(0,0)]
dists = []
fingers = {}

#UI START
mousesqr = pygame.Rect(0,0,0,0)
MenuAButton = pygame.Rect((screen.get_width())-200, screen.get_height()-200, 120, 120)
Menutext = pygame.transform.rotate(font.render("Menu", (0,0,0), True), -90)
MenuaButton = False
MenuA = pygame.Rect((screen.get_width()-700, screen.get_height()-900, 600, 600))
PlaceButton = pygame.Rect(screen.get_width()-200, screen.get_height()-900, 150, 600)
Placetext = pygame.transform.rotate(font.render("Place Objects", (0,0,0), True), -90)
PlacebuttonClick = True
PlaceMenu = pygame.Rect(0, 0, 200, screen.get_height())
SwipeButton = pygame.Rect(screen.get_width()-350, screen.get_height()-900, 150, 600)
Swipetext = pygame.transform.rotate(font.render("Move Around", (0,0,0), True), -90)
swiping = False
ResetButton = pygame.Rect(screen.get_width()-500, screen.get_height()-900, 150, 600)
Deletetext = pygame.transform.rotate(font.render("Delete All Objects", (0,0,0), True), -90)
TimeRect = pygame.Rect((screen.get_width())-200, 0, 120, 220)
timeclick = 1
TimeText = pygame.transform.rotate(font.render("Speed: "+str(timeclick)+"x" , (0,0,0), True), -90)
timebutton = False

#SLIDERS START
SliderMassRect = pygame.Rect(50, 100, 50, 500)
SliderMassText = pygame.transform.rotate(font.render("MASS: "+str(SHIPMASS), (0,0,0), True), -90)
SliderMassSlider = pygame.Rect(50, 100, 50, 50)
SliderSizeRect = pygame.Rect(50, 700, 50, 500)
SliderSizeText = pygame.transform.rotate(font.render("SIZE: "+str(size), (0,0,0), True), -90)
SliderSizeSlider = pygame.Rect(50, 700, 50, 50)
SliderColourRect = pygame.Rect(50, 1300, 50, 500)
CheckBoxLockedRect = pygame.Rect(20, 2000, 100, 100)
CheckBoxLockedText = pygame.transform.rotate(font.render("Locked", (0,0,0), True), -90)
#SLIDERS END
#UI END


while True:
	mousepos = pygame.mouse.get_pos()
	mousesqr = pygame.Rect(mousepos[0],mousepos[1],20,20)
	screen.fill((0,0,0)) 
	for event in pygame.event.get():
		if event.type == pygame.FINGERDOWN:
			x = event.x * screen.get_width()
			y = event.y * screen.get_height()
			fingers[event.finger_id] = x, y
			if swiping:
				mouselocs = []
			if mousesqr.colliderect(MenuAButton):
				if not MenuaButton:
					MenuaButton = True
				else:
					MenuaButton = False
			elif mousesqr.colliderect(TimeRect):
					if timeclick < 3:
						timeclick += 1
					elif timeclick == 3:
						timeclick = 5
					else:
						timeclick = 1
					TimeText = pygame.transform.rotate(font.render("Speed: "+str(timeclick)+"x" , (0,0,0), True), -90)
					
			elif MenuaButton:
				if mousesqr.colliderect(ResetButton):
					objs = []
				if mousesqr.colliderect(SwipeButton):
					swiping = True
					PlacebuttonClick = False
				if mousesqr.colliderect(PlaceButton):
					PlacebuttonClick = True
					swiping = False
					MenuaButton = False
			elif PlaceMenu:
				if mousesqr.colliderect(CheckBoxLockedRect):
					if Locked:
						Locked = False
					else:
						Locked = True
				elif PlacebuttonClick and mousesqr.x > 200:	
					temploc = pygame.mouse.get_pos()
					
		if event.type == pygame.FINGERUP:
			fingers.pop(event.finger_id, None)
			mouselocs = []
			sliding = False
			if temploc and PlacebuttonClick:
				swiping = False
				obj = createobject(temploc, mousepos)
				objs.append(obj)
			temploc = None
		if event.type == pygame.FINGERMOTION:
			x = event.x * screen.get_width()
			y = event.y * screen.get_height()
			fingers[event.finger_id] = x, y
	if temploc:
		pygame.draw.line(screen, (255,255,255),temploc, mousepos)
		pygame.draw.circle(screen, (0, 255, 0), temploc, size*SCALE)
	
	#if COPSCALE != SCALE:
#		scalechange = True

	for obj in objs:
		obj.draw()
		obj.gravpull(Fg, D, A, theta)
		obj.move()
		obj.collide()
	
	
	pygame.draw.rect(screen, (255,255,255), MenuAButton)
	screen.blit(Menutext, ((screen.get_width())-160, screen.get_height()-197))
	pygame.draw.rect(screen, (255,255,255), TimeRect)
	screen.blit(TimeText, ((screen.get_width())-160, 10))
	if MenuaButton:
		pygame.draw.rect(screen, (255,255,255), MenuA)
		pygame.draw.rect(screen, (255,0,255), PlaceButton)
		screen.blit(Placetext, (screen.get_width()-160, screen.get_height()-750))
		pygame.draw.rect(screen, (0,255,0), SwipeButton)
		screen.blit(Swipetext, (screen.get_width()-310, screen.get_height()-750))
		pygame.draw.rect(screen, (255,0,0), ResetButton)
		screen.blit(Deletetext, (screen.get_width()-460, screen.get_height()-750))
	if PlacebuttonClick:
		pygame.draw.rect(screen, (255,0,255), PlaceMenu)
		pygame.draw.rect(screen, (255, 255, 255), SliderMassRect)
		pygame.draw.rect(screen, (0,0,0), SliderMassSlider)
		screen.blit(SliderMassText, (0, 100))
		pygame.draw.rect(screen, (255, 255, 255), SliderSizeRect)
		pygame.draw.rect(screen, (0,0,0), SliderSizeSlider)
		screen.blit(SliderSizeText, (0, 700))
		pygame.draw.rect(screen, (255, 255, 255), SliderColourRect)
		pygame.draw.rect(screen, (255, 255, 255), CheckBoxLockedRect)
		screen.blit(CheckBoxLockedText, (120, 2000))
		if Locked:
			pygame.draw.line(screen, (0,0,0), (40, 2040),(70, 2020), 10)
			pygame.draw.line(screen, (0,0,0), (100, 2070),(40, 2040), 10)
	
	if swiping and len(fingers.items()) == 1:
		if len(mouselocs) == 0:
			mouselocs.append(pygame.mouse.get_pos())
		for i in range(len(mouselocs)):
			if mouselocs[i] != mousepos:
				if i == len(mouselocs)-1:
					mouselocs.append(pygame.mouse.get_pos())
		if len(mouselocs) > 10:
			mouselocs.pop(0)
		if mouselocs[len(mouselocs)-1] == mouselocs[0][0] or mouselocs[len(mouselocs)-1][1] == mouselocs[0][1]:
			pass
		for i in range(len(objs)):
			try:
				objs[i].x += ((mouselocs[len(mouselocs)-1][0] - mouselocs[0][0]))/(SCALE*10)
				objs[i].y += ((mouselocs[len(mouselocs)-1][1] -mouselocs[0][1]))/(SCALE*10)
			except:
				pass
	elif swiping and len(fingers.items()) == 2:
		dists.append(math.sqrt(((fingers.get(0)[0]-fingers.get(1)[0])**2)+((fingers.get(0)[1]-fingers.get(1)[1])**2)))
		if dists[0] - dists[len(dists)-1] < 0 and SCALE < 5:
			SCALE += ((abs(dists[0] - dists[len(dists)-1])))/20000
		elif dists[0] - dists[len(dists)-1] > 0 and SCALE > 0.1:
			SCALE -= ((abs(dists[0] - dists[len(dists)-1]))/20000)
		
		SCALE = abs(SCALE)
		if len(dists)-1 > 10:
			dists.pop(0)
	else:
		mouselocs = []
		dists = []
		
	if scalechange:
		COPSCALE = SCALE
		scalechange = False
	
	if PlaceMenu:
		mousepos = pygame.mouse.get_pos()
		mousesqr = pygame.Rect(mousepos[0],mousepos[1],20,20)
		if (mousesqr.colliderect(SliderMassSlider) and mousesqr.x < 200):
			sliding = True
		else:
			sliding = False
		if sliding:
			SliderMassSlider.y = pygame.mouse.get_pos()[1]
			if SliderMassSlider.y < 100:
				SliderMassSlider.y = 100
			elif SliderMassSlider.y > 550:
				SliderMassSlider.y = 550
				
		if (mousesqr.colliderect(SliderSizeSlider) and mousesqr.x < 200):
			sliding = True
		else:
			sliding = False
		if sliding:
			SliderSizeSlider.y = pygame.mouse.get_pos()[1]
			if SliderSizeSlider.y < 700:
				SliderSizeSlider.y = 700
			elif SliderSizeSlider.y > 1150:
				SliderSizeSlider.y = 1150
		
	
	if (((SliderMassSlider.y-96)/400)*10000) != SHIPMASS:
		SHIPMASS =((SHIPMASS/108000)*400)+96
		SHIPMASS = (((SliderMassSlider.y-96)/400)*10000)
	SliderMassText = pygame.transform.rotate(font.render("MASS: "+str(SHIPMASS), (0,0,0), True), -90)
	
	if (((SliderSizeSlider.y-660)/400)*100) != size:
		size =((size/100)*400)+660
		size = (((SliderSizeSlider.y-660)/400)*100)
	SliderSizeText = pygame.transform.rotate(font.render("SIZE: "+str(size), (0,0,0), True), -90)
	
	#for i in range(len(objs)):
#			if PlaceMenu:
#				if objs[i].x-objs[i].size < 200 or objs[i].x+objs[i].size > screen.get_width():
#					objs[i].v_x = -objs[i].v_x 
			#else:
#				if objs[i].x-objs[i].size < 0 or objs[i].x+objs[i].size > screen.get_width():
#					objs[i].v_x = -objs[i].v_x 
#			if objs[i].y-objs[i].size < 0 or objs[i].y+objs[i].size > screen.get_height():
#				objs[i].v_y = -objs[i].v_y
	
	#for finger, pos in fingers.items():
#		mousesqr = pygame.Rect(pos[0],pos[1],20,20)
#		pygame.draw.rect(screen, (255,255,255), mousesqr)
	pygame.display.flip()
	clock.tick(120)