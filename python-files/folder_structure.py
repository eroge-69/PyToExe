import os

# Define the project structure
structure = {
    "project-root": {
        "assets": {
            "css": {},
            "js": {},
            "images": {}
        },
        "includes": {
            "header.php": "",
            "footer.php": "",
            "db.php": ""
        },
        "views": {
            "home.php": "",
            "login.php": "",
            "dashboard.php": ""
        },
        "uploads": {},  # Empty folder for uploaded files
        "controllers": {
            "auth.php": "",
            "upload.php": ""
        },
        "index.php": "",
        ".htaccess": ""  # Optional routing file
    }
}

# Function to create folders and files recursively
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)

# Start building from current directory
create_structure(".", structure)

print("✅ Project structure created successfully!")
