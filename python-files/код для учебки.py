import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle

# Конфигурация мира
WORLD_SIZE = 100
BORDER_MARGIN = 5
DRONE_COUNT = 15
OBSTACLE_COUNT = 5

class Obstacle:
    """Статическое препятствие"""
    def __init__(self, x, y, radius):
        self.position = np.array([x, y], dtype=float)
        self.radius = radius
        self.color = '#888888'

class MovingObstacle:
    """Динамическое препятствие с движением"""
    def __init__(self, x, y, radius):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.random.uniform(-1, 1, 2)
        self.radius = radius
        self.color = '#FFA500'
        
    def update(self):
        self.position += self.velocity
        
        # Отскок от границ
        for i in range(2):
            if self.position[i] <= self.radius or self.position[i] >= WORLD_SIZE - self.radius:
                self.velocity[i] *= -1
                self.position[i] = np.clip(self.position[i], 
                                         self.radius, 
                                         WORLD_SIZE - self.radius)

class Drone:
    def __init__(self, x, y, is_leader=False):
        self.position = np.array([x, y], dtype=float)
        self.velocity = np.random.uniform(-0.5, 0.5, 2)
        self.is_leader = is_leader
        
        # Параметры движения
        self.max_speed = 2.5 if is_leader else 2.0
        self.max_force = 0.2
        self.perception_radius = 20
        self.safety_radius = 3.0
        self.actual_radius = 1.5  # Физический размер
        
        # Визуализация
        self.size = 40 if is_leader else 20
        self.color = '#FF3333' if is_leader else '#3399FF'
        self.arrow_color = '#FF0000' if is_leader else '#0066CC'
        
    def update(self, leader, drones, obstacles):
        if self.is_leader:
            if hasattr(self, 'target_position'):
                desired = self.target_position - self.position
            else:
                desired = np.zeros(2)
        else:
            desired = self.flock_behavior(leader, drones, obstacles)
        
        if np.linalg.norm(desired) > 0:
            desired = desired / np.linalg.norm(desired) * self.max_speed
        
        steering = np.clip(desired - self.velocity, -self.max_force, self.max_force)
        self.velocity += steering
        
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = self.velocity / speed * self.max_speed
            
        self.position += self.velocity
        self.apply_border_constraints()
        self.prevent_collisions(drones, obstacles)
        
    def apply_border_constraints(self):
        margin = self.actual_radius + 1
        self.position = np.clip(self.position, 
                              [margin, margin], 
                              [WORLD_SIZE-margin, WORLD_SIZE-margin])
        
        for i in range(2):
            if self.position[i] <= margin * 2 or self.position[i] >= WORLD_SIZE - margin * 2:
                self.velocity[i] *= -0.5

    def flock_behavior(self, leader, drones, obstacles):
        follow = (leader.position - self.position) * 0.5
        
        align = np.zeros(2)
        cohesion = np.zeros(2)
        separate = np.zeros(2)
        neighbor_count = 0
        
        for drone in drones:
            if drone is not self:
                dist = np.linalg.norm(drone.position - self.position)
                if dist < self.perception_radius:
                    align += drone.velocity
                    cohesion += drone.position
                    if dist < self.safety_radius * 2:
                        separate += (self.position - drone.position) / (dist**2 + 0.01)
                    neighbor_count += 1
        
        if neighbor_count > 0:
            align = (align / neighbor_count) * 0.15
            cohesion = ((cohesion / neighbor_count) - self.position) * 0.15
            separate = (separate / neighbor_count) * 1.8
        
        avoid = np.zeros(2)
        for obs in obstacles:
            dist = np.linalg.norm(obs.position - self.position)
            if dist < (obs.radius + self.safety_radius * 1.5):
                dir_away = (self.position - obs.position) / (dist + 0.01)
                strength = min(2.0, 1.0 / (dist - obs.radius + 0.01))
                avoid += dir_away * strength * 4.0
        
        return follow + align + cohesion + separate + avoid
    
    def prevent_collisions(self, drones, obstacles):
        for drone in drones:
            if drone is not self:
                dist = np.linalg.norm(drone.position - self.position)
                min_dist = self.actual_radius + drone.actual_radius
                if dist < min_dist:
                    push_dir = (self.position - drone.position) / (dist + 0.01)
                    push_force = (min_dist - dist) * 0.8
                    self.position += push_dir * push_force
        
        for obs in obstacles:
            dist = np.linalg.norm(obs.position - self.position)
            if dist < (obs.radius + self.actual_radius):
                push_dir = (self.position - obs.position) / (dist + 0.01)
                push_force = (obs.radius + self.actual_radius - dist) * 0.9
                self.position += push_dir * push_force

# Инициализация
drones = []
leader = Drone(WORLD_SIZE/2, WORLD_SIZE/2, is_leader=True)
drones.append(leader)

# Создаем дроны по кругу
angles = np.linspace(0, 2*np.pi, DRONE_COUNT, endpoint=False)
for angle in angles:
    x = leader.position[0] + 15 * np.cos(angle)
    y = leader.position[1] + 15 * np.sin(angle)
    drones.append(Drone(x, y))

# Создаем препятствия (3 статических и 2 движущихся)
obstacles = [
    Obstacle(30, 30, 8),
    Obstacle(70, 70, 10),
    Obstacle(30, 70, 6),
    MovingObstacle(50, 20, 7),
    MovingObstacle(20, 50, 5)
]

# Настройка анимации
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_xlim(0, WORLD_SIZE)
ax.set_ylim(0, WORLD_SIZE)
ax.set_title("Роевое поведение дронов с динамическими препятствиями")

def on_mouse_move(event):
    if event.inaxes:
        leader.target_position = np.array([event.xdata, event.ydata])

fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

def animate(frame):
    ax.clear()
    ax.set_xlim(0, WORLD_SIZE)
    ax.set_ylim(0, WORLD_SIZE)
    
    # Обновляем движущиеся препятствия
    for obs in obstacles:
        if isinstance(obs, MovingObstacle):
            obs.update()
    
    # Обновляем дронов
    for drone in drones:
        drone.update(leader, drones, obstacles)
    
    # Рисуем препятствия
    for obs in obstacles:
        ax.add_patch(Circle(obs.position, obs.radius, color=obs.color, alpha=0.5))
    
    # Рисуем дронов
    for drone in drones:
        ax.add_patch(Circle(drone.position, drone.actual_radius, 
                          color=drone.color, alpha=0.3))
        ax.scatter(drone.position[0], drone.position[1], s=drone.size,
                  c=drone.color, edgecolors='black', linewidth=0.5, zorder=10)
        
        ax.arrow(drone.position[0], drone.position[1],
                drone.velocity[0] * 2,
                drone.velocity[1] * 2,
                head_width=1.5, head_length=2, 
                fc=drone.arrow_color, ec='black', zorder=5)
    
    # Статус
    ax.text(5, 95, f"Дронов: {len(drones)}", fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
    ax.text(5, 90, "Ведущий: красный", fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
    ax.text(5, 85, "Движущиеся препятствия: оранжевые", fontsize=10, bbox=dict(facecolor='white', alpha=0.7))

ani = animation.FuncAnimation(fig, animate, frames=200, interval=50)
plt.show()