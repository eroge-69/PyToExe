import os
import json
import uuid
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class AIAppBuilder:
    def __init__(self):
        self.projects = {}
        self.templates = self.load_templates()
        
    def load_templates(self):
        """Load templates for different app types"""
        return {
            "mobile": {
                "framework": "react-native",
                "template_path": "templates/mobile"
            },
            "website": {
                "framework": "react",
                "template_path": "templates/website"
            },
            "desktop": {
                "framework": "electron",
                "template_path": "templates/desktop"
            },
            "ai_agent": {
                "framework": "python",
                "template_path": "templates/ai_agent"
            }
        }
    
    def create_project(self, prompt, app_type):
        """Step 1: Create project from prompt"""
        project_id = str(uuid.uuid4())[:8]
        project = {
            "id": project_id,
            "name": f"app_{project_id}",
            "type": app_type,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
            "status": "generating",
            "code": "",
            "path": f"projects/{project_id}"
        }
        
        # Generate code based on prompt and app type
        project["code"] = self.generate_code(prompt, app_type)
        
        # Create project directory
        os.makedirs(project["path"], exist_ok=True)
        
        # Save project metadata
        with open(f"{project['path']}/project.json", "w") as f:
            json.dump(project, f, indent=2)
        
        self.projects[project_id] = project
        return project_id
    
    def generate_code(self, prompt, app_type):
        """Generate code based on prompt and app type"""
        # In a real implementation, this would use an AI model
        # For this prototype, we'll use template-based generation
        
        template = self.templates.get(app_type, {})
        
        # Simulate AI code generation
        if app_type == "mobile":
            return f"""// App generated from prompt: {prompt}
import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

const App = () => {{
  return (
    <View style={{styles.container}}>
      <Text style={{styles.text}}>Hello from your {prompt} app!</Text>
    </View>
  );
}};

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5fcff'
  }},
  text: {{
    fontSize: 20,
    textAlign: 'center',
    margin: 10
  }}
}});

export default App;
"""
        elif app_type == "website":
            return f"""<!-- Website generated from prompt: {prompt} -->
<!DOCTYPE html>
<html>
<head>
    <title>{prompt} Website</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f0f0f0;
        }}
        .container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to your {prompt} website!</h1>
        <p>This website was generated from your prompt.</p>
    </div>
</body>
</html>
"""
        elif app_type == "desktop":
            return f"""// Desktop app generated from prompt: {prompt}
const {{ app, BrowserWindow }} = require('electron');
const path = require('path');

function createWindow () {{
  const win = new BrowserWindow({{
    width: 800,
    height: 600,
    webPreferences: {{
      nodeIntegration: true
    }}
  }});

  win.loadFile('index.html');
  win.webContents.on('did-finish-load', () => {{
    win.webContents.executeJavaScript(`
      document.body.innerHTML = '<h1>Hello from your {prompt} desktop app!</h1>';
    `);
  }});
}}

app.whenReady().then(createWindow);
"""
        elif app_type == "ai_agent":
            return f"""# AI Agent generated from prompt: {prompt}
import openai
import sys

class AIAgent:
    def __init__(self):
        self.name = "{prompt} Agent"
        # Initialize with your API key
        # openai.api_key = 'your-api-key'
    
    def process_input(self, input_text):
        '''Process user input and generate response'''
        # In a real implementation, this would call an AI API
        response = f"Hello! I am your {prompt} AI Agent. You said: {{input_text}}"
        return response

if __name__ == "__main__":
    agent = AIAgent()
    print("AI Agent started. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        response = agent.process_input(user_input)
        print(f"Agent: {{response}}")
"""
        else:
            return f"# Code for {app_type} app based on prompt: {prompt}"
    
    def build_project(self, project_id):
        """Step 2: Build the project into an executable app"""
        if project_id not in self.projects:
            return False, "Project not found"
        
        project = self.projects[project_id]
        project_path = project["path"]
        
        # Create the appropriate files based on app type
        if project["type"] == "mobile":
            with open(f"{project_path}/App.js", "w") as f:
                f.write(project["code"])
            # In a real implementation, we would run react-native build commands
            print(f"Building React Native app at {project_path}")
            
        elif project["type"] == "website":
            with open(f"{project_path}/index.html", "w") as f:
                f.write(project["code"])
            print(f"Website built at {project_path}/index.html")
            
        elif project["type"] == "desktop":
            with open(f"{project_path}/main.js", "w") as f:
                f.write(project["code"])
            # Create package.json for Electron app
            package_json = {
                "name": project["name"],
                "version": "1.0.0",
                "main": "main.js",
                "scripts": {
                    "start": "electron ."
                }
            }
            with open(f"{project_path}/package.json", "w") as f:
                json.dump(package_json, f, indent=2)
            print(f"Desktop app built at {project_path}")
            
        elif project["type"] == "ai_agent":
            with open(f"{project_path}/agent.py", "w") as f:
                f.write(project["code"])
            print(f"AI Agent built at {project_path}/agent.py")
        
        project["status"] = "built"
        self._update_project(project)
        return True, "Build successful"
    
    def preview_project(self, project_id):
        """Step 3: Preview the project"""
        if project_id not in self.projects:
            return False, "Project not found"
        
        project = self.projects[project_id]
        
        if project["type"] == "website":
            # For a website, we can open it in a browser
            import webbrowser
            url = f"file://{os.path.abspath(project['path'])}/index.html"
            webbrowser.open(url)
            return True, f"Opening website preview: {url}"
        
        elif project["type"] in ["mobile", "desktop"]:
            # For mobile and desktop, we would need emulators
            return True, f"To preview this {project['type']} app, you would need an emulator."
        
        elif project["type"] == "ai_agent":
            # For AI agent, we can run it in a subprocess
            try:
                result = subprocess.run(
                    ["python", f"{project['path']}/agent.py"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return True, f"AI Agent output:\n{result.stdout}"
            except subprocess.TimeoutExpired:
                return True, "AI Agent started successfully (process stopped after 10 seconds)"
        
        return False, "Preview not available for this app type"
    
    def update_project(self, project_id, new_prompt):
        """Update an existing project with a new prompt"""
        if project_id not in self.projects:
            return False, "Project not found"
        
        project = self.projects[project_id]
        project["prompt"] = new_prompt
        project["code"] = self.generate_code(new_prompt, project["type"])
        project["status"] = "updated"
        
        self._update_project(project)
        return True, "Project updated successfully"
    
    def _update_project(self, project):
        """Update project metadata file"""
        with open(f"{project['path']}/project.json", "w") as f:
            json.dump(project, f, indent=2)
        self.projects[project["id"]] = project
    
    def list_projects(self):
        """List all created projects"""
        return [{"id": p["id"], "name": p["name"], "type": p["type"], "status": p["status"]} 
                for p in self.projects.values()]

# Example usage
def main():
    builder = AIAppBuilder()
    
    print("=== AI App Builder Demo ===\n")
    
    # Step 1: Create a project from a prompt
    print("Step 1: Creating a website from prompt...")
    project_id = builder.create_project(
        "A personal portfolio website", 
        "website"
    )
    print(f"Created project with ID: {project_id}\n")
    
    # Step 2: Build the project
    print("Step 2: Building project...")
    success, message = builder.build_project(project_id)
    print(f"Build result: {message}\n")
    
    # Step 3: Preview the project
    print("Step 3: Previewing project...")
    success, message = builder.preview_project(project_id)
    print(f"Preview: {message}\n")
    
    # List all projects
    print("All projects:")
    projects = builder.list_projects()
    for project in projects:
        print(f" - {project['name']} ({project['type']}): {project['status']}")
    
    # Example of updating a project
    print("\nUpdating project with new prompt...")
    success, message = builder.update_project(
        project_id, 
        "An updated portfolio website with dark mode"
    )
    print(f"Update: {message}")
    
    # Rebuild the updated project
    success, message = builder.build_project(project_id)
    print(f"Rebuild: {message}")

if __name__ == "__main__":
    main()