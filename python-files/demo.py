import tkinter as tk
from tkinter import scrolledtext
import openai

# ---------- SETUP YOUR OPENAI API KEY ----------
openai.api_key = "YOUR_OPENAI_API_KEY"  # replace with your real key

# ---------- FUNCTIONS ----------
def send_message():
    user_msg = input_box.get()
    if not user_msg.strip():
        return
    append_message(user_msg, "You")
    input_box.delete(0, tk.END)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=150
        )
        bot_msg = response.choices[0].message.content.strip()
    except Exception as e:
        bot_msg = f"⚠️ Something went wrong: {e}"
    
    append_message(bot_msg, "Genius AI")

def append_message(msg, sender):
    chat_area.configure(state='normal')
    chat_area.insert(tk.END, f"{sender}: {msg}\n\n")
    chat_area.configure(state='disabled')
    chat_area.yview(tk.END)

# ---------- GUI ----------
root = tk.Tk()
root.title("🤖 Genius AI")
root.geometry("400x500")
root.resizable(False, False)

# Banner image (requires PIL)
try:
    from PIL import Image, ImageTk
    import requests
    from io import BytesIO

    url = "https://static.wikia.nocookie.net/marvelmovies/images/2/21/Illuminati_Mr._Fantastic.jpg"
    response = requests.get(url)
    img_data = Image.open(BytesIO(response.content))
    img_data = img_data.resize((250, 250))
    banner_img = ImageTk.PhotoImage(img_data)
    label_img = tk.Label(root, image=banner_img)
    label_img.pack(pady=5)
except:
    pass  # if PIL not installed, skip image

chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', width=50, height=20)
chat_area.pack(padx=10, pady=10)

input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=5, fill=tk.X)

input_box = tk.Entry(input_frame, width=30)
input_box.pack(side=tk.LEFT, padx=(0,5), pady=5, expand=True, fill=tk.X)
input_box.bind("<Return>", lambda event: send_message())

send_btn = tk.Button(input_frame, text="Send", command=send_message, bg="#007bff", fg="white")
send_btn.pack(side=tk.RIGHT)

root.mainloop()
