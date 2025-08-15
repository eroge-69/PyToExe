# main.py
# This script creates a simple system tray application.
# It uses the 'pystray' library for the tray icon and 'Pillow' to create an icon on the fly.

import pystray
from PIL import Image, ImageDraw

def create_image(width, height, color1, color2):
    """
    Generates a simple image to be used as the system tray icon.
    This function creates a 64x64 pixel transparent image with a blue circle in the center.
    """
    # Create a new image with a transparent background
    image = Image.new('RGBA', (width, height), color1)
    # Get a drawing context
    dc = ImageDraw.Draw(image)
    
    # Draw a filled blue ellipse (circle) in the center of the image
    # The coordinates define the bounding box of the ellipse.
    dc.ellipse(
        [(width // 4, height // 4), (width * 3 // 4, height * 3 // 4)],
        fill=color2
    )
    
    return image

def on_quit_callback(icon, item):
    """
    This function is called when the 'Quit' menu item is clicked.
    It stops the icon, which terminates the application.
    """
    icon.stop()

def setup_tray_icon():
    """
    Sets up and runs the system tray icon.
    """
    # 1. Create the icon image
    # We are creating a 64x64 pixel image.
    # Color 1 is transparent for the background.
    # Color 2 is a shade of blue for the circle.
    image = create_image(64, 64, (0, 0, 0, 0), (66, 133, 244))

    # 2. Create the menu that appears on right-click
    # It contains a single item: 'Quit', which calls the on_quit_callback function.
    menu = pystray.Menu(
        pystray.MenuItem('Quit', on_quit_callback)
    )

    # 3. Create the pystray.Icon instance
    # 'MySystemTrayApp' is the internal name.
    # 'image' is the icon we created.
    # 'My Awesome App' is the tooltip text that appears on hover.
    # 'menu' is the right-click context menu.
    icon = pystray.Icon(
        'MySystemTrayApp',
        image,
        'My Awesome App',
        menu
    )

    # 4. Run the icon
    # This is a blocking call and will run until icon.stop() is called.
    icon.run()

if __name__ == '__main__':
    setup_tray_icon()
