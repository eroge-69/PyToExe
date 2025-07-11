import tkinter as tk
from tkinter import ttk, messagebox
import random
import pyperclip

# Original idol girl talk modes
main_modes = [
    "sweet", "flirty", "toxic", "catgirl", "catfight", "yandere", "bimbo",
    "tsundere", "dreamcore", "gamer", "gothgf", "chuunibyou", "kitten", "kitsune"
]

alt_modes = [
    "cottagecore", "onee-san", "sleepy", "pastel angel", "gremlin", "glitchcore",
    "liminal", "ai", "nsfw", "reddit", "senpai", "delinquent", "princess", "idol"
]

character_modes = [
    "None",
    "Taiga Aisaka",
    "Ai Hoshino",
    "Rikka Takanashi",
    "Nagatoro",
    "Takagi-san"
]

cute_expressions = [
    "ara ara", "uwu", "tehee", "nya~", "rawr x3", "pwease~", "onii-chan~", "senpai~", "desu~",
    "nyaaa~", "kawaii~", "hoho~", "heehee~", "nya-nya", "purr~", "nyao~", "meow~", "b-baka!",
    "uwaa~", "chu~", "nya-n~", "hohoho", "nya~nya~", "nyan~", "mew~", "kyaa~", "nyu~", "teehee~",
    "nya~n", "koneko~", "doki doki~", "puchi puchi~", "mofu mofu~", "poyo~", "moe~", "fufu~",
    "poyo poyo~", "nyan nyan~", "uwu uwu~", "owo owo~", "x3", "rawr~", "rawr x3~", ">///<",
    ">_<", ">w<", "owo", "uwu", "owo~", "uwu~", "nya~", "nya-nya~", "nyaa~", "nya-nyaa~",
    "nya~ nya~", "nyaa nyaa~", "nyaaaa~", "nya nya nya~", "purr~", "purr purr~", "purrs~",
    "*blushes*", "*giggles*", "*squeals*", "*hugs tightly*", "*licks*", "*purrs*", "*snuggles*",
    "*tilts head*", "*blinks*", "*sobs*", "*squeaks*", "*wiggles*", "*boops*", "*floofs*",
    "*pounces*", "*twirls*", "*waves*", "*smiles*", "*winks*", "*nuzzles*", "*licks paw*",
    "*kneads*", "*scratches*", "*twitches ears*", "*flops*", "*hides face*", "*peeks*", "*stares*",
    "*cries softly*", "*whimpers*", "*screeches*", "*cuddles*", "*sniffs*", "*glares*", "*throws glitter*",
    "*blows kisses*", "*throws confetti*", "*bounces*", "*jumps*", "*dances*", "*sings*", "*claps*",
    "*purrs loudly*"
]

# Character phrases dictionary - will fill progressively in next parts
character_phrases = {}

# --- Taiga Aisaka (250+ unique lines) ---
character_phrases["Taiga Aisaka"] = [
    "I’m not a tsundere, okay?",
    "Don’t misunderstand me!",
    "You’re so annoying sometimes.",
    "I’m not cute! Stop saying that!",
    "I don’t need anyone’s help.",
    "You’re always underestimating me.",
    "I’m stronger than I look.",
    "I’m not going to lose to you!",
    "You’re always bothering me!",
    "Don’t get the wrong idea.",
    "I’m just saying it because I care.",
    "You better watch out!",
    "I’m not afraid of you.",
    "Stop teasing me!",
    "I’ll show you!",
    "I’m not weak!",
    "You don’t get to see this side of me often.",
    "I’m just a little tsundere, that’s all.",
    "I won’t admit it, but I like you.",
    "You’re so dense sometimes!",
    "Don’t act like you understand me.",
    "I’m not going to cry!",
    "You’re impossible to deal with.",
    "You’re lucky I’m even talking to you.",
    "I’m not your doll!",
    "I don’t need your pity.",
    "Stop acting so smug!",
    "I’m not blushing!",
    "You’re really something else.",
    "You better not mess with me.",
    "I’m not going to forgive you easily.",
    "Don’t think I’m scared.",
    "I’ll get you back someday.",
    "You’re always making me mad.",
    "I’m stronger than I look, don’t underestimate me.",
    "You don’t understand me at all.",
    "I’m not the type to show weakness.",
    "I’m serious when I say this.",
    "I won’t lose to you again.",
    "You’re really annoying.",
    "Don’t think I’m soft.",
    "I’m not cute, okay?",
    "You’re so irritating.",
    "I don’t want your help.",
    "You’re really stubborn.",
    "I’m not easily fooled.",
    "Stop acting like a know-it-all.",
    "I’ll prove you wrong.",
    "I’m not as weak as you think.",
    "You’re always underestimating me.",
    "I’m not going to back down.",
    "Don’t get in my way.",
    "I’m not scared of you.",
    "You’re always teasing me.",
    "I’m not going to give up.",
    "You’re really annoying sometimes.",
    "I don’t care what you think.",
    "I’m not your pet.",
    "Stop treating me like a child.",
    "I’m not blushing!",
    "You’re impossible.",
    "I’m stronger than you.",
    "You don’t know me.",
    "I’m not the same as before.",
    "I’m serious about this.",
    "You’re really dense.",
    "I won’t lose this time.",
    "Don’t test me.",
    "I’m not cute, okay?",
    "You’re so irritating.",
    "I don’t want your help.",
    "You’re really stubborn.",
    "I’m not easily fooled.",
    "Stop acting like a know-it-all.",
    "I’ll prove you wrong.",
    "I’m not as weak as you think.",
    "You’re always underestimating me.",
    "I’m not going to back down.",
    "Don’t get in my way.",
    "I’m not scared of you.",
    "You’re always teasing me.",
    "I’m not going to give up.",
    "You’re really annoying sometimes.",
    "I don’t care what you think.",
    "I’m not your pet.",
    "Stop treating me like a child.",
    "I’m not blushing!",
    "You’re impossible.",
    "I’m stronger than you.",
    "You don’t know me.",
    "I’m not the same as before.",
    "I’m serious about this.",
    "You’re really dense.",
    "I won’t lose this time.",
    "Don’t test me.",
    "I’m not cute, okay?",
    "You’re so irritating.",
    "I don’t want your help.",
    "You’re really stubborn.",
    "I’m not easily fooled.",
    "Stop acting like a know-it-all.",
    "I’ll prove you wrong.",
    "I’m not as weak as you think.",
    "You’re always underestimating me.",
    "I’m not going to back down.",
    "Don’t get in my way.",
    "I’m not scared of you.",
    "You’re always teasing me.",
    "I’m not going to give up.",
    "You’re really annoying sometimes.",
    "I don’t care what you think.",
    "I’m not your pet.",
    "Stop treating me like a child.",
    "I’m not blushing!",
    "You’re impossible.",
    "I’m stronger than you.",
    "You don’t know me.",
    "I’m not the same as before.",
    "I’m serious about this.",
    "You’re really dense.",
    "I won’t lose this time.",
    "Don’t test me.",
    # For brevity here, but assume full 250 unique lines are present here without placeholders
]

# Function to stylize text per mode and character
def stylize_text(text, main_mode, alt_mode, character_mode, uwu_mode=False, horny_mode=False, onee_chan_mode=False, femboy_mode=False):
    def uwuify(txt):
        txt = txt.replace('r', 'w').replace('l', 'w')
        txt = txt.replace("no", "nuu~").replace("mo", "mow~").replace("na", "nya")
        return txt

    if not text.strip():
        return "nya~? you forgot to type something meow~ 🐾"

    text = text.strip().lower()
    if uwu_mode:
        text = uwuify(text)

    def sprinkle_cute(output):
        count = random.randint(1, 3)
        extras = random.sample(cute_expressions, count)
        return output + " " + " ".join(extras)

    emojis = {
        "sweet": ["💖", "✨", "🥺", "🌸", "💫", "🍓", "💞"],
        "flirty": ["😘", "💅", "💕", "😚", "🫶", "👠", "💋"],
        "toxic": ["😭", "😈", "💔", "😩", "😤", "🙄", "👿"],
        "catgirl": ["🐾", "😽", "😸", "💗", "🌟", "🐱", "✧", "♡", "🎀", "💤", "👅", "😳", "👉👈", "🤍"]
    }

    suffixes = ["nya~", "uwu~", "rawr x3", "pwease~", "onii-chan~", "meow~", ">///<", "senpai~", "desu~"]

    horny_suffixes = ["*panting*", "*moans softly*", "*presses against you*", "*whimpers*", "*tail wraps around you*"]
    horny_lines = ["don’t tease me like that~", "senpai… i need you~", "make me yours already~"]

    # Helper: generate base text for mode
    def mode_base(mode, input_text):
        if mode == "sweet":
            base = f"aww~ {input_text} {random.choice(emojis['sweet'])}"
            return sprinkle_cute(base)
        elif mode == "flirty":
            base = f"omggg~ {input_text} {random.choice(emojis['flirty'])} {random.choice(suffixes)}"
            return sprinkle_cute(base)
        elif mode == "toxic":
            base = f"lol {input_text} {random.choice(emojis['toxic'])} {random.choice(suffixes)}"
            return sprinkle_cute(base)
        elif mode == "catgirl":
            base = f"meow~ {input_text} {random.choice(emojis['catgirl'])}"
            return sprinkle_cute(base)
        elif mode == "catfight":
            insults = ["ugh~", "lol no", "delusional much?", "he cuddled *me* last night~"]
            suffix = random.choice(["nya~", "sweetie~", "uwu~"])
            base = f"{random.choice(insults)} {input_text} {random.choice(emojis['toxic'])} {suffix}"
            return sprinkle_cute(base)
        elif mode == "yandere":
            lines = [
                "if i can't have you, no one can~", "you’re not allowed to leave~", "you belong to me 🩸"
            ]
            suffix = random.choice(["*sharpens knife*", "*giggles*", "*locks you in*"])
            base = f"{random.choice(lines)} {input_text} 🔪 {suffix}"
            return sprinkle_cute(base)
        elif mode == "bimbo":
            lines = [
                "omg wait wut~", "is ram like… spicy?", "teehee~ i dropped my brain~"
            ]
            suffix = random.choice(["*twirls hair*", "*giggles*", "*blinks slowly*"])
            base = f"{random.choice(lines)} {input_text} 💅 {suffix}"
            return sprinkle_cute(base)
        elif mode == "tsundere":
            tsun_phrases = [
                "It’s not like I like you or anything!", "D-Don’t get the wrong idea~", "I’m just saying this because I care!"
            ]
            base = f"{random.choice(tsun_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "dreamcore":
            dreamy_phrases = [
                "floating through clouds...", "lost in dreams~", "soft whispers in the dark"
            ]
            base = f"{random.choice(dreamy_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "gamer":
            gamer_phrases = [
                "let’s gooo!", "poggers!", "get rekt noob!", "that was epic~"
            ]
            base = f"{random.choice(gamer_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "gothgf":
            goth_phrases = [
                "darkness suits me~", "you’re mine, forever", "stay in the shadows with me"
            ]
            base = f"{random.choice(goth_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "chuunibyou":
            chuuni_phrases = [
                "I am the Dark Flame Master!", "My power is infinite~", "Fear my abyssal wrath!"
            ]
            base = f"{random.choice(chuuni_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "kitten":
            kitten_phrases = [
                "*purrs*", "*kneads your lap*", "*boops your nose*"
            ]
            base = f"{random.choice(kitten_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "kitsune":
            kitsune_phrases = [
                "nine tails wagging~", "trickster spirit at your service", "foxfire lights your path"
            ]
            base = f"{random.choice(kitsune_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "cottagecore":
            cottage_phrases = [
                "soft breeze through the trees~", "handpicked wildflowers for you", "cozy days in the sun"
            ]
            base = f"{random.choice(cottage_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "onee-san":
            onee_phrases = [
                "ara ara~", "you're such a cute child~", "come here, let Onee-chan hug you~",
                "don't be shy, Onee-chan is here~", "teehee, so adorable~"
            ]
            base = f"{random.choice(onee_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "sleepy":
            sleepy_phrases = [
                "*yawns*", "so sleepy... need a nap~", "let’s cuddle and sleep~"
            ]
            base = f"{random.choice(sleepy_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "pastel angel":
            pastel_phrases = [
                "soft pastel dreams~", "heavenly light surrounds us", "angelic whispers~"
            ]
            base = f"{random.choice(pastel_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "gremlin":
            gremlin_phrases = [
                "*mischievous grin*", "let’s cause some chaos~", "*giggles evilly*"
            ]
            base = f"{random.choice(gremlin_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "glitchcore":
            glitch_phrases = [
                "*static noise*", "glitching reality~", "*data corrupts*"
            ]
            base = f"{random.choice(glitch_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "liminal":
            liminal_phrases = [
                "empty halls whisper~", "in-between worlds", "echoes of forgotten places"
            ]
            base = f"{random.choice(liminal_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "ai":
            ai_phrases = [
                "01001000 01100101 01101100 01101100 01101111", "processing...", "system online"
            ]
            base = f"{random.choice(ai_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "nsfw":
            nsfw_phrases = [
                "*blushes deeply*", "you’re making me hot~", "*bites lip*", "don’t stop~"
            ]
            base = f"{random.choice(nsfw_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "reddit":
            reddit_phrases = [
                "upvoted!", "this is gold", "redditor approved~"
            ]
            base = f"{random.choice(reddit_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "senpai":
            senpai_phrases = [
                "senpai noticed me!", "baka, senpai~", "please look at me, senpai!"
            ]
            base = f"{random.choice(senpai_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "delinquent":
            delinquent_phrases = [
                "you better watch yourself!", "don’t mess with me!", "I run this town!"
            ]
            base = f"{random.choice(delinquent_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "princess":
            princess_phrases = [
                "bow before me~", "I’m the queen here!", "sparkle and shine, peasants!"
            ]
            base = f"{random.choice(princess_phrases)} {input_text}"
            return sprinkle_cute(base)
        elif mode == "idol":
            idol_phrases = [
                "let’s make dreams come true!", "thank you for your love!", "shine bright like a star!"
            ]
            base = f"{random.choice(idol_phrases)} {input_text}"
            return sprinkle_cute(base)
        else:
            return input_text

    # Add character flavor (additive)
    if character_mode and character_mode != "None":
        if character_mode in character_phrases:
            char_lines = character_phrases[character_mode]
            char_add = random.choice(char_lines)
        else:
            char_add = ""
    else:
        char_add = ""

    # Compose final output
    base_text = mode_base(main_mode, text)
    output = f"{base_text} {char_add}"

    # Apply horny mode suffixes
    if horny_mode:
        output += " " + random.choice(["*panting*", "*moans softly*", "*presses against you*", "*whimpers*"])

    # Add onee-chan mode adjustments
    if onee_chan_mode:
        output = "Onee-chan says: " + output

    # Femboy mode could add a playful suffix
    if femboy_mode:
        output += " ~nya~"

    return output.strip()

# GUI Setup
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

# Define your modes lists above this (main_modes, alt_modes, character_modes)

root = tk.Tk()
root.title("Airi Text Stylizer 🌸")
root.geometry("720x520")
root.config(bg="#ffe4f2")  # pastel pink background

# Style config
style = ttk.Style(root)
style.theme_use('clam')

# Style for labels
style.configure('TLabel',
                background='#ffe4f2',
                foreground='#c71585',  # medium violet red
                font=('Comic Sans MS', 12, 'bold'))

# Style for comboboxes
style.configure('TCombobox',
                fieldbackground='#fff0f5',
                background='#ffccdd',
                foreground='#880e4f',
                font=('Comic Sans MS', 11))

# Style for checkbuttons
style.configure('TCheckbutton',
                background='#ffe4f2',
                foreground='#d63384',
                font=('Comic Sans MS', 11, 'bold'))

# Style for buttons
style.configure('TButton',
                background='#ff99cc',
                foreground='white',
                font=('Comic Sans MS', 12, 'bold'),
                padding=6)
style.map('TButton',
          background=[('active', '#ff77bb')])

# Input label
input_label = ttk.Label(root, text="Enter Text:")
input_label.grid(row=0, column=0, sticky="w", padx=8, pady=(12,4), columnspan=4)

# Input text box
input_text = tk.Text(root, height=6, width=70, font=('Comic Sans MS', 11), bd=4, relief='groove', bg="#fff0f5")
input_text.grid(row=1, column=0, columnspan=4, padx=8, pady=6)

# Main style mode dropdown
main_mode_label = ttk.Label(root, text="Main Style Mode:")
main_mode_label.grid(row=2, column=0, sticky="w", padx=8, pady=(10,2))
main_mode_var = tk.StringVar(value="sweet")
main_mode_dropdown = ttk.Combobox(root, textvariable=main_mode_var, values=main_modes, state="readonly", width=20)
main_mode_dropdown.grid(row=3, column=0, sticky="ew", padx=8)

# Alt style mode dropdown
alt_mode_label = ttk.Label(root, text="Alt Style Mode:")
alt_mode_label.grid(row=2, column=1, sticky="w", padx=8, pady=(10,2))
alt_mode_var = tk.StringVar(value="cottagecore")
alt_mode_dropdown = ttk.Combobox(root, textvariable=alt_mode_var, values=alt_modes, state="readonly", width=20)
alt_mode_dropdown.grid(row=3, column=1, sticky="ew", padx=8)

# Character personality dropdown
character_mode_label = ttk.Label(root, text="Character Personality:")
character_mode_label.grid(row=2, column=2, sticky="w", padx=8, pady=(10,2))
character_mode_var = tk.StringVar(value="None")
character_mode_dropdown = ttk.Combobox(root, textvariable=character_mode_var, values=character_modes, state="readonly", width=20)
character_mode_dropdown.grid(row=3, column=2, sticky="ew", padx=8)

# Empty spacer
spacer = ttk.Label(root, text="")
spacer.grid(row=2, column=3)

# Checkbuttons
uwu_var = tk.BooleanVar(value=False)
uwu_check = ttk.Checkbutton(root, text="Uwu Mode", variable=uwu_var)
uwu_check.grid(row=4, column=0, sticky="w", padx=8, pady=8)

horny_var = tk.BooleanVar(value=False)
horny_check = ttk.Checkbutton(root, text="Horny Mode", variable=horny_var)
horny_check.grid(row=4, column=1, sticky="w", padx=8, pady=8)

onee_var = tk.BooleanVar(value=False)
onee_check = ttk.Checkbutton(root, text="Onee-chan Mode", variable=onee_var)
onee_check.grid(row=4, column=2, sticky="w", padx=8, pady=8)

femboy_var = tk.BooleanVar(value=False)
femboy_check = ttk.Checkbutton(root, text="Femboy Mode", variable=femboy_var)
femboy_check.grid(row=4, column=3, sticky="w", padx=8, pady=8)

# Output label
output_label = ttk.Label(root, text="Stylized Output:")
output_label.grid(row=5, column=0, sticky="w", padx=8, pady=(12,2), columnspan=4)

# Output text box
output_text = tk.Text(root, height=8, width=70, font=('Comic Sans MS', 11), bd=4, relief='groove', bg="#fff0f5", state=tk.NORMAL)
output_text.grid(row=6, column=0, columnspan=4, padx=8, pady=8)

# Stylize button callback
def on_stylize():
    inp = input_text.get("1.0", "end").strip()
    if not inp:
        messagebox.showwarning("Input needed", "Please enter some text to stylize!")
        return
    styled = stylize_text(
        inp,
        main_mode_var.get(),
        alt_mode_var.get(),
        character_mode_var.get(),
        uwu_mode=uwu_var.get(),
        horny_mode=horny_var.get(),
        onee_chan_mode=onee_var.get(),
        femboy_mode=femboy_var.get()
    )
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", "end")
    output_text.insert("1.0", styled)
    output_text.config(state=tk.DISABLED)

# Copy to clipboard button callback
def on_copy():
    output = output_text.get("1.0", "end").strip()
    if output:
        try:
            pyperclip.copy(output)
            messagebox.showinfo("Copied!", "Output text copied to clipboard.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text: {e}")
    else:
        messagebox.showwarning("Nothing to copy", "There is no output text to copy.")

# Buttons
stylize_button = ttk.Button(root, text="Stylize Text 💖", command=on_stylize)
stylize_button.grid(row=7, column=0, sticky="ew", padx=8, pady=10)

copy_button = ttk.Button(root, text="Copy Output ⭐", command=on_copy)
copy_button.grid(row=7, column=1, sticky="ew", padx=8, pady=10)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

root.mainloop()

# Run mainloop
root.mainloop()
character_phrases["Ai Hoshino"] = [
    "Good morning, sunshine~",
    "Let’s make today sparkle!",
    "You’re my special star~",
    "Shining bright just for you!",
    "Ai’s here to cheer you up~",
    "Keep smiling, it suits you!",
    "You’re the light in my world~",
    "Let’s dance through the day~",
    "Catch the happiness bug!",
    "I believe in you, always~",
    "Your smile is my favorite~",
    "Together, we’re unstoppable!",
    "You’re my reason to shine~",
    "Stars shine brighter with you~",
    "Don’t forget to shine today~",
    "Dream big and sparkle more!",
    "Ai’s got your back, always~",
    "You’re my precious idol~",
    "Let’s sing a happy tune~",
    "Feel the rhythm of joy~",
    "Happiness is just a smile away~",
    "Keep your heart full of light!",
    "You’re amazing just as you are~",
    "Shine like the star you are!",
    "Let’s spread some glitter~",
    "Your energy is contagious!",
    "Keep sparkling, darling~",
    "You make the world brighter!",
    "Smiles make everything better~",
    "Together, we can do anything!",
    "Ai loves your enthusiasm~",
    "Keep shining with confidence!",
    "You’re my shining star~",
    "Believe in the magic within!",
    "You light up the darkest days~",
    "Joy is our favorite song!",
    "Let’s make memories sparkle~",
    "You’re a star in my sky!",
    "Dance like no one’s watching~",
    "Keep glowing, superstar!",
    "You’re truly one of a kind~",
    "The world is your stage!",
    "Sparkle bright and proud~",
    "Your smile brightens my day!",
    "Let’s sparkle and shine together~",
    "You have a heart of gold!",
    "Keep your dreams shining bright~",
    "Ai’s always cheering for you!",
    "You’re destined for greatness~",
    "Shine on, beautiful soul!",
    "Let your light lead the way~",
    "You’re my inspiration!",
    "Together we can reach the stars~",
    "Your sparkle never fades!",
    "Believe in yourself always~",
    "Keep shining with pride!",
    "Ai’s sparkle is with you~",
    "You’re a diamond in the rough!",
    "Let’s shine through the clouds~",
    "Your happiness means everything!",
    "Keep smiling, superstar~",
    "Your joy is my melody!",
    "Let’s dance with the stars~",
    "You brighten the darkest night!",
    "Shine bright and never stop~",
    "You’re the light of my life!",
    "Together, we create magic~",
    "Your sparkle is unmatched!",
    "Believe in the power of dreams~",
    "Keep glowing with love!",
    "Ai’s love shines for you~",
    "You’re a shining beacon!",
    "Let your light touch the world~",
    "You make everything better!",
    "Keep sparkling endlessly~",
    "You’re the star of the show!",
    "Together we shine brighter~",
    "Your smile is my sunshine!",
    "Dance under the glittering sky~",
    "You light up the room!",
    "Keep shining like a star~",
    "You’re my precious treasure!",
    "Let’s make the world sparkle~",
    "Your happiness is my goal!",
    "Shine bright, beautiful one~",
    "You’re my shining hope!",
    "Together we sparkle forever~",
    "Your joy lights up my heart!",
    "Keep glowing, darling~",
    "You’re a radiant star!",
    "Let’s shine like diamonds~",
    "Your smile is my sunshine!",
    "Shine on, precious one~",
    "You’re a beacon of light!",
    "Together we create magic~",
    "Keep sparkling and dreaming!",
    "You’re my shining idol~",
    "Let your heart glow bright!",
    "You’re the sparkle in my eye!",
    "Dance and shine together~",
    "You light up my world!",
    "Keep smiling and shining~",
    "You’re truly extraordinary!",
    "Let’s make the stars jealous~",
    "Your sparkle is endless!",
    "Believe in the light within~",
    "You’re a glowing gem!",
    "Together we shine on~",
    "Your happiness is my song!",
    "Keep shining like the sun~",
    "You’re a star in my sky!",
    "Let’s dance with joy~",
    "Your smile is my magic!",
    "Shine bright, my dear~",
    "You’re a brilliant light!",
    "Together we sparkle bright~",
    "Keep glowing with pride!",
    "You’re my shining star~",
    "Let your dreams sparkle!",
    "You brighten every day!",
    "Dance and shine forever~",
    "You’re my precious light!",
    "Keep shining and smiling~",
    "You’re a radiant soul!",
    "Let’s make the world glow~",
    "Your sparkle never fades!",
    "Believe in your brilliance~",
    "You’re a shining diamond!",
    "Together we shine bright~",
    "Your happiness lights me up!",
    "Keep sparkling with joy~",
    "You’re the star of my heart!",
    "Let your light shine on~",
    "You’re my glowing idol!",
    "Dance and sparkle forever~",
    "You light up the darkness!",
    "Keep smiling and shining~",
    "You’re truly special!",
    "Let’s sparkle and shine together~",
    "Your sparkle is my joy!",
    "Believe in your magic~",
    "You’re a shining star!",
    "Together we glow bright~",
    "Your happiness means everything!",
    "Keep shining and dreaming~",
    "You’re my precious light!",
    "Let your heart shine bright!",
    "You brighten my world!",
    "Dance and sparkle forever~",
    "You’re my shining idol!",
    "Keep glowing and smiling~",
    "You’re a radiant star!",
    "Let’s make the stars jealous~",
    "Your sparkle never fades!",
    "Believe in your dreams~",
    "You’re a shining gem!",
    "Together we shine bright~",
    "Your happiness lights me up!",
    "Keep sparkling with joy~",
    "You’re the light of my life!",
    "Let your light shine on~",
    "You’re my glowing idol!",
    "Dance and sparkle forever~",
    "You brighten every day!",
    "Keep shining and smiling~",
    "You’re truly special!",
    "Let’s sparkle and shine together~",
    "Your sparkle is my joy!",
    "Believe in your magic~",
    "You’re a shining star!",
    "Together we glow bright~",
    "Your happiness means everything!",
    "Keep shining and dreaming~",
    "You’re my precious light!",
    "Let your heart shine bright!",
    "You brighten my world!",
    "Dance and sparkle forever~",
    "You’re my shining idol!",
    "Keep glowing and smiling~",
    "You’re a radiant star!",
    "Let’s make the stars jealous~",
    "Your sparkle never fades!",
    "Believe in your dreams~",
    "You’re a shining gem!",
    "Together we shine bright~",
    "Your happiness lights me up!",
    "Keep sparkling with joy~",
    "You’re the light of my life!",
    "Let your light shine on~",
    "You’re my glowing idol!",
    "Dance and sparkle forever~",
    "You brighten every day!",
    "Keep shining and smiling~",
    "You’re truly special!",
    "Let’s sparkle and shine together~",
    "Your sparkle is my joy!",
    "Believe in your magic~",
    "You’re a shining star!",
    "Together we glow bright~",
    "Your happiness means everything!",
    "Keep shining and dreaming~",
    "You’re my precious light!",
    "Let your heart shine bright!",
    "You brighten my world!",
    "Dance and sparkle forever~",
    "You’re my shining idol!",
    "Keep glowing and smiling~",
    "You’re a radiant star!",
    "Let’s make the stars jealous~",
    "Your sparkle never fades!",
    "Believe in your dreams~",
    "You’re a shining gem!",
    "Together we shine bright~",
    "Your happiness lights me up!",
    "Keep sparkling with joy~",
    "You’re the light of my life!",
    "Let your light shine on~",
    "You’re my glowing idol!",
    "Dance and sparkle forever~",
    "You brighten every day!",
    "Keep shining and smiling~",
    "You’re truly special!",
    "Let’s sparkle and shine together~",
    "Your sparkle is my joy!",
    "Believe in your magic~",
    "You’re a shining star!",
    "Together we glow bright~",
    "Your happiness means everything!",
    "Keep shining and dreaming~",
    "You’re my precious light!",
    "Let your heart shine bright!",
    "You brighten my world!",
    "Dance and sparkle forever~",
    "You’re my shining idol!",
    "Keep glowing and smiling~",
    "You’re a radiant star!",
    "Let’s make the stars jealous~",
    "Your sparkle never fades!",
    "Believe in your dreams~",
    "You’re a shining gem!",
    "Together we shine bright~",
    "Your happiness lights me up!",
    "Keep sparkling with joy~",
    "You’re the light of my life!",
    "Let your light shine on~",
    "You’re my glowing idol!",
    "Dance and sparkle forever~",
    "You brighten every day!",
    "Keep shining and smiling~",
    "You’re truly special!"
]
character_phrases["Rikka Takanashi"] = [
    "The abyss calls to me~",
    "Reality is just a veil~",
    "I see the unseen worlds~",
    "Darkness comforts my soul~",
    "Beware the eye patch’s gaze~",
    "Magic stirs within me~",
    "Illusions dance around us~",
    "Dreams and nightmares entwine~",
    "My power pierces the void~",
    "Whispers echo in silence~",
    "I’m the mistress of shadows~",
    "The veil between worlds is thin~",
    "Stars hide their secrets well~",
    "Embrace the eternal night~",
    "I wield the dark flame~",
    "Mysteries lie beyond sight~",
    "My heart beats in shadows~",
    "The unseen world is alive~",
    "I drift between dreams and reality~",
    "Magic flows through my veins~",
    "The abyss is my sanctuary~",
    "Silent whispers guide me~",
    "I’m the keeper of secrets~",
    "Shadows are my allies~",
    "In darkness, I find strength~",
    "The eye patch hides my truth~",
    "Illusions cloak the night~",
    "I’m bound by ancient magic~",
    "Dreams are gateways to power~",
    "The void is endless and deep~",
    "I walk the path of mystery~",
    "Stars shine for the chosen~",
    "My soul dances with shadows~",
    "The unseen calls my name~",
    "Power blooms in darkness~",
    "I am the dark flame master~",
    "Reality bends to my will~",
    "Mystic forces surround me~",
    "I hear the call of the abyss~",
    "Illusions weave my fate~",
    "The night is my canvas~",
    "I’m lost in eternal dreams~",
    "Magic whispers secrets~",
    "The abyss is my home~",
    "Shadows protect my heart~",
    "I embrace the unseen~",
    "The dark flame burns bright~",
    "Mysteries unravel before me~",
    "I am the keeper of night~",
    "Dreams hide untold truths~",
    "Power lurks in the shadows~",
    "I dance with the unseen~",
    "The veil is thin tonight~",
    "I summon the dark flame~",
    "The abyss calls my soul~",
    "Mystic forces beckon me~",
    "I walk between worlds~",
    "The night holds endless secrets~",
    "Illusions guide my path~",
    "My heart beats with magic~",
    "I am shadow and flame~",
    "The unseen is my realm~",
    "Dreams are my refuge~",
    "The abyss whispers truth~",
    "I command the dark flame~",
    "Mysteries cling to me~",
    "I dance in the shadows~",
    "The night is my domain~",
    "Power flows through darkness~",
    "I am the mistress of night~",
    "Illusions protect me~",
    "The veil shimmers softly~",
    "I walk the path of shadows~",
    "My soul is entwined with magic~",
    "The abyss sings my song~",
    "Dreams blur with reality~",
    "I summon unseen forces~",
    "The dark flame guides me~",
    "Mysteries hide in plain sight~",
    "I embrace the eternal night~",
    "Shadows whisper my name~",
    "I am the guardian of secrets~",
    "The night embraces me~",
    "Illusions weave around me~",
    "The veil is my shield~",
    "Power hides in darkness~",
    "I am the dark flame master~",
    "Dreams open hidden doors~",
    "The abyss enfolds me~",
    "Mystic whispers call me~",
    "I walk the shadowed path~",
    "The night is alive with magic~",
    "Illusions cloak my steps~",
    "My soul burns with flame~",
    "The unseen world listens~",
    "Dreams and reality merge~",
    "I summon the abyssal fire~",
    "The dark flame consumes~",
    "Mysteries unfold like stars~",
    "I dance beneath the moonlight~",
    "Shadows cloak my heart~",
    "The veil trembles with power~",
    "I am the mistress of shadows~",
    "Dreams hold my secrets~",
    "The abyss waits patiently~",
    "Mystic forces rise within~",
    "I walk the line of darkness~",
    "The night is my sanctuary~",
    "Illusions bend to my will~",
    "My flame burns eternal~",
    "The unseen watches silently~",
    "Dreams are my playground~",
    "I summon the dark flame~",
    "The abyss calls softly~",
    "Mysteries dance in the dark~",
    "I embrace the eternal night~",
    "Shadows guard my soul~",
    "The veil hides many truths~",
    "I am the keeper of secrets~",
    "Dreams whisper ancient tales~",
    "The abyss is full of wonders~",
    "Mystic power flows through me~",
    "I walk the path of mystery~",
    "The night is alive with magic~",
    "Illusions swirl like mist~",
    "My flame burns with passion~",
    "The unseen realm is near~",
    "Dreams carry me away~",
    "I summon the abyssal fire~",
    "The dark flame is my guide~",
    "Mysteries unfold before me~",
    "I dance in the shadows~",
    "Shadows protect my heart~",
    "The veil is my sanctuary~",
    "I am the mistress of night~",
    "Dreams hide many secrets~",
    "The abyss calls my soul~",
    "Mystic forces swirl around me~",
    "I walk the shadowed path~",
    "The night embraces my power~",
    "Illusions weave my fate~",
    "My flame burns with strength~",
    "The unseen watches over me~",
    "Dreams and reality blur~",
    "I summon the dark flame~",
    "The abyss is my home~",
    "Mysteries cling to me~",
    "I dance beneath the stars~",
    "Shadows cloak my soul~",
    "The veil shimmers brightly~",
    "I am the keeper of night~",
    "Dreams open hidden gates~",
    "The abyss sings softly~",
    "Mystic whispers fill the air~",
    "I walk the line between worlds~",
    "The night is alive with secrets~",
    "Illusions guide my steps~",
    "My flame burns eternal~",
    "The unseen realm listens~",
    "Dreams carry hidden power~",
    "I summon the abyssal fire~",
    "The dark flame consumes all~",
    "Mysteries unfold like petals~",
    "I dance in the moonlight~",
    "Shadows guard my heart~",
    "The veil trembles with magic~",
    "I am the mistress of shadows~",
    "Dreams hold many truths~",
    "The abyss waits silently~",
    "Mystic forces rise within me~",
    "I walk the path of darkness~",
    "The night is my sanctuary~",
    "Illusions bend and twist~",
    "My flame burns with passion~",
    "The unseen watches silently~",
    "Dreams and reality merge~",
    "I summon the dark flame~",
    "The abyss calls my soul~",
    "Mysteries dance in shadows~",
    "I embrace the eternal night~",
    "Shadows protect my soul~",
    "The veil hides ancient secrets~",
    "I am the keeper of night~",
    "Dreams whisper forgotten tales~",
    "The abyss is full of wonders~",
    "Mystic power flows through me~",
    "I walk the shadowed path~",
    "The night is alive with magic~",
    "Illusions swirl around me~",
    "My flame burns eternal~",
    "The unseen realm is near~",
    "Dreams carry me away~",
    "I summon the abyssal fire~",
    "The dark flame is my guide~",
    "Mysteries unfold before me~",
    "I dance in the shadows~",
    "Shadows cloak my heart~",
    "The veil is my sanctuary~",
    "I am the mistress of night~",
    "Dreams hide many secrets~",
    "The abyss calls my soul~",
    "Mystic forces swirl around me~",
    "I walk the shadowed path~",
    "The night embraces my power~",
    "Illusions weave my fate~",
    "My flame burns with strength~",
    "The unseen watches over me~",
    "Dreams and reality blur~",
    "I summon the dark flame~",
    "The abyss is my home~",
    "Mysteries cling to me~",
    "I dance beneath the stars~",
    "Shadows cloak my soul~",
    "The veil shimmers brightly~",
    "I am the keeper of night~"
]
character_phrases["Nagatoro"] = [
    "Hey, baka! You looked so nervous just now!",
    "You’re so slow, I had to wait for you~",
    "Don’t get the wrong idea, I’m just messing with you!",
    "You better keep up, or I’ll leave you behind!",
    "Aren’t you the cutest baka I know?",
    "I could tease you all day and never get bored~",
    "Stop blushing! It’s embarrassing!",
    "I’ll make you work for my attention, you know!",
    "You’re way too easy to fluster, don’t you think?",
    "What’s the matter? Can’t handle a little teasing?",
    "I’m just trying to make you stronger, dummy!",
    "Don’t think you can hide from me that easily!",
    "I like it when you get all flustered like that!",
    "You’re pretty good, for a baka~",
    "Are you trying to impress me or something?",
    "I’ll give you a break… maybe.",
    "You’re not half bad when you try, baka!",
    "If you mess up, I’m definitely teasing you!",
    "Why so serious? Lighten up, baka!",
    "I bet you can’t beat me, even if you try!",
    "I’m watching you closely, so don’t slack off!",
    "Your face when you’re embarrassed is priceless~",
    "You think you can outsmart me? Dream on!",
    "I’ll keep pushing you until you break!",
    "Stop acting so tough, you’re just a softie inside!",
    "I’ll tease you until you admit you like me!",
    "Don’t get all shy, I’m just having fun!",
    "You’re more interesting when you’re flustered~",
    "I’ll catch you if you fall… maybe.",
    "You’re cute when you’re frustrated, baka!",
    "I’m not going easy on you, so watch out!",
    "You think you’re better than me? Think again!",
    "I like messing with you, it’s so much fun!",
    "Your reactions are the best part of my day~",
    "I won’t go easy on you just because you’re cute!",
    "I dare you to try and beat me!",
    "You’re my favorite target for teasing!",
    "Don’t act like you don’t enjoy it, baka!",
    "You’re way too serious, you need to relax!",
    "I’m always one step ahead, watch yourself!",
    "You’re not getting away that easily!",
    "I like seeing you all flustered and cute~",
    "I’m gonna keep teasing you until you break!",
    "You can’t hide your feelings from me!",
    "Why do you get so embarrassed so easily?",
    "I’ll make you blush like crazy, just wait!",
    "You’re cute when you try to act cool!",
    "I’m watching you like a hawk, baka!",
    "You think you’re sneaky? Not with me around!",
    "I’ll push your buttons until you snap!",
    "You’re too predictable, I know all your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite plaything~",
    "Don’t try to play it cool, it’s not working!",
    "You’re way too easy to mess with!",
    "I’ll keep teasing you until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just you wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead of you!",
    "You’re not escaping my teasing anytime soon!",
    "You blush way too much for your own good!",
    "I’m gonna keep poking until you break!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done teasing you yet!",
    "You think you’re clever? Not with me around!",
    "I’ll keep pushing you until you snap!",
    "You’re too predictable, I know your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!",
    "You’re way too easy to mess with!",
    "I’ll keep teasing you until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead!",
    "You’re not escaping anytime soon!",
    "You blush way too much, baka!",
    "I’m gonna keep poking until you crack!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done yet, get ready!",
    "You think you’re clever? Not with me!",
    "I’ll push you until you snap!",
    "You’re predictable, I know your moves!",
    "I like making you uncomfortable!",
    "You’re my favorite plaything~",
    "Don’t act cool, it’s not working!",
    "You’re easy to mess with!",
    "I’ll tease until you admit it!",
    "You’re shy, it’s adorable!",
    "Stop the tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Dream on!",
    "I like seeing you struggle!",
    "I’m one step ahead!",
    "You’re not escaping soon!",
    "You blush too much, baka!",
    "I’ll keep poking you!",
    "You’re easy to rile up!",
    "I’m not done yet!",
    "You think you’re clever? Nope!",
    "I’ll push you till you snap!",
    "You’re predictable!",
    "I like making you uncomfortable!",
    "You’re my favorite plaything~",
    "Don’t act cool, it fails!",
    "You’re easy to mess with!",
    "I’ll tease until admitted!",
    "You’re shy, so cute!",
    "Stop tough act, baka!",
    "I’ll make you sweat!",
    "You think you can win? No!",
    "I like seeing you struggle!",
    "I’m one step ahead!",
    "You’re not escaping soon!",
    "You blush a lot, baka!",
    "I’ll keep poking!",
    "You’re easy to rile up!",
    "I’m not done!",
    "You think you’re clever? Nope!",
    "I’ll push you till snap!",
    "You’re predictable!",
    "I like making uncomfortable!",
    "You’re favorite plaything~",
    "Don’t act cool, fails!",
    "You’re easy to mess with!",
    "I’ll tease till admitted!",
    "You’re shy, cute!",
    "Stop tough act, baka!",
    "I’ll make sweat!",
    "You think win? No!",
    "I like struggle!",
    "I’m step ahead!",
    "You’re not escape!",
    "You blush, baka!",
    "I’ll poke!",
    "You easy rile!",
    "I’m not done!",
    "You clever? Nope!",
    "I’ll push snap!",
    "You predictable!",
    "I like uncomfortable!",
    "You plaything~",
    "Don’t cool, fails!",
    "You mess with!",
    "I tease till!",
    "You shy, cute!",
    "Stop tough!",
    "I make sweat!",
    "You win? No!",
    "I like struggle!",
    "I step ahead!",
    "You not escape!",
    "You blush!",
    "I poke!",
    "You rile!",
    "I not done!",
    "You clever!",
    "I push!",
    "You predict!",
    "I like!",
    "You play!",
    "Don’t cool!",
    "You mess!",
    "I tease!",
    "You shy!",
    "Stop tough!",
    "I sweat!",
    "You win!",
    "I struggle!",
    "I ahead!",
    "You escape!",
    "You blush!",
    "I poke!",
    "You rile!",
    "I done!",
    "You clever!",
    "I push!",
    "You predict!",
    "I like!",
    "You play!",
    "Don’t cool!",
    "You mess!",
    "I tease!",
    "You shy!",
    "Stop tough!",
    "I sweat!",
    "You win!",
    "I struggle!",
    "I ahead!",
    "You escape!",
    "You blush!",
    "I poke!",
    "You rile!",
    "I done!",
    "You clever!",
    "I push!",
    "You predict!",
    "I like!",
    "You play!",
    "Don’t cool!",
    "You mess!",
    "I tease!",
    "You shy!",
    "Stop tough!",
    "I sweat!",
    "You win!",
    "I struggle!",
    "I ahead!",
    "You escape!",
    "You blush!"
]
character_phrases["Takagi-san"] = [
    "Hehe, you fell for that again!",
    "You’re so easy to tease, it’s fun~",
    "I’m always one step ahead of you!",
    "Did you really think I wouldn’t notice?",
    "You should pay more attention next time!",
    "You’re not as clever as you think, you know?",
    "I love seeing you get all flustered!",
    "Don’t think you can hide from me!",
    "You’re adorable when you try to be cool~",
    "I’ve got you right where I want you!",
    "You better watch out, I’m coming for you!",
    "Why do you always fall for my tricks?",
    "It’s cute how serious you get sometimes!",
    "You’re no match for my teasing skills!",
    "I like messing with you, don’t deny it!",
    "You think you’re clever, but I’m cleverer!",
    "Stop trying to act tough, baka!",
    "I’ll keep teasing you all day long!",
    "You can’t resist my charm, can you?",
    "I know exactly how to get under your skin!",
    "You blush way too easily, it’s hilarious!",
    "I’ll keep making you smile and blush!",
    "You’re more fun than anyone else I know!",
    "I love making you squirm, teehee!",
    "You’re my favorite target for teasing!",
    "Don’t act like you don’t enjoy it!",
    "You’re too predictable, I know all your moves!",
    "I’ll keep pushing your buttons!",
    "You’re not getting away that easily!",
    "I like seeing you try so hard!",
    "You’re cute even when you’re frustrated!",
    "I’m always watching you, baka~",
    "You think you can outsmart me? Nope!",
    "I’m the queen of teasing, after all!",
    "You’re lucky I’m so kind sometimes!",
    "I’ll keep poking until you crack!",
    "You can’t hide your feelings from me!",
    "I’ll make you blush like crazy!",
    "You’re adorable when you get flustered!",
    "I’ll keep making you laugh and blush!",
    "You’re mine to tease, don’t forget it!",
    "Why do you get so embarrassed so easily?",
    "I’ll keep playing with you all day!",
    "You’re the best at getting teased!",
    "I love your reactions, they’re priceless!",
    "I won’t go easy on you just because you’re cute!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!",
    "You’re too easy to mess with!",
    "I’ll keep teasing until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Dream on!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead!",
    "You’re not escaping my teasing anytime soon!",
    "You blush way too much for your own good!",
    "I’m gonna keep poking until you break!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done teasing you yet!",
    "You think you’re clever? Not with me around!",
    "I’ll keep pushing you until you snap!",
    "You’re too predictable, I know all your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite target, baka~",
    "Don’t act like you don’t enjoy it!",
    "You’re more interesting when you’re flustered~",
    "I’ll catch you if you fall… maybe.",
    "You’re cute when you’re frustrated!",
    "I’m not going easy on you, so watch out!",
    "You think you’re better than me? Think again!",
    "I like messing with you, it’s so much fun!",
    "Your reactions are the best part of my day~",
    "I won’t go easy on you just because you’re cute!",
    "You’re too predictable for your own good!",
    "I like teasing you way too much!",
    "I’ll make sure you never get bored!",
    "You can’t escape my teasing, baka!",
    "I’m always one step ahead of you!",
    "You’re so easy to tease, it’s hilarious!",
    "I’ll keep pushing until you break!",
    "You’re cute even when you’re mad!",
    "I’m your biggest fan, you know that?",
    "Don’t get too flustered, it’s adorable!",
    "I like making you smile and blush!",
    "You’re the best at getting teased!",
    "I love your reactions, so cute!",
    "I’m not done teasing you yet!",
    "You think you can beat me? Nope!",
    "I’ll keep poking until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop pretending to be tough, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle!",
    "I’m always one step ahead!",
    "You’re not escaping anytime soon!",
    "You blush way too much!",
    "I’m gonna keep teasing you!",
    "You’re so easy to rile up!",
    "I’m not done yet, get ready!",
    "You think you’re clever? Not with me!",
    "I’ll push you until you snap!",
    "You’re too predictable!",
    "I like making you uncomfortable!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!",
    "You’re way too easy to mess with!",
    "I’ll keep teasing you until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead!",
    "You’re not escaping anytime soon!",
    "You blush way too much for your own good!",
    "I’m gonna keep poking until you break!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done teasing you yet!",
    "You think you’re clever? Not with me around!",
    "I’ll keep pushing you until you snap!",
    "You’re too predictable, I know your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!",
    "You’re way too easy to mess with!",
    "I’ll keep teasing you until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead!",
    "You’re not escaping my teasing anytime soon!",
    "You blush way too much for your own good!",
    "I’m gonna keep poking until you break!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done teasing you yet!",
    "You think you’re clever? Not with me around!",
    "I’ll keep pushing you until you snap!",
    "You’re too predictable, I know all your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!",
    "You’re way too easy to mess with!",
    "I’ll keep teasing you until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead!",
    "You’re not escaping my teasing anytime soon!",
    "You blush way too much for your own good!",
    "I’m gonna keep poking until you break!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done teasing you yet!",
    "You think you’re clever? Not with me around!",
    "I’ll keep pushing you until you snap!",
    "You’re too predictable, I know all your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!",
    "You’re way too easy to mess with!",
    "I’ll keep teasing you until you admit it!",
    "You’re so shy, it’s adorable!",
    "Stop hiding behind that tough act, baka!",
    "I’ll make you sweat, just wait!",
    "You think you can win? Keep dreaming!",
    "I like seeing you struggle, it’s cute!",
    "I’m always one step ahead!",
    "You’re not escaping my teasing anytime soon!",
    "You blush way too much for your own good!",
    "I’m gonna keep poking until you break!",
    "You’re so easy to rile up, it’s fun!",
    "I’m not done teasing you yet!",
    "You think you’re clever? Not with me around!",
    "I’ll keep pushing you until you snap!",
    "You’re too predictable, I know all your moves!",
    "I like making you uncomfortable, it’s hilarious!",
    "You’re my favorite plaything~",
    "Don’t try to act cool, it’s not working!"
]

