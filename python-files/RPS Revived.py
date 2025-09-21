import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import socket
import threading
import json

class RPSGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rock Paper Scissors - Multiplayer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Game state variables
        self.host_socket = None
        self.client_socket = None
        self.connection = None
        self.is_host = False
        self.is_connected = False
        self.player_choice = None
        self.opponent_choice = None
        self.game_code = None
        
        self.create_main_menu()
        
    def create_main_menu(self):
        """Create the main menu interface"""
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        title_label = tk.Label(self.root, text="Rock Paper Scissors", font=("Arial", 20, "bold"))
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(self.root, text="Multiplayer Edition", font=("Arial", 14))
        subtitle_label.pack(pady=5)
        
        # Create game frame
        frame = tk.Frame(self.root)
        frame.pack(pady=30)
        
        # Host game button
        host_btn = tk.Button(frame, text="Host Game", command=self.host_game, 
                            width=20, height=2, font=("Arial", 12))
        host_btn.grid(row=0, column=0, padx=20, pady=10)
        
        # Join game button
        join_btn = tk.Button(frame, text="Join Game", command=self.join_game, 
                            width=20, height=2, font=("Arial", 12))
        join_btn.grid(row=0, column=1, padx=20, pady=10)
        
        # How to play button
        help_btn = tk.Button(self.root, text="How to Play", command=self.show_help, 
                            font=("Arial", 10))
        help_btn.pack(pady=10)
        
    def host_game(self):
        """Set up as game host"""
        self.is_host = True
        self.create_host_interface()
        self.start_server()
        
    def join_game(self):
        """Set up as game client"""
        self.is_host = False
        self.create_client_interface()
        
    def create_host_interface(self):
        """Create interface for game host"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        title_label = tk.Label(self.root, text="Hosting Game", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Game code display
        code_frame = tk.Frame(self.root)
        code_frame.pack(pady=10)
        
        tk.Label(code_frame, text="Your Game Code:", font=("Arial", 12)).pack()
        
        self.code_label = tk.Label(code_frame, text="Generating...", font=("Courier", 16, "bold"), fg="blue")
        self.code_label.pack(pady=5)
        
        # Copy code button
        copy_btn = tk.Button(self.root, text="Copy Code", command=self.copy_code, font=("Arial", 10))
        copy_btn.pack(pady=5)
        
        # Status area
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        tk.Label(status_frame, text="Status:", font=("Arial", 12)).pack()
        
        self.status_text = scrolledtext.ScrolledText(status_frame, width=40, height=8, font=("Arial", 10))
        self.status_text.pack(pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Back button
        back_btn = tk.Button(self.root, text="Back to Menu", command=self.back_to_menu, font=("Arial", 10))
        back_btn.pack(pady=10)
        
    def create_client_interface(self):
        """Create interface for game client"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        title_label = tk.Label(self.root, text="Join Game", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Code entry
        code_frame = tk.Frame(self.root)
        code_frame.pack(pady=10)
        
        tk.Label(code_frame, text="Enter Game Code:", font=("Arial", 12)).pack()
        
        self.code_entry = tk.Entry(code_frame, font=("Courier", 16), justify="center", width=15)
        self.code_entry.pack(pady=5)
        
        # Connect button
        connect_btn = tk.Button(self.root, text="Connect", command=self.connect_to_game, 
                               font=("Arial", 12), width=15)
        connect_btn.pack(pady=10)
        
        # Status area
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        
        tk.Label(status_frame, text="Status:", font=("Arial", 12)).pack()
        
        self.status_text = scrolledtext.ScrolledText(status_frame, width=40, height=8, font=("Arial", 10))
        self.status_text.pack(pady=5)
        self.status_text.config(state=tk.DISABLED)
        
        # Back button
        back_btn = tk.Button(self.root, text="Back to Menu", command=self.back_to_menu, font=("Arial", 10))
        back_btn.pack(pady=10)
        
    def create_game_interface(self):
        """Create the game playing interface"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        title_label = tk.Label(self.root, text="Rock Paper Scissors", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Opponent status
        self.opponent_status = tk.Label(self.root, text="Waiting for opponent...", font=("Arial", 12), fg="gray")
        self.opponent_status.pack(pady=5)
        
        # Game choices
        choices_frame = tk.Frame(self.root)
        choices_frame.pack(pady=20)
        
        rock_btn = tk.Button(choices_frame, text="✊ Rock", command=lambda: self.make_choice("rock"), 
                            font=("Arial", 14), width=10, height=2)
        rock_btn.grid(row=0, column=0, padx=10, pady=5)
        
        paper_btn = tk.Button(choices_frame, text="✋ Paper", command=lambda: self.make_choice("paper"), 
                             font=("Arial", 14), width=10, height=2)
        paper_btn.grid(row=0, column=1, padx=10, pady=5)
        
        scissors_btn = tk.Button(choices_frame, text="✌️ Scissors", command=lambda: self.make_choice("scissors"), 
                                font=("Arial", 14), width=10, height=2)
        scissors_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Player choice display
        self.choice_label = tk.Label(self.root, text="Make your choice!", font=("Arial", 12))
        self.choice_label.pack(pady=10)
        
        # Result display
        self.result_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=10)
        
        # Play again button (initially hidden)
        self.play_again_btn = tk.Button(self.root, text="Play Again", command=self.reset_round, 
                                       font=("Arial", 12), state=tk.DISABLED)
        self.play_again_btn.pack(pady=10)
        
        # Disconnect button
        disconnect_btn = tk.Button(self.root, text="Disconnect", command=self.disconnect, font=("Arial", 10))
        disconnect_btn.pack(pady=5)
        
    def start_server(self):
        """Start the game server"""
        try:
            # Generate a random 4-digit code
            self.game_code = str(random.randint(1000, 9999))
            self.code_label.config(text=self.game_code)
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self.run_server, daemon=True)
            server_thread.start()
            
            self.update_status("Server started. Waiting for opponent to connect...")
        except Exception as e:
            self.update_status(f"Error starting server: {str(e)}")
            
    def run_server(self):
        """Run the game server"""
        try:
            self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.host_socket.bind(('0.0.0.0', 12345))
            self.host_socket.listen(1)
            
            self.update_status("Waiting for connection...")
            self.connection, address = self.host_socket.accept()
            self.is_connected = True
            
            self.update_status(f"Connected to {address[0]}")
            self.root.after(0, self.create_game_interface)
            
            # Start listening for messages
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except Exception as e:
            self.update_status(f"Server error: {str(e)}")
            
    def connect_to_game(self):
        """Connect to a game as client"""
        code = self.code_entry.get().strip()
        if not code or len(code) != 4 or not code.isdigit():
            messagebox.showerror("Error", "Please enter a valid 4-digit code")
            return
            
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('localhost', 12345))
            self.connection = self.client_socket
            self.is_connected = True
            
            self.update_status("Connected to game!")
            self.root.after(0, self.create_game_interface)
            
            # Start listening for messages
            receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            receive_thread.start()
            
        except Exception as e:
            self.update_status(f"Connection error: {str(e)}")
            
    def receive_messages(self):
        """Receive messages from the other player"""
        while self.is_connected:
            try:
                data = self.connection.recv(1024).decode()
                if not data:
                    break
                    
                message = json.loads(data)
                
                if message['type'] == 'choice':
                    self.opponent_choice = message['choice']
                    self.root.after(0, lambda: self.opponent_status.config(
                        text=f"Opponent has made a choice!"))
                    
                elif message['type'] == 'result_request':
                    self.root.after(0, self.determine_winner)
                    
            except:
                if self.is_connected:
                    self.root.after(0, lambda: self.update_status("Connection lost!"))
                break
                
    def send_message(self, message_type, data=None):
        """Send a message to the other player"""
        if not self.is_connected:
            return
            
        message = {'type': message_type}
        if data:
            message.update(data)
            
        try:
            self.connection.send(json.dumps(message).encode())
        except:
            self.update_status("Error sending message")
            
    def make_choice(self, choice):
        """Player makes a choice"""
        self.player_choice = choice
        choices = {"rock": "✊ Rock", "paper": "✋ Paper", "scissors": "✌️ Scissors"}
        self.choice_label.config(text=f"You chose: {choices[choice]}")
        
        # Send choice to opponent
        self.send_message('choice', {'choice': choice})
        
        # If both players have made choices, determine winner
        if self.opponent_choice:
            self.determine_winner()
        else:
            self.send_message('result_request')
            
    def determine_winner(self):
        """Determine the winner of the round"""
        if not self.player_choice or not self.opponent_choice:
            return
            
        # Determine winner
        if self.player_choice == self.opponent_choice:
            result = "It's a tie!"
        elif (self.player_choice == "rock" and self.opponent_choice == "scissors") or \
             (self.player_choice == "paper" and self.opponent_choice == "rock") or \
             (self.player_choice == "scissors" and self.opponent_choice == "paper"):
            result = "You win! 🎉"
        else:
            result = "You lose! 😢"
            
        choices = {"rock": "✊ Rock", "paper": "✋ Paper", "scissors": "✌️ Scissors"}
        result_text = f"{result}\nYou: {choices[self.player_choice]}\nOpponent: {choices[self.opponent_choice]}"
        
        self.result_label.config(text=result_text)
        self.play_again_btn.config(state=tk.NORMAL)
        
    def reset_round(self):
        """Reset the round for a new game"""
        self.player_choice = None
        self.opponent_choice = None
        self.choice_label.config(text="Make your choice!")
        self.result_label.config(text="")
        self.opponent_status.config(text="Waiting for opponent...")
        self.play_again_btn.config(state=tk.DISABLED)
        
    def update_status(self, message):
        """Update the status text area"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        
    def copy_code(self):
        """Copy the game code to clipboard"""
        if self.game_code:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.game_code)
            messagebox.showinfo("Copied", "Game code copied to clipboard!")
            
    def show_help(self):
        """Show how to play instructions"""
        help_text = """HOW TO PLAY ROCK PAPER SCISSORS:

1. Host creates a game and shares the code
2. Other player joins with the code
3. Both players choose Rock, Paper, or Scissors
4. The winner is determined:
   - Rock beats Scissors
   - Paper beats Rock
   - Scissors beats Paper
   - Same choice is a tie

Play again to see who's the ultimate champion!"""
        messagebox.showinfo("How to Play", help_text)
        
    def back_to_menu(self):
        """Return to the main menu"""
        self.disconnect()
        self.create_main_menu()
        
    def disconnect(self):
        """Disconnect from the game"""
        self.is_connected = False
        try:
            if self.host_socket:
                self.host_socket.close()
            if self.client_socket:
                self.client_socket.close()
        except:
            pass
            
        self.host_socket = None
        self.client_socket = None
        self.connection = None
        
        self.create_main_menu()
        
    def run(self):
        """Run the application"""
        self.root.mainloop()

# Run the game
if __name__ == "__main__":
    game = RPSGame()
    game.run()