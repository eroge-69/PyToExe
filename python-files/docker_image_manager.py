# docker_image_manager.py

import tkinter as tk
from tkinter import messagebox
import easygui
import yaml
import subprocess
import re


def run_command(command):
    """Run a shell command, return True if success, else False and error message."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def parse_images_from_compose(file_path):
    """Parse docker-compose.yaml and extract all image names."""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)
    images = []
    services = data.get('services', {})
    for service_name, service_data in services.items():
        image = service_data.get('image')
        if image:
            images.append(image)
    return images


def extract_image_name_tag(image):
    """
    Given image string like 'nginx:latest' or 'registry.com/repo/image:tag'
    return (image_name, tag) tuple.
    If no tag, default to 'latest'
    """
    # Regex to split into repo/image and tag parts
    match = re.match(r'([^:]+)(?::(.+))?', image)
    if match:
        name = match.group(1)
        tag = match.group(2) if match.group(2) else 'latest'
        return name, tag
    return image, 'latest'


def pull_tag_push_image(image, local_registry_url):
    """
    Pull the image, tag it to local registry, and push.
    Return (success: bool, message: str)
    """
    success, msg = run_command(f"docker pull {image}")
    if not success:
        return False, f"Failed to pull {image}: {msg}"

    image_name, tag = extract_image_name_tag(image)
    # Strip possible registry and repo from original image name to just image name and tag
    # For tagging local registry, we want local_registry_url/image_name:tag
    # But keep repo path after local_registry_url if needed
    # To keep repo path, we remove registry part if exists
    # Example: registry.com/repo/image:tag -> repo/image:tag
    # This is complex, for simplicity, we'll keep everything after first slash for tagging
    # Extract repo/image from image_name, skipping registry domain (if any)
    if '/' in image_name:
        parts = image_name.split('/')
        if '.' in parts[0] or ':' in parts[0]:
            # first part is registry domain, remove it
            repo_path = '/'.join(parts[1:])
        else:
            repo_path = image_name
    else:
        repo_path = image_name

    new_tag = f"{local_registry_url.rstrip('/')}/{repo_path}:{tag}"

    success, msg = run_command(f"docker tag {image} {new_tag}")
    if not success:
        return False, f"Failed to tag {image} as {new_tag}: {msg}"

    success, msg = run_command(f"docker push {new_tag}")
    if not success:
        return False, f"Failed to push {new_tag}: {msg}"

    return True, f"Successfully pushed {new_tag}"


class DockerImageManagerApp:
    def __init__(self, root):
        self.root = root
        root.title("Docker Image Manager")

        # Registry URL input
        tk.Label(root, text="Local Registry URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.registry_entry = tk.Entry(root, width=40)
        self.registry_entry.grid(row=0, column=1, padx=5, pady=5)

        # Upload compose button
        self.upload_button = tk.Button(root, text="Upload docker-compose.yaml", command=self.upload_compose)
        self.upload_button.grid(row=1, column=0, columnspan=2, pady=5)

        # Single image input and button
        tk.Label(root, text="Single Image:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.single_image_entry = tk.Entry(root, width=40)
        self.single_image_entry.grid(row=2, column=1, padx=5, pady=5)

        self.single_image_button = tk.Button(root, text="Pull, Tag & Push Single Image", command=self.handle_single_image)
        self.single_image_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Status box
        self.status_text = tk.Text(root, height=10, width=60, state='disabled')
        self.status_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def log_status(self, message):
        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message + '\n')
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')
        self.root.update()

    def upload_compose(self):
        registry_url = self.registry_entry.get().strip()
        if not registry_url:
            messagebox.showerror("Error", "Please enter the Local Registry URL.")
            return

        file_path = easygui.fileopenbox(filetypes=["*.yaml", "*.yml"])
        if not file_path:
            return

        self.log_status(f"Loading compose file: {file_path}")
        try:
            images = parse_images_from_compose(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse YAML: {e}")
            return

        if not images:
            messagebox.showinfo("Info", "No images found in docker-compose.yaml.")
            return

        self.log_status(f"Found images: {images}")

        for image in images:
            self.log_status(f"Processing image: {image}")
            success, msg = pull_tag_push_image(image, registry_url)
            if success:
                self.log_status(f"SUCCESS: {msg}")
            else:
                self.log_status(f"ERROR: {msg}")

        self.log_status("Done processing docker-compose images.")

    def handle_single_image(self):
        registry_url = self.registry_entry.get().strip()
        image = self.single_image_entry.get().strip()
        if not registry_url:
            messagebox.showerror("Error", "Please enter the Local Registry URL.")
            return
        if not image:
            messagebox.showerror("Error", "Please enter an image name.")
            return

        self.log_status(f"Processing single image: {image}")
        success, msg = pull_tag_push_image(image, registry_url)
        if success:
            self.log_status(f"SUCCESS: {msg}")
        else:
            self.log_status(f"ERROR: {msg}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DockerImageManagerApp(root)
    root.mainloop()

