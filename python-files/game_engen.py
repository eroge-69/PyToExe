import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class GameEngine:
    def __init__(self):
        self.engine_path = os.path.dirname(os.path.abspath(__file__))
        self.templates_path = os.path.join(self.engine_path, "Templates")
        self.ensure_templates_exist()
    
    def ensure_templates_exist(self):
        """Создает папку шаблонов и default шаблоны"""
        if not os.path.exists(self.templates_path):
            os.makedirs(self.templates_path)
            self.create_default_templates()
    
    def create_default_templates(self):
        """Создает стандартные шаблоны проектов"""
        templates = {
            "empty": self.get_empty_template(),
            "platform": self.get_platform_template(),
            "shooter": self.get_shooter_template()
        }
        
        for template_name, template_content in templates.items():
            template_dir = os.path.join(self.templates_path, template_name)
            os.makedirs(template_dir, exist_ok=True)
            
            with open(os.path.join(template_dir, "main.lua"), "w", encoding="utf-8") as f:
                f.write(template_content)
    
    def get_empty_template(self):
        """Шаблон пустого проекта"""
        return """-- {project_name}
-- Автоматически создан GameEngine

function love.load()
    -- Инициализация игры
    love.window.setTitle('{project_name}')
    
    -- Загрузка ресурсов
    player = {{
        x = 400,
        y = 300,
        speed = 200,
        size = 30
    }}
    
    -- Настройка шрифта
    font = love.graphics.newFont(24)
end

function love.update(dt)
    -- Обновление логики игры
    updatePlayer(dt)
end

function love.draw()
    -- Отрисовка игры
    love.graphics.setBackgroundColor(0.1, 0.1, 0.3)
    
    -- Рисуем игрока
    love.graphics.setColor(1, 0.2, 0.2)
    love.graphics.circle('fill', player.x, player.y, player.size)
    
    -- Интерфейс
    love.graphics.setColor(1, 1, 1)
    love.graphics.setFont(font)
    love.graphics.print('Добро пожаловать в {project_name}!', 10, 10)
    love.graphics.print('FPS: ' .. love.timer.getFPS(), 10, 40)
end

function updatePlayer(dt)
    -- Движение игрока
    if love.keyboard.isDown('w', 'up') then
        player.y = player.y - player.speed * dt
    end
    if love.keyboard.isDown('s', 'down') then
        player.y = player.y + player.speed * dt
    end
    if love.keyboard.isDown('a', 'left') then
        player.x = player.x - player.speed * dt
    end
    if love.keyboard.isDown('d', 'right') then
        player.x = player.x + player.speed * dt
    end
end

function love.keypressed(key)
    if key == 'escape' then
        love.event.quit()
    end
end
"""
    
    def get_platform_template(self):
        """Шаблон платформера"""
        return """-- Платформер шаблон
function love.load()
    love.window.setTitle('Платформер')
    
    -- Игрок
    player = {
        x = 100,
        y = 300,
        width = 30,
        height = 50,
        speed = 200,
        jumpForce = -400,
        velocityY = 0,
        isGrounded = false
    }
    
    -- Платформы
    platforms = {
        {x = 0, y = 400, width = 800, height = 20},
        {x = 200, y = 300, width = 100, height = 20},
        {x = 400, y = 250, width = 100, height = 20}
    }
    
    gravity = 800
    font = love.graphics.newFont(18)
end

function love.update(dt)
    updatePlayer(dt)
    applyGravity(dt)
    checkCollisions()
end

function love.draw()
    love.graphics.setBackgroundColor(0.2, 0.3, 0.5)
    
    -- Рисуем платформы
    love.graphics.setColor(0.3, 0.7, 0.3)
    for _, platform in ipairs(platforms) do
        love.graphics.rectangle("fill", platform.x, platform.y, platform.width, platform.height)
    end
    
    -- Рисуем игрока
    love.graphics.setColor(1, 0.2, 0.2)
    love.graphics.rectangle("fill", player.x, player.y, player.width, player.height)
    
    -- Интерфейс
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("Платформер - Пробел для прыжка", 10, 10)
end

function updatePlayer(dt)
    -- Горизонтальное движение
    if love.keyboard.isDown("a", "left") then
        player.x = player.x - player.speed * dt
    end
    if love.keyboard.isDown("d", "right") then
        player.x = player.x + player.speed * dt
    end
    
    -- Прыжок
    if love.keyboard.isDown("space") and player.isGrounded then
        player.velocityY = player.jumpForce
        player.isGrounded = false
    end
end

function applyGravity(dt)
    player.velocityY = player.velocityY + gravity * dt
    player.y = player.y + player.velocityY * dt
end

function checkCollisions()
    player.isGrounded = false
    
    for _, platform in ipairs(platforms) do
        if player.x + player.width > platform.x and
           player.x < platform.x + platform.width and
           player.y + player.height > platform.y and
           player.y + player.height < platform.y + platform.height and
           player.velocityY > 0 then
           
            player.y = platform.y - player.height
            player.velocityY = 0
            player.isGrounded = true
        end
    end
end

function love.keypressed(key)
    if key == "escape" then
        love.event.quit()
    end
end
"""
    
    def get_shooter_template(self):
        """Шаблон шутера"""
        return """-- Шутер шаблон
function love.load()
    love.window.setTitle('Космический шутер')
    
    player = {
        x = 400,
        y = 500,
        width = 40,
        height = 60,
        speed = 300,
        bullets = {}
    }
    
    enemies = {}
    score = 0
    font = love.graphics.newFont(24)
    
    -- Создаем врагов
    for i = 1, 5 do
        table.insert(enemies, {
            x = math.random(50, 750),
            y = math.random(50, 200),
            width = 30,
            height = 30,
            speed = 100
        })
    end
end

function love.update(dt)
    updatePlayer(dt)
    updateBullets(dt)
    updateEnemies(dt)
    checkCollisions()
end

function love.draw()
    love.graphics.setBackgroundColor(0.1, 0.1, 0.2)
    
    -- Рисуем игрока
    love.graphics.setColor(0.2, 0.8, 1)
    love.graphics.rectangle("fill", player.x - player.width/2, player.y - player.height/2, player.width, player.height)
    
    -- Рисуем пули
    love.graphics.setColor(1, 1, 0)
    for _, bullet in ipairs(player.bullets) do
        love.graphics.rectangle("fill", bullet.x - 2, bullet.y - 10, 4, 20)
    end
    
    -- Рисуем врагов
    love.graphics.setColor(1, 0.3, 0.3)
    for _, enemy in ipairs(enemies) do
        love.graphics.rectangle("fill", enemy.x - enemy.width/2, enemy.y - enemy.height/2, enemy.width, enemy.height)
    end
    
    -- Интерфейс
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("Счет: " .. score, 10, 10)
    love.graphics.print("Управление: WASD, Пробел - стрельба", 10, 40)
end

function updatePlayer(dt)
    if love.keyboard.isDown("a", "left") and player.x > player.width/2 then
        player.x = player.x - player.speed * dt
    end
    if love.keyboard.isDown("d", "right") and player.x < 800 - player.width/2 then
        player.x = player.x + player.speed * dt
    end
    if love.keyboard.isDown("w", "up") and player.y > player.height/2 then
        player.y = player.y - player.speed * dt
    end
    if love.keyboard.isDown("s", "down") and player.y < 600 - player.height/2 then
        player.y = player.y + player.speed * dt
    end
end

function love.keypressed(key)
    if key == "space" then
        table.insert(player.bullets, {
            x = player.x,
            y = player.y - player.height/2,
            speed = 500
        })
    end
    
    if key == "escape" then
        love.event.quit()
    end
end

function updateBullets(dt)
    for i = #player.bullets, 1, -1 do
        local bullet = player.bullets[i]
        bullet.y = bullet.y - bullet.speed * dt
        
        if bullet.y < -20 then
            table.remove(player.bullets, i)
        end
    end
end

function updateEnemies(dt)
    for _, enemy in ipairs(enemies) do
        enemy.x = enemy.x + math.sin(love.timer.getTime()) * enemy.speed * dt
    end
end

function checkCollisions()
    for i = #player.bullets, 1, -1 do
        local bullet = player.bullets[i]
        
        for j = #enemies, 1, -1 do
            local enemy = enemies[j]
            
            if bullet.x > enemy.x - enemy.width/2 and
               bullet.x < enemy.x + enemy.width/2 and
               bullet.y > enemy.y - enemy.height/2 and
               bullet.y < enemy.y + enemy.height/2 then
               
                table.remove(player.bullets, i)
                table.remove(enemies, j)
                score = score + 100
                break
            end
        end
    end
end
"""
    
    def create_project(self, project_name, template="empty"):
        """Создает новый проект"""
        try:
            project_path = os.path.join(os.getcwd(), project_name)
            
            if os.path.exists(project_path):
                if not messagebox.askyesno("Подтверждение", f"Папка '{project_path}' уже существует. Перезаписать?"):
                    return False
                shutil.rmtree(project_path)
            
            self.create_project_structure(project_path)
            self.copy_template_files(template, project_path)
            self.generate_main_lua(project_path, project_name, template)
            self.generate_config_files(project_path, project_name)
            
            print(f"✅ Проект '{project_name}' создан успешно!")
            print(f"📁 Папка: {project_path}")
            
            # Автоматически открываем папку
            self.open_folder(project_path)
            return True
            
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            print(error_msg)
            messagebox.showerror("Ошибка", f"Ошибка создания проекта: {str(e)}")
            return False
    
    def create_project_structure(self, project_path):
        """Создает структуру папок проекта"""
        folders = [
            "src",
            "assets",
            "assets/images", 
            "assets/sounds",
            "assets/music"
        ]
        
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
    
    def copy_template_files(self, template, project_path):
        """Копирует файлы шаблона"""
        template_path = os.path.join(self.templates_path, template)
        if os.path.exists(template_path):
            dest_path = os.path.join(project_path, "src")
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(template_path, dest_path)
    
    def generate_main_lua(self, project_path, project_name, template):
        """Генерирует основной файл игры"""
        template_main = os.path.join(project_path, "src", "main.lua")
        if os.path.exists(template_main) and template != "empty":
            return
            
        main_content = self.get_empty_template().format(project_name=project_name)
        with open(template_main, "w", encoding="utf-8") as f:
            f.write(main_content)
    
    def generate_config_files(self, project_path, project_name):
        """Генерирует конфигурационные файлы"""
        # conf.lua
        conf_content = f"""function love.conf(t)
    t.window.title = '{project_name}'
    t.window.width = 800
    t.window.height = 600
    t.window.resizable = false
    t.console = true
end"""
        
        with open(os.path.join(project_path, "conf.lua"), "w", encoding="utf-8") as f:
            f.write(conf_content)
        
        # README.md
        readme_content = f"""# {project_name}

Проект создан с помощью GameEngine.

## Запуск
- Убедитесь, что установлен Love2D
- Перетащите папку проекта на love.exe
- Или используйте команду: `love .`

## Структура
- `src/main.lua` - основной код игры
- `assets/` - ресурсы (изображения, звуки)
- `conf.lua` - настройки игры

## Управление
- WASD/Стрелки - движение
- ESC - выход
"""
        with open(os.path.join(project_path, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)
    
    def run_project(self, project_path):
        """Запускает проект в Love2D"""
        try:
            love_path = self.find_love2d()
            if not love_path:
                if messagebox.askyesno("Love2D не найден", 
                                      "Love2D не найден!\\n\\nУстановите его с https://love2d.org\\n\\nХотите открыть сайт для скачивания?"):
                    self.open_url("https://love2d.org")
                return False
            
            subprocess.Popen([love_path, project_path])
            print("🚀 Запускаем проект...")
            return True
            
        except Exception as e:
            error_msg = f"❌ Ошибка запуска: {str(e)}"
            print(error_msg)
            messagebox.showerror("Ошибка", f"Ошибка запуска: {str(e)}")
            return False
    
    def find_love2d(self):
        """Ищет установленный Love2D"""
        possible_paths = [
            r"C:\Program Files\LOVE\love.exe",
            r"C:\Program Files (x86)\LOVE\love.exe",
            "/usr/bin/love",
            "/usr/local/bin/love",
            "love.exe",
            "love"
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
            # Проверяем в PATH
            try:
                subprocess.run([path, "--version"], capture_output=True, check=True)
                return path
            except:
                continue
        
        return None
    
    def open_folder(self, path):
        """Открывает папку в проводнике"""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.Popen(["open", path])
            else:  # Linux
                subprocess.Popen(["xdg-open", path])
            return True
        except Exception as e:
            print(f"Не удалось открыть папку: {e}")
            return False
    
    def open_url(self, url):
        """Открывает URL в браузере"""
        try:
            import webbrowser
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"Не удалось открыть URL: {e}")
            return False
    
    def get_available_templates(self):
        """Возвращает список доступных шаблонов"""
        if os.path.exists(self.templates_path):
            return [d for d in os.listdir(self.templates_path) 
                   if os.path.isdir(os.path.join(self.templates_path, d))]
        return []


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.engine = GameEngine()
        self.setup_ui()
    
    def setup_ui(self):
        """Настраивает графический интерфейс"""
        self.title("🎮 GameEngine - Создатель игр на Lua")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Заголовок
        title_label = tk.Label(self, text="GameEngine - Создатель игр", 
                              font=("Arial", 16, "bold"), fg="darkblue")
        title_label.place(x=20, y=15)
        
        # Название проекта
        tk.Label(self, text="Название проекта:").place(x=20, y=60)
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.place(x=180, y=60)
        self.name_entry.insert(0, "MyGame")
        
        # Шаблон
        tk.Label(self, text="Шаблон:").place(x=20, y=90)
        self.template_combo = ttk.Combobox(self, width=27, state="readonly")
        self.template_combo.place(x=180, y=90)
        self.update_templates_list()
        
        # Папка назначения
        tk.Label(self, text="Папка:").place(x=20, y=120)
        self.folder_entry = tk.Entry(self, width=25)
        self.folder_entry.place(x=180, y=120)
        self.folder_entry.insert(0, os.getcwd())
        
        self.folder_button = tk.Button(self, text="...", width=3, command=self.select_folder)
        self.folder_button.place(x=385, y=118)
        
        # Кнопки
        self.create_button = tk.Button(self, text="🎮 Создать проект", width=20, height=2,
                                      bg="lightgreen", command=self.create_project)
        self.create_button.place(x=20, y=160)
        
        self.run_button = tk.Button(self, text="🚀 Запустить проект", width=20, height=2,
                                   bg="lightblue", command=self.run_project)
        self.run_button.place(x=240, y=160)
        
        self.open_folder_button = tk.Button(self, text="📁 Открыть папку проекта", 
                                           width=52, command=self.open_project_folder)
        self.open_folder_button.place(x=20, y=210)
        
        # Лог
        tk.Label(self, text="Лог выполнения:").place(x=20, y=260)
        self.log_text = tk.Text(self, width=67, height=10, font=("Consolas", 9))
        self.log_text.place(x=20, y=285)
        
        # Статус
        self.status_label = tk.Label(self, text="Готов к созданию проектов!", fg="green")
        self.status_label.place(x=20, y=470)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def update_templates_list(self):
        """Обновляет список шаблонов"""
        templates = self.engine.get_available_templates()
        self.template_combo["values"] = templates
        if templates:
            self.template_combo.current(0)
    
    def create_project(self):
        """Создает проект"""
        project_name = self.name_entry.get().strip()
        if not project_name:
            messagebox.showwarning("Ошибка", "Введите название проекта!")
            return
        
        template = self.template_combo.get()
        self.log(f"Создаем проект: {project_name}")
        self.log(f"Шаблон: {template}")
        self.log(f"Папка: {os.path.join(self.folder_entry.get(), project_name)}")
        
        success = self.engine.create_project(project_name, template)
        if success:
            self.log("✅ Проект создан успешно!")
            self.status_label.config(text="Проект создан успешно!", fg="green")
        else:
            self.status_label.config(text="Ошибка при создании проекта!", fg="red")
    
    def run_project(self):
        """Запускает проект"""
        project_path = os.path.join(self.folder_entry.get(), self.name_entry.get())
        
        if not os.path.exists(project_path):
            self.log("❌ Проект не найден! Сначала создайте проект.")
            return
        
        self.log("🚀 Запускаем проект...")
        success = self.engine.run_project(project_path)
        if success:
            self.log("✅ Проект запущен!")
        else:
            self.log("❌ Не удалось запустить проект")
    
    def open_project_folder(self):
        """Открывает папку проекта"""
        project_path = os.path.join(self.folder_entry.get(), self.name_entry.get())
        
        if not os.path.exists(project_path):
            self.log("❌ Проект не найден! Сначала создайте проект.")
            return
        
        self.engine.open_folder(project_path)
        self.log("📁 Открываем папку проекта...")
    
    def select_folder(self):
        """Выбирает папку для проекта"""
        folder = filedialog.askdirectory(initialdir=self.folder_entry.get())
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
    
    def log(self, message):
        """Добавляет сообщение в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        if messagebox.askokcancel("Выход", "Закрыть GameEngine?"):
            self.destroy()


def show_help():
    """Показывает справку по использованию"""
    help_text = """Использование:
  python game_engine.py new <ProjectName> [template]  - Создать новый проект
  python game_engine.py run [path]                    - Запустить проект
  python game_engine.py gui                           - Открыть визуальный редактор

Доступные шаблоны:
  empty     - Пустой проект
  platform  - Платформер
  shooter   - Космический шутер

Примеры:
  python game_engine.py new MyAwesomeGame
  python game_engine.py new SpaceShooter shooter
  python game_engine.py run MyAwesomeGame

Просто запустите python game_engine.py без параметров для открытия GUI"""
    print(help_text)


def main():
    """Основная функция"""
    if len(sys.argv) == 1:
        # Запуск GUI
        app = MainWindow()
        app.mainloop()
    else:
        # Обработка командной строки
        engine = GameEngine()
        
        command = sys.argv[1].lower()
        
        if command in ["new", "create"]:
            if len(sys.argv) < 3:
                print("❌ Укажите название проекта: python game_engine.py new MyGame")
                return
            
            project_name = sys.argv[2]
            template = sys.argv[3] if len(sys.argv) > 3 else "empty"
            engine.create_project(project_name, template)
            
        elif command == "run":
            project_path = sys.argv[2] if len(sys.argv) > 2 else "."
            engine.run_project(project_path)
            
        elif command == "gui":
            app = MainWindow()
            app.mainloop()
            
        else:
            show_help()


if __name__ == "__main__":
    main()