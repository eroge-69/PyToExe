import pygame

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
player = pygame.Rect(400,500, 10, 20)
radius = 100
other = pygame.Rect(0,0, 10, 20)
others = []
x = 0
y = 0
j = 0
for i in range(100):
	x += i * 10
	if x > screen.get_width():
		j += 1
		x = 0
		y = j * 20
	others.append(pygame.Rect(x,y, 10, 20))
while True:
	screen.fill((0,0,0))
	player.y += 1
	
	pygame.draw.circle(screen, (255,0,0), (player.x+5, player.y+10), radius)
	pygame.draw.rect(screen, (255,255,255), player)
	
	for i in range(len(others)):
			for j in range(len(others)):
				if others[i].colliderect(others[j]):
					others[i].x -= 10
					others[i].y -= 20
					others[j].x += 10
					others[j].y += 20
	
	for other in others:
		if other.x - player.x < radius and other.x - player.x > -radius:
			if other.x-player.x < 0:
				other.x = other.x - 4
			else:
				other.x = other.x + 4
		else:
				if other.x-player.x < 0:
					other.x = other.x + 4
				else:
					other.x = other.x - 4
				
		if other.y - player.y < radius and other.y - player.y > -radius:
			if other.y-player.y < 0:
				other.y = other.y - 4
			else:
				other.y = other.y + 4
		else:
			if other.y-player.y < 0:
				other.y = other.y + 4
			else:
				other.y = other.y -4
	
	
				

		pygame.draw.rect(screen, (255,255,255), other)
				
	clock.tick(1200)
	pygame.display.flip()