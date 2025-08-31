import json
import urllib.request
import urllib.parse
import os
import time
from datetime import datetime
import random
import sys

# Your Gemini API Key
API_KEY = "AIzaSyCvS0k0PH1BNQ0Q15W7goDR2XraTKpXL-E"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class PureAIAssistant:
    def __init__(self):
        self.conversation_history = []
    
    def make_api_request(self, prompt):
        """Make direct API request to Gemini without external libraries"""
        try:
            # Prepare the request data
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
            
            # Convert to JSON
            json_data = json.dumps(data).encode('utf-8')
            
            # Create request
            req = urllib.request.Request(
                API_URL,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-goog-api-key': API_KEY
                }
            )
            
            # Make request
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['candidates'][0]['content']['parts'][0]['text']
                
        except Exception as e:
            return f"❌ API Error: {str(e)}"
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """Print cool ASCII banner"""
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'reset': '\033[0m'
        }
        
        banner = f"""
{colors['cyan']}╔═══════════════════════════════════════════════════════════════╗
║{colors['yellow']}                    🤖 AI COMMAND CENTER 🤖                    {colors['cyan']}║
║{colors['green']}                  Powered by Gemini 2.0 Flash                 {colors['cyan']}║
║{colors['purple']}                     Pure Python Edition                      {colors['cyan']}║
╚═══════════════════════════════════════════════════════════════╝{colors['reset']}
        """
        print(banner)
    
    def print_menu(self):
        """Print main menu options"""
        colors = {
            'blue': '\033[94m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'reset': '\033[0m'
        }
        
        menu = f"""
{colors['green']}🎯 Choose your mission:{colors['reset']}
{colors['blue']}[1]{colors['reset']} 💬 Chat with AI
{colors['blue']}[2]{colors['reset']} 🎲 Generate Random Story
{colors['blue']}[3]{colors['reset']} 🔍 Code Helper & Generator
{colors['blue']}[4]{colors['reset']} 📝 Writing Assistant
{colors['blue']}[5]{colors['reset']} 🧠 Math & Logic Solver
{colors['blue']}[6]{colors['reset']} 🎨 Creative Content Generator
{colors['blue']}[7]{colors['reset']} 🎮 Text Adventure Game
{colors['blue']}[8]{colors['reset']} 🔧 System & File Tools
{colors['blue']}[9]{colors['reset']} 🌟 Surprise Me!
{colors['red']}[0]{colors['reset']} 🚪 Exit

{colors['yellow']}Enter your choice: {colors['reset']}"""
        return input(menu)
    
    def typewriter_effect(self, text, speed=0.02):
        """Print text with typewriter effect"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(speed)
        print()
    
    def loading_animation(self, message="Processing"):
        """Show loading animation"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        for i in range(20):
            print(f'\r{chars[i % len(chars)]} {message}...', end='', flush=True)
            time.sleep(0.1)
        print('\r' + ' ' * 50 + '\r', end='')
    
    def chat_mode(self):
        """Interactive chat mode"""
        print("\n🤖 \033[96mEntering Chat Mode...\033[0m (type 'quit' to return)")
        print("─" * 60)
        
        while True:
            user_input = input("\n👤 \033[93mYou: \033[0m")
            if user_input.lower() in ['quit', 'exit', 'back']:
                break
            
            if user_input.strip():
                print("🤖 \033[96mAI:\033[0m ", end="")
                self.loading_animation("Thinking")
                response = self.make_api_request(user_input)
                self.typewriter_effect(response)
    
    def story_generator(self):
        """Generate random creative stories"""
        genres = ["sci-fi", "fantasy", "mystery", "horror", "romance", "adventure", "comedy"]
        settings = ["space station", "medieval castle", "modern city", "jungle", "underwater city", "desert", "mountains"]
        characters = ["detective", "wizard", "robot", "alien", "knight", "scientist", "thief", "princess"]
        
        genre = random.choice(genres)
        setting = random.choice(settings)
        character = random.choice(characters)
        
        print(f"\n🎲 \033[95mGenerating {genre} story...\033[0m")
        print(f"📍 Setting: {setting}")
        print(f"👤 Main character: {character}")
        print("─" * 50)
        
        prompt = f"""
        Write an engaging {genre} short story (about 300-500 words) featuring a {character} in a {setting}.
        Make it creative, with an interesting plot twist and vivid descriptions.
        Include dialogue and make it entertaining.
        """
        
        self.loading_animation("Creating story")
        response = self.make_api_request(prompt)
        print("\n📖 \033[92mYour Story:\033[0m")
        print("─" * 20)
        self.typewriter_effect(response, 0.03)
        
        input("\n📎 Press Enter to continue...")
    
    def code_helper(self):
        """Code generation and help"""
        print("\n💻 \033[94mCode Helper & Generator\033[0m")
        print("─" * 40)
        
        options = """
What do you need help with?
[1] Generate code from description
[2] Explain code concept
[3] Debug/fix code
[4] Best practices advice
[5] Algorithm implementation

Your choice: """
        
        choice = input(options)
        
        if choice == '1':
            description = input("Describe what you want to build: ")
            language = input("Programming language (Python/JavaScript/etc): ")
            prompt = f"Generate complete, working {language} code for: {description}. Include comments and example usage."
        
        elif choice == '2':
            concept = input("What programming concept to explain: ")
            prompt = f"Explain {concept} in programming with simple examples and practical use cases."
        
        elif choice == '3':
            print("Paste your code (type 'END' on new line when finished):")
            code_lines = []
            while True:
                line = input()
                if line.strip() == 'END':
                    break
                code_lines.append(line)
            code = '\n'.join(code_lines)
            prompt = f"Debug and fix this code, explain issues and provide corrected version:\n\n{code}"
        
        elif choice == '4':
            topic = input("What programming topic for best practices: ")
            prompt = f"Provide best practices and tips for {topic} programming."
        
        elif choice == '5':
            algorithm = input("Which algorithm to implement: ")
            prompt = f"Implement {algorithm} algorithm with detailed explanation and complexity analysis."
        
        else:
            print("❌ Invalid choice!")
            return
        
        self.loading_animation("Processing code request")
        response = self.make_api_request(prompt)
        print("\n💡 \033[92mCode Solution:\033[0m")
        print("─" * 20)
        print(response)
        
        input("\n📎 Press Enter to continue...")
    
    def writing_assistant(self):
        """Writing and text help"""
        print("\n✍️ \033[95mWriting Assistant\033[0m")
        print("─" * 30)
        
        tasks = [
            "Write a professional email",
            "Create a poem",
            "Draft a business proposal",
            "Write product description",
            "Create social media post",
            "Write a recipe",
            "Draft a letter",
            "Create a tutorial"
        ]
        
        print("Available writing tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"[{i}] {task}")
        
        try:
            choice = int(input("\nChoose task number: ")) - 1
            if 0 <= choice < len(tasks):
                topic = input(f"Topic/subject for '{tasks[choice]}': ")
                
                prompt = f"""
                {tasks[choice]} about: {topic}
                
                Make it professional, well-structured, and engaging.
                Include all necessary details and proper formatting.
                """
                
                self.loading_animation("Writing content")
                response = self.make_api_request(prompt)
                print(f"\n📝 \033[92m{tasks[choice]}:\033[0m")
                print("─" * 30)
                print(response)
            else:
                print("❌ Invalid choice!")
        
        except ValueError:
            print("❌ Please enter a valid number!")
        
        input("\n📎 Press Enter to continue...")
    
    def math_solver(self):
        """Math and logic problem solver"""
        print("\n🧮 \033[93mMath & Logic Solver\033[0m")
        print("─" * 30)
        
        problem = input("Enter your math problem or logic puzzle: ")
        
        prompt = f"""
        Solve this math/logic problem step by step: {problem}
        
        Provide:
        1. Clear step-by-step solution
        2. Explanation of methods used
        3. Final answer
        4. Alternative approaches if applicable
        5. How to verify the answer
        """
        
        self.loading_animation("Solving problem")
        response = self.make_api_request(prompt)
        print("\n🎯 \033[92mSolution:\033[0m")
        print("─" * 15)
        print(response)
        
        input("\n📎 Press Enter to continue...")
    
    def creative_generator(self):
        """Creative content generator"""
        print("\n🎨 \033[96mCreative Content Generator\033[0m")
        print("─" * 40)
        
        creative_types = [
            "Song lyrics", "Poem", "Joke collection", "Riddles",
            "Character backstory", "World description", "Dialogue script",
            "Product names", "Business ideas", "Art concepts"
        ]
        
        print("What would you like me to create?")
        for i, ctype in enumerate(creative_types, 1):
            print(f"[{i}] {ctype}")
        
        try:
            choice = int(input("\nChoice: ")) - 1
            if 0 <= choice < len(creative_types):
                theme = input(f"Theme/topic for {creative_types[choice]}: ")
                
                prompt = f"Create {creative_types[choice]} with theme: {theme}. Be creative, original, and engaging."
                
                self.loading_animation("Creating content")
                response = self.make_api_request(prompt)
                print(f"\n🌟 \033[92mYour {creative_types[choice]}:\033[0m")
                print("─" * 30)
                self.typewriter_effect(response)
            else:
                print("❌ Invalid choice!")
        
        except ValueError:
            print("❌ Please enter a valid number!")
        
        input("\n📎 Press Enter to continue...")
    
    def text_adventure(self):
        """Text-based adventure game"""
        print("\n🎮 \033[91mText Adventure Game Generator\033[0m")
        print("─" * 40)
        
        setting = input("Adventure setting (e.g., haunted mansion, space ship, jungle): ")
        
        prompt = f"""
        Create an interactive text adventure game set in: {setting}
        
        Include:
        1. Atmospheric description of the setting
        2. 3-4 different choices for the player
        3. Consequences for each choice
        4. Engaging narrative with some suspense
        5. An interesting challenge or puzzle
        
        Make it immersive and fun!
        """
        
        self.loading_animation("Building adventure")
        response = self.make_api_request(prompt)
        print(f"\n🗺️ \033[92mYour Adventure:\033[0m")
        print("─" * 20)
        self.typewriter_effect(response, 0.04)
        
        input("\n📎 Press Enter to continue...")
    
    def system_tools(self):
        """System and file utilities"""
        print("\n🔧 \033[94mSystem & File Tools\033[0m")
        print("─" * 30)
        
        print(f"🕒 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💻 Operating System: {os.name}")
        print(f"📁 Current Directory: {os.getcwd()}")
        print(f"🐍 Python Version: {sys.version}")
        
        # List files in current directory
        print(f"\n📂 Files in current directory:")
        try:
            files = os.listdir('.')
            for i, file in enumerate(files[:10], 1):  # Show first 10 files
                size = os.path.getsize(file) if os.path.isfile(file) else 0
                file_type = "📁" if os.path.isdir(file) else "📄"
                print(f"  {file_type} {file} ({size} bytes)")
            if len(files) > 10:
                print(f"  ... and {len(files)-10} more files")
        except:
            print("  ❌ Cannot list files")
        
        print(f"\n🔑 API Status: ✅ Connected to Gemini")
        print(f"🌐 No external dependencies needed!")
        
        input("\n📎 Press Enter to continue...")
    
    def surprise_me(self):
        """Random surprise feature"""
        surprises = [
            self.story_generator,
            self.creative_generator,
            lambda: self.random_fact(),
            lambda: self.daily_challenge(),
            lambda: self.wisdom_generator()
        ]
        
        surprise_func = random.choice(surprises)
        surprise_func()
    
    def random_fact(self):
        """Generate random interesting fact"""
        topics = ["science", "history", "nature", "technology", "space", "psychology"]
        topic = random.choice(topics)
        
        prompt = f"Share a fascinating and lesser-known fact about {topic}. Make it interesting and educational."
        
        print(f"\n🔮 \033[95mRandom {topic.title()} Fact:\033[0m")
        self.loading_animation("Finding interesting fact")
        response = self.make_api_request(prompt)
        print("─" * 30)
        self.typewriter_effect(response)
        
        input("\n📎 Press Enter to continue...")
    
    def daily_challenge(self):
        """Generate daily challenge"""
        challenges = ["coding", "creative writing", "logic puzzle", "learning", "productivity"]
        challenge_type = random.choice(challenges)
        
        prompt = f"Create a fun daily {challenge_type} challenge that someone can complete in 15-30 minutes."
        
        print(f"\n⚡ \033[93mDaily {challenge_type.title()} Challenge:\033[0m")
        self.loading_animation("Preparing challenge")
        response = self.make_api_request(prompt)
        print("─" * 30)
        print(response)
        
        input("\n📎 Press Enter to continue...")
    
    def wisdom_generator(self):
        """Generate wisdom/advice"""
        prompt = "Share an inspiring quote or piece of wisdom with explanation of why it's meaningful."
        
        print("\n💎 \033[96mDaily Wisdom:\033[0m")
        self.loading_animation("Gathering wisdom")
        response = self.make_api_request(prompt)
        print("─" * 20)
        self.typewriter_effect(response)
        
        input("\n📎 Press Enter to continue...")
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            choice = self.print_menu()
            
            if choice == '1':
                self.chat_mode()
            elif choice == '2':
                self.story_generator()
            elif choice == '3':
                self.code_helper()
            elif choice == '4':
                self.writing_assistant()
            elif choice == '5':
                self.math_solver()
            elif choice == '6':
                self.creative_generator()
            elif choice == '7':
                self.text_adventure()
            elif choice == '8':
                self.system_tools()
            elif choice == '9':
                self.surprise_me()
            elif choice == '0':
                print("\n👋 \033[92mThanks for using AI Command Center!\033[0m")
                print("🚀 \033[96mKeep exploring and stay curious!\033[0m")
                break
            else:
                print("\n❌ Invalid choice! Please try again.")
                time.sleep(2)

# Run the application
if __name__ == "__main__":
    print("🚀 Starting Pure Python AI Assistant...")
    print("📡 No external dependencies needed!")
    time.sleep(2)
    
    assistant = PureAIAssistant()
    assistant.run()