# main.py - WordPress Plugin Builder with Chat & Settings
import os
import json
import requests
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "model": "llama3",
    "temperature": 0.5,
    "base_url": "http://localhost:11434",
    "project_path": "",
    "system_prompt": "You are a skilled WordPress plugin developer. Write secure, standards-compliant code."
}

class SettingsWindow:
    def __init__(self, parent, config, refresh_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Settings")
        self.window.geometry("600x520")
        self.window.transient(parent)
        self.window.grab_set()
        self.config = config
        self.refresh_callback = refresh_callback

        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        row = 0
        ttk.Label(scrollable_frame, text="Ollama Model Name (e.g. llama3, phi3)").grid(sticky="w", padx=20, pady=5)
        self.model_var = tk.StringVar(value=self.config.get("model", ""))
        ttk.Entry(scrollable_frame, textvariable=self.model_var, width=50).grid(row=row+1, padx=20, pady=5, sticky="w")

        ttk.Label(scrollable_frame, text="Temperature (0.1 = precise, 0.8 = creative)").grid(row=row+2, sticky="w", padx=20, pady=5)
        self.temp_var = tk.DoubleVar(value=self.config.get("temperature", 0.5))
        ttk.Scale(scrollable_frame, from_=0.1, to=0.9, variable=self.temp_var, orient="horizontal").grid(row=row+3, padx=20, pady=5, sticky="ew")
        temp_label = ttk.Label(scrollable_frame, textvariable=self.temp_var)
        temp_label.grid(row=row+3, column=1, padx=5)

        ttk.Label(scrollable_frame, text="Base URL (usually http://localhost:11434)").grid(row=row+4, sticky="w", padx=20, pady=5)
        self.url_var = tk.StringVar(value=self.config.get("base_url", "http://localhost:11434"))
        ttk.Entry(scrollable_frame, textvariable=self.url_var, width=50).grid(row=row+5, padx=20, pady=5, sticky="w")

        ttk.Label(scrollable_frame, text="Default Project Folder").grid(row=row+6, sticky="w", padx=20, pady=5)
        self.path_var = tk.StringVar(value=self.config.get("project_path", ""))
        path_entry = ttk.Entry(scrollable_frame, textvariable=self.path_var, width=40)
        path_entry.grid(row=row+7, column=0, padx=20, pady=5, sticky="w")
        ttk.Button(scrollable_frame, text="Browse", command=self.browse_path).grid(row=row+7, column=1, padx=5)

        ttk.Label(scrollable_frame, text="System Prompt (AI behavior)").grid(row=row+8, sticky="w", padx=20, pady=5)
        self.sys_prompt_text = scrolledtext.ScrolledText(scrollable_frame, height=5)
        self.sys_prompt_text.insert("1.0", self.config.get("system_prompt", DEFAULT_CONFIG["system_prompt"]))
        self.sys_prompt_text.grid(row=row+9, padx=20, pady=5, sticky="ew")

        self.test_btn = ttk.Button(scrollable_frame, text="📡 Test Ollama Connection", command=self.test_connection)
        self.test_btn.grid(row=row+10, padx=20, pady=10)

        ttk.Button(scrollable_frame, text="💾 Save Settings", command=self.save).grid(row=row+11, pady=10)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.window.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(0, weight=1)

    def browse_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_var.set(folder)

    def test_connection(self):
        url = self.url_var.get().strip().rstrip("/") + "/api/tags"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                models = [t["name"] for t in response.json().get("models", [])]
                messagebox.showinfo("✅ Success", f"Connected!\nLoaded models: {', '.join(models)}")
            else:
                messagebox.showerror("❌ Failed", f"Status: {response.status_code}")
        except Exception as e:
            messagebox.showerror("💥 Error", f"Cannot reach Ollama:\n{str(e)}\n\nIs Ollama running?")

    def save(self):
        new_config = {
            "model": self.model_var.get().strip(),
            "temperature": round(self.temp_var.get(), 2),
            "base_url": self.url_var.get().strip(),
            "project_path": self.path_var.get().strip(),
            "system_prompt": self.sys_prompt_text.get("1.0", tk.END).strip()
        }

        if not new_config["model"]:
            messagebox.showwarning("⚠️", "Please enter a model name.")
            return

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=4)
            messagebox.showinfo("✅", "Settings saved!")
            self.refresh_callback()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config:\n{str(e)}")


class ChatTab:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.frame = ttk.Frame(parent)

        os.makedirs("chats", exist_ok=True)
        self.conversation = []

        title_frame = tk.Frame(self.frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(title_frame, text="💬 Chat with Ollama (Local & Private)", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)

        btn_frame = tk.Frame(title_frame)
        btn_frame.pack(side=tk.RIGHT)
        tk.Button(btn_frame, text="🆕 New Chat", command=self.new_chat).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="💾 Save Chat", command=self.save_chat).pack(side=tk.LEFT, padx=2)

        self.chat_log = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, bg="white", state="disabled", font=("Arial", 9))
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        input_frame = tk.Frame(self.frame)
        tk.Label(input_frame, text="You:", anchor="w").pack(anchor="w", padx=5)
        self.user_input = scrolledtext.ScrolledText(input_frame, height=3, font=("Arial", 9))
        self.user_input.pack(fill=tk.X, padx=5, pady=2)

        send_clear_frame = tk.Frame(input_frame)
        send_clear_frame.pack(pady=5)
        tk.Button(send_clear_frame, text="📤 Send", width=10, command=self.send_message).pack(side=tk.LEFT, padx=5)
        tk.Button(send_clear_frame, text="🗑️ Clear Input", width=12, command=lambda: self.user_input.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=5)

        input_frame.pack(fill=tk.X, padx=10, pady=5)
        self.append_to_log(f"🤖 AI: Ready! Using model: {self.config['model']}")

    def append_to_log(self, text):
        self.chat_log.config(state="normal")
        self.chat_log.insert(tk.END, text + "\n\n")
        self.chat_log.config(state="disabled")
        self.chat_log.see(tk.END)

    def send_message(self):
        user_msg = self.user_input.get("1.0", tk.END).strip()
        if not user_msg: return
        self.append_to_log(f"You: {user_msg}")
        self.user_input.delete("1.0", tk.END)
        self.append_to_log("⏳ AI is thinking...")

        full_context = "\n".join([f"User: {c['prompt']}\nAssistant: {c['response']}" for c in self.conversation])
        full_context += f"\nUser: {user_msg}\nAssistant:"

        url = f"{self.config['base_url'].rstrip('/')}/api/generate"
        payload = {
            "model": self.config["model"],
            "prompt": full_context,
            "system": self.config.get("system_prompt", "You are a helpful assistant."),
            "options": {"temperature": self.config["temperature"]},
            "stream": False
        }

        try:
            resp = requests.post(url, json=payload, timeout=120)
            if resp.status_code == 200:
                ai_response = resp.json()["response"].strip()
                self.append_to_log(f"🤖 AI: {ai_response}")
                self.conversation.append({"prompt": user_msg, "response": ai_response})
            else:
                self.append_to_log(f"❌ API Error: {resp.text}")
        except Exception as e:
            self.append_to_log(f"💥 Failed: {str(e)}")

    def new_chat(self):
        if self.conversation:
            if messagebox.askyesno("🆕", "Start new chat? Current will not be saved."):
                self.conversation = []
                self.chat_log.config(state="normal")
                self.chat_log.delete("1.0", tk.END)
                self.chat_log.config(state="disabled")
                self.append_to_log("🗨️ New chat started.")

    def save_chat(self):
        if not self.conversation and self.chat_log.get("1.0", "end").strip() == "": return
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filepath = os.path.join("chats", f"chat-{timestamp}.txt")
        content = self.chat_log.get("1.0", tk.END)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Ollama Chat - {datetime.now()}\n{'-'*50}\n\n")
                f.write(content)
            messagebox.showinfo("✅", f"Saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_config(self, new_config):
        self.config.update(new_config)
        self.append_to_log(f"🔄 Model: {self.config['model']}")


class PluginBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 WordPress Plugin Builder + Ollama Chat")
        self.root.geometry("900x700")
        self.config = self.load_config()

        menubar = tk.Menu(root)
        root.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Settings", menu=settings_menu)
        settings_menu.add_command(label="Open Settings", command=self.open_settings)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.plugin_frame = self.create_plugin_tab()
        self.notebook.add(self.plugin_frame, text="📁 Plugin Builder")

        self.chat_tab = ChatTab(self.notebook, self.config)
        self.notebook.add(self.chat_tab.frame, text="💬 Chat with Ollama")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in data: data[k] = v
                return data
            except: pass
        return DEFAULT_CONFIG.copy()

    def open_settings(self):
        def refresh():
            self.config = self.load_config()
            self.chat_tab.update_config(self.config)
        SettingsWindow(self.root, self.config, refresh)

    def create_plugin_tab(self):
        frame = ttk.Frame(self.notebook)
        tk.Label(frame, text="Project Name:").pack(pady=(10, 0))
        self.name_entry = tk.Entry(frame, width=50); self.name_entry.pack()
        tk.Label(frame, text="Describe Your Plugin:").pack(pady=5)
        self.prompt_text = scrolledtext.ScrolledText(frame, height=10)
        self.prompt_text.pack(fill=tk.BOTH, expand=True, padx=10)

        btn_frame = tk.Frame(frame); btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="📁 New Project", command=self.new_project).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="💾 Save Project", command=self.save_project).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="⚡ Generate Plugin", command=self.generate_plugin).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="✅ Validate Files", command=self.validate_files).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="📋 Use in Chat", command=self.load_plugin_to_chat).grid(row=0, column=4, padx=5)

        tk.Label(frame, text="Status Log:").pack(anchor="w", padx=10)
        self.status_log = scrolledtext.ScrolledText(frame, height=12, bg="black", fg="white", font=("Courier", 9))
        self.status_log.pack(fill=tk.BOTH, expand=True, padx=10)
        self.log("🔌 Loaded model: " + self.config['model'])
        return frame

    def log(self, msg):
        self.status_log.insert(tk.END, msg + "\n"); self.status_log.see(tk.END)

    def call_ollama(self, prompt, system=None):
        if system is None: system = self.config["system_prompt"]
        url = f"{self.config['base_url']}/api/generate"
        payload = {
            "model": self.config["model"],
            "prompt": prompt,
            "system": system,
            "options": {"temperature": self.config["temperature"]},
            "stream": False
        }
        try:
            resp = requests.post(url, json=payload, timeout=120)
            return resp.json()["response"] if resp.status_code == 200 else f"❌ Error: {resp.text}"
        except Exception as e:
            return f"💥 Conn failed: {str(e)}"

    def new_project(self):
        name = self.name_entry.get().strip()
        if not name: return messagebox.showwarning("⚠️", "Enter name!")
        folder = filedialog.askdirectory(initialdir=self.config.get("project_path"))
        if not folder: return
        self.project_dir = os.path.join(folder, name.lower().replace(" ", "-"))
        os.makedirs(self.project_dir, exist_ok=True)
        self.log(f"✅ Project: {self.project_dir}")

    def save_project(self):
        if not hasattr(self, 'project_dir'): return messagebox.showwarning("⚠️", "Create project!")
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        with open(os.path.join(self.project_dir, "prompt.txt"), "w", encoding="utf-8") as f:
            f.write(prompt)
        self.log("📝 Saved prompt.txt")

    def generate_plugin(self):
        if not hasattr(self, 'project_dir'): return messagebox.showwarning("⚠️", "No project!")
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt: return messagebox.showwarning("⚠️", "Write description!")
        self.log("⏳ Generating...")
        response = self.call_ollama(f"Generate WordPress plugin:\n{prompt}\nOnly PHP in ```php ... ```")
        if "💥" in response or "❌" in response: return self.log(response)

        start = response.find("```php") + 7; end = response.find("```", start)
        code = response[start:end].strip() if start > 6 and end > -1 else response.strip()

        path = os.path.join(self.project_dir, "plugin.php")
        with open(path, "w", encoding="utf-8") as f: f.write(code)
        self.log(f"✅ Generated: {path}")
        self.validate_files()

    def validate_files(self):
        path = os.path.join(self.project_dir, "plugin.php")
        if not os.path.exists(path): return self.log("❌ No plugin.php")
        with open(path, "r", encoding="utf-8") as f: code = f.read()
        self.log("🔍 Validating...")
        result = self.call_ollama(f"Review for security, hooks, conflicts:\n{code[:8000]}")
        self.log("🔎 " + (result[:800] + "..." if len(result) > 800 else result))

    def load_plugin_to_chat(self):
        if not hasattr(self, 'project_dir'): return messagebox.showwarning("⚠️", "No project!")
        path = os.path.join(self.project_dir, "plugin.php")
        if not os.path.exists(path): return messagebox.showwarning("⚠️", "Generate plugin first!")
        try:
            with open(path, "r", encoding="utf-8") as f: code = f.read()
            if messagebox.askyesno("📋 Load Code", "Copy to clipboard OR send to Chat tab?"):
                self.root.clipboard_clear(); self.root.clipboard_append(code); self.root.update()
                messagebox.showinfo("✅", "Code copied!")
            else:
                self.chat_tab.user_input.delete("1.0", tk.END)
                self.chat_tab.user_input.insert("1.0", f"Here's my plugin. Improve it:\n\n```php\n{code}\n```\n\nWhat should I add?")
                self.notebook.select(1)
                messagebox.showinfo("💬", "Sent to Chat tab!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PluginBuilderApp(root)
    root.mainloop()