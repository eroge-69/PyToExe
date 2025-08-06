import tkinter as tk
from tkinter import scrolledtext

class ChatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Dilip AI")

        # Create a scrolled text area for chat history
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD, width=50, height=20)
        self.chat_area.grid(row=0, column=0, padx=10, pady=10)

        # Create an entry box for user input
        self.entry_box = tk.Entry(self.root, width=50)
        self.entry_box.grid(row=1, column=0, padx=10, pady=10)

        # Create a send button
        self.send_button = tk.Button(self.root, text="Send", width=10, command=self.send_message)
        self.send_button.grid(row=2, column=0, padx=10, pady=10)

    def send_message(self):
        user_message = self.entry_box.get()  # Get user input
        if user_message:
            self.chat_area.configure(state='normal')
            self.chat_area.insert(tk.END, f"You: {user_message}\n")  # Show user message
            self.chat_area.yview(tk.END)  # Scroll to bottom of the chat

            # Get bot response
            bot_response = self.get_bot_response(user_message)
            self.chat_area.insert(tk.END, f"Bot: {bot_response}\n\n")  # Show bot response
            self.chat_area.yview(tk.END)

            # Clear the entry box for next input
            self.entry_box.delete(0, tk.END)

    def get_bot_response(self, message):
        # Simple logic for bot response (you can make it more complex with NLP, etc.)
        message = message.lower()
        if "hello" in message or "hi" in message:
            return "Hello! How are you today?"
        elif "i am fine" in message or "i m fine" in message or "fine" in message:
            return "I'm also fine,  how can i help you?"
        elif "what is address of dilip kumar pandit" in message or "what is add of dilip kumar pandit" in message:
            return "At-Dasua,Post- Khesar,Dist- Banka, Srate - Bihar -813207"
        elif "thanks" in message or "thank you" in message:
            return "thank you for searching"
        elif "bye" in message or "by" in message:
            return "Goodbye! Have a nice day!"
        else:
            return "I'm sorry, I have no idea ,what are you saying."

if __name__ == "__main__":
    root = tk.Tk()
    chatbot = ChatBot(root)
    root.mainloop()
