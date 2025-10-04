import tkinter as tk
from tkinter import ttk, filedialog
import random
import json

# Расширенные свойства веществ
ATOM_TYPES = {
    'Кислород': {'color': 'blue', 'mass': 16, 'size': 4},
    'Водород': {'color': 'cyan', 'mass': 1, 'size': 2},
    'Углерод': {'color': 'black', 'mass': 12, 'size': 3},
    'Азот': {'color': 'purple', 'mass': 14, 'size': 4},
    'Железо': {'color': 'red', 'mass': 55, 'size': 5},
    'Золото': {'color': 'gold', 'mass': 197, 'size': 4},
    'Водная пара': {'color': 'lightblue', 'mass': 18, 'size': 4},
    'Диоксид углерода': {'color': 'gray', 'mass': 44, 'size': 4},
    'Графит': {'color': 'darkgray', 'mass': 12, 'size': 3},
    'Аммиак': {'color': 'pink', 'mass': 17, 'size': 3},
    'Метан': {'color': 'darkgreen', 'mass': 16, 'size': 3},
    'Ржавчина': {'color': 'brown', 'mass': 80, 'size': 4},
}

# Реакции между веществами
REACTIONS = {
    frozenset(['Водород', 'Кислород']): {'product': 'Вода', 'energy': -10},
    frozenset(['Углерод', 'Кислород']): {'product': 'Диоксид углерода', 'energy': -8},
    frozenset(['Водород', 'Азот']): {'product': 'Аммиак', 'energy': -5},
    frozenset(['Мета', 'Водород']): {'product': 'Метан', 'energy': -12},
    frozenset(['Железо', 'Кислород']): {'product': 'Ржавчина', 'energy': -7}
}

class Particle:
    def __init__(self, canvas, x, y, substance, color, mass, size, dx=0, dy=0):
        self.canvas = canvas
        self.substance = substance
        self.color = color
        self.mass = mass
        self.size = size
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.id = self.canvas.create_oval(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=self.color
        )

    def move(self):
        self.x += self.dx
        self.y += self.dy
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Отскок от стен
        if self.x - self.size <= 0:
            self.x = self.size
            self.dx *= -1
        elif self.x + self.size >= width:
            self.x = width - self.size
            self.dx *= -1
        if self.y - self.size <= 0:
            self.y = self.size
            self.dy *= -1
        elif self.y + self.size >= height:
            self.y = height - self.size
            self.dy *= -1

        self.canvas.coords(
            self.id,
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size
        )

    def get_position(self):
        return self.x, self.y

    def delete(self):
        self.canvas.delete(self.id)

class MatterSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Расширенный симулятор материи с физикой столкновений")
        
        # Интерфейс
        control_frame = ttk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Агрегатное состояние
        ttk.Label(control_frame, text="Агрегатное состояние:").grid(row=0, column=0, sticky=tk.W)
        self.state_var = tk.StringVar(value='Газ')
        ttk.Radiobutton(control_frame, text='Твердое', variable=self.state_var, value='Твердое', command=self.update_parameters).grid(row=0, column=1)
        ttk.Radiobutton(control_frame, text='Жидкое', variable=self.state_var, value='Жидкое', command=self.update_parameters).grid(row=0, column=2)
        ttk.Radiobutton(control_frame, text='Газ', variable=self.state_var, value='Газ', command=self.update_parameters).grid(row=0, column=3)

        # Температура (отображение и управление)
        ttk.Label(control_frame, text="Температура (К):").grid(row=1, column=0, sticky=tk.W)
        self.temp_value_label = ttk.Label(control_frame, text="0 К")
        self.temp_value_label.grid(row=1, column=1)

        # Кнопки + и -
        temp_buttons_frame = ttk.Frame(control_frame)
        temp_buttons_frame.grid(row=1, column=2, columnspan=2, sticky=tk.W)
        self.temp_minus_button = ttk.Button(temp_buttons_frame, text="-", width=3, command=self.decrease_temperature)
        self.temp_minus_button.pack(side=tk.LEFT)
        self.temp_plus_button = ttk.Button(temp_buttons_frame, text="+", width=3, command=self.increase_temperature)
        self.temp_plus_button.pack(side=tk.LEFT)

        self.temp_scale = ttk.Scale(control_frame, from_=0, to=3000, orient=tk.HORIZONTAL, command=self.update_temperature_scale)
        self.temp_scale.set(300)
        self.temp_scale.grid(row=1, column=4, sticky=tk.EW)

        # Тип вещества
        ttk.Label(control_frame, text="Тип вещества:").grid(row=2, column=0, sticky=tk.W)
        self.atom_type_var = tk.StringVar(value='Кислород')
        self.atom_types_list = list(ATOM_TYPES.keys())
        for i, atom in enumerate(self.atom_types_list):
            ttk.Radiobutton(control_frame, text=atom, variable=self.atom_type_var, value=atom, command=self.update_current_substance).grid(row=2, column=1 + i)

        # Управление
        button_frame = ttk.Frame(root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.start_button = ttk.Button(button_frame, text="Запустить", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = ttk.Button(button_frame, text="Остановить", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(button_frame, text="Очистить", command=self.clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        self.spawn_button = ttk.Button(button_frame, text="Появить выбранное вещество", command=self.spawn_selected_substance)
        self.spawn_button.pack(side=tk.LEFT, padx=5)

        # Холст
        self.canvas = tk.Canvas(root, width=700, height=500, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.particles = []
        self.running = False
        self.temperature = self.temp_scale.get()
        self.state = self.state_var.get()

        # Текущий выбранный тип вещества
        self.current_substance = self.atom_type_var.get()

        self.canvas.bind("<Button-1>", self.add_particle)

        self.update_parameters()
        self.update_temperature_display()

    def update_temperature_display(self):
        self.temp_value_label.config(text=f"{int(self.temperature)} К")

    def update_temperature_scale(self, event=None):
        self.temperature = self.temp_scale.get()
        self.update_temperature_display()

    def increase_temperature(self):
        new_temp = self.temp_scale.get() + 50
        if new_temp > 3000:
            new_temp = 3000
        self.temp_scale.set(new_temp)
        self.update_temperature_display()

    def decrease_temperature(self):
        new_temp = self.temp_scale.get() - 50
        if new_temp < 0:
            new_temp = 0
        self.temp_scale.set(new_temp)
        self.update_temperature_display()

    def update_parameters(self):
        self.state = self.state_var.get()

    def update_current_substance(self):
        self.current_substance = self.atom_type_var.get()

    def get_particle_properties(self):
        atom_info = ATOM_TYPES[self.current_substance]
        base_mass = atom_info['mass']
        base_size = atom_info['size']
        color = atom_info['color']
        speed_factor = self.temperature / 300 if self.temperature > 0 else 0
        if self.state == 'Твердое':
            dx = dy = 0
        elif self.state == 'Жидкое':
            dx = random.uniform(-1, 1) * speed_factor
            dy = random.uniform(-1, 1) * speed_factor
        else:  # Газ
            dx = random.uniform(-2, 2) * speed_factor
            dy = random.uniform(-2, 2) * speed_factor
        return color, base_mass, base_size, dx, dy

    def add_particle(self, event):
        color, mass, size, dx, dy = self.get_particle_properties()
        particle = Particle(self.canvas, event.x, event.y, self.current_substance, color, mass, size, dx, dy)
        self.particles.append(particle)

    def spawn_selected_substance(self):
        color, mass, size, dx, dy = self.get_particle_properties()
        x = self.canvas.winfo_width() // 2
        y = self.canvas.winfo_height() // 2
        particle = Particle(self.canvas, x, y, self.current_substance, color, mass, size, dx, dy)
        self.particles.append(particle)

    def handle_collisions(self):
        # Обработка столкновений и реакций
        to_remove = set()
        for i in range(len(self.particles)):
            p1 = self.particles[i]
            for j in range(i + 1, len(self.particles)):
                p2 = self.particles[j]
                if p1 in to_remove or p2 in to_remove:
                    continue
                if self.are_colliding(p1, p2):
                    self.resolve_collision(p1, p2)
                    self.try_reaction(p1, p2, to_remove)
        # Удаляем частицы после реакции
        for p in to_remove:
            if p in self.particles:
                p.delete()
                self.particles.remove(p)

    def are_colliding(self, p1, p2):
        x1, y1 = p1.get_position()
        x2, y2 = p2.get_position()
        dist = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
        return dist <= p1.size + p2.size

    def resolve_collision(self, p1, p2):
        # Закон сохранения импульса (упрощенно)
        x1, y1 = p1.get_position()
        x2, y2 = p2.get_position()

        nx = x2 - x1
        ny = y2 - y1
        dist = max(((nx)**2 + (ny)**2)**0.5, 0.01)

        # Нормализуем
        nx /= dist
        ny /= dist

        # Проекции скоростей на нормаль
        v1 = p1.dx * nx + p1.dy * ny
        v2 = p2.dx * nx + p2.dy * ny

        total_mass = p1.mass + p2.mass
        # Новые скорости по закону сохранения импульса
        v1_new = (v1 * (p1.mass - p2.mass) + 2 * p2.mass * v2) / total_mass
        v2_new = (v2 * (p2.mass - p1.mass) + 2 * p1.mass * v1) / total_mass

        # Обновляем компоненты скоростей
        p1.dx += (v1_new - v1) * nx
        p1.dy += (v1_new - v1) * ny
        p2.dx += (v2_new - v2) * nx
        p2.dy += (v2_new - v2) * ny

        # Немного смещаем частицы, чтобы избежать повторных столкновений
        overlap = p1.size + p2.size - dist
        p1.x -= nx * overlap / 2
        p1.y -= ny * overlap / 2
        p2.x += nx * overlap / 2
        p2.y += ny * overlap / 2

        p1.move()
        p2.move()

    def try_reaction(self, p1, p2, to_remove):
        substances = frozenset([p1.substance, p2.substance])
        reaction_info = REACTIONS.get(substances)
        if reaction_info:
            # Удаляем исходные
            to_remove.add(p1)
            to_remove.add(p2)
            # Обновляем температуру
            self.temperature += reaction_info['energy']
            self.temperature = max(0, min(3000, self.temperature))
            self.temp_scale.set(self.temperature)
            self.update_temperature_display()
            # Создаем продукт реакции
            color, mass, size, dx, dy = self.get_particle_properties_for_substance(reaction_info['product'])
            new_particle = Particle(
                self.canvas,
                (p1.x + p2.x) / 2,
                (p1.y + p2.y) / 2,
                reaction_info['product'],
                color,
                mass,
                size,
                dx,
                dy
            )
            self.particles.append(new_particle)

    def get_particle_properties_for_substance(self, substance):
        info = ATOM_TYPES.get(substance, {'color': 'gray', 'mass': 10, 'size': 3})
        color = info['color']
        mass = info['mass']
        size = info['size']
        speed_factor = self.temperature / 300 if self.temperature > 0 else 0
        dx = random.uniform(-2, 2) * speed_factor
        dy = random.uniform(-2, 2) * speed_factor
        return color, mass, size, dx, dy

    def start(self):
        if not self.running:
            self.running = True
            self.animate()

    def stop(self):
        self.running = False

    def clear_canvas(self):
        self.canvas.delete('all')
        self.particles.clear()

    def save_scene(self):
        scene = []
        for p in self.particles:
            scene.append({
                'substance': p.substance,
                'x': p.x,
                'y': p.y,
                'dx': p.dx,
                'dy': p.dy,
                'color': p.color,
                'mass': p.mass,
                'size': p.size
            })
        filename = filedialog.asksaveasfilename(defaultextension=".json")
        if filename:
            with open(filename, 'w') as f:
                json.dump(scene, f)

    def load_scene(self):
        filename = filedialog.askopenfilename()
        if filename:
            with open(filename, 'r') as f:
                scene = json.load(f)
            self.clear_canvas()
            for obj in scene:
                p = Particle(
                    self.canvas,
                    obj['x'], obj['y'],
                    obj['substance'],
                    obj['color'],
                    obj['mass'],
                    obj['size'],
                    obj['dx'],
                    obj['dy']
                )
                self.particles.append(p)

    def animate(self):
        if self.running:
            for particle in self.particles:
                particle.move()
            self.handle_collisions()
            self.root.after(20, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = MatterSimulation(root)
    root.mainloop()
