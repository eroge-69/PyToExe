import customtkinter as ctk
import requests
import threading
import time

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# 🔍 Search Function
def search_duckduckgo(query):
    url = "https://api.duckduckgo.com/"
    params = {'q': query, 'format': 'json', 'no_html': 1, 'skip_disambig': 1}
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("Abstract"):
        return data["Abstract"]
    elif data.get("RelatedTopics"):
        for topic in data["RelatedTopics"]:
            if isinstance(topic, dict) and topic.get("Text"):
                return topic["Text"]
    return "😕 Sorry, I couldn't find a proper answer."


# 🎬 Typing animation effect
def typing_effect(text, widget):
    widget.configure(state="normal")
    widget.delete("0.0", "end")
    for char in text:
        widget.insert("end", char)
        widget.update()
        time.sleep(0.01)
    widget.configure(state="disabled")


# 🎯 When search is triggered
def on_search():
    query = entry.get()
    if query.strip() == "":
        typing_effect("⚠️ Please enter a query.", output_box)
        return
    output_box.configure(state="normal")
    output_box.delete("0.0", "end")
    output_box.insert("end", "Searching...")
    output_box.configure(state="disabled")
    threading.Thread(target=search_thread, args=(query,)).start()


def search_thread(query):
    result = search_duckduckgo(query)
    typing_effect(f"🤖 Ketern AI: {result}", output_box)


# 🖼 GUI Layout
app = ctk.CTk()
app.title("Ketern AI")
app.geometry("600x500")
app.resizable(False, False)

title_label = ctk.CTkLabel(app, text="🌐 Ketern AI", font=("Arial", 28, "bold"))
title_label.pack(pady=20)

entry = ctk.CTkEntry(app, placeholder_text="Type your question here...", width=500, font=("Arial", 16))
entry.pack(pady=10)

search_button = ctk.CTkButton(app, text="🔎 Search", command=on_search, corner_radius=8, hover_color="green")
search_button.pack(pady=10)

output_box = ctk.CTkTextbox(app, width=550, height=250, font=("Arial", 14), wrap="word", state="disabled")
output_box.pack(pady=20)

exit_button = ctk.CTkButton(app, text="❌ Exit", command=app.destroy, fg_color="red", hover_color="#990000")
exit_button.pack(pady=5)

app.mainloop()
