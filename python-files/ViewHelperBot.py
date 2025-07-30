import tkinter as tk
from tkinter import ttk, messagebox

# --- Tips and Ideas Database ---
def get_tips_and_ideas(target, subs, niche, game, long_form, short_form):
    tips_sections = {}
    video_ideas = []

    # Content Form Tips
    if long_form and not short_form:
        if niche == "Education":
            tips_sections["Long Form Tips"] = [
                "Break down complex topics into digestible parts.",
                "Use diagrams and visual aids to enhance explanations.",
                "Add chapter markers for longer tutorials."
            ]
        elif niche == "Fitness":
            tips_sections["Long Form Tips"] = [
                "Show full workout routines with warmups and cooldowns.",
                "Share progress journeys with detailed commentary.",
                "Include nutrition and health guidance in long videos."
            ]
        else:
            tips_sections["Long Form Tips"] = [
                "Focus on storytelling and pacing to keep viewers engaged.",
                "Use timestamps and highlights for easier navigation.",
                "Balance detail with viewer attention span."
            ]
    elif short_form and not long_form:
        if niche == "Beauty":
            tips_sections["Short Form Tips"] = [
                "Show quick before/after transitions.",
                "Use trending sounds for product showcases.",
                "Keep it vibrant and visual — less talking, more action."
            ]
        elif niche == "Fitness":
            tips_sections["Short Form Tips"] = [
                "Post short clips of impressive workout moves.",
                "Use timers and counters to make it engaging.",
                "Show tips in 15 seconds or less."
            ]
        else:
            tips_sections["Short Form Tips"] = [
                "Start with a hook in the first 3 seconds.",
                "Use fast-paced cuts and bold captions.",
                "Make your CTA (call to action) visual and short."
            ]
    elif long_form and short_form:
        tips_sections["Both Forms Tips"] = [
            "Create short teasers for your long videos.",
            "Use short form to funnel traffic to long form content.",
            "Cross-promote your different video formats."
        ]
    else:
        tips_sections["Content Form Tips"] = ["Please select at least one content form: Long Form or Short Form."]

    # Views Tips
    views_tips = []
    if niche == "Education":
        views_tips = [
            "Use keyword tools like TubeBuddy or VidIQ for SEO.",
            "Create videos on trending school topics or exam prep."
        ]
    elif niche == "Beauty":
        views_tips = [
            "Use visually appealing thumbnails and bold fonts.",
            "Follow and create trends around products and looks."
        ]
    elif niche == "Gaming":
        views_tips = [
            f"Cover updates, bugs, or patch notes about {game} right after release.",
            f"Use {game} mods or challenges to stand out."
        ]
    else:
        views_tips = [
            "Ask your audience what they want to see next in comments.",
            "Use storytelling thumbnails with expressions and action shots."
        ]

    tips_sections["Views Tips"] = views_tips

    # Engagement Tips
    if niche == "Fitness":
        engagement_tips = [
            "Challenge viewers to follow your fitness routine and tag you.",
            "Post transformation reels and celebrate viewer wins."
        ]
    elif subs < 1000:
        engagement_tips = [
            "Ask engaging questions in every video.",
            "Pin your favorite or funniest comment."
        ]
    else:
        engagement_tips = [
            "Host AMA (Ask Me Anything) sessions on live.",
            "Use polls, community posts, and Q&A stickers."
        ]
    tips_sections["Engagement Tips"] = engagement_tips

    # SEO Tips
    seo_tips = [
        f"Use searchable keywords specific to your niche: {niche}.",
        "Include the keyword in title, description, and tags."
    ]
    if target > 5000:
        seo_tips.append("Use subtitles or auto-captions to boost reach.")
    tips_sections["SEO Tips"] = seo_tips

    # Niche-specific Tips & Video Ideas
    if niche == "Gaming":
        tips_sections["Gaming Tips"] = [
            f"Cover new modes, glitches, or trends in {game}.",
            f"React to viral content related to {game}.",
            f"Do live challenges in {game} to engage your chat."
        ]
        if subs < 100:
            video_ideas = [
                f"Trying {game} for the first time! (Hilarious reactions)",
                f"Newbie fails compilation - {game} edition",
                f"Underrated weapons or tricks in {game}"
            ]
        elif subs < 1000:
            video_ideas = [
                f"Top 5 secret spots in {game}",
                f"Live ranking every weapon in {game}",
                f"Can I win with NO HUD in {game}?"
            ]
        else:
            video_ideas = [
                f"Pro tournament highlight in {game}",
                f"Fan submitted plays – reacting to YOUR {game} clips",
                f"Road to Top Rank in {game} – Full Series"
            ]
    elif niche == "Education":
        tips_sections["Education Tips"] = [
            "Use visuals and practical examples whenever possible.",
            "Make use of animations to simplify abstract ideas.",
            "Summarize key takeaways at the end."
        ]
        video_ideas = [
            "Math tricks you never learned in school",
            "Crash course on [Topic] in under 5 minutes",
            "What schools don’t teach about [concept]"
        ]
    elif niche == "Beauty":
        tips_sections["Beauty Tips"] = [
            "Use high quality lighting and camera angles.",
            "Keep background aesthetic and tidy.",
            "Explain what works for your skin type clearly."
        ]
        video_ideas = [
            "$10 vs $100 makeup challenge",
            "My 5-minute morning glam routine",
            "Trying viral TikTok beauty hacks"
        ]
    elif niche == "Fitness":
        tips_sections["Fitness Tips"] = [
            "Record in well-lit environments with clear form.",
            "Time your sets and show progression.",
            "Motivate and instruct without overwhelming."
        ]
        video_ideas = [
            "Follow-along 15 min no equipment workout",
            "What I eat in a day to stay lean",
            "Day 1 vs Day 30 transformation"
        ]
    else:
        tips_sections["General Tips"] = [
            "Be authentic and consistent.",
            "Deliver value in every video you post."
        ]
        video_ideas = [
            "A day in my life – honest version",
            "The biggest mistake I made when starting YouTube",
            "Why I started creating content"
        ]

    return tips_sections, video_ideas


# --- GUI Starts Here ---
root = tk.Tk()
root.title("View Helper Bot")
root.geometry("700x650")
root.configure(bg="#f4f4f4")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 10, "bold"))
style.configure("TLabel", font=("Segoe UI", 10))
style.configure("TCheckbutton", font=("Segoe UI", 10))

# --- Inputs ---
tk.Label(root, text="Enter Target Views:", bg="#f4f4f4").pack()
entry_views = tk.Entry(root)
entry_views.pack()

tk.Label(root, text="Enter Your Subscribers:", bg="#f4f4f4").pack()
entry_subs = tk.Entry(root)
entry_subs.pack()

tk.Label(root, text="Select Your Niche:", bg="#f4f4f4").pack()
niche_var = tk.StringVar()
niche_dropdown = ttk.Combobox(root, textvariable=niche_var, values=["Gaming", "Fitness", "Education", "Beauty", "Other"])
niche_dropdown.pack()

game_var = tk.StringVar()
game_dropdown = ttk.Combobox(root, textvariable=game_var, values=["Minecraft", "Fortnite", "Roblox", "Call of Duty", "Valorant"])
game_label = tk.Label(root, text="Select a Game (if Gaming):", bg="#f4f4f4")

def on_niche_change(event):
    if niche_var.get() == "Gaming":
        game_label.pack()
        game_dropdown.pack()
    else:
        game_label.pack_forget()
        game_dropdown.pack_forget()

niche_dropdown.bind("<<ComboboxSelected>>", on_niche_change)

# --- Format Checkboxes ---
tk.Label(root, text="Select Video Format:", bg="#f4f4f4").pack()
var_long_form = tk.BooleanVar()
var_short_form = tk.BooleanVar()
tk.Checkbutton(root, text="Long Form", variable=var_long_form, bg="#f4f4f4").pack()
tk.Checkbutton(root, text="Short Form", variable=var_short_form, bg="#f4f4f4").pack()

# --- Output Box ---
result_text = tk.Text(root, height=20, width=80, wrap="word", state=tk.DISABLED, bg="white")
result_text.pack(pady=10)

# --- Show Tips Function ---
def show_tips():
    try:
        target_views = int(entry_views.get())
        subs = int(entry_subs.get())
        niche = niche_var.get()
        game = game_var.get() if niche == "Gaming" else ""
        long_form = var_long_form.get()
        short_form = var_short_form.get()

        if not (long_form or short_form):
            messagebox.showwarning("Select Format", "Please select Long Form and/or Short Form.")
            return

        if niche == "Gaming" and not game:
            messagebox.showwarning("Game Missing", "Please select a game for the Gaming niche.")
            return

        tips_sections, video_ideas = get_tips_and_ideas(target_views, subs, niche, game, long_form, short_form)

        formatted = ""
        for section, tips in tips_sections.items():
            formatted += f"{section}:\n"
            for tip in tips:
                formatted += f"  • {tip}\n"
            formatted += "\n"

        formatted += "\nVideo Ideas:\n"
        for idea in video_ideas:
            formatted += f"  • {idea}\n"

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, formatted.strip())
        result_text.config(state=tk.DISABLED)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for views and subscribers.")

# --- Button ---
ttk.Button(root, text="Get Tips & Ideas", command=show_tips).pack(pady=10)

# --- Run the App ---
root.mainloop()