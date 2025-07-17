import pygame
import sys

# 初始化 pygame
pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("点击图片播放声音")

# 加载图片
image = pygame.image.load("image.jpg")
image_rect = image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# 加载声音
sound = pygame.mixer.Sound("sound.wav")

# 主循环
running = True
while running:
    screen.fill((255, 255, 255))  # 白色背景
    screen.blit(image, image_rect)  # 绘制图片
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 检查鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if image_rect.collidepoint(mouse_pos):
                sound.play()  # 点击图片区域时播放声音

pygame.quit()
sys.exit()
