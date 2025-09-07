import tkinter as tk
import random

# List of verses (add as many as you want)
verses = [
    ("Philippians 4:13", "I can do all things through Christ who strengthens me."),
    ("Jeremiah 29:11", "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future."),
    ("John 3:16", "For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life."),
    ("Romans 8:28", "And we know that in all things God works for the good of those who love him, who have been called according to his purpose."),
    ("Psalm 23:1", "The Lord is my shepherd; I shall not want."),
    ("Proverbs 3:5-6", "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."),
    ("Isaiah 40:31", "But those who hope in the Lord will renew their strength. They will soar on wings like eagles; they will run and not grow weary, they will walk and not be faint.")
]

def show_verse():
    ref, text = random.choice(verses)
    verse_label.config(text=f"{ref}\n\n{text}")

# Create window
root = tk.Tk()
root.title("Bible Verse of the Day")
root.geometry("500x300")

# Title label
title_label = tk.Label(root, text="📖 Bible Verse Generator", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

# Verse display label
verse_label = tk.Label(root, text="Click the button to get a verse!", wraplength=450, justify="center", font=("Arial", 12))
verse_label.pack(pady=20)

# Button
verse_button = tk.Button(root, text="Get Verse", command=show_verse, font=("Arial", 14), bg="#d9ead3")
verse_button.pack(pady=20)

# Run the app
root.mainloop()
