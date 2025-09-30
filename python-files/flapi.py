import pygame
import random
import math 
import sys
import torch 
import torch.nn as nn 
import copy

WIDTH = 800
HEIGHT = 600
FPS = 60

class Pipe:
    def __init__(self, start_x=None):
        self.x = start_x if start_x else WIDTH
        self.width = 60
        self.gap_size = 120
        self.gap_center = random.randint(self.gap_size//2 + 80, HEIGHT - self.gap_size//2 - 80)
        self.speed = 3
        self.passed_by = []
    
    def update(self):
        self.x -= self.speed
        
    def get_top(self):
        return self.gap_center - self.gap_size // 2
        
    def get_bot(self):
        return self.gap_center + self.gap_size // 2
        
    def draw(self, screen):
        top_height = self.gap_center - self.gap_size // 2
        pygame.draw.rect(screen, (0, 255, 0), (self.x, 0, self.width, top_height))
        
        bottom_start = self.gap_center + self.gap_size // 2
        bottom_height = HEIGHT - bottom_start
        pygame.draw.rect(screen, (0, 255, 0), (self.x, bottom_start, self.width, bottom_height))
    
    def is_off_screen(self):
        return self.x + self.width < 0

class Bird:
    def __init__(self):
        self.x = 100 + random.randint(-5, 5)
        self.y = HEIGHT / 2 + random.randint(-10, 10)
        self.velocity = 0
        self.size = 20
        self.is_alive = True
        self.fitness = 0 
        self.time_alive = 0 
        self.pipes_passed = 0

    def jump(self):
        self.velocity = -8

    def update(self):
        self.velocity += 0.6
        self.y += self.velocity
        if self.is_alive:
            self.time_alive += 1
    
    def draw(self, screen):
        if self.pipes_passed == 0:
            color = (255, 0, 0)
        elif self.pipes_passed < 3:
            color = (255, 165, 0)
        else:
            color = (0, 255, 0)
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))

class FlappyBirdAI(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(4, 12),
            nn.ReLU(),
            nn.Linear(12, 1),
            nn.Sigmoid()  
        )

    def forward(self, x):
        return self.layers(x)
    
    def decide_action(self, inputs):
        x = torch.tensor(inputs, dtype=torch.float32)
        output = self.forward(x)
        return output.item() > 0.5

def copy_and_mutate(parent_ai, mutation_rate=0.5, mutation_strength=0.7):
    child_ai = FlappyBirdAI()
    child_ai.load_state_dict(parent_ai.state_dict())
    
    with torch.no_grad():
        for param in child_ai.parameters():
            mutation_mask = torch.rand_like(param) < mutation_rate
            mutations = torch.randn_like(param) * mutation_strength
            param[mutation_mask] += mutations[mutation_mask]
    
    return child_ai

def check_collision_with_pipes(bird, pipes):
    for pipe in pipes:
        if (bird.x < pipe.x + pipe.width and bird.x + bird.size > pipe.x):
            if (bird.y < pipe.get_top() or bird.y + bird.size > pipe.get_bot()):
                return True
    return False

def check_collision_with_bounds(bird):
    return bird.y < 0 or bird.y + bird.size > HEIGHT

def get_next_pipe(bird, pipes):
    for pipe in pipes:
        if pipe.x + pipe.width > bird.x:
            return pipe
    return None

def get_ai_inputs(bird, pipes):
    next_pipe = get_next_pipe(bird, pipes)
    if next_pipe is None:
        return [0.5, 0, 1, 0.5]
    
    bird_y = bird.y / HEIGHT
    bird_velocity = (bird.velocity + 15) / 30
    pipe_distance = (next_pipe.x - bird.x) / WIDTH
    gap_center = next_pipe.gap_center / HEIGHT
    
    return [bird_y, bird_velocity, pipe_distance, gap_center]

def calculate_fitness(bird, pipes):
    fitness = 0
    
    fitness += bird.time_alive * 1.0
    
    if bird.pipes_passed > 0:
        if bird.pipes_passed == 1:
            fitness += 2500
        elif bird.pipes_passed == 2:
            fitness += 5000
        elif bird.pipes_passed == 3:
            fitness += 6000
        elif bird.pipes_passed >= 4:
            base = 13500
            extra_pipes = bird.pipes_passed - 3
            fitness += base + (extra_pipes * 4000 * (1.2 ** extra_pipes))
    
    next_pipe = get_next_pipe(bird, pipes)
    if next_pipe:
        horizontal_distance = next_pipe.x - bird.x
        bird_center_y = bird.y + bird.size/2
        gap_center = next_pipe.gap_center
        gap_diff = abs(bird_center_y - gap_center)
        
        if horizontal_distance > 0 and horizontal_distance < 200:
            approach_progress = (200 - horizontal_distance) * 1.5
            fitness += approach_progress
        
        if gap_diff < 150:
            vertical_bonus = (150 - gap_diff) * 1.5
            fitness += vertical_bonus
        
        if horizontal_distance < 80:
            fitness += 300
        
        if (bird.x < next_pipe.x + next_pipe.width and bird.x + bird.size > next_pipe.x):
            fitness += 800
            
            if (bird.y > next_pipe.get_top() and bird.y + bird.size < next_pipe.get_bot()):
                fitness += 1200
    
    return max(100, fitness)

def reset_game():
    list_pipe = []
    list_pipe.append(Pipe(WIDTH + 200))
    return list_pipe

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Evolution IA")

running = True
clock = pygame.time.Clock()
last_pipe_time = pygame.time.get_ticks()
generation = 1
best_all_time = 0

birds = []
ais = []

for i in range(50):
    birds.append(Bird())
    ais.append(FlappyBirdAI())

list_pipe = reset_game()

while running:
    current_time = pygame.time.get_ticks()
    
    if not list_pipe or (list_pipe and list_pipe[-1].x < WIDTH - 300):
        if current_time - last_pipe_time > 1500:
            list_pipe.append(Pipe())
            last_pipe_time = current_time 
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    for i in range(len(birds)):
        if birds[i].is_alive:
            ai_inputs = get_ai_inputs(birds[i], list_pipe)
            if ais[i].decide_action(ai_inputs):
                birds[i].jump()
                
    for pipe in list_pipe:
        pipe.update()
        
    for i in range(len(birds)):
        if birds[i].is_alive:
            birds[i].update()
            birds[i].fitness = calculate_fitness(birds[i], list_pipe)
            
            if check_collision_with_pipes(birds[i], list_pipe) or check_collision_with_bounds(birds[i]):
                birds[i].is_alive = False
    
    alive_count = sum(1 for bird in birds if bird.is_alive)

    if alive_count == 0:
        birds_with_fitness = [(birds[i].fitness, i) for i in range(len(birds))]
        birds_with_fitness.sort(reverse=True)
        
        best_fitness = birds_with_fitness[0][0]
        avg_fitness = sum(f for f, _ in birds_with_fitness) / len(birds_with_fitness)
        best_pipes = birds[birds_with_fitness[0][1]].pipes_passed
        
        if best_pipes > best_all_time:
            best_all_time = best_pipes
        
        best_bird = birds[birds_with_fitness[0][1]]
        
        if generation > 50:
            if best_pipes <= 3:
                conservation_ratio = 0.2
                exploration_mode = True
            else:
                conservation_ratio = 0.3
                exploration_mode = False
        else:
            conservation_ratio = 0.35 if best_pipes > 0 else 0.25
            exploration_mode = False
        
        if exploration_mode:
            best_indices = [idx for _, idx in birds_with_fitness[:25]]
        else:
            if best_pipes > 0:
                successful_birds = [(fitness, idx) for fitness, idx in birds_with_fitness if birds[idx].pipes_passed > 0]
                if len(successful_birds) >= 3:
                    best_indices = [idx for _, idx in successful_birds[:10]]
                else:
                    best_indices = [idx for _, idx in birds_with_fitness[:15]]
            else:
                best_indices = [idx for _, idx in birds_with_fitness[:12]]
        
        new_birds = []
        new_ais = []
        conservation_count = int(50 * conservation_ratio)
        
        for i in range(50):
            new_birds.append(Bird())
            
            if i < conservation_count:
                parent_idx = best_indices[i % len(best_indices)]
                new_ai = FlappyBirdAI()
                new_ai.load_state_dict(ais[parent_idx].state_dict())
                
            elif exploration_mode and i < conservation_count + 20:
                parent_idx = random.choice(best_indices[:min(15, len(best_indices))])
                new_ai = copy_and_mutate(ais[parent_idx], mutation_rate=0.4, mutation_strength=0.4)
                
            elif not exploration_mode and i < conservation_count + 20:
                parent_idx = random.choice(best_indices[:min(8, len(best_indices))])
                new_ai = copy_and_mutate(ais[parent_idx], mutation_rate=0.15, mutation_strength=0.15)
                
            else:
                new_ai = FlappyBirdAI()
                
            new_ais.append(new_ai)
        
        birds = new_birds
        ais = new_ais
        generation += 1
        
        list_pipe = reset_game()
        last_pipe_time = pygame.time.get_ticks()
        
    screen.fill((135, 206, 235))
    
    for pipe in list_pipe:
        for i, bird in enumerate(birds):
            if (pipe.x + pipe.width < bird.x and 
                bird.is_alive and 
                i not in pipe.passed_by):
                pipe.passed_by.append(i)
                bird.pipes_passed += 1
                
    list_pipe = [pipe for pipe in list_pipe if not pipe.is_off_screen()]
    
    for bird in birds:
        if bird.is_alive:
            bird.draw(screen)
            
    for pipe in list_pipe:
        pipe.draw(screen)
    
    font = pygame.font.Font(None, 24)
    gen_text = font.render(f"Génération: {generation}", True, (255, 255, 255))
    alive_text = font.render(f"Vivants: {alive_count}", True, (255, 255, 255))
    pipe_count_text = font.render(f"Pipes actifs: {len(list_pipe)}", True, (255, 255, 255))
    record_text = font.render(f"Record: {best_all_time} tuyaux", True, (255, 255, 0))
    
    if birds:
        best_current = max(birds, key=lambda b: b.pipes_passed)
        best_text = font.render(f"Meilleur actuel: {best_current.pipes_passed} tuyaux", True, (255, 255, 255))
        screen.blit(best_text, (10, 70))
    
    screen.blit(gen_text, (10, 10))
    screen.blit(alive_text, (10, 40))
    screen.blit(pipe_count_text, (10, 100))
    screen.blit(record_text, (10, 130))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()