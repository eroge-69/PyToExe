import pygame
import math
import random
import pickle
import os
import time

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Игра со щитом")

WHITE = (230, 230, 230)
BLACK = (20, 20, 20)
GRAY1 = (80, 80, 80)
GRAY2 = (160, 160, 160)
GRAY3 = (200, 200, 200)
GRAY4 = (100, 100, 100)

class Player:
    def __init__(self, x, y, angle=0):
        self.x = x
        self.y = y
        self.angle = angle
        self.shield_length = 90
        self.shield_width = 8
        self.rotation_speed = 3.45
        
    def rotate_left(self):
        self.angle += self.rotation_speed
    def rotate_right(self):
        self.angle -= self.rotation_speed
    def draw(self, screen, color_shield=GRAY2, color_center=GRAY4):
        pygame.draw.circle(screen, GRAY1, (self.x, self.y), 20)
        arrow_len = 25
        arrow_angle = self.angle
        ax = self.x + arrow_len * math.cos(math.radians(arrow_angle))
        ay = self.y - arrow_len * math.sin(math.radians(arrow_angle))
        pygame.draw.line(screen, WHITE, (self.x, self.y), (ax, ay), 3)
        arc_radius = 36
        arc_width = 3
        arc_angle = 60
        start_angle = math.radians(self.angle - arc_angle/2)
        end_angle = math.radians(self.angle + arc_angle/2)
        rect = pygame.Rect(self.x - arc_radius, self.y - arc_radius, arc_radius*2, arc_radius*2)
        pygame.draw.arc(screen, color_shield, rect, start_angle, end_angle, arc_width)
        pygame.draw.circle(screen, color_center, (self.x, self.y), 5)

class Bullet:
    def __init__(self, x, y, target_x, target_y, speed=3):
        self.x = x
        self.y = y
        self.speed = speed
        
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.dx = (dx / distance) * speed
            self.dy = (dy / distance) * speed
        else:
            self.dx = 0
            self.dy = speed
            
    def move(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, screen):
        pygame.draw.circle(screen, GRAY3, (int(self.x), int(self.y)), 7)
        
    def is_off_screen(self):
        return (self.x < -20 or self.x > WIDTH+20 or self.y < -20 or self.y > HEIGHT+20)
        
    def collides_with_shield(self, player):
        arc_radius = 36
        arc_angle = 60
        dx = self.x - player.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > arc_radius + 7 or dist < arc_radius - 7:
            return False
        bullet_angle = math.degrees(math.atan2(dy, dx))
        diff = (bullet_angle - player.angle + 360) % 360
        if diff > 180:
            diff -= 360
        return abs(diff) <= arc_angle / 2

class QAgent:
    def __init__(self, actions, filename="ai_knowledge.pkl"):
        self.q = {}
        self.actions = actions
        self.filename = filename
        self.load()
    def get_state(self, player, bullets):
        if not bullets:
            return (0, 0, 0, 0)
        bullet = min(bullets, key=lambda b: math.hypot(b.x - player.x, b.y - player.y))
        dx = bullet.x - player.x
        dy = player.y - bullet.y
        dist = int(min(99, math.hypot(dx, dy)//10))
        angle_to_bullet = int((math.degrees(math.atan2(dy, dx)) - player.angle + 360) % 360 // 15)
        player_angle = int(player.angle % 360 // 15)
        speed = int(math.hypot(bullet.dx, bullet.dy))
        return (player_angle, angle_to_bullet, dist, speed)
    def choose_action(self, state, eps=0.1):
        if random.random() < eps:
            return random.choice(self.actions)
        qs = [self.q.get((state, a), 0) for a in self.actions]
        maxq = max(qs)
        return random.choice([a for a, qv in zip(self.actions, qs) if qv == maxq])
    def update(self, state, action, reward, next_state, alpha=0.2, gamma=0.95):
        best_next = max([self.q.get((next_state, a), 0) for a in self.actions])
        old = self.q.get((state, action), 0)
        self.q[(state, action)] = old + alpha * (reward + gamma * best_next - old)
    def save(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.q, f)
    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as f:
                self.q = pickle.load(f)

def train_ai(agent, episodes=100):
    print(f"[AI] Начало обучения на {episodes} эпизодах...")
    scores = []
    for ep in range(1, episodes+1):
        player = Player(WIDTH // 2, HEIGHT // 2, angle=0)
        bullets = []
        score = 0
        lives = 3
        bullet_spawn_timer = 0
        bullet_spawn_delay = 120
        min_bullet_delay = 10
        rotation_speed = 3.45
        progression_timer = 0
        progression_level = 1
        running = True
        last_state = last_action = None
        reward = 0
        while running:
            state = agent.get_state(player, bullets)
            action = agent.choose_action(state, eps=0.2)
            if action == "left": player.angle += rotation_speed
            elif action == "right": player.angle -= rotation_speed
            
            progression_timer += 1
            if progression_timer >= 300:
                progression_timer = 0
                bullet_spawn_delay = max(int(bullet_spawn_delay * 0.90), min_bullet_delay)
                rotation_speed *= 1.10
                progression_level += 1
                
            bullet_spawn_timer += 1
            if bullet_spawn_timer >= bullet_spawn_delay:
                bullet_spawn_timer = 0
                side = random.choice(['top', 'bottom', 'left', 'right'])
                if side == 'top': x = random.randint(0, WIDTH); y = -10
                elif side == 'bottom': x = random.randint(0, WIDTH); y = HEIGHT + 10
                elif side == 'left': x = -10; y = random.randint(0, HEIGHT)
                else: x = WIDTH + 10; y = random.randint(0, HEIGHT)
                bullets.append(Bullet(x, y, player.x, player.y))
                
            for bullet in bullets[:]:
                bullet.move()
                hit = bullet.collides_with_shield(player)
                if hit:
                    bullets.remove(bullet)
                    score += 10
                    reward += 2
                    continue
                dist_to_player = math.sqrt((bullet.x - player.x)**2 + (bullet.y - player.y)**2)
                if dist_to_player < 20:
                    bullets.remove(bullet)
                    lives -= 1
                    reward -= 2
                    if lives <= 0:
                        running = False
                    continue
                if bullet.is_off_screen():
                    bullets.remove(bullet)
                    
            if last_state is not None and last_action is not None:
                agent.update(last_state, last_action, reward, state)
            last_state, last_action, reward = state, action, 0
            
        scores.append(score)
        if ep % 10 == 0 or ep == 1:
            avg = sum(scores[-20:]) / min(len(scores), 20)
            print(f"[AI] Эпизод {ep}/{episodes} | Счет: {score} | Средний (20): {avg:.1f}")
    agent.save()
    print("[AI] Обучение завершено! Знания сохранены.")

def main():
    clock = pygame.time.Clock()
    player = Player(WIDTH // 2, HEIGHT // 2, angle=0)
    bullets = []
    score = 0
    lives = 3
    bullet_spawn_timer = 0
    font = pygame.font.Font(None, 36)
    
    bullet_spawn_delay = 120
    min_bullet_delay = 10
    rotation_speed = 3.45
    progression_timer = 0
    progression_level = 1
    
    running = True
    agent = QAgent(["left", "right", "none"])
    ai_mode = False
    training = False
    last_state = last_action = None
    reward = 0
    
    max_training_episodes = 100
    training_episode = 1
    training_scores = []
    training_lives = []
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        player.rotation_speed = rotation_speed
        
        mods = pygame.key.get_mods()
        if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_ALT:
            if keys[pygame.K_h]:
                ai_mode = not ai_mode
                pygame.time.wait(300)
            if keys[pygame.K_j]:
                training = True
                ai_mode = True
                pygame.time.wait(300)
        
        if ai_mode:
            state = agent.get_state(player, bullets)
            if training:
                action = agent.choose_action(state, eps=0.2)
            else:
                action = agent.choose_action(state, eps=0.0)
            if action == "left":
                player.angle += rotation_speed
            elif action == "right":
                player.angle -= rotation_speed
                
            if last_state is not None and last_action is not None:
                agent.update(last_state, last_action, reward, state)
            last_state, last_action, reward = state, action, 0
        else:
            if keys[pygame.K_LEFT]:
                player.rotate_left()
            if keys[pygame.K_RIGHT]:
                player.rotate_right()
        
        progression_timer += 1
        if progression_timer >= 300:
            progression_timer = 0
            bullet_spawn_delay = max(int(bullet_spawn_delay * 0.90), min_bullet_delay)
            rotation_speed *= 1.10
            progression_level += 1
        
        bullet_spawn_timer += 1
        if bullet_spawn_timer >= bullet_spawn_delay:
            bullet_spawn_timer = 0
            
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x = random.randint(0, WIDTH)
                y = -10
            elif side == 'bottom':
                x = random.randint(0, WIDTH)
                y = HEIGHT + 10
            elif side == 'left':
                x = -10
                y = random.randint(0, HEIGHT)
            else:
                x = WIDTH + 10
                y = random.randint(0, HEIGHT)
                
            bullets.append(Bullet(x, y, player.x, player.y))
            
        for bullet in bullets[:]:
            bullet.move()
            
            hit = bullet.collides_with_shield(player)
            if hit:
                bullets.remove(bullet)
                score += 10
                reward += 2
                continue
                
            dist_to_player = math.sqrt((bullet.x - player.x)**2 + (bullet.y - player.y)**2)
            if dist_to_player < 20:
                bullets.remove(bullet)
                lives -= 1
                reward -= 2
                if lives <= 0:
                    running = False
                continue
                
            if bullet.is_off_screen():
                bullets.remove(bullet)
                
        screen.fill(BLACK)
        
        player.draw(screen)
        
        for bullet in bullets:
            bullet.draw(screen)
            
        score_text = font.render(f"Счет: {score}", True, WHITE)
        lives_text = font.render(f"Жизни: {lives}", True, WHITE)
        level_text = font.render(f"Уровень: {progression_level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        screen.blit(level_text, (10, 90))
        
        if training:
            avg_score = sum(training_scores[-20:]) / min(len(training_scores), 20) if training_scores else 0
            train_text = font.render(f"Обучение: эпизод {training_episode}/{max_training_episodes}", True, WHITE)
            avg_text = font.render(f"Средний счет (20): {avg_score:.1f}", True, WHITE)
            screen.blit(train_text, (10, 130))
            screen.blit(avg_text, (10, 170))
        
        pygame.display.flip()
        if training:
            time.sleep(0.0006)
        else:
            clock.tick(60)
        
        if not running and ai_mode and training:
            agent.save()
            training_scores.append(score)
            training_lives.append(lives)
            training_episode += 1
            if training_episode > max_training_episodes:
                training = False
                ai_mode = False
                break
            player = Player(WIDTH // 2, HEIGHT // 2, angle=0)
            bullets = []
            score = 0
            lives = 3
            bullet_spawn_timer = 0
            bullet_spawn_delay = 120
            rotation_speed = 3.45
            progression_timer = 0
            progression_level = 1
            running = True
            last_state = last_action = None
            reward = 0
            continue

    screen.fill(BLACK)
    game_over_text = font.render("Игра окончена!", True, WHITE)
    final_score_text = font.render(f"Финальный счет: {score}", True, WHITE)
    restart_text = font.render("Нажмите любую клавишу для выхода", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                waiting = False
                
    pygame.quit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--train":
        agent = QAgent(["left", "right", "none"])
        episodes = 100
        if len(sys.argv) > 2:
            try:
                episodes = int(sys.argv[2])
            except ValueError:
                print("[AI] Некорректное число эпизодов, используется 100 по умолчанию.")
        train_ai(agent, episodes=episodes)
    else:
        main()
