import tkinter as tk
import webview
import threading
import sys
import json
import os

class KickChatWindow:
    def __init__(self):
        self.settings_file = "chat_settings.json"
        self.default_settings = {
            "position": "bottom_right",
            "width": 400,
            "height": 700
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        """Load settings from file or create default"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except:
            pass
    
    def get_position_coordinates(self, position):
        """Calculate window position based on setting"""
        root = tk.Tk()
        root.withdraw()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        
        window_width = self.settings["width"]
        window_height = self.settings["height"]
        
        positions = {
            "top_left": (50, 50),
            "top_right": (screen_width - window_width - 50, 50),
            "bottom_left": (50, screen_height - window_height - 100),
            "bottom_right": (screen_width - window_width - 50, screen_height - window_height - 100),
            "center": ((screen_width - window_width) // 2, (screen_height - window_height) // 2)
        }
        
        return positions.get(position, positions["bottom_right"])
    
    def show_settings(self):
        """Show settings popup"""
        def create_settings_window():
            settings_window = tk.Tk()
            settings_window.title("Chat Settings")
            settings_window.geometry("250x300")
            settings_window.configure(bg='#2c2c2c')
            settings_window.resizable(False, False)
            settings_window.attributes('-topmost', True)
            
            settings_window.update_idletasks()
            x = (settings_window.winfo_screenwidth() // 2) - (250 // 2)
            y = (settings_window.winfo_screenheight() // 2) - (300 // 2)
            settings_window.geometry(f"250x300+{x}+{y}")
            
            title_label = tk.Label(
                settings_window, 
                text="Chat Position", 
                font=("Arial", 14, "bold"),
                bg='#2c2c2c', 
                fg='white'
            )
            title_label.pack(pady=20)
            
            positions = [
                ("Top Left", "top_left"),
                ("Top Right", "top_right"),
                ("Bottom Left", "bottom_left"),
                ("Bottom Right", "bottom_right"),
                ("Center", "center")
            ]
            
            def change_position(new_pos):
                self.settings["position"] = new_pos
                self.save_settings()
                settings_window.destroy()
                webview.windows[0].destroy()
                
            for text, pos in positions:
                is_current = pos == self.settings["position"]
                bg_color = '#4CAF50' if is_current else '#4a4a4a'
                
                btn = tk.Button(
                    settings_window,
                    text=text + (" ✓" if is_current else ""),
                    command=lambda p=pos: change_position(p),
                    bg=bg_color,
                    fg='white',
                    font=("Arial", 10, "bold" if is_current else "normal"),
                    relief='flat',
                    padx=20,
                    pady=8,
                    cursor='hand2'
                )
                btn.pack(pady=5, padx=20, fill='x')
                
                if not is_current:
                    def on_enter(e, button=btn):
                        button.configure(bg='#5a5a5a')
                    def on_leave(e, button=btn):
                        button.configure(bg='#4a4a4a')
                        
                    btn.bind("<Enter>", on_enter)
                    btn.bind("<Leave>", on_leave)
            
            close_btn = tk.Button(
                settings_window,
                text="Close",
                command=settings_window.destroy,
                bg='#666',
                fg='white',
                font=("Arial", 10),
                relief='flat',
                padx=20,
                pady=8
            )
            close_btn.pack(pady=20)
            
            settings_window.mainloop()
        
        settings_thread = threading.Thread(target=create_settings_window, daemon=True)
        settings_thread.start()
    
    def create_chat_window(self):
        """Create the main chat window"""
        x, y = self.get_position_coordinates(self.settings["position"])
        
        window_config = {
            'title': 'Kick Chat - kinqcollin',
            'url': 'https://kick.com/popout/kinqcollin/chat',
            'width': self.settings["width"],
            'height': self.settings["height"],
            'x': x,
            'y': y,
            'min_size': (300, 400),
            'resizable': True,
            'on_top': True,
            'shadow': True,
            'frameless': False,  # Changed to False to enable proper dragging
            'easy_drag': True
        }
        
        window = webview.create_window(**window_config)
        
        # Simple API class
        class API:
            def close_window(self):
                window.destroy()
            
            def minimize_window(self):
                window.minimize()
            
            def move_window(self, position):
                x, y = self.get_position_coordinates(position)
                window.move(x, y)
                self.settings["position"] = position
                self.save_settings()
        
        api = API()
        
        def on_window_loaded():
            # Expose API functions to JavaScript
            window.expose(api.close_window, api.minimize_window, api.move_window)
            
            js_code = '''
            // Hide the default title bar if it exists and add custom styling
            const style = document.createElement('style');
            style.textContent = `
                /* Hide default title bar elements if present */
                .titlebar, .window-titlebar, [class*="titlebar"] {
                    display: none !important;
                }
                
                .custom-topbar {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 32px;
                    background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
                    border-bottom: 1px solid #333;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0 12px;
                    z-index: 99999;
                    user-select: none;
                    cursor: move;
                    -webkit-app-region: drag;
                }
                
                .topbar-title {
                    color: #fff;
                    font-size: 13px;
                    font-weight: 600;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    opacity: 0.9;
                    flex: 1;
                    pointer-events: none;
                }
                
                .topbar-controls {
                    display: flex;
                    gap: 6px;
                    -webkit-app-region: no-drag;
                }
                
                .topbar-btn {
                    width: 18px;
                    height: 18px;
                    background: #333;
                    border: 1px solid #555;
                    border-radius: 2px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    font-size: 10px;
                    color: #ccc;
                    font-weight: bold;
                    transition: all 0.15s ease;
                    position: relative;
                }
                
                .topbar-btn:hover {
                    background: #444;
                    border-color: #666;
                    color: #fff;
                }
                
                .topbar-btn.settings:hover {
                    background: #4a90e2;
                    border-color: #4a90e2;
                }
                
                .topbar-btn.minimize:hover {
                    background: #53a653;
                    border-color: #53a653;
                }
                
                .topbar-btn.close:hover {
                    background: #f85149;
                    border-color: #f85149;
                }
                
                /* Settings dropdown */
                .settings-dropdown {
                    position: absolute;
                    top: 22px;
                    right: 0;
                    background: #2c2c2c;
                    border: 1px solid #555;
                    border-radius: 4px;
                    min-width: 120px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(-10px);
                    transition: all 0.2s ease;
                    z-index: 100000;
                }
                
                .settings-dropdown.show {
                    opacity: 1;
                    visibility: visible;
                    transform: translateY(0);
                }
                
                .settings-item {
                    padding: 8px 12px;
                    color: #ccc;
                    cursor: pointer;
                    font-size: 11px;
                    border-bottom: 1px solid #444;
                    transition: background 0.15s ease;
                }
                
                .settings-item:last-child {
                    border-bottom: none;
                }
                
                .settings-item:hover {
                    background: #3a3a3a;
                    color: #fff;
                }
                
                .settings-item.active {
                    background: #4a90e2;
                    color: #fff;
                }
                
                /* Push content down for topbar */
                body {
                    padding-top: 32px !important;
                    margin: 0 !important;
                }
                
                /* Kick-style scrollbar */
                ::-webkit-scrollbar {
                    width: 6px;
                }
                
                ::-webkit-scrollbar-track {
                    background: #1a1a1a;
                }
                
                ::-webkit-scrollbar-thumb {
                    background: #53a653;
                    border-radius: 3px;
                }
                
                ::-webkit-scrollbar-thumb:hover {
                    background: #4a9b4a;
                }
                
                /* Auto-login notification */
                .login-status {
                    position: fixed;
                    top: 40px;
                    right: 12px;
                    background: #53a653;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                    z-index: 99998;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                }
                
                .login-status.show {
                    opacity: 1;
                }
            `;
            document.head.appendChild(style);
            
            // Create topbar
            const topbar = document.createElement('div');
            topbar.className = 'custom-topbar';
            topbar.innerHTML = `
                <div class="topbar-title">Kick Chat - kinqcollin</div>
                <div class="topbar-controls">
                    <div class="topbar-btn settings" onclick="toggleSettings()">⚙</div>
                    <div class="topbar-btn minimize" onclick="minimizeWindow()">−</div>
                    <div class="topbar-btn close" onclick="closeWindow()">×</div>
                </div>
            `;
            
            document.body.insertBefore(topbar, document.body.firstChild);
            
            // Create settings dropdown
            const settingsBtn = topbar.querySelector('.settings');
            const settingsDropdown = document.createElement('div');
            settingsDropdown.className = 'settings-dropdown';
            settingsDropdown.innerHTML = `
                <div class="settings-item" onclick="moveToPosition('top_left')">Top Left</div>
                <div class="settings-item" onclick="moveToPosition('top_right')">Top Right</div>
                <div class="settings-item" onclick="moveToPosition('bottom_left')">Bottom Left</div>
                <div class="settings-item" onclick="moveToPosition('bottom_right')">Bottom Right</div>
                <div class="settings-item" onclick="moveToPosition('center')">Center</div>
            `;
            settingsBtn.appendChild(settingsDropdown);
            
            // Check if user is logged in and show status
            setTimeout(() => {
                const loginElements = document.querySelectorAll('[data-testid*="login"], .login, [class*="login"], [href*="login"]');
                const userElements = document.querySelectorAll('[data-testid*="user"], .user-avatar, [class*="avatar"], [class*="user"]');
                
                const loginStatus = document.createElement('div');
                loginStatus.className = 'login-status';
                
                if (userElements.length > 0 && loginElements.length === 0) {
                    loginStatus.textContent = 'Logged in ✓';
                    loginStatus.style.background = '#53a653';
                } else {
                    loginStatus.textContent = 'Not logged in';
                    loginStatus.style.background = '#f85149';
                }
                
                document.body.appendChild(loginStatus);
                loginStatus.classList.add('show');
                
                // Hide after 3 seconds
                setTimeout(() => {
                    loginStatus.classList.remove('show');
                    setTimeout(() => loginStatus.remove(), 300);
                }, 3000);
            }, 2000);
            
            // Functions for buttons
            let settingsOpen = false;
            
            window.toggleSettings = function() {
                const dropdown = document.querySelector('.settings-dropdown');
                settingsOpen = !settingsOpen;
                
                if (settingsOpen) {
                    dropdown.classList.add('show');
                    // Update active position
                    const items = dropdown.querySelectorAll('.settings-item');
                    items.forEach(item => item.classList.remove('active'));
                    
                    // You'd need to get current position from Python here
                    // For now, we'll highlight based on the onclick data
                } else {
                    dropdown.classList.remove('show');
                }
            };
            
            window.moveToPosition = function(position) {
                pywebview.api.move_window(position);
                // Close dropdown
                document.querySelector('.settings-dropdown').classList.remove('show');
                settingsOpen = false;
                
                // Update active state
                const items = document.querySelectorAll('.settings-item');
                items.forEach(item => {
                    item.classList.remove('active');
                    if (item.textContent.toLowerCase().replace(' ', '_') === position) {
                        item.classList.add('active');
                    }
                });
            };
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (settingsOpen && !e.target.closest('.settings')) {
                    document.querySelector('.settings-dropdown').classList.remove('show');
                    settingsOpen = false;
                }
            });
            
            window.closeWindow = function() {
                pywebview.api.close_window();
            };
            
            window.minimizeWindow = function() {
                pywebview.api.minimize_window();
            };
            '''
            
            window.evaluate_js(js_code)
        
        # Start webview with cookies enabled
        webview.start(debug=False, func=on_window_loaded, private_mode=False)

def main():
    try:
        app = KickChatWindow()
        app.create_chat_window()
    except KeyboardInterrupt:
        print("\nClosing application...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()