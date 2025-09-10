import sys
import json
import asyncio
import websockets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
import queue

# Hardcoded values for the bot
BOT_UUID = "57b5fd03-3450-4d9d-ba63-a4d13f816e94"
COMMAND_KEY = "=uOk]tPUX6sdhe:?Hxnp,N<7rLm2=JJtbRp=Oz*FS@18]5Zdpro7Z6#x32oL@@0X;_3lqjYd#s|ra&!P9$lV]1)Qc;5>V7[24F2w2:Ez~(4tGS0Y)n6o=!HMcTBM@`1Z"
WEBSOCKET_URL = "ws://localhost:8765"

class WebSocketThread(QThread):
    output_received = pyqtSignal(str)
    connection_status = pyqtSignal(str)
    directory_changed = pyqtSignal(str)
    
    def __init__(self, bot_uuid, command_key, websocket_url):
        super().__init__()
        self.bot_uuid = bot_uuid
        self.command_key = command_key
        self.websocket_url = websocket_url
        self.websocket = None
        self.connected = False
        self.running = True
        self.command_queue = queue.Queue()
        self.current_directory = "C:\\"
        
    def run(self):
        asyncio.run(self.websocket_loop())
        
    async def websocket_loop(self):
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.connection_status.emit(f"Connected to server at {self.websocket_url}")
            
            # Register as a commander
            register_msg = {
                "bot/commander": "commander",
                "uuid": self.bot_uuid,
                "command_key": self.command_key
            }
            
            await self.websocket.send(json.dumps(register_msg))
            self.connection_status.emit("Sent registration request")
            
            # Wait for registration confirmation
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("status") == "registerd":
                self.connected = True
                self.connection_status.emit("Successfully registered as commander!")
            else:
                self.connection_status.emit(f"Registration failed: {response_data}")
                return
            
            # Main loop to handle messages and commands
            while self.running:
                # Check for commands to send
                try:
                    command = self.command_queue.get_nowait()
                    if command:
                        command_msg = {
                            "type": "command",
                            "uuid": self.bot_uuid,
                            "command": command
                        }
                        await self.websocket.send(json.dumps(command_msg))
                        # Show the command in the terminal
                        self.output_received.emit(f"> {command}")
                except queue.Empty:
                    pass
                
                # Check for incoming messages
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=0.1)
                    
                    # Debug: print raw message
                    print(f"DEBUG: Received message: {response}")
                    
                    try:
                        response_data = json.loads(response)
                        
                        if response_data.get("type") == "output":
                            output_text = response_data.get("output", "")
                            cwd = response_data.get("cwd", self.current_directory)
                            
                            # Update current directory if provided
                            if cwd and cwd != self.current_directory:
                                self.current_directory = cwd
                                self.directory_changed.emit(cwd)
                                
                            # Emit output
                            if output_text:
                                self.output_received.emit(output_text)
                            
                        elif response_data.get("type") == "error":
                            self.output_received.emit(f"Error: {response_data.get('message', 'Unknown error')}")
                        elif response_data.get("type") == "bot disconnect":
                            self.output_received.emit("Bot disconnected!")
                            self.connected = False
                            break
                            
                    except json.JSONDecodeError:
                        self.output_received.emit(f"Received non-JSON message: {response}")
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self.output_received.emit(f"Error receiving message: {e}")
                    break
                    
        except Exception as e:
            self.connection_status.emit(f"Connection error: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()
                
    def send_command(self, command):
        self.command_queue.put(command)
        
    def stop(self):
        self.running = False

class CommanderGUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # Track current working directory for prompt
        self.current_dir = "C:\\"
        self.prompt_text = f"{self.current_dir}> "

        # Command history
        self.command_history = []
        self.history_index = None
        self.prompt_position = 0

        # GUI setup
        self.setWindowTitle("SSH-like Bot Terminal")
        self.setGeometry(200, 200, 800, 500)
        layout = QVBoxLayout()

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(False)
        self.terminal.setStyleSheet("background-color: black; color: white; font-family: Consolas; font-size: 10pt;")
        self.terminal.installEventFilter(self)
        layout.addWidget(self.terminal)
        self.setLayout(layout)

        # Start WebSocket connection
        self.ws_thread = WebSocketThread(BOT_UUID, COMMAND_KEY, WEBSOCKET_URL)
        self.ws_thread.output_received.connect(self.append_output)
        self.ws_thread.connection_status.connect(self.append_status)
        self.ws_thread.directory_changed.connect(self.update_directory)
        self.ws_thread.start()

        # Start with prompt
        self.append_prompt()

    def append_output(self, text):
        # Move cursor to end and insert output
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.terminal.setTextCursor(cursor)
        
        # Format output with green color
        format = QTextCharFormat()
        format.setForeground(QColor(0, 255, 0))  # Green for output
        
        cursor.insertText(text + "\n", format)
        self.append_prompt()

    def append_status(self, text):
        # Move cursor to end and insert status message
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.terminal.setTextCursor(cursor)
        
        # Format status with cyan color
        format = QTextCharFormat()
        format.setForeground(QColor(0, 255, 255))  # Cyan for status
        
        cursor.insertText(text + "\n", format)
        self.append_prompt()

    def update_directory(self, new_dir):
        """Update the current directory and prompt"""
        if new_dir and new_dir != self.current_dir:
            self.current_dir = new_dir
            self.prompt_text = f"{self.current_dir}> "
            # Clear the current input and update the prompt
            self.terminal.moveCursor(QTextCursor.End)
            self.terminal.textCursor().select(QTextCursor.LineUnderCursor)
            self.terminal.textCursor().removeSelectedText()
            self.append_prompt()

    def append_prompt(self):
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Format prompt with yellow color
        format = QTextCharFormat()
        format.setForeground(QColor(255, 255, 0))  # Yellow for prompt
        
        cursor.insertText(f"{self.prompt_text}", format)
        self.prompt_position = cursor.position()
        self.terminal.setTextCursor(cursor)

    def get_current_command(self):
        cursor = self.terminal.textCursor()
        cursor.setPosition(self.prompt_position)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        return cursor.selectedText().strip()

    def set_current_command(self, text):
        cursor = self.terminal.textCursor()
        cursor.setPosition(self.prompt_position)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        
        # Format command input with white color
        format = QTextCharFormat()
        format.setForeground(QColor(255, 255, 255))  # White for input
        
        cursor.insertText(text, format)
        self.terminal.setTextCursor(cursor)

    def eventFilter(self, obj, event):
        if obj != self.terminal or event.type() != event.KeyPress:
            return super().eventFilter(obj, event)

        key = event.key()
        cursor = self.terminal.textCursor()

        # Prevent typing above prompt
        if cursor.position() < self.prompt_position:
            cursor.setPosition(self.prompt_position)
            self.terminal.setTextCursor(cursor)
            return True

        # Enter/Return submits command
        if key in (Qt.Key_Return, Qt.Key_Enter):
            cmd = self.get_current_command()
            if cmd:
                self.command_history.append(cmd)
                self.history_index = None

                if cmd.lower() in ("clear", "cls"):
                    self.terminal.clear()
                    self.append_prompt()
                else:
                    # Show the command being executed
                    cursor.movePosition(QTextCursor.End)
                    self.terminal.setTextCursor(cursor)
                    self.terminal.insertPlainText("\n")
                    self.ws_thread.send_command(cmd)

            return True

        # Command history navigation
        elif key == Qt.Key_Up:
            if self.command_history:
                if self.history_index is None:
                    self.history_index = len(self.command_history) - 1
                elif self.history_index > 0:
                    self.history_index -= 1
                self.set_current_command(self.command_history[self.history_index])
            return True
            
        elif key == Qt.Key_Down:
            if self.command_history and self.history_index is not None:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self.set_current_command(self.command_history[self.history_index])
                else:
                    self.history_index = None
                    self.set_current_command("")
            return True

        # Prevent backspacing into prompt
        if key == Qt.Key_Backspace:
            if cursor.position() <= self.prompt_position:
                return True

        # Allow normal typing
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        self.ws_thread.stop()
        self.ws_thread.wait()
        event.accept()

if __name__ == "__main__":
    # Set up asyncio for Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    app = QApplication(sys.argv)
    gui = CommanderGUI()
    gui.show()
    sys.exit(app.exec_())