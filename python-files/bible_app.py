import tkinter as tk
import random

# List of verses (add as many as you want)
verses = [
    ("Genesis 1:1", "In the beginning God created the heavens and the earth."),
    ("Genesis 28:15", "I am with you and will watch over you wherever you go."),
    ("Exodus 14:14", "The Lord will fight for you; you need only to be still."),
    ("Deuteronomy 31:6", "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go."),
    ("Joshua 1:9", "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go."),
    ("2 Samuel 22:31", "As for God, his way is perfect: The Lord’s word is flawless; he shields all who take refuge in him."),
    ("Nehemiah 8:10", "The joy of the Lord is your strength."),
    ("Job 19:25", "I know that my redeemer lives, and that in the end he will stand on the earth."),
    ("Psalm 1:6", "For the Lord watches over the way of the righteous, but the way of the wicked leads to destruction."),
    ("Psalm 16:8", "I keep my eyes always on the Lord. With him at my right hand, I will not be shaken."),
    ("Psalm 18:2", "The Lord is my rock, my fortress and my deliverer; my God is my rock, in whom I take refuge."),
    ("Psalm 23:1", "The Lord is my shepherd; I shall not want."),
    ("Psalm 27:1", "The Lord is my light and my salvation—whom shall I fear?"),
    ("Psalm 28:7", "The Lord is my strength and my shield; my heart trusts in him, and he helps me."),
    ("Psalm 34:8", "Taste and see that the Lord is good; blessed is the one who takes refuge in him."),
    ("Psalm 37:4", "Take delight in the Lord, and he will give you the desires of your heart."),
    ("Psalm 46:1", "God is our refuge and strength, an ever-present help in trouble."),
    ("Psalm 55:22", "Cast your cares on the Lord and he will sustain you; he will never let the righteous be shaken."),
    ("Psalm 91:1", "Whoever dwells in the shelter of the Most High will rest in the shadow of the Almighty."),
    ("Psalm 119:105", "Your word is a lamp to my feet and a light to my path."),
    ("Proverbs 3:5-6", "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."),
    ("Proverbs 18:10", "The name of the Lord is a fortified tower; the righteous run to it and are safe."),
    ("Isaiah 9:6", "For to us a child is born, to us a son is given… and he will be called Wonderful Counselor, Mighty God, Everlasting Father, Prince of Peace."),
    ("Isaiah 26:3", "You will keep in perfect peace those whose minds are steadfast, because they trust in you."),
    ("Isaiah 40:8", "The grass withers and the flowers fall, but the word of our God endures forever."),
    ("Isaiah 40:31", "But those who hope in the Lord will renew their strength. They will soar on wings like eagles."),
    ("Isaiah 41:10", "So do not fear, for I am with you; do not be dismayed, for I am your God."),
    ("Jeremiah 29:11", "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you."),
    ("Lamentations 3:22-23", "The steadfast love of the Lord never ceases; his mercies never come to an end; they are new every morning."),
    ("Matthew 5:14", "You are the light of the world. A town built on a hill cannot be hidden."),
    ("Matthew 6:33", "But seek first his kingdom and his righteousness, and all these things will be given to you as well."),
    ("Matthew 11:28", "Come to me, all you who are weary and burdened, and I will give you rest."),
    ("Matthew 19:26", "With man this is impossible, but with God all things are possible."),
    ("Matthew 22:37", "Love the Lord your God with all your heart and with all your soul and with all your mind."),
    ("Mark 9:23", "Everything is possible for one who believes."),
    ("Mark 12:30", "Love the Lord your God with all your heart and with all your soul and with all your mind and with all your strength."),
    ("Luke 6:31", "Do to others as you would have them do to you."),
    ("Luke 11:9", "Ask and it will be given to you; seek and you will find; knock and the door will be opened to you."),
    ("Luke 18:27", "What is impossible with man is possible with God."),
    ("John 3:16", "For God so loved the world that he gave his one and only Son."),
    ("John 8:12", "I am the light of the world. Whoever follows me will never walk in darkness."),
    ("John 14:6", "I am the way and the truth and the life. No one comes to the Father except through me."),
    ("John 15:5", "I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit."),
    ("Acts 1:8", "But you will receive power when the Holy Spirit comes on you; and you will be my witnesses."),
    ("Acts 16:31", "Believe in the Lord Jesus, and you will be saved—you and your household."),
    ("Romans 1:16", "For I am not ashamed of the gospel, because it is the power of God that brings salvation."),
    ("Romans 3:23", "For all have sinned and fall short of the glory of God."),
    ("Romans 5:8", "But God demonstrates his own love for us in this: While we were still sinners, Christ died for us."),
    ("Romans 6:23", "For the wages of sin is death, but the gift of God is eternal life in Christ Jesus our Lord."),
    ("Romans 8:1", "Therefore, there is now no condemnation for those who are in Christ Jesus.")
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
