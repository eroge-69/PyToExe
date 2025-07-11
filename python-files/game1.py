import pygame
import random


pygame.init()

font = pygame.font.SysFont(None, 19, bold=True)
handling_font = pygame.font.SysFont("arial", 25, bold=True)
description_font = pygame.font.SysFont("times new roman", 14)

win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("DRAWPAD")
win.fill((200, 200, 200))

pad = pygame.Surface((600, 570))
pad.fill((255, 255, 255))
editing_place = pad.get_rect()
editing_place.left = editing_place.top = (win.get_size()[1] - pad.get_size()[1]) // 2

button_draw = font.render("DRAW", True, (250, 0, 250), (0, 250, 0))
drawing_button_place = button_draw.get_rect()
drawing_button_place.left = (win.get_size()[0] + pad.get_size()[0] - button_draw.get_size()[0]) // 2
drawing_button_place.top = editing_place.top

button_erase = font.render("ERASE", True, (250, 250, 0), (0, 0, 250))
erasing_button_place = button_erase.get_rect()
erasing_button_place.left = (win.get_size()[0] + pad.get_size()[0] - button_erase.get_size()[0]) // 2
erasing_button_place.top = drawing_button_place.bottom + button_draw.get_size()[1]

button_change_bgcolor = font.render("CHANGE BACK COLOR", True, (100, 180, 20), (200, 20, 45))
bgcolor_changing_button_place = button_change_bgcolor.get_rect()
bgcolor_changing_button_place.left = (win.get_size()[0] + pad.get_size()[0] - button_change_bgcolor.get_size()[0]) // 2
bgcolor_changing_button_place.top = erasing_button_place.bottom + button_erase.get_size()[1]

handling_text = handling_font.render("HANDLING:", True, (20, 100, 180))
handling_place = handling_text.get_rect()
handling_place.left = (win.get_size()[0] + pad.get_size()[0] - handling_text.get_size()[0]) // 2
handling_place.top = win.get_size()[1] - handling_text.get_size()[1] * 10

clr_win = description_font.render("Press C: clear working area", True, (180, 100, 20))
clr_win_place = clr_win.get_rect()
clr_win_place.left = (win.get_size()[0] + pad.get_size()[0] - clr_win.get_size()[0]) // 2
clr_win_place.top = handling_place.bottom + 20

save_img = description_font.render("Press S: save image", True, (180, 100, 20))
save_img_place = save_img.get_rect()
save_img_place.left = (win.get_size()[0] + pad.get_size()[0] - save_img.get_size()[0]) // 2
save_img_place.top = clr_win_place.bottom + 20

erase_sz_first = description_font.render(f"Press {chr(8592)} or {chr(8594)}:", True, (180, 100, 20))
erase_sz_first_place = erase_sz_first.get_rect()
erase_sz_first_place.left = (win.get_size()[0] + pad.get_size()[0] - erase_sz_first.get_size()[0]) // 2
erase_sz_first_place.top = save_img_place.bottom + 20
erase_sz_second = description_font.render("eraser size changing", True, (180, 100, 20))
erase_sz_second_place = erase_sz_second.get_rect()
erase_sz_second_place.left = (win.get_size()[0] + pad.get_size()[0] - erase_sz_second.get_size()[0]) // 2
erase_sz_second_place.top = erase_sz_first_place.bottom

pen_sz_first = description_font.render(f"Press {chr(8593)} or {chr(8595)}:", True, (180, 100, 20))
pen_sz_first_place = pen_sz_first.get_rect()
pen_sz_first_place.left = (win.get_size()[0] + pad.get_size()[0] - pen_sz_first.get_size()[0]) // 2
pen_sz_first_place.top = erase_sz_second_place.bottom + 20
pen_sz_second = description_font.render("pen size changing", True, (180, 100, 20))
pen_sz_second_place = pen_sz_second.get_rect()
pen_sz_second_place.left = (win.get_size()[0] + pad.get_size()[0] - pen_sz_second.get_size()[0]) // 2
pen_sz_second_place.top = pen_sz_first_place.bottom

draw = False
erase = False
options = {"draw": False, "erase": False}
pensize = erasesize = 1
lastbgcolor = (255, 255, 255)
bgcolor = (255, 255, 255)
pencolor = (0, 0, 0)

run = True

while run:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            run = False
        if ev.type == pygame.MOUSEBUTTONDOWN:
            if options["draw"]:
                draw = True
            if options["erase"]:
                erase = True
        if ev.type == pygame.MOUSEBUTTONUP:
            erase = False
            draw = False
            pos = x, y = ev.pos
            if drawing_button_place.collidepoint(pos):
                options["draw"] = True
                options["erase"] = False
            if erasing_button_place.collidepoint(pos):
                options["erase"] = True
                options["draw"] = False
            if bgcolor_changing_button_place.collidepoint(pos):
                lastcolor = bgcolor
                bgcolor = tuple([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)])
                for x in range(pad.get_size()[0]):
                    for y in range(pad.get_size()[1]):
                        if pad.get_at((x, y)) == lastcolor:
                            pad.set_at((x, y), bgcolor)
        if ev.type == pygame.MOUSEMOTION:
            pos = x, y = ev.pos
            if draw and editing_place.collidepoint(pos):
                for xx in range(x - editing_place.left - pensize // 2 - 1, x - editing_place.left + pensize // 2 + 1):
                    for yy in range(y - editing_place.top - pensize // 2 - 1, y - editing_place.top + pensize // 2 + 1):
                        pad.set_at((xx, yy), pencolor)
            if erase and editing_place.collidepoint(pos):
                for xx in range(x  - editing_place.left - erasesize // 2 - 1, x - editing_place.left + erasesize // 2 + 1):
                    for yy in range(y - editing_place.top - erasesize // 2 - 1, y - editing_place.top + erasesize // 2 + 1):
                        pad.set_at((xx, yy), bgcolor)
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_c:
                pad.fill(bgcolor)
            if ev.key == pygame.K_s:
                letters = list(map(lambda x: chr(x), range(65, 65 + 26)))
                name = "".join(random.sample(letters, random.randint(1, len(letters))))
                pygame.image.save(pad, f"{name}.png")
            if ev.key == pygame.K_UP:
                pensize += 1
            if ev.key == pygame.K_DOWN:
                if pensize > 0:
                    pensize -= 1
            if ev.key == pygame.K_RIGHT:
                erasesize += 1
            if ev.key == pygame.K_LEFT:
                if erasesize > 0:
                    erasesize -= 1

    win.blit(pad, editing_place)
    win.blit(button_draw, drawing_button_place)
    win.blit(button_erase, erasing_button_place)
    win.blit(button_change_bgcolor, bgcolor_changing_button_place)
    win.blit(handling_text, handling_place)
    win.blit(clr_win, clr_win_place)
    win.blit(save_img, save_img_place)
    win.blit(erase_sz_first, erase_sz_first_place)
    win.blit(erase_sz_second, erase_sz_second_place)
    win.blit(pen_sz_first, pen_sz_first_place)
    win.blit(pen_sz_second, pen_sz_second_place)
    pygame.display.update()
    pygame.time.Clock().tick(45)
