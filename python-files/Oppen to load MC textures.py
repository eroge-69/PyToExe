# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 16:09:05 2025

@author: MVomScheidt31
"""

import os
import http.server
import socketserver

# Change directory to your game folder
os.chdir(r"C:\Users\mvomscheidt31\Desktop\Minceraft game assets")

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()


#go to http://localhost:8000/Minecraft2.html
