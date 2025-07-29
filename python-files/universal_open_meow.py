import os

# Get the current user's Downloads folder
downloads = os.path.join(os.environ["USERPROFILE"], "Downloads")
gif_path = os.path.join(downloads, "it does not even mater.exe", "stuff", "meow.gif")

# Open the GIF
os.startfile(gif_path)
