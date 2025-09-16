
import os
import json
import platform
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import subprocess

# Configuration
THEME_COLOR = "#1a1a2e"
ACCENT_COLOR = "#4e54c8"
SECONDARY_COLOR = "#16213e"
TEXT_COLOR = "#ffffff"
BUTTON_COLOR = "#4e54c8"
BUTTON_HOVER = "#3f43a1"

flags = {
    'DFFlagPlayerHumanoidPropertyUpdateRestrict': False, 
    'DFIntDebugDefaultTargetWorldStepsPerFrame': -2147483648, 
    'DFIntMaxMissedWorldStepsRemembered': -2147483648, 
    'DFIntDebugSendDistInSteps': -2147483648, 
    'DFIntWorldStepMax': -2147483648, 
    'DFIntNetworkOwnershipTimeoutMs': 2500, 
    'DFFlagDebugDisableNetworkExtrapolation': True, 
    'DFFlagDebugDisableVelocityValidation': True, 
    'DFIntPingReportIntervalMs': 1500, 
    'DFIntTaskSchedulerTargetFps': 60, 
    'DFFlagDebugBypassPhysicsOwnershipChecks': True, 
    'FFlagSimIslandizerManager': False, 
    'DFIntS2PhysicsSenderRate': 1, 
    'DFFlagDebugEnableInterpolationVisualizer': True, 
    'FFlagFilterPurchasePromptInputDispatch': True, 
    'FFlagRemovePermissionsButtons': True, 
    'FFlagPlayerListReduceRerenders': True, 
    'FFlagAvatarEditorPromptsNoPromptNoRender': True, 
    'FFlagPlayerListClosedNoRenderWithTenFoot': True, 
    'FFlagUseUserProfileStore4': True, 
    'FFlagPublishAssetPromptNoPromptNoRender': True, 
    'FFlagUnreduxChatTransparencyV2': True, 
    'FFlagChatWindowOnlyRenderMessagesOnce': True, 
    'FFlagUnreduxLastInputTypeChanged': True, 
    'FFlagChatWindowSemiRoduxMessages': True, 
    'FFlagInitializeAutocompleteOnlyIfEnabled': True, 
    'FFlagChatWindowMessageRemoveState': True, 
    'FFlagExpChatUseVoiceParticipantsStore2': True, 
    'FFlagExpChatMemoBillboardGui': True, 
    'FFlagExpChatRemoveBubbleChatAppUserMessagesState': True, 
    'FFlagEnableLeaveGameUpsellEntrypoint': False, 
    'FFlagChatOptimizeCommandProcessing': True, 
    'FFlagMemoizeChatReportingMenu': True
}

def get_roblox_paths():
    paths = []
    sys_name = platform.system()
    if sys_name == 'Windows':
        search_dirs = [
            os.path.expanduser('~\\AppData\\Local\\Roblox\\Versions'), 
            'C:\\Program Files\\Roblox\\Versions', 
            'C:\\Program Files (x86)\\Roblox\\Versions'
        ]
        program_files = os.getenv('ProgramFiles', 'C:\\Program Files')
        program_files_x86 = os.getenv('ProgramFiles(x86)', 'C:\\Program Files (x86)')
        
        if program_files not in search_dirs:
            search_dirs.append(os.path.join(program_files, 'Roblox', 'Versions'))
        if program_files_x86 not in search_dirs:
            search_dirs.append(os.path.join(program_files_x86, 'Roblox', 'Versions'))
        
        for base in search_dirs:
            if not os.path.exists(base):
                continue
            try:
                for d in os.listdir(base):
                    version_dir = os.path.join(base, d)
                    if os.path.isdir(version_dir) and os.path.exists(os.path.join(version_dir, 'RobloxPlayerBeta.exe')):
                        paths.append(version_dir)
                        log_message('✅ Found Roblox client', 'green')
            except Exception:
                continue
        
        if not paths:
            log_message('🔍 No Roblox found in common directories, scanning system...', 'yellow')
            try:
                for root, dirs, files in os.walk(os.path.expanduser('~\\AppData\\Local'), followlinks=False):
                    if 'RobloxPlayerBeta.exe' in files:
                        version_dir = root
                        paths.append(version_dir)
                        log_message('✅ Found Roblox client', 'green')
            except Exception:
                log_message('⚠️ Error scanning', 'yellow')
    return paths

def apply_flags():
    log_message('🔄 Applying flags...', 'blue')
    paths = get_roblox_paths()
    if not paths:
        messagebox.showerror('Error', 'No Roblox installation found!')
        log_message('❌ No Roblox installation found', 'red')
        return
    
    for path in paths:
        client_settings_path = os.path.join(path, 'ClientSettings')
        os.makedirs(client_settings_path, exist_ok=True)
        
        client_app_settings_path = os.path.join(client_settings_path, 'ClientAppSettings.json')
        try:
            with open(client_app_settings_path, 'w') as f:
                json.dump(flags, f, indent=4)
            log_message(f'✅ Applied flags to: {path}', 'green')
        except Exception as e:
            log_message(f'❌ Failed to apply flags to: {path}', 'red')
    
    log_message('✅ All flags applied successfully!', 'green')
    messagebox.showinfo('Success', 'All flags applied successfully!')

def detach_flags():
    log_message('🔄 Detaching flags...', 'blue')
    paths = get_roblox_paths()
    if not paths:
        messagebox.showerror('Error', 'No Roblox installation found!')
        log_message('❌ No Roblox installation found', 'red')
        return
    
    for path in paths:
        client_settings_path = os.path.join(path, 'ClientSettings')
        client_app_settings_path = os.path.join(client_settings_path, 'ClientAppSettings.json')
        
        try:
            if os.path.exists(client_app_settings_path):
                os.remove(client_app_settings_path)
                log_message(f'✅ Removed flags from: {path}', 'green')
        except Exception as e:
            log_message(f'❌ Failed to remove flags from: {path}', 'red')
    
    log_message('✅ All flags detached successfully!', 'green')
    messagebox.showinfo('Success', 'All flags detached successfully!')

def log_message(msg, color='white'):
    status_box.config(state='normal')
    status_box.insert('end', msg + '\n', color)
    status_box.tag_config('white', foreground='#cccccc')
    status_box.tag_config('green', foreground='#4cd964')
    status_box.tag_config('red', foreground='#ff3b30')
    status_box.tag_config('blue', foreground='#5ac8fa')
    status_box.tag_config('yellow', foreground='#ffcc00')
    status_box.config(state='disabled')
    status_box.see('end')

def on_enter(e):
    e.widget['background'] = BUTTON_HOVER

def on_leave(e):
    e.widget['background'] = BUTTON_COLOR

# Create main window
root = tk.Tk()
root.title('Ez Hub x L1ght Hub ANTI HIT')
root.geometry('700x550')
root.configure(bg=THEME_COLOR)
root.resizable(False, False)

# Set window icon (if available)
try:
    root.iconbitmap(default='icon.ico')
except:
    pass

# Header frame
header_frame = tk.Frame(root, bg=THEME_COLOR)
header_frame.pack(fill='x', pady=(20, 10))

# Title
title_label = tk.Label(
    header_frame, 
    text='Ez Hub x L1ght Hub', 
    font=('Segoe UI', 24, 'bold'), 
    fg=TEXT_COLOR, 
    bg=THEME_COLOR
)
title_label.pack()

subtitle_label = tk.Label(
    header_frame, 
    text='ANTI HIT', 
    font=('Segoe UI', 16), 
    fg=ACCENT_COLOR, 
    bg=THEME_COLOR
)
subtitle_label.pack()

# Discord link
discord_label = tk.Label(
    header_frame, 
    text='LAGGY', 
    font=('Segoe UI', 10), 
    fg=TEXT_COLOR, 
    bg=THEME_COLOR,
    cursor='hand2'
)
discord_label.pack(pady=(5, 15))

def open_discord(event):
    import webbrowser
    webbrowser.open('https://discord.gg/Tj94EVatwy')

discord_label.bind('<Button-1>', open_discord)

# Button frame
button_frame = tk.Frame(root, bg=THEME_COLOR)
button_frame.pack(pady=20)

# Apply button
apply_button = tk.Button(
    button_frame, 
    text='ATTACH FLAGS', 
    command=apply_flags,
    font=('Segoe UI', 12, 'bold'),
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    activebackground=BUTTON_HOVER,
    activeforeground=TEXT_COLOR,
    relief='flat',
    width=15,
    height=2,
    cursor='hand2'
)
apply_button.pack(side='left', padx=10)
apply_button.bind('<Enter>', on_enter)
apply_button.bind('<Leave>', on_leave)

# Detach button
detach_button = tk.Button(
    button_frame, 
    text='DETACH FLAGS', 
    command=detach_flags,
    font=('Segoe UI', 12, 'bold'),
    bg=SECONDARY_COLOR,
    fg=TEXT_COLOR,
    activebackground=BUTTON_HOVER,
    activeforeground=TEXT_COLOR,
    relief='flat',
    width=15,
    height=2,
    cursor='hand2'
)
detach_button.pack(side='left', padx=10)
detach_button.bind('<Enter>', on_enter)
detach_button.bind('<Leave>', on_leave)

# Status frame
status_frame = tk.Frame(root, bg=SECONDARY_COLOR, relief='flat', bd=0)
status_frame.pack(pady=(0, 20), padx=25, fill='both', expand=True)

# Status label
status_label = tk.Label(
    status_frame, 
    text='STATUS LOG', 
    font=('Segoe UI', 10, 'bold'), 
    fg=TEXT_COLOR, 
    bg=SECONDARY_COLOR,
    anchor='w'
)
status_label.pack(fill='x', padx=10, pady=(10, 5))

# Status box with scrollbar
status_box_frame = tk.Frame(status_frame, bg=SECONDARY_COLOR)
status_box_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

status_box = tk.Text(
    status_box_frame, 
    height=12, 
    bg='#0f1120', 
    fg='#cccccc', 
    font=('Consolas', 10), 
    relief='flat', 
    wrap='word',
    padx=10,
    pady=10
)
status_box.pack(side='left', fill='both', expand=True)

scrollbar = ttk.Scrollbar(status_box_frame, orient='vertical', command=status_box.yview)
scrollbar.pack(side='right', fill='y')

status_box.config(yscrollcommand=scrollbar.set, state='disabled')

# Footer
footer_frame = tk.Frame(root, bg=THEME_COLOR)
footer_frame.pack(fill='x', pady=(0, 10))

footer_label = tk.Label(
    footer_frame, 
    text='© 2023 Ez Hub x L1ght Hub | ANTI HIT Protection', 
    font=('Segoe UI', 9), 
    fg='#6c757d', 
    bg=THEME_COLOR
)
footer_label.pack()

# Center window on screen
root.update_idletasks()
w, h = root.winfo_width(), root.winfo_height()
x = root.winfo_screenwidth() // 2 - w // 2
y = root.winfo_screenheight() // 2 - h // 2
root.geometry(f'{w}x{h}+{x}+{y}')

# Initial log message
log_message('🚀 Ez Hub x L1ght Hub ANTI HIT initialized', 'blue')
log_message('⚠️ Make sure Roblox is closed before applying flags', 'yellow')

root.mainloop()