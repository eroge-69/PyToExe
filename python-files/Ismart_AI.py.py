import customtkinter as ctk
import openai
import pyttsx3

# ---- CONFIG ----
openai.api_key = "4648e5c7-6bf1-4656-bd32-bf08aeba1d00"

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)  # speaking speed

# ---- MEMORY ----
conversation_history = []

# ---- FUNCTIONS ----
def get_response(prompt):
    global conversation_history
    conversation_history.append(f"You: {prompt}")
    # Join last 10 messages for context
    context = "\n".join(conversation_history[-10:])
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=context,
        max_tokens=200,
        temperature=0.7
    )
    answer = response.choices[0].text.strip()
    conversation_history.append(f"ISMART: {answer}")
    return answer

def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return
    chat_box.configure(state='normal')
    chat_box.insert(ctk.END, f"You: {user_input}\n")
    chat_box.configure(state='disabled')
    entry.delete(0, ctk.END)
    response = get_response(user_input)
    chat_box.configure(state='normal')
    chat_box.insert(ctk.END, f"ISMART: {response}\n\n")
    chat_box.configure(state='disabled')
    chat_box.see(ctk.END)
    engine.say(response)
    engine.runAndWait()

# ---- GUI SETUP ----
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("ISMART AI Assistant")
root.geometry("600x600")

chat_box = ctk.CTkTextbox(root, state='disabled')
chat_box.pack(padx=10, pady=10, fill='both', expand=True)

entry = ctk.CTkEntry(root)
entry.pack(padx=10, pady=10, fill='x')
entry.bind("<Return>", lambda event: send_message())

send_button = ctk.CTkButton(root, text="Send", command=send_message)
send_button.pack(pady=5)

root.mainloop()
