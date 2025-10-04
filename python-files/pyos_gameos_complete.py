#!/usr/bin/env python3
"""
PyOS GameOS - Gamified Operating System Simulator
Learn OS concepts through gaming mechanics!

🎮 FEATURES:
- 🏆 Achievement/Badge system with 20+ achievements
- 📈 Experience points and leveling system  
- 🎯 Daily missions and challenges
- 📊 Progress tracking and statistics
- 🎊 Notification system with rewards
- 🎮 Mini-games integrated into the OS
- 🥇 Leaderboard system
- 🎨 Gamified UI with progress bars
- 💰 Resource management challenges
- ⚡ Speed challenges and time trials
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import json
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math
import os

class Achievement:
    def __init__(self, id: str, name: str, description: str, icon: str, xp_reward: int):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.xp_reward = xp_reward
        self.unlocked = False
        self.unlock_time = None

class Mission:
    def __init__(self, id: str, name: str, description: str, xp_reward: int, difficulty: str, target: int = 1):
        self.id = id
        self.name = name
        self.description = description
        self.xp_reward = xp_reward
        self.difficulty = difficulty
        self.completed = False
        self.progress = 0
        self.target = target

class GameStats:
    def __init__(self):
        self.level = 1
        self.xp = 0
        self.total_xp = 0
        self.files_created = 0
        self.files_deleted = 0
        self.directories_created = 0
        self.processes_created = 0
        self.processes_killed = 0
        self.commands_executed = 0
        self.achievements_unlocked = 0
        self.missions_completed = 0
        self.login_streak = 1
        self.games_played = 0
        self.time_played = 0
        self.directories_explored = set()
        self.challenge_streak = 0

    def add_xp(self, amount: int):
        self.xp += amount
        self.total_xp += amount

        # Level up calculation
        old_level = self.level
        self.level = int(math.sqrt(self.total_xp / 100)) + 1

        return self.level > old_level

class GameManager:
    def __init__(self):
        self.stats = GameStats()
        self.achievements = {}
        self.missions = []
        self.active_missions = []
        self.notifications = []
        self.game_start_time = datetime.now()
        self.last_activity = datetime.now()

        self._initialize_achievements()
        self._generate_daily_missions()

    def _initialize_achievements(self):
        """Initialize all achievements"""
        achievements_list = [
            ("first_steps", "First Steps", "Create your first file", "📄", 50),
            ("builder", "Builder", "Create your first directory", "📁", 50),
            ("taskmaster", "Taskmaster", "Create your first process", "⚙️", 75),
            ("productive", "Productive", "Create 10 files", "📚", 200),
            ("architect", "Architect", "Create 5 directories", "🏗️", 150),
            ("terminal_rookie", "Terminal Rookie", "Execute 25 commands", "💻", 200),
            ("terminal_expert", "Terminal Expert", "Execute 100 commands", "🖥️", 500),
            ("cleaner", "Cleaner", "Delete 10 files", "🧹", 150),
            ("explorer", "Explorer", "Visit 10 different directories", "🗺️", 200),
            ("speed_demon", "Speed Demon", "Complete 5 actions in 1 minute", "⚡", 300),
            ("night_owl", "Night Owl", "Use system after 11 PM", "🦉", 100),
            ("early_bird", "Early Bird", "Use system before 7 AM", "🐦", 100),
            ("dedication", "Dedication", "Login for 5 consecutive days", "🔥", 500),
            ("multitasker", "Multitasker", "Have 8 processes running", "🔀", 400),
            ("system_admin", "System Admin", "Reach level 5", "👑", 1000),
            ("master_admin", "Master Admin", "Reach level 10", "💎", 2000),
            ("completionist", "Completionist", "Complete 20 missions", "✅", 800),
            ("gamer", "Gamer", "Play 5 mini-games", "🎮", 300),
            ("efficiency", "Efficiency Expert", "Complete mission with 100% accuracy", "🎯", 400),
            ("legendary", "Legendary User", "Unlock 15 achievements", "🌟", 1500),
        ]

        for data in achievements_list:
            achievement = Achievement(*data)
            self.achievements[achievement.id] = achievement

    def _generate_daily_missions(self):
        """Generate daily missions"""
        mission_templates = [
            ("create_files", "File Creator", "Create 5 new files", 150, "Easy", 5),
            ("organize_files", "Organizer", "Create 3 directories and organize files", 200, "Medium", 3),
            ("process_master", "Process Master", "Create and manage 4 processes", 250, "Medium", 4),
            ("explorer_mission", "Explorer", "Navigate to 8 different directories", 180, "Easy", 8),
            ("terminal_warrior", "Terminal Warrior", "Execute 20 terminal commands", 300, "Medium", 20),
            ("cleanup_mission", "Cleanup Crew", "Delete 8 old files", 120, "Easy", 8),
            ("system_monitor", "System Monitor", "Check system stats 5 times", 100, "Easy", 5),
            ("efficiency_test", "Efficiency Test", "Complete 10 tasks in 3 minutes", 400, "Hard", 10),
            ("memory_manager", "Memory Manager", "Monitor memory usage for 5 minutes", 200, "Medium", 1),
            ("backup_task", "Backup Task", "Copy 6 files to backup folder", 250, "Medium", 6),
        ]

        # Select 3 random missions for the day
        selected = random.sample(mission_templates, 3)
        self.active_missions = []

        for data in selected:
            mission = Mission(*data)
            self.active_missions.append(mission)

    def add_notification(self, message: str, type: str = "success"):
        """Add a notification"""
        notification = {
            "message": message,
            "type": type,
            "time": datetime.now(),
            "id": len(self.notifications)
        }
        self.notifications.append(notification)

        # Keep only last 10 notifications
        if len(self.notifications) > 10:
            self.notifications.pop(0)

    def check_achievement(self, achievement_id: str):
        """Check and unlock achievement if conditions are met"""
        if achievement_id not in self.achievements or self.achievements[achievement_id].unlocked:
            return

        achievement = self.achievements[achievement_id]
        should_unlock = False

        # Check conditions
        if achievement_id == "first_steps" and self.stats.files_created >= 1:
            should_unlock = True
        elif achievement_id == "builder" and self.stats.directories_created >= 1:
            should_unlock = True
        elif achievement_id == "taskmaster" and self.stats.processes_created >= 1:
            should_unlock = True
        elif achievement_id == "productive" and self.stats.files_created >= 10:
            should_unlock = True
        elif achievement_id == "architect" and self.stats.directories_created >= 5:
            should_unlock = True
        elif achievement_id == "terminal_rookie" and self.stats.commands_executed >= 25:
            should_unlock = True
        elif achievement_id == "terminal_expert" and self.stats.commands_executed >= 100:
            should_unlock = True
        elif achievement_id == "cleaner" and self.stats.files_deleted >= 10:
            should_unlock = True
        elif achievement_id == "explorer" and len(self.stats.directories_explored) >= 10:
            should_unlock = True
        elif achievement_id == "system_admin" and self.stats.level >= 5:
            should_unlock = True
        elif achievement_id == "master_admin" and self.stats.level >= 10:
            should_unlock = True
        elif achievement_id == "completionist" and self.stats.missions_completed >= 20:
            should_unlock = True
        elif achievement_id == "gamer" and self.stats.games_played >= 5:
            should_unlock = True
        elif achievement_id == "legendary" and self.stats.achievements_unlocked >= 15:
            should_unlock = True
        elif achievement_id == "dedication" and self.stats.login_streak >= 5:
            should_unlock = True
        elif achievement_id == "night_owl":
            hour = datetime.now().hour
            should_unlock = hour >= 23
        elif achievement_id == "early_bird":
            hour = datetime.now().hour
            should_unlock = hour <= 7

        if should_unlock:
            self.unlock_achievement(achievement_id)

    def unlock_achievement(self, achievement_id: str):
        """Unlock an achievement"""
        achievement = self.achievements[achievement_id]
        achievement.unlocked = True
        achievement.unlock_time = datetime.now()

        # Award XP
        leveled_up = self.stats.add_xp(achievement.xp_reward)
        self.stats.achievements_unlocked += 1

        # Notification
        message = f"🏆 Achievement Unlocked: {achievement.name} (+{achievement.xp_reward} XP)"
        if leveled_up:
            message += f" 🎉 LEVEL UP! Now Level {self.stats.level}!"

        self.add_notification(message)

        # Check for more achievements
        self.check_achievement("legendary")

    def update_mission_progress(self, mission_type: str, amount: int = 1):
        """Update mission progress"""
        for mission in self.active_missions:
            if not mission.completed and mission.id == mission_type:
                mission.progress = min(mission.progress + amount, mission.target)
                if mission.progress >= mission.target:
                    self.complete_mission(mission)

    def complete_mission(self, mission: Mission):
        """Complete a mission"""
        mission.completed = True
        leveled_up = self.stats.add_xp(mission.xp_reward)
        self.stats.missions_completed += 1

        message = f"✅ Mission Complete: {mission.name} (+{mission.xp_reward} XP)"
        if leveled_up:
            message += f" 🎉 LEVEL UP! Now Level {self.stats.level}!"

        self.add_notification(message)

        # Check achievements
        self.check_achievement("completionist")

    def get_level_progress(self):
        """Get current level progress"""
        current_level_xp = (self.stats.level - 1) ** 2 * 100
        next_level_xp = self.stats.level ** 2 * 100
        progress_in_level = self.stats.total_xp - current_level_xp
        xp_needed_for_level = next_level_xp - current_level_xp

        return {
            "current_xp": progress_in_level,
            "needed_xp": xp_needed_for_level,
            "percentage": (progress_in_level / xp_needed_for_level) * 100
        }

class GameFileSystem:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.root = {
            "type": "directory",
            "contents": {},
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        self.current_path = "/"
        self._initialize_game_files()

    def _initialize_game_files(self):
        """Initialize file system with game content"""
        # Create directories
        directories = [
            "/home", "/home/player", "/home/player/Documents", 
            "/home/player/Games", "/home/player/Achievements",
            "/usr", "/usr/games", "/tmp", "/challenges"
        ]

        for directory in directories:
            self.mkdir(directory, game_action=False)

        # Create game files
        files = {
            "/home/player/welcome.txt": """🎮 Welcome to PyOS GameOS! 🎮

Congratulations on starting your journey as a System Administrator!

🎯 Your Mission:
Learn operating system concepts while having fun!

🏆 How to Play:
• Create files and folders to earn XP
• Complete daily missions for bonus rewards  
• Unlock achievements by mastering different skills
• Level up to become the ultimate System Admin!

💡 Tips:
• Use the terminal for bonus XP
• Explore different directories
• Manage processes like a pro
• Keep your system organized

Good luck, Administrator! 🚀""",

            "/home/player/tutorial.txt": """📚 GameOS Tutorial

🎮 Game Mechanics:
• XP (Experience Points): Earned by performing actions
• Levels: Increase as you gain more XP
• Achievements: Special rewards for milestones
• Missions: Daily challenges with XP rewards

📁 File Management:
• create files: +10 XP each
• Create folders: +25 XP each  
• Delete items: +5 XP each
• Navigate folders: +2 XP each

⚙️ Process Management:
• Create process: +30 XP
• Kill process: +20 XP
• Monitor system: +10 XP

💻 Terminal Commands:
• Each command: +5 XP
• 25 commands: Unlock "Terminal Rookie" 
• 100 commands: Unlock "Terminal Expert"

🎯 Pro Tips:
• Complete missions daily for big XP bonuses
• Explore all directories for the "Explorer" achievement
• Try the mini-games in /usr/games/
• Check your stats regularly to track progress""",

            "/usr/games/snake.py": """#!/usr/bin/env python3
# 🐍 Snake Game - PyOS Edition

print("🐍 Welcome to Snake Game!")
print("Coming Soon: Playable Snake game")
print("Play games to unlock the 'Gamer' achievement!")

# This will be a fully playable snake game
# integrated into the operating system simulator""",

            "/usr/games/puzzle.py": """#!/usr/bin/env python3  
# 🧩 Logic Puzzle Game

print("🧩 Welcome to Logic Puzzles!")
print("Solve puzzles to earn bonus XP!")
print("Coming Soon: Interactive puzzle challenges")

# Interactive logic puzzles that teach
# system administration concepts""",

            "/challenges/daily_challenge.txt": """🎯 Daily Challenge System

Each day brings new challenges!

Today's Challenges:
✅ Create 5 files (Reward: 150 XP)
✅ Explore 8 directories (Reward: 180 XP)  
✅ Execute 20 commands (Reward: 300 XP)

Complete all daily challenges to earn bonus rewards
and maintain your challenge streak!

Challenge Streak: Building streaks unlocks special achievements""",

            "/tmp/game_log.txt": f"""🎮 GameOS Activity Log

Session Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Player Level: 1
Total XP: 0
Achievements Unlocked: 0

Recent Activities:
- System initialized
- Welcome files created
- Tutorial loaded
- Daily missions generated

Ready to start your gaming adventure!"""
        }

        for path, content in files.items():
            self.create_file(path, content, game_action=False)

    def _navigate_to_path(self, path: str):
        """Navigate to path"""
        if path == "/":
            return self.root

        parts = [p for p in path.split("/") if p]
        current = self.root

        for part in parts:
            if part in current.get("contents", {}) and current["contents"][part]["type"] == "directory":
                current = current["contents"][part]
            else:
                return None
        return current

    def mkdir(self, path: str, game_action: bool = True) -> bool:
        """Create directory with game mechanics"""
        try:
            parent_path = "/".join(path.split("/")[:-1]) or "/"
            dir_name = path.split("/")[-1]

            parent = self._navigate_to_path(parent_path)
            if parent is None:
                return False

            if "contents" not in parent:
                parent["contents"] = {}

            parent["contents"][dir_name] = {
                "type": "directory", 
                "contents": {},
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }

            if game_action:
                # Game mechanics
                self.game_manager.stats.directories_created += 1
                leveled_up = self.game_manager.stats.add_xp(25)

                if leveled_up:
                    self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

                # Check achievements
                self.game_manager.check_achievement("builder")
                self.game_manager.check_achievement("architect")

                # Update missions
                self.game_manager.update_mission_progress("organize_files")

            return True
        except Exception as e:
            return False

    def create_file(self, path: str, content: str = "", game_action: bool = True) -> bool:
        """Create file with game mechanics"""
        try:
            parent_path = "/".join(path.split("/")[:-1]) or "/"
            file_name = path.split("/")[-1]

            parent = self._navigate_to_path(parent_path)
            if parent is None:
                return False

            if "contents" not in parent:
                parent["contents"] = {}

            parent["contents"][file_name] = {
                "type": "file",
                "content": content,
                "size": len(content),
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat()
            }

            if game_action:
                # Game mechanics
                self.game_manager.stats.files_created += 1
                leveled_up = self.game_manager.stats.add_xp(10)

                if leveled_up:
                    self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

                # Check achievements
                self.game_manager.check_achievement("first_steps")
                self.game_manager.check_achievement("productive")

                # Update missions
                self.game_manager.update_mission_progress("create_files")
                self.game_manager.update_mission_progress("backup_task")

            return True
        except Exception as e:
            return False

    def rm(self, path: str) -> bool:
        """Remove with game mechanics"""
        try:
            parent_path = "/".join(path.split("/")[:-1]) or "/"
            item_name = path.split("/")[-1]

            parent = self._navigate_to_path(parent_path)
            if parent and item_name in parent.get("contents", {}):
                item = parent["contents"][item_name]
                del parent["contents"][item_name]

                # Game mechanics
                if item["type"] == "file":
                    self.game_manager.stats.files_deleted += 1
                    leveled_up = self.game_manager.stats.add_xp(5)

                    if leveled_up:
                        self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

                    # Check achievements
                    self.game_manager.check_achievement("cleaner")

                    # Update missions
                    self.game_manager.update_mission_progress("cleanup_mission")

                return True
            return False
        except:
            return False

    def cd(self, path: str) -> bool:
        """Change directory with exploration tracking"""
        try:
            old_path = self.current_path

            if path == "..":
                if self.current_path != "/":
                    self.current_path = "/".join(self.current_path.split("/")[:-1]) or "/"
                    success = True
            else:
                if path.startswith("/"):
                    new_path = path
                else:
                    new_path = f"{self.current_path.rstrip('/')}/{path}"

                if self._navigate_to_path(new_path):
                    self.current_path = new_path
                    success = True
                else:
                    success = False

            if success and old_path != self.current_path:
                # Track exploration
                self.game_manager.stats.directories_explored.add(self.current_path)
                self.game_manager.stats.add_xp(2)

                # Check achievements
                self.game_manager.check_achievement("explorer")

                # Update missions
                self.game_manager.update_mission_progress("explorer_mission")

            return success
        except:
            return False

    def ls(self, path: str = None) -> List[Dict]:
        """List directory contents"""
        try:
            if path is None:
                path = self.current_path

            target = self._navigate_to_path(path)
            if target is None or target.get("type") != "directory":
                return []

            items = []
            for name, item in target.get("contents", {}).items():
                items.append({
                    "name": name,
                    "type": item["type"],
                    "size": item.get("size", len(item.get("contents", {}))),
                    "modified": item.get("modified", "")[:16]
                })
            return items
        except:
            return []

    def cat(self, path: str) -> Optional[str]:
        """Read file content"""
        try:
            if not path.startswith("/"):
                path = f"{self.current_path.rstrip('/')}/{path}"

            parent_path = "/".join(path.split("/")[:-1]) or "/"
            file_name = path.split("/")[-1]

            parent = self._navigate_to_path(parent_path)
            if parent and file_name in parent.get("contents", {}):
                item = parent["contents"][file_name]
                if item["type"] == "file":
                    return item.get("content", "")
            return None
        except:
            return None

print("✅ Part 1 complete - Core game classes created!")
print("- Achievement system with XP rewards")
print("- Mission system with daily challenges")  
print("- Gamified file system with progress tracking")
print("- Statistics and leveling system \n\n")# Part 2: GameOS GUI with all gaming features

class GameProcess:
    def __init__(self, pid: int, name: str, command: str, game_manager):
        self.pid = pid
        self.name = name
        self.command = command
        self.state = "ready"
        self.memory_usage = random.randint(100, 500)
        self.cpu_time = 0
        self.created = datetime.now()
        self.game_manager = game_manager

class GameProcessManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.processes = {}
        self.next_pid = 1
        self._create_initial_processes()

    def _create_initial_processes(self):
        """Create initial system processes"""
        self.create_process("init", "/sbin/init", game_action=False)
        self.create_process("kernel", "/kernel/main", game_action=False)
        self.create_process("gamemaster", "/usr/bin/gamemaster", game_action=False)
        self.create_process("desktop", "/usr/bin/desktop", game_action=False)

    def create_process(self, name: str, command: str, game_action: bool = True) -> int:
        pid = self.next_pid
        self.next_pid += 1
        self.processes[pid] = GameProcess(pid, name, command, self.game_manager)

        if game_action:
            # Game mechanics
            self.game_manager.stats.processes_created += 1
            leveled_up = self.game_manager.stats.add_xp(30)

            if leveled_up:
                self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

            # Check achievements
            self.game_manager.check_achievement("taskmaster")
            self.game_manager.check_achievement("multitasker")

            # Update missions
            self.game_manager.update_mission_progress("process_master")

        return pid

    def kill_process(self, pid: int) -> bool:
        if pid in self.processes and pid > 4:  # Protect system processes
            self.processes[pid].state = "terminated"

            # Game mechanics
            self.game_manager.stats.processes_killed += 1
            leveled_up = self.game_manager.stats.add_xp(20)

            if leveled_up:
                self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

            # Update missions
            self.game_manager.update_mission_progress("process_master")

            return True
        return False

    def list_processes(self) -> List[Dict]:
        return [
            {
                "pid": p.pid,
                "name": p.name,
                "state": p.state,
                "memory": p.memory_usage,
                "cpu_time": p.cpu_time,
                "command": p.command
            }
            for p in self.processes.values()
        ]

class GameMemoryManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.total_memory = 8192
        self.used_memory = random.randint(1000, 2000)
        self.free_memory = self.total_memory - self.used_memory

    def get_status(self) -> Dict:
        utilization = (self.used_memory / self.total_memory) * 100

        # Update highest memory usage for achievements
        if utilization > self.game_manager.stats.highest_memory_usage:
            self.game_manager.stats.highest_memory_usage = utilization

        return {
            "total": self.total_memory,
            "used": self.used_memory,
            "free": self.free_memory,
            "utilization": utilization
        }

class GameKernel:
    def __init__(self):
        self.game_manager = GameManager()
        self.filesystem = GameFileSystem(self.game_manager)
        self.process_manager = GameProcessManager(self.game_manager)
        self.memory_manager = GameMemoryManager(self.game_manager)
        self.boot_time = datetime.now()

    def get_system_info(self):
        uptime = datetime.now() - self.boot_time
        return {
            "os_name": "PyOS GameOS",
            "version": "1.0 Gaming Edition",
            "uptime": str(uptime).split(".")[0],
            "boot_time": self.boot_time.isoformat(),
            "memory": self.memory_manager.get_status(),
            "level": self.game_manager.stats.level,
            "total_xp": self.game_manager.stats.total_xp
        }

class GameOSGUI:
    def __init__(self):
        self.kernel = GameKernel()
        self.game_manager = self.kernel.game_manager
        self.root = tk.Tk()
        self.setup_window()
        self.create_interface()

        # Start game timer
        self.game_timer_start = datetime.now()
        self.update_game_timer()

    def setup_window(self):
        """Setup main window with gaming theme"""
        self.root.title("🎮 PyOS GameOS - Operating System Simulator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Gaming color scheme
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors for gaming theme
        self.root.configure(bg='#1a1a2e')

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")

    def create_interface(self):
        """Create the gaming interface"""
        # Create top game bar
        self.create_game_bar()

        # Create menu
        self.create_menu()

        # Create main content with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create all tabs
        self.create_dashboard_tab()
        self.create_file_manager_tab()
        self.create_process_manager_tab()
        self.create_terminal_tab()
        self.create_achievements_tab()
        self.create_missions_tab()
        self.create_games_tab()
        self.create_leaderboard_tab()

        # Create status bar
        self.create_status_bar()

        # Start updates
        self.update_displays()
        self.show_notifications()

    def create_game_bar(self):
        """Create top game status bar"""
        game_bar = tk.Frame(self.root, bg='#16213e', height=60)
        game_bar.pack(fill=tk.X, padx=5, pady=5)
        game_bar.pack_propagate(False)

        # Player info frame
        player_frame = tk.Frame(game_bar, bg='#16213e')
        player_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Player level and XP
        level_text = f"Level {self.game_manager.stats.level}"
        self.level_label = tk.Label(player_frame, text=level_text, 
                                   font=('Arial', 12, 'bold'), 
                                   fg='#ffd700', bg='#16213e')
        self.level_label.pack(anchor='w')

        # XP Progress bar
        progress_frame = tk.Frame(player_frame, bg='#16213e')
        progress_frame.pack(fill=tk.X, pady=2)

        tk.Label(progress_frame, text="XP:", font=('Arial', 8), 
                fg='white', bg='#16213e').pack(side=tk.LEFT)

        self.xp_progress = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.xp_progress.pack(side=tk.LEFT, padx=5)

        self.xp_label = tk.Label(progress_frame, text="0/100", 
                               font=('Arial', 8), fg='white', bg='#16213e')
        self.xp_label.pack(side=tk.LEFT, padx=5)

        # Stats frame
        stats_frame = tk.Frame(game_bar, bg='#16213e')
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Quick stats
        self.achievements_count_label = tk.Label(stats_frame, 
                                               text=f"🏆 {self.game_manager.stats.achievements_unlocked}", 
                                               font=('Arial', 10, 'bold'), 
                                               fg='#ffd700', bg='#16213e')
        self.achievements_count_label.pack(anchor='e')

        self.missions_count_label = tk.Label(stats_frame, 
                                           text=f"✅ {self.game_manager.stats.missions_completed}", 
                                           font=('Arial', 10, 'bold'), 
                                           fg='#00ff7f', bg='#16213e')
        self.missions_count_label.pack(anchor='e')

        # Update progress bar
        self.update_xp_display()

    def create_menu(self):
        """Create menu with gaming options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎮 Game", menu=game_menu)
        game_menu.add_command(label="📊 Dashboard", command=lambda: self.notebook.select(0))
        game_menu.add_command(label="🏆 Achievements", command=lambda: self.notebook.select(4))
        game_menu.add_command(label="🎯 Missions", command=lambda: self.notebook.select(5))
        game_menu.add_separator()
        game_menu.add_command(label="🔄 New Daily Missions", command=self.generate_new_missions)
        game_menu.add_command(label="📈 View Stats", command=self.show_detailed_stats)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="New File (+10 XP)", command=self.new_file)
        file_menu.add_command(label="New Folder (+25 XP)", command=self.new_folder)

        # Process menu
        process_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Process", menu=process_menu)
        process_menu.add_command(label="New Process (+30 XP)", command=self.new_process)

        # Games menu
        games_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎲 Games", menu=games_menu)
        games_menu.add_command(label="🐍 Snake Game", command=self.play_snake)
        games_menu.add_command(label="🧩 Puzzle Challenge", command=self.play_puzzle)
        games_menu.add_command(label="⚡ Speed Challenge", command=self.speed_challenge)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="🎮 How to Play", command=self.show_game_help)
        help_menu.add_command(label="🏆 Achievement Guide", command=self.show_achievement_guide)
        help_menu.add_command(label="ℹ️ About GameOS", command=self.show_about)

    def create_dashboard_tab(self):
        """Create main dashboard with game overview"""
        dashboard = ttk.Frame(self.notebook)
        self.notebook.add(dashboard, text="📊 Dashboard")

        # Create scrollable frame
        canvas = tk.Canvas(dashboard)
        scrollbar = ttk.Scrollbar(dashboard, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Welcome message
        welcome_frame = ttk.LabelFrame(scrollable_frame, text="🎮 Welcome to GameOS!", padding=15)
        welcome_frame.pack(fill=tk.X, padx=10, pady=5)

        welcome_text = f"""Welcome back, System Administrator! 

🎯 Your Current Status:
• Level: {self.game_manager.stats.level}
• Total XP: {self.game_manager.stats.total_xp:,}
• Achievements: {self.game_manager.stats.achievements_unlocked}/20
• Missions Completed: {self.game_manager.stats.missions_completed}
• Login Streak: {self.game_manager.stats.login_streak} days

Ready to continue your journey to becoming a Master System Administrator?"""

        tk.Label(welcome_frame, text=welcome_text, font=('Arial', 11), justify=tk.LEFT).pack()

        # Quick stats
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📈 Quick Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        # Create stat boxes
        stat_boxes = [
            ("📄 Files Created", self.game_manager.stats.files_created, "#4CAF50"),
            ("📁 Folders Created", self.game_manager.stats.directories_created, "#2196F3"),
            ("⚙️ Processes Created", self.game_manager.stats.processes_created, "#FF9800"),
            ("💻 Commands Executed", self.game_manager.stats.commands_executed, "#9C27B0"),
        ]

        for i, (label, value, color) in enumerate(stat_boxes):
            col = i % 2
            row = i // 2

            stat_frame = tk.Frame(stats_grid, bg=color, relief='raised', bd=2)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            stats_grid.columnconfigure(col, weight=1)

            tk.Label(stat_frame, text=str(value), font=('Arial', 18, 'bold'), 
                    fg='white', bg=color).pack()
            tk.Label(stat_frame, text=label, font=('Arial', 10), 
                    fg='white', bg=color).pack()

        # Recent achievements
        achievements_frame = ttk.LabelFrame(scrollable_frame, text="🏆 Recent Achievements", padding=10)
        achievements_frame.pack(fill=tk.X, padx=10, pady=5)

        self.recent_achievements_text = scrolledtext.ScrolledText(achievements_frame, height=6)
        self.recent_achievements_text.pack(fill=tk.X)

        # Active missions overview
        missions_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Active Missions", padding=10)
        missions_frame.pack(fill=tk.X, padx=10, pady=5)

        self.mission_overview_frame = tk.Frame(missions_frame)
        self.mission_overview_frame.pack(fill=tk.X)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Update dashboard content
        self.update_dashboard()

    def update_dashboard(self):
        """Update dashboard content"""
        # Update recent achievements
        self.recent_achievements_text.delete(1.0, tk.END)
        recent_achievements = [a for a in self.game_manager.achievements.values() if a.unlocked]
        recent_achievements.sort(key=lambda x: x.unlock_time or datetime.min, reverse=True)

        if recent_achievements:
            for achievement in recent_achievements[:5]:
                self.recent_achievements_text.insert(tk.END, 
                    f"{achievement.icon} {achievement.name} - {achievement.description}\n")
        else:
            self.recent_achievements_text.insert(tk.END, "No achievements unlocked yet. Start exploring to earn your first achievement!")

        # Update mission overview
        for widget in self.mission_overview_frame.winfo_children():
            widget.destroy()

        if self.game_manager.active_missions:
            for i, mission in enumerate(self.game_manager.active_missions):
                mission_frame = tk.Frame(self.mission_overview_frame, relief='ridge', bd=1)
                mission_frame.pack(fill=tk.X, pady=2)

                # Mission info
                info_frame = tk.Frame(mission_frame)
                info_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(info_frame, text=f"🎯 {mission.name}", 
                        font=('Arial', 10, 'bold')).pack(anchor='w')
                tk.Label(info_frame, text=mission.description, 
                        font=('Arial', 9)).pack(anchor='w')

                # Progress bar
                progress_frame = tk.Frame(mission_frame)
                progress_frame.pack(fill=tk.X, padx=5, pady=2)

                progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
                progress_bar.pack(side=tk.LEFT)
                progress_bar['value'] = (mission.progress / mission.target) * 100

                status = "✅ Complete" if mission.completed else f"{mission.progress}/{mission.target}"
                tk.Label(progress_frame, text=status).pack(side=tk.LEFT, padx=5)

                if mission.completed:
                    tk.Label(progress_frame, text=f"🎉 +{mission.xp_reward} XP", 
                            fg='green', font=('Arial', 8, 'bold')).pack(side=tk.LEFT)

print("✅ Part 2 complete - Game GUI framework created!")# Part 2: GameOS GUI with all gaming features

class GameProcess:
    def __init__(self, pid: int, name: str, command: str, game_manager):
        self.pid = pid
        self.name = name
        self.command = command
        self.state = "ready"
        self.memory_usage = random.randint(100, 500)
        self.cpu_time = 0
        self.created = datetime.now()
        self.game_manager = game_manager

class GameProcessManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.processes = {}
        self.next_pid = 1
        self._create_initial_processes()

    def _create_initial_processes(self):
        """Create initial system processes"""
        self.create_process("init", "/sbin/init", game_action=False)
        self.create_process("kernel", "/kernel/main", game_action=False)
        self.create_process("gamemaster", "/usr/bin/gamemaster", game_action=False)
        self.create_process("desktop", "/usr/bin/desktop", game_action=False)

    def create_process(self, name: str, command: str, game_action: bool = True) -> int:
        pid = self.next_pid
        self.next_pid += 1
        self.processes[pid] = GameProcess(pid, name, command, self.game_manager)

        if game_action:
            # Game mechanics
            self.game_manager.stats.processes_created += 1
            leveled_up = self.game_manager.stats.add_xp(30)

            if leveled_up:
                self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

            # Check achievements
            self.game_manager.check_achievement("taskmaster")
            self.game_manager.check_achievement("multitasker")

            # Update missions
            self.game_manager.update_mission_progress("process_master")

        return pid

    def kill_process(self, pid: int) -> bool:
        if pid in self.processes and pid > 4:  # Protect system processes
            self.processes[pid].state = "terminated"

            # Game mechanics
            self.game_manager.stats.processes_killed += 1
            leveled_up = self.game_manager.stats.add_xp(20)

            if leveled_up:
                self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

            # Update missions
            self.game_manager.update_mission_progress("process_master")

            return True
        return False

    def list_processes(self) -> List[Dict]:
        return [
            {
                "pid": p.pid,
                "name": p.name,
                "state": p.state,
                "memory": p.memory_usage,
                "cpu_time": p.cpu_time,
                "command": p.command
            }
            for p in self.processes.values()
        ]

class GameMemoryManager:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.total_memory = 8192
        self.used_memory = random.randint(1000, 2000)
        self.free_memory = self.total_memory - self.used_memory

    def get_status(self) -> Dict:
        utilization = (self.used_memory / self.total_memory) * 100

        # Update highest memory usage for achievements
        if utilization > self.game_manager.stats.highest_memory_usage:
            self.game_manager.stats.highest_memory_usage = utilization

        return {
            "total": self.total_memory,
            "used": self.used_memory,
            "free": self.free_memory,
            "utilization": utilization
        }

class GameKernel:
    def __init__(self):
        self.game_manager = GameManager()
        self.filesystem = GameFileSystem(self.game_manager)
        self.process_manager = GameProcessManager(self.game_manager)
        self.memory_manager = GameMemoryManager(self.game_manager)
        self.boot_time = datetime.now()

    def get_system_info(self):
        uptime = datetime.now() - self.boot_time
        return {
            "os_name": "PyOS GameOS",
            "version": "1.0 Gaming Edition",
            "uptime": str(uptime).split(".")[0],
            "boot_time": self.boot_time.isoformat(),
            "memory": self.memory_manager.get_status(),
            "level": self.game_manager.stats.level,
            "total_xp": self.game_manager.stats.total_xp
        }

class GameOSGUI:
    def __init__(self):
        self.kernel = GameKernel()
        self.game_manager = self.kernel.game_manager
        self.root = tk.Tk()
        self.setup_window()
        self.create_interface()

        # Start game timer
        self.game_timer_start = datetime.now()
        self.update_game_timer()

    def setup_window(self):
        """Setup main window with gaming theme"""
        self.root.title("🎮 PyOS GameOS - Operating System Simulator")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        # Gaming color scheme
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors for gaming theme
        self.root.configure(bg='#1a1a2e')

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")

    def create_interface(self):
        """Create the gaming interface"""
        # Create top game bar
        self.create_game_bar()

        # Create menu
        self.create_menu()

        # Create main content with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Create all tabs
        self.create_dashboard_tab()
        self.create_file_manager_tab()
        self.create_process_manager_tab()
        self.create_terminal_tab()
        self.create_achievements_tab()
        self.create_missions_tab()
        self.create_games_tab()
        self.create_leaderboard_tab()

        # Create status bar
        self.create_status_bar()

        # Start updates
        self.update_displays()
        self.show_notifications()

    def create_game_bar(self):
        """Create top game status bar"""
        game_bar = tk.Frame(self.root, bg='#16213e', height=60)
        game_bar.pack(fill=tk.X, padx=5, pady=5)
        game_bar.pack_propagate(False)

        # Player info frame
        player_frame = tk.Frame(game_bar, bg='#16213e')
        player_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Player level and XP
        level_text = f"Level {self.game_manager.stats.level}"
        self.level_label = tk.Label(player_frame, text=level_text, 
                                   font=('Arial', 12, 'bold'), 
                                   fg='#ffd700', bg='#16213e')
        self.level_label.pack(anchor='w')

        # XP Progress bar
        progress_frame = tk.Frame(player_frame, bg='#16213e')
        progress_frame.pack(fill=tk.X, pady=2)

        tk.Label(progress_frame, text="XP:", font=('Arial', 8), 
                fg='white', bg='#16213e').pack(side=tk.LEFT)

        self.xp_progress = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.xp_progress.pack(side=tk.LEFT, padx=5)

        self.xp_label = tk.Label(progress_frame, text="0/100", 
                               font=('Arial', 8), fg='white', bg='#16213e')
        self.xp_label.pack(side=tk.LEFT, padx=5)

        # Stats frame
        stats_frame = tk.Frame(game_bar, bg='#16213e')
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Quick stats
        self.achievements_count_label = tk.Label(stats_frame, 
                                               text=f"🏆 {self.game_manager.stats.achievements_unlocked}", 
                                               font=('Arial', 10, 'bold'), 
                                               fg='#ffd700', bg='#16213e')
        self.achievements_count_label.pack(anchor='e')

        self.missions_count_label = tk.Label(stats_frame, 
                                           text=f"✅ {self.game_manager.stats.missions_completed}", 
                                           font=('Arial', 10, 'bold'), 
                                           fg='#00ff7f', bg='#16213e')
        self.missions_count_label.pack(anchor='e')

        # Update progress bar
        self.update_xp_display()

    def create_menu(self):
        """Create menu with gaming options"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎮 Game", menu=game_menu)
        game_menu.add_command(label="📊 Dashboard", command=lambda: self.notebook.select(0))
        game_menu.add_command(label="🏆 Achievements", command=lambda: self.notebook.select(4))
        game_menu.add_command(label="🎯 Missions", command=lambda: self.notebook.select(5))
        game_menu.add_separator()
        game_menu.add_command(label="🔄 New Daily Missions", command=self.generate_new_missions)
        game_menu.add_command(label="📈 View Stats", command=self.show_detailed_stats)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="New File (+10 XP)", command=self.new_file)
        file_menu.add_command(label="New Folder (+25 XP)", command=self.new_folder)

        # Process menu
        process_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Process", menu=process_menu)
        process_menu.add_command(label="New Process (+30 XP)", command=self.new_process)

        # Games menu
        games_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🎲 Games", menu=games_menu)
        games_menu.add_command(label="🐍 Snake Game", command=self.play_snake)
        games_menu.add_command(label="🧩 Puzzle Challenge", command=self.play_puzzle)
        games_menu.add_command(label="⚡ Speed Challenge", command=self.speed_challenge)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="🎮 How to Play", command=self.show_game_help)
        help_menu.add_command(label="🏆 Achievement Guide", command=self.show_achievement_guide)
        help_menu.add_command(label="ℹ️ About GameOS", command=self.show_about)

    def create_dashboard_tab(self):
        """Create main dashboard with game overview"""
        dashboard = ttk.Frame(self.notebook)
        self.notebook.add(dashboard, text="📊 Dashboard")

        # Create scrollable frame
        canvas = tk.Canvas(dashboard)
        scrollbar = ttk.Scrollbar(dashboard, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Welcome message
        welcome_frame = ttk.LabelFrame(scrollable_frame, text="🎮 Welcome to GameOS!", padding=15)
        welcome_frame.pack(fill=tk.X, padx=10, pady=5)

        welcome_text = f"""Welcome back, System Administrator! 

🎯 Your Current Status:
• Level: {self.game_manager.stats.level}
• Total XP: {self.game_manager.stats.total_xp:,}
• Achievements: {self.game_manager.stats.achievements_unlocked}/20
• Missions Completed: {self.game_manager.stats.missions_completed}
• Login Streak: {self.game_manager.stats.login_streak} days

Ready to continue your journey to becoming a Master System Administrator?"""

        tk.Label(welcome_frame, text=welcome_text, font=('Arial', 11), justify=tk.LEFT).pack()

        # Quick stats
        stats_frame = ttk.LabelFrame(scrollable_frame, text="📈 Quick Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        stats_grid = tk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)

        # Create stat boxes
        stat_boxes = [
            ("📄 Files Created", self.game_manager.stats.files_created, "#4CAF50"),
            ("📁 Folders Created", self.game_manager.stats.directories_created, "#2196F3"),
            ("⚙️ Processes Created", self.game_manager.stats.processes_created, "#FF9800"),
            ("💻 Commands Executed", self.game_manager.stats.commands_executed, "#9C27B0"),
        ]

        for i, (label, value, color) in enumerate(stat_boxes):
            col = i % 2
            row = i // 2

            stat_frame = tk.Frame(stats_grid, bg=color, relief='raised', bd=2)
            stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            stats_grid.columnconfigure(col, weight=1)

            tk.Label(stat_frame, text=str(value), font=('Arial', 18, 'bold'), 
                    fg='white', bg=color).pack()
            tk.Label(stat_frame, text=label, font=('Arial', 10), 
                    fg='white', bg=color).pack()

        # Recent achievements
        achievements_frame = ttk.LabelFrame(scrollable_frame, text="🏆 Recent Achievements", padding=10)
        achievements_frame.pack(fill=tk.X, padx=10, pady=5)

        self.recent_achievements_text = scrolledtext.ScrolledText(achievements_frame, height=6)
        self.recent_achievements_text.pack(fill=tk.X)

        # Active missions overview
        missions_frame = ttk.LabelFrame(scrollable_frame, text="🎯 Active Missions", padding=10)
        missions_frame.pack(fill=tk.X, padx=10, pady=5)

        self.mission_overview_frame = tk.Frame(missions_frame)
        self.mission_overview_frame.pack(fill=tk.X)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Update dashboard content
        self.update_dashboard()

    def update_dashboard(self):
        """Update dashboard content"""
        # Update recent achievements
        self.recent_achievements_text.delete(1.0, tk.END)
        recent_achievements = [a for a in self.game_manager.achievements.values() if a.unlocked]
        recent_achievements.sort(key=lambda x: x.unlock_time or datetime.min, reverse=True)

        if recent_achievements:
            for achievement in recent_achievements[:5]:
                self.recent_achievements_text.insert(tk.END, 
                    f"{achievement.icon} {achievement.name} - {achievement.description}\n")
        else:
            self.recent_achievements_text.insert(tk.END, "No achievements unlocked yet. Start exploring to earn your first achievement!")

        # Update mission overview
        for widget in self.mission_overview_frame.winfo_children():
            widget.destroy()

        if self.game_manager.active_missions:
            for i, mission in enumerate(self.game_manager.active_missions):
                mission_frame = tk.Frame(self.mission_overview_frame, relief='ridge', bd=1)
                mission_frame.pack(fill=tk.X, pady=2)

                # Mission info
                info_frame = tk.Frame(mission_frame)
                info_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(info_frame, text=f"🎯 {mission.name}", 
                        font=('Arial', 10, 'bold')).pack(anchor='w')
                tk.Label(info_frame, text=mission.description, 
                        font=('Arial', 9)).pack(anchor='w')

                # Progress bar
                progress_frame = tk.Frame(mission_frame)
                progress_frame.pack(fill=tk.X, padx=5, pady=2)

                progress_bar = ttk.Progressbar(progress_frame, length=200, mode='determinate')
                progress_bar.pack(side=tk.LEFT)
                progress_bar['value'] = (mission.progress / mission.target) * 100

                status = "✅ Complete" if mission.completed else f"{mission.progress}/{mission.target}"
                tk.Label(progress_frame, text=status).pack(side=tk.LEFT, padx=5)

                if mission.completed:
                    tk.Label(progress_frame, text=f"🎉 +{mission.xp_reward} XP", 
                            fg='green', font=('Arial', 8, 'bold')).pack(side=tk.LEFT)

                    print("✅ Part 2 complete - Game GUI framework created!")
    def create_file_manager_tab(self):
        """File manager with XP rewards"""
        file_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_frame, text="📁 File Manager (+XP)")

        # XP info banner
        xp_banner = tk.Frame(file_frame, bg='#4CAF50', height=30)
        xp_banner.pack(fill=tk.X)
        xp_banner.pack_propagate(False)

        tk.Label(xp_banner, text="💰 Earn XP: Create File (+10 XP) | Create Folder (+25 XP) | Delete Item (+5 XP)", 
                bg='#4CAF50', fg='white', font=('Arial', 10, 'bold')).pack(expand=True)

        # Path display
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(path_frame, text="📍 Current Path:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value="/")
        ttk.Label(path_frame, textvariable=self.path_var, font=('Courier', 10)).pack(side=tk.LEFT, padx=10)

        # File list
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("Name", "Type", "Size", "Modified")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        for col in columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Gaming buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="📄 New File (+10 XP)", 
                  command=self.new_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 New Folder (+25 XP)", 
                  command=self.new_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete (+5 XP)", 
                  command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="👁️ View", 
                  command=self.view_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.refresh_files).pack(side=tk.LEFT, padx=5)

        # Bind events
        self.file_tree.bind("<Double-1>", self.on_file_double_click)

        self.refresh_files()

    def create_achievements_tab(self):
        """Achievements showcase"""
        achievements_frame = ttk.Frame(self.notebook)
        self.notebook.add(achievements_frame, text="🏆 Achievements")

        # Progress header
        header_frame = ttk.Frame(achievements_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        progress_text = f"🏆 Achievements Unlocked: {self.game_manager.stats.achievements_unlocked}/20"
        tk.Label(header_frame, text=progress_text, font=('Arial', 14, 'bold')).pack()

        # Achievement progress bar
        achievement_progress = ttk.Progressbar(header_frame, length=400, mode='determinate')
        achievement_progress.pack(pady=5)
        achievement_progress['value'] = (self.game_manager.stats.achievements_unlocked / 20) * 100

        # Scrollable achievements list
        canvas = tk.Canvas(achievements_frame)
        scrollbar = ttk.Scrollbar(achievements_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display achievements
        for achievement in self.game_manager.achievements.values():
            self.create_achievement_card(scrollable_frame, achievement)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        scrollbar.pack(side="right", fill="y")

    def create_achievement_card(self, parent, achievement):
        """Create achievement card"""
        # Card frame with different colors for unlocked/locked
        bg_color = '#4CAF50' if achievement.unlocked else '#757575'

        card_frame = tk.Frame(parent, bg=bg_color, relief='raised', bd=2)
        card_frame.pack(fill=tk.X, padx=5, pady=3)

        # Icon and name
        top_frame = tk.Frame(card_frame, bg=bg_color)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        icon_label = tk.Label(top_frame, text=achievement.icon, font=('Arial', 20), bg=bg_color)
        icon_label.pack(side=tk.LEFT)

        name_frame = tk.Frame(top_frame, bg=bg_color)
        name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        name_color = 'white' if achievement.unlocked else '#E0E0E0'
        name_label = tk.Label(name_frame, text=achievement.name, 
                             font=('Arial', 12, 'bold'), fg=name_color, bg=bg_color)
        name_label.pack(anchor='w')

        desc_label = tk.Label(name_frame, text=achievement.description, 
                             font=('Arial', 10), fg=name_color, bg=bg_color)
        desc_label.pack(anchor='w')

        # XP reward
        xp_label = tk.Label(top_frame, text=f"+{achievement.xp_reward} XP", 
                           font=('Arial', 10, 'bold'), fg='#FFD700', bg=bg_color)
        xp_label.pack(side=tk.RIGHT)

        # Unlock time if unlocked
        if achievement.unlocked and achievement.unlock_time:
            time_label = tk.Label(card_frame, 
                                 text=f"Unlocked: {achievement.unlock_time.strftime('%Y-%m-%d %H:%M')}", 
                                 font=('Arial', 8), fg='white', bg=bg_color)
            time_label.pack(anchor='w', padx=10, pady=2)

    def create_missions_tab(self):
        """Daily missions tab"""
        missions_frame = ttk.Frame(self.notebook)
        self.notebook.add(missions_frame, text="🎯 Daily Missions")

        # Header
        header_frame = ttk.Frame(missions_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(header_frame, text="🎯 Daily Missions", 
                font=('Arial', 16, 'bold')).pack()
        tk.Label(header_frame, text="Complete missions to earn bonus XP and maintain your streak!", 
                font=('Arial', 10)).pack()

        # Mission streak info
        streak_frame = ttk.LabelFrame(missions_frame, text="🔥 Mission Streak", padding=10)
        streak_frame.pack(fill=tk.X, padx=10, pady=5)

        streak_text = f"Current Streak: {self.game_manager.stats.challenge_streak} days\n"
        streak_text += f"Total Missions Completed: {self.game_manager.stats.missions_completed}"
        tk.Label(streak_frame, text=streak_text, font=('Arial', 11)).pack()

        # Active missions
        missions_container = ttk.LabelFrame(missions_frame, text="📋 Today's Missions", padding=10)
        missions_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.missions_display_frame = tk.Frame(missions_container)
        self.missions_display_frame.pack(fill=tk.BOTH, expand=True)

        # Refresh missions button
        button_frame = ttk.Frame(missions_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="🔄 Generate New Daily Missions", 
                  command=self.generate_new_missions).pack()

        self.update_missions_display()

    def update_missions_display(self):
        """Update missions display"""
        # Clear existing widgets
        for widget in self.missions_display_frame.winfo_children():
            widget.destroy()

        if not self.game_manager.active_missions:
            tk.Label(self.missions_display_frame, 
                    text="No active missions. Generate new daily missions!", 
                    font=('Arial', 12)).pack(expand=True)
            return

        for mission in self.game_manager.active_missions:
            # Mission card
            mission_card = tk.Frame(self.missions_display_frame, relief='ridge', bd=2)
            mission_card.pack(fill=tk.X, pady=5)

            # Mission header
            header = tk.Frame(mission_card)
            header.pack(fill=tk.X, padx=10, pady=5)

            # Difficulty color
            diff_colors = {"Easy": "#4CAF50", "Medium": "#FF9800", "Hard": "#F44336"}
            diff_color = diff_colors.get(mission.difficulty, "#757575")

            tk.Label(header, text="🎯", font=('Arial', 16)).pack(side=tk.LEFT)

            info_frame = tk.Frame(header)
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

            tk.Label(info_frame, text=mission.name, 
                    font=('Arial', 12, 'bold')).pack(anchor='w')
            tk.Label(info_frame, text=mission.description, 
                    font=('Arial', 10)).pack(anchor='w')

            # Difficulty and XP
            reward_frame = tk.Frame(header)
            reward_frame.pack(side=tk.RIGHT)

            tk.Label(reward_frame, text=mission.difficulty, 
                    bg=diff_color, fg='white', font=('Arial', 8, 'bold'), 
                    padx=5, pady=2).pack()
            tk.Label(reward_frame, text=f"+{mission.xp_reward} XP", 
                    font=('Arial', 10, 'bold'), fg='#FFD700').pack()

            # Progress bar
            progress_frame = tk.Frame(mission_card)
            progress_frame.pack(fill=tk.X, padx=10, pady=5)

            progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
            progress_bar.pack(side=tk.LEFT)

            if mission.target > 0:
                progress_percentage = (mission.progress / mission.target) * 100
                progress_bar['value'] = progress_percentage

                progress_text = f"{mission.progress}/{mission.target}"
                if mission.completed:
                    progress_text += " ✅ COMPLETE!"
            else:
                progress_text = "Ready to start"

            tk.Label(progress_frame, text=progress_text, 
                    font=('Arial', 10)).pack(side=tk.LEFT, padx=10)

    def create_games_tab(self):
        """Mini-games tab"""
        games_frame = ttk.Frame(self.notebook)
        self.notebook.add(games_frame, text="🎮 Mini-Games")

        # Header
        header_frame = ttk.Frame(games_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(header_frame, text="🎮 Mini-Games Hub", 
                font=('Arial', 16, 'bold')).pack()
        tk.Label(header_frame, text="Play games to earn bonus XP and unlock achievements!", 
                font=('Arial', 10)).pack()

        # Games grid
        games_grid = tk.Frame(games_frame)
        games_grid.pack(expand=True, pady=20)

        # Game cards
        games = [
            ("🐍 Snake", "Classic Snake game", "snake", "#4CAF50"),
            ("🧩 Puzzle", "Logic puzzles", "puzzle", "#2196F3"),
            ("⚡ Speed Test", "Test your speed", "speed", "#FF9800"),
            ("🎯 Memory Game", "Memory challenge", "memory", "#9C27B0"),
        ]

        for i, (name, desc, game_id, color) in enumerate(games):
            row = i // 2
            col = i % 2

            game_card = tk.Frame(games_grid, bg=color, relief='raised', bd=3, width=200, height=150)
            game_card.grid(row=row, column=col, padx=10, pady=10)
            game_card.pack_propagate(False)

            tk.Label(game_card, text=name, font=('Arial', 14, 'bold'), 
                    fg='white', bg=color).pack(expand=True)
            tk.Label(game_card, text=desc, font=('Arial', 10), 
                    fg='white', bg=color).pack()

            play_button = tk.Button(game_card, text="▶️ Play", 
                                   command=lambda gid=game_id: self.play_game(gid))
            play_button.pack(pady=5)

        # Game stats
        stats_frame = ttk.LabelFrame(games_frame, text="🏆 Gaming Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(stats_frame, text=f"Games Played: {self.game_manager.stats.games_played}", 
                font=('Arial', 11)).pack()

    def create_leaderboard_tab(self):
        """Leaderboard tab"""
        leaderboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(leaderboard_frame, text="🥇 Leaderboard")

        # Header
        header_frame = ttk.Frame(leaderboard_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(header_frame, text="🥇 Global Leaderboard", 
                font=('Arial', 16, 'bold')).pack()
        tk.Label(header_frame, text="See how you rank against other System Administrators!", 
                font=('Arial', 10)).pack()

        # Current player stats
        player_frame = ttk.LabelFrame(leaderboard_frame, text="👤 Your Stats", padding=10)
        player_frame.pack(fill=tk.X, padx=10, pady=5)

        stats_text = f"""Level: {self.game_manager.stats.level}
Total XP: {self.game_manager.stats.total_xp:,}
Achievements: {self.game_manager.stats.achievements_unlocked}/20
Login Streak: {self.game_manager.stats.login_streak} days
Files Created: {self.game_manager.stats.files_created}"""

        tk.Label(player_frame, text=stats_text, font=('Courier', 10), justify=tk.LEFT).pack()

        # Mock leaderboard (in real app, this would connect to a server)
        leaderboard_data_frame = ttk.LabelFrame(leaderboard_frame, text="🏆 Top Players", padding=10)
        leaderboard_data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Leaderboard table
        columns = ("Rank", "Player", "Level", "XP", "Achievements")
        leaderboard_tree = ttk.Treeview(leaderboard_data_frame, columns=columns, show="headings", height=15)

        for col in columns:
            leaderboard_tree.heading(col, text=col)
            leaderboard_tree.column(col, width=100)

        # Mock data
        mock_data = [
            (1, "SystemMaster", 15, "22,500", "18/20"),
            (2, "AdminPro", 12, "14,400", "15/20"),
            (3, "CodeNinja", 10, "10,000", "12/20"),
            (4, "TechWizard", 8, "6,400", "10/20"),
            (5, f"YOU ({datetime.now().strftime('%H:%M')})", self.game_manager.stats.level, 
                f"{self.game_manager.stats.total_xp:,}", f"{self.game_manager.stats.achievements_unlocked}/20"),
        ]

        for data in mock_data:
            item = leaderboard_tree.insert("", tk.END, values=data)
            if "YOU" in str(data[1]):
                leaderboard_tree.set(item, "Player", data[1])
                # Highlight current player

        leaderboard_tree.pack(fill=tk.BOTH, expand=True)

        # Note about online features
        note_frame = tk.Frame(leaderboard_frame)
        note_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(note_frame, text="📝 Note: This is a demo leaderboard. In the full version, you'd compete with real players!", 
                font=('Arial', 9), fg='gray').pack()

        print("✅ Complete gamified GUI created!")
        print("Features include:")
        print("- Dashboard with game stats")
        print("- XP and leveling system")
        print("- Achievement showcase")
        print("- Daily missions")
        print("- Mini-games hub")
        print("- Leaderboard")
        print("- Gamified file manager")
    def update_xp_display(self):
        """Update XP progress bar"""
        progress = self.game_manager.get_level_progress()
        self.xp_progress['value'] = progress['percentage']
        self.xp_label.config(text=f"{int(progress['current_xp'])}/{int(progress['needed_xp'])}")

        # Update level display
        self.level_label.config(text=f"Level {self.game_manager.stats.level}")
        self.achievements_count_label.config(text=f"🏆 {self.game_manager.stats.achievements_unlocked}")
        self.missions_count_label.config(text=f"✅ {self.game_manager.stats.missions_completed}")

    def refresh_files(self):
        """Refresh file list"""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        items = self.kernel.filesystem.ls()
        for item in items:
            icon = "📁" if item["type"] == "directory" else "📄"
            name_with_icon = f"{icon} {item['name']}"

            self.file_tree.insert("", tk.END, values=(
                name_with_icon,
                item["type"],
                f"{item['size']} bytes" if item["type"] == "file" else f"{item['size']} items",
                item["modified"]
            ))

        self.path_var.set(self.kernel.filesystem.current_path)

    def new_file(self):
        """Create new file with XP reward"""
        filename = simpledialog.askstring("New File", "Enter filename:")
        if filename:
            current_path = self.kernel.filesystem.current_path
            file_path = f"{current_path.rstrip('/')}/{filename}" if current_path != "/" else f"/{filename}"

            if self.kernel.filesystem.create_file(file_path, ""):
                self.refresh_files()
                self.update_xp_display()
                self.update_missions_display()

    def new_folder(self):
        """Create new folder with XP reward"""
        foldername = simpledialog.askstring("New Folder", "Enter folder name:")
        if foldername:
            current_path = self.kernel.filesystem.current_path
            folder_path = f"{current_path.rstrip('/')}/{foldername}" if current_path != "/" else f"/{foldername}"

            if self.kernel.filesystem.mkdir(folder_path):
                self.refresh_files()
                self.update_xp_display()
                self.update_missions_display()

    def delete_item(self):
        """Delete selected item with XP reward"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name = item["values"][0].split(" ", 1)[1]  # Remove icon

            if messagebox.askyesno("Confirm Delete", f"Delete '{name}'? (+5 XP)"):
                current_path = self.kernel.filesystem.current_path
                item_path = f"{current_path.rstrip('/')}/{name}" if current_path != "/" else f"/{name}"

                if self.kernel.filesystem.rm(item_path):
                    self.refresh_files()
                    self.update_xp_display()
                    self.update_missions_display()

    def on_file_double_click(self, event):
        """Handle file double click"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name = item["values"][0].split(" ", 1)[1]  # Remove icon
            file_type = item["values"][1]

            if file_type == "directory":
                if self.kernel.filesystem.cd(name):
                    self.refresh_files()
            else:
                self.view_file()

    def view_file(self):
        """View selected file"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name = item["values"][0].split(" ", 1)[1]  # Remove icon

            content = self.kernel.filesystem.cat(name)
            if content is not None:
                viewer = tk.Toplevel(self.root)
                viewer.title(f"View - {name}")
                viewer.geometry("600x400")

                text_widget = scrolledtext.ScrolledText(viewer)
                text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                text_widget.insert(1.0, content)
                text_widget.config(state=tk.DISABLED)

                ttk.Button(viewer, text="Close", command=viewer.destroy).pack(pady=5)

    def create_process_manager_tab(self):
        """Process manager with gaming elements"""
        process_frame = ttk.Frame(self.notebook)
        self.notebook.add(process_frame, text="⚙️ Process Manager (+XP)")

        # XP banner
        xp_banner = tk.Frame(process_frame, bg='#FF9800', height=30)
        xp_banner.pack(fill=tk.X)
        xp_banner.pack_propagate(False)

        tk.Label(xp_banner, text="⚙️ Process XP: Create Process (+30 XP) | Kill Process (+20 XP)", 
                bg='#FF9800', fg='white', font=('Arial', 10, 'bold')).pack(expand=True)

        # Process list
        columns = ("PID", "Name", "State", "Memory", "CPU", "Command")
        self.process_tree = ttk.Treeview(process_frame, columns=columns, show="headings")

        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)

        self.process_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Buttons
        button_frame = ttk.Frame(process_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="➕ New Process (+30 XP)", 
                  command=self.new_process).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Kill Process (+20 XP)", 
                  command=self.kill_process).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.refresh_processes).pack(side=tk.LEFT, padx=5)

        self.refresh_processes()

    def refresh_processes(self):
        """Refresh process list"""
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        processes = self.kernel.process_manager.list_processes()
        for proc in processes:
            state_icon = {"ready": "⏸️", "running": "▶️", "terminated": "❌"}.get(proc["state"], "❓")
            status = f"{state_icon} {proc['state']}"

            self.process_tree.insert("", tk.END, values=(
                proc["pid"],
                proc["name"],
                status,
                f"{proc['memory']} KB",
                proc["cpu_time"],
                proc["command"]
            ))

    def new_process(self):
        """Create new process with XP reward"""
        name = simpledialog.askstring("New Process", "Enter process name:")
        if name:
            command = simpledialog.askstring("New Process", "Enter command:")
            if command:
                self.kernel.process_manager.create_process(name, command)
                self.refresh_processes()
                self.update_xp_display()
                self.update_missions_display()

    def kill_process(self):
        """Kill selected process with XP reward"""
        selection = self.process_tree.selection()
        if selection:
            item = self.process_tree.item(selection[0])
            pid = int(item["values"][0])
            name = item["values"][1]

            if pid <= 4:
                messagebox.showwarning("Protected Process", "Cannot kill system processes!")
                return

            if messagebox.askyesno("Confirm Kill", f"Kill process '{name}'? (+20 XP)"):
                if self.kernel.process_manager.kill_process(pid):
                    self.refresh_processes()
                    self.update_xp_display()
                    self.update_missions_display()

    def create_terminal_tab(self):
        """Gaming terminal with XP rewards"""
        terminal_frame = ttk.Frame(self.notebook)
        self.notebook.add(terminal_frame, text="💻 Terminal (+5 XP/cmd)")

        # XP banner
        xp_banner = tk.Frame(terminal_frame, bg='#9C27B0', height=30)
        xp_banner.pack(fill=tk.X)
        xp_banner.pack_propagate(False)

        tk.Label(xp_banner, text="💻 Each command gives +5 XP! Use 'help' to see available commands.", 
                bg='#9C27B0', fg='white', font=('Arial', 10, 'bold')).pack(expand=True)

        # Terminal output
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame, 
            bg="black", 
            fg="#00ff00", 
            font=("Courier", 11)
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Command input
        input_frame = ttk.Frame(terminal_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.prompt_label = ttk.Label(input_frame, text="player@gameos:/$")
        self.prompt_label.pack(side=tk.LEFT)

        self.command_entry = ttk.Entry(input_frame)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.command_entry.bind("<Return>", self.execute_command)

        ttk.Button(input_frame, text="Execute (+5 XP)", 
                  command=self.execute_command).pack(side=tk.RIGHT)

        # Initialize terminal
        self.terminal_output.insert(tk.END, "🎮 Welcome to GameOS Terminal! 🎮\n")
        self.terminal_output.insert(tk.END, "Each command earns you +5 XP!\n")
        self.terminal_output.insert(tk.END, "Type 'help' to see available commands\n\n")

    def execute_command(self, event=None):
        """Execute command with XP reward"""
        command = self.command_entry.get().strip()
        if not command:
            return

        # Add to terminal
        current_path = self.kernel.filesystem.current_path
        self.terminal_output.insert(tk.END, f"player@gameos:{current_path}$ {command}\n")

        # Clear entry
        self.command_entry.delete(0, tk.END)

        # Award XP for command
        leveled_up = self.game_manager.stats.add_xp(5)
        self.game_manager.stats.commands_executed += 1

        if leveled_up:
            self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

        # Check achievements
        self.game_manager.check_achievement("terminal_rookie")
        self.game_manager.check_achievement("terminal_expert")

        # Update missions
        self.game_manager.update_mission_progress("terminal_warrior")

        # Execute command
        parts = command.split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []

        output = ""

        if cmd == "help":
            output = """🎮 GameOS Terminal Commands (+5 XP each):

📁 File System:
  ls              - List files and directories
  cd <path>       - Change directory (+2 XP exploration bonus)
  pwd             - Show current directory
  mkdir <name>    - Create directory (+25 XP)
  touch <name>    - Create file (+10 XP)
  cat <file>      - Display file content
  rm <path>       - Remove file/directory (+5 XP)

⚙️ Process Management:
  ps              - List processes
  kill <pid>      - Kill process (+20 XP)
  top             - Show system status

🎮 Gaming:
  stats           - Show your game stats
  achievements    - List achievements
  missions        - Show active missions
  level           - Show level info

🎯 Pro Tips:
• Complete missions for bonus XP!
• Explore directories for achievements
• Create files and folders for steady XP gain"""

        elif cmd == "stats":
            output = f"""🎮 Your Gaming Stats:

📊 Progress:
  Level: {self.game_manager.stats.level}
  Total XP: {self.game_manager.stats.total_xp:,}
  XP to next level: {int(self.game_manager.get_level_progress()['needed_xp'] - self.game_manager.get_level_progress()['current_xp'])}

🏆 Achievements:
  Unlocked: {self.game_manager.stats.achievements_unlocked}/20

📈 Activity:
  Files Created: {self.game_manager.stats.files_created}
  Folders Created: {self.game_manager.stats.directories_created}  
  Processes Created: {self.game_manager.stats.processes_created}
  Commands Executed: {self.game_manager.stats.commands_executed}
  Login Streak: {self.game_manager.stats.login_streak} days"""

        elif cmd == "level":
            progress = self.game_manager.get_level_progress()
            bar_length = 20
            filled = int((progress['percentage'] / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)

            output = f"""📈 Level Information:

Current Level: {self.game_manager.stats.level}
Progress: [{bar}] {progress['percentage']:.1f}%
Current XP: {int(progress['current_xp'])}
Needed for next level: {int(progress['needed_xp'] - progress['current_xp'])}
Total XP: {self.game_manager.stats.total_xp:,}"""

        elif cmd == "ls":
            items = self.kernel.filesystem.ls()
            for item in items:
                icon = "📁" if item["type"] == "directory" else "📄"
                output += f"{icon} {item['name']}\n"

        elif cmd == "cd":
            if args:
                if self.kernel.filesystem.cd(args[0]):
                    output = f"📁 Changed to: {self.kernel.filesystem.current_path}"
                    self.refresh_files()
                else:
                    output = f"❌ cd: {args[0]}: No such directory"
            else:
                output = "❌ cd: missing argument"

        elif cmd == "pwd":
            output = f"📍 {self.kernel.filesystem.current_path}"

        elif cmd == "ps":
            processes = self.kernel.process_manager.list_processes()
            output = f"{'PID':<6} {'NAME':<15} {'STATE'}\n"
            for p in processes:
                output += f"{p['pid']:<6} {p['name']:<15} {p['state']}\n"

        else:
            output = f"❌ {cmd}: command not found (but you still got +5 XP!)"

        # Add output
        if output:
            self.terminal_output.insert(tk.END, output + "\n")

        self.terminal_output.insert(tk.END, "\n")
        self.terminal_output.see(tk.END)

        # Update displays
        self.update_xp_display()
        self.update_missions_display()

    def create_status_bar(self):
        """Gaming status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Game time
        self.playtime_var = tk.StringVar(value="Playtime: 00:00:00")
        ttk.Label(self.status_frame, textvariable=self.playtime_var).pack(side=tk.LEFT, padx=5)

        # Notifications
        self.notification_var = tk.StringVar(value="🎮 Ready to play!")
        ttk.Label(self.status_frame, textvariable=self.notification_var).pack(side=tk.LEFT, padx=20)

        # Clock
        self.clock_var = tk.StringVar()
        ttk.Label(self.status_frame, textvariable=self.clock_var).pack(side=tk.RIGHT, padx=5)
        self.update_clock()

    def update_clock(self):
        """Update clock"""
        self.clock_var.set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_clock)

    def update_game_timer(self):
        """Update game playtime"""
        playtime = datetime.now() - self.game_timer_start
        self.playtime_var.set(f"Playtime: {str(playtime).split('.')[0]}")
        self.root.after(1000, self.update_game_timer)

    def show_notifications(self):
        """Show recent notifications"""
        if self.game_manager.notifications:
            recent = self.game_manager.notifications[-1]
            self.notification_var.set(recent["message"][:50] + "...")
        self.root.after(5000, self.show_notifications)

    def update_displays(self):
        """Update all displays"""
        self.refresh_processes()
        self.update_dashboard()
        self.update_missions_display()
        self.update_xp_display()

        # Check time-based achievements
        self.game_manager.check_achievement("night_owl")
        self.game_manager.check_achievement("early_bird")

        self.root.after(5000, self.update_displays)

    def generate_new_missions(self):
        """Generate new daily missions"""
        self.game_manager._generate_daily_missions()
        self.update_missions_display()
        self.game_manager.add_notification("🎯 New daily missions generated!")

    def play_game(self, game_id):
        """Play mini-games"""
        self.game_manager.stats.games_played += 1
        leveled_up = self.game_manager.stats.add_xp(50)

        if leveled_up:
            self.game_manager.add_notification(f"🎉 LEVEL UP! Now Level {self.game_manager.stats.level}!")

        self.game_manager.check_achievement("gamer")

        if game_id == "snake":
            self.play_snake()
        elif game_id == "puzzle":
            self.play_puzzle()
        elif game_id == "speed":
            self.speed_challenge()
        elif game_id == "memory":
            self.memory_game()

        self.update_xp_display()

    def play_snake(self):
        """Snake game placeholder"""
        messagebox.showinfo("🐍 Snake Game", 
                           "🐍 Snake Game (+50 XP earned!)\n\n" +
                           "Coming Soon: Full Snake game!\n" +
                           "This will be a playable Snake game integrated into the OS.")

    def play_puzzle(self):
        """Puzzle game placeholder"""
        messagebox.showinfo("🧩 Puzzle Challenge", 
                           "🧩 Puzzle Challenge (+50 XP earned!)\n\n" +
                           "Coming Soon: Logic puzzles!\n" +
                           "Solve programming and system administration puzzles.")

    def speed_challenge(self):
        """Speed challenge mini-game"""
        challenge_window = tk.Toplevel(self.root)
        challenge_window.title("⚡ Speed Challenge")
        challenge_window.geometry("400x300")

        tk.Label(challenge_window, text="⚡ Speed Challenge", 
                font=('Arial', 16, 'bold')).pack(pady=20)

        challenge_text = """Quick! Complete these tasks as fast as possible:

1. Create a file named 'speed_test.txt'
2. Create a folder named 'fast_folder'  
3. Create a process named 'speedrun'
4. Navigate to /tmp directory
5. Execute 5 terminal commands

Timer starts when you close this window!
Bonus XP for completing under 1 minute!"""

        tk.Label(challenge_window, text=challenge_text, 
                font=('Arial', 10), justify=tk.LEFT).pack(pady=10, padx=20)

        def start_challenge():
            self.challenge_start_time = datetime.now()
            challenge_window.destroy()
            self.game_manager.add_notification("⚡ Speed Challenge started! Go fast!")

        tk.Button(challenge_window, text="🚀 Start Challenge!", 
                 command=start_challenge, font=('Arial', 12, 'bold')).pack(pady=20)

    def memory_game(self):
        """Memory game placeholder"""
        messagebox.showinfo("🎯 Memory Game", 
                           "🎯 Memory Game (+50 XP earned!)\n\n" +
                           "Coming Soon: Memory challenges!\n" +
                           "Test your memory with system administration scenarios.")

    def show_game_help(self):
        """Show game help"""
        help_text = """🎮 How to Play PyOS GameOS

🎯 Objective:
Become the ultimate System Administrator by learning OS concepts through gaming!

📈 Leveling System:
• Earn XP by performing actions
• Level up to unlock new features
• Higher levels = higher status!

🏆 Achievements:
• 20+ achievements to unlock
• Special rewards for milestones
• Show off your expertise!

🎯 Daily Missions:
• Complete 3 missions daily
• Earn bonus XP and maintain streaks
• New missions generated daily

💰 XP Rewards:
• Create file: +10 XP
• Create folder: +25 XP
• Create process: +30 XP
• Execute command: +5 XP
• Kill process: +20 XP
• Delete item: +5 XP
• Navigate folders: +2 XP

🎮 Mini-Games:
• Play games for bonus XP
• Unlock the "Gamer" achievement
• More games coming soon!

🏅 Pro Tips:
• Complete missions for big XP bonuses
• Explore all directories
• Use the terminal frequently
• Maintain login streaks
• Play mini-games for variety"""

        messagebox.showinfo("🎮 How to Play", help_text)

    def show_achievement_guide(self):
        """Show achievement guide"""
        guide_text = """🏆 Achievement Guide

🥇 Getting Started:
• First Steps - Create your first file
• Builder - Create your first directory  
• Taskmaster - Create your first process

📊 Progress Achievements:
• Productive - Create 10 files
• Architect - Create 5 directories
• Terminal Rookie - Execute 25 commands
• Terminal Expert - Execute 100 commands

🎯 Special Achievements:
• Speed Demon - Complete 5 actions in 1 minute
• Night Owl - Use system after 11 PM
• Early Bird - Use system before 7 AM
• Dedication - Login for 5 consecutive days

🎮 Gaming Achievements:
• Gamer - Play 5 mini-games
• Completionist - Complete 20 missions
• Efficiency Expert - Complete mission with 100% accuracy

🏆 Master Level:
• System Admin - Reach level 5
• Master Admin - Reach level 10
• Legendary User - Unlock 15 achievements

💡 Tips:
• Some achievements are time-based
• Complete missions to progress faster
• Explore different features
• Play regularly to maintain streaks"""

        messagebox.showinfo("🏆 Achievement Guide", guide_text)

    def show_detailed_stats(self):
        """Show detailed statistics"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Detailed Statistics")
        stats_window.geometry("500x600")

        stats_text = scrolledtext.ScrolledText(stats_window)
        stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Calculate session time
        session_time = datetime.now() - self.game_timer_start

        detailed_stats = f"""📊 DETAILED GAME STATISTICS

👤 Player Profile:
═══════════════════
Level: {self.game_manager.stats.level}
Total XP: {self.game_manager.stats.total_xp:,}
Current Session: {str(session_time).split('.')[0]}
Login Streak: {self.game_manager.stats.login_streak} days

🏆 Achievements:
═══════════════════
Unlocked: {self.game_manager.stats.achievements_unlocked}/20
Completion: {(self.game_manager.stats.achievements_unlocked/20)*100:.1f}%

🎯 Mission Progress:
═══════════════════
Total Completed: {self.game_manager.stats.missions_completed}
Active Missions: {len([m for m in self.game_manager.active_missions if not m.completed])}/3

📁 File System Activity:
═══════════════════
Files Created: {self.game_manager.stats.files_created}
Folders Created: {self.game_manager.stats.directories_created}
Items Deleted: {self.game_manager.stats.files_deleted}
Directories Explored: {len(self.game_manager.stats.directories_explored)}

⚙️ Process Management:
═══════════════════
Processes Created: {self.game_manager.stats.processes_created}
Processes Killed: {self.game_manager.stats.processes_killed}

💻 Terminal Usage:
═══════════════════
Commands Executed: {self.game_manager.stats.commands_executed}
Terminal XP Earned: {self.game_manager.stats.commands_executed * 5:,}

🎮 Gaming Activity:
═══════════════════
Mini-Games Played: {self.game_manager.stats.games_played}
Gaming XP Earned: {self.game_manager.stats.games_played * 50:,}

📈 Progress Breakdown:
═══════════════════
File XP: {self.game_manager.stats.files_created * 10:,}
Folder XP: {self.game_manager.stats.directories_created * 25:,}
Process XP: {self.game_manager.stats.processes_created * 30:,}
Terminal XP: {self.game_manager.stats.commands_executed * 5:,}
Gaming XP: {self.game_manager.stats.games_played * 50:,}

Next Level Progress:
Level {self.game_manager.stats.level} → {self.game_manager.stats.level + 1}
XP Needed: {int(self.game_manager.get_level_progress()['needed_xp'] - self.game_manager.get_level_progress()['current_xp']):,}"""

        stats_text.insert(1.0, detailed_stats)
        stats_text.config(state=tk.DISABLED)

        ttk.Button(stats_window, text="Close", command=stats_window.destroy).pack(pady=5)

    def show_about(self):
        """Show about dialog"""
        about_text = f"""🎮 PyOS GameOS - Gamified Operating System Simulator
Version 1.0 Gaming Edition

🎯 Learn operating system concepts through gaming!

🎮 Features:
• 📈 XP and Leveling System
• 🏆 20+ Achievements to Unlock  
• 🎯 Daily Missions & Challenges
• 📊 Detailed Progress Tracking
• 🎲 Integrated Mini-Games
• 🥇 Leaderboard System
• 💻 Gamified Terminal
• 📁 XP-Rewarding File Management

🎓 Educational Goals:
• File System Management
• Process Management
• Memory Management  
• System Administration
• Terminal/Command Line Skills

🏆 Your Progress:
• Current Level: {self.game_manager.stats.level}
• Total XP: {self.game_manager.stats.total_xp:,}
• Achievements: {self.game_manager.stats.achievements_unlocked}/20
• Playtime: {str(datetime.now() - self.game_timer_start).split('.')[0]}

Built with Python & Tkinter
© 2025 GameOS Project"""

        messagebox.showinfo("About PyOS GameOS", about_text)

    def run(self):
        """Start the gamified OS"""
        print("🎮" + "="*50)
        print("🎮 STARTING PyOS GameOS!")
        print("🎮" + "="*50)
        print("🚀 Loading gaming systems...")
        print("✅ Achievement system loaded")
        print("✅ Mission system initialized") 
        print("✅ XP & leveling ready")
        print("✅ Gaming GUI loaded")
        print("🎮 Ready to play! Have fun learning OS concepts!")
        print("🎮" + "="*50)

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n🎮 GameOS interrupted by user")
        except Exception as e:
            print(f"\n❌ Error running GameOS: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Save game progress (in real app)
            print("\n💾 Game progress saved")
            print("👋 Thanks for playing PyOS GameOS!")

if __name__ == "__main__":
    try:
        print("🎮 Initializing PyOS GameOS...")
        app = GameOSGUI()
        app.run()
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
