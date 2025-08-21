import tkinter as tk
from tkinter import scrolledtext, messagebox, font
import subprocess
import threading

# Try to import PIL for logo support (optional)
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class IntuneUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Intune Group Assignment Checker")
        self.root.geometry("850x750")
        self.root.configure(bg="#f0f4f7")
        
        # Custom fonts
        self.title_font = font.Font(family="Segoe UI", size=12, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=10)
        self.output_font = font.Font(family="Consolas", size=10)
        
        # Header frame with logo placeholder
        header_frame = tk.Frame(self.root, bg="#1e3a5f", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Logo area - add your logo here if PIL is available
        if PIL_AVAILABLE:
            logo_img = Image.open(r"C:\Users\eotten\OneDrive - McGohan Brabender\Desktop\intuneGroupCheck\mcgohan-brabender.jpg")
            logo_img = logo_img.resize((40, 40), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header_frame, image=logo_photo, bg="#1e3a5f")
            logo_label.image = logo_photo  # Keep reference!

        else:
            logo_label = tk.Label(header_frame, text="MB", bg="#1e3a5f", fg="white", font=self.title_font)
        logo_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(header_frame, text="Intune Group Assignment Checker", 
                               bg="#1e3a5f", fg="white", font=self.title_font)
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg="#f0f4f7")
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Action buttons frame
        btn_frame = tk.Frame(main_container, bg="#f0f4f7")
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.install_btn = self.create_styled_button(
            btn_frame, "🔧 Install Modules", self.install_modules, "#2c5282")
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        self.list_groups_btn = self.create_styled_button(
            btn_frame, "📋 List All Groups", self.list_groups, "#2d6a4f")
        self.list_groups_btn.pack(side=tk.LEFT, padx=5)
        
        # Input section with better styling
        input_container = tk.LabelFrame(main_container, text="Search Options", 
                                       bg="#ffffff", fg="#1e3a5f", font=self.button_font,
                                       relief=tk.FLAT, borderwidth=1)
        input_container.pack(fill=tk.X, pady=(0, 10))
        
        # Group name input
        name_frame = tk.Frame(input_container, bg="#ffffff")
        name_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(name_frame, text="Group Name:", bg="#ffffff", width=12, anchor="w").pack(side=tk.LEFT)
        self.group_entry = tk.Entry(name_frame, font=self.button_font, relief=tk.SOLID, bd=1)
        self.group_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.check_btn = self.create_styled_button(
            name_frame, "Search", self.run_check, "#d4a574", width=12)
        self.check_btn.pack(side=tk.LEFT, padx=5)
        
        # Object ID input
        id_frame = tk.Frame(input_container, bg="#ffffff")
        id_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        tk.Label(id_frame, text="Object ID:", bg="#ffffff", width=12, anchor="w").pack(side=tk.LEFT)
        self.id_entry = tk.Entry(id_frame, font=self.button_font, relief=tk.SOLID, bd=1)
        self.id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.check_id_btn = self.create_styled_button(
            id_frame, "Search", self.run_check_by_id, "#9b5de5", width=12)
        self.check_id_btn.pack(side=tk.LEFT, padx=5)
        
        # Filter section
        filter_frame = tk.Frame(main_container, bg="#f0f4f7")
        filter_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(filter_frame, text="🔍 Filter:", bg="#f0f4f7", font=self.button_font).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(filter_frame, font=self.button_font, relief=tk.SOLID, bd=1)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind('<KeyRelease>', self.filter_results)
        
        self.clear_filter_btn = self.create_styled_button(
            filter_frame, "Clear", self.clear_filter, "#6c757d", width=8)
        self.clear_filter_btn.pack(side=tk.LEFT)
        
        # Enhanced output area with frame
        output_frame = tk.LabelFrame(main_container, text="Output", bg="#ffffff", 
                                    fg="#1e3a5f", font=self.button_font,
                                    relief=tk.FLAT, borderwidth=1)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Custom text widget with tags for colored output
        self.results = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD,
            font=self.output_font,
            bg="#1e1e1e",  # Dark background for better contrast
            fg="#ffffff",
            insertbackground="white",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for colored output
        self.setup_text_tags()
        
        self.original_results = ""
        
        # Status bar
        self.status_bar = tk.Label(main_container, text="Ready", bg="#e0e0e0", 
                                  anchor="w", relief=tk.SUNKEN, font=self.button_font)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
    
    def create_styled_button(self, parent, text, command, color, width=15):
        """Create a modern styled button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            font=self.button_font,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5,
            width=width,
            cursor="hand2"
        )
        
        # Hover effects
        def on_enter(e):
            btn['bg'] = self.darken_color(color)
        
        def on_leave(e):
            btn['bg'] = color
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def darken_color(self, color):
        """Darken a hex color by 20%"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * 0.8) for c in rgb)
        return '#%02x%02x%02x' % rgb
    
    def setup_text_tags(self):
        """Configure text tags for colored output"""
        self.results.tag_config("header", foreground="#00d4ff", font=("Consolas", 11, "bold"))
        self.results.tag_config("success", foreground="#00ff00")
        self.results.tag_config("warning", foreground="#ffaa00")
        self.results.tag_config("error", foreground="#ff5555")
        self.results.tag_config("info", foreground="#88aaff")
        self.results.tag_config("cyan", foreground="#00ffff")
        self.results.tag_config("magenta", foreground="#ff00ff")
        self.results.tag_config("yellow", foreground="#ffff00")
        self.results.tag_config("gray", foreground="#888888")
        self.results.tag_config("white", foreground="#ffffff")
        self.results.tag_config("item", foreground="#ffffff", lmargin1=20, lmargin2=40)
        self.results.tag_config("subitem", foreground="#aaaaaa", lmargin1=40, lmargin2=60)
    
    def format_output(self, text):
        """Parse and format PowerShell output with colors"""
        self.results.delete(1.0, tk.END)
        lines = text.split('\n')
        
        for line in lines:
            # Headers
            if '===' in line:
                if 'APPS' in line:
                    self.insert_colored_line(line, "cyan")
                elif 'SCRIPTS' in line:
                    self.insert_colored_line(line, "magenta")
                elif 'CONFIGURATION' in line:
                    self.insert_colored_line(line, "success")
                elif 'MEMBERS' in line:
                    self.insert_colored_line(line, "yellow")
                elif 'SUMMARY' in line:
                    self.insert_colored_line(line, "header")
                else:
                    self.insert_colored_line(line, "header")
            
            # Items with bullets
            elif line.strip().startswith('•'):
                self.insert_colored_line(line, "item")
            
            # IDs and sub-items
            elif 'ID:' in line or line.strip().startswith('File:'):
                self.insert_colored_line(line, "subitem")
            
            # Status messages
            elif 'Found' in line and 'groups' in line:
                self.insert_colored_line(line, "info")
            elif 'No' in line and ('assigned' in line or 'found' in line):
                self.insert_colored_line(line, "gray")
            elif 'Error' in line or 'ERROR' in line:
                self.insert_colored_line(line, "error")
            elif 'Installing' in line or 'Loading' in line or 'Checking' in line:
                self.insert_colored_line(line, "warning")
            elif 'success' in line.lower() or 'found exact match' in line.lower():
                self.insert_colored_line(line, "success")
            
            # Member entries with icons or brackets
            elif '👤' in line or '💻' in line or '[User]' in line or '[Device]' in line:
                # Replace broken emojis with cleaner symbols
                line = line.replace('??', '►')
                line = line.replace('👤', '►')
                line = line.replace('💻', '▪')
                line = line.replace('🔹', '•')
                self.insert_colored_line(line, "white")
            
            # Group info
            elif 'Name:' in line or 'Group:' in line:
                self.insert_colored_line(line, "info")
            
            # Summary counts
            elif 'Apps:' in line and 'Scripts:' in line:
                self.insert_colored_line(line, "yellow")
            elif 'Total members:' in line:
                self.insert_colored_line(line, "yellow")
            
            # Default
            else:
                self.insert_colored_line(line, "white")
    
    def insert_colored_line(self, text, tag):
        """Insert a line with specified color tag"""
        self.results.insert(tk.END, text + '\n', tag)
        self.results.see(tk.END)
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def install_modules(self):
        self.install_btn.config(state='disabled', text='Installing...')
        self.update_status("Installing Microsoft Graph modules...")
        self.results.delete(1.0, tk.END)
        self.insert_colored_line("Installing required modules...", "warning")
        self.original_results = ""
        threading.Thread(target=self.execute_install, daemon=True).start()
    
    def execute_install(self):
        ps_script = '''
        Write-Host "Installing Microsoft Graph modules..." -ForegroundColor Yellow
        Install-Module Microsoft.Graph.Authentication, Microsoft.Graph.Groups, Microsoft.Graph.DeviceManagement, Microsoft.Graph.Beta.DeviceManagement -Force -AllowClobber -Scope CurrentUser
        Write-Host "All modules installed successfully!" -ForegroundColor Green
        '''
        try:
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=120)
            self.root.after(0, self.update_install_results, result.stdout or result.stderr)
        except Exception as e:
            self.root.after(0, self.update_install_results, f"Install Error: {str(e)}")
    
    def update_install_results(self, text):
        self.original_results = text
        self.format_output(text)
        self.install_btn.config(state='normal', text='🔧 Install Modules')
        self.update_status("Installation complete")
    
    def list_groups(self):
        self.list_groups_btn.config(state='disabled', text='Loading...')
        self.update_status("Fetching all groups...")
        self.results.delete(1.0, tk.END)
        self.insert_colored_line("Loading all groups...", "warning")
        self.original_results = ""
        threading.Thread(target=self.execute_list_groups, daemon=True).start()
    
    def execute_list_groups(self):
        ps_script = '''
        Connect-MgGraph -Scopes "Group.Read.All", "GroupMember.Read.All" -NoWelcome
        
        Write-Host "=== ALL GROUPS ===" -ForegroundColor Green
        $groups = Get-MgGroup -All | Sort-Object DisplayName
        Write-Host "Found $($groups.Count) total groups:`n" -ForegroundColor Yellow
        
        foreach ($group in $groups) {
            Write-Host "• $($group.DisplayName)" -ForegroundColor White
            Write-Host "  ID: $($group.Id)" -ForegroundColor Gray
        }
        '''
        try:
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=120)
            self.root.after(0, self.update_list_groups_results, result.stdout or result.stderr)
        except Exception as e:
            self.root.after(0, self.update_list_groups_results, f"List Groups Error: {str(e)}")
    
    def update_list_groups_results(self, text):
        self.original_results = text
        self.format_output(text)
        self.list_groups_btn.config(state='normal', text='📋 List All Groups')
        
        # Count groups
        count = text.count('•')
        self.update_status(f"Found {count} groups")
    
    def filter_results(self, event=None):
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.format_output(self.original_results)
        else:
            lines = self.original_results.split('\n')
            filtered_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                if search_term in line.lower():
                    filtered_lines.append(line)
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith("ID: "):
                        filtered_lines.append(lines[i + 1])
                        i += 2
                    else:
                        i += 1
                else:
                    i += 1
            
            if filtered_lines:
                filtered_text = '\n'.join(filtered_lines)
                filter_info = f">>> Showing results containing '{search_term}' <<<\n\n"
                self.results.delete(1.0, tk.END)
                self.insert_colored_line(filter_info, "header")
                self.format_output(filtered_text)
                self.update_status(f"Filtered: {len(filtered_lines)} results")
            else:
                self.results.delete(1.0, tk.END)
                self.insert_colored_line(f"No results found for '{search_term}'", "warning")
                self.update_status("No results found")
    
    def clear_filter(self):
        self.search_entry.delete(0, tk.END)
        if self.original_results:
            self.format_output(self.original_results)
            self.update_status("Filter cleared")
    
    def run_check(self):
        group_name = self.group_entry.get().strip()
        if not group_name:
            messagebox.showwarning("Warning", "Please enter a group name")
            return
            
        self.check_btn.config(state='disabled', text='Checking...')
        self.update_status(f"Checking assignments for '{group_name}'...")
        self.results.delete(1.0, tk.END)
        self.insert_colored_line(f"Checking assignments for '{group_name}'...", "warning")
        self.original_results = ""
        threading.Thread(target=self.execute_ps, args=(group_name,), daemon=True).start()
    
    def run_check_by_id(self):
        group_id = self.id_entry.get().strip()
        if not group_id:
            messagebox.showwarning("Warning", "Please enter a group Object ID")
            return
            
        self.check_id_btn.config(state='disabled', text='Checking...')
        self.update_status(f"Checking assignments for ID '{group_id}'...")
        self.results.delete(1.0, tk.END)
        self.insert_colored_line(f"Checking assignments for Object ID '{group_id}'...", "warning")
        self.original_results = ""
        threading.Thread(target=self.execute_ps_by_id, args=(group_id,), daemon=True).start()
    
    # [execute_ps and execute_ps_by_id methods remain the same as original]
    
    def execute_ps(self, group_name):
        ps_script = f'''
        Connect-MgGraph -Scopes "Group.Read.All", "GroupMember.Read.All", "DeviceManagementApps.Read.All", "DeviceManagementConfiguration.Read.All", "User.Read.All", "Device.Read.All", "Directory.Read.All" -NoWelcome
        Import-Module Microsoft.Graph.Beta.DeviceManagement -Force -ErrorAction SilentlyContinue
        
        Write-Host "Looking for group: {group_name}" -ForegroundColor Yellow
        
        Write-Host "Trying exact match..." -ForegroundColor Gray
        $group = Get-MgGroup -Filter "displayName eq '{group_name}'" -ErrorAction SilentlyContinue
        
        if ($group) {{
            Write-Host "Found exact match!" -ForegroundColor Green
            Write-Host "Name: '$($group.DisplayName)'" -ForegroundColor White
            Write-Host "ID: '$($group.Id)'" -ForegroundColor White
        }} else {{
            Write-Host "No exact match found, trying partial search..." -ForegroundColor Yellow
            $groups = Get-MgGroup -All | Where-Object {{ $_.DisplayName -like "*{group_name}*" }}
            
            Write-Host "Partial search found $($groups.Count) groups" -ForegroundColor Gray
            
            if ($groups.Count -eq 1) {{
                $group = $groups[0]
                Write-Host "Found one similar group:" -ForegroundColor Green
                Write-Host "Name: '$($group.DisplayName)'" -ForegroundColor White
                Write-Host "ID: '$($group.Id)'" -ForegroundColor White
            }} elseif ($groups.Count -gt 1) {{
                Write-Host "Multiple groups found:" -ForegroundColor Yellow
                foreach ($g in $groups) {{ 
                    Write-Host "  • '$($g.DisplayName)' (ID: $($g.Id))" -ForegroundColor White
                }}
                Write-Host "Please use exact group name from above list." -ForegroundColor Yellow
                exit
            }} else {{
                Write-Host "No groups found matching '{group_name}'" -ForegroundColor Red
                Write-Host "Try searching for part of the group name." -ForegroundColor Yellow
                exit
            }}
        }}
        
        if (!$group -or !$group.Id -or !$group.DisplayName) {{
            Write-Host "ERROR: Group object is invalid or incomplete!" -ForegroundColor Red
            Write-Host "Group object: $($group | ConvertTo-Json)" -ForegroundColor Gray
            exit
        }}
        
        $groupId = $group.Id
        $groupName = $group.DisplayName
        
        Write-Host "`nPROCEEDING WITH:" -ForegroundColor Green
        Write-Host "Group Name: $groupName" -ForegroundColor White
        Write-Host "Group ID: $groupId" -ForegroundColor White
        
        $foundAny = $false
        
        # Apps
        Write-Host "`n=== APPS assigned to '$groupName' ===" -ForegroundColor Cyan
        $apps = Get-MgDeviceAppManagementMobileApp
        $appCount = 0
        foreach ($app in $apps) {{
            $assignments = Get-MgDeviceAppManagementMobileAppAssignment -MobileAppId $app.Id -ErrorAction SilentlyContinue
            $matchingAssignment = $assignments | Where-Object {{ 
                $_.Target.GroupId -eq $groupId -or 
                $_.Target.AdditionalProperties.groupId -eq $groupId 
            }}
            if ($matchingAssignment) {{
                $intent = $matchingAssignment.Intent
                $targetType = if ($matchingAssignment.Target.'@odata.type' -like "*user*") {{ "[User]" }} else {{ "[Device]" }}
                Write-Host "• $($app.DisplayName) [$intent] $targetType" -ForegroundColor White
                $appCount++
                $foundAny = $true
            }}
        }}
        if ($appCount -eq 0) {{ Write-Host "No apps assigned" -ForegroundColor Gray }}
        
        # Scripts
        Write-Host "`n=== SCRIPTS assigned to '$groupName' ===" -ForegroundColor Magenta
        $scriptCount = 0
        if (Get-Command Get-MgBetaDeviceManagementScript -ErrorAction SilentlyContinue) {{
            $scripts = Get-MgBetaDeviceManagementScript
            foreach ($script in $scripts) {{
                $scriptAssignments = Get-MgBetaDeviceManagementScriptGroupAssignment -DeviceManagementScriptId $script.Id -ErrorAction SilentlyContinue
                $matchingScriptAssignment = $scriptAssignments | Where-Object {{ $_.TargetGroupId -eq $groupId }}
                if ($matchingScriptAssignment) {{
                    Write-Host "• $($script.DisplayName)" -ForegroundColor White
                    if ($script.FileName) {{ Write-Host "  File: $($script.FileName)" -ForegroundColor Gray }}
                    $scriptCount++
                    $foundAny = $true
                }}
            }}
        }}
        if ($scriptCount -eq 0) {{ Write-Host "No scripts assigned" -ForegroundColor Gray }}
        
        # Configs
        Write-Host "`n=== CONFIGURATION PROFILES assigned to '$groupName' ===" -ForegroundColor Green
        $configs = Get-MgDeviceManagementDeviceConfiguration
        $configCount = 0
        foreach ($config in $configs) {{
            $configAssignments = Get-MgDeviceManagementDeviceConfigurationAssignment -DeviceConfigurationId $config.Id -ErrorAction SilentlyContinue
            $matchingConfigAssignment = $configAssignments | Where-Object {{ 
                $_.Target.GroupId -eq $groupId -or $_.Target.AdditionalProperties.groupId -eq $groupId 
            }}
            if ($matchingConfigAssignment) {{
                Write-Host "• $($config.DisplayName)" -ForegroundColor White
                $configCount++
                $foundAny = $true
            }}
        }}
        if ($configCount -eq 0) {{ Write-Host "No configuration profiles assigned" -ForegroundColor Gray }}
        
        # Members - Enhanced version
        Write-Host "`n=== GROUP MEMBERS ===" -ForegroundColor Yellow
        try {{
            $members = Get-MgGroupMember -GroupId $groupId -All -ErrorAction SilentlyContinue
            if ($members) {{
                $memberCount = 0
                foreach ($member in $members) {{
                    $memberCount++
                    $memberType = "Unknown"
                    $memberName = "Unknown"
                    $memberEmail = ""
                    $memberIcon = "•"
                    
                    if ($member.'@odata.type' -eq '#microsoft.graph.user') {{
                        $memberType = "User"
                        $memberIcon = "►"
                        try {{
                            $userDetails = Get-MgUser -UserId $member.Id -ErrorAction SilentlyContinue
                            if ($userDetails) {{
                                $memberName = $userDetails.DisplayName
                                $memberEmail = if ($userDetails.UserPrincipalName) {{ " ($($userDetails.UserPrincipalName))" }} else {{ "" }}
                            }}
                        }} catch {{
                            $memberName = "User (Limited Access)"
                        }}
                    }} elseif ($member.'@odata.type' -eq '#microsoft.graph.device') {{
                        $memberType = "Device"
                        $memberIcon = "▪"
                        try {{
                            $deviceDetails = Get-MgDevice -DeviceId $member.Id -ErrorAction SilentlyContinue
                            if ($deviceDetails -and $deviceDetails.DisplayName) {{
                                $memberName = $deviceDetails.DisplayName
                            }} else {{
                                $memberName = "Device (No Name)"
                            }}
                        }} catch {{
                            $memberName = "Device (Limited Access)"
                        }}
                    }} else {{
                        # Try to determine type by querying both APIs
                        try {{
                            $deviceDetails = Get-MgDevice -DeviceId $member.Id -ErrorAction Stop
                            $memberType = "Device"
                            $memberIcon = "▪"
                            $memberName = if ($deviceDetails.DisplayName) {{ $deviceDetails.DisplayName }} else {{ "Device (No Name)" }}
                        }} catch {{
                            try {{
                                $userDetails = Get-MgUser -UserId $member.Id -ErrorAction Stop
                                $memberType = "User"
                                $memberIcon = "►"
                                $memberName = $userDetails.DisplayName
                                $memberEmail = if ($userDetails.UserPrincipalName) {{ " ($($userDetails.UserPrincipalName))" }} else {{ "" }}
                            }} catch {{
                                # Fallback to member object properties
                                if ($member.DisplayName) {{
                                    $memberName = $member.DisplayName
                                }}
                                if ($member.UserPrincipalName) {{
                                    $memberType = "User"
                                    $memberIcon = "►"
                                    $memberEmail = " ($($member.UserPrincipalName))"
                                }} elseif ($member.DeviceId -or $member.TrustType) {{
                                    $memberType = "Device"
                                    $memberIcon = "▪"
                                }}
                            }}
                        }}
                    }}
                    
                    if ($memberName -eq "Unknown" -or $memberName -eq "") {{
                        Write-Host "$memberIcon [$memberType] ID: $($member.Id)" -ForegroundColor White
                    }} else {{
                        Write-Host "$memberIcon [$memberType] $memberName$memberEmail" -ForegroundColor White
                        Write-Host "   ID: $($member.Id)" -ForegroundColor Gray
                    }}
                }}
                
                Write-Host "`nTotal members: $memberCount" -ForegroundColor Yellow
            }} else {{
                Write-Host "No members in this group" -ForegroundColor Gray
            }}
        }} catch {{
            Write-Host "Error getting group members: $($_.Exception.Message)" -ForegroundColor Red
        }}

        
        # Summary
        Write-Host "`n=== SUMMARY ===" -ForegroundColor Yellow
        Write-Host "Group: $groupName" -ForegroundColor White
        Write-Host "Apps: $appCount | Scripts: $scriptCount | Configs: $configCount" -ForegroundColor White
        
        if (!$foundAny) {{
            Write-Host "`nThis group has no Intune assignments." -ForegroundColor Yellow
        }}
        '''
        
        try:
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=120)
            self.root.after(0, self.update_results, result.stdout or result.stderr)
        except Exception as e:
            self.root.after(0, self.update_results, f"Error: {str(e)}")
    
    def execute_ps_by_id(self, group_id):
        # Similar to execute_ps but with group_id parameter
        # [Keep the same implementation as in original code]
        ps_script = f'''
        Connect-MgGraph -Scopes "Group.Read.All", "GroupMember.Read.All", "DeviceManagementApps.Read.All", "DeviceManagementConfiguration.Read.All", "User.Read.All", "Device.Read.All", "Directory.Read.All" -NoWelcome
        Import-Module Microsoft.Graph.Beta.DeviceManagement -Force -ErrorAction SilentlyContinue
        
        Write-Host "Getting group by Object ID: {group_id}" -ForegroundColor Yellow
        
        try {{
            $group = Get-MgGroup -GroupId "{group_id}" -ErrorAction Stop
            Write-Host "Found group!" -ForegroundColor Green
            Write-Host "Name: '$($group.DisplayName)'" -ForegroundColor White
            Write-Host "ID: '$($group.Id)'" -ForegroundColor White
        }} catch {{
            Write-Host "ERROR: Group with ID '{group_id}' not found!" -ForegroundColor Red
            Write-Host "Error details: $($_.Exception.Message)" -ForegroundColor Gray
            exit
        }}
        
        $groupId = $group.Id
        $groupName = $group.DisplayName
        
        Write-Host "`nPROCEEDING WITH:" -ForegroundColor Green
        Write-Host "Group Name: $groupName" -ForegroundColor White
        Write-Host "Group ID: $groupId" -ForegroundColor White
        
        $foundAny = $false
        
        # Apps
        Write-Host "`n=== APPS assigned to '$groupName' ===" -ForegroundColor Cyan
        $apps = Get-MgDeviceAppManagementMobileApp
        $appCount = 0
        foreach ($app in $apps) {{
            $assignments = Get-MgDeviceAppManagementMobileAppAssignment -MobileAppId $app.Id -ErrorAction SilentlyContinue
            $matchingAssignment = $assignments | Where-Object {{ 
                $_.Target.GroupId -eq $groupId -or 
                $_.Target.AdditionalProperties.groupId -eq $groupId 
            }}
            if ($matchingAssignment) {{
                $intent = $matchingAssignment.Intent
                $targetType = if ($matchingAssignment.Target.'@odata.type' -like "*user*") {{ "[User]" }} else {{ "[Device]" }}
                Write-Host "• $($app.DisplayName) [$intent] $targetType" -ForegroundColor White
                $appCount++
                $foundAny = $true
            }}
        }}
        if ($appCount -eq 0) {{ Write-Host "No apps assigned" -ForegroundColor Gray }}
        
        # Scripts
        Write-Host "`n=== SCRIPTS assigned to '$groupName' ===" -ForegroundColor Magenta
        $scriptCount = 0
        if (Get-Command Get-MgBetaDeviceManagementScript -ErrorAction SilentlyContinue) {{
            $scripts = Get-MgBetaDeviceManagementScript
            foreach ($script in $scripts) {{
                $scriptAssignments = Get-MgBetaDeviceManagementScriptGroupAssignment -DeviceManagementScriptId $script.Id -ErrorAction SilentlyContinue
                $matchingScriptAssignment = $scriptAssignments | Where-Object {{ $_.TargetGroupId -eq $groupId }}
                if ($matchingScriptAssignment) {{
                    Write-Host "• $($script.DisplayName)" -ForegroundColor White
                    if ($script.FileName) {{ Write-Host "  File: $($script.FileName)" -ForegroundColor Gray }}
                    $scriptCount++
                    $foundAny = $true
                }}
            }}
        }}
        if ($scriptCount -eq 0) {{ Write-Host "No scripts assigned" -ForegroundColor Gray }}
        
        # Configs
        Write-Host "`n=== CONFIGURATION PROFILES assigned to '$groupName' ===" -ForegroundColor Green
        $configs = Get-MgDeviceManagementDeviceConfiguration
        $configCount = 0
        foreach ($config in $configs) {{
            $configAssignments = Get-MgDeviceManagementDeviceConfigurationAssignment -DeviceConfigurationId $config.Id -ErrorAction SilentlyContinue
            $matchingConfigAssignment = $configAssignments | Where-Object {{ 
                $_.Target.GroupId -eq $groupId -or $_.Target.AdditionalProperties.groupId -eq $groupId 
            }}
            if ($matchingConfigAssignment) {{
                Write-Host "• $($config.DisplayName)" -ForegroundColor White
                $configCount++
                $foundAny = $true
            }}
        }}
        if ($configCount -eq 0) {{ Write-Host "No configuration profiles assigned" -ForegroundColor Gray }}
        
        # Members - Enhanced version (same as execute_ps)
        Write-Host "`n=== GROUP MEMBERS ===" -ForegroundColor Yellow
        try {{
            $members = Get-MgGroupMember -GroupId $groupId -All -ErrorAction SilentlyContinue
            if ($members) {{
                $memberCount = 0
                foreach ($member in $members) {{
                    $memberCount++
                    $memberType = "Unknown"
                    $memberName = "Unknown"
                    $memberEmail = ""
                    $memberIcon = "•"
                    
                    if ($member.'@odata.type' -eq '#microsoft.graph.user') {{
                        $memberType = "User"
                        $memberIcon = "►"
                        try {{
                            $userDetails = Get-MgUser -UserId $member.Id -ErrorAction SilentlyContinue
                            if ($userDetails) {{
                                $memberName = $userDetails.DisplayName
                                $memberEmail = if ($userDetails.UserPrincipalName) {{ " ($($userDetails.UserPrincipalName))" }} else {{ "" }}
                            }}
                        }} catch {{
                            $memberName = "User (Limited Access)"
                        }}
                    }} elseif ($member.'@odata.type' -eq '#microsoft.graph.device') {{
                        $memberType = "Device"
                        $memberIcon = "▪"
                        try {{
                            $deviceDetails = Get-MgDevice -DeviceId $member.Id -ErrorAction SilentlyContinue
                            if ($deviceDetails -and $deviceDetails.DisplayName) {{
                                $memberName = $deviceDetails.DisplayName
                            }} else {{
                                $memberName = "Device (No Name)"
                            }}
                        }} catch {{
                            $memberName = "Device (Limited Access)"
                        }}
                    }} else {{
                        # Try to determine type by querying both APIs
                        try {{
                            $deviceDetails = Get-MgDevice -DeviceId $member.Id -ErrorAction Stop
                            $memberType = "Device"
                            $memberIcon = "▪"
                            $memberName = if ($deviceDetails.DisplayName) {{ $deviceDetails.DisplayName }} else {{ "Device (No Name)" }}
                        }} catch {{
                            try {{
                                $userDetails = Get-MgUser -UserId $member.Id -ErrorAction Stop
                                $memberType = "User"
                                $memberIcon = "►"
                                $memberName = $userDetails.DisplayName
                                $memberEmail = if ($userDetails.UserPrincipalName) {{ " ($($userDetails.UserPrincipalName))" }} else {{ "" }}
                            }} catch {{
                                # Fallback to member object properties
                                if ($member.DisplayName) {{
                                    $memberName = $member.DisplayName
                                }}
                                if ($member.UserPrincipalName) {{
                                    $memberType = "User"
                                    $memberIcon = "►"
                                    $memberEmail = " ($($member.UserPrincipalName))"
                                }} elseif ($member.DeviceId -or $member.TrustType) {{
                                    $memberType = "Device"
                                    $memberIcon = "▪"
                                }}
                            }}
                        }}
                    }}
                    
                    if ($memberName -eq "Unknown" -or $memberName -eq "") {{
                        Write-Host "$memberIcon [$memberType] ID: $($member.Id)" -ForegroundColor White
                    }} else {{
                        Write-Host "$memberIcon [$memberType] $memberName$memberEmail" -ForegroundColor White
                        Write-Host "   ID: $($member.Id)" -ForegroundColor Gray
                    }}
                }}
                
                Write-Host "`nTotal members: $memberCount" -ForegroundColor Yellow
            }} else {{
                Write-Host "No members in this group" -ForegroundColor Gray
            }}
        }} catch {{
            Write-Host "Error getting group members: $($_.Exception.Message)" -ForegroundColor Red
        }}

        
        # Summary
        Write-Host "`n=== SUMMARY ===" -ForegroundColor Yellow
        Write-Host "Group: $groupName" -ForegroundColor White
        Write-Host "Apps: $appCount | Scripts: $scriptCount | Configs: $configCount" -ForegroundColor White
        
        if (!$foundAny) {{
            Write-Host "`nThis group has no Intune assignments." -ForegroundColor Yellow
        }}
        '''
        
        try:
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, timeout=120)
            self.root.after(0, self.update_results_by_id, result.stdout or result.stderr)
        except Exception as e:
            self.root.after(0, self.update_results_by_id, f"Error: {str(e)}")
    
    def update_results(self, text):
        self.original_results = text
        self.format_output(text)
        self.check_btn.config(state='normal', text='Search')
        self.update_status("Search complete")
    
    def update_results_by_id(self, text):
        self.original_results = text
        self.format_output(text)
        self.check_id_btn.config(state='normal', text='Search')
        self.update_status("Search complete")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    # Note: PIL/Pillow is optional for logo support
    # Install with: python -m pip install Pillow
    app = IntuneUI()
    app.run()