"""
🔥 GIGABYTE AI - COMPLETE MOBILE APPLICATION
===============================================
Advanced AI Assistant with Perfect Memory
Optimized for Mobile Development in Google Colab

FEATURES:
- Unlimited AI Conversations
- Perfect Memory & Context Awareness
- Mobile-Optimized Interface
- Dark Theme Design
- Persistent Storage
- Security Validation
- Touch-Friendly UI

GOOGLE COLAB SETUP:
1. Upload this file to Google Colab
2. Set your API key: os.environ['GEMINI_API_KEY'] = 'your_key_here'
3. Run: exec(open('GigaByte_AI_Complete.py').read())

REQUIREMENTS AUTO-INSTALLATION:
This file will automatically install all required dependencies
"""

import sys
import subprocess
import os
import importlib.util

# ============================================================================
# DEPENDENCY INSTALLER
# ============================================================================

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install all required dependencies"""
    print("🔥 Gigabyte AI - Checking Dependencies...")
    
    # Required packages with versions
    packages = {
        'google-generativeai': 'google-generativeai>=0.3.0',
        'bleach': 'bleach>=6.0.0',
        'kivy': 'kivy>=2.1.0',
        'kivymd': 'kivymd>=1.1.1',
        'python-dotenv': 'python-dotenv>=1.0.0',
        'requests': 'requests>=2.31.0'
    }
    
    # System dependencies for Kivy (Google Colab)
    print("📦 Installing system dependencies...")
    try:
        os.system("apt-get update -qq")
        os.system("apt-get install -y -qq python3-dev build-essential")
        os.system("apt-get install -y -qq libgl1-mesa-dev libgles2-mesa-dev")
        os.system("apt-get install -y -qq libegl1-mesa-dev libdrm-dev")
        os.system("apt-get install -y -qq libxkbcommon-dev libwayland-dev")
        os.system("apt-get install -y -qq libxinerama-dev libxcursor-dev")
        os.system("apt-get install -y -qq libxi-dev libxrandr-dev libasound2-dev")
    except:
        print("⚠️  System dependencies installation may have issues (continuing...)")
    
    # Install Python packages
    for package_name, package_spec in packages.items():
        try:
            # Check if package is already installed
            spec = importlib.util.find_spec(package_name.replace('-', '_'))
            if spec is None:
                print(f"📥 Installing {package_name}...")
                if install_package(package_spec):
                    print(f"✅ {package_name} installed successfully")
                else:
                    print(f"❌ Failed to install {package_name}")
            else:
                print(f"✅ {package_name} already installed")
        except Exception as e:
            print(f"⚠️  Issue with {package_name}: {e}")
    
    # Set Kivy environment variables
    os.environ['KIVY_WINDOW'] = 'sdl2'
    os.environ['KIVY_GL_BACKEND'] = 'gl'
    os.environ['KIVY_GRAPHICS'] = 'opengl'
    
    print("🎉 Dependencies setup complete!")
    print("=" * 50)

# Install dependencies first
check_and_install_dependencies()

# ============================================================================
# MAIN APPLICATION IMPORTS
# ============================================================================

import logging
import re
import json
from typing import Optional, Tuple, List, Dict
from datetime import datetime
import threading
import time

# Kivy imports
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.image import Image
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.metrics import dp
    from kivy.utils import get_color_from_hex
    from kivy.graphics import Color, Rectangle, RoundedRectangle
except ImportError as e:
    print(f"❌ Kivy import error: {e}")
    print("🔄 Trying to install Kivy again...")
    install_package("kivy>=2.1.0")
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.image import Image
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.metrics import dp
    from kivy.utils import get_color_from_hex
    from kivy.graphics import Color, Rectangle, RoundedRectangle

# AI imports
try:
    import google.generativeai as genai
    import bleach
except ImportError as e:
    print(f"❌ AI library import error: {e}")
    print("🔄 Installing AI libraries...")
    install_package("google-generativeai>=0.3.0")
    install_package("bleach>=6.0.0")
    import google.generativeai as genai
    import bleach

# ============================================================================
# CONFIGURATION AND LOGGING
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gigabyte_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration constants
MAX_PROMPT_LENGTH = int(os.getenv('MAX_PROMPT_LENGTH', '2000'))
MIN_PROMPT_LENGTH = int(os.getenv('MIN_PROMPT_LENGTH', '1'))
MAX_CONTEXT_MESSAGES = int(os.getenv('MAX_CONTEXT_MESSAGES', '10'))
CONVERSATION_FILE = "conversation_history.json"

# Mobile optimization - Set window size for mobile
Window.size = (360, 640)  # Mobile screen size
Window.clearcolor = get_color_from_hex('#1a1a1a')  # Dark theme

# Security patterns to block
SECURITY_PATTERNS = [
    r'exec\s*\(',
    r'eval\s*\(',
    r'__import__',
    r'import\s+os',
    r'subprocess',
    r'system\s*\(',
]

# ============================================================================
# AI MODEL CLASS
# ============================================================================

class AIModel:
    """AI Model handler for Gigabyte AI"""
    
    def __init__(self):
        self.model = None
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize Gigabyte AI model"""
        try:
            API_KEY = os.getenv('GEMINI_API_KEY')
            if not API_KEY:
                logger.error("AI API key not found in environment variables")
                return False
            
            genai.configure(api_key=API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gigabyte AI model initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gigabyte AI model: {str(e)}")
            return False
    
    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Validate and sanitize user prompt"""
        try:
            if not prompt or not prompt.strip():
                return False, "Prompt cannot be empty"
            
            # Check length constraints
            if len(prompt) > MAX_PROMPT_LENGTH:
                return False, f"Prompt too long. Maximum {MAX_PROMPT_LENGTH} characters allowed"
            
            if len(prompt) < MIN_PROMPT_LENGTH:
                return False, f"Prompt too short. Minimum {MIN_PROMPT_LENGTH} characters required"
            
            # Security check
            for pattern in SECURITY_PATTERNS:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return False, "Prompt contains potentially unsafe content"
            
            # Sanitize HTML
            sanitized_prompt = bleach.clean(prompt, tags=[], attributes={}, strip=True)
            
            if not sanitized_prompt.strip():
                return False, "Prompt cannot be empty or contain only whitespace"
            
            return True, sanitized_prompt
            
        except ValueError as e:
            return False, str(e)
    
    def build_context_prompt(self, current_prompt: str, messages: List[Dict]) -> str:
        """Build a context-aware prompt including conversation history"""
        if not messages:
            return current_prompt
        
        # Get recent messages for context
        recent_messages = messages[-MAX_CONTEXT_MESSAGES*2:]
        
        context_parts = [
            "You are Gigabyte AI, an advanced AI assistant with unlimited capabilities and access to our previous conversation history.",
            "You have no usage limits and can help with any request.",
            "Here is our conversation history:",
            ""
        ]
        
        for msg in recent_messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            if role == "user":
                context_parts.append(f"User ({timestamp}): {content}")
            elif role == "assistant":
                context_parts.append(f"Gigabyte AI ({timestamp}): {content}")
        
        context_parts.extend([
            "",
            f"Current User Question: {current_prompt}",
            "",
            "Instructions:",
            "- You are Gigabyte AI with unlimited usage capabilities",
            "- You can reference any part of our previous conversation",
            "- If the user asks about something we discussed before, provide specific details from our chat history",
            "- If the user asks 'what did I ask before?' or similar, summarize their previous questions",
            "- Maintain context and continuity from our previous interactions",
            "- Answer the current question while being aware of our conversation history",
            "- Always identify yourself as Gigabyte AI when asked about your identity",
            "- Keep responses concise and mobile-friendly"
        ])
        
        return "\n".join(context_parts)
    
    def generate_response(self, prompt: str, conversation_history: List[Dict] = None) -> Tuple[bool, str]:
        """Generate response using Gigabyte AI with conversation context"""
        try:
            if not self.model:
                return False, "Gigabyte AI model not initialized"
            
            # Build context-aware prompt if we have conversation history
            if conversation_history and len(conversation_history) > 0:
                context_prompt = self.build_context_prompt(prompt, conversation_history)
                logger.info(f"Generating response with context. Original prompt length: {len(prompt)}, Context prompt length: {len(context_prompt)}")
            else:
                context_prompt = prompt
                logger.info(f"Generating response without context for prompt length: {len(prompt)}")
            
            # Configure generation parameters for mobile
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=512,  # Reduced for mobile
            )
            
            # Generate content
            response = self.model.generate_content(
                context_prompt,
                generation_config=generation_config
            )
            
            # Check if response was generated successfully
            if not response or not response.text:
                logger.error("Empty response from Gigabyte AI")
                return False, "Failed to generate response"
            
            generated_text = response.text.strip()
            
            # Sanitize the response
            sanitized_response = bleach.clean(generated_text, tags=[], attributes={}, strip=True)
            
            return True, sanitized_response
            
        except Exception as e:
            logger.error(f"Gigabyte AI error: {str(e)}")
            
            # Handle specific API errors
            error_message = str(e).lower()
            
            if "quota" in error_message or "rate limit" in error_message:
                return False, "Gigabyte AI is processing many requests. Please try again in a moment."
            elif "invalid" in error_message or "bad request" in error_message:
                return False, "Invalid request to Gigabyte AI"
            else:
                return False, "Gigabyte AI is temporarily busy. Please try again."

# ============================================================================
# CONVERSATION MANAGER CLASS
# ============================================================================

class ConversationManager:
    """Manages conversation history and persistence"""
    
    @staticmethod
    def save_conversation_history(messages: List[Dict]) -> None:
        """Save conversation history to file"""
        try:
            conversation_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": messages
            }
            with open(CONVERSATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved conversation history with {len(messages)} messages")
        except Exception as e:
            logger.error(f"Failed to save conversation history: {str(e)}")
    
    @staticmethod
    def load_conversation_history() -> List[Dict]:
        """Load conversation history from file"""
        try:
            if os.path.exists(CONVERSATION_FILE):
                with open(CONVERSATION_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    messages = data.get("messages", [])
                    logger.info(f"Loaded conversation history with {len(messages)} messages")
                    return messages
            return []
        except Exception as e:
            logger.error(f"Failed to load conversation history: {str(e)}")
            return []
    
    @staticmethod
    def get_conversation_summary(messages: List[Dict]) -> Dict:
        """Get summary statistics of the conversation"""
        if not messages:
            return {"total_messages": 0, "user_messages": 0, "assistant_messages": 0}
        
        user_count = sum(1 for msg in messages if msg.get("role") == "user")
        assistant_count = sum(1 for msg in messages if msg.get("role") == "assistant")
        
        return {
            "total_messages": len(messages),
            "user_messages": user_count,
            "assistant_messages": assistant_count,
            "conversation_started": messages[0].get("timestamp", "Unknown") if messages else "No conversation"
        }

# ============================================================================
# CHAT MESSAGE WIDGET
# ============================================================================

class ChatMessage(BoxLayout):
    """Custom widget for chat messages"""
    
    def __init__(self, message: str, is_user: bool, timestamp: str = "", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(2)
        
        # Message container
        message_container = BoxLayout(orientation='horizontal', size_hint_y=None)
        message_container.bind(minimum_height=message_container.setter('height'))
        
        if is_user:
            # User message (right aligned, blue)
            message_container.add_widget(Label(size_hint_x=0.2))  # Spacer
            
            message_label = Label(
                text=message,
                text_size=(dp(250), None),
                halign='left',
                valign='top',
                color=get_color_from_hex('#FFFFFF'),
                size_hint_x=0.8,
                size_hint_y=None
            )
            message_label.bind(texture_size=message_label.setter('size'))
            
            # Background for user message
            message_bg = BoxLayout(
                size_hint_y=None,
                height=message_label.height + dp(10)
            )
            
            def update_bg(*args):
                message_bg.canvas.before.clear()
                with message_bg.canvas.before:
                    Color(*get_color_from_hex('#2196F3'))  # Blue
                    RoundedRectangle(
                        pos=message_bg.pos,
                        size=message_bg.size,
                        radius=[dp(10)]
                    )
            
            message_bg.bind(pos=update_bg, size=update_bg)
            Clock.schedule_once(update_bg, 0)
            
            message_bg.add_widget(message_label)
            message_container.add_widget(message_bg)
            
        else:
            # AI message (left aligned, dark gray)
            message_label = Label(
                text=f"🔥 Gigabyte AI:\n{message}",
                text_size=(dp(250), None),
                halign='left',
                valign='top',
                color=get_color_from_hex('#FFFFFF'),
                size_hint_x=0.8,
                size_hint_y=None
            )
            message_label.bind(texture_size=message_label.setter('size'))
            
            # Background for AI message
            message_bg = BoxLayout(
                size_hint_y=None,
                height=message_label.height + dp(10)
            )
            
            def update_bg(*args):
                message_bg.canvas.before.clear()
                with message_bg.canvas.before:
                    Color(*get_color_from_hex('#424242'))  # Dark gray
                    RoundedRectangle(
                        pos=message_bg.pos,
                        size=message_bg.size,
                        radius=[dp(10)]
                    )
            
            message_bg.bind(pos=update_bg, size=update_bg)
            Clock.schedule_once(update_bg, 0)
            
            message_bg.add_widget(message_label)
            message_container.add_widget(message_bg)
            message_container.add_widget(Label(size_hint_x=0.2))  # Spacer
        
        self.add_widget(message_container)
        
        # Timestamp
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%H:%M")
                time_label = Label(
                    text=formatted_time,
                    size_hint_y=None,
                    height=dp(20),
                    color=get_color_from_hex('#888888'),
                    font_size=dp(10),
                    halign='right' if is_user else 'left'
                )
                self.add_widget(time_label)
            except:
                pass
        
        self.height = sum(child.height for child in self.children) + dp(10)

# ============================================================================
# MAIN CHAT SCREEN
# ============================================================================

class ChatScreen(Screen):
    """Main chat screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_model = AIModel()
        self.conversation_manager = ConversationManager()
        self.messages = self.conversation_manager.load_conversation_history()
        
        self.build_ui()
        self.load_chat_history()
    
    def build_ui(self):
        """Build the user interface"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60))
        
        def update_header_bg(*args):
            header.canvas.before.clear()
            with header.canvas.before:
                Color(*get_color_from_hex('#1976D2'))  # Blue header
                Rectangle(pos=header.pos, size=header.size)
        
        header.bind(pos=update_header_bg, size=update_header_bg)
        Clock.schedule_once(update_header_bg, 0)
        
        # Logo and title
        try:
            logo = Image(source='gigabyte_logo.png', size_hint_x=None, width=dp(40))
            header.add_widget(logo)
        except:
            header.add_widget(Label(text='🔥', size_hint_x=None, width=dp(40), font_size=dp(24)))
        
        title_label = Label(
            text='Gigabyte AI',
            color=get_color_from_hex('#FFFFFF'),
            font_size=dp(18),
            bold=True
        )
        header.add_widget(title_label)
        
        # Menu button
        menu_btn = Button(
            text='⋮',
            size_hint_x=None,
            width=dp(40),
            font_size=dp(20),
            background_color=get_color_from_hex('#1976D2')
        )
        menu_btn.bind(on_press=self.show_menu)
        header.add_widget(menu_btn)
        
        main_layout.add_widget(header)
        
        # Chat area
        self.chat_scroll = ScrollView()
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        main_layout.add_widget(self.chat_scroll)
        
        # Input area
        input_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(5))
        
        self.text_input = TextInput(
            hint_text='Type your message...',
            multiline=False,
            size_hint_x=0.8,
            background_color=get_color_from_hex('#2C2C2C'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            cursor_color=get_color_from_hex('#2196F3')
        )
        self.text_input.bind(on_text_validate=self.send_message)
        
        send_btn = Button(
            text='Send',
            size_hint_x=0.2,
            background_color=get_color_from_hex('#2196F3')
        )
        send_btn.bind(on_press=self.send_message)
        
        input_layout.add_widget(self.text_input)
        input_layout.add_widget(send_btn)
        main_layout.add_widget(input_layout)
        
        self.add_widget(main_layout)
    
    def load_chat_history(self):
        """Load and display chat history"""
        for message in self.messages:
            is_user = message.get("role") == "user"
            content = message.get("content", "")
            timestamp = message.get("timestamp", "")
            
            chat_message = ChatMessage(content, is_user, timestamp)
            self.chat_layout.add_widget(chat_message)
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)
    
    def send_message(self, instance=None):
        """Send message to AI"""
        message_text = self.text_input.text.strip()
        if not message_text:
            return
        
        # Validate prompt
        is_valid, result = self.ai_model.validate_prompt(message_text)
        if not is_valid:
            self.show_error(f"Validation Error: {result}")
            return
        
        sanitized_prompt = result
        current_time = datetime.now().isoformat()
        
        # Add user message
        user_message = {
            "role": "user",
            "content": sanitized_prompt,
            "timestamp": current_time
        }
        self.messages.append(user_message)
        
        # Display user message
        chat_message = ChatMessage(sanitized_prompt, True, current_time)
        self.chat_layout.add_widget(chat_message)
        
        # Clear input
        self.text_input.text = ""
        
        # Show typing indicator
        typing_indicator = Label(
            text="🔥 Gigabyte AI is thinking...",
            color=get_color_from_hex('#888888'),
            size_hint_y=None,
            height=dp(30)
        )
        self.chat_layout.add_widget(typing_indicator)
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)
        
        # Generate AI response in background
        threading.Thread(target=self.generate_ai_response, args=(sanitized_prompt, typing_indicator)).start()
    
    def generate_ai_response(self, prompt: str, typing_indicator):
        """Generate AI response in background thread"""
        try:
            # Get conversation context (excluding current message)
            conversation_context = self.messages[:-1]
            success, response = self.ai_model.generate_response(prompt, conversation_context)
            
            # Schedule UI update on main thread
            Clock.schedule_once(lambda dt: self.handle_ai_response(success, response, typing_indicator), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.handle_ai_response(False, str(e), typing_indicator), 0)
    
    def handle_ai_response(self, success: bool, response: str, typing_indicator):
        """Handle AI response on main thread"""
        # Remove typing indicator
        self.chat_layout.remove_widget(typing_indicator)
        
        if success:
            # Add AI response to messages
            ai_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
            self.messages.append(ai_message)
            
            # Display AI message
            chat_message = ChatMessage(response, False, ai_message["timestamp"])
            self.chat_layout.add_widget(chat_message)
            
            # Save conversation history
            self.conversation_manager.save_conversation_history(self.messages)
            
        else:
            # Show error message
            error_message = ChatMessage(f"Error: {response}", False)
            self.chat_layout.add_widget(error_message)
            # Remove failed user message
            if self.messages:
                self.messages.pop()
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)
    
    def show_menu(self, instance):
        """Show menu popup"""
        stats = self.conversation_manager.get_conversation_summary(self.messages)
        
        menu_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        # Stats
        stats_label = Label(
            text=f"📊 Conversation Stats\n"
                 f"Total messages: {stats['total_messages']}\n"
                 f"Your messages: {stats['user_messages']}\n"
                 f"AI responses: {stats['assistant_messages']}\n\n"
                 f"🧠 Memory: Perfect Recall\n"
                 f"♾️ Usage: Unlimited\n"
                 f"🚀 Status: Online",
            halign='center'
        )
        menu_layout.add_widget(stats_label)
        
        # Clear history button
        clear_btn = Button(
            text='🗑️ Clear Chat History',
            size_hint_y=None,
            height=dp(40),
            background_color=get_color_from_hex('#F44336')
        )
        
        popup = Popup(
            title='Gigabyte AI Menu',
            content=menu_layout,
            size_hint=(0.8, 0.6)
        )
        
        clear_btn.bind(on_press=lambda x: self.clear_history(popup))
        menu_layout.add_widget(clear_btn)
        
        # Close button
        close_btn = Button(
            text='Close',
            size_hint_y=None,
            height=dp(40),
            background_color=get_color_from_hex('#2196F3')
        )
        close_btn.bind(on_press=popup.dismiss)
        menu_layout.add_widget(close_btn)
        
        popup.open()
    
    def clear_history(self, popup):
        """Clear chat history"""
        self.messages = []
        self.chat_layout.clear_widgets()
        
        # Clear saved file
        try:
            if os.path.exists(CONVERSATION_FILE):
                os.remove(CONVERSATION_FILE)
        except Exception as e:
            logger.error(f"Error clearing history file: {e}")
        
        popup.dismiss()
        self.show_info("Chat history cleared!")
    
    def show_error(self, message: str):
        """Show error popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
    
    def show_info(self, message: str):
        """Show info popup"""
        popup = Popup(
            title='Info',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class GigabyteAIApp(App):
    """Main Gigabyte AI Application"""
    
    def build(self):
        """Build the application"""
        self.title = "Gigabyte AI - Unlimited Assistant"
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add chat screen
        chat_screen = ChatScreen(name='chat')
        sm.add_widget(chat_screen)
        
        return sm
    
    def on_start(self):
        """Called when the app starts"""
        logger.info("Gigabyte AI mobile app started")
        
        # Check API key
        if not os.getenv('GEMINI_API_KEY'):
            popup = Popup(
                title='API Key Required',
                content=Label(text='Please set GEMINI_API_KEY environment variable\n\nExample:\nos.environ["GEMINI_API_KEY"] = "your_key_here"'),
                size_hint=(0.8, 0.6)
            )
            popup.open()
    
    def on_stop(self):
        """Called when the app stops"""
        logger.info("Gigabyte AI mobile app stopped")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function to run the application"""
    print("\n" + "="*60)
    print("🔥 GIGABYTE AI - UNLIMITED MOBILE ASSISTANT")
    print("="*60)
    print("📱 Mobile-Optimized Interface")
    print("🧠 Perfect Memory & Context Awareness")
    print("♾️ Unlimited Usage")
    print("🚀 Advanced AI Capabilities")
    print("="*60)
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  API KEY SETUP REQUIRED")
        print("Before running the app, set your API key:")
        print('os.environ["GEMINI_API_KEY"] = "your_api_key_here"')
        print("\nThen run the app again!")
        return
    
    print("\n🎉 Starting Gigabyte AI...")
    
    try:
        # Run the app
        GigabyteAIApp().run()
    except Exception as e:
        print(f"❌ Error running app: {e}")
        print("💡 Try restarting the runtime and running again")

# Auto-run if executed directly
if __name__ == '__main__':
    main()

# ============================================================================
# GOOGLE COLAB INSTRUCTIONS
# ============================================================================

print("\n" + "="*60)
print("📋 GOOGLE COLAB SETUP INSTRUCTIONS")
print("="*60)
print("1. Upload this file to Google Colab")
print("2. Set your API key:")
print('   os.environ["GEMINI_API_KEY"] = "your_api_key_here"')
print("3. Run the file:")
print('   exec(open("GigaByte_AI_Complete.py").read())')
print("="*60)
print("🔥 Gigabyte AI - Your Unlimited Mobile AI Assistant")
print("="*60)