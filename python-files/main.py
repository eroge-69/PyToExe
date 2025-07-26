import os
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, filedialog, ttk
import webbrowser
import threading
import requests
from bs4 import BeautifulSoup
import datetime
import random
from PIL import Image, ImageTk
from io import BytesIO

class FEMUBOT:
    def __init__(self, root):
        self.root = root
        self.root.title("EGO A TRAINABLE BOT")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Set icon and styling
        # Set icon if available
        if os.path.exists("C:/Users/PC/Downloads/Techarise.png"):
            try:
                from PIL import Image, ImageTk
                img = Image.open("C:/Users/PC/Downloads/Techarise.png")
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(False, photo)
            except Exception as e:
                print(f"Failed to load logo image: {e}")
        elif os.path.exists("femubot_icon.ico"):
            self.root.iconbitmap(default="femubot_icon.ico")
        
        # Knowledge base file
        self.knowledge_file = "knowledge_base.json"
        
        # Load knowledge base
        self.knowledge_base = self.load_knowledge_base()
        
        # Training mode password
        self.train_password = "techarise2025$"
        
        # Create GUI elements
        self.create_widgets()
        
        # Welcome message
        self.display_bot_message("Welcome to EGO A TRAINABLE BOT! I'm here to assist you. Type 'help' to see available commands.")
        self.display_bot_message("Developer Credits: HORACE KALENGA  CONTACT :hkalenga48@gmail.com")
    
    def create_widgets(self):
        # Chat display area
        self.chat_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(self.chat_frame, wrap=tk.WORD, bg="white", fg="black", font=("Arial", 10))
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Input area
        self.input_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.user_input = tk.Entry(self.input_frame, font=("Arial", 12), bg="white", fg="black")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.process_input)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.process_input, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.send_button.pack(side=tk.RIGHT, padx=5)
        
        # Menu bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="Enter Training Mode", command=self.enter_training_mode)
        self.tools_menu.add_command(label="Web Search", command=self.web_search_dialog)
        
        # Initialize training mode flag
        self.in_training_mode = False
        
        # Web Search menu
        self.websearch_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Web Search", menu=self.websearch_menu)
        self.websearch_menu.add_command(label="Generate Text", command=self.text_generation_dialog)
        self.websearch_menu.add_command(label="Generate Image", command=self.image_generation_dialog)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Commands", command=self.show_commands)
        self.help_menu.add_command(label="About", command=self.show_about)
    
    def load_knowledge_base(self):
        """Load the knowledge base from file or create a new one if it doesn't exist"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r') as f:
                    return json.load(f)
            except:
                return {"responses": {}, "patterns": {}}
        else:
            # Create default knowledge base
            default_kb = {
                "responses": {
                    "greeting": ["Hello!", "Hi there!", "Greetings!", "Hello, how can I help you today?"],
                    "goodbye": ["Goodbye!", "See you later!", "Bye!", "Have a great day!"],
                    "thanks": ["You're welcome!", "Happy to help!", "Anytime!", "My pleasure!"],
                    "help": ["I can answer questions, search the web, and learn new responses. Type 'commands' to see all available commands."],
                    "name": ["I am FEMUBOT, your AI assistant.", "My name is FEMUBOT.", "I'm FEMUBOT, created by HORACE KALENGA & FEMU EDUCATIONAL SUCCESS."],
                    "commands": ["Available commands:\n- 'train': Enter training mode (password required)\n- 'search [query]': Search the web\n- 'help': Show help information\n- 'clear': Clear the chat\n- 'exit': Exit the application"],
                    "about": ["I'm FEMUBOT, a trainable chatbot created by HORACE KALENGA & FEMU EDUCATIONAL SUCCESS. I can learn from our conversations and search the web for information."],
                    "weather": ["I can search the web for weather information. Try typing 'search weather in [your location]'."],
                    "time": ["I don't have access to the current time directly, but I can search the web for time information."],
                    "capabilities": ["I can chat with you, learn from our conversations in training mode, and search the web for information. I'm designed to be helpful and informative."],
                    "creator": ["I was created by HORACE KALENGA & FEMU EDUCATIONAL SUCCESS."],
                    "purpose": ["My purpose is to assist users by providing information, answering questions, and learning from interactions to become more helpful over time."]
                },
                "patterns": {
                    "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"],
                    "goodbye": ["bye", "goodbye", "see you", "exit", "quit"],
                    "thanks": ["thank you", "thanks", "appreciate it", "thank"],
                    "help": ["help", "assist", "support", "guide"],
                    "name": ["who are you", "what's your name", "what are you", "your name"],
                    "commands": ["commands", "what can you do", "functions", "capabilities"],
                    "about": ["about you", "tell me about yourself", "your background"],
                    "weather": ["weather", "forecast", "temperature", "rain", "sunny"],
                    "time": ["time", "current time", "what time", "clock"],
                    "capabilities": ["abilities", "features", "what can you do", "skills"],
                    "creator": ["who made you", "who created you", "your creator", "your developer"],
                    "purpose": ["why were you made", "what is your purpose", "why do you exist", "what are you for"]
                }
            }
            self.save_knowledge_base(default_kb)
            return default_kb
    
    def save_knowledge_base(self, knowledge_base=None):
        """Save the knowledge base to file"""
        if knowledge_base is None:
            knowledge_base = self.knowledge_base
        
        with open(self.knowledge_file, 'w') as f:
            json.dump(knowledge_base, f, indent=4)
    
    def display_bot_message(self, message):
        """Display a message from the bot in the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"EGO A TRAINABLE BOT: {message}\n\n", "bot")
        self.chat_display.tag_configure("bot", foreground="#0066CC", font=("Arial", 10, "bold"))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_user_message(self, message):
        """Display a message from the user in the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"You: {message}\n\n", "user")
        self.chat_display.tag_configure("user", foreground="#006600", font=("Arial", 10))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.display_bot_message("Chat cleared.")
    
    def process_input(self, event=None):
        """Process user input and generate a response"""
        user_input = self.user_input.get().strip()
        if not user_input:
            return
        
        self.display_user_message(user_input)
        self.user_input.delete(0, tk.END)
        
        # Process commands
        if user_input.lower() == "exit":
            self.root.quit()
            return
        elif user_input.lower() == "clear":
            self.clear_chat()
            return
        elif user_input.lower() == "train":
            self.enter_training_mode()
            return
        elif user_input.lower().startswith("search "):
            query = user_input[7:].strip()
            if query:
                self.web_search(query)
            else:
                self.display_bot_message("Please provide a search query.")
            return
        elif user_input.lower().startswith("generate text "):
            prompt = user_input[14:].strip()
            if prompt:
                self.generate_text(prompt)
            else:
                self.display_bot_message("Please provide a prompt for text generation.")
            return
        elif user_input.lower().startswith("generate image "):
            prompt = user_input[15:].strip()
            if prompt:
                self.generate_image(prompt)
            else:
                self.display_bot_message("Please provide a prompt for image generation.")
            return
        elif user_input.lower() == "view knowledge":
            # Only allow in training mode
            if self.in_training_mode:
                self.view_knowledge_base()
            else:
                self.display_bot_message("Knowledge base can only be accessed in training mode. Type 'train' to enter training mode.")
            return
        elif user_input.lower().startswith("search knowledge "):
            # Only allow in training mode
            if self.in_training_mode:
                query = user_input[16:].strip()
                if query:
                    self.search_knowledge_base(query)
                else:
                    self.display_bot_message("Please provide a search term for the knowledge base.")
            else:
                self.display_bot_message("Knowledge base can only be accessed in training mode. Type 'train' to enter training mode.")
            return
        
        # Generate response
        response = self.generate_response(user_input)
        self.display_bot_message(response)
    
    def generate_response(self, user_input):
        """Generate a response based on user input"""
        user_input = user_input.lower()
        
        # Check for pattern matches in knowledge base
        for intent, patterns in self.knowledge_base["patterns"].items():
            for pattern in patterns:
                if pattern in user_input:
                    responses = self.knowledge_base["responses"].get(intent, [])
                    if responses:
                        return random.choice(responses)
        
        # If no pattern matches, check for direct matches in responses
        for key in self.knowledge_base["responses"]:
            if key.lower() in user_input:
                return random.choice(self.knowledge_base["responses"][key])
        
        # Default response if no match found
        return "I don't have information about that yet. You can teach me in training mode or try a web search."
    
    def enter_training_mode(self):
        """Enter training mode with password protection"""
        password = simpledialog.askstring("Password Required", "Enter password to access training mode:", show='*')
        if password == self.train_password:
            self.display_bot_message("Training mode activated. You can now teach me new responses.")
            self.in_training_mode = True
            
            # Create Knowledge Base menu when in training mode
            self.kb_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Knowledge Base", menu=self.kb_menu)
            self.kb_menu.add_command(label="Upload Text File", command=self.upload_text_file)
            self.kb_menu.add_command(label="View Knowledge Base", command=self.view_knowledge_base)
            self.kb_menu.add_command(label="Search Knowledge Base", command=self.search_knowledge_base)
            self.kb_menu.add_command(label="Export Knowledge Base", command=self.export_knowledge_base)
            self.kb_menu.add_command(label="Import Knowledge Base", command=self.import_knowledge_base)
            self.kb_menu.add_command(label="Edit Knowledge Base", command=self.edit_knowledge_base)
            
            self.train_bot()
        else:
            self.display_bot_message("Incorrect password. Access denied.")
    
    def train_bot(self):
        """Train the bot with new patterns and responses"""
        # Create training dialog
        train_window = tk.Toplevel(self.root)
        train_window.title("FEMUBOT Training Mode")
        train_window.geometry("600x400")
        train_window.configure(bg="#f0f0f0")
        
        # Training form
        tk.Label(train_window, text="Train FEMUBOT", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)
        
        # Intent frame
        intent_frame = tk.Frame(train_window, bg="#f0f0f0")
        intent_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(intent_frame, text="Intent/Category:", bg="#f0f0f0").pack(side=tk.LEFT)
        intent_entry = tk.Entry(intent_frame, width=30)
        intent_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Pattern frame
        pattern_frame = tk.Frame(train_window, bg="#f0f0f0")
        pattern_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(pattern_frame, text="Pattern (trigger words):", bg="#f0f0f0").pack(side=tk.LEFT)
        pattern_entry = tk.Entry(pattern_frame, width=30)
        pattern_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Response frame
        response_frame = tk.Frame(train_window, bg="#f0f0f0")
        response_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(response_frame, text="Response:", bg="#f0f0f0").pack(side=tk.LEFT)
        response_entry = tk.Entry(response_frame, width=30)
        response_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Status label
        status_label = tk.Label(train_window, text="", bg="#f0f0f0", fg="#006600")
        status_label.pack(pady=10)
        
        # Function to add training data
        def add_training_data():
            intent = intent_entry.get().strip()
            pattern = pattern_entry.get().strip().lower()
            response = response_entry.get().strip()
            
            if not intent or not pattern or not response:
                status_label.config(text="All fields are required!", fg="#CC0000")
                return
            
            # Add to knowledge base
            if intent not in self.knowledge_base["patterns"]:
                self.knowledge_base["patterns"][intent] = []
            
            if intent not in self.knowledge_base["responses"]:
                self.knowledge_base["responses"][intent] = []
            
            if pattern not in self.knowledge_base["patterns"][intent]:
                self.knowledge_base["patterns"][intent].append(pattern)
            
            if response not in self.knowledge_base["responses"][intent]:
                self.knowledge_base["responses"][intent].append(response)
            
            # Save knowledge base
            self.save_knowledge_base()
            
            # Clear entries and show success message
            intent_entry.delete(0, tk.END)
            pattern_entry.delete(0, tk.END)
            response_entry.delete(0, tk.END)
            status_label.config(text="Training data added successfully!", fg="#006600")
        
        # Add button
        add_button = tk.Button(train_window, text="Add Training Data", command=add_training_data, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        add_button.pack(pady=10)
        
        # Close button
        close_button = tk.Button(train_window, text="Close Training Mode", command=lambda: self.close_training_mode(train_window), bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        close_button.pack(pady=5)
    
    def close_training_mode(self, train_window):
        """Close training mode and remove Knowledge Base menu"""
        train_window.destroy()
        
        # Remove Knowledge Base menu
        try:
            self.menu_bar.delete("Knowledge Base")
        except:
            pass
        
        self.in_training_mode = False
        self.display_bot_message("Training mode deactivated.")
    
    def web_search_dialog(self):
        """Open a dialog for web search"""
        query = simpledialog.askstring("Web Search", "Enter search query:")
        if query:
            self.web_search(query)
    
    def web_search(self, query):
        """Perform a web search and display results"""
        self.display_bot_message(f"Searching the web for: {query}")
        
        # Start search in a separate thread to avoid freezing the UI
        threading.Thread(target=self._perform_web_search, args=(query,), daemon=True).start()
    
    def _perform_web_search(self, query):
        """Perform the actual web search and display results"""
        try:
            # Format query for URL
            search_query = query.replace(' ', '+')
            url = f"https://www.google.com/search?q={search_query}"
            
            # Send request with headers to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract search results
                search_results = []
                
                # Get search result divs
                results = soup.find_all('div', class_='g')
                
                for result in results[:3]:  # Limit to first 3 results
                    title_element = result.find('h3')
                    if title_element:
                        title = title_element.text
                        
                        # Find the URL
                        link_element = result.find('a')
                        link = link_element['href'] if link_element and 'href' in link_element.attrs else ""
                        
                        # Find the description
                        desc_element = result.find('div', class_='VwiC3b')
                        description = desc_element.text if desc_element else "No description available"
                        
                        search_results.append({
                            "title": title,
                            "link": link,
                            "description": description
                        })
                
                # Display results
                if search_results:
                    result_text = "Here are the top results:\n\n"
                    for i, result in enumerate(search_results, 1):
                        result_text += f"{i}. {result['title']}\n"
                        result_text += f"   {result['description']}\n"
                        if result['link'].startswith('http'):
                            result_text += f"   Link: {result['link']}\n\n"
                    
                    # Update UI from main thread
                    self.root.after(0, lambda: self.display_bot_message(result_text))
                else:
                    self.root.after(0, lambda: self.display_bot_message("No results found. Try a different search query."))
            else:
                self.root.after(0, lambda: self.display_bot_message(f"Error: Unable to perform search. Status code: {response.status_code}"))
        
        except Exception as e:
            self.root.after(0, lambda: self.display_bot_message(f"Error performing web search: {str(e)}"))
    
    def show_commands(self):
        """Show available commands"""
        commands = """
Available Commands:
- 'train': Enter training mode (password required)
- 'search [query]': Search the web
- 'generate text [prompt]': Generate text using Web Search
- 'generate image [prompt]': Generate image using Web Search
- 'help': Show help information
- 'clear': Clear the chat
- 'exit': Exit the application

You can also use the menus at the top of the window to access these features.
        """
        self.display_bot_message(commands)
    
    def show_about(self):
        """Show about information"""
        about_text = """
FEMUBOT - AI Assistant

Version: 2.0
Developer Credits: HORACE KALENGA & FEMU EDUCATIONAL SUCCESS

FEMUBOT is a trainable chatbot that can learn from user interactions,
search the web for information, and generate text and images using
Web Search APIs.

© 2025 FEMU EDUCATIONAL SUCCESS. All rights reserved.
        """
        messagebox.showinfo("About FEMUBOT", about_text)


    # Web Search Text Generation
    def text_generation_dialog(self):
        """Open a dialog for text generation"""
        prompt = simpledialog.askstring("Text Generation", "Enter prompt for text generation:")
        if prompt:
            self.generate_text(prompt)
    
    def generate_text(self, prompt):
        """Generate text using Web Search API"""
        self.display_bot_message(f"Generating text for prompt: {prompt}")
        
        # Start generation in a separate thread to avoid freezing the UI
        threading.Thread(target=self._perform_text_generation, args=(prompt,), daemon=True).start()
    
    def _perform_text_generation(self, prompt):
        """Perform the actual text generation and display results"""
        try:
            # Format prompt for URL
            formatted_prompt = prompt.replace(' ', '%20')
            url = f"https://text.pollinations.ai/{formatted_prompt}"
            
            # Send request
            response = requests.get(url)
            
            if response.status_code == 200:
                # Display the generated text
                generated_text = response.text
                self.root.after(0, lambda: self.display_bot_message(f"Generated Text:\n\n{generated_text}"))
            else:
                self.root.after(0, lambda: self.display_bot_message(f"Error: Unable to generate text. Status code: {response.status_code}"))
        
        except Exception as e:
            self.root.after(0, lambda: self.display_bot_message(f"Error generating text: {str(e)}"))
    
    # Web Search Image Generation
    def image_generation_dialog(self):
        """Open a dialog for image generation"""
        prompt = simpledialog.askstring("Image Generation", "Enter prompt for image generation:")
        if prompt:
            self.generate_image(prompt)
    
    def generate_image(self, prompt):
        """Generate image using Web Search API"""
        self.display_bot_message(f"Generating image for prompt: {prompt}")
        
        # Start generation in a separate thread to avoid freezing the UI
        threading.Thread(target=self._perform_image_generation, args=(prompt,), daemon=True).start()
    
    def _perform_image_generation(self, prompt):
        """Perform the actual image generation and display results"""
        try:
            # Format prompt for URL
            formatted_prompt = prompt.replace(' ', '%20')
            url = f"https://image.pollinations.ai/prompt/{formatted_prompt}"
            
            # Send request
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                # Create a new window to display the image
                self.root.after(0, lambda: self._display_generated_image(response.content, prompt))
            else:
                self.root.after(0, lambda: self.display_bot_message(f"Error: Unable to generate image. Status code: {response.status_code}"))
        
        except Exception as e:
            self.root.after(0, lambda: self.display_bot_message(f"Error generating image: {str(e)}"))
    
    def _display_generated_image(self, image_data, prompt):
        """Display the generated image in a new window"""
        try:
            # Create a new window
            img_window = tk.Toplevel(self.root)
            img_window.title(f"Generated Image: {prompt}")
            img_window.geometry("800x600")
            
            # Load the image
            img = Image.open(BytesIO(image_data))
            
            # Resize the image if it's too large
            max_width, max_height = 780, 500
            width, height = img.size
            if width > max_width or height > max_height:
                ratio = min(max_width/width, max_height/height)
                width = int(width * ratio)
                height = int(height * ratio)
                img = img.resize((width, height), Image.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Create a label to display the image
            img_label = tk.Label(img_window, image=photo)
            img_label.image = photo  # Keep a reference to avoid garbage collection
            img_label.pack(pady=10)
            
            # Add a save button
            save_button = tk.Button(img_window, text="Save Image",
                                   command=lambda: self._save_image(image_data),
                                   bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
            save_button.pack(pady=10)
            
            # Add a close button
            close_button = tk.Button(img_window, text="Close",
                                    command=img_window.destroy,
                                    bg="#f44336", fg="white", font=("Arial", 10, "bold"))
            close_button.pack(pady=5)
            
            # Display a message in the main chat
            self.display_bot_message("Image generated successfully! It's displayed in a new window.")
            
        except Exception as e:
            self.display_bot_message(f"Error displaying image: {str(e)}")
    
    def _save_image(self, image_data):
        """Save the generated image to a file"""
        try:
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                messagebox.showinfo("Success", f"Image saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    # Knowledge Base Management
    def upload_text_file(self):
        """Upload a text file to train the bot"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            # Process each line
            category = os.path.basename(file_path).split('.')[0]
            
            # Create training dialog
            train_window = tk.Toplevel(self.root)
            train_window.title("Process Training Data")
            train_window.geometry("600x400")
            train_window.configure(bg="#f0f0f0")
            
            # Category frame
            category_frame = tk.Frame(train_window, bg="#f0f0f0")
            category_frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(category_frame, text="Category:", bg="#f0f0f0").pack(side=tk.LEFT)
            category_entry = tk.Entry(category_frame, width=30)
            category_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            category_entry.insert(0, category)
            
            # Lines frame
            lines_frame = tk.Frame(train_window, bg="#f0f0f0")
            lines_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
            
            tk.Label(lines_frame, text="Lines to process:", bg="#f0f0f0").pack(anchor=tk.W)
            
            # Create a scrolled text widget to display the lines
            lines_text = scrolledtext.ScrolledText(lines_frame, wrap=tk.WORD, height=10)
            lines_text.pack(fill=tk.BOTH, expand=True, pady=5)
            
            # Insert the lines
            for line in content:
                lines_text.insert(tk.END, line)
            
            # Status label
            status_label = tk.Label(train_window, text="", bg="#f0f0f0", fg="#006600")
            status_label.pack(pady=10)
            
            # Function to process the lines
            def process_lines():
                category = category_entry.get().strip()
                if not category:
                    status_label.config(text="Category is required!", fg="#CC0000")
                    return
                
                lines = lines_text.get(1.0, tk.END).strip().split('\n')
                if not lines or all(not line.strip() for line in lines):
                    status_label.config(text="No lines to process!", fg="#CC0000")
                    return
                
                # Add to knowledge base
                if category not in self.knowledge_base["patterns"]:
                    self.knowledge_base["patterns"][category] = []
                
                if category not in self.knowledge_base["responses"]:
                    self.knowledge_base["responses"][category] = []
                
                # Process each line
                added_count = 0
                for line in lines:
                    line = line.strip()
                    if line:
                        # Add as both pattern and response
                        if line not in self.knowledge_base["patterns"][category]:
                            self.knowledge_base["patterns"][category].append(line)
                        
                        if line not in self.knowledge_base["responses"][category]:
                            self.knowledge_base["responses"][category].append(line)
                        
                        added_count += 1
                
                # Save knowledge base
                self.save_knowledge_base()
                
                # Show success message
                status_label.config(text=f"Added {added_count} entries to the knowledge base!", fg="#006600")
            
            # Process button
            process_button = tk.Button(train_window, text="Process Training Data", command=process_lines, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
            process_button.pack(pady=10)
            
            # Close button
            close_button = tk.Button(train_window, text="Close", command=train_window.destroy, bg="#f44336", fg="white", font=("Arial", 10, "bold"))
            close_button.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {str(e)}")
    
    def view_knowledge_base(self, search_term=None):
        """View the knowledge base"""
        # Create a new window
        kb_window = tk.Toplevel(self.root)
        kb_window.title("Knowledge Base Viewer")
        kb_window.geometry("800x600")
        
        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(kb_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs for patterns and responses
        patterns_frame = ttk.Frame(notebook)
        responses_frame = ttk.Frame(notebook)
        
        notebook.add(patterns_frame, text="Patterns")
        notebook.add(responses_frame, text="Responses")
        
        # Function to create a treeview
        def create_treeview(parent, data_type):
            # Create a frame for the treeview and scrollbar
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create the treeview
            tree = ttk.Treeview(frame, columns=("Category", "Value"), show="headings")
            tree.heading("Category", text="Category")
            tree.heading("Value", text="Value")
            tree.column("Category", width=150)
            tree.column("Value", width=600)
            
            # Add a scrollbar
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack the treeview and scrollbar
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Populate the treeview
            data = self.knowledge_base["patterns"] if data_type == "patterns" else self.knowledge_base["responses"]
            
            for category, values in data.items():
                for value in values:
                    # If search term is provided, only show matching entries
                    if search_term is None or search_term.lower() in value.lower() or search_term.lower() in category.lower():
                        tree.insert("", tk.END, values=(category, value))
            
            return tree
        
        # Create treeviews for patterns and responses
        patterns_tree = create_treeview(patterns_frame, "patterns")
        responses_tree = create_treeview(responses_frame, "responses")
        
        # Add a close button
        close_button = tk.Button(kb_window, text="Close",
                               command=kb_window.destroy,
                               bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        close_button.pack(pady=10)
        
        # If search term was provided, show a message
        if search_term:
            search_label = tk.Label(kb_window, text=f"Showing results for: '{search_term}'", font=("Arial", 10, "italic"))
            search_label.pack(before=close_button, pady=5)
    
    def search_knowledge_base(self, search_term=None):
        """Search the knowledge base"""
        if search_term is None:
            search_term = simpledialog.askstring("Search Knowledge Base", "Enter search term:")
        
        if search_term:
            self.view_knowledge_base(search_term)
        else:
            self.display_bot_message("Please provide a search term.")
    
    def export_knowledge_base(self):
        """Export the knowledge base to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.knowledge_base, f, indent=4)
                messagebox.showinfo("Success", f"Knowledge base exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export knowledge base: {str(e)}")
    
    def import_knowledge_base(self):
        """Import a knowledge base from a file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_kb = json.load(f)
                
                # Validate the imported knowledge base
                if "responses" not in imported_kb or "patterns" not in imported_kb:
                    messagebox.showerror("Error", "Invalid knowledge base format")
                    return
                
                # Ask if the user wants to merge or replace
                response = messagebox.askyesno("Import Options",
                                             "Do you want to merge with the existing knowledge base?\n\n"
                                             "Yes: Merge with existing knowledge base\n"
                                             "No: Replace the existing knowledge base")
                
                if response:  # Merge
                    # Merge patterns
                    for category, patterns in imported_kb["patterns"].items():
                        if category not in self.knowledge_base["patterns"]:
                            self.knowledge_base["patterns"][category] = []
                        
                        for pattern in patterns:
                            if pattern not in self.knowledge_base["patterns"][category]:
                                self.knowledge_base["patterns"][category].append(pattern)
                    
                    # Merge responses
                    for category, responses in imported_kb["responses"].items():
                        if category not in self.knowledge_base["responses"]:
                            self.knowledge_base["responses"][category] = []
                        
                        for response in responses:
                            if response not in self.knowledge_base["responses"][category]:
                                self.knowledge_base["responses"][category].append(response)
                    
                    messagebox.showinfo("Success", "Knowledge base merged successfully")
                else:  # Replace
                    self.knowledge_base = imported_kb
                    messagebox.showinfo("Success", "Knowledge base replaced successfully")
                
                # Save the knowledge base
                self.save_knowledge_base()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import knowledge base: {str(e)}")
    
    def edit_knowledge_base(self):
        """Edit the knowledge base directly"""
        # Create a new window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Knowledge Base")
        edit_window.geometry("800x600")
        
        # Create a notebook (tabbed interface)
        notebook = ttk.Notebook(edit_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs for patterns and responses
        patterns_frame = ttk.Frame(notebook)
        responses_frame = ttk.Frame(notebook)
        
        notebook.add(patterns_frame, text="Patterns")
        notebook.add(responses_frame, text="Responses")
        
        # Function to create an editable treeview
        def create_editable_treeview(parent, data_type):
            # Create a frame for the treeview and scrollbar
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create the treeview
            tree = ttk.Treeview(frame, columns=("Category", "Value"), show="headings")
            tree.heading("Category", text="Category")
            tree.heading("Value", text="Value")
            tree.column("Category", width=150)
            tree.column("Value", width=600)
            
            # Add a scrollbar
            scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Pack the treeview and scrollbar
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Populate the treeview
            data = self.knowledge_base["patterns"] if data_type == "patterns" else self.knowledge_base["responses"]
            
            for category, values in data.items():
                for value in values:
                    tree.insert("", tk.END, values=(category, value))
            
            # Add buttons for editing
            button_frame = ttk.Frame(parent)
            button_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Function to add a new entry
            def add_entry():
                category = simpledialog.askstring("Add Entry", "Enter category:")
                if not category:
                    return
                
                value = simpledialog.askstring("Add Entry", "Enter value:")
                if not value:
                    return
                
                # Add to treeview
                tree.insert("", tk.END, values=(category, value))
                
                # Add to knowledge base
                if data_type == "patterns":
                    if category not in self.knowledge_base["patterns"]:
                        self.knowledge_base["patterns"][category] = []
                    
                    if value not in self.knowledge_base["patterns"][category]:
                        self.knowledge_base["patterns"][category].append(value)
                else:
                    if category not in self.knowledge_base["responses"]:
                        self.knowledge_base["responses"][category] = []
                    
                    if value not in self.knowledge_base["responses"][category]:
                        self.knowledge_base["responses"][category].append(value)
                
                # Save knowledge base
                self.save_knowledge_base()
            
            # Function to edit an entry
            def edit_entry():
                selected = tree.selection()
                if not selected:
                    messagebox.showinfo("Edit Entry", "Please select an entry to edit")
                    return
                
                # Get current values
                current_values = tree.item(selected[0], "values")
                current_category = current_values[0]
                current_value = current_values[1]
                
                # Get new values
                new_category = simpledialog.askstring("Edit Entry", "Enter new category:", initialvalue=current_category)
                if not new_category:
                    return
                
                new_value = simpledialog.askstring("Edit Entry", "Enter new value:", initialvalue=current_value)
                if not new_value:
                    return
                
                # Update treeview
                tree.item(selected[0], values=(new_category, new_value))
                
                # Update knowledge base
                if data_type == "patterns":
                    # Remove old value
                    if current_category in self.knowledge_base["patterns"] and current_value in self.knowledge_base["patterns"][current_category]:
                        self.knowledge_base["patterns"][current_category].remove(current_value)
                    
                    # Add new value
                    if new_category not in self.knowledge_base["patterns"]:
                        self.knowledge_base["patterns"][new_category] = []
                    
                    if new_value not in self.knowledge_base["patterns"][new_category]:
                        self.knowledge_base["patterns"][new_category].append(new_value)
                else:
                    # Remove old value
                    if current_category in self.knowledge_base["responses"] and current_value in self.knowledge_base["responses"][current_category]:
                        self.knowledge_base["responses"][current_category].remove(current_value)
                    
                    # Add new value
                    if new_category not in self.knowledge_base["responses"]:
                        self.knowledge_base["responses"][new_category] = []
                    
                    if new_value not in self.knowledge_base["responses"][new_category]:
                        self.knowledge_base["responses"][new_category].append(new_value)
                
                # Save knowledge base
                self.save_knowledge_base()
            
            # Function to delete an entry
            def delete_entry():
                selected = tree.selection()
                if not selected:
                    messagebox.showinfo("Delete Entry", "Please select an entry to delete")
                    return
                
                # Get current values
                current_values = tree.item(selected[0], "values")
                current_category = current_values[0]
                current_value = current_values[1]
                
                # Confirm deletion
                if not messagebox.askyesno("Delete Entry", f"Are you sure you want to delete this entry?\n\nCategory: {current_category}\nValue: {current_value}"):
                    return
                
                # Remove from treeview
                tree.delete(selected[0])
                
                # Remove from knowledge base
                if data_type == "patterns":
                    if current_category in self.knowledge_base["patterns"] and current_value in self.knowledge_base["patterns"][current_category]:
                        self.knowledge_base["patterns"][current_category].remove(current_value)
                else:
                    if current_category in self.knowledge_base["responses"] and current_value in self.knowledge_base["responses"][current_category]:
                        self.knowledge_base["responses"][current_category].remove(current_value)
                
                # Save knowledge base
                self.save_knowledge_base()
            
            # Add buttons
            add_button = ttk.Button(button_frame, text="Add Entry", command=add_entry)
            add_button.pack(side=tk.LEFT, padx=5)
            
            edit_button = ttk.Button(button_frame, text="Edit Entry", command=edit_entry)
            edit_button.pack(side=tk.LEFT, padx=5)
            
            delete_button = ttk.Button(button_frame, text="Delete Entry", command=delete_entry)
            delete_button.pack(side=tk.LEFT, padx=5)
            
            return tree
        
        # Create editable treeviews for patterns and responses
        patterns_tree = create_editable_treeview(patterns_frame, "patterns")
        responses_tree = create_editable_treeview(responses_frame, "responses")
        
        # Add a save button
        save_button = tk.Button(edit_window, text="Save Changes",
                               command=lambda: self.save_knowledge_base(),
                               bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        save_button.pack(pady=5)
        
        # Add a close button
        close_button = tk.Button(edit_window, text="Close",
                               command=edit_window.destroy,
                               bg="#f44336", fg="white", font=("Arial", 10, "bold"))
        close_button.pack(pady=5)


if __name__ == "__main__":
    # Create main window
    root = tk.Tk()
    app = FEMUBOT(root)
    
    # Run the application
    root.mainloop()