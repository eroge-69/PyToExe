import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import requests
import threading
import json
from bs4 import BeautifulSoup
import urllib.parse
import sys
import os

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    HF_AVAILABLE = True
    print("✓ Transformers and PyTorch libraries loaded successfully")
except ImportError as e:
    HF_AVAILABLE = False
    print(f"✗ Error importing required libraries: {e}")
    print("Please install required packages:")
    print("pip install transformers torch requests beautifulsoup4")

AVAILABLE_MODELS = {
    "DialoGPT-medium": {
        "name": "microsoft/DialoGPT-medium",
        "type": "conversational",
        "size": "345M parameters",
        "description": "Conversational AI trained on Reddit data"
    },
    "DialoGPT-small": {
        "name": "microsoft/DialoGPT-small", 
        "type": "conversational",
        "size": "117M parameters",
        "description": "Smaller, faster conversational model"
    },
    "GPT-2": {
        "name": "gpt2",
        "type": "text-generation",
        "size": "124M parameters", 
        "description": "Classic GPT-2 text generation model"
    },
    "GPT-2 Medium": {
        "name": "gpt2-medium",
        "type": "text-generation", 
        "size": "355M parameters",
        "description": "Larger GPT-2 model with better quality"
    },
    "DistilGPT-2": {
        "name": "distilgpt2",
        "type": "text-generation",
        "size": "82M parameters",
        "description": "Distilled GPT-2, faster and smaller"
    },
    "FLAN-T5-small": {
        "name": "google/flan-t5-small",
        "type": "text2text-generation",
        "size": "80M parameters",
        "description": "Instruction-tuned T5 model"
    },
    "FLAN-T5-base": {
        "name": "google/flan-t5-base", 
        "type": "text2text-generation",
        "size": "250M parameters",
        "description": "Larger instruction-tuned T5 model"
    },
    "BlenderBot-small": {
        "name": "facebook/blenderbot_small-90M",
        "type": "conversational",
        "size": "90M parameters", 
        "description": "Facebook's conversational AI"
    },
    "Qwen2-1.5B": {
        "name": "Qwen/Qwen2-1.5B",
        "type": "text-generation",
        "size": "1.5B parameters",
        "description": "Qwen2 1.5B parameter. Smartest AI model available for Nexo."
    },
    "Qwen2-0.5B": {
        "name": "Qwen/Qwen2-0.5B",
        "type": "text-generation",
        "size": "0.5B parameters",
        "description": "Qwen2 0.5B parameter general-purpose language model"
    }
}

class LocalAI:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.model_loaded = False
        self.current_model = None
        self.model_type = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self, model_key="DialoGPT-medium"):
        if not HF_AVAILABLE:
            print("✗ Hugging Face Transformers not available")
            return False
        
        if model_key not in AVAILABLE_MODELS:
            print(f"✗ Unknown model: {model_key}")
            return False
            
        model_config = AVAILABLE_MODELS[model_key]
        model_name = model_config["name"]
        self.model_type = model_config["type"]
        
        try:
            print(f"🤖 Starting to load {model_key} model...")
            print(f"📥 Model: {model_name}")
            print(f"📊 Size: {model_config['size']}")
            print(f"📝 Description: {model_config['description']}")
            print(f"🔧 Device: {self.device}")
            
            self.cleanup_model()
            
            print(f"📂 Loading model: {model_name}")
            
            print("📝 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            if self.model_type == "text2text-generation":
                print("🔧 Using text2text-generation pipeline...")
                self.pipeline = pipeline("text2text-generation", model=model_name, tokenizer=self.tokenizer, device=0 if self.device == "cuda" else -1)
            else:
                print("🧠 Loading model weights...")
                self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if self.device == "cuda" else torch.float32)
                self.model.to(self.device)
                
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    print("✓ Padding token configured")
                
                self.model.eval()
            
            self.current_model = model_key
            self.model_loaded = True
            print(f"🎉 {model_key} model loaded successfully!")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            print(f"📍 Error type: {type(e).__name__}")
            if "out of memory" in str(e).lower():
                print("💡 Try a smaller model or close other applications")
            return False
    
    def cleanup_model(self):
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def generate_response(self, prompt):
        if not self.model_loaded:
            return "❌ Model not loaded. Please select and load a model."
        
        try:
            print(f"🤔 Processing with {self.current_model}: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
            
            if self.model_type == "text2text-generation":
                formatted_prompt = f"Answer this question in a helpful way: {prompt}"
                response = self.pipeline(formatted_prompt, max_length=200, do_sample=True, temperature=0.7)[0]['generated_text']
            
            elif self.model_type == "conversational":
                if "blenderbot" in self.current_model.lower():
                    inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
                    with torch.no_grad():
                        outputs = self.model.generate(
                            **inputs, 
                            max_length=inputs['input_ids'].shape[1] + 100, 
                            pad_token_id=self.tokenizer.eos_token_id,
                            do_sample=True,
                            temperature=0.7,
                            top_p=0.9
                        )
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    if prompt in response:
                        response = response.replace(prompt, "").strip()
                else:
                    chat_history = []
                    encoded_input = self.tokenizer.encode(prompt + self.tokenizer.eos_token, return_tensors='pt').to(self.device)
                    
                    with torch.no_grad():
                        outputs = self.model.generate(
                            encoded_input,
                            max_length=encoded_input.shape[1] + 150,
                            num_return_sequences=1,
                            temperature=0.7,
                            pad_token_id=self.tokenizer.eos_token_id,
                            do_sample=True,
                            top_p=0.9,
                            repetition_penalty=1.1
                        )
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    if prompt in response:
                        response = response.replace(prompt, "").strip()
            
            else:
                formatted_prompt = f"Human: {prompt}\nAssistant:"
                inputs = self.tokenizer(formatted_prompt, return_tensors="pt", padding=True, truncation=True, max_length=512).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        attention_mask=inputs.get("attention_mask", None),
                        max_new_tokens=150,
                        num_return_sequences=1,
                        temperature=0.7,
                        pad_token_id=self.tokenizer.eos_token_id,
                        do_sample=True,
                        top_p=0.9,
                        repetition_penalty=1.2,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                if formatted_prompt in response:
                    response = response.replace(formatted_prompt, "").strip()
                
                response = response.replace("Human:", "").replace("Assistant:", "").strip()
                
                lines = response.split('\n')
                if lines:
                    response = lines[0].strip()
            
            response = self.clean_response(response)
            
            print(f"💬 Generated response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            return response
            
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            print(f"✗ {error_msg}")
            return "❌ Sorry, I encountered an error while generating a response."
    
    def clean_response(self, response):
        if not response or response.strip() == "" or len(response.strip()) < 2:
            return "Hello! How can I help you today?"
        
        artifacts = ['[', ']', '(', ')', 'added:', 'updated to version', '*wink*', 'mr. saturday', '<', '>', '{', '}']
        for artifact in artifacts:
            if artifact in response:
                response = response.replace(artifact, "")
        
        if len(response) > 300:
            response = response[:300].rsplit(' ', 1)[0] + "..."
        
        return response.strip()

class ChatApp:
    def __init__(self, root):
        self.root = root
        root.title("Nexo AI v1.4 - INSTANT ZERO DELAY")
        root.geometry("1000x800")
        
        root.configure(bg='#1e1e1e')
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Custom.TCombobox', fieldbackground='#3c3c3c', background='#3c3c3c', foreground='#cccccc')

        model_frame = tk.Frame(root, bg='#1e1e1e')
        model_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(model_frame, text="AI Model:", bg='#1e1e1e', fg='#cccccc', 
                font=("Consolas", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_var = tk.StringVar(value="DialoGPT-medium")
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       values=list(AVAILABLE_MODELS.keys()), 
                                       state="readonly", width=20, style='Custom.TCombobox')
        self.model_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        self.load_model_btn = tk.Button(
            model_frame, text="Load Model", command=self.load_selected_model,
            bg="#9c27b0", fg="white", font=("Consolas", 9, "bold"),
            relief=tk.FLAT, bd=0, padx=15, cursor="hand2"
        )
        self.load_model_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = tk.Button(
            model_frame, text="Clear Chat", command=self.clear_chat,
            bg="#f44336", fg="white", font=("Consolas", 9, "bold"),
            relief=tk.FLAT, bd=0, padx=15, cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_info_label = tk.Label(
            model_frame, text="", bg='#1e1e1e', fg='#888888',
            font=("Consolas", 8)
        )
        self.model_info_label.pack(side=tk.LEFT, padx=(10, 0))

        self.chat_box = ScrolledText(
            root, wrap=tk.WORD, width=100, height=30, state=tk.DISABLED,
            font=("Consolas", 11), bg="#2d2d30", fg="#cccccc",
            insertbackground="#ffffff", selectbackground="#264f78",
            relief=tk.FLAT, bd=0
        )
        self.chat_box.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        self.chat_box.tag_configure("user", foreground="#66d9ef", font=("Consolas", 11, "bold"))
        self.chat_box.tag_configure("nexo", foreground="#a6e22e", font=("Consolas", 11, "bold"))
        self.chat_box.tag_configure("system", foreground="#fd971f", font=("Consolas", 10))

        input_frame = tk.Frame(root, bg='#1e1e1e')
        input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))

        self.entry = tk.Entry(
            input_frame, font=("Consolas", 11), bg="#3c3c3c", fg="#cccccc",
            insertbackground="#ffffff", relief=tk.FLAT, bd=5
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind("<Return>", self.on_send)
        self.entry.bind("<Up>", self.on_history_up)
        self.entry.bind("<Down>", self.on_history_down)

        self.send_btn = tk.Button(
            input_frame, text="Send", command=self.on_send,
            bg="#0e639c", fg="white", font=("Consolas", 10, "bold"),
            relief=tk.FLAT, bd=0, padx=20, cursor="hand2"
        )
        self.send_btn.pack(side=tk.RIGHT, padx=5)

        self.scrape_btn = tk.Button(
            input_frame, text="Scrape URL", command=self.on_scrape,
            bg="#1a472a", fg="white", font=("Consolas", 10, "bold"),
            relief=tk.FLAT, bd=0, padx=15, cursor="hand2"
        )
        self.scrape_btn.pack(side=tk.RIGHT)

        self.status_label = tk.Label(
            root, text="Ready to load model", fg="#ffa500", bg='#1e1e1e',
            font=("Consolas", 10, "bold")
        )
        self.status_label.pack(pady=(0, 10))

        self.input_history = []
        self.history_index = -1

        self.update_model_info()
        self.model_combo.bind("<<ComboboxSelected>>", lambda e: self.update_model_info())

        self.local_ai = LocalAI()
        
        self.display_system("⚡ Welcome to Nexo AI v1.4 - INSTANT ZERO DELAY!")
        self.display_system("🚀 MAXIMUM PERFORMANCE - No artificial delays!")
        self.display_system("🔧 Select a model and click 'Load Model' to begin")
        
        self.entry.focus()

    def update_model_info(self):
        selected = self.model_var.get()
        if selected in AVAILABLE_MODELS:
            config = AVAILABLE_MODELS[selected]
            info = f"{config['size']} - {config['description']}"
            self.model_info_label.config(text=info)

    def display_system(self, text):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"🔧 System: {text}\n", "system")
        self.chat_box.see(tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def display_user(self, text):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"👤 You: {text}\n", "user")
        self.chat_box.see(tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def display_nexo(self, text):
        model_name = self.local_ai.current_model or "Nexo"
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"🤖 {model_name}: {text}\n", "nexo")
        self.chat_box.see(tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def display(self, text):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.insert(tk.END, text + "\n")
        self.chat_box.see(tk.END)
        self.chat_box.configure(state=tk.DISABLED)

    def clear_chat(self):
        self.chat_box.configure(state=tk.NORMAL)
        self.chat_box.delete(1.0, tk.END)
        self.chat_box.configure(state=tk.DISABLED)
        self.display_system("Chat cleared")

    def set_status(self, text, color="#cccccc"):
        self.status_label.config(text=f"Status: {text}", fg=color)

    def on_history_up(self, event):
        if self.input_history and self.history_index < len(self.input_history) - 1:
            self.history_index += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.input_history[-(self.history_index + 1)])

    def on_history_down(self, event):
        if self.history_index > 0:
            self.history_index -= 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.input_history[-(self.history_index + 1)])
        elif self.history_index == 0:
            self.history_index = -1
            self.entry.delete(0, tk.END)

    def load_selected_model(self):
        selected_model = self.model_var.get()
        
        def load_model():
            if not HF_AVAILABLE:
                self.display_system("❌ ERROR: transformers library not installed!")
                self.display_system("📦 Install with: pip install transformers torch requests beautifulsoup4")
                self.display_system("🔄 Then restart the application")
                self.set_status("Error: Missing dependencies", "#ff6b6b")
                return
            
            config = AVAILABLE_MODELS[selected_model]
            self.display_system(f"🤖 Loading {selected_model} model...")
            self.display_system(f"📊 {config['size']} - {config['description']}")
            self.set_status(f"Loading {selected_model}...", "#ffa500")
            
            success = self.local_ai.load_model(selected_model)
            
            if success:
                self.display_system(f"🎉 {selected_model} is ready!")
                self.display_system("💬 You can now chat with the AI")
                self.display_system("🌐 Web scraping available with 'Scrape URL' button")
                self.display_system("⚡ INSTANT MODE - Zero delays enabled!")
                self.display_system("=" * 50)
                self.set_status(f"Ready - {selected_model}", "#4caf50")
            else:
                self.display_system(f"❌ Failed to load {selected_model}")
                self.display_system("🔍 Check console for detailed error messages")
                self.set_status("Model load failed", "#ff6b6b")
            
            # Re-enable button immediately
            self.load_model_btn.configure(state=tk.NORMAL, text="Load Model")
        
        self.load_model_btn.configure(state=tk.DISABLED, text="Loading...")
        threading.Thread(target=load_model, daemon=True).start()

    def on_send(self, event=None):
        prompt = self.entry.get().strip()
        if not prompt:
            return
        
        if not self.local_ai.model_loaded:
            self.display_system("⏳ Please load a model first using the 'Load Model' button...")
            return
        
        self.input_history.append(prompt)
        if len(self.input_history) > 50:
            self.input_history.pop(0)
        self.history_index = -1
        
        # Display user message instantly
        self.display_user(prompt)
        self.entry.delete(0, tk.END)
        
        # Set status instantly
        self.set_status("Thinking...", "#2196f3")
        
        # Process in background thread for true zero delay
        threading.Thread(target=self.process_prompt, args=(prompt,), daemon=True).start()

    def process_prompt(self, prompt):
        try:
            response = self.local_ai.generate_response(prompt)
            
            # Update GUI instantly using thread-safe method
            self.root.after(0, self.display_nexo, response)
            self.root.after(0, self.set_status, f"Ready - {self.local_ai.current_model}", "#4caf50")
            
        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            self.root.after(0, self.display_nexo, error_msg)
            self.root.after(0, self.set_status, f"Ready - {self.local_ai.current_model}", "#4caf50")
            print(f"✗ Process error: {e}")

    def on_scrape(self):
        url = self.entry.get().strip()
        if not url:
            self.display_system("⚠️ Please enter a URL to scrape")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.display_system(f"🌐 Scraping: {url}")
        self.entry.delete(0, tk.END)
        
        self.entry.configure(state=tk.DISABLED)
        self.scrape_btn.configure(state=tk.DISABLED, text="Scraping...")
        
        threading.Thread(target=self.scrape_website, args=(url,), daemon=True).start()

    def scrape_website(self, url):
        try:
            self.set_status("Scraping...", "#ff9800")
            print(f"🌐 Scraping website: {url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            
            lines = text.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned_text = ' '.join(cleaned_lines)
            
            max_length = 3000
            if len(cleaned_text) > max_length:
                snippet = cleaned_text[:max_length] + "..."
            else:
                snippet = cleaned_text
            
            self.display_system(f"📄 Content scraped from {url}:")
            self.display_system(f"📝 {snippet}")
            print(f"✓ Successfully scraped {len(cleaned_text)} characters from {url}")
            
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.display_system(f"❌ {error_msg}")
            print(f"✗ Network error: {e}")
        except Exception as e:
            error_msg = f"Scrape error: {str(e)}"
            self.display_system(f"❌ {error_msg}")
            print(f"✗ Scrape error: {e}")
        finally:
            self.set_status(f"Ready - {self.local_ai.current_model}", "#4caf50")
            self.entry.configure(state=tk.NORMAL)
            self.scrape_btn.configure(state=tk.NORMAL, text="Scrape URL")
            self.entry.focus()

def main():
    print("=" * 60)
    print("⚡ NEXO AI v1.4 - INSTANT ZERO DELAY")
    print("🚀 Maximum Performance - No Artificial Delays!")
    print("🔥 Optimized for Instant Response Display")
    print("=" * 60)
    
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    if torch.cuda.is_available():
        print(f"🔥 CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("💻 Using CPU mode")
    
    print("\n🤖 Available Models:")
    for key, config in AVAILABLE_MODELS.items():
        print(f"  • {key}: {config['size']} - {config['description']}")
    
    try:
        root = tk.Tk()
        app = ChatApp(root)
        
        print("\n✓ GUI initialized successfully")
        print("🖥️  Running main loop...")
        print("⚡ INSTANT MODE - Zero delay message display!")
        print("🔧 All debug output will appear in this console")
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        raise
    finally:
        print("🧹 Cleaning up...")
        if 'app' in locals():
            app.local_ai.cleanup_model()

if __name__ == "__main__":
    main()