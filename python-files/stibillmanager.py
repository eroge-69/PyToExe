import os
import webview

BASE = os.path.abspath(os.path.dirname(__file__))
html_path = os.path.join(BASE, 'index.html')
file_url = f'file:///{html_path.replace(os.sep, "/")}'

if not os.path.exists(html_path):
    raise SystemExit(f"index.html not found at: {html_path}")

# Prefer ICO for Windows, fallback to PNG
icon_ico = os.path.join(BASE, 'icon.ico')
icon_png = os.path.join(BASE, 'icon.png')

window_kwargs = {
    'title': 'STI BILLS MANAGER',
    'url': file_url,
    'width': 1100,
    'height': 700,
    'resizable': True
}

if os.path.exists(icon_ico):
    window_kwargs['icon'] = icon_ico
elif os.path.exists(icon_png):
    window_kwargs['icon'] = icon_png

try:
    window = webview.create_window(**window_kwargs)
except TypeError:
    window_kwargs.pop('icon', None)
    window = webview.create_window(**window_kwargs)

webview.start()