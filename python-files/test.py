import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
from tkinter.colorchooser import askcolor
import os
import time
import threading
from datetime import datetime
import sys


class MessageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Message App")

        # Window settings
        self.root.geometry("1000x700")
        self.root.config(bg="#E0F2F7")

        # Ask for a username at the start
        self.username = simpledialog.askstring("Username", "Enter your username:")
        if not self.username:
            self.username = "User"

        # Ask user to select their name color
        self.user_color = self.ask_for_username_color()

        # File path to store messages
        # IMPORTANT: Update this path to a directory where you have write permissions.
        # For example, you could use os.path.join(os.path.expanduser("~"), "Documents", "message_app_chat.txt")
        # to save it in the user's Documents folder.
        self.file_path = r'C:\Users\Public\Documents\text.txt'
        self.seen_messages = set()

        # --- NEW: List to track files copied by this session for deletion on exit ---
        self.sent_files_to_delete = []
        # -------------------------------------------------------------------------

        # Set default color for messages (User and Receiver)
        self.receiver_color = "#00796B"

        # Create the main frame for organizing widgets
        self.main_frame = tk.Frame(self.root, bg="#E0F2F7")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create a frame for the message area
        self.message_display_frame = tk.Frame(self.main_frame, bg="#FFFFFF", bd=2, relief=tk.FLAT, highlightbackground="#B2EBF2", highlightthickness=1)
        self.message_display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Create the text area for displaying messages
        self.text_area = scrolledtext.ScrolledText(self.message_display_frame, wrap=tk.WORD, width=50, height=15, font=("Helvetica Neue", 11), bg="#F5F8FA", fg="#333333", bd=0, relief=tk.FLAT, padx=10, pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)

        # Create the frame for the message input and buttons
        # Using grid for better control of button placement
        self.input_controls_frame = tk.Frame(self.main_frame, bg="#E0F2F7")
        self.input_controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        # Configure columns for the grid layout in input_controls_frame
        # All button columns will expand equally
        self.input_controls_frame.columnconfigure(0, weight=1)
        self.input_controls_frame.columnconfigure(1, weight=1)
        self.input_controls_frame.columnconfigure(2, weight=1)
        self.input_controls_frame.columnconfigure(3, weight=1)

        # Create the entry box for sending messages - Bigger and at the top
        self.message_entry = tk.Entry(self.input_controls_frame, font=("Helvetica Neue", 14), bg="#FFFFFF", fg="#333333", bd=1, relief=tk.SOLID)
        self.message_entry.grid(row=0, column=0, columnspan=4, padx=(0, 0), pady=10, sticky="ew")

        # Create the send button
        self.send_button = tk.Button(self.input_controls_frame, text="Send", font=("Helvetica Neue", 11, "bold"), bg="#4CAF50", fg="white", command=self.send_message, relief=tk.FLAT, padx=15, pady=5)
        self.send_button.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="ew")

        # Create the file send button
        self.file_button = tk.Button(self.input_controls_frame, text="Send File", font=("Helvetica Neue", 11, "bold"), bg="#2196F3", fg="white", command=self.send_file, relief=tk.FLAT, padx=15, pady=5)
        self.file_button.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="ew")

        # Create the clear button
        self.clear_button = tk.Button(self.input_controls_frame, text="Clear Chat", font=("Helvetica Neue", 11, "bold"), bg="#F44336", fg="white", command=self.clear_messages, relief=tk.FLAT, padx=15, pady=5)
        self.clear_button.grid(row=1, column=2, padx=(0, 5), pady=5, sticky="ew")

        # Create the user list toggle button - Always visible
        self.toggle_button = tk.Button(self.input_controls_frame, text="Toggle User List", font=("Helvetica Neue", 11, "bold"), bg="#FFC107", fg="white", command=self.toggle_user_list, relief=tk.FLAT, padx=15, pady=5)
        self.toggle_button.grid(row=1, column=3, padx=(0, 0), pady=5, sticky="ew")

        # Create the user list frame and listbox
        self.user_list_frame = tk.Frame(self.main_frame, bg="#FFFFFF", bd=2, relief=tk.FLAT, highlightbackground="#B2EBF2", highlightthickness=1)
        self.user_list_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        self.user_list_label = tk.Label(self.user_list_frame, text="Active Users", font=("Helvetica Neue", 13, "bold"), bg="#FFFFFF", fg="#333333", pady=5)
        self.user_list_label.pack(fill=tk.X)

        self.user_list = tk.Listbox(self.user_list_frame, height=10, width=20, font=("Helvetica Neue", 10), bg="#F5F8FA", fg="#333333", bd=0, relief=tk.FLAT, selectbackground="#B2EBF2", selectforeground="#333333")
        self.user_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure context menu for copying file content
        self.file_content_menu = tk.Menu(self.root, tearoff=0)
        self.file_content_menu.add_command(label="Copy File Content", command=self.copy_selected_file_content)

        # Configure generic copy context menu (for any selected text)
        self.generic_copy_menu = tk.Menu(self.root, tearoff=0)
        self.generic_copy_menu.add_command(label="Copy", command=self.copy_selected_text)

        # Bind right-click to the text area for context menu
        self.text_area.bind('<Button-3>', self.show_text_area_context_menu)

        # Bind Enter key to send message
        self.root.bind('<Return>', self.send_message_on_enter)

        # Start the message checking thread
        self.check_messages_thread = threading.Thread(target=self.check_messages)
        self.check_messages_thread.daemon = True
        self.check_messages_thread.start()

        # Create the file if it doesn't exist
        if not os.path.exists(self.file_path):
            try:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                with open(self.file_path, 'w') as file:
                    pass
            except Exception as e:
                print(f"Error creating file path or file: {e}")

        # Handle closing window properly to stop thread and delete files
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Initial update of user list and load messages
        self.update_user_list()
        self.load_initial_messages()


    def ask_for_username_color(self):
        """Asks the user to pick a color for their username."""
        color = askcolor(title="Pick Your Username Color")[1]
        if color:
            return color
        return "#0000FF"

    def insert_message(self, message, tag):
        """Inserts a message into the text area with a specific tag."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message, tag)
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

    def send_message(self):
        """Sends the message from the entry box to the chat file."""
        message = self.message_entry.get().strip()
        if message:
            timestamp = datetime.now().strftime("%H:%M")
            full_message = f"[{timestamp}] {self.username}: {message}"
            with open(self.file_path, 'a', encoding='utf-8') as file:
                file.write(f"{full_message}\n")
            self.message_entry.delete(0, tk.END)
            self.update_user_list()

    def send_message_on_enter(self, event=None):
        """Binds the Enter key to the send_message function."""
        self.send_message()

    def load_initial_messages(self):
        """Loads and displays all existing messages from the file when the app starts."""
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
            messages = file.readlines()

        for message in messages:
            message = message.strip()
            if not message:
                continue
            self.seen_messages.add(message)

            if ":" in message:
                parts = message.split(":", 1)
                if len(parts) == 2:
                    header_part = parts[0].strip()
                    msg_content = parts[1].strip()
                    username = self._extract_username_from_header(header_part)

                    if username == self.username:
                        self._display_message_content(message, msg_content, 'user', is_sender=True)
                    else:
                        self._display_message_content(message, msg_content, 'receiver', is_sender=False)
            self.text_area.see(tk.END)


    def read_messages(self):
        """Reads new messages from the file that haven't been seen yet."""
        if not os.path.exists(self.file_path):
            return []

        messages_from_file = []
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
                messages_from_file = file.readlines()
        except Exception as e:
            print(f"Error reading message file: {e}")
            return []

        new_messages = []
        for message in messages_from_file:
            stripped_message = message.strip()
            if stripped_message and stripped_message not in self.seen_messages:
                new_messages.append(stripped_message)
                self.seen_messages.add(stripped_message)
        return new_messages

    def _extract_username_from_header(self, header_part):
        """Helper to extract username from a message header (handling timestamp)."""
        if header_part.startswith('[') and ']' in header_part:
            try:
                timestamp_end_index = header_part.find(']')
                if timestamp_end_index != -1:
                    username = header_part[timestamp_end_index + 1:].strip()
                else:
                    username = header_part.strip()
            except Exception:
                username = header_part.strip()
        else:
            username = header_part.strip()
        return username

    def _display_message_content(self, full_message, content_part, tag, is_sender):
        """Helper to display message and handle file content or links."""
        if "sent a file:" in content_part.lower():
            file_name = content_part.split("sent a file:")[-1].strip()
            self.insert_message(f"{full_message}\n", tag)

            if any(file_name.lower().endswith(ext) for ext in ['.py', '.java', '.txt', '.csv', '.xml', '.html', '.json']):
                # Attempt to read from the shared directory
                file_path_in_shared_dir = os.path.join(os.path.dirname(self.file_path), file_name)
                if os.path.exists(file_path_in_shared_dir):
                    try:
                        with open(file_path_in_shared_dir, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        # Use appropriate tag for file content (user_file_content or receiver_file_content)
                        content_tag = 'user_file_content' if is_sender else 'receiver_file_content'
                        self.insert_message(f"File content from {file_name}:\n{content}\n", content_tag)
                    except Exception as e:
                        self.insert_message(f"Error reading file '{file_name}': {e}\n", 'error')
                else:
                    self.insert_message(f"File content for {file_name} not found locally.\n", 'info')
            else:
                if not is_sender:
                    self.insert_message(f"File '{file_name}' received.\n", 'receiver_file_content')
        else:
            self.insert_message(f"{full_message}\n", tag)


    def check_messages(self):
        """Periodically checks for new messages and displays them."""
        while True:
            new_messages = self.read_messages()
            for message in new_messages:
                if ":" in message:
                    parts = message.split(":", 1)
                    if len(parts) == 2:
                        header_part = parts[0].strip()
                        msg_content = parts[1].strip()
                        username = self._extract_username_from_header(header_part)

                        if username == self.username:
                            self._display_message_content(message, msg_content, 'user', is_sender=True)
                        else:
                            self._display_message_content(message, msg_content, 'receiver', is_sender=False)
            time.sleep(1)

    def update_user_list(self):
        """Updates the list of active users displayed in the user list box."""
        self.user_list.delete(0, tk.END)
        self.user_list.insert(tk.END, f"{self.username} (You)")
        active_users = set()
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    if ":" in line:
                        header_part = line.split(":", 1)[0].strip()
                        username = self._extract_username_from_header(header_part)
                        if username and username != self.username:
                            active_users.add(username)
        for user in sorted(list(active_users)):
            self.user_list.insert(tk.END, user)

    def clear_messages(self):
        """Clears all messages from the chat file and the display area."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    pass
            except Exception as e:
                print(f"Error clearing message file: {e}")

        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state=tk.DISABLED)
        self.seen_messages.clear()
        self.update_user_list()

    def send_file(self):
        """Opens a file dialog, displays selected file's content in chat (if text-based), and sends a message about it.
           The file is copied to the shared directory in the background to ensure other users can access its content."""
        file_path_to_send = filedialog.askopenfilename(title="Select a file")
        if file_path_to_send:
            file_name = os.path.basename(file_path_to_send)
            timestamp = datetime.now().strftime("%H:%M")
            full_message = f"[{timestamp}] {self.username} sent a file: {file_name}"

            # --- Copy the file to the shared directory ---
            # This is essential for other users to be able to read and display its content.
            destination_dir = os.path.dirname(self.file_path)
            os.makedirs(destination_dir, exist_ok=True)
            destination = os.path.join(destination_dir, file_name)

            try:
                with open(destination, 'wb') as dest_file:
                    with open(file_path_to_send, 'rb') as source_file:
                        dest_file.write(source_file.read())
                # Add the path to the list of files to delete on exit
                self.sent_files_to_delete.append(destination)
                # NO explicit "File copied" message here, per your request.
            except Exception as e:
                self.insert_message(f"Error copying file '{file_name}' to shared directory: {e}\n", 'error')
                # If copying fails, the file won't be accessible to others.
                # We still proceed to send the chat message about it.

            # --- Display data for the sender immediately (if text-based) ---
            if any(file_name.lower().endswith(ext) for ext in ['.py', '.java', '.txt', '.csv', '.xml', '.html', '.json']):
                try:
                    with open(file_path_to_send, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    self.insert_message(f"{full_message}\n", 'user')
                    self.insert_message(f"File content from {file_name}:\n{content}\n", 'user_file_content')
                except Exception as e:
                    self.insert_message(f"Error reading local file '{file_name}': {e}\n", 'error')
            else:
                self.insert_message(f"{full_message}\n", 'user')

            # Write the message about sending a file to the chat file (for others to see filename)
            with open(self.file_path, 'a', encoding='utf-8') as file:
                file.write(f"{full_message}\n")

            self.message_entry.delete(0, tk.END)
            self.text_area.see(tk.END)

    def toggle_user_list(self):
        """Toggles the visibility of the active user list."""
        if self.user_list_frame.winfo_ismapped():
            self.user_list_frame.pack_forget()
        else:
            self.user_list_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
            self.update_user_list()

    def show_text_area_context_menu(self, event):
        """Displays a context menu when right-clicking on the text area."""
        try:
            has_selection = bool(self.text_area.tag_ranges(tk.SEL))
        except tk.TclError:
            has_selection = False

        index = self.text_area.index(f"@{event.x},{event.y}")
        tags_at_point = self.text_area.tag_names(index)

        if 'receiver_file_content' in tags_at_point or 'user_file_content' in tags_at_point:
            self.file_content_menu.post(event.x_root, event.y_root)
        elif has_selection:
            self.generic_copy_menu.post(event.x_root, event.y_root)

    def copy_selected_file_content(self):
        """Copies the currently selected text to the clipboard, specifically for file content."""
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.insert_message("Selected file content copied to clipboard.\n", 'info')
            else:
                self.insert_message("No text selected to copy.\n", 'info')
        except tk.TclError:
            self.insert_message("No text selected to copy.\n", 'info')

    def copy_selected_text(self):
        """Copies the currently selected text to the clipboard (generic)."""
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected_text)
                self.insert_message("Selected text copied to clipboard.\n", 'info')
            else:
                self.insert_message("No text selected to copy.\n", 'info')
        except tk.TclError:
            pass

    def on_closing(self):
        """Handles proper shutdown when the window is closed, deleting files sent by this session."""
        for file_path in self.sent_files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted sent file: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error deleting file '{os.path.basename(file_path)}': {e}")
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MessageApp(root)

    app.text_area.tag_config('user', foreground=app.user_color)
    app.text_area.tag_config('receiver', foreground=app.receiver_color)
    app.text_area.tag_config('receiver_file_content', foreground="#004D40", font=("Helvetica Neue", 10, "italic"))
    app.text_area.tag_config('user_file_content', foreground="#006064", font=("Helvetica Neue", 10, "italic"))
    app.text_area.tag_config('info', foreground="#1976D2")
    app.text_area.tag_config('error', foreground="#D32F2F")

    root.mainloop()
