import pygame
import sys

def play_video(video_path):
    pygame.init()
    
    # Загружаем видео
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(video_path)  # Для аудиофайлов
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Ошибка загрузки видео/аудио: {e}")
        return
    
    # Создаем окно для отображения (если видео поддерживается)
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Воспроизведение видео")
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Обновляем экран (если видео поддерживается)
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    video_file = "2.mp3"  # Укажите путь к вашему видеофайлу
    play_video(video_file)