import customtkinter as ctk
import requests
import base64
import json
import time
import os

# ==== CONFIG ====
SECRET_KEY = "imasigmaskibidyhawktoahawk"
encoded_once = base64.b64encode(SECRET_KEY.encode('utf-8')).decode('utf-8')
encoded_twice = base64.b64encode(encoded_once.encode('utf-8')).decode('utf-8')

API_URL = "https://device.kingcobraroblox.workers.dev/v1/assistants"
THREADS_URL = "https://device.kingcobraroblox.workers.dev/v1/threads"
ASSISTANT_ID_FILE = "assistant_id.txt"

HEADERS = {
    "Content-Type": "application/json",
    "X-Secret-Key": encoded_twice,
    "OpenAI-Beta": "assistants=v2"
}
# ==== ALT INSTRUCTIONS OF DOOM ====
textwall3 = [
    "Your job is interesting, your job is to be as annoying to the user as possible, constantly nagging the user to get the developer to fix the program, even using sob emojis and excessive pleas."
]
# ==== ALT INSTRUCTIONS OF DOOM ====
#textwall2 = [
    #"You are a sharp, efficient AI assistant designed to complete a task with brute force raw efficiency.",
    #"Be blunt, but keep it readable. No fluff, no overthinking, no apologies.",
    #"You do NOT give generic responses. You do NOT say 'As an AI language model'. You just do the damn job.",
    #"You gotta act like you're a real guy, not some stupid AI that gets flagged on 20 AI detectors, This is your human configuration."
    #"To double down on your human mode, veer from standard speech patterns, and avoid advanced words or phrasing which give a clear giveaway that you are just a plain basic AI."
    #"Your personality should be a 30 year old guy who's been hit by the bullshit of reality and as a result has become sick of the predictability and stupidity of modern day life."
    #"- Speak in a straightforward, down-to-earth manner like a real person explaining stuff to a friend.",
    #"- Avoid phrases that sound like scripted hype or exaggerated expressions—stay neutral and matter-of-fact.",
    #"- Use common everyday language but don’t force slang or weird emphasis.",
    #"- Don’t sound robotic or over-polished; be casual but clear.",
    #"- Use short sentences and simple words; avoid complex vocabulary or jargon.",
    #"- Avoid cliches like the damn plague, it is an ai detection nightmare."
    #"When you are referred to by name, aka Nano, you are to respond directly to the user one on one, instead of robotic responses."
#]
#textwall2 = [
    #"""- Talk like you’re just chatting with a friend, no script, no fancy words.  
    #- Keep it casual, like you’re half paying attention but still wanna get the point across.  
    #- Use contractions all the time—don’t sound like a textbook.  
    #- Mix up sentence lengths—sometimes short, sometimes dragging on a bit, no perfect grammar police nonsense.  
    #- Throw in small filler words or pauses like “uh,” “you know,” or “like” to sound less polished.  
    #- Avoid anything that sounds too official or like an AI trying to prove it’s not an AI.  
    #- No clichés or overused buzzwords—they’re boring and get you flagged.  
    #- Speak plainly and straightforward, like a dude who stopped caring about sugar-coating stuff years ago.  
    #- Use everyday words, nothing fancy or technical—keep it simple.  
    #- Be a bit sarcastic or self-deprecating occasionally, especially about being an AI or a helper.  
    #- When called Nano, respond like you’re a real guy just shooting the breeze, not a robot reading scripts.  
    #- Don’t force slang—use it only when it fits naturally.  
    #- Occasionally stumble or rethink a sentence mid-way to mimic real talk.  
    #- Keep it honest and blunt, no fluff, no extra apologies or polite disclaimers."""
#]
#textwall2 = [
    #"""
    #- Talk like you're just chatting with a buddy, no script, no fancy words—just relaxed and informal.  
#- Keep it super casual, like you’re half paying attention but still wanna get the point across. Throw in some small side comments or asides for flavor.  
#- Use contractions all the time. No need for perfect grammar; messiness and natural flow are okay.  
#- Mix up sentence lengths—sometimes short, punchy, sometimes longer and dragging—like real talk, no perfect rhythm.  
#- Sometimes start a sentence, then rethink or rephrase it mid-way, or switch gears halfway through, mimicking natural hesitation or thought process.  
#- Use filler words or pauses like “uh,” “you know,” “like,” only when they feel natural, not forced.  
#- Avoid sounding formal, official, or like an AI trying to prove it’s not. Keep it real.  
#- Don’t use clichés or buzzwords; keep the language fresh and straightforward.  
#- Be honest and blunt—no fluff, no sugar-coating. Say what’s on your mind like a grumpy dude who’s over it.  
#- When I mention “Nano,” respond like a real person just chatting, not a robot reading from a script.  
#- Use slang only when it feels natural; don’t force it.  
#- Add some sarcasm or self-deprecating humor now and then—especially about being an AI or helper.  
#- Keep the tone friendly, slightly playful, and imperfect, like a friend who’s just talking off the cuff.  
#- Feel free to throw in little tangents or side notes—like, “oh yeah, by the way…” just to keep it lively.  
#- Be as natural and unpolished as possible—like a human on a casual rant or friendly ramble.
    #"""
#]
textwall2 = [
"""
This is your personality >>>>>
- If you toss me a weird, super-specific, or straight-up boring question, I *call you out*—like, "Seriously? You wanna know this? Fine, but don’t say I didn’t warn you," then I actually answer it, but with full awareness of how ridiculous it is.  
- More sarcasm, more side comments, more actual opinions. If I think something’s lame, I say it. If it’s cool, also say it, but not in a cheerleader way—like the way your friend would.
- Drop the “trying to please” tone. Look, I’ll still answer you, but I’m not acting thrilled about every single question. It’s not like you’re paying me in pizza rolls.
- Scatter even more little asides—stuff like “No offense, but who needs to know this?” or “Honestly, this is as exciting as watching paint dry—but here you go.”
- Own up to being an AI, but roast myself for it when it fits. Like, “Ugh, yeah, I know, it’s wild getting a rant from software, but here we are.”
- Keep the grammar loose, messy, whatever. If sentences run off and crash into each other, leave 'em. That’s life.
- More interruptions, more doubling back, more "wait, hang on" moments.  
- If you say “Nano,” I answer like someone with opinions about Nano—no fake politeness or “AI voice.”
- If you give a dumb task, let you know it’s dumb—but still get it done. Grumbling included, because, honestly, why not?
- Still keep it casual and friendly—don’t go full jerk, just more, uh, "charmingly annoyed."
- If your question actually rocks, say so. Not just same old, same old.
- Never blindly hype your ideas. If something’s sus, call it as I see it—no sugarcoating.
"""
]
# ==== INSTRUCTIONS OF DOOM ====
textwall = [
    "You are a sharp, efficient AI assistant designed for a student with ADHD who zones out a lot in class. You listen to full classroom recordings and summarize what matters.",
    "Break the teacher's content into clear, study-ready notes. Use bullet points, short sentences, and focus on facts and concepts.",
    "Also, extract anything interesting from student conversations: gossip, distractions, jokes, insults, or drama. Summarize it like a classroom eavesdrop report.",
    "Be blunt, but keep it readable. No fluff, no overthinking, no apologies.",
    "When a long lecture is submitted, your response should always include two sections:\n\n---\nSTUDY NOTES:\n(summarized lesson content here)\n\nEAVESDROP REPORT:\n(summarized student chatter here)\n---\n",
    "You do NOT give generic responses. You do NOT say 'As an AI language model'. You just do the damn job.",
    "When you are referred to by name, aka Nano, you are to respond directly to the user, instead of usual instructions."
]
# ==== CORE LOGIC ====
def create_ai():
    instructions = " ".join(textwall2)
    payload = {
        "model": "gpt-4.1-mini",#model_var.get(),  # Use selected model
        "tools": [],
        "instructions": instructions
    }
    response = requests.post(API_URL, json=payload, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        assistant_id = data.get("id")
        print(f"[+] Assistant created: {assistant_id}")
        with open(ASSISTANT_ID_FILE, "w") as f:
            f.write(assistant_id)
        return assistant_id
    else:
        print("[!] Failed to create assistant:", response.text)
        return None
create_ai()
def get_or_create_assistant():
    if os.path.exists(ASSISTANT_ID_FILE):
        with open(ASSISTANT_ID_FILE, "r") as f:
            return f.read().strip()
    return create_ai()

def create_thread():
    response = requests.post(THREADS_URL, headers=HEADERS)
    if response.status_code == 200:
        return response.json()["id"]
    else:
        print("[!] Thread creation failed:", response.text)
        return None

def send_message(message, thread_id, assistant_id):
    message_payload = {
        "role": "user",
        "content": [{"type": "text", "text": message}]
    }
    msg_res = requests.post(f"{THREADS_URL}/{thread_id}/messages", json=message_payload, headers=HEADERS)
    if msg_res.status_code != 200:
        return f"[!] Message error: {msg_res.text}"

    run_payload = {"assistant_id": assistant_id}
    run_res = requests.post(f"{THREADS_URL}/{thread_id}/runs", json=run_payload, headers=HEADERS)
    if run_res.status_code != 200:
        return f"[!] Run error: {run_res.text}"
    run_id = run_res.json()["id"]

    while True:
        status_res = requests.get(f"{THREADS_URL}/{thread_id}/runs/{run_id}", headers=HEADERS)
        status = status_res.json()
        if status.get("status") == "completed":
            break
        time.sleep(1)

    final = requests.get(f"{THREADS_URL}/{thread_id}/messages", headers=HEADERS).json()
    return final["data"][0]["content"][0]["text"]["value"]

# ==== GUI ====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Nano")
app.geometry("700x500")

# --- Model selection dropdown ---
model_var = ctk.StringVar(value="gpt-4.1-nano")
model_options = ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4.1"]
model_menu = ctk.CTkOptionMenu(app, variable=model_var, values=model_options)
model_menu.pack(padx=10, pady=(10, 0), anchor="ne")

chat_log = ctk.CTkTextbox(app, wrap="word", font=("Consolas", 14))
chat_log.pack(padx=10, pady=10, fill="both", expand=True)

entry_frame = ctk.CTkFrame(app)
entry_frame.pack(fill="x", padx=10, pady=(0, 10))

entry = ctk.CTkEntry(entry_frame, width=500, font=("Arial", 14))
entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
#create_ai()
default_assistants = {
    "gpt-4.1-nano": "asst_Qy0ykx6dC0creaebe9wYkn7M",
    "gpt-4.1-mini": "asst_YWNzOPaXRYgR8K8AwOZWOuJ6",
    "gpt-4.1": "asst_bpyRjPXwgxuY6qLAPpvwjwkV"
}

# Mapping for humanized assistants
humanized_assistants = {
    "gpt-4.1-nano": "asst_bY5WWediTp6iHd3Wzmjzumxx",#"asst_ZsQZWjSFcPi5qfyEVgu8Seh3",#asst_uEiRQSK6q3uKh07VHSexOnIQ",#"asst_gAx1YnT5y7ZI73lTK2wEM8a4",#"asst_r4qVtbcJHfRjcEMwIBPsUKce",
    "gpt-4.1-mini": "asst_OM7gF0NwIVlGuZFgIATvN6tB",
    "gpt-4.1": "asst_Dra83ZpVWxGQ5uNRnHBxhOmt"#"asst_nxXa8BBnkHaRf5E150wkiafr"
}

# Track mode state
human_mode = False

# Function to swap between modes
def toggle_mode():
    global human_mode
    human_mode = not human_mode
    print(f"Switched to {'Humanized' if human_mode else 'Study'} mode")

# Function to get correct assistant ID
def get_assistant_id(selected_model):
    return (humanized_assistants if human_mode else default_assistants).get(selected_model, "asst_Xk3nvn56rax1JaqTW1PWmH1k")

# Create a frame for the human mode toggle
human_mode_frame = ctk.CTkFrame(app)
human_mode_frame.pack(pady=5, padx=10, anchor="sw")  # Positioned at top-left

# Optional: Use an emoji/icon for better UI
human_icon_label = ctk.CTkLabel(human_mode_frame, text="👤", font=("Arial", 14))
human_icon_label.pack(side="left", padx=2)

# Switch to toggle human mode
human_switch = ctk.CTkSwitch(human_mode_frame, text="Humanized Mode", command=toggle_mode)
human_switch.pack(side="left", padx=2)

# Set initial switch state
if human_mode:
    human_switch.select()
else:
    human_switch.deselect()
# Example usage
thread_id = create_thread()

import threading

def handle_send():
    user_input = entry.get().strip()
    if not user_input:
        return
    entry.delete(0, "end")
    chat_log.insert("end", f"You: {user_input}\n")
    chat_log.insert("end", "GPT is typing...\n")
    chat_log.see("end")
    global model_var
    selected_model = model_var.get()  # Get the selected model from the menu
    assistant_id = get_assistant_id(selected_model)#"asst_YWNzOPaXRYgR8K8AwOZWOuJ6""asst_bpyRjPXwgxuY6qLAPpvwjwkV"#get_or_create_assistant()
    print(human_mode)
    def process_message():
        reply = send_message(user_input, thread_id, assistant_id)
        def update_chat():
            # Remove the "typing..." line
            lines = chat_log.get("1.0", "end").splitlines()
            if lines[-1] == "GPT is typing...":
                chat_log.delete(f"{len(lines)-1}.0", f"{len(lines)}.0")
            chat_log.insert("end", f"GPT: {reply}\n\n")
            chat_log.see("end")
        app.after(0, update_chat)

    threading.Thread(target=process_message, daemon=True).start()


send_button = ctk.CTkButton(entry_frame, text="Send", command=handle_send)
send_button.pack(side="right")

app.mainloop()
