import customtkinter as ctk
import datetime
import os
import webbrowser
import wikipedia
import pyautogui
import requests
import pyscreeze
import PIL

# --------------- Helper Functions ---------------- #
def search_wikipedia(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return "❌ No results on Wikipedia."

def search_google(query):
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"🔎 Searching Google for {query}..."
    return "Please tell me what to search."

def get_weather_google(city):
    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        return f"🌤️ Weather in {city}: " + requests.get(url).text
    except:
        return "⚠️ Couldn't fetch weather."

def take_screenshot():
    img = pyautogui.screenshot()
    img.save("screenshot.png")
    return "📸 Screenshot saved as screenshot.png"

def get_news():
    try:
        url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=50ec9419c5da4512a5cec0ad561cc4a1"
        data = requests.get(url).json()
        headlines = [article["title"] for article in data["articles"][:5]]
        return "📰 Top News:\n- " + "\n- ".join(headlines)
    except:
        return "⚠️ Couldn't fetch news."

def volume_up():
    return "🔊 Volume Up"

def volume_down():
    return "🔉 Volume Down"

def mute():
    return "🔇 Muted"

def shutdown():
    return "⚠️ Shutting down (not executed for safety)"

def restart():
    return "♻ Restarting (not executed for safety)"

def sleep():
    return "💤 Sleeping (not executed for safety)"

def logout():
    return "👤 Logging out (not executed for safety)"

# ---------------- Chatbot Response ---------------- #
def chatbot_response():
    query = entry.get().lower()
    if not query.strip():
        return
    insert_message("You", query, "user")

    response = "❌ Sorry, I didn't get that."

    if "time" in query:
        response = f"⏰ Time is {datetime.datetime.now().strftime('%H:%M:%S')}"
    elif "hi" in query:
        response = "✋ Hi"
    elif "hello" in query:
        response = "✋ Hello"
    elif "namaste" in query:
        response = "🙏 Namaste"
    elif "open youtube" in query:
        webbrowser.open("https://youtube.com")
        response = "📺 Opening YouTube"
    elif "open google" in query:
        webbrowser.open("https://google.com")
        response = "🌐 Opening Google"
    elif "open notepad" in query:
        os.system("notepad.exe")
        response = "📄 Opening Notepad"
    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        response = search_wikipedia(topic) if topic else "Please tell me a topic."
    elif "search" in query:
        search_term = query.replace("search", "").strip()
        response = search_google(search_term)
    elif "weather" in query:
        city = query.replace("weather", "").strip()
        response = get_weather_google(city) if city else "Please tell me a city."
    elif "screenshot" in query:
        response = take_screenshot()
    elif "news" in query:
        response = get_news()
    elif "volume up" in query:
        response = volume_up()
    elif "volume down" in query:
        response = volume_down()
    elif "mute" in query:
        response = mute()
    elif "shutdown" in query:
        response = shutdown()
    elif "restart" in query:
        response = restart()
    elif "sleep" in query:
        response = sleep()
    elif "logout" in query:
        response = logout()
    elif "bye" in query or "exit" in query:
        response = "👋 Goodbye!"
        insert_message("Jarvis", response, "bot")
        chatbot_win.quit()
        return

    insert_message("Jarvis", response, "bot")
    entry.delete(0, "end")

# ---------------- Chat Bubble Insert ---------------- #
def insert_message(sender, message, side):
    bubble = ctk.CTkFrame(chat_frame, corner_radius=20,
                          fg_color="#4CAF50" if side=="user" else "#3A7CA5")
    label = ctk.CTkLabel(bubble, text=f"{sender}: {message}",
                         wraplength=600, justify="left", anchor="w")
    label.pack(padx=10, pady=5)
    if side == "user":
        bubble.pack(anchor="w", pady=5, padx=10)
    else:
        bubble.pack(anchor="e", pady=5, padx=10)

# ---------------- Open Chatbot ---------------- #
def open_chatbot():
    global chatbot_win, entry, chat_frame
    login_win.destroy()

    chatbot_win = ctk.CTk()
    chatbot_win.title("C.H.A.T B.O.T")
    chatbot_win.state("zoomed")  # maximize

    # Sidebar
    sidebar = ctk.CTkFrame(chatbot_win, width=200, corner_radius=15, fg_color="#2C2C2C")
    sidebar.pack(side="left", fill="y", padx=10, pady=10)

    ctk.CTkLabel(sidebar, text="⚙ Menu", font=("Arial", 16, "bold")).pack(pady=10)
    controls = [
        ("Shutdown", shutdown),
        ("Restart", restart),
        ("Sleep", sleep),
        ("Logout", logout),
        ("Screenshot", take_screenshot),
        ("News", get_news),
        ("Weather", lambda: get_weather_google("Delhi")),
    ]
    for name, func in controls:
        ctk.CTkButton(sidebar, text=name, command=lambda f=func: insert_message("Jarvis", f(), "bot")).pack(pady=5)

    # Chat area
    right_frame = ctk.CTkFrame(chatbot_win)
    right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    chat_frame = ctk.CTkScrollableFrame(right_frame, width=800, height=500)
    chat_frame.pack(pady=10, fill="both", expand=True)

    entry_frame = ctk.CTkFrame(right_frame)
    entry_frame.pack(fill="x", pady=5)

    entry = ctk.CTkEntry(entry_frame, width=700, placeholder_text="Ask me something...")
    entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

    send_button = ctk.CTkButton(entry_frame, text="Send", command=chatbot_response)
    send_button.pack(side="right", padx=10)

    chatbot_win.mainloop()

# ---------------- Login Screen ---------------- #
def check_login():
    if username_entry.get() == "paritosh" and password_entry.get() == "1234":
        open_chatbot()
    else:
        error_label.configure(text="❌ Invalid Credentials")

login_win = ctk.CTk()
login_win.title("Login")
login_win.geometry("400x300+600+250")

ctk.CTkLabel(login_win, text="🔐 Login to C.H.A.T B.O.T", font=("Arial", 20, "bold")).pack(pady=20)

username_entry = ctk.CTkEntry(login_win, placeholder_text="Username")
username_entry.pack(pady=10)

password_entry = ctk.CTkEntry(login_win, placeholder_text="Password", show="*")
password_entry.pack(pady=10)

login_button = ctk.CTkButton(login_win, text="Login", command=check_login)
login_button.pack(pady=10)

error_label = ctk.CTkLabel(login_win, text="", text_color="red")
error_label.pack()

login_win.mainloop()
